import streamlit as st
import io
import os
import re
from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

def clean_markdown(text):
    """Sanitizes text, converts smart punctuation, and handles markdown."""
    if not text: return ""
    
    # 1. Convert "smart" typography to standard ASCII to prevent black boxes (■)
    replacements = {
        '“': '"', '”': '"', '‘': "'", '’': "'",
        '—': '-', '–': '-', '…': '...', '•': '-', '\u2022': '-', '\u2013': '-', '\u2014': '-'
    }
    for search, replace in replacements.items():
        text = text.replace(search, replace)
        
    # 2. Strip any remaining unsupported unicode/emojis
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # 3. Strip out raw HTML tags and backticks
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('```', '')
    
    # 4. Escape special XML characters
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # 5. Convert Markdown **bold** and *italics* to ReportLab safe tags
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = re.sub(r'_(.*?)_', r'<i>\1</i>', text)
    
    # 6. Clean up Markdown headers (###)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    
    return text

def create_brand_book(company, desc):
    if not st.session_state.brand:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = styles["Heading1"]
    title_style.alignment = TA_CENTER
    
    body = ParagraphStyle('body', fontSize=11, leading=16)
    bullet_style = ParagraphStyle('bullet', fontSize=11, leading=16, leftIndent=20)

    story = []

    def add_block(text):
        """Smart parser that turns text into proper PDF paragraphs and bullets."""
        if not text: return
        cleaned_text = clean_markdown(text)
        
        for line in cleaned_text.split("\n"):
            line = line.strip()
            
            # Skip empty lines, markdown dividers (---), and markdown table separators (|---|)
            if not line or line.startswith("---") or re.match(r'^\|?[\s\-:]+\|$', line): 
                continue
            
            # Convert markdown table rows into standard text strings
            if line.startswith("|") and line.endswith("|"):
                line = line.replace("|", " ").strip()
                line = re.sub(r'\s+', ' ', line) # collapse multiple spaces

            # Catch standard bullet points
            if line.startswith("- ") or line.startswith("* "):
                story.append(Paragraph(f"• {line[2:]}", bullet_style))
            # Catch numbered lists (e.g., "1. ")
            elif re.match(r'^\d+\.\s', line): 
                story.append(Paragraph(line, bullet_style))
            # Standard paragraph
            else:
                story.append(Paragraph(line, body))
            story.append(Spacer(1, 6))

    # --- COVER ---
    story.append(Paragraph(f"{company} Brand Book", title_style))
    story.append(Spacer(1, 30))

    # --- LOGO INSERTION (STATIC PNG) ---
    if os.path.exists('logo_animation.gif'):
        try:
            with PILImage.open('logo_animation.gif') as img:
                img.seek(0) 
                rgb_im = img.convert('RGB')
                rgb_im.save('logo_static.png', 'PNG')
            
            story.append(Paragraph("Primary Logo", styles["Heading2"]))
            logo_img = RLImage('logo_static.png', width=250, height=250)
            story.append(logo_img)
            story.append(Spacer(1, 20))
        except Exception as e:
            st.warning(f"Could not add logo to PDF: {e}")

    # --- CONTENT ---
    story.append(Paragraph("Company Overview", styles["Heading2"]))
    add_block(desc)
    story.append(Spacer(1, 10))

    if st.session_state.strategy:
        story.append(Paragraph("Brand Strategy", styles["Heading2"]))
        add_block(st.session_state.strategy)
        story.append(Spacer(1, 10))

    story.append(Paragraph("Slogans", styles["Heading2"]))
    for s in st.session_state.brand.get("slogans", []):
        add_block(f"- {s}")
    story.append(Spacer(1, 10))

    story.append(Paragraph("Typography", styles["Heading2"]))
    for f in st.session_state.brand.get("fonts", []):
        add_block(f"- {f}")
    story.append(Spacer(1, 10))

    story.append(Paragraph("Color Palette", styles["Heading2"]))
    for c in st.session_state.brand.get("palette", []):
        add_block(f"- {c}")
    story.append(Spacer(1, 10))

    if st.session_state.campaign:
        story.append(Paragraph("Campaign Strategy", styles["Heading2"]))
        for cap in st.session_state.campaign.get("captions", []):
            add_block(f"- {cap}")
        add_block(st.session_state.campaign.get("metrics", ""))
        story.append(Spacer(1, 10))

    if st.session_state.translations:
        story.append(Paragraph("Translations", styles["Heading2"]))
        add_block(st.session_state.translations)

    doc.build(story)
    buffer.seek(0)
    return buffer

def render(company, desc):
    st.markdown("### 📕 Brand Book Generator")
    st.caption("Compile all your generated brand assets into a professional PDF.")

    if not st.session_state.get("brand"):
        st.info("💡 **Tip:** Go to the '🎨 Brand Identity' tab and generate your brand first to unlock the PDF download!")
        return

    pdf_buffer = create_brand_book(company, desc)
    
    if pdf_buffer:
        st.success("✅ Your Brand Book is ready!")
        st.download_button(
            label="📥 Download Brand Book PDF",
            data=pdf_buffer,
            file_name=f"{company.replace(' ', '_')}_Brand_Book.pdf",
            mime="application/pdf",
            use_container_width=True
        )
