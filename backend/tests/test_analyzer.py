import pytest
from analyzer import (
    analyze_complaint,
    extract_technical_indicators,
    get_model_and_vectorizer
)
from ml.explainability import explain_prediction

def test_extract_technical_indicators():
    sample_text = (
        "Fraudster called from +91-9876543210 and asked me to send INR 25,000 to "
        "merchant.fastpay@oksbi and visit http://sbi-kyc-verify-portal.online with UTR 261829304123"
    )
    indicators = extract_technical_indicators(sample_text)
    types = [i["indicator_type"] for i in indicators]
    values = [i["indicator_value"] for i in indicators]

    assert "PHONE" in types
    assert "UPI_VPA" in types
    assert "URL" in types
    assert any("9876543210" in v for v in values)
    assert any("merchant.fastpay@oksbi" in v for v in values)

def test_explain_prediction():
    vectorizer, classifier = get_model_and_vectorizer()
    text = "Received fake SMS link demanding UPI PIN and netbanking OTP to unblock account"
    explanation = explain_prediction(text, vectorizer, classifier, top_k=4)
    assert isinstance(explanation, list)
    assert len(explanation) > 0
    assert "term" in explanation[0]
    assert "influence_pct" in explanation[0]

def test_analyze_complaint():
    desc = "My netbanking was debited by 45,000 after I clicked a suspicious refund link."
    result = analyze_complaint(
        description=desc,
        reported_category="Online Financial Fraud",
        severity="High",
        financial_loss=45000,
        personal_info_exposed=False,
        account_compromised=True
    )
    assert "predicted_category" in result
    assert "confidence" in result
    assert "risk_score" in result
    assert result["risk_score"] > 30
    assert "reasons" in result
