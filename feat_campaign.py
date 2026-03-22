import streamlit as st
from utils import generate_ai, extract_json, glass_card

def render(company, industry, tone, desc):
    if st.button("Generate Campaign"):
        prompt=f"""
        Return JSON:
        {{"captions":["","",""], "metrics":""}}
        Company:{company}\nIndustry:{industry}\nTone:{tone}\nDescription:{desc}
        """
        data = extract_json(generate_ai(prompt))
        if data:
            st.session_state.campaign = data
            st.success("Campaign generated!")

    if st.session_state.campaign:
        st.subheader("Campaign Ideas")
        for c in st.session_state.campaign.get("captions", []):
            glass_card(c)
        glass_card(st.session_state.campaign.get("metrics",""))
