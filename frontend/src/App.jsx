import React, { useState, useEffect } from 'react';
import {
  Shield, UserCheck, Moon, Sun, Globe, AlertTriangle,
  PhoneCall, FileText, Search, Activity, Cpu, Database,
  Share2, BarChart3, MessageSquare, Award, ArrowLeftRight,
  Download, LogIn, LogOut, CheckCircle2, ShieldAlert, Swords, GitFork, Sparkles, Command
} from 'lucide-react';
import './App.css';
import { translations } from './i18n';

// Subcomponents
import CitizenPortal from './components/CitizenPortal';
import OfficerConsole from './components/OfficerConsole';
import LinkAnalysisGraph from './components/LinkAnalysisGraph';
import PowerBiStudio from './components/PowerBiStudio';
import CyberCopilot from './components/CyberCopilot';
import ModelBenchmarks from './components/ModelBenchmarks';
import AdminAudit from './components/AdminAudit';
import ScamDojo from './modules/dojo/ScamDojo';
import MoneyTrail from './modules/moneytrail/MoneyTrail';
import EmergingThreatDetector from './modules/threats/EmergingThreatDetector';
import GlobalCommandPalette from './components/GlobalCommandPalette';
import { MODULE_FLAGS } from './config/featureFlags';





// Read API base URL from env if available
const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

