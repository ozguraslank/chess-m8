import streamlit as st
from pages.sidebar import get_menu_side_bar
from scripts.web_helpers import *
from scripts.game_analyzer import * 
from api.lichess_api import *
import chess
import chess.svg
from streamlit.components.v1 import html

change_layout("Match Analysis", "wide")
get_menu_side_bar()

st.markdown("""
    <style>
    /* Center align all text inside the columns */
    .column-value {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }
            
    .single-element {
        margin-top: 15px;
        margin-left: 25px;
    }
            
    .container {
        display: flex;
        justify-content: center;
        align-items: center;
    }
            
    .column-content {
        text-align: center;
    }

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

    /* Change button color on hover */
    div.stButton > button:hover {
        background-color: #214b89;
    }
    </style>
    """, unsafe_allow_html=True)

user_games = None
game_data = None
game_id = None
username = None

st.title("Match Analysis")
st.divider()

col1, _ = st.columns(2)
with col1:
    st.info("Enter your Lilchess username or game ID to start analyzing your games")

col1, _, _, _ = st.columns(4)
with col1:
    query_type = st.selectbox("Query by", ["Username", "Game ID"], index=1)

    if query_type == "Username":
        username = st.text_input("Username")
    else:
        game_id = st.text_input("Game ID")

    if st.button("Query"):
        if not (username or game_id):
            st.warning("Please enter a valid username or game ID")
            st.stop()
        
        if query_type == "Username":
            try:
                user_games = get_user_games(username)
                if not user_games:
                    st.warning("Please enter a valid username")
                    st.stop()

                elif len(user_games) == 0:
                    st.warning("No games found for this user")
                    st.stop()

            except Exception:
                st.warning("Please enter a valid username")
                st.stop()

        else:
            st.session_state['game_id'] = game_id
            with st.spinner("Fetching game data..."):
                game_data = get_game_data(game_id)
                if not game_data:
                    st.warning("Please enter a valid game ID")
                    st.stop()

            with st.spinner("Analyzing game..."):
                game_analysis_json = analyze_game(game_data)
                ai_suggestions_list = []
                ai_suggestions_list.append("Game started")

                for move in game_analysis_json['moves']:
                    ai_suggestions_list.append(move['white_analysis'])
                    ai_suggestions_list.append(move['black_analysis'])

                st.session_state[f'{game_id}_game_data'] = game_data
                st.session_state[f'{game_id}_current_move'] = 0
                st.session_state[f'{game_id}_suggestions'] = ai_suggestions_list

if user_games:
    st.markdown(f"### Last {len(user_games)} Games for {username}")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.info("Click on the 'Analyze' button of the game you want to analyze")
    for game in user_games:
        current_game_accuracy = game["players"]["white"]["analysis"]["accuracy"] if game["players"]["white"]["user"]["name"] == username else game["players"]["black"]["analysis"]["accuracy"]
        
        with st.container(border=True, height=85):
            col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 2, 2, 2, 2])

            # Set colors based on the result of the game
            result = game.get('winner', 'draw')
            if result == 'white':
                white_color = 'green'
                black_color = 'red'
            elif result == 'black':
                white_color = 'red'
                black_color = 'green'
            elif result == 'draw':
                white_color = '#d4c208'
                black_color = '#d4c208'
            else:  # Ongoing or unclear result
                white_color = 'gray'
                black_color = 'gray'

            with col1:
                st.write(f"<div class='column-value'><strong>Game ID</strong></div>", unsafe_allow_html=True)
                st.write(f"<div class='column-value'>{game['id']}</div>", unsafe_allow_html=True)

            with col2:
                st.write(f"<div class='column-value'><strong>Status</strong></div>", unsafe_allow_html=True)
                st.write(f"<div class='column-value'>{game['status']}</div>", unsafe_allow_html=True)

            with col3:
                st.write(f"<div class='column-value'><strong>White</strong></div>", unsafe_allow_html=True)
                st.write(f"<div class='column-value' style='color:{white_color};'>{game['players']['white']['user']['name']}</div>", unsafe_allow_html=True)

            with col4:
                st.write(f"<div class='column-value'><strong>Black</strong></div>", unsafe_allow_html=True)
                st.write(f"<div class='column-value' style='color:{black_color};'>{game['players']['black']['user']['name']}</div>", unsafe_allow_html=True)

            with col5:
                st.write(f"<div class='column-value'><strong>Your accuracy</strong></div>", unsafe_allow_html=True)
                st.write(f"<div class='column-value'>{current_game_accuracy}%</div>", unsafe_allow_html=True)

            with col6:
                if st.button("Analyze", key=f"{game['id']}_button"):
                    game_id = game['id']
                    st.session_state['game_id'] = game_id
                    
                    with st.spinner("Analyzing game..."):
                        game_analysis_json = analyze_game(game_data)
                        ai_suggestions_list = []
                        ai_suggestions_list.append("Game started")

                        for move in game_analysis_json['moves']:
                            ai_suggestions_list.append(move['white_analysis'])
                            ai_suggestions_list.append(move['black_analysis'])

                        st.session_state[f'{game_id}_game_data'] = game_data
                        st.session_state[f'{game_id}_current_move'] = 0
                        st.session_state[f'{game_id}_suggestions'] = ai_suggestions_list

selected_game_id = st.session_state.get('game_id', None)
if selected_game_id:
    game_data = st.session_state.get(f'{selected_game_id}_game_data', None)
    current_move = st.session_state.get(f'{selected_game_id}_current_move', None)
    suggestions = st.session_state.get(f'{selected_game_id}_suggestions', None)

    display_chess_game(selected_game_id, game_data['moves'], suggestions, current_move)