import os
from analytics import fallback_advice

SYSTEM = (
    "You are Credit Assistant, a financial wellness advisor for users in India. "
    "Use the CIBIL score range (300-900), INR amounts and Indian banking context. "
    "Give specific, actionable, concise advice. You are not a licensed advisor; "
    "remind the user to verify major decisions with a professional."
)


def _context(p, m) -> str:
    return (
        f"Profile: CIBIL {p.cibil_score} ({m['cibil_band']}); income INR {p.monthly_income:,.0f}/mo; "
        f"expenses INR {p.monthly_expenses:,.0f}; EMI INR {p.monthly_emi:,.0f}; total debt INR {p.total_debt:,.0f}; "
        f"card limit INR {p.credit_limit:,.0f}, used INR {p.credit_used:,.0f}; active loans {p.active_loans}; "
        f"missed payments {p.missed_payments}; savings INR {p.savings:,.0f}; goal: {p.goal or 'not set'}. "
        f"DTI {m['dti']}%, utilization {m['utilization']}%, savings rate {m['savings_rate']}%, "
        f"health {m['health_score']}/100 ({m['health_label']})."
    )


def _generate(prompt: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.0-flash"), system_instruction=SYSTEM)
    return model.generate_content(prompt).text


def analyze(p, m) -> str:
    if not os.getenv("GEMINI_API_KEY"):
        return fallback_advice(p, m)
    prompt = (
        f"{_context(p, m)}\n\nProvide: 1) a short credit health summary, 2) top risks, "
        "3) five prioritized steps to improve the CIBIL score, 4) debt and utilization plan, "
        "5) savings guidance, 6) a 6-month plan toward the user's goal. Use short markdown sections."
    )
    try:
        return _generate(prompt)
    except Exception:
        return fallback_advice(p, m)


def chat(p, m, message: str) -> str:
    if not os.getenv("GEMINI_API_KEY"):
        return fallback_advice(p, m)
    try:
        return _generate(f"{_context(p, m)}\n\nUser question: {message}")
    except Exception:
        return "The AI service is unavailable right now. Please try again shortly."
