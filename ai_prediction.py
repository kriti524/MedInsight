import requests
import json


def get_health_prediction(full_name, date_of_birth, glucose, haemoglobin, cholesterol):
    """
    Calls the Anthropic Claude API to generate a health prediction based on blood test values.
    Returns a concise health remark string.
    """
    prompt = f"""You are a clinical health assistant. Analyze the following patient blood test results and provide a concise health risk assessment.

Patient Details:
- Name: {full_name}
- Date of Birth: {date_of_birth}
- Glucose: {glucose} mg/dL
- Haemoglobin: {haemoglobin} g/dL
- Cholesterol: {cholesterol} mg/dL

Reference Ranges:
- Glucose: 70-100 mg/dL (fasting normal), 100-125 pre-diabetic, >125 diabetic risk
- Haemoglobin: Men 13.5-17.5 g/dL, Women 12.0-15.5 g/dL (below = anaemia risk)
- Cholesterol: <200 mg/dL desirable, 200-239 borderline high, >240 high risk

Provide a structured health assessment in exactly this format (2-3 sentences max):
1. State whether each value is Normal, Borderline, or High Risk.
2. Mention the most likely health condition risk if any value is abnormal.
3. Give one brief actionable recommendation.

Keep the response under 80 words. Be medically informative but not alarmist."""

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 200,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            text = data.get("content", [{}])[0].get("text", "").strip()
            return text if text else "⚠️ Could not generate prediction. Please try again."
        else:
            return fallback_prediction(glucose, haemoglobin, cholesterol)

    except Exception:
        return fallback_prediction(glucose, haemoglobin, cholesterol)


def fallback_prediction(glucose, haemoglobin, cholesterol):
    """Rule-based fallback prediction if API call fails."""
    issues = []
    recommendations = []

    # Glucose assessment
    if glucose < 70:
        issues.append("Glucose: Low (Hypoglycaemia risk)")
        recommendations.append("increase carbohydrate intake")
    elif 70 <= glucose <= 100:
        issues.append("Glucose: Normal")
    elif 100 < glucose <= 125:
        issues.append("Glucose: Borderline (Pre-diabetic range)")
        recommendations.append("reduce sugar intake and exercise regularly")
    else:
        issues.append("Glucose: High (Diabetic risk)")
        recommendations.append("consult a diabetologist immediately")

    # Haemoglobin assessment
    if haemoglobin < 12.0:
        issues.append("Haemoglobin: Low (Anaemia risk)")
        recommendations.append("increase iron-rich foods or consult for iron therapy")
    elif haemoglobin <= 17.5:
        issues.append("Haemoglobin: Normal")
    else:
        issues.append("Haemoglobin: High (Polycythaemia risk)")
        recommendations.append("consult a haematologist")

    # Cholesterol assessment
    if cholesterol < 200:
        issues.append("Cholesterol: Desirable")
    elif 200 <= cholesterol < 240:
        issues.append("Cholesterol: Borderline High (Cardiovascular risk)")
        recommendations.append("adopt a heart-healthy diet")
    else:
        issues.append("Cholesterol: High (High cardiovascular risk)")
        recommendations.append("seek medical advice for cholesterol management")

    summary = " | ".join(issues)
    if recommendations:
        summary += f". Recommendation: {'; '.join(recommendations).capitalize()}."
    else:
        summary += ". All values within normal range — maintain a healthy lifestyle."

    return summary
