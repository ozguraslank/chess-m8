import streamlit as st

def change_layout(title: str, layout: str = "centered"):
    """
    Change the layout of the Streamlit page and set the page title

    Parameters
    ----------
    title: str
        The title of the page

    layout: str (default="centered")
        The layout of the page
    """
    st.set_page_config(layout=layout, page_title=title)

def cache_game_id(game_id: str):
    """
    Cache the game ID in the Streamlit session state

    Parameters
    ----------
    game_id: str
        The game ID to cache
    """
    st.session_state['game_id'] = game_id
    
def reset_cache():
    """Erase the game ID from the Streamlit session state"""
    if 'game_id' in st.session_state:
        del st.session_state.game_id