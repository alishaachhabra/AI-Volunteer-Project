import streamlit as st
import requests
import pandas as pd

# ---------------- Configuration ----------------
API_KEY = "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"   # Replace with your OpenRouter key
DATA_FILE = "AI csv .xlsx"

# Load dataset once
data = pd.read_excel(DATA_FILE)

# ---------------- Helper Functions ----------------
def call_ai(user_input,
            model="openai/gpt-4o-mini",
            system_prompt="You help users find NGOs and volunteer opportunities."):
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

    try:
        response = requests.post(url, headers=headers, json=data_api)
        resp_json = response.json()
        print("OpenRouter raw response:", resp_json)  # Debugging

        # Case 1: Normal success
        if "choices" in resp_json and len(resp_json["choices"]) > 0:
            return resp_json["choices"][0]["message"]["content"]

        # Case 2: Error returned
        elif "error" in resp_json:
            return f"⚠️ AI Error: {resp_json['error'].get('message', 'Unknown error')}"

        # Case 3: Unexpected format
        else:
            return f"⚠️ AI Error: Unexpected response format → {resp_json}"

    except Exception as e:
        return f"⚠️ AI Exception: {str(e)}"




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
    if location:
        result = result[result["Location"].str.contains(location, case=False)]
    if work:
        result = result[result["Work"].str.contains(work, case=False)]
    if eligibility:
        result = result[result["Eligibility"].str.contains(eligibility, case=False)]

    if not result.empty:
        return result
    return None


def smart_search(user_input):
    question_words = ["what", "why", "how", "who", "when", "define", "is"]
    ai_answer = None
    dataset_result = None

    if any(word in user_input.lower() for word in question_words):
        ai_answer = call_ai(user_input, model="openai/gpt-4o-mini")
    else:
        dataset_result = dataset_search(user_input)
        if dataset_result is None:
            ai_answer = call_ai(user_input, model="openai/gpt-4o-mini")

    return {"ai": ai_answer, "dataset": dataset_result}


def show_image_for_context(user_input):
    if "education" in user_input.lower():
        st.image("https://images.unsplash.com/photo-1588072432836-e10032774350", caption="Education NGO in action")
    elif "health" in user_input.lower():
        st.image("https://images.unsplash.com/photo-1588776814546-1c1e1d6d7f1b", caption="Healthcare NGO support")
    elif "environment" in user_input.lower():
        st.image("https://images.unsplash.com/photo-1508780709619-79562169bc64", caption="Volunteers protecting environment")
    elif "women" in user_input.lower():
        st.image("https://images.unsplash.com/photo-1524504388940-b1c1722653e1", caption="Women empowerment NGO")
    elif "tech" in user_input.lower():
        st.image("https://images.unsplash.com/photo-1519389950473-47ba0277781c", caption="Technology training NGO")
    else:
        st.image("https://images.unsplash.com/photo-1509099836639-18ba1795216d", caption="General volunteering")

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="AI Volunteer Impact Platform", page_icon="🌍", layout="centered")
st.title("🌍 AI Volunteer Impact Platform")

# Initialize history
if "history" not in st.session_state:
    st.session_state["history"] = []

user_input = st.text_input("Ask your question:")
mode = st.radio("Choose mode:", ["AI Explanation", "Dataset Search", "Smart Search"])

def run_query(query, mode):
    if mode == "AI Explanation":
        ai_answer = call_ai(query, model="openai/gpt-4o-mini")
        st.success(ai_answer)
        show_image_for_context(query)
        st.session_state["history"].append(("AI", query))

    elif mode == "Dataset Search":
        result = dataset_search(query)
        if result is not None:
            st.dataframe(result)
            csv = result.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download results as CSV", data=csv, file_name="ngo_results.csv", mime="text/csv")
            st.session_state["history"].append(("Dataset", query))
        else:
            st.error("No matching NGOs found.")

    elif mode == "Smart Search":
        response = smart_search(query)
        tabs = st.tabs(["🤖 AI Explanation", "📊 Dataset Results"])
        with tabs[0]:
            if response["ai"]:
                st.success(response["ai"])
                show_image_for_context(query)
            else:
                st.warning("No AI explanation available.")
        with tabs[1]:
            if response["dataset"] is not None:
                st.dataframe(response["dataset"])
                csv = response["dataset"].to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Download results as CSV", data=csv, file_name="ngo_results.csv", mime="text/csv")
            else:
                st.warning("No dataset results found.")
        st.session_state["history"].append(("Smart", query))

if st.button("Search") and user_input:
    run_query(user_input, mode)

# Sidebar history with clickable buttons
st.sidebar.title("📜 Search History")
for idx, entry in enumerate(st.session_state["history"]):
    mode, query = entry
    if st.sidebar.button(f"{mode}: {query}", key=f"history_{idx}"):
        run_query(query, mode)
