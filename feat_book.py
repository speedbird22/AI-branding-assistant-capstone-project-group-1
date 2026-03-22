import streamlit as st
import io
import zipfile
import os
import json
from PIL import Image as PILImage, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
from utils import generate_ai

def clean_markdown(text):
    """Sanitizes text, converts smart punctuation, and handles markdown."""
    if not text: return ""
    # Ensure text is a string to avoid 'attribute error'
    if not isinstance(text, str):
        text = str(text)
        
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

def create_color_palette_image(palette):
    """Creates a color palette image with swatches and hex codes."""
    if not isinstance(palette, list): return None
    
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
        try:
            draw.rectangle([x, 0, x + swatch_width, 150], fill=color)
            text = str(color)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = x + (swatch_width - text_width) // 2
            draw.text((text_x, 160), text, fill='black', font=font)
        except:
            continue
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

def create_translations_image(translations):
    """Creates an image displaying the three translation blocks."""
    if not isinstance(translations, dict) or not translations:
        return None
    
    img_width = 1000
    line_height = 40
    padding = 30
    
    lines = []
    for lang, text in translations.items():
        lines.append(f"{lang}:")
        lines.append(str(text))
        lines.append("")
    
    img_height = max(600, len(lines) * line_height + padding * 2)
    img = PILImage.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
    
    y_position = padding
    for lang, text in translations.items():
        draw.text((padding, y_position), f"{lang}:", fill='#1a1a1a', font=font_title)
        y_position += line_height + 10
        
        words = str(text).split()
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            bbox = draw.textbbox((0, 0), test_line, font=font_text)
            if bbox[2] - bbox[0] < img_width - padding * 2:
                current_line = test_line
            else:
                if current_line:
                    draw.text((padding + 20, y_position), current_line.strip(), fill='#333333', font=font_text)
                    y_position += line_height
                current_line = word + " "
        
        if current_line:
            draw.text((padding + 20, y_position), current_line.strip(), fill='#333333', font=font_text)
            y_position += line_height
        y_position += 20
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

