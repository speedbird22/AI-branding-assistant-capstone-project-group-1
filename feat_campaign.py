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

        # --- ADD SUGGESTIONS ---
        st.markdown("---")
        st.markdown("### \U0001f4ac Add Suggestions")
        st.caption("Want to refine the campaign? Describe your changes and the AI will update it based on the current results.")
        col1, col2 = st.columns([4, 1])
        with col1:
            campaign_suggestion = st.text_input(
                "Your suggestions:",
                label_visibility="collapsed",
                placeholder="e.g. Make the captions more humorous, focus on social media...",
                key="campaign_suggestion_input"
            )
        with col2:
            apply_campaign_btn = st.button("Apply", use_container_width=True, key="campaign_apply_btn")

        if apply_campaign_btn and campaign_suggestion:
            current_campaign = st.session_state.campaign
            refine_prompt = f"""
            You are refining an existing marketing campaign.

            CURRENT CAMPAIGN DATA:
            Captions: {current_campaign.get('captions', [])}
            Metrics: {current_campaign.get('metrics', '')}

            Company: {company}
            Industry: {industry}
            Tone: {tone}
            Description: {desc}

            USER SUGGESTIONS: "{campaign_suggestion}"

            Task: Apply the user's suggestions and return an updated campaign.
            Return ONLY JSON with this exact structure:
            {{"captions":["","",""], "metrics":""}}
            """
            with st.spinner("Applying your suggestions..."):
                response = generate_ai(refine_prompt)
                data = extract_json(response)
                if data:
                    st.session_state.campaign = data
                    st.success("\u2728 Campaign updated with your suggestions!")
                    st.rerun()
                else:
                    st.warning("\u26a0\ufe0f Could not apply suggestions. Please try again.")
