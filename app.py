"""Premium Streamlit UI for the UNLOX LangChain Q&A mini-project."""
from __future__ import annotations

import html
from pathlib import Path

import streamlit as st
from chatbot import (
    TOPICS, ChatbotConfigurationError, ChatbotResponseError,
    answer_question, build_chain, load_settings, save_local_settings,
    save_local_model, test_connection, DEFAULT_MODEL, AVAILABLE_MODELS,
    validate_question,
)

st.set_page_config(
    page_title="NovaLearn • AI Study Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { color-scheme: dark; }
html, body, [class*="css"], [data-testid="stApp"] { font-family: 'DM Sans', sans-serif; }
[data-testid="stApp"] {
  color: #edf1ff;
  background:
    radial-gradient(ellipse 44% 48% at 87% 15%, rgba(18,140,207,.18), transparent 75%),
    radial-gradient(ellipse 50% 44% at 30% 5%, rgba(130,54,216,.18), transparent 75%),
    radial-gradient(ellipse 54% 45% at 72% 94%, rgba(93,50,193,.16), transparent 74%),
    #090e22;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stMainBlockContainer"] { max-width: 1140px; padding: 2.2rem 2.7rem 7rem; }
[data-testid="stSidebar"] {
 background: linear-gradient(165deg, #161a37 0%, #111531 60%, #1b1740 100%);
 border-right: 1px solid rgba(176,160,255,.15);
}
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] { padding: 1.45rem 1.1rem 2rem; }
.brand { display:flex; align-items:center; gap:12px; padding: 8px 5px 26px; }
.brand-icon { width:49px; height:49px; border-radius:16px; display:grid; place-items:center;
 background: linear-gradient(145deg,#7657ea,#23b2ed); font-size:25px; box-shadow:0 10px 28px #764df244; }
.brand-name { font: 700 18px 'Space Grotesk',sans-serif; color:#fff; letter-spacing:-.3px; }
.brand-sub { color:#b5aaff; font-size:12px; margin-top:2px; }
.sidebar-panel { border:1px solid #8075bc35; border-radius:18px; background:#ffffff08; padding:17px 15px 12px; margin-bottom:18px; }
.side-title { color:#f1edff; font-weight:800; font-size:18px; margin-bottom:9px; }
.side-small { color:#aeb7d6; font-size:13px; line-height:1.7; }
.feature { padding:5px 0; color:#dcdaf2; font-size:13px; }
.feature:before { content:'✓'; display:inline-grid; place-items:center; width:20px; height:20px;
 background:#6651ac; border-radius:50%; margin-right:10px; color:white; font-size:12px; }
.side-rule { border-top:1px solid #aaa0da2d; margin:20px 0; }
[data-testid="stSidebar"] label { color:#d9d4fb !important; font-weight:700; }
[data-testid="stSidebar"] [data-baseweb="select"] > div { background:#242342 !important; border:1px solid #7772b9 !important; border-radius:12px !important; }
[data-testid="stSidebar"] [data-testid="stButton"] button { border-radius:12px; border:1px solid #7667c6;
 background:linear-gradient(105deg,#8149d8,#1699cf); color:white; font-weight:700; min-height:44px; }
.hero { text-align:center; padding-top:13px; padding-bottom:26px; }
.hero-icon { margin:0 auto 18px; display:grid;place-items:center; font-size:45px; width:90px;height:90px;
 border-radius:26px; background:linear-gradient(145deg,#6c47a96c,#006baf70);
 border:1px solid #a18afc91; box-shadow:0 16px 50px #6735db34; }
.hero h1 { font: 700 clamp(30px,4vw,52px)/1.12 'Space Grotesk',sans-serif;
 letter-spacing:-1.8px; color:#f7f7ff; margin:0 0 12px; }
.hero h1 span { background:linear-gradient(90deg,#ba75ff,#44d5f1); background-clip:text; -webkit-background-clip:text; color:transparent; }
.hero .tagline { color:#c8d0e8; font-size:17px; margin:0 0 17px; }
.pill { display:inline-block; background:#ffffff0d; border:1px solid #a78bfa51; color:#c8c4f1;
 border-radius:999px; font-size:12px; padding:8px 15px; }
.section-heading { text-align:center; color:#e6e4fc; font-size:16px; font-weight:800;
 margin:18px 0 16px; }
.section-heading span { color:#ab7aff; }
.status { padding:13px 17px; border-radius:14px; margin-bottom:13px; font-size:13px; line-height:1.5; }
.status-warning { background:#8e284224; border:1px solid #ff759366; color:#ffc6d0; }
.status-info { background:#0f8cda20; border:1px solid #4dc9ff70; color:#b7e9ff; }
.status-ok { background:#208b7750; border:1px solid #42d4b274; color:#c7fff0; }
.suggestion { border:1px solid #9992f04a; background:linear-gradient(135deg,#26294bde,#1b2343d6);
 padding:16px; border-radius:17px; min-height:103px; margin-bottom:5px; }
.suggestion-icon { color:#b99cff;font-size:24px; margin-bottom:9px; }
.suggestion-title {font-size:14px;font-weight:800;color:#f0eaff;margin:0 0 7px;}
.suggestion-sub {font-size:12px;color:#bfc7e4; line-height:1.5;}
[data-testid="stMain"] [data-testid="stButton"] button[kind="secondary"] {
 background: #242947c9; border: 1px solid #7b75b65c; color:#e9e9fc; border-radius:13px;
 text-align:left; min-height:45px; font-weight:600; white-space:normal;
}
[data-testid="stMain"] [data-testid="stButton"] button[kind="secondary"]:hover {
 background:#3d326b; border-color:#bd92ff; color:#fff;
}
[data-testid="stChatMessage"] {background:#181d39aa;border:1px solid #8171b72b;border-radius:15px;margin:9px 0;}
[data-testid="stChatInput"] { border-radius:18px !important; background:#222746 !important; border:1px solid #9888e6a8 !important; box-shadow:0 0 28px #8b5de01d; }
[data-testid="stChatInput"] textarea {color:#fff !important;}
[data-testid="stChatInput"] button { color:#a6aeff !important; }
[data-testid="stBottom"] { background:linear-gradient(0deg,#0b0f24 48%,transparent) !important; }
.footer {color:#7986a6; font-size:12px; text-align:center; padding:27px 0;}
@media(max-width:800px) {
 [data-testid="stMainBlockContainer"] { padding:1.4rem 1rem 7rem; }
 .hero h1 {letter-spacing:-.6px;}
 .hero .tagline {font-size:14px;}
 .hero-icon {width:72px;height:72px;font-size:36px;}
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# Load configuration *before* rendering the sidebar; saving it triggers a rerun.
settings = None
try:
    settings = load_settings()
except ChatbotConfigurationError:
    pass

if "connection_status" not in st.session_state:
    st.session_state.connection_status = "untested"
if "connection_error" not in st.session_state:
    st.session_state.connection_error = ""
if "connection_signature" not in st.session_state:
    st.session_state.connection_signature = ""
# A status from an older key or model must never be treated as verified.
import hashlib
signature = hashlib.sha256(
    ((settings.api_key if settings else "") + ":" + (settings.model if settings else "")).encode("utf-8")
).hexdigest()
if st.session_state.connection_signature != signature:
    st.session_state.connection_status = "untested"
    st.session_state.connection_error = ""
    st.session_state.connection_signature = signature

if "messages" not in st.session_state:
    st.session_state.messages = []
if "topic" not in st.session_state:
    st.session_state.topic = "Study Assistant"

with st.sidebar:
    st.markdown('''<div class="brand"><div class="brand-icon">🎓</div><div>
      <div class="brand-name">NovaLearn AI</div><div class="brand-sub">Your personal study companion</div>
      </div></div>''', unsafe_allow_html=True)
    st.markdown('<div class="side-title">⚙️ &nbsp; Workspace</div>', unsafe_allow_html=True)
    topic = st.selectbox("Assistant topic", list(TOPICS), index=list(TOPICS).index(st.session_state.topic))
    if topic != st.session_state.topic:
        st.session_state.topic = topic
        st.session_state.messages = []
    st.markdown('''<div class="sidebar-panel"><div class="side-title">✦ &nbsp; What I can do</div>
      <p class="side-small">Ask clear questions and learn through tailored explanations, code examples and interview practice.</p>
      <div class="side-rule"></div>
      <div class="feature">Concept explanations</div>
      <div class="feature">Python doubt solving</div>
      <div class="feature">Interview preparation</div>
      <div class="feature">Study & revision support</div></div>''', unsafe_allow_html=True)
    if st.button("↻  Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown('<div class="side-rule"></div>', unsafe_allow_html=True)
    st.markdown('### 🔑 Gemini connection')
    if settings is not None:
        st.caption(f"Key loaded from configuration • Model: `{settings.model}`")
        if st.session_state.connection_status == "verified":
            st.success("Connected to Gemini")
        elif st.session_state.connection_status == "failed":
            st.error(st.session_state.connection_error)
        else:
            st.info("Key found, but not tested yet")
        if st.button("🔌 Test API connection", use_container_width=True):
            with st.spinner("Checking Gemini connectivity…"):
                try:
                    test_connection(settings)
                except (ChatbotResponseError, ChatbotConfigurationError) as exc:
                    st.session_state.connection_status = "failed"
                    st.session_state.connection_error = str(exc)
                except Exception:
                    st.session_state.connection_status = "failed"
                    st.session_state.connection_error = "Could not start Gemini request. Check installed packages."
                else:
                    st.session_state.connection_status = "verified"
                    st.session_state.connection_error = ""
            st.rerun()
    else:
        st.warning("No API key configured")
    with st.expander("🔐 Add / replace Gemini API key", expanded=settings is None):
        st.caption("Paste a valid Gemini Developer API key. It is stored only in this computer's .env file, not in source code.")
        with st.form("save_key_form", clear_on_submit=True):
            new_key = st.text_input("API key", type="password", placeholder="Paste key here")
            selected_model = st.selectbox(
                "Gemini model",
                options=list(AVAILABLE_MODELS),
                index=list(AVAILABLE_MODELS).index(settings.model) if settings and settings.model in AVAILABLE_MODELS else 0,
            )
            submitted = st.form_submit_button("💾 Save key on this PC", use_container_width=True)
        if submitted:
            try:
                save_local_settings(new_key, selected_model)
            except ChatbotConfigurationError as exc:
                st.error(str(exc))
            except OSError:
                st.error("Could not write .env. Check that the project folder allows file changes.")
            else:
                st.rerun()
        st.caption("For safety, rotate any API key previously shared in a chat or screenshot.")
    if settings and settings.model in AVAILABLE_MODELS:
        with st.expander("⚙️ Change Gemini model", expanded=False):
            model_choice = st.selectbox("Model", AVAILABLE_MODELS, index=AVAILABLE_MODELS.index(settings.model), key="model_change")
            if st.button("Apply model", use_container_width=True, disabled=model_choice == settings.model):
                try:
                    save_local_model(model_choice)
                except (OSError, ChatbotConfigurationError):
                    st.error("Could not update model in local .env.")
                else:
                    st.rerun()
    st.caption("🔒 Your API key is excluded from the GitHub ZIP via .gitignore")

st.markdown('''<section class="hero">
    <div class="hero-icon">🎓</div>
    <h1>AI Question-Answering <span>Chatbot</span></h1>
    <p class="tagline">Your AI Study Assistant for Learning, Coding & Interviews</p>
    <div class="pill">✦ &nbsp; UNLOX LangChain Mini-Project &nbsp; • &nbsp; Powered by Gemini + LangChain</div>
    </section>''', unsafe_allow_html=True)

if settings is None:
    st.markdown('''<div class="status status-warning"><strong>⚠️ Gemini API key is not configured</strong><br>
    Open <b>🔐 Add / replace Gemini API key</b> in the left sidebar, paste your key, and click <b>Save key on this PC</b>.
    The app will refresh automatically.</div>
    <div class="status status-info">💡 No need to manually edit app.py. The app securely writes your local <code>.env</code> file.</div>''', unsafe_allow_html=True)
    with st.expander("Alternative: configure .env manually"):
        st.code('Copy-Item .env.example .env\nnotepad .env', language="powershell")
        st.code('GOOGLE_API_KEY=YOUR_OWN_KEY\nGEMINI_MODEL=gemini-3.5-flash-lite', language="ini")
        st.markdown("Generate / manage keys in [Google AI Studio](https://aistudio.google.com/apikey).")
elif st.session_state.connection_status == "verified":
    st.markdown('<div class="status status-ok">● &nbsp; Gemini connection tested successfully. Start chatting below.</div>', unsafe_allow_html=True)
elif st.session_state.connection_status == "failed":
    st.error(st.session_state.connection_error)
else:
    st.markdown('''<div class="status status-info">● &nbsp; Gemini key loaded. Select <b>Test API connection</b> in the sidebar to verify authentication, or try a question directly.</div>''', unsafe_allow_html=True)

PICKS = [
    ("⌘ Python Help", "Explain list comprehensions in Python with examples."),
    ("◈ Concept Clarity", "What is binary search? Explain with a simple example."),
    ("✧ Interview Prep", "Ask me five Python interview questions with answers."),
]
if not st.session_state.messages:
    st.markdown('<div class="section-heading"><span>✦</span> &nbsp; Start exploring with a question</div>', unsafe_allow_html=True)
    cards = st.columns(3)
    for col, (label, sample) in zip(cards, PICKS):
        with col:
            st.markdown(f'''<div class="suggestion"><div class="suggestion-icon">✦</div>
              <div class="suggestion-title">{html.escape(label)}</div>
              <div class="suggestion-sub">{html.escape(sample)}</div></div>''', unsafe_allow_html=True)
    st.write("")
    suggested = st.columns(3)
    example_question = None
    for col, (_, sample) in zip(suggested, PICKS):
        with col:
            if st.button("Try this question ↗", key="sample_" + str(PICKS.index((_, sample))), use_container_width=True, disabled=settings is None):
                example_question = sample
else:
    example_question = None

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask anything about Python, studies, or interviews…", disabled=settings is None)
question = question or example_question
if question:
    try:
        cleaned = validate_question(question)
    except ValueError as exc:
        st.warning(str(exc))
    else:
        previous = st.session_state.messages.copy()
        st.session_state.messages.append({"role": "user", "content": cleaned})
        with st.chat_message("user"):
            st.markdown(cleaned)
        with st.chat_message("assistant"):
            with st.spinner("Thinking through your question…"):
                try:
                    response = answer_question(build_chain(settings, topic), cleaned, topic, previous)
                except (ChatbotResponseError, ChatbotConfigurationError, ValueError) as exc:
                    st.error(str(exc))
                except Exception:
                    st.error("Unable to initialize the AI service. Verify the dependencies and model settings.")
                else:
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

st.markdown('<div class="footer">NovaLearn AI &nbsp; • &nbsp; UNLOX Mini-Project &nbsp; • &nbsp; Built with LangChain & Gemini</div>', unsafe_allow_html=True)
