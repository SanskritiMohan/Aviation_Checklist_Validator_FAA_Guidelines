import os
import json
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
load_dotenv()


# -------------------------
# Streamlit UI setup
# -------------------------
st.set_page_config(page_title="Aviation Checklist Validator", page_icon="✈️", layout="centered")
st.title("Aviation Pre-Flight Checklist Validator")
st.write("Validate your pre-flight checklist against FAA/ICAO standards using AI (powered by LLaMA 3).")

# -------------------------
# API Key (stored securely as environment variable)
# -------------------------
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("❌ Missing API Key. Please set your GROQ_API_KEY as an environment variable.")
    st.stop()

client = Groq(api_key=api_key)

# -------------------------
# System Prompt for the Model
# -------------------------
SYSTEM_PROMPT = """
You are an AI aviation compliance assistant. 
Your task is to analyze pre-flight checklists according to FAA/ICAO regulations and determine whether the checklist is compliant.
Return the result **only** as a JSON object with the following structure:

{
  "compliance_status": "Compliant" or "Needs Review",
  "detected_issues": ["List of detected issues or violations"],
  "improvement_suggestions": ["List of improvements or safety recommendations"]
}
"""

# -------------------------
# Function to validate checklist
# -------------------------
def validate_checklist_pretty(checklist_text, api_key, SYSTEM_PROMPT):
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": checklist_text}
            ],
            temperature=0.3
        )

        output = response.choices[0].message.content.strip()

        # Try to parse JSON
        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            # If model output is not strict JSON, extract possible JSON content
            start = output.find("{")
            end = output.rfind("}") + 1
            if start != -1 and end != -1:
                data = json.loads(output[start:end])
            else:
                return "❌ Invalid JSON! Model response could not be parsed."

        status = data.get("compliance_status", "Unknown")
        issues = data.get("detected_issues", [])
        suggestions = data.get("improvement_suggestions", [])

        # Pretty formatted output
        if status.lower() == "compliant":
            result = "✅ **Compliant:** All checklist items meet FAA/ICAO standards.\n\n"
        else:
            result = "❌ **Needs Review:** Some issues were found.\n\n"

        if issues:
            result += "**Detected Issues:**\n"
            for issue in issues:
                result += f"- {issue}\n"
            result += "\n"

        if suggestions:
            result += "**Improvement Suggestions:**\n"
            for s in suggestions:
                result += f"- {s}\n"

        return result

    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# -------------------------
# File Upload Section
# -------------------------
uploaded_file = st.file_uploader("Upload your checklist file", type=["txt", "json"])

if uploaded_file:
    # Detect file type
    if uploaded_file.name.endswith(".json"):
        try:
            data = json.load(uploaded_file)
            checklist_text = json.dumps(data, indent=2)
        except Exception as e:
            st.error(f"Error reading JSON file: {e}")
            st.stop()
    else:
        checklist_text = uploaded_file.read().decode("utf-8", errors="ignore")

    st.text_area("Checklist Preview", checklist_text, height=200)

    if st.button("Validate Checklist"):
        with st.spinner("Analyzing checklist for compliance..."):
            result = validate_checklist_pretty(checklist_text, api_key, SYSTEM_PROMPT)
        st.markdown(result)
else:
    st.info("Upload a `.txt` or `.json` checklist to begin analysis.")
