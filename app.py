import streamlit as st
import requests
import pandas as pd
import os
import datetime
import tempfile
from math import radians, sin, cos, sqrt, atan2
from transformers import pipeline
from gtts import gTTS
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="VolunteerSphere AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  GLOBAL CSS  –  Bioluminescent Deep-Ocean Theme
# ─────────────────────────────────────────────
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800\&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300\&display=swap');



/\* ── Root Variables ── \*/

:root {

&#x20; --bg-deep:    #020d18;

&#x20; --bg-mid:     #041628;

&#x20; --bg-card:    rgba(4, 28, 54, 0.85);

&#x20; --accent-1:   #00e5ff;

&#x20; --accent-2:   #00ff9d;

&#x20; --accent-3:   #7b61ff;

&#x20; --accent-hot: #ff4d6d;

&#x20; --text-main:  #e0f4ff;

&#x20; --text-muted: #7aadcc;

&#x20; --border:     rgba(0,229,255,0.15);

&#x20; --glow-1:     0 0 20px rgba(0,229,255,0.25);

&#x20; --glow-2:     0 0 20px rgba(0,255,157,0.25);

&#x20; --radius-lg:  18px;

&#x20; --radius-md:  12px;

&#x20; --radius-sm:  8px;

}



/\* ── Base ── \*/

\* { box-sizing: border-box; }



html, body, \[data-testid="stAppViewContainer"] {

&#x20; background: var(--bg-deep) !important;

&#x20; font-family: 'DM Sans', sans-serif;

&#x20; color: var(--text-main);

}



.stApp {

&#x20; background: var(--bg-deep) !important;

&#x20; background-image:

&#x20;   radial-gradient(ellipse 80% 50% at 20% -10%, rgba(0,229,255,0.08) 0%, transparent 60%),

&#x20;   radial-gradient(ellipse 60% 40% at 80% 110%, rgba(123,97,255,0.1) 0%, transparent 60%),

&#x20;   radial-gradient(ellipse 40% 30% at 50% 50%, rgba(0,255,157,0.04) 0%, transparent 70%) !important;

}



/\* ── Main block container ── \*/

.block-container {

&#x20; padding: 2rem 2.5rem !important;

&#x20; max-width: 1100px !important;

&#x20; margin: 0 auto !important;

}



/\* ── Sidebar ── \*/

section\[data-testid="stSidebar"] {

&#x20; background: linear-gradient(180deg, #020d18 0%, #041628 100%) !important;

&#x20; border-right: 1px solid var(--border) !important;

}

section\[data-testid="stSidebar"] \* {

&#x20; color: var(--text-main) !important;

}

section\[data-testid="stSidebar"] .stRadio label,

section\[data-testid="stSidebar"] .stSelectbox label {

&#x20; color: var(--text-muted) !important;

&#x20; font-size: 12px !important;

&#x20; letter-spacing: 0.08em;

&#x20; text-transform: uppercase;

}



/\* ── Typography ── \*/

h1, h2, h3 {

&#x20; font-family: 'Syne', sans-serif !important;

&#x20; letter-spacing: -0.02em;

&#x20; color: var(--text-main) !important;

}



/\* ── Inputs ── \*/

.stTextInput input, .stTextArea textarea {

&#x20; background: rgba(0,229,255,0.05) !important;

&#x20; border: 1px solid var(--border) !important;

&#x20; border-radius: var(--radius-md) !important;

&#x20; color: var(--text-main) !important;

&#x20; font-family: 'DM Sans', sans-serif !important;

&#x20; padding: 12px 16px !important;

&#x20; transition: border-color 0.3s, box-shadow 0.3s;

}

.stTextInput input:focus, .stTextArea textarea:focus {

&#x20; border-color: var(--accent-1) !important;

&#x20; box-shadow: var(--glow-1) !important;

&#x20; outline: none !important;

}

.stTextInput label, .stTextArea label {

&#x20; color: var(--text-muted) !important;

&#x20; font-size: 12px !important;

&#x20; letter-spacing: 0.08em;

&#x20; text-transform: uppercase;

&#x20; font-weight: 500;

}



/\* ── Buttons ── \*/

.stButton > button {

&#x20; background: linear-gradient(135deg, var(--accent-1), var(--accent-3)) !important;

&#x20; color: #020d18 !important;

&#x20; font-family: 'Syne', sans-serif !important;

&#x20; font-weight: 700 !important;

&#x20; font-size: 14px !important;

&#x20; letter-spacing: 0.05em;

&#x20; border: none !important;

&#x20; border-radius: var(--radius-md) !important;

&#x20; padding: 10px 24px !important;

&#x20; transition: all 0.25s ease !important;

&#x20; box-shadow: 0 4px 20px rgba(0,229,255,0.3) !important;

}

.stButton > button:hover {

&#x20; transform: translateY(-2px) scale(1.02) !important;

&#x20; box-shadow: 0 8px 30px rgba(0,229,255,0.5) !important;

}

.stButton > button:active {

&#x20; transform: translateY(0) !important;

}



/\* ── Tabs ── \*/

