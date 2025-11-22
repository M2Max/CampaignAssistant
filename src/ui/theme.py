import streamlit as st


def inject_minimal_theme() -> None:
    """Apply a minimal, high-contrast Scandinavian-inspired theme."""
    st.markdown(
        """
        <style>
        :root {
            color-scheme: light dark;
        }
        .stApp {
            background-color: var(--background-color);
            color: var(--text-color);
        }
        section[data-testid="stSidebar"] {
            background: var(--secondary-background-color);
            background: color-mix(in srgb, var(--secondary-background-color) 90%, var(--background-color) 10%);
            color: var(--text-color);
            border-right: 1px solid color-mix(in srgb, var(--text-color) 8%, transparent);
        }
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stMarkdown {
            color: var(--text-color);
        }
        .stButton>button {
            background: var(--secondary-background-color);
            background: color-mix(in srgb, var(--primary-color) 12%, transparent);
            color: var(--text-color);
            border-radius: 10px;
            border: 1px solid color-mix(in srgb, var(--primary-color) 30%, transparent);
            backdrop-filter: blur(6px);
            transition: border-color 0.15s ease, transform 0.15s ease;
        }
        .stButton>button:hover {
            border-color: var(--primary-color);
            transform: translateY(-1px);
        }
        .minimal-card {
            background: var(--secondary-background-color);
            background: color-mix(in srgb, var(--secondary-background-color) 94%, var(--background-color) 6%);
            color: var(--text-color);
            padding: 1.4rem;
            border-radius: 18px;
            border: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent);
            box-shadow: 0 12px 28px color-mix(in srgb, var(--text-color) 6%, transparent);
        }
        div[data-testid="stChatMessageContent"] {
            background: var(--secondary-background-color);
            background: color-mix(in srgb, var(--secondary-background-color) 92%, var(--background-color) 8%);
            border-radius: 16px;
            border: 1px solid color-mix(in srgb, var(--text-color) 8%, transparent);
            padding: 1rem 1.25rem;
        }
        div[data-testid="stChatMessageContent"] p {
            color: var(--text-color);
        }
        [data-baseweb="input"] input,
        [data-baseweb="textarea"] textarea,
        .stTextInput input,
        .stTextArea textarea {
            background: var(--secondary-background-color);
            background: color-mix(in srgb, var(--secondary-background-color) 92%, var(--background-color) 8%);
            color: var(--text-color);
            border-radius: 12px;
        }
        .stTextInput input:focus,
        .stTextArea textarea:focus {
            border-color: color-mix(in srgb, var(--primary-color) 40%, transparent);
            box-shadow: 0 0 0 1px color-mix(in srgb, var(--primary-color) 25%, transparent);
        }
        .stMarkdown p,
        .stMarkdown li {
            color: var(--text-color);
        }
        section[data-testid="stSidebar"] .stAlert {
            background: color-mix(in srgb, var(--secondary-background-color) 90%, var(--background-color) 10%);
            border-radius: 12px;
        }
        /* Chat list styling */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label > div:first-child {
            display: none;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
            border: 1px solid color-mix(in srgb, var(--text-color) 12%, transparent);
            border-radius: 12px;
            padding: 0.6rem 0.85rem;
            margin-bottom: 0.4rem;
            transition: border-color 0.15s ease, background 0.15s ease;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
            border-color: color-mix(in srgb, var(--primary-color) 55%, transparent);
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label[aria-checked="true"] {
            border-color: var(--primary-color);
            background: color-mix(in srgb, var(--primary-color) 14%, transparent);
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label[aria-checked="true"] p {
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
