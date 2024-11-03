import os
import json
import requests
import streamlit as st
import chess
import chess.svg
from streamlit.components.v1 import html
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

LLM_API_KEY = os.getenv('LLM_API_KEY')
PROMPT = os.getenv('LLM_PROMPT')

def display_chess_game(game_id, moves, suggestions, current_move = 0):
    """
    Display the chess game step by step with navigation buttons.

    Parameters
    ----------
    moves: str
        String of all moves in the game.
    """
    move_list = moves.split()
    num_moves = len(move_list)

    if current_move == num_moves: # If Its the last step, do nothing
        return True

    # Display the board
    col1, col2, _ = st.columns([3, 1, 1])
    with col1:
        board = chess.Board()
        for i in range(current_move):
            board.push_san(move_list[i])

        board_svg = chess.svg.board(board, size=600)  
        html(board_svg, height=650)
    
    with col2:
        for _ in range(15):
            st.write("")
        st.info(suggestions[current_move])

    col1, col2, _, col3, _, _, _, _ = st.columns([2, 2, 5, 2, 5, 1, 1, 1])
    with col1:
        if st.button("Previous"):
            if current_move > 0:
                current_move -= 1
                st.session_state[f'{game_id}_current_move'] = current_move
                st.rerun()

    with col2:
        if st.button("Next"):
            if current_move < num_moves:
                current_move += 1
                st.session_state[f'{game_id}_current_move'] = current_move
                st.rerun()

    with col3:
        if st.button("Reset"):
            current_move = 0
            st.session_state[f'{game_id}_current_move'] = current_move
            st.rerun()

def analyze_game(game_data: str):
    game_pgn = game_data['pgn']
    game_pgn = [line for line in game_pgn.split("\n") if line != "" and not line.startswith("[")][0]

    combined_prompt = PROMPT + "\n\n" + game_pgn
    
    genai.configure(api_key=LLM_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(combined_prompt, generation_config=genai.GenerationConfig(
        response_mime_type="application/json",
        max_output_tokens=50000,
        temperature=0.1
        ))

    return json.loads(response.text)