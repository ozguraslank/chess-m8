import streamlit as st 

def get_menu_side_bar():
    with st.sidebar:
        # Center the logo
        col1, col2, col3 = st.columns([1, 1, 7])
        with col2:
            st.image("img/chess_logo.jpg", width=150, caption = "ChessM8")
        st.divider()
        st.subheader("Menu")
        st.page_link("pages/analyze_game.py", label="Analyze Game")
        st.page_link("pages/opening_tutorial.py", label="Opening Tutorial")