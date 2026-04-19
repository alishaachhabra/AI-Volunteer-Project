import streamlit as st
import requests
import pandas as pd
import os
from transformers import pipeline
from gtts import gTTS
import tempfile
import folium
from streamlit_folium import st_folium

# ---------------- UI DESIGN ----------------
st.set_page_config(page_title="AI Volunteer Impact Platform", page_icon="🌍", layout="wide")
st.markdown("""
<style>

/* 🌌 Background */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

/* 📦 Main Container */
.block-container {
    padding: 2rem 3rem;
    background: rgba(255,255,255,0.05);
    max-width: 1000px;
    margin: auto;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.15);
    box-shadow: 0px 8px 30px rgba(0,0,0,0.3);
}

/* 📊 Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2027, #203a43);
    border-right: 1px solid rgba(255,255,255,0.1);
}

/* 🔤 Headings */
h1, h2, h3 {
    color: white;
    font-weight: 600;
}

/* 🧾 Input Box */
.stTextInput input {
    background: rgba(255,255,255,0.1);
    color: white;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.3);
    padding: 12px;
}

/* 🔘 Buttons */
.stButton button {
    background: linear-gradient(90deg, #ff758c, #ff7eb3);
    color: white;
    border-radius: 12px;
    padding: 10px 18px;
    font-weight: 600;
    border: none;
    transition: 0.3s;
}

.stButton button:hover {
    transform: scale(1.05);
    box-shadow: 0px 5px 15px rgba(255,118,140,0.4);
}

/* 📋 Cards (for history or NGO display) */
.card {
    background: rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 10px;
    border: 1px solid rgba(255,255,255,0.15);
    box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
}

/* 📊 Dataframe */
[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.1);
}

/* 📢 Success box */
.stSuccess {
    background-color: rgba(0,255,150,0.1) !important;
    border-left: 4px solid #00ff95;
}

/* ⚠ Error box */
.stError {
    background-color: rgba(255,0,0,0.1) !important;
    border-left: 4px solid red;
}

/* 💡 Info box */
.stInfo {
    background-color: rgba(0,150,255,0.1) !important;
    border-left: 4px solid #0096ff;
}

/* 🔊 Audio player spacing */
audio {
    margin-top: 10px;
}

/* ➖ Divider */
hr {
    border: none;
    height: 1px;
    background: rgba(255,255,255,0.2);
    margin: 20px 0;
}

</style>
""", unsafe_allow_html=True)




# ---------------- CONFIG ----------------
API_KEY = os.getenv("API_KEY")
DATA_FILE = "AI csv .xlsx"

# ---------------- LOAD ----------------
data = pd.read_excel(DATA_FILE)
sentiment_analyzer = pipeline("sentiment-analysis")

# ---------------- VOICE ----------------
def speak_text(text):
    tts = gTTS(text)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp.name)
    return tmp.name

# ---------------- AI ----------------
def call_ai(user_input):
    if not API_KEY:
        return "⚠️ API Key missing"

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You help users find NGOs and explain volunteering."},
            {"role": "user", "content": user_input}
        ]
    }

    try:
        res = requests.post(url, headers=headers, json=body)
        result = res.json()

        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        return "⚠️ AI error"
    except Exception as e:
        return str(e)

# ---------------- EMOTION ----------------
def detect_emotion(text):
    return sentiment_analyzer(text)[0]['label']

# ---------------- DATASET SEARCH ----------------
def dataset_search(user_input):
    result = data.copy()
    txt = user_input.lower()

    if "delhi" in txt:
        result = result[result["Location"].str.contains("Delhi", case=False)]
    if "noida" in txt:
        result = result[result["Location"].str.contains("Noida", case=False)]
    if "gurgaon" in txt:
        result = result[result["Location"].str.contains("Gurgaon", case=False)]

    if "education" in txt:
        result = result[result["Work"].str.contains("Education", case=False)]
    if "health" in txt:
        result = result[result["Work"].str.contains("Healthcare", case=False)]

    return result if not result.empty else None

