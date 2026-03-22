import streamlit as st
import io
import zipfile
import os
from PIL import Image as PILImage, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
from utils import generate_ai

def clean_markdown(text):
    if not text: return ""
    replacements = {
        '\u201c': '"', '\u201d': '"', '\u2018': "'", '\u2019': "'",
        '\u2014': '=', '\u2013': '-', '\u2026': '...', '\u2022': '-',
    }
    for search, replace in replacements.items():
        text = text.replace(search, replace)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    text = text.replace('**', '')
    text = text.replace('##', '')
    return text

def get_cjk_font(size):
    """Try to load a font that supports CJK (Japanese/Chinese/Korean) characters."""
    cjk_font_paths = [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansJP-Regular.ttf",
        "/usr/share/fonts/truetype/unifont/unifont.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in cjk_font_paths:
        try:
            return ImageFont.truetype(path, size)
        except:
            continue
    return ImageFont.load_default()

def create_color_palette_image(palette):
    colors = palette[:4]
    img_width = 800
    img_height = 200
    swatch_width = img_width // len(colors) if colors else img_width
    img = PILImage.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font = ImageFont.load_default()
    for i, color in enumerate(colors):
        x = i * swatch_width
        draw.rectangle([x, 0, x + swatch_width, 150], fill=color)
        text = color
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = x + (swatch_width - text_width) // 2
        draw.text((text_x, 160), text, fill='black', font=font)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

def create_translations_image(translations):
    if not translations:
        return None
    if not isinstance(translations, dict):
        return None
    img_width = 1000
    line_height = 45
    padding = 30
    lines_data = []
    for lang, text in translations.items():
        if text:
            lines_data.append(('title', f"{lang}:"))
            # wrap text into chunks
            words = str(text).split()
            chunk = ""
            for word in words:
                if len(chunk) + len(word) + 1 < 70:
                    chunk += word + " "
                else:
                    if chunk:
                        lines_data.append(('body', chunk.strip()))
                    chunk = word + " "
            if chunk:
                lines_data.append(('body', chunk.strip()))
            lines_data.append(('gap', ''))
    img_height = max(400, len(lines_data) * line_height + padding * 2 + 60)
    img = PILImage.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(img)
    font_title = get_cjk_font(26)
    font_body = get_cjk_font(22)
    # Header
    try:
        header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    except:
        header_font = get_cjk_font(30)
    draw.text((padding, padding), "Brand Translations", fill='#111111', font=header_font)
    draw.line([(padding, padding + 40), (img_width - padding, padding + 40)], fill='#cccccc', width=2)
    y = padding + 60
    for kind, text in lines_data:
        if kind == 'gap':
            y += 15
        elif kind == 'title':
            draw.text((padding, y), text, fill='#1a1a2e', font=font_title)
            y += line_height
        else:
            draw.text((padding + 20, y), text, fill='#444444', font=font_body)
            y += line_height
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

def create_brand_book_pdf(company, industry, tone, desc, brand, campaign, strategy,
                          final_slogan, final_font, final_campaign_caption, extra_content):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('T', parent=styles['Heading1'], fontSize=24,
                                  spaceAfter=30, alignment=TA_CENTER)
    heading_style = ParagraphStyle('H', parent=styles['Heading2'], fontSize=16, spaceAfter=12)
    body_style = ParagraphStyle('B', parent=styles['BodyText'], fontSize=11,
                                 textColor='#555555', spaceAfter=10)
    story = []
    story.append(Paragraph(clean_markdown(f"{company} Brand Book"), title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Company Overview", heading_style))
    story.append(Paragraph(clean_markdown(f"Industry: {industry}"), body_style))
    story.append(Paragraph(clean_markdown(f"Brand Tone: {tone}"), body_style))
    story.append(Paragraph(clean_markdown(f"Description: {desc}"), body_style))
    story.append(Spacer(1, 0.2*inch))
    if brand:
        story.append(Paragraph("Brand Identity", heading_style))
        slogan = final_slogan or (brand.get('slogans', [''])[0] if brand.get('slogans') else '')
        font_name = final_font or (brand.get('fonts', [''])[0] if brand.get('fonts') else '')
        if slogan:
            story.append(Paragraph(clean_markdown(f"Tagline: {slogan}"), body_style))
        if font_name:
            story.append(Paragraph(clean_markdown(f"Primary Font: {font_name}"), body_style))
        if brand.get('color_palette'):
            story.append(Paragraph(clean_markdown(f"Color Palette: {', '.join(brand['color_palette'][:4])}"), body_style))
        story.append(Spacer(1, 0.2*inch))
    if campaign:
        story.append(Paragraph("Campaign Strategy", heading_style))
        ideas = campaign.get('campaign_ideas', [])
        if final_campaign_caption and final_campaign_caption in ideas:
            story.append(Paragraph(clean_markdown(f"Featured: {final_campaign_caption}"), body_style))
        else:
            for idx, idea in enumerate(ideas[:3], 1):
                story.append(Paragraph(clean_markdown(f"{idx}. {idea}"), body_style))
        story.append(Spacer(1, 0.2*inch))
    if strategy:
        story.append(Paragraph("Brand Strategy", heading_style))
        if strategy.get('target_audience'):
            story.append(Paragraph(clean_markdown(f"Target Audience: {strategy['target_audience']}"), body_style))
        if strategy.get('positioning'):
            story.append(Paragraph(clean_markdown(f"Positioning: {strategy['positioning']}"), body_style))
        story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Brand Translations", heading_style))
    story.append(Paragraph("See translations.png in this package for multilingual brand content.", body_style))
    if extra_content:
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Additional Brand Guidelines", heading_style))
        story.append(Paragraph(clean_markdown(extra_content), body_style))
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_brand_book_zip(company, industry, tone, desc):
    brand = st.session_state.get('brand', {})
    campaign = st.session_state.get('campaign', {})
    strategy = st.session_state.get('strategy', {})
    translations = st.session_state.get('translations', {})
    final_slogan = st.session_state.get('final_slogan', '')
    final_font = st.session_state.get('final_font', '')
    final_campaign_caption = st.session_state.get('final_campaign_caption', '')
    extra_content = st.session_state.get('book_extra_content', '')
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        if brand.get('color_palette'):
            palette_img = create_color_palette_image(brand['color_palette'])
            zf.writestr('color_palette.png', palette_img.read())
        if os.path.exists('logo_animation.gif'):
            with open('logo_animation.gif', 'rb') as f:
                zf.writestr('logo_animation.gif', f.read())
        pdf_buf = create_brand_book_pdf(company, industry, tone, desc, brand, campaign, strategy,
                                        final_slogan, final_font, final_campaign_caption, extra_content)
        zf.writestr('brand_book.pdf', pdf_buf.read())
        if translations:
            trans_img = create_translations_image(translations)
            if trans_img:
                zf.writestr('translations.png', trans_img.read())
    zip_buffer.seek(0)
    return zip_buffer

def render(company, industry, tone, desc):
    st.markdown("## Brand Book")
    st.caption("Download your complete brand package: color palette, logo, brand book PDF, and translations image.")
    st.markdown("### Finalized Selections")
    final_slogan = st.session_state.get('final_slogan', '')
    final_font = st.session_state.get('final_font', '')
    final_campaign_caption = st.session_state.get('final_campaign_caption', '')
    col1, col2, col3 = st.columns(3)
    with col1:
        if final_slogan:
            st.success(f"**Tagline:** {final_slogan}")
        else:
            st.info("No tagline selected yet")
    with col2:
        if final_font:
            st.success(f"**Font:** {final_font}")
        else:
            st.info("No font selected yet")
    with col3:
        if final_campaign_caption:
            st.success(f"**Campaign:** {final_campaign_caption[:40]}...")
        else:
            st.info("No campaign selected yet")
    st.markdown("---")
    st.markdown("### Add Extra Brand Guidelines")
    st.caption("Optional: add logo usage rules, brand voice notes, or any extra guidelines.")
    extra_suggestions = st.text_area(
        "Extra Content",
        value=st.session_state.get('book_extra_content', ''),
        placeholder="e.g., Logo usage rules, color combinations to avoid...",
        height=100,
        label_visibility="collapsed"
    )
    if st.button("Save Guidelines", key="save_extra"):
        if extra_suggestions.strip():
            st.session_state.book_extra_content = extra_suggestions
            st.success("Saved!")
    st.markdown("---")
    st.markdown("### Download Brand Package")
    if st.button("Generate Brand Book Package", type="primary"):
        with st.spinner("Building your brand package..."):
            try:
                zip_buf = create_brand_book_zip(company, industry, tone, desc)
                st.download_button(
                    label="Download Brand Book (ZIP)",
                    data=zip_buf,
                    file_name=f"{company.replace(' ', '_')}_brand_book.zip",
                    mime="application/zip"
                )
                st.success("Brand book package ready! Click above to download.")
                st.info("Package includes: color_palette.png | logo_animation.gif (if available) | brand_book.pdf | translations.png")
            except Exception as e:
                st.error(f"Error: {str(e)}")
