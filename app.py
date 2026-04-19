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

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

/* Glass container */
.block-container {
    background: rgba(255, 255, 255, 0.05);
    padding: 30px;
    border-radius: 20px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(0,0,0,0.6);
}

/* Input */
.stTextInput input {
    background-color: rgba(255,255,255,0.1);
    color: white;
}

/* Button */
.stButton button {
    background: linear-gradient(90deg, #ff6a88, #ff99ac);
    color: white;
}

/* Cards */
.card {
    background: rgba(255,255,255,0.1);
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 8px;
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
<h1 style='text-align:center;'>🌍 AI Volunteer Impact Platform</h1>
<p style='text-align:center;'>AI + Voice + Emotion + Map + Image</p>
""", unsafe_allow_html=True)

# ---------------- HISTORY ----------------
if "history" not in st.session_state:
    st.session_state["history"] = []

# ---------------- INPUT ----------------
col1, col2 = st.columns([3,1])

with col1:
    user_input = st.text_input("Ask your question:")

with col2:
    st.write("")
    st.write("")
    search_btn = st.button("🔍 Search")

# ---------------- IMAGE BUTTON ----------------
if st.button("🎨 Generate Image"):
    if user_input:
        generate_image(user_input)

# ---------------- MODE ----------------
mode = st.radio("Choose mode:", ["AI Explanation","Dataset Search","Smart Search"])

st.markdown("---")

# ---------------- MAIN ----------------
def run_query(query):

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
    st.session_state["history"].insert(0, f"{mode}: {user_input}")
    st.session_state["history"] = st.session_state["history"][:10]
    run_query(user_input)

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 📜 Search History")

if len(st.session_state["history"]) == 0:
    st.sidebar.write("No searches yet")
else:
    for item in st.session_state["history"]:
        st.sidebar.markdown(f"<div class='card'>{item}</div>", unsafe_allow_html=True)
