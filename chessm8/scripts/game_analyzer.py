import json
from typing import Optional, Union, List
import streamlit as st
from streamlit.components.v1 import html
import chess
import chess.svg
from config.prompts import *
from api.gemini_api import send_request_to_gemini
from dotenv import load_dotenv
load_dotenv()


def display_chess_game(game_id: str, moves: Union[str, List[str]], comments: List[str], current_move: int = 0, evals: Optional[List[float]] = None):
    """
    Display the chess game step by step with navigation buttons.

    Parameters
    ----------
    moves: str or List of str
        String of all moves in the game. e.g. "m1 m2 m3 m4 m5 m6 ..." or ["m1", "m2", "m3", ...]

    comments: list
        List of comments for each move. e.g. ["Comment 1", "Comment 2", ...]

    current_move: int (default=0)
        Current move number.

    evals: list (default=None)
        List of evaluation scores for each move (If available)
    """
    if isinstance(moves, str):
        move_list = moves.split()
    else:
        move_list = moves
        
    num_moves = len(move_list)

    if current_move >= num_moves: # If Its the last step, do nothing
        current_move = num_moves

    # Display the board
    col1, col2, col3 = st.columns([20, 1, 22])
    with col1:
        board = chess.Board()
        for i in range(current_move):
            try:
                board.push_san(move_list[i])
            except chess.IllegalMoveError:
                break

        board_svg = chess.svg.board(board, size=500)  
        html(board_svg, height=510)
    
    with col3:
        for _ in range(2):
            st.write("")
        if evals is not None:
            eval = evals[current_move]
            color = 'green' if eval > 0 else ('red' if eval < 0 else '#d4c208')
            st.write(f"<div class='column-value'><strong>Evaluation Score (White is ahead If score > 0, or reversed)</strong></div>", unsafe_allow_html=True)
            st.write(f"<div class='column-value' style='color: {color};'>{eval}</div>", unsafe_allow_html=True)

        if evals is not None:
            st.divider()
        st.write(f"<div style='text-align: center;'><strong>AI Comments</strong></div>", unsafe_allow_html=True)
        st.write("")
        try:
            st.info(comments[current_move])
        except IndexError:
            st.info("No comments available for this move")

    col1, col2, _, col3, _, _, _, _, _, _ = st.columns([4, 8, 1, 9, 3, 3, 3, 2, 2, 2])
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
    """
    Analyze the chess game using LLM API.

    Parameters
    ----------
    game_data: dict
        Dictionary containing the game data.

    Returns
    -------
    dict
        Dictionary containing the AI analysis of the game.
    """
    game_pgn = game_data['pgn']
    game_pgn = [line for line in game_pgn.split("\n") if line != "" and not line.startswith("[")][0]

    combined_prompt = GAME_ANALYSIS_PROMPT
    combined_prompt += """

Here is a game pgn below
    """
    combined_prompt += game_pgn

    return send_request_to_gemini(combined_prompt, "gemini-1.5-pro")

def get_chess_opening_tutorial(opening_name: str):
    """
    Get the chess opening tutorial via AI

    Parameters
    ----------
    opening_name: str
        Name of the opening.

    Returns
    -------
    dict
        Dictionary containing the opening tutorial powered-by AI
    
    """
    combined_prompt = OPENING_TUTORIAL_PROMPT
    combined_prompt += f"""

Here is a requested opening below:
{opening_name}
    """
    return send_request_to_gemini(combined_prompt, "gemini-1.5-pro")
    