import { createContext, useContext, useEffect, useState } from 'react';
import { BrowserRouter, Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import { ArrowRight, Eye, EyeOff, Heart, Shield } from 'lucide-react';
import CyberShield from './CyberShield.jsx';
import './Cynexa.css';

const AuthContext = createContext(null);

async function request(path, body) {
  const response = await fetch(path, {
    method: body ? 'POST' : 'GET',
    credentials: 'include',
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.message || 'Request could not be completed.');
  return data;
}

export default function Cynexa() {
  return <BrowserRouter><AuthRoot /></BrowserRouter>;
}

function AuthRoot() {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    let active = true;
    request('/api/auth/me')
      .then((r) => { if (active && r.authenticated) setUser(r.user); })
      .catch(() => { if (active) setUser(null); })
      .finally(() => { if (active) setChecking(false); });
    return () => { active = false; };
  }, []);

  const login = (u) => {
    setUser(u);
    navigate(u.role === 'ADMIN' ? '/admin' : '/dashboard', { replace: true });
  };

  const logout = async () => {
    try { await request('/api/auth/logout', {}); } catch { /* ignore */ }
    setUser(null);
    navigate('/login', { replace: true });
  };

  if (checking) {
    return (
      <div className="splash-load">
        <div className="splash-spinner" />
        <span>Loading CyberNexa...</span>
      </div>
    );
  }

  const dest = user ? (user.role === 'ADMIN' ? '/admin' : '/dashboard') : null;

  return (
    <AuthContext.Provider value={{ user, login, logout, setUser }}>
      <Routes>
        <Route path="/" element={user ? <Navigate to={dest} replace /> : <Landing />} />
        <Route path="/login" element={user ? <Navigate to={dest} replace /> : <Login />} />
        <Route path="/signup" element={user ? <Navigate to={dest} replace /> : <Signup />} />
        <Route path="/safety-login" element={user ? <Navigate to={dest} replace /> : <SafetyLogin />} />
        <Route path="*" element={user ? <CyberShield user={user} onLogout={logout} onUserUpdate={setUser} /> : <Navigate to="/login" replace />} />
      </Routes>
    </AuthContext.Provider>
  );
}

/* ── Landing ──────────────────────────────────────────────────────── */

function Landing() {
  const navigate = useNavigate();
  return (
    <div className="landing-root">
      {/* full-screen cybercrime background */}
      <div className="landing-bg" />
      <div className="landing-overlay" />

      <nav className="landing-nav">
        <div className="landing-logo">
          <Shield size={20} />
          <span>CyberNexa</span>
        </div>
        <div className="landing-nav-right">
          <button className="ln-btn-ghost" onClick={() => navigate('/login')}>Sign In</button>
          <button className="ln-btn-primary" onClick={() => navigate('/signup')}>Get Started</button>
        </div>
      </nav>

      <main className="landing-main">
        {/* Left portal — Cyber Intelligence */}
        <div className="portal portal-cyber" onClick={() => navigate('/login')}>
          <div className="portal-icon"><Shield size={36} /></div>
          <h2>Cybercrime Intelligence</h2>
          <ul>
            <li>AI-powered complaint prediction</li>
            <li>RAG knowledge retrieval</li>
            <li>Incident reports &amp; history</li>
            <li>Cyber threat intelligence</li>
            <li>AI Chatbot assistant</li>
          </ul>
          <button className="portal-btn" onClick={() => navigate('/login')}>
            Enter <ArrowRight size={16} />
          </button>
        </div>

        {/* Right portal — Women Safety */}
        <div className="portal portal-safety" onClick={() => navigate('/safety-login')}>
          <div className="portal-icon portal-icon-safety"><Heart size={36} /></div>
          <h2>Women Safety</h2>
          <ul>
            <li>Emergency alert &amp; contacts</li>
            <li>Live location sharing</li>
            <li>Voice evidence recording</li>
            <li>Trip safety monitoring</li>
            <li>Safety AI chatbot</li>
          </ul>
          <button className="portal-btn portal-btn-safety" onClick={(e) => { e.stopPropagation(); navigate('/safety-login'); }}>
            Enter <ArrowRight size={16} />
          </button>
        </div>
      </main>

      <footer className="landing-footer">
        <span>CyberNexa · Demo Platform · Emergency services: 112 / 1091</span>
      </footer>
    </div>
  );
}

/* ── Cyber Intelligence Login ─────────────────────────────────────── */

function Login() {
  const { login } = useContext(AuthContext);
  const location = useLocation();
  const navigate = useNavigate();
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(false);
  const [showPw, setShowPw] = useState(false);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState(location.state?.registered ? 'Account created. Sign in.' : '');
  const [isError, setIsError] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setMsg(''); setIsError(false); setBusy(true);
    try {
      const r = await request('/api/auth/login', { identifier, password, remember });
      login(r.user);
    } catch (err) {
      setMsg(err.message); setIsError(true);
    } finally { setBusy(false); }
  };

  return (
    <div className="auth-root cyber-auth">
      <div className="auth-bg-cyber" />
      <div className="auth-overlay" />
      <div className="auth-box">
        <div className="auth-brand">
          <Shield size={22} />
          <span>CyberNexa</span>
        </div>
        <h1 className="auth-title">Cybercrime Intelligence</h1>
        <p className="auth-sub">Sign in to your workspace</p>

        <form className="auth-form" onSubmit={submit}>
          <label>
            Email or username
            <input autoComplete="username" required value={identifier}
              onChange={(e) => setIdentifier(e.target.value)} placeholder="you@example.com" />
          </label>
          <label>
            Password
            <div className="pw-wrap">
              <input autoComplete="current-password" required
                type={showPw ? 'text' : 'password'} value={password}
                onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
              <button type="button" onClick={() => setShowPw(!showPw)}>
                {showPw ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
          </label>
          <div className="auth-row">
            <label className="check-label">
              <input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} />
              Remember me
            </label>
          </div>
          {msg && <div className={`auth-msg ${isError ? 'error' : 'success'}`}>{msg}</div>}
          <button className="auth-submit" disabled={busy}>
            {busy ? 'Signing in...' : 'Sign In'} <ArrowRight size={15} />
          </button>
        </form>

        <div className="auth-links">
          <button onClick={() => navigate('/signup')}>Create account</button>
          <span>·</span>
          <button onClick={() => navigate('/')}>Home</button>
          <span>·</span>
          <button onClick={() => navigate('/safety-login')}>Women Safety Login</button>
        </div>
      </div>
    </div>
  );
}

