import React, { useState, useEffect, useRef } from 'react';
import {
  Shield, PhoneCall, AlertTriangle, Clock, CheckCircle2,
  Mic, MicOff, Upload, Search, FileText, Download, Award,
  ExternalLink, Sparkles, ChevronRight, RefreshCw, ArrowRight,
  HelpCircle, Eye, AlertOctagon, Check, ShieldCheck, Swords
} from 'lucide-react';
import { jsPDF } from 'jspdf';
import { createWorker } from 'tesseract.js';
import ScamWeatherCard from '../modules/weather/ScamWeatherCard';
import ScamDojo from '../modules/dojo/ScamDojo';
import SafeScan from '../modules/safescan/SafeScan';
import { MODULE_FLAGS } from '../config/featureFlags';




const QUIZ_QUESTIONS = [
  {
    id: 1,
    q: "Do you use unique, complex passwords and a password manager for your primary banking and email accounts?",
    options: [
      { text: "Yes, completely unique passwords with 12+ characters", points: 10 },
      { text: "Mostly unique, but I reuse variations of 2-3 passwords", points: 5 },
      { text: "I use the same simple password across most platforms", points: 0 }
    ]
  },
  {
    id: 2,
    q: "Is Two-Factor Authentication (2FA) via Authenticator App enabled on your email and net banking?",
    options: [
      { text: "Yes, using authenticator app or hardware key", points: 10 },
      { text: "Enabled, but via SMS OTP only", points: 6 },
      { text: "No 2FA enabled / Password only", points: 0 }
    ]
  },
  {
    id: 3,
    q: "If an incoming caller claiming to be your bank asks for an OTP to prevent account suspension, what do you do?",
    options: [
      { text: "Disconnect immediately and call the official bank branch number", points: 10 },
      { text: "Ask caller to verify my details before deciding", points: 2 },
      { text: "Share the OTP if they sound urgent or official", points: 0 }
    ]
  },
  {
    id: 4,
    q: "Do you verify payment recipients before entering your UPI PIN on PhonePe, Google Pay, or Paytm?",
    options: [
      { text: "Always verify; I know UPI PIN is NEVER needed to receive money", points: 10 },
      { text: "Usually check name, but sometimes scan advance QR codes", points: 4 },
      { text: "I have entered UPI PIN believing it would credit money", points: 0 }
    ]
  },
  {
    id: 5,
    q: "How do you handle links sent via SMS claiming electricity disconnection or pending tax refunds?",
    options: [
      { text: "Never click; I log in directly via official billing website", points: 10 },
      { text: "Sometimes click if the domain looks official", points: 3 },
      { text: "Click and enter my details if urged with deadline", points: 0 }
    ]
  },
  {
    id: 6,
    q: "If a caller claiming to be police or customs threatens 'Digital Arrest' via Skype video call, what is your reaction?",
    options: [
      { text: "Recognize it as an extortion scam; police never do virtual arrests", points: 10 },
      { text: "Get frightened and comply with private verification instructions", points: 0 },
      { text: "Unsure if law enforcement actually uses Skype", points: 3 }
    ]
  },
  {
    id: 7,
    q: "Do you download Android APK files from Telegram, WhatsApp, or instant loan app promotions?",
    options: [
      { text: "Never; only install from official Google Play Store with verified reviews", points: 10 },
      { text: "Occasionally download utility or modded APKs", points: 3 },
      { text: "Have downloaded quick loan or discount APKs from links", points: 0 }
    ]
  },
  {
    id: 8,
    q: "When using public Wi-Fi at airports or cafes, do you use a trusted VPN or avoid financial transactions?",
    options: [
      { text: "Always use cellular data or VPN for sensitive tasks", points: 10 },
      { text: "Sometimes check banking apps on public networks", points: 4 },
      { text: "Always connect to free public Wi-Fi without VPN", points: 0 }
    ]
  },
  {
    id: 9,
    q: "Do you have transaction limits set on your debit/credit cards for international and online usage?",
    options: [
      { text: "Yes, strict daily limits configured via banking app", points: 10 },
      { text: "Limits are set to default bank maximums", points: 4 },
      { text: "Never configured card limits or switch controls", points: 0 }
    ]
  },
  {
    id: 10,
    q: "Do you know the National Cyber Crime Helpline number for immediate financial fraud interdiction?",
    options: [
      { text: "Yes, 1930 (Golden Hour interdiction within 2 hours)", points: 10 },
      { text: "Vaguely aware there is a helpline", points: 4 },
      { text: "Did not know 1930 exists", points: 0 }
    ]
  }
];

