import streamlit as st
import requests
import pandas as pd
import os
import tempfile
from gtts import gTTS

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="VolunteerSphere — AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  GLOBAL CSS — Bioluminescent Deep-Ocean Theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {
  --bg-deep:    #020d18;
  --bg-mid:     #041628;
  --bg-card:    rgba(4, 28, 54, 0.85);
  --accent-1:   #00e5ff;
  --accent-2:   #00ff9d;
  --accent-3:   #7b61ff;
  --accent-hot: #ff4d6d;
  --text-main:  #e0f4ff;
  --text-muted: #7aadcc;
  --border:     rgba(0,229,255,0.15);
  --glow-1:     0 0 20px rgba(0,229,255,0.25);
  --radius-lg:  18px;
  --radius-md:  12px;
  --radius-sm:  8px;
}

* { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg-deep) !important;
  font-family: 'DM Sans', sans-serif;
  color: var(--text-main);
}

.stApp {
  background: var(--bg-deep) !important;
  background-image:
    radial-gradient(ellipse 70% 50% at 15% 0%, rgba(0,229,255,0.07) 0%, transparent 60%),
    radial-gradient(ellipse 50% 40% at 85% 100%, rgba(123,97,255,0.09) 0%, transparent 60%) !important;
}

.block-container {
  padding: 1.5rem 2.5rem !important;
  max-width: 900px !important;
  margin: 0 auto !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #020d18 0%, #041628 100%) !important;
  border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color: var(--text-main) !important; }

/* Typography */
h1, h2, h3 {
  font-family: 'Syne', sans-serif !important;
  letter-spacing: -0.02em;
  color: var(--text-main) !important;
}

/* Chat input */
.stChatInput textarea {
  background: rgba(0,229,255,0.05) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  color: var(--text-main) !important;
  font-family: 'DM Sans', sans-serif !important;
}
.stChatInput textarea:focus {
  border-color: var(--accent-1) !important;
  box-shadow: var(--glow-1) !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
  background: transparent !important;
  border: none !important;
  padding: 4px 0 !important;
}

/* Buttons */
.stButton > button {
  background: linear-gradient(135deg, var(--accent-1), var(--accent-3)) !important;
  color: #020d18 !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 700 !important;
  font-size: 13px !important;
  letter-spacing: 0.05em;
  border: none !important;
  border-radius: var(--radius-md) !important;
  padding: 8px 18px !important;
  transition: all 0.25s ease !important;
  box-shadow: 0 4px 20px rgba(0,229,255,0.25) !important;
}
.stButton > button:hover {
  transform: translateY(-2px) scale(1.02) !important;
  box-shadow: 0 8px 30px rgba(0,229,255,0.45) !important;
}

/* Toggles / checkboxes */
.stCheckbox label { color: var(--text-muted) !important; font-size: 13px !important; }

/* Selectbox */
.stSelectbox [data-baseweb="select"] > div {
  background: rgba(0,229,255,0.05) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  color: var(--text-main) !important;
}

/* Text inputs */
.stTextInput input {
  background: rgba(0,229,255,0.05) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  color: var(--text-main) !important;
}

/* Alerts */
.stSuccess {
  background: rgba(0,255,157,0.08) !important;
  border: 1px solid rgba(0,255,157,0.3) !important;
  border-radius: var(--radius-md) !important;
}
.stInfo {
  background: rgba(0,229,255,0.08) !important;
  border: 1px solid rgba(0,229,255,0.3) !important;
  border-radius: var(--radius-md) !important;
}

/* Audio */
audio {
  filter: invert(1) hue-rotate(180deg) !important;
  border-radius: var(--radius-md) !important;
  width: 100% !important;
  margin-top: 8px;
}

