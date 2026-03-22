import streamlit as st
from utils import generate_ai, extract_json, glass_card, font_card

def render(company, industry, tone, desc):
    if st.button("Generate Brand Identity"):
        prompt=f"""
        Return ONLY JSON.
        {{"slogans":["","","","",""], "fonts":["","",""], "palette":["#HEX","#HEX","#HEX","#HEX"]}}
        Company:{company}\nIndustry:{industry}\nTone:{tone}\nDescription:{desc}
        """
        data = extract_json(generate_ai(prompt))
        if data:
            st.session_state.brand = data
            st.success("✨ Your brand identity is ready below!")

    brand = st.session_state.brand
    if brand:
        st.subheader("Slogans")
        for s in brand.get("slogans", []):
            glass_card(s)

        st.subheader("Fonts")
        for f in brand.get("fonts", []):
            font_card(f)

        st.subheader("Color Palette")
        cols = st.columns(len(brand.get("palette", [])))
        for col, color in zip(cols, brand.get("palette", [])):
            col.markdown(f"""
            <div style="background:{color}; color:white; padding:35px; border-radius:14px; text-align:center;">
            {color}
            </div>
            """, unsafe_allow_html=True)
