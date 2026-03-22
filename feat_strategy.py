import streamlit as st
from utils import generate_ai, glass_card

def render(company, industry, tone, desc):
    if st.button("Generate Strategy Report"):
        prompt=f"""
        Create a highly structured professional brand strategy report.
        
        CRITICAL FORMATTING RULES:
        - Use clear headers and bullet points.
        - DO NOT use Markdown tables (e.g. no | Column | Column |).
        - DO NOT use code blocks or backticks (```).
        - Write strictly in standard paragraphs and bulleted lists.
        
        Company:{company}
        Industry:{industry}
        Tone:{tone}
        Description:{desc}
        """
        report = generate_ai(prompt)
        st.session_state.strategy = report
        st.success("Strategy ready!")

    if st.session_state.strategy:
        glass_card(st.session_state.strategy)
