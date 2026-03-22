import streamlit as st
import io
import os
import re
import zipfile
from PIL import Image as PILImage, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from utils import generate_ai

def clean_markdown(text):
    """Sanitizes text, converts smart punctuation, and handles markdown."""
    if not text: return ""
    replacements = {
        '\u201c': '"', '\u201d': '"', '\u2018': "'", '\u2019': "'",
        '\u2014': '-', '\u2013': '-', '\u2026': '...', '\u2022': '-',
    }
    for search, replace in replacements.items():
        text = text.replace(search, replace)
    
    # Basic cleanup
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = text.replace('```', '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Convert Markdown to ReportLab HTML-like tags
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    return text

def create_color_palette_image(palette):
    """Creates a color palette image with swatches and hex codes."""
    colors = palette[:4]
    img_width, img_height = 800, 200
    swatch_width = img_width // len(colors)
    img = PILImage.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font = ImageFont.load_default()

    for i, color in enumerate(colors):
        x = i * swatch_width
        draw.rectangle([x, 0, x + swatch_width, 150], fill=color)
        
        # FIXED: Corrected text width calculation
        bbox = draw.textbbox((0, 0), color, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = x + (swatch_width - text_width) // 2
        draw.text((text_x, 160), color, fill='black', font=font)

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

def create_brand_book_pdf(company, desc):
    """Creates the brand book PDF."""
    if not st.session_state.get("brand"):
        return None
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = styles["Heading1"]
    title_style.alignment = TA_CENTER
    body = ParagraphStyle('body', fontSize=11, leading=16)
    bullet_style = ParagraphStyle('bullet', fontSize=11, leading=16, leftIndent=20)
    
    # FIXED: Corrected list initialization
    story = []

    def add_block(text):
        if not text: return
        cleaned_text = clean_markdown(text)
        for line in cleaned_text.split("\n"):
            line = line.strip()
            # Skip empty lines or markdown table separators
            if not line or line.startswith("---") or re.match(r'^[\s\-:|]+$', line):
                continue
            
            if line.startswith("- ") or line.startswith("* "):
                story.append(Paragraph(f"&bull; {line[2:]}", bullet_style))
            elif re.match(r'^\d+\.\s', line):
                story.append(Paragraph(line, bullet_style))
            else:
                story.append(Paragraph(line, body))
            story.append(Spacer(1, 6))

    # --- Document Structure ---
    story.append(Paragraph(f"{company} Brand Book", title_style))
    story.append(Spacer(1, 30))
    
    sections = [
        ("Company Overview", desc),
        ("Brand Strategy", st.session_state.get("strategy")),
        ("Slogans", st.session_state.get("final_slogan") or st.session_state.brand.get("slogans")),
        ("Typography", st.session_state.get("final_font") or st.session_state.brand.get("fonts")),
        ("Color Palette", st.session_state.brand.get("palette")),
        ("Additional Notes", st.session_state.get("book_extra_content"))
    ]

    for title, content in sections:
        if content:
            story.append(Paragraph(title, styles["Heading2"]))
            if isinstance(content, list):
                for item in content: add_block(f"- {item}")
            else:
                add_block(content)
            story.append(Spacer(1, 10))

    doc.build(story)
    buffer.seek(0)
    return buffer

def create_brand_book_zip(company, desc):
    """Creates a ZIP file containing assets."""
    if not st.session_state.get("brand"):
        return None
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        palette = st.session_state.brand.get("palette", [])
        if palette:
            color_img = create_color_palette_image(palette)
            zip_file.writestr('color_palette.png', color_img.read())

        pdf_buffer = create_brand_book_pdf(company, desc)
        if pdf_buffer:
            zip_file.writestr('brand_book.pdf', pdf_buffer.read())
            
    zip_buffer.seek(0)
    return zip_buffer

def render(company, industry, tone, desc):
    st.markdown("### 📘 Brand Book Generator")
    
    if not st.session_state.get("brand"):
        st.info("💡 Tip: Go to the '🎨 Brand Identity' tab first!")
        return

    # User Suggestions Section
    st.markdown("---")
    book_suggestion = st.text_input("Add custom sections (e.g. Target Audience):")
    if st.button("Generate Extra Content") and book_suggestion:
        with st.spinner("Generating..."):
            prompt = f"Write a brand book section for {company} about {book_suggestion}."
            st.session_state.book_extra_content = generate_ai(prompt)
            st.success("Done!")

    # Final Export
    zip_data = create_brand_book_zip(company, desc)
    if zip_data:
        st.download_button(
            label="📥 Download Brand Book Package (ZIP)",
            data=zip_data,
            file_name=f"{company.replace(' ', '_')}_Brand_Book.zip",
            mime="application/zip",
            use_container_width=True
        )
