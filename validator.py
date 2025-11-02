import json
from openai import OpenAI

def validate_checklist_pretty(checklist_text, api_key, system_prompt):
    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": checklist_text}
            ],
            temperature=0.3
        )

        output = response.choices[0].message.content.strip()
        data = json.loads(output)

        status = data.get("compliance_status", "Unknown")
        issues = data.get("detected_issues", [])
        suggestions = data.get("improvement_suggestions", [])

        # Pretty formatting
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

    except json.JSONDecodeError:
        return "❌ Invalid JSON! The model's response could not be parsed."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"
