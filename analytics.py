"""Financial indicators and rule-based health assessment (CIBIL scale 300-900)."""


def score_band(score: int) -> str:
    if score >= 750: return "Excellent"
    if score >= 700: return "Good"
    if score >= 650: return "Fair"
    if score >= 550: return "Poor"
    return "Very poor"


def compute_metrics(p) -> dict:
    income = p.monthly_income or 0
    dti = round(p.monthly_emi / income * 100, 1) if income else 0.0
    util = round(p.credit_used / p.credit_limit * 100, 1) if p.credit_limit else 0.0
    savings_rate = round((income - p.monthly_expenses - p.monthly_emi) / income * 100, 1) if income else 0.0

    h = 100
    h -= min(30, max(0, dti - 20))
    h -= min(25, max(0, util - 30) * 0.5)
    h -= min(25, p.missed_payments * 8)
    h -= 10 if savings_rate < 10 else 0
    h -= 5 if p.active_loans > 4 else 0
    h = max(0, round(h))
    label = "Strong" if h >= 75 else "Moderate" if h >= 50 else "At risk"

    risks = []
    if dti > 40: risks.append("Debt-to-income ratio is above 40%; lenders may see you as high risk.")
    elif dti > 30: risks.append("Debt-to-income ratio is above 30%.")
    if util > 50: risks.append("Credit utilization is above 50%; aim for under 30%.")
    elif util > 30: risks.append("Credit utilization is above 30%.")
    if p.missed_payments: risks.append(f"{p.missed_payments} missed payment(s) are lowering your score.")
    if savings_rate < 10: risks.append("Monthly savings rate is under 10% of income.")
    if p.active_loans > 4: risks.append("You have many active loans; avoid new credit enquiries.")

    return {
        "dti": dti, "utilization": util, "savings_rate": savings_rate,
        "health_score": h, "health_label": label,
        "cibil_band": score_band(p.cibil_score), "risks": risks,
    }


def fallback_advice(p, m) -> str:
    tips = ["Pay every EMI and card bill on or before the due date; set up auto-debit."]
    if m["utilization"] > 30:
        tips.append("Reduce card utilization below 30% by paying down balances or requesting a limit increase.")
    if m["dti"] > 30:
        tips.append("Prepay the highest-interest loan first to bring your EMI burden down.")
    if m["savings_rate"] < 10:
        tips.append("Automate a monthly transfer to savings and build a 6-month emergency fund.")
    if p.missed_payments:
        tips.append("Clear overdue amounts now; payment history is the biggest CIBIL factor.")
    tips.append("Avoid multiple loan applications within a short period.")
    return "Rule-based guidance (Gemini key not configured):\n- " + "\n- ".join(tips)