def create_brand_book_pdf(company, industry, tone, desc, brand, campaign, strategy, final_slogan, final_font, final_campaign_caption, extra_content):
    """Creates a brand book PDF with finalized content."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor='#1a1a1a', spaceAfter=30, alignment=TA_CENTER)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=16, textColor='#333333', spaceAfter=12)
    body_style = ParagraphStyle('CustomBody', parent=styles['BodyText'], fontSize=11, textColor='#666666', spaceAfter=12)
    
    story = []
    story.append(Paragraph(clean_markdown(f"{company} Brand Book"), title_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("Company Overview", heading_style))
    story.append(Paragraph(clean_markdown(f"Industry: {industry}"), body_style))
    story.append(Paragraph(clean_markdown(f"Brand Tone: {tone}"), body_style))
    story.append(Paragraph(clean_markdown(f"Description: {desc}"), body_style))
    story.append(Spacer(1, 0.2*inch))
    
    if isinstance(brand, dict) and brand:
        story.append(Paragraph("Brand Identity", heading_style))
        slogan = final_slogan or (brand.get('slogans', [""])[0] if brand.get('slogans') else "")
        if slogan: story.append(Paragraph(clean_markdown(f"Tagline: {slogan}"), body_style))
        
        font_choice = final_font or (brand.get('fonts', [""])[0] if brand.get('fonts') else "")
        if font_choice: story.append(Paragraph(clean_markdown(f"Primary Font: {font_choice}"), body_style))
        
        if brand.get('color_palette'):
            colors_text = ", ".join(brand['color_palette'][:4])
            story.append(Paragraph(clean_markdown(f"Color Palette: {colors_text}"), body_style))
        story.append(Spacer(1, 0.2*inch))
    
    if isinstance(campaign, dict) and campaign:
        story.append(Paragraph("Campaign Strategy", heading_style))
        ideas = campaign.get('campaign_ideas', [])
        if final_campaign_caption and final_campaign_caption in ideas:
            story.append(Paragraph(clean_markdown(f"Featured Campaign: {final_campaign_caption}"), body_style))
        elif ideas:
            for idx, idea in enumerate(ideas[:3], 1):
                story.append(Paragraph(clean_markdown(f"{idx}. {idea}"), body_style))
        story.append(Spacer(1, 0.2*inch))
    
    if isinstance(strategy, dict) and strategy:
        story.append(Paragraph("Brand Strategy", heading_style))
        if strategy.get('target_audience'):
            story.append(Paragraph(clean_markdown(f"Target Audience: {strategy['target_audience']}"), body_style))
        if strategy.get('positioning'):
            story.append(Paragraph(clean_markdown(f"Positioning: {strategy['positioning']}"), body_style))
        story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("Brand Translations", heading_style))
    story.append(Paragraph("See translations.png for multilingual brand content.", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    if extra_content:
        story.append(Paragraph("Additional Brand Guidelines", heading_style))
        story.append(Paragraph(clean_markdown(extra_content), body_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_brand_book_zip(company, industry, tone, desc):
    """Creates a ZIP file with safety checks for dictionary types."""
    # DATA SAFETY CHECKS: Ensure these are dicts before calling .get()
    brand = st.session_state.get('brand', {})
    if not isinstance(brand, dict): brand = {}
        
    campaign = st.session_state.get('campaign', {})
    if not isinstance(campaign, dict): campaign = {}
        
    strategy = st.session_state.get('strategy', {})
    if not isinstance(strategy, dict): strategy = {}
        
    translations = st.session_state.get('translations', {})
    if not isinstance(translations, dict): translations = {}
    
    final_slogan = st.session_state.get('final_slogan', '')
    final_font = st.session_state.get('final_font', '')
    final_campaign_caption = st.session_state.get('final_campaign_caption', '')
    extra_content = st.session_state.get('book_extra_content', '')
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        if brand.get('color_palette'):
            palette_img = create_color_palette_image(brand['color_palette'])
            if palette_img: zip_file.writestr('color_palette.png', palette_img.read())
        
        if os.path.exists('logo_animation.gif'):
            with open('logo_animation.gif', 'rb') as f:
                zip_file.writestr('logo_animation.gif', f.read())
        
        pdf_buffer = create_brand_book_pdf(company, industry, tone, desc, brand, campaign, strategy, 
                                          final_slogan, final_font, final_campaign_caption, extra_content)
        zip_file.writestr('brand_book.pdf', pdf_buffer.read())
        
        if translations:
            translations_img = create_translations_image(translations)
            if translations_img:
                zip_file.writestr('translations.png', translations_img.read())
    
    zip_buffer.seek(0)
    return zip_buffer

def render(company, industry, tone, desc):
    st.markdown("## 📖 Brand Book")
    st.caption("Download your complete brand package.")
    
    st.markdown("### ✅ Finalized Selections")
    final_slogan = st.session_state.get('final_slogan', '')
    final_font = st.session_state.get('final_font', '')
    final_campaign_caption = st.session_state.get('final_campaign_caption', '')
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if final_slogan: st.success(f"**Tagline:** {final_slogan}")
        else: st.info("No tagline selected")
    with col2:
        if final_font: st.success(f"**Font:** {final_font}")
        else: st.info("No font selected")
    with col3:
        if final_campaign_caption: st.success(f"**Campaign:** {final_campaign_caption[:30]}...")
        else: st.info("No campaign selected")
    
    st.markdown("---")
    st.markdown("### 💬 Add Extra Brand Guidelines")
    
    extra_suggestions = st.text_area(
        "Extra Content",
        value=st.session_state.get('book_extra_content', ''),
        placeholder="e.g., Logo usage rules...",
        height=100
    )
    
    if st.button("💾 Save", key="save_extra"):
        st.session_state.book_extra_content = extra_suggestions
        st.success("Saved!")
    
    st.markdown("---")
    st.markdown("### 📦 Download Brand Package")
    
    if st.button("🎨 Generate Brand Book Package", type="primary"):
        with st.spinner("Creating your brand book package..."):
            try:
                zip_buffer = create_brand_book_zip(company, industry, tone, desc)
                st.download_button(
                    label="⬇️ Download Brand Book (ZIP)",
                    data=zip_buffer,
                    file_name=f"{company.replace(' ', '_')}_brand_book.zip",
                    mime="application/zip"
                )
                st.success("✅ Brand book package ready!")
            except Exception as e:
                st.error(f"Error creating brand book: {str(e)}")
