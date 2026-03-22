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
    """Sanitizes text and converts basic Markdown to ReportLab-friendly HTML."""
    if not text: return ""
    
    # Handle smart quotes and special characters
    replacements = {
        '\u201c': '"', '\u201d': '"', '\u2018': "'", '\u2019': "'",
        '\u2014': '-', '\u2013': '-', '\u2026': '...', '\u2022': '-',
    }
    for search, replace in replacements.items():
        text = text.replace(search, replace)
    
    # Basic HTML escaping for ReportLab
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Convert Bold/Italic Markdown to <b>/<i> tags
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    
    # Strip headers and code blocks
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    return text.strip()

def create_color_palette_image(palette):
    """Creates a horizontal color swatch image."""
    colors = palette[:4]  # Limit to 4 colors
    img_w, img_h = 800, 200
    swatch_w = img_w // len(colors)
    
    img = PILImage.new('RGB', (img_w, img_h), 'white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        font = ImageFont.load_default()

    for i, color in enumerate(colors):
        x = i * swatch_w
        # Draw the color block
        draw.rectangle([x, 0, x + swatch_w, 150], fill=color)
        
        # Calculate text position (Fixed math here)
        bbox = draw.textbbox((0, 0), color, font=font)
        tw = bbox[2] - bbox[0]
        tx = x + (swatch_w - tw) // 2
        draw.text((tx, 160), color, fill='black', font=font)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

def create_brand_book_pdf(company, desc):
    """Generates the structured PDF document."""
    if "brand" not in st.session_state: return None
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER)
    body_style = ParagraphStyle('Body', fontSize=11, leading=14)
    bullet_style = ParagraphStyle('Bullet', fontSize=11, leading=14, leftIndent=20)

    story = []

    def add_content(text, is_bullet=False):
        if not text: return
        cleaned = clean_markdown(text)
        for line in cleaned.split('\n'):
            if not line.strip(): continue
            style = bullet_style if (is_bullet or line.startswith('-')) else body_style
            story.append(Paragraph(line.lstrip('- '), style))
            story.append(Spacer(1, 4))

    # Building the Document
    story.append(Paragraph(f"{company} Brand Guidelines", title_style))
    story.append(Spacer(1, 24))

    sections = [
        ("Company Overview", desc),
        ("Brand Strategy", st.session_state.get("strategy")),
        ("Typography", st.session_state.get("final_font")),
        ("Visual Palette", ", ".join(st.session_state.brand.get("palette", []))),
        ("Additional Insights", st.session_state.get("book_extra_content"))
    ]

    for header, content in sections:
        if content:
            story.append(Paragraph(header, styles["Heading2"]))
            add_content(content)
            story.append(Spacer(1, 12))

    doc.build(story)
    buffer.seek(0)
    return buffer

def render(company, industry, tone, desc):
    st.header("📘 Brand Book Generator")
    
    if not st.session_state.get("brand"):
        st.warning("Please generate your Brand Identity first!")
        return

    # --- UI for Custom Content ---
    st.subheader("✨ Customize your Book")
    user_input = st.text_input("Add specific details (e.g., 'Target Audience')")
    
    if st.button("Generate Custom Content") and user_input:
        with st.spinner("Writing..."):
            prompt = f"Write a professional brand book section for {company} regarding: {user_input}"
            st.session_state.book_extra_content = generate_ai(prompt)
            st.success("Added to your book!")

    # --- Final Download ---
    st.divider()
    if st.button("📦 Prepare Download Package"):
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, 'w') as zip_f:
            # 1. PDF
            pdf = create_brand_book_pdf(company, desc)
            if pdf: zip_f.writestr(f"{company}_BrandBook.pdf", pdf.read())
            
            # 2. Palette
            palette = st.session_state.brand.get("palette", [])
            if palette:
                img = create_color_palette_image(palette)
                zip_f.writestr("color_palette.png", img.read())

        st.download_button(
            label="Download ZIP",
            data=zip_buf.getvalue(),
            file_name=f"{company}_Assets.zip",
            mime="application/zip"
        )