/* ── Women Safety Login ───────────────────────────────────────────── */

function SafetyLogin() {
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState('');
  const [isError, setIsError] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setMsg(''); setIsError(false); setBusy(true);
    try {
      const r = await request('/api/auth/login', { identifier, password });
      login(r.user);
    } catch (err) {
      setMsg(err.message); setIsError(true);
    } finally { setBusy(false); }
  };

  return (
    <div className="auth-root safety-auth">
      <div className="auth-bg-safety" />
      <div className="auth-overlay safety-overlay" />
      <div className="auth-box safety-box">
        <div className="auth-brand safety-brand">
          <Heart size={22} />
          <span>Women Safety</span>
        </div>
        <h1 className="auth-title safety-title">Stay Safe. Stay Connected.</h1>
        <p className="auth-sub">Sign in to access emergency tools</p>

        <div className="safety-notice">
          <span>🆘</span>
          <span>Emergency? Call <strong>112</strong> or Women Helpline <strong>1091</strong></span>
        </div>

        <form className="auth-form" onSubmit={submit}>
          <label>
            Email or username
            <input autoComplete="username" required value={identifier}
              onChange={(e) => setIdentifier(e.target.value)} placeholder="you@example.com" />
          </label>
          <label>
            Password
            <div className="pw-wrap">
              <input autoComplete="current-password" required
                type={showPw ? 'text' : 'password'} value={password}
                onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
              <button type="button" onClick={() => setShowPw(!showPw)}>
                {showPw ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
          </label>
          {msg && <div className={`auth-msg ${isError ? 'error' : 'success'}`}>{msg}</div>}
          <button className="auth-submit safety-submit" disabled={busy}>
            {busy ? 'Signing in...' : 'Enter Safety Portal'} <Heart size={15} />
          </button>
        </form>

        <div className="auth-links safety-links">
          <button onClick={() => navigate('/signup')}>Create account</button>
          <span>·</span>
          <button onClick={() => navigate('/login')}>Cyber Intelligence Login</button>
          <span>·</span>
          <button onClick={() => navigate('/')}>Home</button>
        </div>
      </div>
    </div>
  );
}

/* ── Signup ───────────────────────────────────────────────────────── */

function Signup() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ full_name: '', username: '', email: '', password: '', confirmPassword: '' });
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    if (form.password !== form.confirmPassword) return setError('Passwords do not match.');
    if (!/[a-z]/.test(form.password) || !/[A-Z]/.test(form.password) || !/\d/.test(form.password) || form.password.length < 12)
      return setError('Use 12+ characters with uppercase, lowercase, and a number.');
    setBusy(true);
    try {
      await request('/api/auth/signup', { full_name: form.full_name, username: form.username, email: form.email, password: form.password });
      navigate('/login', { replace: true, state: { registered: true } });
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  };

  return (
    <div className="auth-root cyber-auth">
      <div className="auth-bg-cyber" />
      <div className="auth-overlay" />
      <div className="auth-box auth-box-wide">
        <div className="auth-brand">
          <Shield size={22} />
          <span>CyberNexa</span>
        </div>
        <h1 className="auth-title">Create Account</h1>
        <p className="auth-sub">Join CyberNexa</p>

        <form className="auth-form signup-form" onSubmit={submit}>
          <div className="form-row-2">
            <label>
              Full name
              <input autoComplete="name" required maxLength={100} value={form.full_name}
                onChange={(e) => set('full_name', e.target.value)} placeholder="Your name" />
            </label>
            <label>
              Username
              <input autoComplete="username" required minLength={3} maxLength={24}
                value={form.username} onChange={(e) => set('username', e.target.value)} placeholder="username" />
            </label>
          </div>
          <label>
            Email
            <input autoComplete="email" type="email" required value={form.email}
              onChange={(e) => set('email', e.target.value)} placeholder="you@example.com" />
          </label>
          <div className="form-row-2">
            <label>
              Password
              <div className="pw-wrap">
                <input autoComplete="new-password" required type={showPw ? 'text' : 'password'}
                  value={form.password} onChange={(e) => set('password', e.target.value)} placeholder="12+ chars" />
                <button type="button" onClick={() => setShowPw(!showPw)}>
                  {showPw ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </label>
            <label>
              Confirm password
              <input autoComplete="new-password" required type={showPw ? 'text' : 'password'}
                value={form.confirmPassword} onChange={(e) => set('confirmPassword', e.target.value)} placeholder="Repeat" />
            </label>
          </div>
          {error && <div className="auth-msg error">{error}</div>}
          <button className="auth-submit" disabled={busy}>
            {busy ? 'Creating...' : 'Create Account'} <ArrowRight size={15} />
          </button>
        </form>

        <div className="auth-links">
          <button onClick={() => navigate('/login')}>Already have an account? Sign in</button>
        </div>
      </div>
    </div>
  );
}
