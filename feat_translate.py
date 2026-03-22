import streamlit as st
from utils import generate_ai, glass_card

def render():
    st.markdown("### Choose your markets")
    
    col1, col2, col3 = st.columns(3)
    lang1 = col1.text_input("Language 1", value="Spanish")
    lang2 = col2.text_input("Language 2", value="French")
    lang3 = col3.text_input("Language 3", value="Japanese")

    if st.button("Translate Top Slogan"):
        if st.session_state.brand.get("slogans"):
            slogan = st.session_state.brand["slogans"][0]
            with st.spinner("Translating..."):
                res = generate_ai(f"Translate this slogan: '{slogan}' into {lang1}, {lang2}, and {lang3}. Format it nicely.")
                st.session_state.translations = res
                st.success("Translations ready!")
        else:
            st.warning("⚠️ Please generate your Brand Identity first to get a slogan!")

    if st.session_state.translations:
        glass_card(st.session_state.translations)