.stTabs \[data-baseweb="tab-list"] {

&#x20; background: transparent !important;

&#x20; border-bottom: 1px solid var(--border) !important;

&#x20; gap: 4px;

}

.stTabs \[data-baseweb="tab"] {

&#x20; background: transparent !important;

&#x20; color: var(--text-muted) !important;

&#x20; font-family: 'Syne', sans-serif !important;

&#x20; font-weight: 600 !important;

&#x20; font-size: 13px !important;

&#x20; letter-spacing: 0.06em;

&#x20; text-transform: uppercase;

&#x20; border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;

&#x20; padding: 10px 20px !important;

&#x20; border: none !important;

&#x20; transition: all 0.2s;

}

.stTabs \[aria-selected="true"] {

&#x20; color: var(--accent-1) !important;

&#x20; background: rgba(0,229,255,0.08) !important;

&#x20; border-bottom: 2px solid var(--accent-1) !important;

}



/\* ── Metric cards ── \*/

\[data-testid="metric-container"] {

&#x20; background: var(--bg-card) !important;

&#x20; border: 1px solid var(--border) !important;

&#x20; border-radius: var(--radius-lg) !important;

&#x20; padding: 20px !important;

&#x20; backdrop-filter: blur(12px);

}

\[data-testid="stMetricValue"] {

&#x20; font-family: 'Syne', sans-serif !important;

&#x20; color: var(--accent-1) !important;

&#x20; font-size: 2rem !important;

}

\[data-testid="stMetricLabel"] {

&#x20; color: var(--text-muted) !important;

&#x20; font-size: 12px !important;

&#x20; letter-spacing: 0.08em;

&#x20; text-transform: uppercase;

}



/\* ── Dataframe ── \*/

\[data-testid="stDataFrame"] {

&#x20; border-radius: var(--radius-lg) !important;

&#x20; border: 1px solid var(--border) !important;

&#x20; overflow: hidden;

}



/\* ── Alerts ── \*/

.stSuccess {

&#x20; background: rgba(0,255,157,0.08) !important;

&#x20; border: 1px solid rgba(0,255,157,0.3) !important;

&#x20; border-radius: var(--radius-md) !important;

&#x20; color: var(--text-main) !important;

}

.stError {

&#x20; background: rgba(255,77,109,0.08) !important;

&#x20; border: 1px solid rgba(255,77,109,0.3) !important;

&#x20; border-radius: var(--radius-md) !important;

}

.stWarning {

&#x20; background: rgba(255,165,0,0.08) !important;

&#x20; border: 1px solid rgba(255,165,0,0.3) !important;

&#x20; border-radius: var(--radius-md) !important;

}

.stInfo {

&#x20; background: rgba(0,229,255,0.08) !important;

&#x20; border: 1px solid rgba(0,229,255,0.3) !important;

&#x20; border-radius: var(--radius-md) !important;

}



/\* ── Slider ── \*/

.stSlider \[data-testid="stTickBar"] { color: var(--text-muted) !important; }

.stSlider \[role="slider"] { background: var(--accent-1) !important; }



/\* ── Select / Radio ── \*/

.stSelectbox \[data-baseweb="select"] > div {

&#x20; background: rgba(0,229,255,0.05) !important;

&#x20; border: 1px solid var(--border) !important;

&#x20; border-radius: var(--radius-md) !important;

&#x20; color: var(--text-main) !important;

}

.stRadio \[data-testid="stMarkdownContainer"] p {

&#x20; color: var(--text-muted) !important;

&#x20; font-size: 12px;

&#x20; letter-spacing: 0.06em;

&#x20; text-transform: uppercase;

}



/\* ── Audio ── \*/

audio {

&#x20; filter: invert(1) hue-rotate(180deg) !important;

&#x20; border-radius: var(--radius-md) !important;

&#x20; width: 100% !important;

}



/\* ── Scrollbar ── \*/

::-webkit-scrollbar { width: 6px; height: 6px; }

::-webkit-scrollbar-track { background: var(--bg-deep); }

::-webkit-scrollbar-thumb {

&#x20; background: rgba(0,229,255,0.25);

&#x20; border-radius: 3px;

}

::-webkit-scrollbar-thumb:hover { background: var(--accent-1); }



/\* ── Divider ── \*/

hr {

&#x20; border: none !important;

&#x20; height: 1px !important;

&#x20; background: var(--border) !important;

&#x20; margin: 28px 0 !important;

}

