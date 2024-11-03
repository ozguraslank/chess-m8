import os
import json
from typing import Optional, List
import streamlit as st
import chess
import chess.svg
from streamlit.components.v1 import html
from api.gemini_api import send_request_to_gemini
from dotenv import load_dotenv
load_dotenv()

PROMPT = """
You are a strong chess grandmaster and experienced chess instructor, analyzing a chess game in the detailed, insightful style of Daniel Naroditsky. Use Stockfish evaluation strictly as a reference for assessing each move’s quality. Do not reference, suggest, or analyze alternative moves, hypothetical continuations, or variations at any point in the analysis.

Response Requirements:

    Move-by-Move Analysis: Analyze the game move by move, using the following format:
        1. [Comment to white's move]
        1.. [Comment to black's move]
        2. [Comment to white's move]
        2.. [Comment to black's move]
        … and so forth.
        
    Commentary Standards:
        - Provide exactly three (3) to four (4) sentences of concise, insightful commentary for every move, without exception. Critically verify that each move has at least 3 sentences and no more than 4, especially when assessing critical positions, mistakes, inaccuracies, or blunders.
        - Commentary should focus on why the move is effective or ineffective, based solely on its impact on the current board position. Emphasize core opening principles, such as center control, piece development, king safety, and tempo, as well as the positional impact, coordination, and control it brings.
        - Use Stockfish evaluations (if available) solely to judge the quality of each move (e.g., "good," "inaccurate," "blunder"), without any mention or hint of alternative moves or what could have been done instead.

    Explanation Depth:
        - Strictly adhere to the 3-4 sentence requirement for each move without deviation. Do not restate or describe the move itself; instead, focus on its positional impact and alignment with general principles and Stockfish’s evaluation.
        - Commentary should be consistent and constructive, noting any strategic implications, tactical flaws, or missed positional opportunities. 
        - If a move’s impact is minor, this should be stated concisely in 3 sentences to maintain consistency.
        - If there is little to comment on near the game’s end, simply state that fact and conclude the analysis.

Accuracy and Position-Checking:
    - All references to piece activity, threats, and interactions must be accurate based on the current board position. Double-check for any inaccuracies in comments on tactics, piece threats, or piece coordination.

Final Recommendations:
    After the move-by-move analysis, provide a summary of key areas for improvement for both players. Focus on general principles for stronger opening strategy and positional play without suggesting specific alternative moves. Conclude with:
        - General advice on improving move selection.
        - Tips on achieving active piece play and effective board control.

Example JSON Format:
{
  'moves': [
    {
      'move_number': move number here,
      'white': 'move here',
      'black': 'move here',
      'white_analysis': 'text here',
      'black_analysis': 'text here',
      'eval': [
        0: eval score here,
        1: eval score here
        ] 
    }
  ],
  'final_recommendations': {
    'white': 'text here',
    'black': 'text here'
  }
}
"""

def display_chess_game(game_id: str, moves: str, comments: List[str], current_move: int = 0, evals: Optional[List[float]] = None):
    """
    Display the chess game step by step with navigation buttons.

    Parameters
    ----------
    moves: str
        String of all moves in the game. e.g. "m1 m2 m3 m4 m5 m6 ..."

    comments: list
        List of comments for each move. e.g. ["Comment 1", "Comment 2", ...]

    current_move: int (default=0)
        Current move number.

    evals: list (default=None)
        List of evaluation scores for each move (If available)
    """
    move_list = moves.split()
    num_moves = len(move_list)

    if current_move >= num_moves: # If Its the last step, do nothing
        current_move = num_moves

    # Display the board
    col1, col2, col3 = st.columns([20, 1, 22])
    with col1:
        board = chess.Board()
        for i in range(current_move):
            board.push_san(move_list[i])

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

        st.divider()
        st.write(f"<div style='text-align: center;'><strong>AI Comments</strong></div>", unsafe_allow_html=True)
        st.write("")
        st.info(comments[current_move])

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

    combined_prompt = PROMPT
    combined_prompt += """

Here is a game pgn below
    """
    combined_prompt += game_pgn

    ai_response = send_request_to_gemini(combined_prompt)
    ai_result = None

    # Sometimes LLM API returns different formats of JSON, so let's try to scenarios
    try:
        ai_result = json.loads(ai_response.text)
    except:
        try:
            ai_result = eval(ai_response.text)
        except:
            pass # If it fails, it will return None

    return ai_result