import streamlit as st
import requests
import pandas as pd

API_KEY = "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"
data = pd.read_excel("AI csv .xlsx")

def call_ai(user_input, model="openai/gpt-3.5-turbo", system_prompt="You help users find NGOs and explain volunteering in simple terms."):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data_api = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    }
    response = requests.post(url, headers=headers, json=data_api)
    return response.json()['choices'][0]['message']['content']

def dataset_search(user_input):
    user_input_lower = user_input.lower()
    location, work, eligibility = None, None, None

    if "delhi" in user_input_lower: location = "Delhi"
    elif "noida" in user_input_lower: location = "Noida"
    elif "gurgaon" in user_input_lower: location = "Gurgaon"

    if "education" in user_input_lower: work = "Education"
    elif "health" in user_input_lower: work = "Healthcare"
    elif "environment" in user_input_lower: work = "Environment"
    elif "women" in user_input_lower: work = "Women"
    elif "tech" in user_input_lower: work = "Technology"
    elif "mental" in user_input_lower: work = "Mental Health"

    if "student" in user_input_lower: eligibility = "Students"
    elif "anyone" in user_input_lower: eligibility = "Anyone"
    elif "volunteer" in user_input_lower: eligibility = "Volunteers"

    result = data.copy()
    filters_applied = False

    if location:
        result = result[result['Location'].str.contains(location, case=False)]
        filters_applied = True
    if work:
        result = result[result['Work'].str.contains(work, case=False)]
        filters_applied = True
    if eligibility:
        result = result[result['Eligibility'].str.contains(eligibility, case=False)]
        filters_applied = True

    if filters_applied and not result.empty:
        return result
    return None

def smart_search(user_input):
    question_words = ["what", "why", "how", "who", "when", "define", "is"]
    if any(word in user_input.lower() for word in question_words):
        return {"type": "ai", "content": call_ai(user_input, model="openai/gpt-4o-mini")}
    else:
        result = dataset_search(user_input)
        if result is not None:
            return {"type": "dataset", "content": result}
        else:
            return {"type": "ai", "content": call_ai(user_input)}

# ---------------- Streamlit UI ----------------
st.title("🌍 NGO Finder & Explainer")

user_input = st.text_input("Ask your question:")
mode = st.radio("Choose mode:", ["AI Explanation", "Dataset Search", "Smart Search"])

if st.button("Search") and user_input:
    if mode == "AI Explanation":
        st.markdown("## 🤖 AI Explanation")
        st.success(call_ai(user_input, model="openai/gpt-4o-mini"))  # green box for AI

    elif mode == "Dataset Search":
        result = dataset_search(user_input)
        if result is not None:
            st.markdown("## 📊 Matching NGOs")
            st.dataframe(result)  # clean table
        else:
            st.error("No matching NGOs found.")
    
    elif mode == "Smart Search":
        response = smart_search(user_input)
        if response["type"] == "ai":
            st.markdown("## 🤖 AI Explanation")
            st.success(response["content"])  # green box
        elif response["type"] == "dataset":
            st.markdown("## 📊 Matching NGOs")
            st.dataframe(response["content"])  # table
