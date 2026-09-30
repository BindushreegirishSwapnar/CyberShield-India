import React, { useState, useEffect, useRef } from 'react';
import {
  Swords, ShieldAlert, AlertTriangle, Award, CheckCircle2,
  Volume2, VolumeX, Mic, MicOff, Send, RefreshCw, Sparkles,
  UserCheck, ShieldCheck, Flame, Info, ExternalLink, HelpCircle,
  Eye, PhoneOff, ArrowRight, Download, Share2, EyeOff
} from 'lucide-react';
import { jsPDF } from 'jspdf';

export default function ScamDojo({ apiBase = '/api/v1', lang = 'en' }) {
  // Scenario state
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState('digital_arrest');
  const [elderMode, setElderMode] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(false);

  // Chat state
  const [messages, setMessages] = useState([]);
  const [inputVal, setInputVal] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionEnded, setSessionEnded] = useState(false);
  const [endReason, setEndReason] = useState(null);

  // Red Flag Coach state
  const [score, setScore] = useState(50);
  const [latestCoachFeedback, setLatestCoachFeedback] = useState([]);
  const [detectedRedFlags, setDetectedRedFlags] = useState(['AUTHORITY', 'FEAR', 'ISOLATION']);
  const [suggestedCounters, setSuggestedCounters] = useState([]);
  const [psychologicalBreakdown, setPsychologicalBreakdown] = useState([]);

  // End Game / Certificate state
  const [certificateData, setCertificateData] = useState(null);
  const [showCertificateModal, setShowCertificateModal] = useState(false);

  // Speech Recognition state
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef(null);

  const activeScenario = scenarios.find(s => s.id === selectedScenarioId) || scenarios[0];

  // 1. Fetch Scenarios
  useEffect(() => {
    async function loadScenarios() {
      try {
        const res = await fetch(`${apiBase}/dojo/scenarios`);
        const json = await res.json();
        if (json.status === 'success' && json.data.length > 0) {
          setScenarios(json.data);
          initSession(json.data[0]);
        }
      } catch (err) {
        console.error("Failed to load scenarios:", err);
      }
    }
    loadScenarios();
  }, [apiBase]);

  // Scroll to bottom on messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Text to Speech
  const speakMessage = (text) => {
    if (!soundEnabled || !('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = elderMode ? 0.85 : 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  };

  // Initialize a Scenario Session
  const initSession = (scen) => {
    if (!scen) return;
    setMessages([
      {
        sender: 'scammer',
        role: scen.scammer_role,
        avatar: scen.avatar,
        text: scen.opening_message,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
    setScore(50);
    setSessionEnded(false);
    setEndReason(null);
    setDetectedRedFlags(scen.red_flags || []);
    setSuggestedCounters(scen.recommended_counters || []);
    setLatestCoachFeedback(["⚠️ Scammer opened with high-pressure coercion. Challenge their claims using facts or legal mandates."]);
    setPsychologicalBreakdown([
      {
        tactic: scen.red_flags?.[0] || "Coercive Pressure",
        description: "Scammer attempts to bypass rational thought through manufactured shock.",
        severity: "HIGH"
      }
    ]);

    if (soundEnabled) {
      speakMessage(scen.opening_message);
    }
  };

  const handleScenarioChange = (id) => {
    setSelectedScenarioId(id);
    const scen = scenarios.find(s => s.id === id);
    if (scen) {
      initSession(scen);
    }
  };

  // Speech Recognition (Microphone)
  const toggleSpeechRecognition = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert("Speech recognition is not supported in this browser.");
      return;
    }

    if (isListening) {
      setIsListening(false);
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = lang === 'hi' ? 'hi-IN' : lang === 'kn' ? 'kn-IN' : 'en-IN';

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInputVal(prev => prev ? `${prev} ${transcript}` : transcript);
    };

    recognition.start();
  };

  // Submit citizen message
  const handleSendMessage = async (msgText) => {
    const textToSend = msgText || inputVal;
    if (!textToSend.trim() || loading || sessionEnded) return;

    setInputVal('');
    const newCitizenMsg = {
      sender: 'citizen',
      text: textToSend.trim(),
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    const updatedHistory = [...messages, newCitizenMsg];
    setMessages(updatedHistory);
    setLoading(true);

    try {
      const res = await fetch(`${apiBase}/dojo/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scenario_id: selectedScenarioId,
          conversation_history: updatedHistory.map(m => ({
            role: m.sender === 'citizen' ? 'user' : 'scammer',
            content: m.text
          })),
          user_message: textToSend.trim(),
          elder_mode: elderMode
        })
      });

      const json = await res.json();
      if (json.status === 'success') {
        const turnData = json.data;
        const delta = turnData.coach_analysis.citizen_resilience_delta || 0;
        setScore(prev => Math.max(0, Math.min(100, prev + delta)));
        setLatestCoachFeedback(turnData.coach_analysis.coach_feedback || []);
        setDetectedRedFlags(turnData.coach_analysis.detected_red_flags || []);
        setSuggestedCounters(turnData.suggested_counters || []);
        setPsychologicalBreakdown(turnData.coach_analysis.psychological_breakdown || []);

        const scammerMsg = {
          sender: 'scammer',
          role: activeScenario?.scammer_role || 'Scammer',
          avatar: activeScenario?.avatar || '⚠️',
          text: turnData.scammer_message,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };

        setMessages(prev => [...prev, scammerMsg]);
        if (soundEnabled) {
          speakMessage(turnData.scammer_message);
        }

        if (turnData.is_session_ended) {
          setSessionEnded(true);
          setEndReason(turnData.end_reason);
        }
      }
    } catch (err) {
      console.error("Dojo chat error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Finish session & generate certificate
  const handleFinishTraining = async () => {
    try {
      const res = await fetch(`${apiBase}/dojo/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scenario_id: selectedScenarioId,
          total_score: score - 50,
          turns_played: Math.ceil(messages.length / 2),
          elder_mode: elderMode
        })
      });
      const json = await res.json();
      if (json.status === 'success') {
        setCertificateData(json);
        setShowCertificateModal(true);
      }
    } catch (err) {
      console.error("Evaluation error:", err);
    }
  };

  // Generate downloadable PDF Certificate
  const handleDownloadCertificate = () => {
    if (!certificateData) return;
    const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
    const cert = certificateData.certificate;

    // Background styling
    doc.setFillColor(250, 247, 242);
    doc.rect(0, 0, 297, 210, 'F');

    // Outer border
    doc.setDrawColor(31, 111, 107);
    doc.setLineWidth(3);
    doc.rect(10, 10, 277, 190);

    // Inner gold border
    doc.setDrawColor(217, 130, 91);
    doc.setLineWidth(1);
    doc.rect(14, 14, 269, 182);

    // Header
    doc.setFont("helvetica", "bold");
    doc.setFontSize(22);
    doc.setTextColor(31, 111, 107);
    doc.text("CYBERSHIELD INDIA • NATIONAL SAFETY ACADEMY", 148.5, 36, { align: "center" });

    doc.setFontSize(13);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(100, 100, 100);
    doc.text("Under National Cyber Crime Coordination Centre (I4C) Standards", 148.5, 46, { align: "center" });

    // Certificate Title
    doc.setFont("times", "bolditalic");
    doc.setFontSize(28);
    doc.setTextColor(20, 20, 20);
    doc.text("Certificate of Scam Immunity", 148.5, 68, { align: "center" });

    doc.setFont("helvetica", "normal");
    doc.setFontSize(14);
    doc.setTextColor(80, 80, 80);
    doc.text("This official credential certifies that", 148.5, 84, { align: "center" });

    // Recipient
    doc.setFont("helvetica", "bold");
    doc.setFontSize(22);
    doc.setTextColor(31, 111, 107);
    doc.text(cert.recipient, 148.5, 100, { align: "center" });

    // Details
    doc.setFont("helvetica", "normal");
    doc.setFontSize(13);
    doc.setTextColor(60, 60, 60);
    doc.text(
      `has successfully countered interactive psychological extortion simulations in the ${activeScenario?.title || 'Cyber Threat'} scenario, demonstrating a defensive immunity rating of:`,
      148.5, 116, { align: "center", maxWidth: 220 }
    );

    // Badge Title
    doc.setFont("helvetica", "bold");
    doc.setFontSize(20);
    doc.setTextColor(217, 130, 91);
    doc.text(`${certificateData.badge_name} (${certificateData.immunity_score}/100)`, 148.5, 138, { align: "center" });

    // Certificate metadata
    doc.setFontSize(10);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(120, 120, 120);
    doc.text(`Certificate ID: ${cert.cert_id}`, 25, 172);
    doc.text(`Issue Date: ${cert.date}`, 25, 178);
    doc.text(`Verification Cryptographic Hash: ${cert.verification_hash.slice(0, 32)}...`, 25, 184);

    doc.setFont("helvetica", "bold");
    doc.text("Director of Cyber Literacy", 270, 172, { align: "right" });
    doc.setFont("helvetica", "normal");
    doc.text("CyberShield India Academy", 270, 178, { align: "right" });

    doc.save(`CyberShield_Immunity_Certificate_${cert.cert_id}.pdf`);
  };

  return (
    <div style={{
      fontSize: elderMode ? '1.25rem' : '1rem',
      lineHeight: elderMode ? 1.6 : 1.45
    }}>
      {/* Simulation / Demo Environment Warning Tag */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: 12,
        marginBottom: 16
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span className="demo-chip" style={{ background: '#1F6F6B', color: '#FFFFFF', fontWeight: 700 }}>
            MODULE 2 • SCAM DOJO
          </span>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-light)', fontStyle: 'italic' }}>
            Simulated / demo training sandbox — No real funds or personal credentials are ever exposed
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {/* Streak indicator */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            background: '#FEF3C7',
            color: '#B45309',
            padding: '4px 12px',
            borderRadius: 20,
            fontSize: '0.88rem',
            fontWeight: 700,
            border: '1px solid #FCD34D'
          }}>
            <Flame size={16} color="#D97706" />
            <span>3-Day Dojo Streak</span>
          </div>

          {/* Elder Mode Toggle */}
          <button
            onClick={() => setElderMode(!elderMode)}
            className={`control-btn ${elderMode ? 'control-btn-primary' : ''}`}
            style={{
              borderRadius: 20,
              padding: '6px 14px',
              fontSize: '0.85rem',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: 6
            }}
            title="Toggle Elder Mode with extra large text and simplified guidance"
          >
            {elderMode ? <Eye size={16} /> : <EyeOff size={16} />}
            <span>Elder Mode: {elderMode ? 'ON' : 'OFF'}</span>
          </button>
        </div>
      </div>

      {/* Scenario Selection Tabs */}
      <div style={{
        display: 'flex',
        gap: 10,
        marginBottom: 20,
        overflowX: 'auto',
        paddingBottom: 6
      }}>
        {scenarios.map(scen => (
          <button
            key={scen.id}
            onClick={() => handleScenarioChange(scen.id)}
            className={`control-btn ${selectedScenarioId === scen.id ? 'control-btn-primary' : ''}`}
            style={{
              padding: '10px 16px',
              borderRadius: 12,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              fontSize: elderMode ? '1.1rem' : '0.92rem',
              fontWeight: 600,
              whiteSpace: 'nowrap'
            }}
          >
            <span>{scen.avatar}</span>
            <span>{scen.title}</span>
          </button>
        ))}
      </div>

      {/* Main Training Arena: 2-Column Split */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: 24,
        alignItems: 'start'
      }}>
        {/* Left Column: Interactive Chat Sandbox */}
        <div className="app-card" style={{
          display: 'flex',
          flexDirection: 'column',
          height: elderMode ? '680px' : '600px',
          padding: 0,
          overflow: 'hidden',
          border: '2px solid var(--border-color)',
          background: '#FFFFFF'
        }}>
          {/* Chat Header (Simulated Caller / Scammer ID) */}
          <div style={{
            background: 'linear-gradient(135deg, #1F6F6B 0%, #154D4A 100%)',
            color: '#FFFFFF',
            padding: '16px 20px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{
                width: 44,
                height: 44,
                borderRadius: '50%',
                background: 'rgba(255,255,255,0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.4rem'
              }}>
                {activeScenario?.avatar || '⚠️'}
              </div>
              <div>
                <h4 style={{ margin: 0, fontSize: elderMode ? '1.25rem' : '1.05rem', fontWeight: 700 }}>
                  {activeScenario?.scammer_role || 'Suspect'}
                </h4>
                <div style={{ fontSize: '0.8rem', opacity: 0.85, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#EF4444', display: 'inline-block' }}></span>
                  <span>Active Coercive Threat Simulation</span>
                </div>
              </div>
            </div>

            {/* Read Aloud Audio Toggle */}
            <button
              onClick={() => setSoundEnabled(!soundEnabled)}
              style={{
                background: soundEnabled ? 'rgba(255,255,255,0.25)' : 'transparent',
                border: '1px solid rgba(255,255,255,0.4)',
                color: '#FFFFFF',
                borderRadius: 20,
                padding: '6px 12px',
                cursor: 'pointer',
                fontSize: '0.82rem',
                display: 'flex',
                alignItems: 'center',
                gap: 6
              }}
              title="Speak scammer messages aloud"
            >
              {soundEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
              <span>{soundEnabled ? 'Speech ON' : 'Speech OFF'}</span>
            </button>
          </div>

          {/* Message Stream */}
          <div style={{
            flex: 1,
            overflowY: 'auto',
            padding: '20px',
            background: '#FAF7F2',
            display: 'flex',
            flexDirection: 'column',
            gap: 16
          }}>
            {messages.map((m, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  justifyContent: m.sender === 'citizen' ? 'flex-end' : 'flex-start'
                }}
              >
                <div style={{
                  maxWidth: '85%',
                  background: m.sender === 'citizen' ? '#1F6F6B' : '#FFFFFF',
                  color: m.sender === 'citizen' ? '#FFFFFF' : '#1F2937',
                  borderRadius: m.sender === 'citizen' ? '16px 16px 2px 16px' : '16px 16px 16px 2px',
                  padding: elderMode ? '16px 20px' : '14px 18px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                  border: m.sender === 'scammer' ? '2px solid #FCA5A5' : 'none'
                }}>
                  {m.sender === 'scammer' && (
                    <div style={{
                      fontSize: '0.78rem',
                      fontWeight: 700,
                      color: '#DC2626',
                      marginBottom: 6,
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px'
                    }}>
                      ⚠️ {m.role}
                    </div>
                  )}
                  <div style={{ fontSize: elderMode ? '1.2rem' : '0.96rem', wordBreak: 'break-word' }}>
                    {m.text}
                  </div>
                  <div style={{
                    fontSize: '0.72rem',
                    color: m.sender === 'citizen' ? 'rgba(255,255,255,0.7)' : '#9CA3AF',
                    textAlign: 'right',
                    marginTop: 6
                  }}>
                    {m.time}
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                <RefreshCw size={16} className="spin" />
                <span>Scammer analyzing your psychological defense...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Counter-Phrase Bank */}
          {!sessionEnded && suggestedCounters.length > 0 && (
            <div style={{
              background: '#F5EFE6',
              padding: '10px 16px',
              borderTop: '1px solid var(--border-color)',
              display: 'flex',
              gap: 8,
              overflowX: 'auto',
              alignItems: 'center'
            }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--primary)', whiteSpace: 'nowrap' }}>
                DEFENSE PILLS:
              </span>
              {suggestedCounters.map((phrase, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendMessage(phrase)}
                  disabled={loading}
                  style={{
                    background: '#FFFFFF',
                    border: '1px solid var(--border-color)',
                    borderRadius: 16,
                    padding: '5px 12px',
                    fontSize: elderMode ? '0.95rem' : '0.8rem',
                    cursor: 'pointer',
                    whiteSpace: 'nowrap',
                    color: 'var(--primary)',
                    fontWeight: 600
                  }}
                  title="Click to fire counter-response"
                >
                  💬 {phrase}
                </button>
              ))}
            </div>
          )}

          {/* Chat Input Bar */}
          <div style={{
            padding: '14px 16px',
            background: '#FFFFFF',
            borderTop: '1px solid var(--border-color)',
            display: 'flex',
            gap: 10,
            alignItems: 'center'
          }}>
            <button
              onClick={toggleSpeechRecognition}
              className={`control-btn ${isListening ? 'control-btn-primary' : ''}`}
              style={{
                borderRadius: '50%',
                width: 44,
                height: 44,
                padding: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
              }}
              title="Voice Input (Speech-to-Text)"
            >
              {isListening ? <MicOff size={20} color="#DC2626" /> : <Mic size={20} />}
            </button>

            <input
              type="text"
              className="form-input"
              style={{
                flex: 1,
                minHeight: 44,
                fontSize: elderMode ? '1.15rem' : '0.95rem',
                borderRadius: 24,
                paddingLeft: 16
              }}
              placeholder={elderMode ? "Type what you would say..." : "Counter the scammer or enter your reply..."}
              value={inputVal}
              onChange={e => setInputVal(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSendMessage()}
              disabled={loading || sessionEnded}
            />

            <button
              onClick={() => handleSendMessage()}
              className="btn-primary"
              style={{
                borderRadius: 24,
                minHeight: 44,
                padding: '0 20px',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                flexShrink: 0
              }}
              disabled={loading || sessionEnded || !inputVal.trim()}
            >
              <span>Send</span>
              <Send size={16} />
            </button>
          </div>
        </div>

        {/* Right Column: Live Red Flag Coach & Scoring */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Live Immunity Gauge Card */}
          <div className="app-card" style={{
            background: 'linear-gradient(135deg, #FAF7F2 0%, #FFFFFF 100%)',
            border: '2px solid var(--border-color)',
            padding: '24px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: 8 }}>
                  <ShieldCheck size={22} color="var(--primary)" />
                  <span>Red Flag Coach</span>
                </h3>
                <p style={{ margin: '4px 0 0 0', fontSize: '0.84rem', color: 'var(--text-muted)' }}>
                  Real-time cognitive resilience &amp; manipulation telemetry
                </p>
              </div>

              {/* Immunity Score Badge */}
              <div style={{
                width: 68,
                height: 68,
                borderRadius: '50%',
                background: score >= 70 ? '#E8F6F3' : score >= 45 ? '#FEF9E7' : '#FDF2E9',
                border: `3px solid ${score >= 70 ? '#1F6F6B' : score >= 45 ? '#D9825B' : '#C8553D'}`,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
              }}>
                <span style={{ fontSize: '1.35rem', fontWeight: 800, color: score >= 70 ? '#1F6F6B' : score >= 45 ? '#D9825B' : '#C8553D', lineHeight: 1 }}>
                  {score}
                </span>
                <span style={{ fontSize: '0.62rem', fontWeight: 700, color: 'var(--text-light)', textTransform: 'uppercase' }}>
                  IMMUNITY
                </span>
              </div>
            </div>

            {/* Coach Live Feedback */}
            <div style={{
              background: '#FDFBF7',
              borderRadius: 12,
              padding: '14px',
              border: '1px solid var(--border-color)',
              marginBottom: 16
            }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase' }}>
                Coach Evaluation:
              </div>
              {latestCoachFeedback.map((fb, idx) => (
                <div key={idx} style={{ fontSize: elderMode ? '1.05rem' : '0.88rem', color: 'var(--text-main)', marginBottom: 4 }}>
                  {fb}
                </div>
              ))}
            </div>

            {/* Detected Psychological Manipulation Badges */}
            <div style={{ marginBottom: 18 }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase' }}>
                Active Psychological Exploits:
              </div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {detectedRedFlags.map((flag, idx) => (
                  <span
                    key={idx}
                    style={{
                      background: '#FEE2E2',
                      color: '#B91C1C',
                      padding: '4px 10px',
                      borderRadius: 14,
                      fontSize: '0.78rem',
                      fontWeight: 700,
                      border: '1px solid #FCA5A5'
                    }}
                  >
                    🚩 {flag}
                  </span>
                ))}
              </div>
            </div>

            {/* Exploit Breakdown */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 20 }}>
              {psychologicalBreakdown.map((item, idx) => (
                <div key={idx} style={{ background: '#FFFFFF', padding: '10px 14px', borderRadius: 8, border: '1px solid var(--border-color)', fontSize: '0.82rem' }}>
                  <div style={{ fontWeight: 700, color: '#C8553D', marginBottom: 2 }}>{item.tactic}</div>
                  <div style={{ color: 'var(--text-muted)' }}>{item.description}</div>
                </div>
              ))}
            </div>

            {/* End / Certificate Action Button */}
            <button
              onClick={handleFinishTraining}
              className="btn-primary"
              style={{
                width: '100%',
                minHeight: 48,
                borderRadius: 12,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 8,
                fontWeight: 700
              }}
            >
              <Award size={18} />
              <span>Complete Training &amp; Get Certificate</span>
            </button>
          </div>
        </div>
      </div>

      {/* Certificate Modal */}
      {showCertificateModal && certificateData && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.65)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: 20
        }}>
          <div style={{
            background: '#FFFFFF',
            borderRadius: 16,
            maxWidth: 620,
            width: '100%',
            padding: 32,
            boxShadow: '0 20px 40px rgba(0,0,0,0.2)',
            border: '3px solid var(--primary)',
            maxHeight: '90vh',
            overflowY: 'auto'
          }}>
            <div style={{ textAlign: 'center', marginBottom: 20 }}>
              <div style={{
                width: 72,
                height: 72,
                borderRadius: '50%',
                background: '#E8F6F3',
                color: '#1F6F6B',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: 12
              }}>
                <Award size={44} />
              </div>
              <h2 style={{ fontFamily: 'var(--font-serif)', color: 'var(--primary)', margin: '0 0 6px 0', fontSize: '1.8rem' }}>
                Scam Immunity Certified!
              </h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', margin: 0 }}>
                CyberShield India National Safety Academy Credential
              </p>
            </div>

            {/* Certificate Preview Card */}
            <div style={{
              background: '#FAF7F2',
              border: '2px solid var(--border-color)',
              borderRadius: 12,
              padding: '20px',
              marginBottom: 24,
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-light)', letterSpacing: '1px' }}>
                AWARDED BADGE
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: certificateData.badge_color, margin: '6px 0' }}>
                {certificateData.badge_name}
              </div>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: 14 }}>
                {certificateData.badge_title} • Immunity Rating: {certificateData.immunity_score}/100
              </div>

              <div style={{ textAlign: 'left', background: '#FFFFFF', padding: '14px', borderRadius: 8, fontSize: '0.84rem' }}>
                <div style={{ fontWeight: 700, color: 'var(--primary)', marginBottom: 4 }}>Defensive Strengths:</div>
                {certificateData.strengths.map((s, i) => (
                  <div key={i} style={{ color: '#16A34A', marginBottom: 2 }}>✓ {s}</div>
                ))}
              </div>
            </div>

            {/* Modal Actions */}
            <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
              <button onClick={handleDownloadCertificate} className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Download size={18} />
                <span>Download Official Certificate (PDF)</span>
              </button>
              <button onClick={() => setShowCertificateModal(false)} className="btn-secondary">
                <span>Return to Dojo</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
