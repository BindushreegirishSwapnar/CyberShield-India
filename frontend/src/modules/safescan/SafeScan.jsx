import React, { useState, useEffect, useRef } from 'react';
import {
  QrCode, ShieldAlert, ShieldCheck, AlertTriangle, Search,
  Upload, Camera, FileText, ArrowRight, CheckCircle2,
  ExternalLink, Sparkles, RefreshCw, AlertOctagon, Phone,
  Globe, CreditCard, Share2, Zap
} from 'lucide-react';
import jsQR from 'jsqr';
import { createWorker } from 'tesseract.js';

export default function SafeScan({
  apiBase = '/api/v1',
  lang = 'en',
  onPrefillComplaint = null
}) {
  const [activeMode, setActiveMode] = useState('text'); // 'text', 'qr', 'ocr'
  const [entityType, setEntityType] = useState('phone'); // 'phone', 'upi', 'url', 'account'
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [verdict, setVerdict] = useState(null);
  const [ocrText, setOcrText] = useState('');
  const [ocrProgress, setOcrProgress] = useState(0);
  const [ocrProcessing, setOcrProcessing] = useState(false);

  const fileInputRef = useRef(null);
  const qrInputRef = useRef(null);

  // Check for PWA Web Share Target query params on mount
  useEffect(() => {
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const sharedTitle = urlParams.get('title') || '';
      const sharedText = urlParams.get('text') || '';
      const sharedUrl = urlParams.get('url') || '';
      const combined = `${sharedTitle} ${sharedText} ${sharedUrl}`.trim();

      if (combined) {
        setActiveMode('text');
        setInputValue(combined);
        handleDirectLookup(combined);
      }
    } catch (e) {
      console.warn("Share target read error:", e);
    }
  }, []);

  // Quick lookup handler
  const handleDirectLookup = async (valToUse, forcedType) => {
    const val = valToUse || inputValue;
    const type = forcedType || entityType;
    if (!val.trim()) return;

    setLoading(true);
    setVerdict(null);

    try {
      const res = await fetch(`${apiBase}/safescan/lookup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ entity_type: type, entity_value: val.trim() })
      });
      const json = await res.json();
      if (json.status === 'success') {
        setVerdict({
          type: 'lookup',
          data: json.data
        });
      }
    } catch (err) {
      console.error("Lookup failed:", err);
    } finally {
      setLoading(false);
    }
  };

  // QR Code Image File Decoder
  const handleQrUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setVerdict(null);

    const reader = new FileReader();
    reader.onload = (event) => {
      const img = new Image();
      img.onload = async () => {
        const canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);

        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const code = jsQR(imageData.data, imageData.width, imageData.height);

        if (code && code.data) {
          // Parse UPI QR via backend
          try {
            const res = await fetch(`${apiBase}/safescan/qr-check`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ qr_text: code.data })
            });
            const json = await res.json();
            if (json.status === 'success') {
              setVerdict({
                type: 'qr',
                data: json.data
              });
            }
          } catch (err) {
            console.error("QR analysis error:", err);
          }
        } else {
          alert("Could not detect a clear QR code in this image. Please upload a high-resolution photo.");
        }
        setLoading(false);
      };
      img.src = event.target.result;
    };
    reader.readAsDataURL(file);
  };

  // Screenshot OCR with Tesseract.js
  const handleOcrUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setOcrProcessing(true);
    setOcrProgress(10);
    setVerdict(null);

    try {
      const worker = await createWorker('eng');
      setOcrProgress(40);
      const ret = await worker.recognize(file);
      setOcrProgress(80);
      await worker.terminate();

      const extracted = ret.data.text;
      setOcrText(extracted);
      setOcrProgress(95);

      // Send to backend for bulk entity extraction & reputation lookups
      const res = await fetch(`${apiBase}/safescan/ocr-analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: extracted })
      });
      const json = await res.json();
      if (json.status === 'success') {
        setVerdict({
          type: 'ocr',
          data: json.data
        });
      }
    } catch (err) {
      console.error("OCR analysis error:", err);
      alert("Error extracting text from screenshot. Please try again.");
    } finally {
      setOcrProcessing(false);
      setOcrProgress(0);
    }
  };

  // Demo Presets for 1-click evaluation
  const runDemoPreset = (presetKey) => {
    if (presetKey === 'sbi_phish') {
      setActiveMode('text');
      setEntityType('url');
      setInputValue('https://sbi-kyc-verify.xyz/update-pan');
      handleDirectLookup('https://sbi-kyc-verify.xyz/update-pan', 'url');
    } else if (presetKey === 'mule_phone') {
      setActiveMode('text');
      setEntityType('phone');
      setInputValue('9876543210');
      handleDirectLookup('9876543210', 'phone');
    } else if (presetKey === 'deceptive_qr') {
      setActiveMode('qr');
      // Directly check simulated QR payload
      setLoading(true);
      fetch(`${apiBase}/safescan/qr-check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          qr_text: 'upi://pay?pa=fakeescrow99@ybl&pn=Maharashtra%20State%20Electricity%20Board&am=1450&cu=INR&tn=Bill%20Clearance'
        })
      })
      .then(res => res.json())
      .then(json => {
        if (json.status === 'success') {
          setVerdict({ type: 'qr', data: json.data });
        }
      })
      .finally(() => setLoading(false));
    }
  };

  return (
    <div>
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
            MODULE 3 • SAFE-SCAN
          </span>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-light)', fontStyle: 'italic' }}>
            Simulated / demo threat intelligence cross-referenced against 5,000 synthetic complaints
          </span>
        </div>

        {/* 1-Click Evaluation Presets */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-muted)' }}>QUICK DEMO:</span>
          <button
            onClick={() => runDemoPreset('sbi_phish')}
            className="control-btn"
            style={{ fontSize: '0.78rem', padding: '4px 10px', minHeight: 32 }}
          >
            🌐 Typosquat URL
          </button>
          <button
            onClick={() => runDemoPreset('mule_phone')}
            className="control-btn"
            style={{ fontSize: '0.78rem', padding: '4px 10px', minHeight: 32 }}
          >
            📱 Mule Phone
          </button>
          <button
            onClick={() => runDemoPreset('deceptive_qr')}
            className="control-btn"
            style={{ fontSize: '0.78rem', padding: '4px 10px', minHeight: 32 }}
          >
            ⚡ Deceptive QR
          </button>
        </div>
      </div>

      {/* Main Safe-Scan Interactive Console */}
      <div className="app-card" style={{
        background: '#FFFFFF',
        border: '2px solid var(--border-color)',
        padding: '24px',
        marginBottom: 24
      }}>
        {/* Input Mode Selector Tabs */}
        <div style={{
          display: 'flex',
          gap: 10,
          borderBottom: '1px solid var(--border-color)',
          paddingBottom: 14,
          marginBottom: 20,
          flexWrap: 'wrap'
        }}>
          <button
            onClick={() => { setActiveMode('text'); setVerdict(null); }}
            className={`control-btn ${activeMode === 'text' ? 'control-btn-primary' : ''}`}
            style={{ padding: '8px 16px', borderRadius: 20, display: 'flex', alignItems: 'center', gap: 8 }}
          >
            <Search size={16} />
            <span>Phone / UPI / URL Lookup</span>
          </button>

          <button
            onClick={() => { setActiveMode('qr'); setVerdict(null); }}
            className={`control-btn ${activeMode === 'qr' ? 'control-btn-primary' : ''}`}
            style={{ padding: '8px 16px', borderRadius: 20, display: 'flex', alignItems: 'center', gap: 8 }}
          >
            <QrCode size={16} />
            <span>UPI QR Inspector</span>
          </button>

          <button
            onClick={() => { setActiveMode('ocr'); setVerdict(null); }}
            className={`control-btn ${activeMode === 'ocr' ? 'control-btn-primary' : ''}`}
            style={{ padding: '8px 16px', borderRadius: 20, display: 'flex', alignItems: 'center', gap: 8 }}
          >
            <Camera size={16} />
            <span>Screenshot OCR Scanner</span>
          </button>
        </div>

        {/* MODE 1: Direct Text / Entity Lookup */}
        {activeMode === 'text' && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: '180px 1fr auto', gap: 12, alignItems: 'center' }}>
              <select
                className="form-select"
                value={entityType}
                onChange={e => setEntityType(e.target.value)}
                style={{ minHeight: 46 }}
              >
                <option value="phone">Phone Number</option>
                <option value="upi">UPI ID / VPA</option>
                <option value="url">URL / Domain</option>
                <option value="account">Bank Account / IFSC</option>
              </select>

              <input
                type="text"
                className="form-input"
                style={{ minHeight: 46, fontSize: '1rem', paddingLeft: 16 }}
                placeholder={
                  entityType === 'phone' ? 'e.g. +91 98765 43210' :
                  entityType === 'upi' ? 'e.g. refund-officer@okhdfcbank' :
                  entityType === 'url' ? 'e.g. sbi-kyc-verify.xyz/update' : 'e.g. 5010049281729'
                }
                value={inputValue}
                onChange={e => setInputValue(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleDirectLookup()}
              />

              <button
                onClick={() => handleDirectLookup()}
                className="btn-primary"
                style={{ minHeight: 46, padding: '0 24px', display: 'flex', alignItems: 'center', gap: 8 }}
                disabled={loading || !inputValue.trim()}
              >
                <Search size={18} />
                <span>Scan Reputation</span>
              </button>
            </div>
          </div>
        )}

        {/* MODE 2: UPI QR Code Inspector */}
        {activeMode === 'qr' && (
          <div style={{ textAlign: 'center', padding: '24px 16px' }}>
            <div style={{
              width: 80,
              height: 80,
              borderRadius: '50%',
              background: '#E8F6F3',
              color: 'var(--primary)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 16
            }}>
              <QrCode size={40} />
            </div>
            <h3 style={{ margin: '0 0 8px 0', fontSize: '1.25rem', color: 'var(--primary)' }}>
              Inspect Payment QR Code Before Scanning in Banking Apps
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', maxWidth: 540, margin: '0 auto 20px' }}>
              Upload or snap a photo of any printed or digital UPI QR code. Safe-Scan inspects the underlying destination VPA, merchant authorization, and prior fraud records.
            </p>

            <input
              type="file"
              ref={qrInputRef}
              accept="image/*"
              style={{ display: 'none' }}
              onChange={handleQrUpload}
            />

            <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
              <button
                onClick={() => qrInputRef.current?.click()}
                className="btn-primary"
                style={{ display: 'flex', alignItems: 'center', gap: 8 }}
                disabled={loading}
              >
                <Upload size={18} />
                <span>Upload QR Image</span>
              </button>
              <button
                onClick={() => runDemoPreset('deceptive_qr')}
                className="btn-secondary"
                style={{ display: 'flex', alignItems: 'center', gap: 8 }}
              >
                <Zap size={16} />
                <span>Load Deceptive Electricity QR Demo</span>
              </button>
            </div>
          </div>
        )}

        {/* MODE 3: Screenshot OCR Scanner */}
        {activeMode === 'ocr' && (
          <div style={{ textAlign: 'center', padding: '24px 16px' }}>
            <div style={{
              width: 80,
              height: 80,
              borderRadius: '50%',
              background: '#FAF7F2',
              color: 'var(--primary)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 16,
              border: '2px dashed var(--border-color)'
            }}>
              <Camera size={38} />
            </div>
            <h3 style={{ margin: '0 0 8px 0', fontSize: '1.25rem', color: 'var(--primary)' }}>
              Scan WhatsApp, SMS, or Telegram Screenshot
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', maxWidth: 540, margin: '0 auto 20px' }}>
              Upload an image of an extortion message or job offer. In-browser OCR will extract all suspect phone numbers, URLs, and payment handles for automated threat intelligence lookup.
            </p>

            <input
              type="file"
              ref={fileInputRef}
              accept="image/*"
              style={{ display: 'none' }}
              onChange={handleOcrUpload}
            />

            <button
              onClick={() => fileInputRef.current?.click()}
              className="btn-primary"
              style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}
              disabled={ocrProcessing}
            >
              <Upload size={18} />
              <span>Upload Chat Screenshot</span>
            </button>

            {ocrProcessing && (
              <div style={{ marginTop: 20, maxWidth: 400, margin: '20px auto 0' }}>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 6 }}>
                  Extracting text and cross-referencing national databases ({ocrProgress}%)...
                </div>
                <div style={{ width: '100%', height: 8, background: '#E5E7EB', borderRadius: 4, overflow: 'hidden' }}>
                  <div style={{ width: `${ocrProgress}%`, height: '100%', background: 'var(--primary)', transition: 'width 0.3s' }}></div>
                </div>
              </div>
            )}
          </div>
        )}

        {loading && (
          <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>
            <RefreshCw size={24} className="spin" />
            <div style={{ marginTop: 8 }}>Querying National 5,000-Complaint Database &amp; Whitelists...</div>
          </div>
        )}
      </div>

      {/* Safety Verdict Card Output */}
      {verdict && (
        <div className="app-card" style={{
          background: '#FFFFFF',
          border: `2px solid ${
            verdict.data.verdict === 'MALICIOUS' || verdict.data.overall_verdict === 'MALICIOUS' || verdict.data.risk_verdict === 'MALICIOUS' ? '#C8553D' :
            verdict.data.verdict === 'SUSPICIOUS' || verdict.data.overall_verdict === 'SUSPICIOUS' || verdict.data.risk_verdict === 'SUSPICIOUS' ? '#D9825B' :
            '#1F6F6B'
          }`,
          padding: '24px',
          boxShadow: '0 8px 24px rgba(0,0,0,0.06)'
        }}>
          {/* Verdict Banner Header */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: 20,
            flexWrap: 'wrap',
            gap: 12
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <div style={{
                width: 56,
                height: 56,
                borderRadius: '50%',
                background: verdict.data.verdict === 'MALICIOUS' || verdict.data.overall_verdict === 'MALICIOUS' || verdict.data.risk_verdict === 'MALICIOUS' ? '#FEE2E2' :
                            verdict.data.verdict === 'SUSPICIOUS' || verdict.data.overall_verdict === 'SUSPICIOUS' || verdict.data.risk_verdict === 'SUSPICIOUS' ? '#FEF3C7' : '#E8F6F3',
                color: verdict.data.verdict === 'MALICIOUS' || verdict.data.overall_verdict === 'MALICIOUS' || verdict.data.risk_verdict === 'MALICIOUS' ? '#DC2626' :
                       verdict.data.verdict === 'SUSPICIOUS' || verdict.data.overall_verdict === 'SUSPICIOUS' || verdict.data.risk_verdict === 'SUSPICIOUS' ? '#D97706' : '#1F6F6B',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
              }}>
                {verdict.data.verdict === 'MALICIOUS' || verdict.data.overall_verdict === 'MALICIOUS' || verdict.data.risk_verdict === 'MALICIOUS' ? <AlertOctagon size={32} /> :
                 verdict.data.verdict === 'SUSPICIOUS' || verdict.data.overall_verdict === 'SUSPICIOUS' || verdict.data.risk_verdict === 'SUSPICIOUS' ? <AlertTriangle size={32} /> :
                 <ShieldCheck size={32} />}
              </div>

              <div>
                <span className="badge" style={{
                  background: verdict.data.verdict === 'MALICIOUS' || verdict.data.overall_verdict === 'MALICIOUS' || verdict.data.risk_verdict === 'MALICIOUS' ? '#DC2626' :
                              verdict.data.verdict === 'SUSPICIOUS' || verdict.data.overall_verdict === 'SUSPICIOUS' || verdict.data.risk_verdict === 'SUSPICIOUS' ? '#D97706' : '#1F6F6B',
                  color: '#FFFFFF',
                  fontWeight: 700,
                  fontSize: '0.82rem',
                  letterSpacing: '0.5px',
                  marginBottom: 4
                }}>
                  {verdict.data.risk_badge || verdict.data.verdict_badge || `VERDICT: ${verdict.data.risk_verdict || verdict.data.verdict}`}
                </span>
                <h3 style={{ margin: '4px 0 0 0', fontSize: '1.4rem', color: 'var(--text-main)' }}>
                  {verdict.type === 'qr' ? `UPI Payment Destination: ${verdict.data.payee_name}` :
                   verdict.type === 'ocr' ? `Multi-Entity Intelligence Analysis` :
                   `Reputation Scan: ${verdict.data.entity_value}`}
                </h3>
              </div>
            </div>

            {/* 1-Tap Report to 1930 / I4C Button */}
            <button
              onClick={() => {
                if (onPrefillComplaint) {
                  onPrefillComplaint({
                    suspectPhone: verdict.data.entity_type === 'phone' ? verdict.data.entity_value : '',
                    suspectUpi: verdict.data.entity_type === 'upi' ? verdict.data.entity_value : (verdict.data.vpa || ''),
                    suspectUrl: verdict.data.entity_type === 'url' ? verdict.data.entity_value : '',
                    description: `Reported via Safe-Scan: ${verdict.data.summary || 'Suspicious financial communication'}`
                  });
                } else {
                  alert("Complaint prefilled! Switching to complaint registration wizard.");
                }
              }}
              className="btn-primary"
              style={{
                background: '#DC2626',
                borderColor: '#B91C1C',
                padding: '8px 18px',
                borderRadius: 20,
                fontSize: '0.88rem',
                display: 'flex',
                alignItems: 'center',
                gap: 8
              }}
            >
              <AlertTriangle size={16} />
              <span>Report this to 1930 / I4C</span>
            </button>
          </div>

          {/* Detailed Findings Grid */}
          <div style={{
            background: '#FAF7F2',
            padding: '18px',
            borderRadius: 12,
            border: '1px solid var(--border-color)',
            marginBottom: 16
          }}>
            {/* If Lookalike Domain Detected */}
            {verdict.data.lookalike_analysis && verdict.data.lookalike_analysis.is_lookalike && (
              <div style={{
                background: '#FEE2E2',
                borderLeft: '4px solid #DC2626',
                padding: '12px 16px',
                borderRadius: 6,
                marginBottom: 14
              }}>
                <div style={{ fontWeight: 700, color: '#B91C1C', marginBottom: 2 }}>
                  ⚠️ Lookalike Domain Impersonation Detected!
                </div>
                <div style={{ fontSize: '0.9rem', color: '#7F1D1D' }}>
                  {verdict.data.lookalike_analysis.notes} (Targeting: <strong>{verdict.data.lookalike_analysis.official_target}</strong>)
                </div>
              </div>
            )}

            {/* If QR Mismatch Detected */}
            {verdict.type === 'qr' && (
              <div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 14, marginBottom: 12 }}>
                  <div>
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>DESTINATION VPA:</span>
                    <div style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--primary)' }}>{verdict.data.vpa}</div>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>DISPLAYED PAYEE NAME:</span>
                    <div style={{ fontWeight: 700, fontSize: '1rem' }}>{verdict.data.payee_name}</div>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>MERCHANT CATEGORY:</span>
                    <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{verdict.data.merchant_code}</div>
                  </div>
                </div>

                {verdict.data.risk_flags.length > 0 && (
                  <div style={{ background: '#FEF3C7', padding: '10px 14px', borderRadius: 8, borderLeft: '4px solid #D97706', fontSize: '0.88rem', color: '#92400E' }}>
                    {verdict.data.risk_flags.map((f, i) => <div key={i}>• {f}</div>)}
                  </div>
                )}
              </div>
            )}

            {/* Summary Text */}
            <p style={{ margin: '8px 0 0 0', fontSize: '0.95rem', color: 'var(--text-main)', lineHeight: 1.5 }}>
              {verdict.data.summary || (verdict.type === 'qr' ? 'UPI transaction destination validated against security registries.' : 'Entity evaluated against 5,000 complaints.')}
            </p>
          </div>

          {/* Database Matches Telemetry */}
          {verdict.data.complaint_count !== undefined && (
            <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              <div>Linked Complaints in Database: <strong style={{ color: 'var(--text-main)' }}>{verdict.data.complaint_count}</strong></div>
              <div>Reported Financial Loss: <strong style={{ color: 'var(--text-main)' }}>₹{verdict.data.total_loss_inr?.toLocaleString() || 0}</strong></div>
              {verdict.data.categories?.length > 0 && (
                <div>Crime Typologies: <strong style={{ color: 'var(--text-main)' }}>{verdict.data.categories.join(', ')}</strong></div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