# ---------------- SMART ----------------
def smart_search(user_input):
    if any(w in user_input.lower() for w in ["what","why","how"]):
        return {"ai": call_ai(user_input), "dataset": None}

    ds = dataset_search(user_input)
    if ds is not None:
        return {"ai": None, "dataset": ds}

    return {"ai": call_ai(user_input), "dataset": None}

# ---------------- MAP ----------------
def show_map(df):
    if df is None or df.empty:
        return

    if "Latitude" not in df.columns or "Longitude" not in df.columns:
        st.warning("Latitude/Longitude missing")
        return

    m = folium.Map(location=[28.61,77.23], zoom_start=6)

    for _, row in df.iterrows():
        try:
            folium.Marker(
                [float(row["Latitude"]), float(row["Longitude"])],
                popup=row.get("NGO","NGO")
            ).add_to(m)
        except:
            continue

    st.subheader("🌍 NGO Map")
    st_folium(m, width=700, height=500)

# ---------------- IMAGE ----------------
def generate_image(prompt):
    try:
        query = prompt.replace(" ", "+")
        image_url = f"https://loremflickr.com/800/400/{query}"

        st.image(image_url, caption="🎨 AI Generated Image")

    except Exception as e:
        st.error(f"Image error: {e}")

# ---------------- HEADER ----------------
st.markdown("""
<div style="
    text-align:center;
    padding:30px 20px;
    margin: 20px auto;
    max-width: 900px;
    border-radius:18px;
    background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.15);
    box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
">
    <h1 style="margin-bottom:8px;">🌍 AI Volunteer Impact Platform</h1>
    <p style="font-size:15px; opacity:0.8;">
        ✨ AI + Voice + Emotion + Map + Image — Smart NGO Discovery Platform
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------- HISTORY ----------------
if "history" not in st.session_state:
    st.session_state["history"] = []

# ---------------- INPUT ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)

col1, col2 = st.columns([4,1])

with col1:
    user_input = st.text_input("Ask your question:")

with col2:
    st.write("")
    st.write("")
    search_btn = st.button("🔍 Search")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- IMAGE BUTTON ----------------
if st.button("🎨 Generate Image"):
    if user_input:
        generate_image(user_input)

# ---------------- MODE ----------------
mode = st.radio("Choose mode:", ["AI Explanation","Dataset Search","Smart Search"])

st.markdown("---")

# ---------------- MAIN ----------------
def run_query(query):
    mode = st.session_state.get("last_mode", "AI Explanation")

    emotion = detect_emotion(query)
    if emotion == "NEGATIVE":
        query += " suggest NGOs"
        st.info("💡 Emotion detected → suggesting help")

    if mode == "AI Explanation":
        res = call_ai(query)
        st.success(res)

        audio = speak_text(res)
        st.markdown("### 🔊 Listen to response")
        st.audio(audio)

    elif mode == "Dataset Search":
        res = dataset_search(query)

        if res is not None:
            st.dataframe(res)
            show_map(res)
        else:
            st.error("No NGOs found")

    elif mode == "Smart Search":
        res = smart_search(query)

        if res["ai"]:
            st.success(res["ai"])
            audio = speak_text(res["ai"])
            st.audio(audio)

        if res["dataset"] is not None:
            st.dataframe(res["dataset"])
            show_map(res["dataset"])

# ---------------- BUTTON ----------------
if search_btn and user_input:
    # Save history
    st.session_state["history"].insert(0, f"{mode}: {user_input}")
    st.session_state["history"] = st.session_state["history"][:10]

    # Save query for persistence (IMPORTANT FIX)
    st.session_state["last_query"] = user_input
    st.session_state["last_mode"] = mode
    if "last_query" in st.session_state:
        run_query(st.session_state["last_query"])
# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 📜 Search History")

if len(st.session_state["history"]) == 0:
    st.sidebar.write("No searches yet")
else:
    for item in st.session_state["history"]:
        st.sidebar.markdown(f"<div class='card'>{item}</div>", unsafe_allow_html=True)