export default function App() {
  // Multilingual State (Default: English)
  const [lang, setLang] = useState(() => {
    return localStorage.getItem('cybershield_lang') || 'en';
  });

  const t = translations[lang] || translations.en;

  const handleLanguageChange = (newLang) => {
    setLang(newLang);
    localStorage.setItem('cybershield_lang', newLang);
  };

  // Theme State (Default: Natural Light)
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('cybershield_theme') || 'light';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('cybershield_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  // Authentication State
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const saved = localStorage.getItem('cybershield_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const handleLogin = (user, token) => {
    setCurrentUser(user);
    localStorage.setItem('cybershield_user', JSON.stringify(user));
    if (token) localStorage.setItem('cybershield_token', token);
  };

  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('cybershield_user');
    localStorage.removeItem('cybershield_token');
    setActiveTab('citizen');
  };

  // Active Tab State: 'citizen', 'triage', 'linkgraph', 'bistudio', 'copilot', 'model', 'admin'
  const [activeTab, setActiveTab] = useState('citizen');

  // Command Palette (Ctrl+K) State
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setCommandPaletteOpen(prev => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Case Context for Copilot
  const [activeCaseContext, setActiveCaseContext] = useState(null);

  const handleOpenCaseInCopilot = (caseObj) => {
    setActiveCaseContext(caseObj);
    setActiveTab('copilot');
  };

  // Backend Health Status State ('online', 'offline', 'checking')
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    const checkServerHealth = async () => {
      try {
        const res = await fetch(`${API_BASE}/health`);
        if (res.ok) {
          setBackendStatus('online');
        } else {
          setBackendStatus('offline');
        }
      } catch {
        setBackendStatus('offline');
      }
    };
    checkServerHealth();
    const interval = setInterval(checkServerHealth, 20000);
    return () => clearInterval(interval);
  }, []);

  // Threat Advisories Ticker State
  const [tickerAdvisories, setTickerAdvisories] = useState([
    "ACTIVE ALERT: UPI QR Code Reversal Fraud reported across metro commercial districts. Helpline 1930 active.",
    "CERT-In ADVISORY: Fake SMS headers mimicking State Bank of India PAN update portals.",
    "NATIONAL WARNING: Fraudsters impersonating customs/CBI placing victims under 'Digital Arrest' via Skype."
  ]);

  useEffect(() => {
    const fetchAdvisories = async () => {
      try {
        const res = await fetch(`${API_BASE}/intelligence/early-warning`);
        const json = await res.json();
        if (res.ok && json.data && json.data.length > 0) {
          setTickerAdvisories(json.data.map(a => `${a.status}: ${a.threat_title} (${a.region}) — ${a.recommendation}`));
        }
      } catch {
        // Fallback to initial advisories
      }
    };
    fetchAdvisories();
  }, []);

  // PWA Install Prompt State
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [canInstall, setCanInstall] = useState(false);

  useEffect(() => {
    const handleBeforeInstallPrompt = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setCanInstall(true);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    return () => window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
  }, []);

  const handleInstallPWA = async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === 'accepted') {
      setCanInstall(false);
    }
    setDeferredPrompt(null);
  };

  return (
    <div className="app-shell">
      {/* Official Government Top Bar */}
      <div className="gov-topbar">
        <div className="gov-emblem-text">
          <span>GOVERNMENT OF INDIA</span>
          <span style={{ opacity: 0.6 }}>|</span>
          <span>INDIAN CYBER CRIME COORDINATION CENTRE (I4C)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span className="gov-emblem-badge">{t.helplineTitle}</span>
          <a href="tel:1930" style={{ color: '#FFFFFF', fontWeight: 800, textDecoration: 'none' }}>
            {t.emergencyHelpline}
          </a>
        </div>
      </div>

      {/* Main Header */}
      <header className="app-header">
        <div className="brand-section" onClick={() => setActiveTab('citizen')}>
          <div className="brand-shield-icon">
            <Shield size={26} />
          </div>
          <div className="brand-titles">
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span className="brand-name">{t.appName}</span>
              <span
                data-testid="backend-status-dot"
                title={backendStatus === 'online' ? 'System API Online (5,000 Complaints Connected)' : 'Backend Server Reconnecting / Waking Up'}
                style={{
                  width: 10,
                  height: 10,
                  borderRadius: '50%',
                  background: backendStatus === 'online' ? '#2ECC71' : backendStatus === 'checking' ? '#F39C12' : '#E74C3C',
                  display: 'inline-block',
                  boxShadow: backendStatus === 'online' ? '0 0 6px #2ECC71' : '0 0 6px #E74C3C'
                }}
              />
            </div>
            <span className="brand-tagline">{t.tagline}</span>
          </div>
        </div>

        <div className="header-controls">
          {/* Quick Command Palette Button (Ctrl+K) */}
          <button
            onClick={() => setCommandPaletteOpen(true)}
            className="control-btn"
            title="Global Command Palette (Ctrl+K)"
            style={{ fontWeight: 700, gap: 6 }}
          >
            <Command size={16} />
            <span style={{ fontSize: '0.85rem' }}>Ctrl+K</span>
          </button>

          {/* Mode Switcher */}
          <button
            onClick={() => {
              if (activeTab === 'citizen') {
                setActiveTab(currentUser ? 'triage' : 'triage');
              } else {
                setActiveTab('citizen');
              }
            }}
            className="control-btn"
            style={{ fontWeight: 700, borderColor: 'var(--primary)' }}
          >
            <ArrowLeftRight size={16} />
            <span>{activeTab === 'citizen' ? t.portalOfficer : t.portalCitizen}</span>
          </button>

          {/* Language Switcher */}
          <div style={{ position: 'relative' }}>
            <select
              value={lang}
              onChange={e => handleLanguageChange(e.target.value)}
              className="control-btn"
              style={{ minHeight: 44, padding: '6px 12px', cursor: 'pointer' }}
              aria-label="Language Selector"
            >
              <option value="en">English</option>
              <option value="hi">हिंदी (Hindi)</option>
              <option value="kn">ಕನ್ನಡ (Kannada)</option>
            </select>
          </div>

          {/* Theme Toggle (Light / Dark) */}
          <button
            onClick={toggleTheme}
            className="control-btn"
            title={theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Natural Light Mode'}
            aria-label="Toggle Theme"
          >
            {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
          </button>

          {/* PWA Install Button */}
          {canInstall && (
            <button onClick={handleInstallPWA} className="control-btn-primary control-btn" title="Install PWA on device">
              <Download size={16} />
              <span>Install App</span>
            </button>
          )}

          {/* Auth Button */}
          {currentUser ? (
            <button onClick={handleLogout} className="control-btn" title="Sign Out">
              <LogOut size={16} />
              <span>{t.logout}</span>
            </button>
          ) : (
            <button onClick={() => setActiveTab('triage')} className="control-btn">
              <LogIn size={16} />
              <span>{t.loginOfficer}</span>
            </button>
          )}
        </div>
      </header>

      {/* Backend Waking Up Warning Strip */}
      {backendStatus === 'offline' && (
        <div style={{
          background: '#FFF3CD',
          color: '#856404',
          textAlign: 'center',
          padding: '8px 16px',
          fontSize: '0.85rem',
          fontWeight: 600,
          borderBottom: '1px solid #FFEBAA',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 8
        }}>
          <span>⚠️ Backend waking up (free-tier servers sleep after inactivity)... Reconnecting in background.</span>
        </div>
      )}

      {/* Synthetic Demonstration Data Banner */}
      <div className="demo-banner-strip">
        <div className="demo-banner-content">
          <span className="demo-chip">{t.syntheticBadge}</span>
          <span>{t.provenanceCite} — All records presented are synthetic and modeled for investigative analytics.</span>
        </div>
        <div style={{ fontSize: '0.75rem', opacity: 0.85 }}>
          Standard: Section 94 BNSS &amp; Section 63 BSA 2023 Digital Protocols
        </div>
      </div>

      {/* Live Threat Advisory Ticker */}
      <div className="threat-ticker">
        <span className="ticker-label">
          <ShieldAlert size={14} />
          <span>LIVE THREAT TICKER</span>
        </span>
        <div className="ticker-text">
          {tickerAdvisories.join("  •  ")}
        </div>
      </div>

      {/* Main Container */}
      <div className="app-container">
        {/* Desktop Sidebar Navigation */}
        <aside className="desktop-sidebar">
          <div>
            <div className="nav-group-title">CITIZEN SERVICES</div>
            <ul className="sidebar-nav-list">
              <li>
                <button
                  onClick={() => setActiveTab('citizen')}
                  className={`sidebar-nav-btn ${activeTab === 'citizen' ? 'active' : ''}`}
                >
                  <FileText size={18} />
                  <span>{t.navHome}</span>
                </button>
              </li>
              {MODULE_FLAGS.SCAM_DOJO && (
                <li>
                  <button
                    onClick={() => setActiveTab('dojo')}
                    className={`sidebar-nav-btn ${activeTab === 'dojo' ? 'active' : ''}`}
                  >
                    <Swords size={18} />
                    <span>Scam Dojo (AI Simulator)</span>
                  </button>
                </li>
              )}
            </ul>


            <div className="nav-group-title" style={{ marginTop: 20 }}>LAW ENFORCEMENT &amp; AI</div>
            <ul className="sidebar-nav-list">
              <li>
                <button
                  onClick={() => setActiveTab('triage')}
                  className={`sidebar-nav-btn ${activeTab === 'triage' ? 'active' : ''}`}
                >
                  <Activity size={18} />
                  <span>{t.navTriage}</span>
                </button>
              </li>
              <li>
                <button
                  onClick={() => setActiveTab('linkgraph')}
                  className={`sidebar-nav-btn ${activeTab === 'linkgraph' ? 'active' : ''}`}
                >
                  <Share2 size={18} />
                  <span>{t.navLinkGraph}</span>
                </button>
              </li>
              {MODULE_FLAGS.MONEY_TRAIL && (
                <li>
                  <button
                    onClick={() => setActiveTab('moneytrail')}
                    className={`sidebar-nav-btn ${activeTab === 'moneytrail' ? 'active' : ''}`}
                  >
                    <GitFork size={18} />
                    <span>Money Trail (Rapid Freeze)</span>
                  </button>
                </li>
              )}
              {MODULE_FLAGS.EMERGING_THREATS && (
                <li>
                  <button
                    onClick={() => setActiveTab('threats')}
                    className={`sidebar-nav-btn ${activeTab === 'threats' ? 'active' : ''}`}
                  >
                    <Sparkles size={18} />
                    <span>Emerging Threat Detector</span>
                  </button>
                </li>
              )}
              <li>


                <button
                  onClick={() => setActiveTab('bistudio')}
                  className={`sidebar-nav-btn ${activeTab === 'bistudio' ? 'active' : ''}`}
                >
                  <BarChart3 size={18} />
                  <span>{t.navBiStudio}</span>
                </button>
              </li>
              <li>
                <button
                  onClick={() => setActiveTab('copilot')}
                  className={`sidebar-nav-btn ${activeTab === 'copilot' ? 'active' : ''}`}
                >
                  <MessageSquare size={18} />
                  <span>{t.navCopilot}</span>
                </button>
              </li>
              <li>
                <button
                  onClick={() => setActiveTab('model')}
                  className={`sidebar-nav-btn ${activeTab === 'model' ? 'active' : ''}`}
                >
                  <Cpu size={18} />
                  <span>{t.navModel}</span>
                </button>
              </li>
              <li>
                <button
                  onClick={() => setActiveTab('admin')}
                  className={`sidebar-nav-btn ${activeTab === 'admin' ? 'active' : ''}`}
                >
                  <Database size={18} />
                  <span>{t.navAdmin}</span>
                </button>
              </li>
            </ul>
          </div>

          <div className="sidebar-footer-card">
            <strong>24x7 Citizen Helpline:</strong>
            <p style={{ margin: '4px 0 0 0' }}>Dial 1930 for immediate transaction interdiction.</p>
          </div>
        </aside>

        {/* Primary Workspace View */}
        <main className="main-workspace">
          {activeTab === 'citizen' && (
            <CitizenPortal
              t={t}
              lang={lang}
              apiBase={API_BASE}
              onSwitchToOfficer={() => setActiveTab('triage')}
            />
          )}

          {activeTab === 'dojo' && MODULE_FLAGS.SCAM_DOJO && (
            <ScamDojo
              apiBase={API_BASE}
              lang={lang}
            />
          )}


          {activeTab === 'triage' && (
            <OfficerConsole
              t={t}
              lang={lang}
              currentUser={currentUser}
              onLogin={handleLogin}
              onLogout={handleLogout}
              onOpenCaseInCopilot={handleOpenCaseInCopilot}
              apiBase={API_BASE}
            />
          )}

          {activeTab === 'linkgraph' && (
            <LinkAnalysisGraph
              t={t}
              apiBase={API_BASE}
              onSelectCase={handleOpenCaseInCopilot}
            />
          )}

          {activeTab === 'moneytrail' && MODULE_FLAGS.MONEY_TRAIL && (
            <MoneyTrail
              apiBase={API_BASE}
              lang={lang}
              activeCaseId={activeCaseContext?.complaint_id || 'CR-2026-98214'}
            />
          )}

          {activeTab === 'threats' && MODULE_FLAGS.EMERGING_THREATS && (
            <EmergingThreatDetector
              apiBase={API_BASE}
              lang={lang}
            />
          )}



          {activeTab === 'bistudio' && (
            <PowerBiStudio
              t={t}
              apiBase={API_BASE}
            />
          )}

          {activeTab === 'copilot' && (
            <CyberCopilot
              t={t}
              apiBase={API_BASE}
              activeCaseContext={activeCaseContext}
              onClearCaseContext={() => setActiveCaseContext(null)}
            />
          )}

          {activeTab === 'model' && (
            <ModelBenchmarks
              t={t}
              apiBase={API_BASE}
            />
          )}

          {activeTab === 'admin' && (
            <AdminAudit
              t={t}
              apiBase={API_BASE}
            />
          )}
        </main>
      </div>

      {/* Mobile-First Bottom Navigation Bar */}
      <nav className="mobile-bottom-nav">
        <button
          onClick={() => setActiveTab('citizen')}
          className={`mobile-nav-item ${activeTab === 'citizen' ? 'active' : ''}`}
        >
          <FileText size={20} />
          <span>Citizen</span>
        </button>
        <button
          onClick={() => setActiveTab('triage')}
          className={`mobile-nav-item ${activeTab === 'triage' ? 'active' : ''}`}
        >
          <Activity size={20} />
          <span>Triage</span>
        </button>
        <button
          onClick={() => setActiveTab('linkgraph')}
          className={`mobile-nav-item ${activeTab === 'linkgraph' ? 'active' : ''}`}
        >
          <Share2 size={20} />
          <span>Links</span>
        </button>
        <button
          onClick={() => setActiveTab('bistudio')}
          className={`mobile-nav-item ${activeTab === 'bistudio' ? 'active' : ''}`}
        >
          <BarChart3 size={20} />
          <span>Studio</span>
        </button>
        <button
          onClick={() => setActiveTab('copilot')}
          className={`mobile-nav-item ${activeTab === 'copilot' ? 'active' : ''}`}
        >
          <MessageSquare size={20} />
          <span>Copilot</span>
        </button>
      </nav>
      {/* Global Command Palette */}
      <GlobalCommandPalette
        isOpen={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
        onNavigateTab={(tab) => setActiveTab(tab)}
        apiBase={API_BASE}
      />
    </div>
  );
}
