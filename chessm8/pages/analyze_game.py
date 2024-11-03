import streamlit as st
from pages.sidebar import get_menu_side_bar
from scripts.web_helpers import *
from scripts.game_analyzer import * 
from api.lichess_api import *

change_layout("Game Analysis", "wide")
get_menu_side_bar()

st.markdown("""
    <style>
    .column-value {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }
            
    .container {
        display: flex;
        justify-content: center;
        align-items: center;
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

    div.stButton > button:hover {
        background-color: #214b89;
    }
    </style>
    """, unsafe_allow_html=True)

user_games = None
game_data = None
game_id = None
username = None

st.title("Game Analysis")
st.divider()

col1, _ = st.columns(2)
with col1:
    st.info("Enter your Lichess username or game ID to start analyzing your games")

col1, _, _, _ = st.columns(4)
with col1:
    query_type = st.selectbox("Query by", ["Username", "Game ID"], index=1)

    if query_type == "Username":
        username = st.text_input("Username")
    else:
        game_id = st.text_input("Game ID")

    if st.button("Analyze", key='analyze_button'):
        if not (username or game_id):
            st.warning("Please enter a valid username or game ID")
            st.stop()
        
        elif query_type == "Username":
            reset_cache()
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
            st.rerun()

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
                st.button(
                label='Analyze',
                key=f"{game['id']}_button",
                on_click=lambda game_id=game['id']: cache_game_id(game_id)
                )

selected_game_id = st.session_state.get('game_id', None) # If a game is selected
if selected_game_id:
    try:
        # Get game data
        game_data = st.session_state.get(f'{selected_game_id}_game_data', None)
        if not game_data:
            with st.spinner("Fetching game data..."):
                game_data = get_game_data(selected_game_id)
                if not game_data:
                    st.warning("Please enter a valid game ID")
                    st.stop()
                else:
                    st.session_state[f'{selected_game_id}_game_data'] = game_data

        # Get AI suggestions and evals
        ai_suggestions_list = st.session_state.get(f'{selected_game_id}_ai_suggestions', [])
        evals = st.session_state.get(f'{selected_game_id}_evals', [])
        current_move = st.session_state.get(f'{selected_game_id}_current_move', 0) 

        if game_data is not None and ai_suggestions_list == [] and evals == []:
            with st.spinner("Analyzing game... (It can take up to 2 minutes)"):
                game_analysis_json = analyze_game(game_data)
                if not game_analysis_json:
                    print("Game analysis failed, here is the game analysis json in the first attempt:")
                    print(game_analysis_json)
                    st.warning("Game analysis is failed, trying again...")
                    game_analysis_json = analyze_game(game_data)

                if not game_analysis_json:
                    print("Game analysis failed again, here is the game analysis json in the second attempt:")
                    print(game_analysis_json)
                    st.error(f"Game analysis failed for this game, please try another game")
                    st.stop()

                ai_suggestions_list.append("Game starts") # Add a dummy move for the game start
                evals.append(0)                           # Add a dummy eval for the game start

                # Get AI suggestions and evals for each move and add them to the lists required for displaying the game
                for move in game_analysis_json['moves']:
                    ai_suggestions_list.append(move['white_analysis'])
                    ai_suggestions_list.append(move['black_analysis'])

                    if not move['eval']: # If eval is not available, add -1
                        evals.append(-1)
                    else:
                        evals.extend(move['eval']) # eval is a list of 2 elements for every pack, add them to the list

                st.session_state[f'{selected_game_id}_ai_suggestions'] = ai_suggestions_list
                st.session_state[f'{selected_game_id}_evals'] = evals
                st.session_state[f'{selected_game_id}_current_move'] = current_move

        # If all required data is collected, display the game
        if game_data != None and len(ai_suggestions_list) > 0 and len(evals) > 0:
            display_chess_game(selected_game_id, game_data['moves'], ai_suggestions_list, current_move, evals)
            
    except Exception as e:
        st.error(f"Game analysis is failed for this game, please try another game")
        st.stop()