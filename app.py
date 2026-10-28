import streamlit as st
from pathlib import Path
from datetime import datetime
import ast
import csv
import re
import os
import json
import html
import hmac
import logging
from collections import Counter

import streamlit.components.v1 as components
import chromadb
from sentence_transformers import SentenceTransformer

# Keep diagnostics server-side; never log patient questions or answer text.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("radiation_oncology_chatbot")


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Radiation Oncology AI Assistant",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    html, body, [class*="css"] { font-family: 'Segoe UI', 'Inter', sans-serif; }

    .stApp { background: linear-gradient(180deg, #f6f9fd 0%, #eef4fa 100%); }
    .block-container { padding-top: 4.2rem !important; max-width: 1400px; }
    header[data-testid="stHeader"] { background: transparent; }
    .stApp .main p, .stApp .main li, .stApp .main span, .stApp .main label { color: #1f3350; }

    [class*="st-key-download_patient_guide"] button {
        background: linear-gradient(120deg, #0f55b8 0%, #1a72d4 100%) !important;
        border: 1.5px solid #0f55b8 !important; color: #fff !important; border-radius: 10px !important;
        font-weight: 700;
    }
    [class*="st-key-download_patient_guide"] button p { color: #fff !important; }

    /* ---------------- SIDEBAR ---------------- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d4a9a 0%, #0a3a7c 45%, #072a5c 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] label { color: #eaf1f8; }

    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background: #ffffff !important; border-radius: 10px !important; border: 1px solid #cfe0f1 !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] * { color: #12365e !important; }
    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] label p {
        font-size: 0.78rem; letter-spacing: 0.06em; color: #cfe3f7 !important;
    }

    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.35);
        border-radius: 10px; color: #ffffff !important; font-weight: 600; transition: all .2s ease;
    }
    section[data-testid="stSidebar"] .stButton > button p { color: #ffffff !important; }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(47,155,214,0.30); border-color: #5fb8ec; transform: translateY(-1px);
    }

    .sb-brand {
        padding: 0.9rem 1rem; border-radius: 14px;
        background: linear-gradient(135deg, rgba(47,155,214,0.35) 0%, rgba(30,80,200,0.35) 100%);
        border: 1px solid rgba(255,255,255,0.18); margin-bottom: 0.9rem;
        display: flex; align-items: center; gap: .75rem;
    }
    .sb-logo { font-size: 2rem; line-height: 1; }
    .sb-title { font-size: 1.3rem; font-weight: 800; color: #fff; line-height: 1.15; }
    .sb-sub { font-size: .8rem; color: #d7e9f8; margin-top: .15rem; }

    .sb-section-title { font-size: .72rem; letter-spacing: .08em; text-transform: uppercase;
        color: #b9d4ee; margin: 1.1rem 0 .5rem .2rem; }
    .sb-pill { display: flex; align-items: center; gap: .6rem; padding: .6rem .75rem; margin-bottom: .5rem;
        border-radius: 10px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.28);
        font-size: .84rem; color: #eaf1f8; }
    .sb-pill-icon { width: 1.3rem; text-align: center; }