export default function CitizenPortal({
  t,
  lang,
  onSwitchToOfficer,
  apiBase = '/api/v1'
}) {
  const [activeTab, setActiveTab] = useState('wizard'); // 'wizard', 'checker', 'hygiene', 'tracker'

  // Wizard State
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState(() => {
    try {
      const saved = localStorage.getItem('cybershield_draft_complaint');
      return saved ? JSON.parse(saved) : {
        category: 'Online Financial Fraud',
        amount: '',
        incidentDate: new Date().toISOString().slice(0, 16),
        channel: 'UPI / Mobile Banking',
        suspectPhone: '',
        suspectUpi: '',
        suspectUrl: '',
        suspectBank: '',
        description: '',
        victimName: 'Citizen Complainant',
        victimPhone: '',
        victimState: 'Karnataka',
        victimCity: 'Bengaluru'
      };
    } catch {
      return {
        category: 'Online Financial Fraud',
        amount: '',
        incidentDate: new Date().toISOString().slice(0, 16),
        channel: 'UPI / Mobile Banking',
        suspectPhone: '',
        suspectUpi: '',
        suspectUrl: '',
        suspectBank: '',
        description: '',
        victimName: 'Citizen Complainant',
        victimPhone: '',
        victimState: 'Karnataka',
        victimCity: 'Bengaluru'
      };
    }
  });

  // Autosave Draft
  useEffect(() => {
    try {
      localStorage.setItem('cybershield_draft_complaint', JSON.stringify(formData));
    } catch (e) {
      console.warn("Storage quota exceeded", e);
    }
  }, [formData]);

  // Submission State
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submittedComplaint, setSubmittedComplaint] = useState(null);

  // Voice Input State
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  // OCR Upload State
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrStatus, setOcrStatus] = useState('');

  // Suspicious Message Checker State
  const [checkerText, setCheckerText] = useState('');
  const [checkerLoading, setCheckerLoading] = useState(false);
  const [checkerResult, setCheckerResult] = useState(null);

  // Hygiene Quiz State
  const [quizAnswers, setQuizAnswers] = useState({});
  const [quizScore, setQuizScore] = useState(null);

  // Tracker State
  const [searchCompId, setSearchCompId] = useState('');
  const [trackedCase, setTrackedCase] = useState(null);
  const [trackingLoading, setTrackingLoading] = useState(false);
  const [trackingError, setTrackingError] = useState('');

  // Golden Hour Live Countdown (2 Hours remaining from incident)
  const [timeLeft, setTimeLeft] = useState({ hours: 1, minutes: 48, seconds: 22 });
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev.seconds > 0) return { ...prev, seconds: prev.seconds - 1 };
        if (prev.minutes > 0) return { ...prev, minutes: prev.minutes - 1, seconds: 59 };
        if (prev.hours > 0) return { hours: prev.hours - 1, minutes: 59, seconds: 59 };
        return { hours: 0, minutes: 0, seconds: 0 };
      });
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Web Speech API Initialization
  const handleToggleVoice = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert("Voice speech recognition is not supported in this browser. Please use Google Chrome or Edge.");
      return;
    }

    if (isListening) {
      if (recognitionRef.current) recognitionRef.current.stop();
      setIsListening(false);
      return;
    }

    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRec();
    recognition.continuous = true;
    recognition.interimResults = true;
    
    // Set speech recognition language
    if (lang === 'hi') recognition.lang = 'hi-IN';
    else if (lang === 'kn') recognition.lang = 'kn-IN';
    else recognition.lang = 'en-IN';

    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event) => {
      let finalTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript + ' ';
        }
      }
      if (finalTranscript) {
        setFormData(prev => ({
          ...prev,
          description: (prev.description ? prev.description + ' ' : '') + finalTranscript.trim()
        }));
      }
    };
    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);

    recognitionRef.current = recognition;
    recognition.start();
  };

  // Tesseract OCR Screenshot Analysis
  const handleOcrUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setOcrLoading(true);
    setOcrStatus(t.ocrProcessing);

    try {
      const worker = await createWorker('eng');
      const ret = await worker.recognize(file);
      const text = ret.data.text;
      await worker.terminate();

      // Extract details via regex
      const upiMatch = text.match(/[a-zA-Z0-9.\-_]{2,40}@(okhdfcbank|okaxis|oksbi|okicici|paytm|ybl|apl|upi|ibl)/i);
      const phoneMatch = text.match(/(?:\+91[-\s]?)?[6-9]\d{9}/);
      const amountMatch = text.match(/(?:Rs\.?|INR|₹)\s*([\d,]+(?:\.\d{2})?)/i);
      const urlMatch = text.match(/https?:\/\/[^\s<>"]+|www\.[^\s<>"]+/i);

      setFormData(prev => ({
        ...prev,
        suspectUpi: upiMatch ? upiMatch[0] : prev.suspectUpi,
        suspectPhone: phoneMatch ? phoneMatch[0] : prev.suspectPhone,
        suspectUrl: urlMatch ? urlMatch[0] : prev.suspectUrl,
        amount: amountMatch ? amountMatch[1].replace(/,/g, '') : prev.amount,
        description: (prev.description ? prev.description + '\n\n' : '') +
          `[OCR Evidence Extraction]:\n${text.slice(0, 300)}...`
      }));

      setOcrStatus(t.ocrSuccess);
      setTimeout(() => setOcrStatus(''), 4000);
    } catch (err) {
      console.error(err);
      setOcrStatus("OCR extraction failed. You can paste the text manually.");
      setTimeout(() => setOcrStatus(''), 4000);
    } finally {
      setOcrLoading(false);
    }
  };

  // Submit Complaint to Backend
  const handleSubmitComplaint = async (e) => {
    e.preventDefault();
    if (!formData.description.trim()) {
      alert("Please provide a description of the incident.");
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await fetch(`${apiBase}/cases`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description: formData.description,
          category: formData.category,
          financial_loss: parseFloat(formData.amount || 0),
          state: formData.victimState,
          city: formData.victimCity,
          platform: formData.channel,
          incident_date: formData.incidentDate.slice(0, 10),
          severity: parseFloat(formData.amount || 0) >= 100000 ? "High" : "Medium",
          suspect_phone: formData.suspectPhone,
          suspect_upi: formData.suspectUpi,
          suspect_url: formData.suspectUrl,
          suspect_bank: formData.suspectBank
        })
      });

      const json = await res.json();
      if (res.ok && json.data) {
        setSubmittedComplaint(json.data);
        localStorage.removeItem('cybershield_draft_complaint');
      } else {
        alert(json.message || "Failed to register complaint.");
      }
    } catch (err) {
      alert("Could not connect to CyberShield backend. Please check connection.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Generate Official PDF Acknowledgement
  const handleDownloadAckPdf = (caseData) => {
    const doc = new jsPDF();
    const id = caseData.complaint_id || 'CC-2026-IN-DRAFT';
    
    // Header Banner
    doc.setFillColor(31, 111, 107); // Deep Teal
    doc.rect(0, 0, 210, 32, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(16);
    doc.text("CYBERSHIELD INDIA — CITIZEN ACKNOWLEDGEMENT", 14, 16);
    doc.setFontSize(9);
    doc.setFont("helvetica", "normal");
    doc.text("National Cyber Crime Reporting Portal & Rapid Triage Unit (I4C Standards)", 14, 24);

    // Case Details Table
    doc.setTextColor(35, 39, 42);
    doc.setFontSize(11);
    doc.setFont("helvetica", "bold");
    doc.text("OFFICIAL COMPLAINT ACKNOWLEDGEMENT RECEIPT", 14, 44);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    let y = 54;
    const items = [
      ["Complaint Reference ID", id],
      ["Date of Registration", caseData.complaint_date || new Date().toISOString().slice(0, 10)],
      ["Incident Category", caseData.predicted_category || caseData.crime_type || formData.category],
      ["Reported Financial Loss", `INR Rs. ${Number(caseData.financial_loss || formData.amount || 0).toLocaleString('en-IN')}`],
      ["Assessed AI Risk Level", `${caseData.risk_level || 'HIGH'} (Score: ${caseData.risk_score || 72}/100)`],
      ["Investigating Cyber Cell", caseData.cyber_cell_station || `Cyber Crime Police Station, ${formData.victimCity}`],
      ["Immediate Priority SLA", caseData.priority || 'High Priority (Under 6h)'],
      ["Helpline Toll-Free", "1930 (24x7 Citizen Cyber Helpline)"]
    ];

    items.forEach(([label, val]) => {
      doc.setFont("helvetica", "bold");
      doc.text(`${label}:`, 14, y);
      doc.setFont("helvetica", "normal");
      doc.text(String(val), 80, y);
      y += 8;
    });

    // Golden Hour Guidelines Box
    y += 6;
    doc.setFillColor(241, 235, 221); // Sand
    doc.roundedRect(14, y, 182, 38, 3, 3, 'F');
    doc.setTextColor(31, 111, 107);
    doc.setFont("helvetica", "bold");
    doc.text("MANDATORY GOLDEN HOUR CITIZEN DIRECTIVES:", 18, y + 8);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(8.5);
    doc.setTextColor(59, 66, 74);
    doc.text("1. Contact your beneficiary and remitting bank immediately to request debit freeze under RBI SOP.", 18, y + 15);
    doc.text("2. Dial 1930 to trigger national CFCFRMS payment interdiction before fraudster withdraws funds.", 18, y + 22);
    doc.text("3. Retain this acknowledgement for submission to jurisdictional police officers under Section 94 BNSS.", 18, y + 29);

    // Complaint Narrative Excerpt
    y += 48;
    doc.setFontSize(10);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(35, 39, 42);
    doc.text("Complainant Statement on Record:", 14, y);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(8.5);
    const splitDesc = doc.splitTextToSize(caseData.description || formData.description, 182);
    doc.text(splitDesc.slice(0, 10), 14, y + 7);

    // Footer
    doc.setFontSize(8);
    doc.setTextColor(120, 130, 140);
    doc.text("Digitally generated by CyberShield India AI Platform. Verification link: https://cybercrime.gov.in", 14, 285);

    doc.save(`CyberShield_Acknowledgement_${id}.pdf`);
  };

  // Run Suspicious Message Checker
  const handleRunChecker = async () => {
    if (!checkerText.trim()) return;
    setCheckerLoading(true);
    try {
      const res = await fetch(`${apiBase}/analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description: checkerText,
          financial_loss: 0,
          category: 'Phishing Attack'
        })
      });
      const json = await res.json();
      if (res.ok && json.data) {
        setCheckerResult(json.data);
      }
    } catch {
      alert("Checker service unavailable.");
    } finally {
      setCheckerLoading(false);
    }
  };

  // Submit Hygiene Quiz
  const handleSubmitQuiz = () => {
    let total = 0;
    Object.values(quizAnswers).forEach(pts => { total += pts; });
    setQuizScore(total);
  };

  // Track Complaint by ID
  const handleTrackComplaint = async (e) => {
    e.preventDefault();
    if (!searchCompId.trim()) return;
    setTrackingLoading(true);
    setTrackingError('');
    setTrackedCase(null);

    try {
      const res = await fetch(`${apiBase}/cases/${encodeURIComponent(searchCompId.trim())}`);
      const json = await res.json();
      if (res.ok && json.data) {
        setTrackedCase(json.data);
      } else {
        setTrackingError("No complaint found matching reference ID. Please verify spelling.");
      }
    } catch {
      setTrackingError("Unable to connect to complaint registry.");
    } finally {
      setTrackingLoading(false);
    }
  };

  return (
    <div>
      {/* Golden Hour Rapid Action Banner */}
      <div className="golden-hour-bar">
        <div className="golden-hour-info">
          <div className="golden-hour-badge">
            <Clock size={18} />
            <span>GOLDEN HOUR: {String(timeLeft.hours).padStart(2, '0')}:{String(timeLeft.minutes).padStart(2, '0')}:{String(timeLeft.seconds).padStart(2, '0')}</span>
          </div>
          <div className="golden-hour-text">
            <h4>{t.goldenHour}</h4>
            <p>{t.goldenHourSub}</p>
          </div>
        </div>
        <a href="tel:1930" className="helpline-1930-btn">
          <PhoneCall size={20} />
          <span>{t.call1930}</span>
        </a>
      </div>

      {MODULE_FLAGS.SCAM_WEATHER && (
        <div style={{ marginBottom: '28px' }}>
          <ScamWeatherCard apiBase={apiBase} lang={lang} />
        </div>
      )}

      <div className="page-hero">

        <h1 className="page-title">{t.heroTitle}</h1>
        <p className="page-subtitle">{t.heroSubtitle}</p>
      </div>

      {/* Citizen Navigation Pill Tabs */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '28px', flexWrap: 'wrap' }}>
        <button
          onClick={() => setActiveTab('wizard')}
          className={`control-btn ${activeTab === 'wizard' ? 'control-btn-primary' : ''}`}
        >
          <FileText size={18} />
          <span>{t.actionReportCrime}</span>
        </button>
        <button
          onClick={() => setActiveTab('checker')}
          className={`control-btn ${activeTab === 'checker' ? 'control-btn-primary' : ''}`}
        >
          <Shield size={18} />
          <span>{t.actionQuickCheck}</span>
        </button>
        <button
          onClick={() => setActiveTab('hygiene')}
          className={`control-btn ${activeTab === 'hygiene' ? 'control-btn-primary' : ''}`}
        >
          <Award size={18} />
          <span>{t.actionTestHygiene}</span>
        </button>
        <button
          onClick={() => setActiveTab('tracker')}
          className={`control-btn ${activeTab === 'tracker' ? 'control-btn-primary' : ''}`}
        >
          <Search size={18} />
          <span>{t.actionTrackStatus}</span>
        </button>
        {MODULE_FLAGS.SCAM_DOJO && (
          <button
            onClick={() => setActiveTab('dojo')}
            className={`control-btn ${activeTab === 'dojo' ? 'control-btn-primary' : ''}`}
            style={{ fontWeight: 700, borderColor: '#D9825B' }}
          >
            <Swords size={18} color={activeTab === 'dojo' ? '#FFFFFF' : '#D9825B'} />
            <span>Scam Dojo (AI Simulator)</span>
          </button>
        )}
      </div>


      {/* TAB 1: 4-STEP GUIDED COMPLAINT WIZARD */}
      {activeTab === 'wizard' && (
        <div>
          {submittedComplaint ? (
            <div className="app-card" style={{ textAlign: 'center', padding: '48px 32px' }}>
              <div style={{ width: 72, height: 72, borderRadius: '50%', background: 'var(--secondary-subtle)', color: 'var(--primary)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: 20 }}>
                <CheckCircle2 size={44} />
              </div>
              <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: '1.8rem', color: 'var(--primary)', marginBottom: 8 }}>
                {t.complaintSuccess}
              </h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem', marginBottom: 20 }}>
                {t.complaintIdLabel}: <strong style={{ color: 'var(--text-main)', fontSize: '1.2rem' }}>{submittedComplaint.complaint_id}</strong>
              </p>
              <div style={{ background: 'var(--bg-sand)', padding: '16px', borderRadius: '12px', maxWidth: 600, margin: '0 auto 28px', textAlign: 'left', fontSize: '0.9rem' }}>
                <p><strong>Predicted Category:</strong> {submittedComplaint.predicted_category}</p>
                <p><strong>Assessed Risk:</strong> {submittedComplaint.risk_level} ({submittedComplaint.risk_score}/100)</p>
                <p><strong>Assigned Station:</strong> {submittedComplaint.cyber_cell_station}</p>
                <p><strong>Status:</strong> {submittedComplaint.current_status} — Immediate transaction freeze initiated.</p>
              </div>
              <div style={{ display: 'flex', gap: '14px', justifyContent: 'center', flexWrap: 'wrap' }}>
                <button onClick={() => handleDownloadAckPdf(submittedComplaint)} className="btn-primary">
                  <Download size={18} />
                  <span>{t.downloadAckPdf}</span>
                </button>
                <button onClick={() => { setSubmittedComplaint(null); setStep(1); }} className="btn-secondary">
                  <span>File Another Complaint</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="app-card">
              {/* Wizard Step Indicator */}
              <div className="wizard-progress">
                <div className={`progress-step ${step === 1 ? 'active' : step > 1 ? 'completed' : ''}`}>
                  <div className="step-circle">{step > 1 ? <Check size={16} /> : '1'}</div>
                  <span className="step-label">{t.step1Title}</span>
                </div>
                <div className={`progress-step ${step === 2 ? 'active' : step > 2 ? 'completed' : ''}`}>
                  <div className="step-circle">{step > 2 ? <Check size={16} /> : '2'}</div>
                  <span className="step-label">{t.step2Title}</span>
                </div>
                <div className={`progress-step ${step === 3 ? 'active' : step > 3 ? 'completed' : ''}`}>
                  <div className="step-circle">{step > 3 ? <Check size={16} /> : '3'}</div>
                  <span className="step-label">{t.step3Title}</span>
                </div>
                <div className={`progress-step ${step === 4 ? 'active' : ''}`}>
                  <div className="step-circle">4</div>
                  <span className="step-label">{t.step4Title}</span>
                </div>
              </div>

              <form onSubmit={handleSubmitComplaint}>
                {/* STEP 1: Crime Category & Amount */}
                {step === 1 && (
                  <div>
                    <div className="card-header">
                      <div>
                        <h3 className="card-title">{t.step1Title}</h3>
                        <p className="card-subtitle">Select the type of attack and financial loss suffered.</p>
                      </div>
                    </div>

                    <div className="grid-2">
                      <div className="form-group">
                        <label className="form-label">{t.categoryLabel}</label>
                        <select
                          className="form-select"
                          value={formData.category}
                          onChange={e => setFormData({ ...formData, category: e.target.value })}
                        >
                          <option value="Online Financial Fraud">Online Financial Fraud (UPI / NetBanking)</option>
                          <option value="Phishing Attack">Phishing Attack (Cloned links / OTP theft)</option>
                          <option value="Account Takeover">Account Takeover (SIM Swap / Social Media Hack)</option>
                          <option value="Investment/Crypto Fraud">Investment / Crypto Fraud (Task rating Ponzi)</option>
                          <option value="Social Engineering">Social Engineering (Digital Arrest / Impersonation)</option>
                          <option value="Online Shopping Fraud">Online Shopping Fraud (Fake website flash sale)</option>
                          <option value="Identity Theft">Identity Theft (Loan apps / Matrimonial fake)</option>
                          <option value="Cyber Bullying / Harassment">Cyber Bullying / Deepfake Extortion</option>
                          <option value="Ransomware / Malware">Ransomware / Malware Endpoint Attack</option>
                          <option value="Data Breach">Corporate Data Breach / Exfiltration</option>
                        </select>
                      </div>

                      <div className="form-group">
                        <label className="form-label">{t.amountLostLabel}</label>
                        <input
                          type="number"
                          className="form-input"
                          placeholder="e.g. 45000 (Enter 0 if no financial loss)"
                          value={formData.amount}
                          onChange={e => setFormData({ ...formData, amount: e.target.value })}
                        />
                        <span className="form-hint">Financial losses &gt; ₹50,000 trigger automated Critical triage.</span>
                      </div>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 20 }}>
                      <button type="button" onClick={() => setStep(2)} className="btn-primary">
                        <span>Continue to Step 2</span>
                        <ChevronRight size={18} />
                      </button>
                    </div>
                  </div>
                )}

                {/* STEP 2: Date & Medium */}
                {step === 2 && (
                  <div>
                    <div className="card-header">
                      <div>
                        <h3 className="card-title">{t.step2Title}</h3>
                        <p className="card-subtitle">Provide when the fraud occurred and communication platform used.</p>
                      </div>
                    </div>

                    <div className="grid-2">
                      <div className="form-group">
                        <label className="form-label">{t.incidentDateLabel}</label>
                        <input
                          type="datetime-local"
                          className="form-input"
                          value={formData.incidentDate}
                          onChange={e => setFormData({ ...formData, incidentDate: e.target.value })}
                        />
                      </div>

                      <div className="form-group">
                        <label className="form-label">{t.channelLabel}</label>
                        <select
                          className="form-select"
                          value={formData.channel}
                          onChange={e => setFormData({ ...formData, channel: e.target.value })}
                        >
                          <option value="UPI / Mobile Banking">UPI / Google Pay / PhonePe / Paytm</option>
                          <option value="WhatsApp / SMS">WhatsApp / SMS Text Header</option>
                          <option value="Voice Phone Call">Voice Phone Call (Spoofed Caller ID)</option>
                          <option value="Skype / Video Call">Skype / Video Call (Digital Arrest)</option>
                          <option value="Telegram Group">Telegram Group / Channel</option>
                          <option value="Instagram / Facebook">Instagram / Facebook Sponsored Ad</option>
                          <option value="Fake E-Commerce Portal">Fake E-Commerce Website</option>
                        </select>
                      </div>
                    </div>

                    <div className="grid-2">
                      <div className="form-group">
                        <label className="form-label">Victim State</label>
                        <select
                          className="form-select"
                          value={formData.victimState}
                          onChange={e => setFormData({ ...formData, victimState: e.target.value })}
                        >
                          <option value="Karnataka">Karnataka</option>
                          <option value="Maharashtra">Maharashtra</option>
                          <option value="Telangana">Telangana</option>
                          <option value="Delhi">Delhi</option>
                          <option value="Tamil Nadu">Tamil Nadu</option>
                          <option value="Gujarat">Gujarat</option>
                          <option value="Uttar Pradesh">Uttar Pradesh</option>
                          <option value="West Bengal">West Bengal</option>
                          <option value="Rajasthan">Rajasthan</option>
                          <option value="Kerala">Kerala</option>
                          <option value="Andhra Pradesh">Andhra Pradesh</option>
                          <option value="Haryana">Haryana</option>
                          <option value="Madhya Pradesh">Madhya Pradesh</option>
                          <option value="Bihar">Bihar</option>
                          <option value="Punjab">Punjab</option>
                          <option value="Odisha">Odisha</option>
                          <option value="Assam">Assam</option>
                          <option value="Jharkhand">Jharkhand</option>
                          <option value="Chhattisgarh">Chhattisgarh</option>
                          <option value="Uttarakhand">Uttarakhand</option>
                        </select>
                      </div>

                      <div className="form-group">
                        <label className="form-label">City / District</label>
                        <input
                          type="text"
                          className="form-input"
                          placeholder="e.g. Bengaluru"
                          value={formData.victimCity}
                          onChange={e => setFormData({ ...formData, victimCity: e.target.value })}
                        />
                      </div>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 20 }}>
                      <button type="button" onClick={() => setStep(1)} className="btn-secondary">
                        Back
                      </button>
                      <button type="button" onClick={() => setStep(3)} className="btn-primary">
                        <span>Continue to Step 3</span>
                        <ChevronRight size={18} />
                      </button>
                    </div>
                  </div>
                )}

                {/* STEP 3: Suspect Indicators */}
                {step === 3 && (
                  <div>
                    <div className="card-header">
                      <div>
                        <h3 className="card-title">{t.step3Title}</h3>
                        <p className="card-subtitle">Enter any phone numbers, UPI handles, links, or bank accounts given by suspect.</p>
                      </div>
                    </div>

                    <div className="grid-2">
                      <div className="form-group">
                        <label className="form-label">{t.suspectPhoneLabel}</label>
                        <input
                          type="text"
                          className="form-input"
                          placeholder="e.g. +91-9876543210"
                          value={formData.suspectPhone}
                          onChange={e => setFormData({ ...formData, suspectPhone: e.target.value })}
                        />
                      </div>

                      <div className="form-group">
                        <label className="form-label">{t.suspectUpiLabel}</label>
                        <input
                          type="text"
                          className="form-input"
                          placeholder="e.g. merchant.fastpay@oksbi"
                          value={formData.suspectUpi}
                          onChange={e => setFormData({ ...formData, suspectUpi: e.target.value })}
                        />
                      </div>
                    </div>

                    <div className="grid-2">
                      <div className="form-group">
                        <label className="form-label">{t.suspectUrlLabel}</label>
                        <input
                          type="text"
                          className="form-input"
                          placeholder="e.g. http://sbi-kyc-verify-portal.online"
                          value={formData.suspectUrl}
                          onChange={e => setFormData({ ...formData, suspectUrl: e.target.value })}
                        />
                      </div>

                      <div className="form-group">
                        <label className="form-label">{t.suspectBankLabel}</label>
                        <input
                          type="text"
                          className="form-input"
                          placeholder="e.g. 918273645012 (IFSC: HDFC0001234)"
                          value={formData.suspectBank}
                          onChange={e => setFormData({ ...formData, suspectBank: e.target.value })}
                        />
                      </div>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 20 }}>
                      <button type="button" onClick={() => setStep(2)} className="btn-secondary">
                        Back
                      </button>
                      <button type="button" onClick={() => setStep(4)} className="btn-primary">
                        <span>Continue to Step 4</span>
                        <ChevronRight size={18} />
                      </button>
                    </div>
                  </div>
                )}

                {/* STEP 4: Narrative Description with Voice & OCR Assist */}
                {step === 4 && (
                  <div>
                    <div className="card-header">
                      <div>
                        <h3 className="card-title">{t.step4Title}</h3>
                        <p className="card-subtitle">Provide a clear statement. You can speak in your language or upload screenshots.</p>
                      </div>
                    </div>

                    {/* Voice and OCR Toolbar */}
                    <div className="voice-ocr-toolbar">
                      <button
                        type="button"
                        onClick={handleToggleVoice}
                        className={`assist-btn ${isListening ? 'listening' : ''}`}
                      >
                        {isListening ? <MicOff size={16} /> : <Mic size={16} />}
                        <span>{isListening ? t.voiceListening : t.voiceInput}</span>
                      </button>

                      <label className="assist-btn" style={{ cursor: 'pointer' }}>
                        <Upload size={16} />
                        <span>{ocrLoading ? 'Processing...' : t.ocrUpload}</span>
                        <input
                          type="file"
                          accept="image/*"
                          style={{ display: 'none' }}
                          onChange={handleOcrUpload}
                          disabled={ocrLoading}
                        />
                      </label>
                    </div>

                    {ocrStatus && (
                      <div style={{ marginTop: 8, fontSize: '0.85rem', color: 'var(--primary)', fontWeight: 600 }}>
                        {ocrStatus}
                      </div>
                    )}

                    <div className="form-group" style={{ marginTop: 14 }}>
                      <label className="form-label">{t.descriptionLabel}</label>
                      <textarea
                        className="form-textarea"
                        placeholder={t.descriptionPlaceholder}
                        value={formData.description}
                        onChange={e => setFormData({ ...formData, description: e.target.value })}
                        required
                      />
                      <span className="form-hint">
                        AI will automatically extract threat indicators, assess severity, and check for correlated cases across India.
                      </span>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 20 }}>
                      <button type="button" onClick={() => setStep(3)} className="btn-secondary">
                        Back
                      </button>
                      <button type="submit" disabled={isSubmitting} className="btn-primary btn-accent">
                        <span>{isSubmitting ? t.submitting : t.submitComplaint}</span>
                        <ArrowRight size={18} />
                      </button>
                    </div>
                  </div>
                )}
              </form>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: SUSPICIOUS MESSAGE & LINK CHECKER (UPGRADED TO SAFE-SCAN) */}
      {activeTab === 'checker' && (
        MODULE_FLAGS.SAFE_SCAN ? (
          <SafeScan
            apiBase={apiBase}
            lang={lang}
            onPrefillComplaint={(prefill) => {
              setFormData(prev => ({
                ...prev,
                suspectPhone: prefill.suspectPhone || prev.suspectPhone,
                suspectUpi: prefill.susfallUpi || prefill.suspectUpi || prev.suspectUpi,
                suspectUrl: prefill.suspectUrl || prev.suspectUrl,
                description: prefill.description || prev.description
              }));
              setActiveTab('wizard');
              setStep(1);
            }}
          />
        ) : (
          <div className="app-card">
            <div className="card-header">
              <div>
                <h3 className="card-title">{t.checkerTitle}</h3>
                <p className="card-subtitle">{t.checkerSubtitle}</p>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">{t.checkerInputLabel}</label>
              <textarea
                className="form-textarea"
                placeholder={t.checkerPlaceholder}
                value={checkerText}
                onChange={e => setCheckerText(e.target.value)}
              />
            </div>

            <button
              onClick={handleRunChecker}
              disabled={checkerLoading || !checkerText.trim()}
              className="btn-primary"
            >
              <Search size={18} />
              <span>{checkerLoading ? t.scanning : t.scanButton}</span>
            </button>
          </div>
        )
      )}


      {/* TAB 3: CYBER HYGIENE QUIZ */}
      {activeTab === 'hygiene' && (
        <div className="app-card">
          <div className="card-header">
            <div>
              <h3 className="card-title">{t.quizTitle}</h3>
              <p className="card-subtitle">{t.quizSubtitle}</p>
            </div>
          </div>

          {quizScore !== null ? (
            <div style={{ textAlign: 'center', padding: '30px 20px' }}>
              <div style={{ fontSize: '3rem', fontWeight: 800, color: quizScore >= 80 ? 'var(--primary)' : quizScore >= 50 ? 'var(--warning)' : 'var(--danger)' }}>
                {quizScore} / 100
              </div>
              <h3 style={{ fontFamily: 'var(--font-serif)', marginTop: 8 }}>
                {quizScore >= 80 ? t.championTier : quizScore >= 60 ? t.vigilantTier : quizScore >= 40 ? t.vulnerableTier : t.highRiskTier}
              </h3>
              <p style={{ maxWidth: 600, margin: '12px auto 24px', color: 'var(--text-muted)' }}>
                {quizScore >= 80
                  ? "Outstanding digital safety awareness! You adhere to multi-factor defense, official channel validation, and fast incident interdiction."
                  : "Caution advised: You have vulnerabilities that modern cyber syndicates frequently exploit through coercive psychological manipulation and QR/SMS vectors."}
              </p>
              <button onClick={() => { setQuizScore(null); setQuizAnswers({}); }} className="btn-secondary">
                Retake Assessment
              </button>
            </div>
          ) : (
            <div>
              {QUIZ_QUESTIONS.map(q => (
                <div key={q.id} style={{ marginBottom: 24, paddingBottom: 18, borderBottom: '1px solid var(--border-color)' }}>
                  <p style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-main)', marginBottom: 10 }}>
                    {q.id}. {q.q}
                  </p>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {q.options.map((opt, oIdx) => (
                      <label
                        key={oIdx}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 10,
                          padding: '10px 14px',
                          borderRadius: 8,
                          background: quizAnswers[q.id] === opt.points ? 'var(--primary-subtle)' : 'var(--bg-app)',
                          border: `1.5px solid ${quizAnswers[q.id] === opt.points ? 'var(--primary)' : 'var(--border-color)'}`,
                          cursor: 'pointer'
                        }}
                      >
                        <input
                          type="radio"
                          name={`quiz_${q.id}`}
                          checked={quizAnswers[q.id] === opt.points}
                          onChange={() => setQuizAnswers({ ...quizAnswers, [q.id]: opt.points })}
                        />
                        <span style={{ fontSize: '0.9rem' }}>{opt.text}</span>
                      </label>
                    ))}
                  </div>
                </div>
              ))}

              <button
                onClick={handleSubmitQuiz}
                disabled={Object.keys(quizAnswers).length < QUIZ_QUESTIONS.length}
                className="btn-primary"
              >
                <span>{t.submitQuiz}</span>
                <ChevronRight size={18} />
              </button>
            </div>
          )}
        </div>
      )}

      {/* TAB 4: COMPLAINT STATUS TRACKER */}
      {activeTab === 'tracker' && (
        <div className="app-card">
          <div className="card-header">
            <div>
              <h3 className="card-title">{t.trackerTitle}</h3>
              <p className="card-subtitle">{t.trackerSubtitle}</p>
            </div>
          </div>

          <form onSubmit={handleTrackComplaint} style={{ display: 'flex', gap: 12, marginBottom: 28, flexWrap: 'wrap' }}>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. CC-2026-KA-000101"
              value={searchCompId}
              onChange={e => setSearchCompId(e.target.value)}
              style={{ maxWidth: 360 }}
              required
            />
            <button type="submit" disabled={trackingLoading} className="btn-primary">
              <Search size={18} />
              <span>{trackingLoading ? 'Searching...' : t.trackButton}</span>
            </button>
          </form>

          {trackingError && (
            <div style={{ color: 'var(--danger)', fontWeight: 600, marginBottom: 20 }}>
              {trackingError}
            </div>
          )}

          {trackedCase && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, flexWrap: 'wrap', gap: 10 }}>
                <div>
                  <h4 style={{ margin: 0, fontSize: '1.2rem' }}>Case #{trackedCase.complaint_id}</h4>
                  <p style={{ margin: '2px 0 0 0', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                    {trackedCase.category || trackedCase.crime_type} | Station: {trackedCase.cyber_cell_station}
                  </p>
                </div>
                <button onClick={() => handleDownloadAckPdf(trackedCase)} className="btn-secondary">
                  <Download size={16} />
                  <span>Download Acknowledgement</span>
                </button>
              </div>

              {/* Status Timeline */}
              <div className="timeline-track">
                <div className="timeline-step completed">
                  <div className="timeline-title">{t.statusReceived}</div>
                  <div className="timeline-desc">Lodged on National Cyber Crime System ({trackedCase.complaint_date})</div>
                </div>
                <div className="timeline-step completed">
                  <div className="timeline-title">{t.statusTriaged}</div>
                  <div className="timeline-desc">Assessed Risk Score: {trackedCase.risk_score}/100 ({trackedCase.risk_level})</div>
                </div>
                <div className={`timeline-step ${trackedCase.assigned_officer && trackedCase.assigned_officer !== 'Unassigned' ? 'completed' : 'current'}`}>
                  <div className="timeline-title">{t.statusAssigned}</div>
                  <div className="timeline-desc">Assigned to: {trackedCase.assigned_officer || 'Station House Officer'}</div>
                </div>
                <div className={`timeline-step ${trackedCase.current_status === 'Investigating' || trackedCase.current_status === 'Resolved' ? 'completed' : 'current'}`}>
                  <div className="timeline-title">{t.statusInvestigating}</div>
                  <div className="timeline-desc">{trackedCase.investigation_status || 'Preliminary Evidence Acquisition'}</div>
                </div>
                <div className={`timeline-step ${trackedCase.current_status === 'Resolved' ? 'completed' : ''}`}>
                  <div className="timeline-title">{t.statusFrozen} &amp; {t.statusResolved}</div>
                  <div className="timeline-desc">Beneficiary interdiction and judicial disposition status.</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 5: SCAM DOJO GAMIFIED AI SIMULATION */}
      {activeTab === 'dojo' && MODULE_FLAGS.SCAM_DOJO && (
        <div style={{ marginBottom: 28 }}>
          <ScamDojo apiBase={apiBase} lang={lang} />
        </div>
      )}

      {/* Scam of the Week Spotlight Card */}

      <div className="app-card" style={{ background: 'linear-gradient(135deg, #FFFFFF, #FAF7F2)', border: '1.5px solid var(--border-color)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: 24, alignItems: 'center' }}>
          <div>
            <span className="badge badge-high" style={{ marginBottom: 10 }}>Scam of the Week</span>
            <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: '1.4rem', color: 'var(--text-main)', marginBottom: 8 }}>
              "Digital Arrest" Law Enforcement Extortion Scheme
            </h3>
            <p style={{ fontSize: '0.92rem', color: 'var(--text-body)', lineHeight: 1.6 }}>
              Threat actors pose as customs, police, or judicial authorities via Skype/WhatsApp video calls, alleging illegal contraband parcels or financial laundering. They coerce victims to keep cameras on for hours and transfer life savings to "clearance accounts".
            </p>
            <div style={{ background: 'var(--bg-card)', padding: '12px 16px', borderRadius: 8, marginTop: 12, borderLeft: '4px solid var(--primary)', fontSize: '0.88rem' }}>
              <strong>Official CERT-In Advisory:</strong> Indian law enforcement agencies NEVER issue summons or place citizens under arrest via Skype or video call. Never remit funds to any personal or "verification" account.
            </div>
          </div>
          <div style={{ borderRadius: 'var(--radius-lg)', overflow: 'hidden', height: 220, boxShadow: 'var(--shadow-card)' }}>
            <img src="/images/cyber_awareness.jpg" alt="Cyber Awareness" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          </div>
        </div>
      </div>
    </div>
  );
}
