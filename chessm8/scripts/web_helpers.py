import streamlit as st

def change_layout(title: str, layout: str = "centered"):
    st.set_page_config(layout=layout, page_title=title)