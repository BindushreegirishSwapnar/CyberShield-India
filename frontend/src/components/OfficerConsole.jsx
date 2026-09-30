import React, { useState, useEffect } from 'react';
import {
  Shield, AlertTriangle, Clock, Search, Filter, RefreshCw,
  FileText, Download, CheckCircle2, Sliders, MessageSquare,
  Copy, Check, User, ArrowUpRight, Lock, ExternalLink, Activity
} from 'lucide-react';
import { jsPDF } from 'jspdf';

const PRESET_USERS = [
  {
    role: "Administrator",
    name: "Dr. Rajeshwar Rao, IPS",
    email: "admin@cybercrime.gov.in",
    username: "admin",
    pass: "Admin@2026",
    badge: "DG Cyber Operations"
  },
  {
    role: "Senior Analyst",
    name: "Pooja Sharma",
    email: "analyst.sharma@cybercrime.gov.in",
    username: "analyst_sharma",
    pass: "Analyst@2026",
    badge: "Lead Intelligence Analyst"
  },
  {
    role: "Investigator",
    name: "Inspector Anand Patil",
    email: "io.patil@cybercrime.gov.in",
    username: "io_patil",
    pass: "Officer@2026",
    badge: "Cyber Crime PS SHO"
  }
];

export default function OfficerConsole({
  t,
  lang,
  currentUser,
  onLogin,
  onLogout,
  onOpenCaseInCopilot,
  apiBase = '/api/v1'
}) {
  // Login Form State
  const [loginUsername, setLoginUsername] = useState('admin');
  const [loginPassword, setLoginPassword] = useState('Admin@2026');
  const [loginError, setLoginError] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);

  // Triage Queue State
  const [cases, setCases] = useState([]);
  const [loadingCases, setLoadingCases] = useState(false);
  const [totalCases, setTotalCases] = useState(0);
  const [page, setPage] = useState(1);

  // Filters
  const [filterCategory, setFilterCategory] = useState('All');
  const [filterRisk, setFilterRisk] = useState('All');
  const [filterState, setFilterState] = useState('All');
  const [filterStatus, setFilterStatus] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  // Selected Case Modal
  const [selectedCase, setSelectedCase] = useState(null);
  const [caseNotes, setCaseNotes] = useState('');
  const [copiedText, setCopiedText] = useState('');
  const [updatingStatus, setUpdatingStatus] = useState(false);

  // What-If Simulator State
  const [simCategory, setSimCategory] = useState('Online Financial Fraud');
  const [simLoss, setSimLoss] = useState(45000);
  const [simDelayHours, setSimDelayHours] = useState(2);
  const [simPii, setSimPii] = useState(false);
  const [simAccountComp, setSimAccountComp] = useState(true);

  // Fetch Cases from Backend
  const fetchCases = async () => {
    setLoadingCases(true);
    try {
      const params = new URLSearchParams({
        page: String(page),
        page_size: '15',
        sort_by: 'risk_score',
        sort_order: 'desc'
      });
      if (filterCategory !== 'All') params.append('crime_type', filterCategory);
      if (filterRisk !== 'All') params.append('risk_level', filterRisk);
      if (filterState !== 'All') params.append('state', filterState);
      if (filterStatus !== 'All') params.append('status', filterStatus);
      if (searchQuery.trim()) params.append('search', searchQuery.trim());

      const res = await fetch(`${apiBase}/cases?${params.toString()}`);
      const json = await res.json();
      if (res.ok && json.data) {
        setCases(json.data);
        setTotalCases(json.total || json.data.length);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingCases(false);
    }
  };

  useEffect(() => {
    if (currentUser) {
      fetchCases();
    }
  }, [currentUser, page, filterCategory, filterRisk, filterState, filterStatus]);

  // Handle Login
  const handlePerformLogin = async (e) => {
    e.preventDefault();
    setLoginLoading(true);
    setLoginError('');

    try {
      const res = await fetch(`${apiBase}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: loginUsername.trim(),
          password: loginPassword
        })
      });

      const json = await res.json();
      if (res.ok && json.status === 'success') {
        onLogin(json.user, json.token);
      } else {
        setLoginError(json.message || "Invalid credentials.");
      }
    } catch {
      setLoginError("Could not connect to authentication service.");
    } finally {
      setLoginLoading(false);
    }
  };

  // Quick Preset Login
  const handleQuickPreset = (preset) => {
    setLoginUsername(preset.username);
    setLoginPassword(preset.pass);
  };

  // Copy to clipboard
  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopiedText(text);
    setTimeout(() => setCopiedText(''), 2500);
  };

  // Update Case Status
  const handleUpdateStatus = async (newStatus) => {
    if (!selectedCase) return;
    setUpdatingStatus(true);
    try {
      const res = await fetch(`${apiBase}/cases/${selectedCase.id || selectedCase.complaint_id}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: newStatus,
          note: `Status transition to ${newStatus} by ${currentUser?.full_name || 'Officer'}`
        })
      });
      if (res.ok) {
        setSelectedCase(prev => ({ ...prev, current_status: newStatus }));
        fetchCases();
      }
    } catch {
      alert("Failed to update case status.");
    } finally {
      setUpdatingStatus(false);
    }
  };

  // Generate Draft FIR Summary PDF
  const handleDownloadFirPdf = async (comp) => {
    try {
      const res = await fetch(`${apiBase}/reports/case/${comp.complaint_id}/fir-draft`);
      const json = await res.json();
      const firData = json.data || {};

      const doc = new jsPDF();
      doc.setFont("helvetica", "bold");
      doc.setFontSize(14);
      doc.text("FIRST INFORMATION REPORT (DRAFT SUMMARY)", 14, 20);
      doc.setFontSize(9);
      doc.setFont("helvetica", "normal");
      doc.text("Under Section 173 Bharatiya Nagarik Suraksha Sanhita 2023 / Section 154 CrPC", 14, 26);

      doc.setDrawColor(31, 111, 107);
      doc.line(14, 30, 196, 30);

      doc.setFontSize(10);
      doc.text(`Police Station: ${firData.station || comp.cyber_cell_station || 'Cyber PS'}`, 14, 38);
      doc.text(`Reference Case ID: ${comp.complaint_id}`, 14, 45);
      doc.text(`Date of Registration: ${comp.complaint_date || '2026-09-29'}`, 14, 52);
      doc.text(`Investigating Officer: ${comp.assigned_officer || 'Station House Officer'}`, 14, 59);

      doc.setFont("helvetica", "bold");
      doc.text("STATUTORY PENAL PROVISIONS CITED:", 14, 70);
      doc.setFont("helvetica", "normal");
      doc.setFontSize(9);
      let y = 78;
      const statutes = firData.statutes || [
        { section: "Section 66D IT Act", title: "Cheating by Personation", bns_equivalent: "Section 318(4) BNS" }
      ];
      statutes.forEach(s => {
        doc.text(`• ${s.section}: ${s.title} (${s.bns_equivalent || ''})`, 18, y);
        y += 7;
      });

      y += 6;
      doc.setFont("helvetica", "bold");
      doc.setFontSize(10);
      doc.text("Complainant Statement & Allegation:", 14, y);
      doc.setFont("helvetica", "normal");
      doc.setFontSize(8.5);
      const splitDesc = doc.splitTextToSize(comp.description || 'No description provided.', 182);
      doc.text(splitDesc.slice(0, 14), 14, y + 7);

      y += 85;
      doc.setFont("helvetica", "bold");
      doc.setFontSize(9.5);
      doc.text("INVESTIGATIVE DIRECTIVES UNDER SECTION 94 BNSS:", 14, y);
      doc.setFont("helvetica", "normal");
      doc.setFontSize(8.5);
      doc.text("1. Immediate notice to beneficiary banks for lien marking and reversal.", 18, y + 6);
      doc.text("2. Subpoena telecom providers for subscriber CDR and IPDR under Sec 63 BSA 2023.", 18, y + 12);
      doc.text("3. Dispatch automated I4C alert to prevent mule fund layering across jurisdictions.", 18, y + 18);

      doc.save(`FIR_Draft_${comp.complaint_id}.pdf`);
    } catch {
      alert("Failed to compile FIR draft PDF.");
    }
  };

  // Calculate What-If Simulator Risk & Recovery Chance
  const calculateWhatIf = () => {
    // Loss factor
    let lossFactor = simLoss >= 500000 ? 25 : simLoss >= 200000 ? 20 : simLoss >= 50000 ? 15 : simLoss > 0 ? 8 : 0;
    // Delay factor
    let delayFactor = Math.min(20, Math.round(simDelayHours * 0.8));
    // Category factor
    let catFactor = simCategory === 'Ransomware / Malware' ? 22 : simCategory === 'Online Financial Fraud' ? 18 : 14;
    let risk = Math.min(98, Math.max(15, catFactor + lossFactor + (simPii ? 15 : 0) + (simAccountComp ? 18 : 0) + delayFactor));

    // Recovery Chance (%): drops rapidly after 2 hours (Golden Hour window)
    let recoveryChance = 92;
    if (simDelayHours <= 2) recoveryChance = Math.max(70, 95 - simDelayHours * 10);
    else if (simDelayHours <= 6) recoveryChance = Math.max(45, 75 - (simDelayHours - 2) * 8);
    else if (simDelayHours <= 24) recoveryChance = Math.max(20, 45 - (simDelayHours - 6) * 1.4);
    else recoveryChance = Math.max(5, 20 - (simDelayHours - 24) * 0.3);

    return { risk: Math.round(risk), recovery: Math.round(recoveryChance) };
  };

  const simResult = calculateWhatIf();

  // If Not Authenticated, Show Officer Sign-In Screen
  if (!currentUser) {
    return (
      <div style={{ maxWidth: 840, margin: '20px auto' }}>
        <div className="hero-banner-card" style={{ gridTemplateColumns: '1.1fr 0.9fr' }}>
          <div>
            <span className="badge badge-medium" style={{ marginBottom: 12 }}>Authorized Personnel Only</span>
            <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: '1.9rem', color: 'var(--primary)', marginBottom: 10 }}>
              Law Enforcement &amp; Cyber Cell Console
            </h2>
            <p style={{ fontSize: '0.95rem', color: 'var(--text-body)', marginBottom: 20 }}>
              Access AI-prioritized triage queues, mule-account link graphs, cross-jurisdiction threat correlation, and automated FIR summaries.
            </p>

            <form onSubmit={handlePerformLogin} style={{ background: 'var(--bg-card)', padding: '22px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
              <div className="form-group">
                <label className="form-label">Official Username / Email</label>
                <input
                  type="text"
                  className="form-input"
                  value={loginUsername}
                  onChange={e => setLoginUsername(e.target.value)}
                  placeholder="admin or io_patil"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Password</label>
                <input
                  type="password"
                  className="form-input"
                  value={loginPassword}
                  onChange={e => setLoginPassword(e.target.value)}
                  required
                />
              </div>

              {loginError && (
                <div style={{ color: 'var(--danger)', fontSize: '0.85rem', fontWeight: 600, marginBottom: 14 }}>
                  {loginError}
                </div>
              )}

              <button type="submit" disabled={loginLoading} className="btn-primary" style={{ width: '100%' }}>
                <Lock size={16} />
                <span>{loginLoading ? 'Authenticating...' : 'Sign In to Officer Console'}</span>
              </button>
            </form>

            {/* Quick Demo Credentials Switcher */}
            <div style={{ marginTop: 18 }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>
                Quick Demo Accounts (1-Click Fill):
              </span>
              <div style={{ display: 'flex', gap: 8, marginTop: 8, flexWrap: 'wrap' }}>
                {PRESET_USERS.map((u, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => handleQuickPreset(u)}
                    className="assist-btn"
                    style={{ fontSize: '0.78rem' }}
                  >
                    <User size={13} />
                    <span>{u.name} ({u.role})</span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="hero-image-wrap">
            <img src="/images/auth_soc_hero.jpg" alt="Cyber Cell SOC" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Officer Header Status Card */}
      <div className="app-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span className="badge badge-medium">{currentUser.role || 'Officer'}</span>
            <h3 style={{ margin: 0 }}>{currentUser.full_name || 'Inspector Anand Patil'}</h3>
          </div>
          <p style={{ margin: '3px 0 0 0', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            {currentUser.designation || 'Station House Officer'} | Jurisdiction: {currentUser.state || 'National Command'}
          </p>
        </div>

        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <button onClick={fetchCases} className="control-btn" title="Refresh Triage Queue">
            <RefreshCw size={16} className={loadingCases ? 'spin' : ''} />
            <span>Refresh</span>
          </button>
          <button onClick={onLogout} className="control-btn" style={{ color: 'var(--danger)' }}>
            <span>Sign Out</span>
          </button>
        </div>
      </div>

      {/* WHAT-IF RECOVERY SIMULATOR */}
      <div className="app-card" style={{ background: 'linear-gradient(135deg, #FFFFFF, #FAF7F2)', border: '1.5px solid var(--border-color)' }}>
        <div className="card-header">
          <div>
            <h3 className="card-title">{t.whatIfSimulator}</h3>
            <p className="card-subtitle">
              Simulate how financial loss amounts and reporting lag directly impact recovery probability and risk categorization.
            </p>
          </div>
        </div>

        <div className="grid-2">
          <div>
            <div className="form-group">
              <label className="form-label">Simulated Financial Loss: ₹{Number(simLoss).toLocaleString('en-IN')}</label>
              <input
                type="range"
                min="0"
                max="2500000"
                step="10000"
                value={simLoss}
                onChange={e => setSimLoss(Number(e.target.value))}
                style={{ width: '100%' }}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Reporting Delay: {simDelayHours} Hours</label>
              <input
                type="range"
                min="0"
                max="72"
                step="1"
                value={simDelayHours}
                onChange={e => setSimDelayHours(Number(e.target.value))}
                style={{ width: '100%' }}
              />
              <span className="form-hint">
                {simDelayHours <= 2 ? 'Within Golden Hour Window (Highest Interdiction Odds)' : simDelayHours <= 6 ? 'Intermediary Layering Window Active' : 'Funds likely moved through mule rings and ATM cash-outs'}
              </span>
            </div>

            <div className="form-group">
              <label className="form-label">Attack Typology</label>
              <select
                className="form-select"
                value={simCategory}
                onChange={e => setSimCategory(e.target.value)}
              >
                <option value="Online Financial Fraud">Online Financial Fraud (UPI / NetBanking)</option>
                <option value="Phishing Attack">Phishing Attack (Credential / OTP Harvesting)</option>
                <option value="Ransomware / Malware">Ransomware / Malware Endpoint Encryption</option>
                <option value="Social Engineering">Social Engineering (Digital Arrest)</option>
                <option value="Investment/Crypto Fraud">Investment / Crypto Fraud (Ponzi)</option>
              </select>
            </div>
          </div>

          <div style={{ background: 'var(--bg-card)', padding: '24px', borderRadius: 14, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', gap: 28, marginBottom: 16 }}>
              <div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Predicted Risk Score</span>
                <div style={{ fontSize: '2.5rem', fontWeight: 800, color: simResult.risk >= 75 ? 'var(--danger)' : simResult.risk >= 50 ? 'var(--warning)' : 'var(--primary)' }}>
                  {simResult.risk} / 100
                </div>
              </div>

              <div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Fund Recovery Chance</span>
                <div style={{ fontSize: '2.5rem', fontWeight: 800, color: simResult.recovery >= 70 ? 'var(--primary)' : simResult.recovery >= 40 ? 'var(--warning)' : 'var(--danger)' }}>
                  {simResult.recovery}%
                </div>
              </div>
            </div>

            <div style={{ fontSize: '0.88rem', color: 'var(--text-muted)', maxWidth: 420 }}>
              {simDelayHours <= 2
                ? 'Rapid action: Requisition 1930 Helpline and Section 94 BNSS notices immediately to freeze beneficiary gateway balances.'
                : 'Reporting delay exceeds Golden Hour. Mandate transaction flow mapping across secondary and tertiary mule accounts.'}
            </div>
          </div>
        </div>
      </div>

      {/* TRIAGE QUEUE & MULTI-FILTER BAR */}
      <div className="app-card">
        <div className="card-header">
          <div>
            <h3 className="card-title">{t.triageQueueTitle}</h3>
            <p className="card-subtitle">{t.triageQueueSub}</p>
          </div>
          <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 600 }}>
            Showing {cases.length} of {totalCases.toLocaleString('en-IN')} Complaints
          </span>
        </div>

        {/* Filter Controls */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12, marginBottom: 20 }}>
          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label" style={{ fontSize: '0.8rem' }}>Search Complaints</label>
            <input
              type="text"
              className="form-input"
              placeholder="Search ID, victim, keyword..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') fetchCases(); }}
            />
          </div>

          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label" style={{ fontSize: '0.8rem' }}>{t.filterRisk}</label>
            <select
              className="form-select"
              value={filterRisk}
              onChange={e => { setFilterRisk(e.target.value); setPage(1); }}
            >
              <option value="All">All Risk Levels</option>
              <option value="CRITICAL">Critical Risk (Score &gt;= 75)</option>
              <option value="HIGH">High Risk (Score 50-74)</option>
              <option value="MEDIUM">Medium Risk (Score 25-49)</option>
              <option value="LOW">Low Risk (&lt; 25)</option>
            </select>
          </div>

          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label" style={{ fontSize: '0.8rem' }}>{t.filterCategory}</label>
            <select
              className="form-select"
              value={filterCategory}
              onChange={e => { setFilterCategory(e.target.value); setPage(1); }}
            >
              <option value="All">All Categories</option>
              <option value="Online Financial Fraud">Online Financial Fraud</option>
              <option value="Phishing Attack">Phishing Attack</option>
              <option value="Account Takeover">Account Takeover</option>
              <option value="Ransomware / Malware">Ransomware / Malware</option>
              <option value="Social Engineering">Social Engineering</option>
              <option value="Investment/Crypto Fraud">Investment / Crypto Fraud</option>
              <option value="Identity Theft">Identity Theft</option>
            </select>
          </div>

          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label" style={{ fontSize: '0.8rem' }}>{t.filterState}</label>
            <select
              className="form-select"
              value={filterState}
              onChange={e => { setFilterState(e.target.value); setPage(1); }}
            >
              <option value="All">All States (20)</option>
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
            </select>
          </div>
        </div>

        {/* Complaints Data Table */}
        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Case ID</th>
                <th>Category</th>
                <th>State &amp; City</th>
                <th>Financial Loss</th>
                <th>AI Risk Score</th>
                <th>SLA Mandate</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {loadingCases ? (
                <tr>
                  <td colSpan={8} style={{ textAlign: 'center', padding: '36px' }}>
                    <RefreshCw size={24} className="spin" style={{ margin: '0 auto 8px' }} />
                    <p style={{ margin: 0, color: 'var(--text-muted)' }}>Querying intelligence database...</p>
                  </td>
                </tr>
              ) : cases.length === 0 ? (
                <tr>
                  <td colSpan={8} style={{ textAlign: 'center', padding: '36px', color: 'var(--text-muted)' }}>
                    No complaints match current filter parameters.
                  </td>
                </tr>
              ) : (
                cases.map(c => {
                  const score = c.risk_score || 0;
                  const isCrit = score >= 75;
                  const isHigh = score >= 50 && score < 75;

                  return (
                    <tr key={c.id || c.complaint_id}>
                      <td style={{ fontWeight: 700, whiteSpace: 'nowrap' }}>
                        {c.complaint_id}
                      </td>
                      <td>
                        <span style={{ fontWeight: 600 }}>{c.predicted_category || c.crime_type}</span>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{c.platform || 'Online'}</div>
                      </td>
                      <td>
                        <span>{c.city || 'Urban'}</span>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{c.state}</div>
                      </td>
                      <td style={{ fontWeight: 700, color: c.financial_loss >= 100000 ? 'var(--danger)' : 'var(--text-main)' }}>
                        ₹{Number(c.financial_loss || 0).toLocaleString('en-IN')}
                      </td>
                      <td>
                        <span className={`badge ${isCrit ? 'badge-critical' : isHigh ? 'badge-high' : 'badge-medium'}`}>
                          {c.risk_level || (isCrit ? 'CRITICAL' : 'HIGH')} ({score}/100)
                        </span>
                      </td>
                      <td>
                        <span style={{ fontSize: '0.8rem', fontWeight: 600, color: isCrit ? 'var(--danger)' : isHigh ? '#B5651D' : 'var(--text-muted)' }}>
                          {isCrit ? t.slaCritical : isHigh ? t.slaHigh : t.slaStandard}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>
                          {c.current_status || 'New'}
                        </span>
                      </td>
                      <td>
                        <button
                          onClick={() => setSelectedCase(c)}
                          className="control-btn"
                          style={{ padding: '6px 12px', fontSize: '0.82rem' }}
                        >
                          <span>{t.viewCaseDetail}</span>
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 18, flexWrap: 'wrap', gap: 10 }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Page {page} of {Math.ceil(totalCases / 15) || 1}
          </span>
          <div style={{ display: 'flex', gap: 8 }}>
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="control-btn"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={page >= Math.ceil(totalCases / 15)}
              className="control-btn"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      {/* CASE DETAIL DOSSIER MODAL */}
      {selectedCase && (
        <div className="modal-overlay" onClick={() => setSelectedCase(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--border-color)', paddingBottom: 16, marginBottom: 20 }}>
              <div>
                <span className={`badge ${selectedCase.risk_score >= 75 ? 'badge-critical' : 'badge-high'}`} style={{ marginBottom: 6 }}>
                  {selectedCase.risk_level} RISK ({selectedCase.risk_score}/100)
                </span>
                <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: '1.6rem', margin: 0 }}>
                  Case Dossier #{selectedCase.complaint_id}
                </h2>
                <p style={{ margin: '4px 0 0 0', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                  {selectedCase.cyber_cell_station || `Cyber Crime Police Station, ${selectedCase.city}`}
                </p>
              </div>
              <button onClick={() => setSelectedCase(null)} className="control-btn" style={{ padding: '6px 10px' }}>
                ✕
              </button>
            </div>

            {/* Quick Actions Row */}
            <div style={{ display: 'flex', gap: 12, marginBottom: 20, flexWrap: 'wrap' }}>
              <button
                onClick={() => onOpenCaseInCopilot && onOpenCaseInCopilot(selectedCase)}
                className="btn-primary"
                style={{ fontSize: '0.9rem', padding: '8px 16px' }}
              >
                <MessageSquare size={16} />
                <span>{t.askAboutCase}</span>
              </button>
              <button
                onClick={() => handleDownloadFirPdf(selectedCase)}
                className="btn-secondary"
                style={{ fontSize: '0.9rem', padding: '8px 16px' }}
              >
                <Download size={16} />
                <span>{t.downloadFirDraft}</span>
              </button>
            </div>

            {/* Key Dossier Grid */}
            <div className="grid-2" style={{ marginBottom: 20 }}>
              <div style={{ background: 'var(--bg-app)', padding: 16, borderRadius: 12, border: '1px solid var(--border-color)' }}>
                <h4 style={{ margin: '0 0 10px 0', fontSize: '1rem', color: 'var(--primary)' }}>Incident Parameters</h4>
                <div style={{ fontSize: '0.88rem', display: 'flex', flexDirection: 'column', gap: 6 }}>
                  <div><strong>Category:</strong> {selectedCase.predicted_category || selectedCase.crime_type}</div>
                  <div><strong>Financial Loss:</strong> ₹{Number(selectedCase.financial_loss || 0).toLocaleString('en-IN')}</div>
                  <div><strong>Incident Date:</strong> {selectedCase.incident_date || 'N/A'}</div>
                  <div><strong>Registration Date:</strong> {selectedCase.complaint_date || 'N/A'}</div>
                  <div><strong>Channel / Platform:</strong> {selectedCase.platform || 'Online'}</div>
                </div>
              </div>

              <div style={{ background: 'var(--bg-app)', padding: 16, borderRadius: 12, border: '1px solid var(--border-color)' }}>
                <h4 style={{ margin: '0 0 10px 0', fontSize: '1rem', color: 'var(--primary)' }}>Operational Status Workflow</h4>
                <div style={{ marginBottom: 10, fontSize: '0.88rem' }}>
                  <strong>Current Status:</strong> <span style={{ fontWeight: 700, color: 'var(--primary)' }}>{selectedCase.current_status}</span>
                </div>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {['Under Review', 'Investigating', 'Resolved', 'Closed'].map(st => (
                    <button
                      key={st}
                      disabled={updatingStatus || selectedCase.current_status === st}
                      onClick={() => handleUpdateStatus(st)}
                      className="control-btn"
                      style={{
                        padding: '6px 10px',
                        fontSize: '0.78rem',
                        background: selectedCase.current_status === st ? 'var(--primary)' : 'var(--bg-card)',
                        color: selectedCase.current_status === st ? '#FFFFFF' : 'var(--text-main)'
                      }}
                    >
                      {st}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Extracted Indicators Table */}
            <div style={{ marginBottom: 20 }}>
              <h4 style={{ margin: '0 0 10px 0', fontSize: '1rem' }}>Extracted Threat Indicators (IOCs)</h4>
              <div style={{ background: 'var(--bg-sand)', padding: 14, borderRadius: 10, fontSize: '0.88rem' }}>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  {typeof selectedCase.threat_indicators === 'string' ? (
                    JSON.parse(selectedCase.threat_indicators || '[]').map((ind, i) => (
                      <span
                        key={i}
                        onClick={() => handleCopy(ind.value || ind.label || ind.indicator_value)}
                        style={{ background: '#FFFFFF', padding: '4px 10px', borderRadius: 6, border: '1px solid var(--border-color)', display: 'inline-flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}
                        title="Click to copy"
                      >
                        <strong>{ind.type || ind.indicator_type || 'IOC'}:</strong> {ind.value || ind.label || ind.indicator_value}
                        {copiedText === (ind.value || ind.label || ind.indicator_value) ? <Check size={12} color="green" /> : <Copy size={12} />}
                      </span>
                    ))
                  ) : (
                    <span>No structured indicators recorded.</span>
                  )}
                </div>
              </div>
            </div>

            {/* Complainant Statement */}
            <div style={{ marginBottom: 20 }}>
              <h4 style={{ margin: '0 0 8px 0', fontSize: '1rem' }}>Complainant Statement on Record</h4>
              <div style={{ background: 'var(--bg-app)', padding: 16, borderRadius: 10, fontSize: '0.9rem', lineHeight: 1.6, border: '1px solid var(--border-color)' }}>
                "{selectedCase.description}"
              </div>
            </div>

            {/* Explainable AI Attribution */}
            {selectedCase.reasons && (
              <div>
                <h4 style={{ margin: '0 0 8px 0', fontSize: '1rem' }}>AI Decision Attribution &amp; Risk Drivers</h4>
                <ul style={{ paddingLeft: 20, fontSize: '0.88rem', color: 'var(--text-muted)' }}>
                  {typeof selectedCase.reasons === 'string' ? (
                    JSON.parse(selectedCase.reasons || '[]').map((r, i) => (
                      <li key={i}>{r}</li>
                    ))
                  ) : (
                    <li>Automated scoring based on financial loss, account compromise and timing factors.</li>
                  )}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
