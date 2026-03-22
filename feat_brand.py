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
            st.success("\u2728 Your brand identity is ready below!")

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
</div>
<p style="text-align:center; font-size:13px; margin-top:6px; font-family:monospace; color:#ccc;">{color}</p>
""", unsafe_allow_html=True)

        # --- ADD SUGGESTIONS ---
        st.markdown("---")
        st.markdown("### \U0001f4ac Add Suggestions")
        st.caption("Have an idea or want to tweak the brand identity? Describe your changes and let the AI refine it based on what was already generated.")
        col1, col2 = st.columns([4, 1])
        with col1:
            brand_suggestion = st.text_input(
                "Your suggestions:",
                label_visibility="collapsed",
                placeholder="e.g. Make the slogans more playful, add a darker color to the palette...",
                key="brand_suggestion_input"
            )
        with col2:
            apply_brand_btn = st.button("Apply", use_container_width=True, key="brand_apply_btn")

        if apply_brand_btn and brand_suggestion:
            current_brand = st.session_state.brand
            refine_prompt = f"""
            You are refining an existing brand identity.

            CURRENT BRAND DATA:
            Slogans: {current_brand.get('slogans', [])}
            Fonts: {current_brand.get('fonts', [])}
            Color Palette: {current_brand.get('palette', [])}

            Company: {company}
            Industry: {industry}
            Tone: {tone}
            Description: {desc}

            USER SUGGESTIONS: "{brand_suggestion}"

            Task: Apply the user's suggestions and return an updated brand identity.
            Return ONLY JSON with this exact structure:
            {{"slogans":["","","","",""], "fonts":["","",""], "palette":["#HEX","#HEX","#HEX","#HEX"]}}
            """
            with st.spinner("Applying your suggestions..."):
                response = generate_ai(refine_prompt)
                data = extract_json(response)
                if data:
                    st.session_state.brand = data
                    st.success("\u2728 Brand identity updated with your suggestions!")
                    st.rerun()
                else:
                    st.warning("\u26a0\ufe0f Could not apply suggestions. Please try again.")