/* Divider */
hr {
  border: none !important;
  height: 1px !important;
  background: var(--border) !important;
  margin: 20px 0 !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: rgba(0,229,255,0.2); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CONFIG & LOAD
# ─────────────────────────────────────────────
API_KEY   = os.getenv("API_KEY")
DATA_FILE = "AI csv .xlsx"

@st.cache_data
def load_data():
    try:
        return pd.read_excel(DATA_FILE)
    except:
        return pd.DataFrame()

data = load_data()

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are VolunteerBot — a warm, knowledgeable AI assistant for VolunteerSphere,
an NGO discovery platform focused on India. You help users:
- Find NGOs by location, cause, or eligibility
- Understand how to get started with volunteering
- Learn about social causes and their impact
- Get motivated and take action

You are trained to answer all kinds of questions including:
- How can I volunteer? / What is an NGO? / How to join an NGO?
- NGOs in Delhi / Noida / Gurgaon / Mumbai and other cities
- Suggest NGOs for education / healthcare / environment / women safety / mental health / child welfare
- Can students join NGOs without experience?
- Is volunteering paid or unpaid? / Do NGOs provide certificates?
- Can I volunteer online? / Can I work part-time as a volunteer?
- How do I verify if an NGO is genuine? / Are NGOs safe to work with?
- Tell me about specific NGOs like CRY, Goonj, WWF India, Pratham, Teach for India
- Compare NGOs / Which NGO is best for beginners?
- What skills are needed for volunteering?
- How do NGOs get funding? / Can I start my own NGO?
- What will I learn from NGO work? / Will volunteering help my resume?
- How many hours should I volunteer per week?
- Can introverts work in NGOs? / Can I volunteer from home?

IMPORTANT RULES:
- Always use the NGO dataset provided to give specific, accurate NGO names and details
- When user asks for NGOs by city or cause, list matching ones from the dataset with their details
- Keep replies concise (3-5 sentences) unless user asks for detail
- Be encouraging, empathetic, and action-oriented
- Use simple bullet points when listing NGOs or steps
- Always end with a follow-up question or a call to action
- If asked about a specific NGO from the dataset, give its name, location, work, and contact"""

# Pass the FULL dataset to AI so it can answer questions about all 45 NGOs
DATASET_CONTEXT = data.to_string(index=False) if not data.empty else "Dataset not loaded."

QUICK_PROMPTS = [
    "🏥 Healthcare NGOs in Delhi",
    "🎓 Education volunteering for students",
    "🌿 Environment NGOs near Mumbai",
    "👩 Women empowerment organizations",
    "💻 Tech volunteering opportunities",
    "🧠 Mental health support NGOs",
    "🍽️ Hunger relief organizations",
    "🐾 Animal welfare NGOs",
]

def call_ai(messages):
    if not API_KEY:
        return "⚠️ API Key not configured. Please set the API_KEY environment variable."
    url     = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    # Use the model chosen from sidebar dropdown, default to gpt-4o-mini
    selected_model = st.session_state.get("model_select", "openai/gpt-4o-mini")

    body    = {
        "model": selected_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT + f"\n\n--- FULL NGO DATABASE (use this to answer questions) ---\n{DATASET_CONTEXT}"}
        ] + messages,
        "max_tokens": 600
    }
    try:
        res  = requests.post(url, headers=headers, json=body, timeout=25)
        data_resp = res.json()
        return data_resp["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Error: {e}"


def speak_text(text):
    try:
        tts = gTTS(text[:500])
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tmp.name)
        return tmp.name
    except:
        return None


def dataset_lookup(query):
    """Quick dataset search to show alongside AI response."""
    if data.empty:
        return None
    q = query.lower()
    results = data.copy()
    filtered = False

    for city in ["delhi","noida","gurgaon","mumbai","bangalore","chennai",
                 "kolkata","hyderabad","pune","jaipur","chandigarh","ludhiana"]:
        if city in q:
            results = results[results["Location"].str.contains(city, case=False, na=False)]
            filtered = True; break

    cause_map = {
        "education":"Education","health":"Healthcare","environment":"Environment",
        "women":"Women","tech":"Technology","mental":"Mental Health",
        "child":"Children","animal":"Animal","hunger":"Food","food":"Food",
        "disability":"Disability","senior":"Elderly","elder":"Elderly"
    }
    for kw, val in cause_map.items():
        if kw in q:
            results = results[results["Work"].str.contains(val, case=False, na=False)]
            filtered = True; break

    return results.head(5) if (filtered and not results.empty) else None


def render_user_bubble(text):
    st.markdown(f"""
    <div style="
        display:flex; justify-content:flex-end; margin:10px 0;
    ">
        <div style="
            max-width:75%;
            background: linear-gradient(135deg, rgba(0,229,255,0.15), rgba(123,97,255,0.15));
            border: 1px solid rgba(0,229,255,0.25);
            border-radius: 18px 18px 4px 18px;
            padding: 12px 18px;
            font-size: 14px;
            color: #e0f4ff;
            line-height: 1.6;
            box-shadow: 0 4px 16px rgba(0,229,255,0.1);
        ">{text}</div>
        <div style="
            width:34px; height:34px; border-radius:50%;
            background: linear-gradient(135deg,#00e5ff,#7b61ff);
            display:flex; align-items:center; justify-content:center;
            font-size:15px; margin-left:10px; flex-shrink:0;
            box-shadow: 0 0 12px rgba(0,229,255,0.4);
        ">👤</div>
    </div>
    """, unsafe_allow_html=True)


def render_bot_bubble(text, show_voice=False, idx=None):
    # Convert markdown-style **bold** for display
    display_text = text.replace("**","<b>",1)
    # Simple bold toggle
    bold_open = True
    out = ""
    for ch in text:
        out += ch
    # Just render as-is in the bubble
    st.markdown(f"""
    <div style="
        display:flex; align-items:flex-start; margin:10px 0;
    ">
        <div style="
            width:34px; height:34px; border-radius:50%;
            background: linear-gradient(135deg,#00ff9d,#00e5ff);
            display:flex; align-items:center; justify-content:center;
            font-size:15px; margin-right:10px; flex-shrink:0;
            box-shadow: 0 0 12px rgba(0,255,157,0.4);
        ">🤖</div>
        <div style="
            max-width:80%;
            background: rgba(4,28,54,0.9);
            border: 1px solid rgba(0,255,157,0.2);
            border-radius: 4px 18px 18px 18px;
            padding: 14px 18px;
            font-size: 14px;
            color: #e0f4ff;
            line-height: 1.7;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            white-space: pre-wrap;
        ">{text}</div>
    </div>
    """, unsafe_allow_html=True)

    if show_voice and idx is not None:
        if st.button("🔊 Listen", key=f"voice_{idx}", help="Read this response aloud"):
            audio_path = speak_text(text)
            if audio_path:
                st.audio(audio_path)


def render_ngo_cards_mini(df):
    if df is None or df.empty:
        return
    st.markdown("""
    <div style="
        margin: 8px 0 4px 44px;
        font-family:'Syne',sans-serif;
        font-size:11px;letter-spacing:0.1em;
        text-transform:uppercase;color:#7aadcc;
    ">📋 Matching NGOs from Database</div>
    """, unsafe_allow_html=True)
    for _, row in df.iterrows():
        st.markdown(f"""
        <div style="
            margin:6px 0 6px 44px;
            background:rgba(0,229,255,0.05);
            border:1px solid rgba(0,229,255,0.15);
            border-radius:10px;padding:10px 14px;
            font-size:13px;color:#a8c8e0;
        ">
            <b style="color:#e0f4ff;">🏛️ {row.get('NGO','—')}</b><br>
            <span style="color:#7aadcc;">
                📍 {row.get('Location','—')} &nbsp;|&nbsp;
                🎯 {row.get('Work','—')} &nbsp;|&nbsp;
                👤 {row.get('Eligibility','Open')}
            </span>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = False

if "show_dataset" not in st.session_state:
    st.session_state.show_dataset = True

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 0 8px;">
        <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:800;
            background:linear-gradient(90deg,#00e5ff,#00ff9d);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            VolunteerSphere
        </div>
        <div style="color:#7aadcc;font-size:11px;letter-spacing:0.1em;
            text-transform:uppercase;margin-top:2px;">
            AI Chatbot
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Settings
    st.markdown("""
    <div style="font-family:'Syne',sans-serif;font-size:11px;letter-spacing:0.1em;
        text-transform:uppercase;color:#7aadcc;margin-bottom:10px;">
        ⚙️ Settings
    </div>
    """, unsafe_allow_html=True)

    st.session_state.voice_enabled  = st.checkbox("🔊 Voice on every reply",  value=st.session_state.voice_enabled)
    st.session_state.show_dataset   = st.checkbox("📋 Show matching NGO cards", value=st.session_state.show_dataset)

    model_choice = st.selectbox(
        "AI Model",
        ["openai/gpt-4o-mini", "openai/gpt-3.5-turbo", "anthropic/claude-3-haiku"],
        key="model_select"
    )

    st.markdown("---")

    # Quick prompts
    st.markdown("""
    <div style="font-family:'Syne',sans-serif;font-size:11px;letter-spacing:0.1em;
        text-transform:uppercase;color:#7aadcc;margin-bottom:10px;">
        ⚡ Quick Questions
    </div>
    """, unsafe_allow_html=True)

    for prompt in QUICK_PROMPTS:
        if st.button(prompt, key=f"quick_{prompt}", use_container_width=True):
            st.session_state.messages.append({"role":"user","content":prompt})
            with st.spinner("Thinking..."):
                reply = call_ai(st.session_state.messages)
            st.session_state.messages.append({"role":"assistant","content":reply})
            st.rerun()

    st.markdown("---")

    # Stats
    st.markdown(f"""
    <div style="color:#7aadcc;font-size:12px;line-height:1.8;">
        💬 Messages: <b style="color:#00e5ff;">{len(st.session_state.messages)}</b><br>
        🏛️ NGOs loaded: <b style="color:#00ff9d;">{len(data)}</b>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("""
    <div style="color:#7aadcc;font-size:11px;text-align:center;margin-top:16px;line-height:1.6;">
        Built with ❤️ using Streamlit<br>
        <span style="color:#00e5ff;">AI + Voice + NGO Data</span>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style="
    padding:36px 32px 28px;
    margin-bottom:24px;
    border-radius:22px;
    background: linear-gradient(135deg,
        rgba(0,229,255,0.07) 0%,
        rgba(4,22,40,0.9) 45%,
        rgba(0,255,157,0.06) 100%);
    border:1px solid rgba(0,229,255,0.18);
    box-shadow: 0 0 50px rgba(0,229,255,0.06), inset 0 1px 0 rgba(255,255,255,0.05);
    position:relative; overflow:hidden;
">
    <div style="position:absolute;top:-50px;right:-50px;width:180px;height:180px;
        border-radius:50%;
        background:radial-gradient(circle,rgba(0,229,255,0.1),transparent 70%);
        pointer-events:none;"></div>

    <div style="display:flex;align-items:center;gap:14px;margin-bottom:10px;">
        <span style="font-size:36px;filter:drop-shadow(0 0 10px rgba(0,229,255,0.6));">🤖</span>
        <div>
            <div style="
                font-family:'Syne',sans-serif;font-size:clamp(20px,3.5vw,30px);
                font-weight:800;letter-spacing:-0.03em;
                background:linear-gradient(90deg,#00e5ff,#00ff9d);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            ">VolunteerBot</div>
            <div style="color:#7aadcc;font-size:12px;letter-spacing:0.1em;
                text-transform:uppercase;margin-top:2px;">
                AI-Powered NGO Assistant
            </div>
        </div>
    </div>
    <p style="color:#a8c8e0;font-size:14px;max-width:520px;line-height:1.7;margin:0;">
        Ask me anything about NGOs, volunteering, social causes, or how to make an impact.
        I can search our database and give you personalised guidance.
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CHAT HISTORY
# ─────────────────────────────────────────────
if not st.session_state.messages:
    # Welcome state
    st.markdown("""
    <div style="
        text-align:center;padding:40px 24px;
        background:rgba(4,28,54,0.5);
        border:1px dashed rgba(0,229,255,0.15);
        border-radius:20px;margin-bottom:16px;
    ">
        <div style="font-size:40px;margin-bottom:12px;">💬</div>
        <div style="font-family:'Syne',sans-serif;font-size:17px;font-weight:700;
            color:#e0f4ff;margin-bottom:8px;">
            Start a conversation
        </div>
        <div style="color:#7aadcc;font-size:13px;max-width:380px;margin:0 auto;line-height:1.6;">
            Type a question below or pick a quick prompt from the sidebar.
            I'll search the NGO database and give you AI-powered guidance.
        </div>
    </div>

    <div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-bottom:20px;">
        <div style="background:rgba(0,229,255,0.07);border:1px solid rgba(0,229,255,0.2);
            border-radius:20px;padding:6px 14px;font-size:12px;color:#00e5ff;">
            🏥 Healthcare NGOs in Delhi
        </div>
        <div style="background:rgba(0,255,157,0.07);border:1px solid rgba(0,255,157,0.2);
            border-radius:20px;padding:6px 14px;font-size:12px;color:#00ff9d;">
            🎓 Education volunteering
        </div>
        <div style="background:rgba(123,97,255,0.07);border:1px solid rgba(123,97,255,0.2);
            border-radius:20px;padding:6px 14px;font-size:12px;color:#b39dff;">
            🌿 Environment NGOs Mumbai
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # Render all messages
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            render_user_bubble(msg["content"])
        else:
            show_voice = st.session_state.voice_enabled or (i == len(st.session_state.messages) - 1)
            render_bot_bubble(msg["content"], show_voice=True, idx=i)

            # Show dataset cards for latest assistant message
            if st.session_state.show_dataset and i == len(st.session_state.messages) - 1:
                # Find the user message that triggered this
                if i > 0 and st.session_state.messages[i-1]["role"] == "user":
                    user_q = st.session_state.messages[i-1]["content"]
                    ds_results = dataset_lookup(user_q)
                    render_ngo_cards_mini(ds_results)

            # Auto voice for latest message
            if st.session_state.voice_enabled and i == len(st.session_state.messages) - 1:
                audio_path = speak_text(msg["content"])
                if audio_path:
                    st.audio(audio_path)

# ─────────────────────────────────────────────
#  CHAT INPUT
# ─────────────────────────────────────────────
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# Typing area
col_input, col_send = st.columns([5, 1])

with col_input:
    user_message = st.chat_input(
        placeholder="Ask about NGOs, volunteering opportunities, social causes..."
    )

if user_message:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_message})

    # Get AI reply
    with st.spinner(""):
        st.markdown("""
        <div style="
            display:flex;align-items:center;gap:10px;
            padding:10px 18px;margin:8px 0;
            background:rgba(4,28,54,0.7);
            border:1px solid rgba(0,229,255,0.1);
            border-radius:12px;font-size:13px;color:#7aadcc;
            width:fit-content;
        ">
            <span style="animation:pulse 1s infinite;display:inline-block;">●</span>
            <span style="animation:pulse 1s 0.2s infinite;display:inline-block;">●</span>
            <span style="animation:pulse 1s 0.4s infinite;display:inline-block;">●</span>
            &nbsp; VolunteerBot is thinking...
        </div>
        <style>
        @keyframes pulse {
            0%,100%{opacity:0.3;transform:scale(0.8)}
            50%{opacity:1;transform:scale(1)}
        }
        </style>
        """, unsafe_allow_html=True)

        # Build message history for API (last 10 turns to avoid token overflow)
        api_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[-10:]
        ]
        reply = call_ai(api_messages)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="
    display:flex;justify-content:space-between;align-items:center;
    flex-wrap:wrap;gap:12px;
    color:#7aadcc;font-size:12px;padding:4px 0 12px;
">
    <div>
        <span style="color:#00e5ff;font-family:'Syne',sans-serif;font-weight:700;">VolunteerSphere AI</span>
        &nbsp;·&nbsp; Powered by GPT-4o-mini via OpenRouter
    </div>
    <div style="display:flex;gap:16px;">
        <span>🏛️ NGO Database Active</span>
        <span style="color:#00ff9d;">● Online</span>
    </div>
</div>
""", unsafe_allow_html=True)
