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

        # --- ADD SUGGESTIONS ---
        st.markdown("---")
        st.markdown("### \U0001f4ac Add Suggestions")
        st.caption("Want to expand or modify the strategy? Describe your changes and the AI will refine it based on what was already generated.")
        col1, col2 = st.columns([4, 1])
        with col1:
            strategy_suggestion = st.text_input(
                "Your suggestions:",
                label_visibility="collapsed",
                placeholder="e.g. Focus more on digital marketing, add a section on partnerships...",
                key="strategy_suggestion_input"
            )
        with col2:
            apply_strategy_btn = st.button("Apply", use_container_width=True, key="strategy_apply_btn")

        if apply_strategy_btn and strategy_suggestion:
            refine_prompt = f"""
            You are refining an existing brand strategy report.

            CURRENT STRATEGY:
            {st.session_state.strategy}

            Company: {company}
            Industry: {industry}
            Tone: {tone}
            Description: {desc}

            USER SUGGESTIONS: "{strategy_suggestion}"

            Task: Apply the user's suggestions and return an updated brand strategy report.

            CRITICAL FORMATTING RULES:
            - Use clear headers and bullet points.
            - DO NOT use Markdown tables.
            - DO NOT use code blocks or backticks.
            - Write strictly in standard paragraphs and bulleted lists.
            """
            with st.spinner("Applying your suggestions..."):
                response = generate_ai(refine_prompt)
                if response:
                    st.session_state.strategy = response
                    st.success("\u2728 Strategy updated with your suggestions!")
                    st.rerun()
                else:
                    st.warning("\u26a0\ufe0f Could not apply suggestions. Please try again.")