""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HELPERS — HTML components
# ─────────────────────────────────────────────
def hero():
    st.markdown("""
    <style>
    .hero-box {
        position: relative;
        overflow: hidden;
        padding: 48px 40px 40px;
        margin-bottom: 32px;
        border-radius: 24px;
        background: linear-gradient(135deg, rgba(0,229,255,0.08) 0%, rgba(4,22,40,0.9) 40%, rgba(123,97,255,0.08) 100%);
        border: 1px solid rgba(0,229,255,0.2);
        box-shadow: 0 0 60px rgba(0,229,255,0.07);
    }
    .hero-title {
        font-family: 'Syne', sans-serif;
        font-size: 36px;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(90deg, #00e5ff, #00ff9d, #7b61ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.1;
        margin-bottom: 6px;
    }
    .hero-sub {
        color: #7aadcc;
        font-size: 13px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-top: 4px;
    }
    .hero-desc {
        color: #a8c8e0;
        font-size: 15px;
        max-width: 560px;
        line-height: 1.7;
        margin: 16px 0 0 0;
    }
    .hero-tags {
        display: flex;
        gap: 12px;
        margin-top: 20px;
        flex-wrap: wrap;
    }
    .hero-tag {
        border-radius: 30px;
        padding: 6px 16px;
        font-size: 13px;
    }
    </style>
    <div class="hero-box">
        <div class="hero-title">🌍 VolunteerSphere AI</div>
        <div class="hero-sub">Smart NGO Discovery Platform</div>
        <div class="hero-desc">
            Find NGOs near you, explore volunteering opportunities, and get AI-powered guidance
            — all in one intelligent platform.
        </div>
        <div class="hero-tags">
            <span class="hero-tag" style="background:rgba(0,229,255,0.08);border:1px solid rgba(0,229,255,0.2);color:#00e5ff;">
                🤖 AI-Powered Search
            </span>
            <span class="hero-tag" style="background:rgba(0,255,157,0.08);border:1px solid rgba(0,255,157,0.2);color:#00ff9d;">
                📍 Location-Aware
            </span>
            <span class="hero-tag" style="background:rgba(123,97,255,0.08);border:1px solid rgba(123,97,255,0.2);color:#b39dff;">
                🔊 Voice Readout
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def ngo_card(row):
    dist = f"<span style='color:#00ff9d;font-weight:700;'>{row['Distance_km']:.1f} km away</span>" \
           if "Distance_km" in row else ""
    st.markdown(f"""
    <div style="
        background:rgba(4,28,54,0.85);
        border:1px solid rgba(0,229,255,0.15);
        border-radius:16px;
        padding:18px 22px;
        margin-bottom:14px;
        backdrop-filter:blur(12px);
        transition:all 0.3s;
        box-shadow:0 4px 24px rgba(0,0,0,0.3);
    " onmouseover="this.style.borderColor='rgba(0,229,255,0.4)';this.style.transform='translateY(-2px)'"
      onmouseout="this.style.borderColor='rgba(0,229,255,0.15)';this.style.transform='translateY(0)'">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;">
            <div>
                <div style="font-family:'Syne',sans-serif;font-size:17px;font-weight:700;
                    color:#e0f4ff;margin-bottom:8px;">
                    🏛️ {row.get('NGO','Unknown NGO')}
                </div>
                <div style="display:flex;gap:16px;flex-wrap:wrap;font-size:13px;color:#7aadcc;">
                    <span>📍 {row.get('Location','—')}</span>
                    <span>🎯 {row.get('Work','—')}</span>
                    <span>👤 {row.get('Eligibility','Open to all')}</span>
                </div>
            </div>
            <div style="text-align:right;font-size:13px;">{dist}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def section_header(icon, title, subtitle=""):
    st.markdown(f"""
    <div style="margin:28px 0 18px;">
        <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:700;
            color:#e0f4ff;display:flex;align-items:center;gap:10px;">
            <span style="font-size:24px;">{icon}</span> {title}
        </div>
        {"<div style='color:#7aadcc;font-size:13px;margin-top:4px;margin-left:34px;'>"+subtitle+"</div>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)


def stat_pill(label, value, color="#00e5ff"):
    return f"""
    <div style="
        display:inline-flex;align-items:center;gap:8px;
        background:rgba(4,28,54,0.8);
        border:1px solid {color}33;
        border-radius:30px;padding:6px 16px;
        font-size:13px;color:{color};margin:4px;
    ">{value} {label}</div>
    """


# ─────────────────────────────────────────────
#  CONFIG & LOAD
# ─────────────────────────────────────────────
API_KEY   = os.getenv("API_KEY")
DATA_FILE = "AI csv .xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(DATA_FILE)
    # Fix dirty data - spaces and commas in Location
    df["Location"] = df["Location"].str.strip().str.rstrip(",")
    for col in ["NGO", "Work", "Eligibility"]:
        if col in df.columns:
            df[col] = df[col].str.strip()
    return df

@st.cache_resource
def load_sentiment():
    return pipeline("sentiment-analysis")

data              = load_data()
sentiment_analyzer = load_sentiment()

# ─────────────────────────────────────────────
#  UTILITY FUNCTIONS
# ─────────────────────────────────────────────
def speak_text(text):
    tts = gTTS(text[:500])
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp.name)
    return tmp.name


def call_ai(user_input, system="You help users find NGOs and explain volunteering opportunities in simple, inspiring terms."):
    if not API_KEY:
        return "⚠️ API Key not configured. Set the API_KEY environment variable."
    url     = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    body    = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user_input}
        ]
    }
    try:
        res = requests.post(url, headers=headers, json=body, timeout=20)
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ AI Error: {e}"


def detect_emotion(text):
    try:
        return sentiment_analyzer(text[:512])[0]["label"]
    except:
        return "POSITIVE"


def dataset_search(user_input):
    result = data.copy()
    txt    = user_input.lower()
    filters_applied = False

    # Location
    for city in ["delhi","noida","gurgaon","mumbai","bangalore","chennai","kolkata",
                 "hyderabad","pune","ludhiana","chandigarh","jaipur","agra","surat"]:
        if city in txt:
            result = result[result["Location"].str.contains(city, case=False, na=False)]
            filters_applied = True
            break

    # Cause
    cause_map = {
        "education":"Education", "health":"Healthcare", "environment":"Environment",
        "women":"Women", "tech":"Technology", "mental":"Mental Health",
        "child":"Children", "animal":"Animal", "hunger":"Food", "food":"Food",
        "disability":"Disability", "senior":"Elderly", "elder":"Elderly"
    }
    for kw, col_val in cause_map.items():
        if kw in txt:
            result = result[result["Work"].str.contains(col_val, case=False, na=False)]
            filters_applied = True
            break

    # Eligibility
    for elig in ["student","volunteer","anyone","professional","youth"]:
        if elig in txt:
            result = result[result["Eligibility"].str.contains(elig, case=False, na=False)]
            filters_applied = True
            break

    # Generic name search
    if not filters_applied:
        mask = (
            data["NGO"].str.contains(user_input, case=False, na=False) |
            data["Location"].str.contains(user_input, case=False, na=False) |
            data["Work"].str.contains(user_input, case=False, na=False)
        )
        result = data[mask]
        if not result.empty:
            filters_applied = True

    return result if (filters_applied and not result.empty) else None


def smart_search(user_input):
    question_words = ["what","why","how","who","when","define","is","suggest",
                      "does","can","are","i","find","will","do","list","show","help"]
    if any(w in user_input.lower() for w in question_words):
        return {"ai": call_ai(user_input), "dataset": None}
    ds = dataset_search(user_input)
    if ds is not None:
        return {"ai": None, "dataset": ds}
    return {"ai": call_ai(user_input), "dataset": None}


# ─────────────────────────────────────────────
#  LOCATION UTILS
# ─────────────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    a = sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))


CITY_COORDS = {
    "delhi":(28.6139,77.2090), "noida":(28.5355,77.3910), "gurgaon":(28.4595,77.0266),
    "mumbai":(19.0760,72.8777), "bangalore":(12.9716,77.5946), "chennai":(13.0827,80.2707),
    "kolkata":(22.5726,88.3639), "hyderabad":(17.3850,78.4867), "pune":(18.5204,73.8567),
    "ludhiana":(30.9010,75.8573), "chandigarh":(30.7333,76.7794), "jaipur":(26.9124,75.7873),
    "agra":(27.1767,78.0081), "surat":(21.1702,72.8311), "amritsar":(31.6340,74.8723),
    "bhopal":(23.2599,77.4126), "lucknow":(26.8467,80.9462), "patna":(25.5941,85.1376),
}


def geocode_city(city_name):
    """Try Nominatim geocoding as fallback."""
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
        res = requests.get(url, headers={"User-Agent":"VolunteerSphere/1.0"}, timeout=5).json()
        if res:
            return float(res[0]["lat"]), float(res[0]["lon"]), res[0]["display_name"][:60]
    except:
        pass
    return None


def find_nearby_ngos(user_lat, user_lon, radius_km=25):
    df = data.copy()
    if "Latitude" not in df.columns or "Longitude" not in df.columns:
        return None
    df = df.dropna(subset=["Latitude","Longitude"])
    df["Distance_km"] = df.apply(
        lambda r: haversine(user_lat, user_lon, float(r["Latitude"]), float(r["Longitude"])), axis=1
    )
    nearby = df[df["Distance_km"] <= radius_km].sort_values("Distance_km")
    return nearby if not nearby.empty else None


def show_map(df, user_lat=None, user_lon=None):
    if df is None or df.empty:
        return
    if "Latitude" not in df.columns or "Longitude" not in df.columns:
        st.warning("Map unavailable: Latitude/Longitude columns missing.")
        return
    center_lat = user_lat if user_lat else df["Latitude"].mean()
    center_lon = user_lon if user_lon else df["Longitude"].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=9,
                   tiles="CartoDB dark_matter")

    if user_lat and user_lon:
        folium.Marker(
            [user_lat, user_lon],
            popup="📍 You are here",
            icon=folium.Icon(color="red", icon="home", prefix="fa")
        ).add_to(m)

    for _, row in df.iterrows():
        try:
            dist_txt = f" — {row['Distance_km']:.1f} km" if "Distance_km" in row else ""
            folium.CircleMarker(
                [float(row["Latitude"]), float(row["Longitude"])],
                radius=8, color="#00e5ff", fill=True, fill_color="#00ff9d",
                fill_opacity=0.8,
                popup=f"🏛️ {row.get('NGO','NGO')}{dist_txt}"
            ).add_to(m)
        except:
            continue

    section_header("🗺️","Interactive Map","NGO locations plotted on map")
    st_folium(m, width="100%", height=450)



# ─────────────────────────────────────────────
#  SAVE FUNCTIONS (Session State version)
# ─────────────────────────────────────────────
def save_signup(name, email, interest, city=""):
    if "all_signups" not in st.session_state:
        st.session_state["all_signups"] = []
    st.session_state["all_signups"].append({
        "Name": name, "Email": email,
        "Interest": interest, "City": city,
        "Time": datetime.datetime.now().strftime("%H:%M %d-%b-%Y")
    })
    return True

def save_feedback(rating, feedback_text):
    if "all_feedback" not in st.session_state:
        st.session_state["all_feedback"] = []
    st.session_state["all_feedback"].append({
        "Rating": rating, "Feedback": feedback_text,
        "Time": datetime.datetime.now().strftime("%H:%M %d-%b-%Y")
    })
    return True


# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────
for key, val in {
    "history":[], "result":None, "user_location":None, "last_query":"", "last_mode":""
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

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
        <div style="color:#7aadcc;font-size:11px;letter-spacing:0.1em;text-transform:uppercase;margin-top:2px;">
            AI Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Quick stats
    st.markdown("""
    <div style="font-family:'Syne',sans-serif;font-size:11px;letter-spacing:0.1em;
        text-transform:uppercase;color:#7aadcc;margin-bottom:10px;">
        📊 Dataset Stats
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    c1.metric("NGOs", len(data))
    c2.metric("Cities", data["Location"].nunique() if "Location" in data.columns else "—")

    st.markdown("---")

    # Cause filter
    st.markdown("""
    <div style="font-family:'Syne',sans-serif;font-size:11px;letter-spacing:0.1em;
        text-transform:uppercase;color:#7aadcc;margin-bottom:6px;">
        🎯 Filter by Cause
    </div>
    """, unsafe_allow_html=True)

    cause_filter = st.selectbox(
        "", ["All Causes"] + (sorted(data["Work"].dropna().unique().tolist()) if "Work" in data.columns else []),
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Search history
    st.markdown("""
    <div style="font-family:'Syne',sans-serif;font-size:11px;letter-spacing:0.1em;
        text-transform:uppercase;color:#7aadcc;margin-bottom:10px;">
        🕓 Recent Searches
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state["history"]:
        st.markdown("<div style='color:#7aadcc;font-size:13px;padding:8px 0;'>No searches yet</div>", unsafe_allow_html=True)
    else:
        for item in st.session_state["history"][:8]:
            st.markdown(f"""
            <div style="
                background:rgba(0,229,255,0.05);
                border:1px solid rgba(0,229,255,0.1);
                border-radius:8px;padding:8px 12px;
                margin-bottom:6px;font-size:12px;color:#a8c8e0;
                line-height:1.4;
            ">{item}</div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="color:#7aadcc;font-size:11px;text-align:center;line-height:1.6;">
        Built with ❤️ using Streamlit<br>
        <span style="color:#00e5ff;">AI + Voice + Maps + Emotion</span>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HERO
# ─────────────────────────────────────────────
hero()

# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
tab_search, tab_nearby, tab_dashboard, tab_signup = st.tabs([
    "🔍  Search",
    "📍  NGOs Near Me",
    "📊  Dashboard",
    "🙋  Join & Feedback"
])

# ══════════════════════════════════════════════
#  TAB 1 — SEARCH
# ══════════════════════════════════════════════
with tab_search:

    # Search bar
    st.markdown("""
    <div style="
        background:rgba(4,28,54,0.8);
        border:1px solid rgba(0,229,255,0.15);
        border-radius:20px;
        padding:24px 28px;
        margin-bottom:20px;
        backdrop-filter:blur(12px);
    ">
    """, unsafe_allow_html=True)

    col_input, col_mode = st.columns([3,1])

    with col_input:
        user_input = st.text_input(
            "What are you looking for?",
            placeholder="e.g. Education NGOs in Delhi, healthcare volunteers, women empowerment...",
            key="main_input"
        )

    with col_mode:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        mode = st.selectbox("Mode", ["Smart Search","AI Explanation","Dataset Search"], label_visibility="collapsed")

    col_btn1, col_btn2, col_spacer = st.columns([1,1,4])
    with col_btn1:
        search_btn = st.button("🔍 Search", use_container_width=True)
    with col_btn2:
        voice_btn = st.button("🔊 Read Aloud", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Apply cause filter from sidebar
    filtered_data = data.copy()
    if cause_filter != "All Causes" and "Work" in data.columns:
        filtered_data = data[data["Work"].str.contains(cause_filter, case=False, na=False)]

    # ---- Run search ----
    def run_query(query, search_mode):
        emotion = detect_emotion(query)
        if emotion == "NEGATIVE":
            query += " suggest supportive NGOs and how to get involved"
            st.info("💡 Emotion detected — showing extra suggestions")

        if any(phrase in query.lower() for phrase in ["near me","nearby","my location","close to me"]):
            if st.session_state["user_location"]:
                lat, lon = st.session_state["user_location"]
                nearby = find_nearby_ngos(lat, lon, 30)
                if nearby is not None:
                    st.session_state["result"] = {"type":"dataset","data":nearby,"lat":lat,"lon":lon}
                    return
            else:
                st.warning("📍 Please set your location in the **NGOs Near Me** tab first, then search again.")
                return

        if search_mode == "AI Explanation":
            context = filtered_data.head(5).to_string(index=False) if not filtered_data.empty else ""
            prompt  = f"User asked: {query}\n\nRelevant NGOs from our database:\n{context}\n\nAnswer helpfully using this data."
            st.session_state["result"] = {"type":"ai","data":call_ai(prompt)}

        elif search_mode == "Dataset Search":
            res = dataset_search(query)
            st.session_state["result"] = {"type":"dataset","data":res,"lat":None,"lon":None}

        else:
            res = smart_search(query)
            if res["ai"]:
                context = dataset_search(query)
                if context is not None:
                    prompt = f"User asked: {query}\n\nMatching NGOs:\n{context.head(5).to_string(index=False)}\n\nAnswer helpfully."
                    res["ai"] = call_ai(prompt)
            st.session_state["result"] = {"type":"smart","data":res,"lat":None,"lon":None}

    if search_btn and user_input:
        st.session_state["history"].insert(0, f"{mode}: {user_input}")
        st.session_state["history"] = st.session_state["history"][:10]
        run_query(user_input, mode)

    # ---- Display results ----
    result = st.session_state.get("result")

    if result:
        st.markdown("---")

        if result["type"] == "ai":
            section_header("🤖","AI Response","Powered by GPT-4o-mini via OpenRouter")
            st.markdown(f"""
            <div style="
                background:rgba(0,229,255,0.06);
                border:1px solid rgba(0,229,255,0.2);
                border-radius:16px;
                padding:22px 26px;
                color:#e0f4ff;
                line-height:1.8;
                font-size:15px;
            ">{result['data']}</div>
            """, unsafe_allow_html=True)

            if voice_btn or (search_btn and user_input):
                try:
                    audio_path = speak_text(result["data"])
                    st.audio(audio_path)
                except:
                    pass

        elif result["type"] == "dataset":
            df = result.get("data")
            if df is not None and not df.empty:
                section_header("📋","Matching NGOs",f"{len(df)} result(s) found")
                for _, row in df.iterrows():
                    ngo_card(row)
                show_map(df, result.get("lat"), result.get("lon"))
            else:
                st.error("😔 No NGOs found matching your search. Try different keywords or use AI Explanation mode.")

        elif result["type"] == "smart":
            res_data = result["data"]
            if res_data.get("ai"):
                section_header("🤖","AI Response")
                st.markdown(f"""
                <div style="
                    background:rgba(0,229,255,0.06);
                    border:1px solid rgba(0,229,255,0.2);
                    border-radius:16px;padding:22px 26px;
                    color:#e0f4ff;line-height:1.8;font-size:15px;
                ">{res_data['ai']}</div>
                """, unsafe_allow_html=True)
                if voice_btn:
                    try:
                        st.audio(speak_text(res_data["ai"]))
                    except:
                        pass

            if res_data.get("dataset") is not None:
                section_header("📋","Matching NGOs",f"{len(res_data['dataset'])} result(s) found")
                for _, row in res_data["dataset"].iterrows():
                    ngo_card(row)
                show_map(res_data["dataset"])


# ══════════════════════════════════════════════
#  TAB 2 — NGOs NEAR ME
# ══════════════════════════════════════════════
with tab_nearby:
    section_header("📍","NGOs Near Me","Find volunteering opportunities closest to your location")

    # Location input panel
    st.markdown("""
    <div style="
        background:rgba(4,28,54,0.8);
        border:1px solid rgba(0,255,157,0.2);
        border-radius:20px;padding:24px 28px;
        margin-bottom:20px;backdrop-filter:blur(12px);
    ">
    """, unsafe_allow_html=True)

    col_loc, col_radius = st.columns([3,1])

    with col_loc:
        manual_loc = st.text_input(
            "Enter your city or coordinates",
            placeholder="e.g. Ludhiana, Delhi, or 28.61,77.23",
            key="location_input"
        )

    with col_radius:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        radius_km = st.slider("Radius (km)", 5, 150, 30, key="radius_slider", label_visibility="collapsed")
        st.caption(f"Radius: **{radius_km} km**")

    col_detect, col_find, col_clear = st.columns([1.2,1.2,3])
    with col_detect:
        detect_btn = st.button("🌐 Auto-Detect", use_container_width=True, key="detect_btn")
    with col_find:
        find_btn = st.button("🔍 Find NGOs", use_container_width=True, key="find_btn")
    with col_clear:
        if st.button("✕ Clear Location", key="clear_btn"):
            st.session_state["user_location"] = None
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Auto-detect via browser JS
    if detect_btn:
        st.markdown("""
        <div style="
            background:rgba(0,229,255,0.06);border:1px solid rgba(0,229,255,0.2);
            border-radius:12px;padding:14px 18px;color:#a8c8e0;font-size:14px;
            margin-bottom:12px;
        ">
            ℹ️ Browser location detection: Your browser will ask for permission.
            If blocked, enter your city name manually above.
        </div>
        """, unsafe_allow_html=True)
        components.html("""
        <script>
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(pos) {
                    const coords = pos.coords.latitude + "," + pos.coords.longitude;
                    // Store in URL param so Streamlit can read it on next interaction
                    const url = new URL(window.location.href);
                    url.searchParams.set('geo', coords);
                    window.history.replaceState(null, '', url);
                    document.getElementById('geo_result').innerText =
                        "✅ Location detected: " + pos.coords.latitude.toFixed(4) + ", " + pos.coords.longitude.toFixed(4) +
                        "\\nPaste these coordinates in the input box above.";
                },
                function(err) {
                    document.getElementById('geo_result').innerText =
                        "❌ Could not auto-detect. Please type your city name manually.";
                }
            );
        }
        </script>
        <div id="geo_result" style="
            font-family:monospace;color:#00e5ff;font-size:13px;
            padding:10px;background:rgba(0,229,255,0.05);border-radius:8px;
            white-space:pre-line;min-height:40px;
        ">Requesting location...</div>
        """, height=80)

    # Resolve location from input
    if find_btn and manual_loc:
        city_key = manual_loc.strip().lower()

        if city_key in CITY_COORDS:
            lat, lon = CITY_COORDS[city_key]
            st.session_state["user_location"] = (lat, lon, manual_loc.title())
            st.success(f"📍 Location set: **{manual_loc.title()}**")

        elif "," in manual_loc:
            try:
                parts = manual_loc.split(",")
                lat, lon = float(parts[0].strip()), float(parts[1].strip())
                st.session_state["user_location"] = (lat, lon, f"{lat:.4f}, {lon:.4f}")
                st.success(f"📍 Coordinates set: {lat:.4f}, {lon:.4f}")
            except:
                st.error("Invalid format. Use lat,lon — e.g. 28.61,77.23")

        else:
            geo = geocode_city(manual_loc)
            if geo:
                lat, lon, display_name = geo
                st.session_state["user_location"] = (lat, lon, display_name)
                st.success(f"📍 Found: **{display_name}**")
            else:
                st.error("City not found. Try spelling it differently or enter coordinates.")

    # Show results
    if st.session_state["user_location"]:
        user_lat, user_lon, loc_name = st.session_state["user_location"] if len(st.session_state["user_location"])==3 else (*st.session_state["user_location"], "Your Location")

        st.markdown(f"""
        <div style="
            display:inline-flex;align-items:center;gap:10px;
            background:rgba(0,255,157,0.08);border:1px solid rgba(0,255,157,0.25);
            border-radius:30px;padding:8px 20px;margin:12px 0;
            font-size:14px;color:#00ff9d;
        ">
            📍 Active location: {loc_name} &nbsp;|&nbsp; Searching within {radius_km} km
        </div>
        """, unsafe_allow_html=True)

        nearby_ngos = find_nearby_ngos(user_lat, user_lon, radius_km)

        if nearby_ngos is not None:
            section_header("✅","Results",f"{len(nearby_ngos)} NGOs found within {radius_km} km")

            # Distance buckets
            under10  = len(nearby_ngos[nearby_ngos["Distance_km"] <  10])
            under25  = len(nearby_ngos[nearby_ngos["Distance_km"] <  25])

            st.markdown(f"""
            <div style="margin-bottom:20px;">
                {stat_pill("under 10 km", under10, "#00ff9d")}
                {stat_pill("under 25 km", under25, "#00e5ff")}
                {stat_pill("total found",  len(nearby_ngos), "#b39dff")}
            </div>
            """, unsafe_allow_html=True)

            for _, row in nearby_ngos.iterrows():
                ngo_card(row)

            show_map(nearby_ngos, user_lat, user_lon)

            # AI summary
            section_header("🤖","AI Summary of Nearby NGOs")
            ngo_list = ", ".join(nearby_ngos["NGO"].tolist()[:6])
            ai_nearby = call_ai(
                f"The user is near {loc_name}. Nearby NGOs are: {ngo_list}. "
                f"Briefly describe each and suggest how to get involved. Keep it concise and encouraging."
            )
            st.markdown(f"""
            <div style="
                background:rgba(0,229,255,0.06);border:1px solid rgba(0,229,255,0.2);
                border-radius:16px;padding:22px 26px;
                color:#e0f4ff;line-height:1.8;font-size:15px;
            ">{ai_nearby}</div>
            """, unsafe_allow_html=True)

            try:
                st.audio(speak_text(f"Found {len(nearby_ngos)} NGOs near you. {ai_nearby[:400]}"))
            except:
                pass

        else:
            st.warning(f"😔 No NGOs found within {radius_km} km of {loc_name}. Try increasing the radius.")
            fallback_ai = call_ai(
                f"No NGOs were found near {loc_name}. Suggest how someone there can volunteer online or remotely. Be encouraging."
            )
            section_header("💡","AI Suggestion","Remote & online volunteering options")
            st.markdown(f"""
            <div style="
                background:rgba(123,97,255,0.06);border:1px solid rgba(123,97,255,0.2);
                border-radius:16px;padding:22px 26px;
                color:#e0f4ff;line-height:1.8;font-size:15px;
            ">{fallback_ai}</div>
            """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style="
            text-align:center;padding:48px 24px;
            background:rgba(4,28,54,0.5);
            border:1px dashed rgba(0,229,255,0.2);
            border-radius:20px;
        ">
            <div style="font-size:48px;margin-bottom:16px;">📍</div>
            <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:700;
                color:#e0f4ff;margin-bottom:8px;">Set your location to get started</div>
            <div style="color:#7aadcc;font-size:14px;max-width:380px;margin:0 auto;line-height:1.6;">
                Enter your city name or coordinates above to discover NGOs near you.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  TAB 3 — DASHBOARD
# ══════════════════════════════════════════════
with tab_dashboard:
    st.subheader("📊 Impact Dashboard")
    st.caption("Overview of all NGOs in our database")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total NGOs",     len(data))
    c2.metric("Cities Covered", data["Location"].nunique() if "Location" in data.columns else "—")
    c3.metric("Cause Areas",    data["Work"].nunique()     if "Work"     in data.columns else "—")
    c4.metric("Signups",        len(st.session_state.get("all_signups", [])))

    st.markdown("---")

    if "Work" in data.columns:
        st.subheader("🎯 NGOs by Cause Area")
        st.bar_chart(data["Work"].value_counts().head(12))

    col_left, col_right = st.columns(2)
    with col_left:
        if "Location" in data.columns:
            st.subheader("📍 Top Cities")
            st.bar_chart(data["Location"].value_counts().head(8))
    with col_right:
        if "Eligibility" in data.columns:
            st.subheader("👤 By Eligibility")
            st.bar_chart(data["Eligibility"].value_counts())

    st.markdown("---")
    st.subheader("📋 Browse Full Dataset")
    st.caption("Click any column header to sort")
    show_cols  = [c for c in ["NGO","Location","Work","Eligibility","Description","Contact"] if c in data.columns]
    display_df = filtered_data[show_cols] if cause_filter != "All Causes" else data[show_cols]
    st.dataframe(display_df, use_container_width=True, height=350)

    if st.session_state.get("all_signups"):
        st.markdown("---")
        st.subheader("🙋 Signups This Session")
        st.dataframe(pd.DataFrame(st.session_state["all_signups"]), use_container_width=True)

# ══════════════════════════════════════════════
#  TAB 4 — SIGNUP & FEEDBACK
# ══════════════════════════════════════════════
with tab_signup:
    col_form1, col_form2 = st.columns(2)

    with col_form1:
        section_header("🙋","Volunteer Signup","Register your interest — we'll connect you")
        st.markdown("""
        <div style="
            background:rgba(4,28,54,0.8);
            border:1px solid rgba(0,229,255,0.15);
            border-radius:20px;padding:28px;
            backdrop-filter:blur(12px);
        ">
        """, unsafe_allow_html=True)

        name     = st.text_input("Full Name",  placeholder="Your name", key="signup_name")
        email    = st.text_input("Email",      placeholder="you@example.com", key="signup_email")
        interest = st.text_input("Interest",   placeholder="NGO name or cause you care about", key="signup_interest")
        city     = st.text_input("Your City",  placeholder="Delhi, Mumbai...", key="signup_city")

        if st.button("✅ Register as Volunteer", use_container_width=True, key="signup_submit"):
            if name and email:
                success = save_signup(name, email, interest, city)
                if success:
                    st.success(f"🎉 Thank you {name}! We'll reach out at {email} soon.")
                    st.balloons()
                ai_msg = call_ai(f"A volunteer named {name} is interested in {interest or 'volunteering'} in {city or 'India'}. Give them a warm, short welcome message and one tip to get started.")
                st.markdown(f"""
                <div style="
                    background:rgba(0,255,157,0.06);border:1px solid rgba(0,255,157,0.2);
                    border-radius:12px;padding:16px;margin-top:12px;
                    color:#e0f4ff;font-size:14px;line-height:1.7;
                ">🤖 {ai_msg}</div>
                """, unsafe_allow_html=True)
            else:
                st.error("Name and Email are required.")

        st.markdown("</div>", unsafe_allow_html=True)

    with col_form2:
        section_header("💬","Share Feedback","Help us improve VolunteerSphere")
        st.markdown("""
        <div style="
            background:rgba(4,28,54,0.8);
            border:1px solid rgba(123,97,255,0.2);
            border-radius:20px;padding:28px;
            backdrop-filter:blur(12px);
        ">
        """, unsafe_allow_html=True)

        rating   = st.select_slider("Rate your experience", ["⭐","⭐⭐","⭐⭐⭐","⭐⭐⭐⭐","⭐⭐⭐⭐⭐"], value="⭐⭐⭐", key="feedback_rating")
        feedback = st.text_area("Your feedback", placeholder="What did you like? What can we improve?", height=120, key="feedback_text")

        if st.button("📩 Submit Feedback", use_container_width=True, key="feedback_submit"):
            if feedback:
                success = save_feedback(rating, feedback)
                emotion = detect_emotion(feedback)
                if success:
                    if emotion == "POSITIVE":
                        st.success("🙏 Thank you for the kind words! We're glad you found it helpful.")
                    else:
                        st.info("🙏 Thank you for your honest feedback. We'll work on improving!")
            else:
                st.error("Please write some feedback before submitting.")

        st.markdown("</div>", unsafe_allow_html=True)
