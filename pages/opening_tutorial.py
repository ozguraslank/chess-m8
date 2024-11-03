import streamlit as st
from pages.sidebar import get_menu_side_bar
from config.chess_tutorial_config import *
from scripts.web_helpers import *
from scripts.game_analyzer import * 

change_layout("Chess Opening Tutorial", "wide")
get_menu_side_bar()

st.markdown("""
    <style>
    div.stButton > button {
        background-color: #3b6dba;
        color: white;            
        padding: 10px 24px;      
        border: none;            
        border-radius: 4px;      
        font-size: 16px;         
        cursor: pointer;          
        margin-top: 5px;
    }

    div.stButton > button:hover {
        background-color: #214b89;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Chess Opening Tutorial")
st.divider()

col1, col2, col3, col4, _ = st.columns(5)

with col1:
    opening_level = st.selectbox("Select Level", CHESS_OPENINGS['levels'])
with col2:
    opening_strategy = st.selectbox("Select Strategy", CHESS_OPENINGS['strategies'])
with col3:
    available_openings = [opening for opening in CHESS_OPENINGS['openings'] if CHESS_OPENINGS['openings'][opening]['level'] == opening_level and CHESS_OPENINGS['openings'][opening]['approach'] == opening_strategy]
    available_openings_names = [CHESS_OPENINGS['openings'][opening]['name'] for opening in available_openings]
    opening_name = st.selectbox("Select Opening", available_openings_names)

if st.button("Get Tutorial"):
    with st.spinner("Creating tutorial simulation for you..."):
        opening_tutorial = get_chess_opening_tutorial(opening_name)
        if opening_tutorial is not None:
            opening_tutorial = opening_tutorial['tutorial']
            st.session_state[f"{opening_name}_tutorial"] = opening_tutorial

selected_tutorial = st.session_state.get(f'{opening_name}_tutorial', None)
if selected_tutorial:
    selected_tutorial_comments = ["Game starts"]
    selected_tutorial_comments.extend(selected_tutorial['suggestions'])
    selected_tutorial_moves = selected_tutorial['moves']
    
    current_move = st.session_state.get(f'{opening_name}_tutorial_current_move', 0)
    display_chess_game(f"{opening_name}_tutorial", selected_tutorial_moves, selected_tutorial_comments, current_move)