import { useEffect, useMemo, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Activity, AlertTriangle, ArrowDownRight, ArrowRight, ArrowUpRight, Bell,
  BookOpen, Bot, Check, ChevronDown, ChevronLeft, ChevronRight, CircleHelp,
  Clock3, Database, Eye, FileClock, FileText, Globe2, Heart, LayoutDashboard, LocateFixed, LockKeyhole,
  LogOut, MapPin, Menu, MessageSquareText, Network, PhoneCall, Plus, Radar, RefreshCw, Search, Settings,
  Shield, ShieldAlert, ShieldCheck, Siren, Sparkles, Square, Timer, Trash2, Volume2, X, Zap
} from 'lucide-react';
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Pie, PieChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis
} from 'recharts';
import './CyberShield.css';

const userNavigation = [
  ['Dashboard', LayoutDashboard], ['Cybercrime Prediction', Radar], ['RAG Intelligence', MessageSquareText],
  ['Prediction History', FileClock], ['My Reports', FileText], ['Threat Intelligence', ShieldAlert],
  ['Crime Statistics', Activity], ['Women Safety', Heart], ['Safety History', Clock3],
  ['Knowledge Base', BookOpen], ['Profile', ShieldCheck], ['Settings', Settings],
];
const adminNavigation = [
  ['Admin Dashboard', LayoutDashboard], ['Users', ShieldCheck], ['Complaints', FileText], ['Safety Alerts', Heart],
  ['Predictions', FileClock], ['Analytics', Activity], ['Knowledge Base', BookOpen],
  ['Reference Dataset', Database], ['System Status', Zap], ['Settings', Settings],
];
const routeMap = {
  '/dashboard': 'Dashboard', '/admin': 'Admin Dashboard', '/predict': 'Cybercrime Prediction',
  '/rag': 'RAG Intelligence', '/history': 'Prediction History', '/reports': 'My Reports',
  '/women-safety': 'Women Safety', '/safety-history': 'Safety History',
  '/admin/users': 'Users', '/admin/complaints': 'Complaints', '/admin/predictions': 'Predictions',
  '/admin/analytics': 'Analytics', '/knowledge-base': 'Knowledge Base',
  '/admin/safety-alerts': 'Safety Alerts',
  '/admin/knowledge-base': 'Knowledge Base', '/dataset/kaggle-job-fraud': 'Reference Dataset',
  '/admin/datasets/kaggle-job-fraud': 'Reference Dataset', '/admin/system': 'System Status',
  '/threat-intelligence': 'Threat Intelligence',
  '/crime-statistics': 'Crime Statistics',
  '/profile': 'Profile', '/settings': 'Settings', '/admin/settings': 'Settings',
};
const palette = ['#52d5e4', '#738aff', '#ab8cf5', '#f5b65f', '#f17b98', '#6bbf9d'];
const severityTone = (value) => String(value || 'medium').toLowerCase();

async function api(path, options) {
  const response = await fetch(path, { credentials: 'include', ...options });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.message || `Request failed (${response.status})`);
  return data;
}

function App({ user, onLogout, onUserUpdate }) {
  const location = useLocation();
  const navigate = useNavigate();
  const allowedPages = user.role === 'ADMIN' ? adminNavigation : userNavigation;
  const defaultPage = user.role === 'ADMIN' ? 'Admin Dashboard' : 'Dashboard';
  const [page, setPage] = useState(routeMap[location.pathname] || defaultPage);
  const [health, setHealth] = useState(false);
  const [complaints, setComplaints] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [queryHistory, setQueryHistory] = useState([]);
  const [adminUsers, setAdminUsers] = useState(null);
  const [adminComplaints, setAdminComplaints] = useState([]);
  const [adminOverview, setAdminOverview] = useState(null);
  const [adminSystem, setAdminSystem] = useState(null);
  const [referenceDataset, setReferenceDataset] = useState(null);
  const [datasetLoading, setDatasetLoading] = useState(false);
  const [datasetAttempted, setDatasetAttempted] = useState(false);
  const [search, setSearch] = useState('');
  const [toast, setToast] = useState('');
  const [busy, setBusy] = useState(false);
  const [mobileMenu, setMobileMenu] = useState(false);
  const [modal, setModal] = useState(null);
  const [ragResult, setRagResult] = useState(null);
  const [chatResult, setChatResult] = useState(null);
  const [chatQuestion, setChatQuestion] = useState('');
  const [predictionResult, setPredictionResult] = useState(null);
  const [savedComplaintId, setSavedComplaintId] = useState(null);
  const [form, setForm] = useState({ description: '', location: '', severity: 'High' });
  const [theme, setTheme] = useState(localStorage.getItem('cybershield-theme') || 'dark');
  const [notifications, setNotifications] = useState(localStorage.getItem('cybershield-notifications') !== 'false');
  const [compact, setCompact] = useState(localStorage.getItem('cybershield-compact') === 'true');
  const [filter, setFilter] = useState('All');
  const [ingestForm, setIngestForm] = useState({ title: '', category: 'Cybersecurity awareness', source: 'Local reference', text: '' });

  const refresh = async (quiet = false) => {
    try {
      const [status, records] = await Promise.all([api('/api/health'), api('/api/complaints')]);
      setHealth(status.status === 'online');
      setComplaints(records.data || []);
    } catch {
      setHealth(false);
    }
    try {
      const [knowledge, history] = await Promise.all([api('/api/rag/documents'), api('/api/rag/history')]);
      setDocuments(knowledge.data || []);
      setQueryHistory(history.data || []);
    } catch {
      setDocuments([]);
    }
    if (user.role === 'ADMIN') {
      try {
        const [overview, users, system, reports] = await Promise.all([
          api('/api/admin/dashboard'), api('/api/admin/users'), api('/api/admin/system'), api('/api/admin/complaints'),
        ]);
        setAdminOverview(overview);
        setAdminUsers(users.data || []);
        setAdminSystem(system);
        setAdminComplaints(reports.data || []);
      } catch {
        setAdminSystem(null);
        setAdminUsers([]);
      }
    }
    if (!quiet) setToast('Workspace data refreshed.');
  };

  useEffect(() => {
    refresh(true);
    const interval = window.setInterval(() => refresh(true), 30000);
    return () => window.clearInterval(interval);
  }, [user.role]);
  useEffect(() => {
    const nextPage = routeMap[location.pathname];
    const permitted = allowedPages.some(([label]) => label === nextPage);
    if (nextPage && permitted) setPage(nextPage);
    else if (!permitted) {
      setPage(defaultPage);
      navigate(user.role === 'ADMIN' ? '/admin' : '/dashboard', { replace: true });
    }
  }, [location.pathname, user.role]);
  useEffect(() => {
    if (page !== 'Reference Dataset' || datasetAttempted) return;
    setDatasetAttempted(true);
    setDatasetLoading(true);
    api('/api/datasets/indian-job-fraud').then((result) => {
      setReferenceDataset(result.dataset);
    }).catch((error) => {
      setToast(error.message);
    }).finally(() => {
      setDatasetLoading(false);
    });
  }, [page, datasetAttempted]);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem('cybershield-theme', theme);
  }, [theme]);
  useEffect(() => {
    if (!toast) return undefined;
    const timer = window.setTimeout(() => setToast(''), 3500);
    return () => window.clearTimeout(timer);
  }, [toast]);

  const filteredComplaints = useMemo(() => complaints.filter((item) => {
    const matchesQuery = !search || [item.id, item.category, item.location, item.status].some((part) => String(part).toLowerCase().includes(search.toLowerCase()));
    return matchesQuery && (filter === 'All' || String(item.severity).toLowerCase() === filter.toLowerCase());
  }), [complaints, search, filter]);
  const highRisk = complaints.filter((item) => ['high', 'critical'].includes(severityTone(item.severity))).length;
  const todayPredictions = queryHistory.filter((item) => new Date(item.created_at).toDateString() === new Date().toDateString()).length;

  const submitIncident = async (event) => {
    event.preventDefault();
    if (form.description.trim().length < 12 || !form.location.trim()) {
      setToast('Enter a location and an incident description of at least 12 characters.');
      return;
    }
    setBusy(true);
    setRagResult(null);
    setPredictionResult(null);
    try {
      // Step 1: get prediction with location for police station lookup
      let prediction = null;
      try {
        const predRes = await api('/api/predict', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ description: form.description, location: form.location }),
        });
        prediction = predRes.prediction;
        setPredictionResult(prediction);
      } catch { /* prediction unavailable — continue */ }

      // Step 2: save complaint (use predicted category if available, otherwise infer)
      const category = prediction?.predicted_category || 'Cybercrime Report';
      const saved = await api('/api/complaints', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ category, description: form.description, location: form.location, severity: form.severity }),
      });
      setSavedComplaintId(saved.complaint_id);

      // Step 3: RAG retrieval
      try {
        const result = await api('/api/rag/query', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: form.description, complaint_id: saved.complaint_id }),
        });
        setRagResult(result);
        setToast('Complaint analyzed. Prediction and knowledge guidance shown below.');
      } catch (error) {
        setToast(`Complaint saved; RAG retrieval unavailable: ${error.message}`);
      }
      setForm((f) => ({ ...f, description: '', location: '' }));
      await refresh(true);
    } catch (error) {
      setToast(`Complaint could not be saved: ${error.message}`);
    } finally {
      setBusy(false);
    }
  };

  const runQuery = async (event) => {
    event.preventDefault();
    if (chatQuestion.trim().length < 3) return setToast('Enter at least 3 characters to search the knowledge base.');
    setBusy(true);
    try {
      setChatResult(await api('/api/rag/query', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query: chatQuestion }) }));
      await refresh(true);
    } catch (error) {
      setToast(`Knowledge retrieval failed: ${error.message}`);
    } finally {
      setBusy(false);
    }
  };

  const ingestDocument = async (event) => {
    event.preventDefault();
    setBusy(true);
    try {
      const result = await api('/api/rag/ingest', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(ingestForm) });
      setToast(`Added ${result.data.chunks} knowledge chunks.`);
      setIngestForm({ title: '', category: 'Cybersecurity awareness', source: 'Local reference', text: '' });
      await refresh(true);
    } catch (error) {
      setToast(`Document was not added: ${error.message}`);
    } finally {
      setBusy(false);
    }
  };

  const reindexKnowledge = async () => {
    try {
      const result = await api('/api/rag/reindex', { method: 'POST' });
      setToast(`Re-indexed ${result.chunks_reindexed} chunks.`);
      await refresh(true);
    } catch (error) {
      setToast(`Re-index failed: ${error.message}`);
    }
  };

  const disableKnowledgeDocument = async (documentId) => {
    try {
      await api(`/api/rag/documents/${documentId}`, { method: 'DELETE' });
      setToast('Document disabled from future retrieval.');
      await refresh(true);
    } catch (error) {
      setToast(`Document could not be disabled: ${error.message}`);
    }
  };

  const clearRetrievalHistory = async () => {
    try {
      await api('/api/rag/history', { method: 'DELETE' });
      setQueryHistory([]);
      setToast('RAG query history cleared. Complaint and knowledge records were preserved.');
    } catch (error) {
      setToast(`History could not be cleared: ${error.message}`);
    }
  };

  const updateAdminUser = async (userId, changes) => {
    try {
      await api(`/api/admin/users/${userId}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(changes) });
      setToast('User account updated.');
      await refresh(true);
    } catch (error) {
      setToast(error.message);
    }
  };

  const deleteAdminUser = async (targetUser) => {
    if (!window.confirm(`Delete ${targetUser.full_name}'s account? Complaint records will be retained without an owner.`)) return;
    try {
      await api(`/api/admin/users/${targetUser.id}`, { method: 'DELETE' });
      setToast('User account deleted.');
      await refresh(true);
    } catch (error) {
      setToast(error.message);
    }
  };

  const go = (label) => {
    setPage(label);
    setMobileMenu(false);
    setSearch('');
    const paths = user.role === 'ADMIN'
      ? { 'Admin Dashboard': '/admin', Users: '/admin/users', Complaints: '/admin/complaints', 'Safety Alerts': '/admin/safety-alerts', Predictions: '/admin/predictions', Analytics: '/admin/analytics', 'Knowledge Base': '/admin/knowledge-base', 'Reference Dataset': '/admin/datasets/kaggle-job-fraud', 'System Status': '/admin/system', Settings: '/admin/settings' }
      : { Dashboard: '/dashboard', 'Cybercrime Prediction': '/predict', 'RAG Intelligence': '/rag', 'Prediction History': '/history', 'My Reports': '/reports', 'Threat Intelligence': '/threat-intelligence', 'Crime Statistics': '/crime-statistics', 'Women Safety': '/women-safety', 'Safety History': '/safety-history', 'Knowledge Base': '/knowledge-base', 'Reference Dataset': '/dataset/kaggle-job-fraud', Profile: '/profile', Settings: '/settings' };
    if (paths[label]) navigate(paths[label]);
  };

  return <div className={`shell ${compact ? 'compact' : ''}`}>
    <aside className={`sidebar ${mobileMenu ? 'open' : ''}`}>
      <div className="brand"><span className="brand-icon"><Shield size={22} /></span><span><b>CyberNexa</b><small>{user.role === 'ADMIN' ? 'ADMIN' : 'CYBERNEXA'}</small></span><button className="icon-btn sidebar-dismiss" onClick={() => setMobileMenu(false)} aria-label="Close navigation"><X size={17} /></button></div>
      <div className="workspace-caption">NAVIGATION</div>
      <nav>{allowedPages.map(([name, Icon]) => <button key={name} onClick={() => go(name)} className={`nav-item ${page === name ? 'active' : ''}`}><Icon size={17} /><span>{name}</span>{name === 'Knowledge Base' && <small>{documents.length || 0}</small>}</button>)}</nav>
      <div className="sidebar-bottom"><div className="connection"><span className={`pulse ${health ? '' : 'offline'}`} /><span><b>{health ? 'API connected' : 'API offline'}</b><small>{health ? 'SQLite · Flask' : 'Local view only'}</small></span><button className="icon-btn" title="Refresh connection" onClick={() => refresh()}><RefreshCw size={15} /></button></div><button className="analyst" onClick={() => go(user.role === 'ADMIN' ? 'Users' : 'Profile')}><span className="avatar">{user.full_name.slice(0, 1).toUpperCase()}</span><span><b>{user.full_name}</b><small>{user.role === 'ADMIN' ? 'Administrator' : `@${user.username}`}</small></span></button><button className="logout-link" onClick={onLogout}><LogOut size={15} /> Sign out</button></div>
    </aside>
    {mobileMenu && <button className="scrim" aria-label="Close navigation" onClick={() => setMobileMenu(false)} />}
    <main className="main-area">
      <header className="topbar"><div className="crumb"><button className="icon-btn mobile-toggle" aria-label="Open navigation" onClick={() => setMobileMenu(true)}><Menu size={19} /></button><b>{page}</b></div><div className="top-actions"><span className="today-date"><Clock3 size={13} />{new Date().toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })} · {new Date().toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}</span><label className="search"><Search size={16} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search incidents..." /></label><span className="system-badge"><i className={`pulse ${health ? '' : 'offline'}`} />{health ? 'Systems normal' : 'Demo mode'}</span><button className="icon-btn" aria-label="Notifications" onClick={() => setToast(notifications ? 'No new notifications.' : 'Notifications are disabled in settings.')}><Bell size={18} /></button><button className="top-user" onClick={() => go(user.role === 'ADMIN' ? 'Settings' : 'Profile')}><span className="avatar">{user.full_name.slice(0, 1).toUpperCase()}</span><span>{user.full_name}</span></button></div></header>
      <section className={[
        'content',
        (page === 'Dashboard' || page === 'Admin Dashboard') ? 'dashboard-content' : '',
        page === 'RAG Intelligence' ? 'rag-content' : '',
        page === 'Reference Dataset' ? 'dataset-content' : '',
        page === 'Cybercrime Prediction' ? 'predict-content' : '',
        page === 'Threat Intelligence' ? 'threat-content' : '',
        page === 'Women Safety' ? 'safety-content' : '',
        page === 'Safety History' ? 'safety-history-content' : '',
        page === 'Prediction History' ? 'history-content' : '',
        (page === 'My Reports' || page === 'Complaints') ? 'reports-content' : '',
        page === 'Profile' ? 'profile-content' : '',
        page === 'Settings' ? 'settings-content' : '',
        page === 'Knowledge Base' ? 'knowledge-content' : '',
        (page === 'Users' || page === 'Analytics' || page === 'Predictions' || page === 'Safety Alerts' || page === 'System Status') ? 'admin-content' : '',
        page === 'Crime Statistics' ? 'stats-content' : '',
      ].filter(Boolean).join(' ')}>
        {page === 'Dashboard' && <Dashboard user={user} complaints={complaints} documents={documents} queries={queryHistory} health={health} onNavigate={go} onOpen={setModal} refresh={() => refresh()} today={todayPredictions} highRisk={highRisk} />}
        {page === 'Admin Dashboard' && <AdminDashboard overview={adminOverview} system={adminSystem} onNavigate={go} />}
        {page === 'Cybercrime Prediction' && (health ? <Prediction form={form} setForm={setForm} submit={submitIncident} busy={busy} rag={ragResult} health={health} prediction={predictionResult} complaintId={savedComplaintId} /> : <OfflinePreview form={form} setForm={setForm} />)}
        {page === 'RAG Intelligence' && <RagAssistant question={chatQuestion} setQuestion={setChatQuestion} run={runQuery} busy={busy} result={chatResult} history={queryHistory} />}
        {page === 'Threat Intelligence' && <Threats />}
        {page === 'Crime Statistics' && <CrimeStatistics />}
        {(page === 'Incident Reports' || page === 'My Reports' || page === 'Complaints') && <Reports incidents={page === 'Complaints' ? adminComplaints : filteredComplaints} filter={filter} setFilter={setFilter} onOpen={setModal} admin={page === 'Complaints'} />}
        {page === 'Prediction History' && <History entries={queryHistory} onClear={clearRetrievalHistory} />}
        {page === 'Predictions' && <History entries={queryHistory} onClear={clearRetrievalHistory} admin />}
        {page === 'Users' && <AdminUsers users={adminUsers} onUpdate={updateAdminUser} onDelete={deleteAdminUser} currentUser={user} />}
        {page === 'Crime Analytics' && <Analytics incidents={complaints} onOpen={setModal} />}
        {page === 'Analytics' && <Analytics incidents={complaints} onOpen={setModal} />}
        {page === 'Knowledge Base' && <Knowledge documents={documents} stats={documents.length} form={ingestForm} setForm={setIngestForm} submit={ingestDocument} busy={busy} admin={user.role === 'ADMIN'} onReindex={reindexKnowledge} onDisable={disableKnowledgeDocument} />}
        {page === 'Reference Dataset' && <ReferenceDataset dataset={referenceDataset} loading={datasetLoading} />}
        {page === 'Women Safety' && <WomenSafety onToast={setToast} />}
        {page === 'Safety History' && <SafetyHistory />}
        {page === 'Safety Alerts' && <AdminSafetyAlerts />}
        {page === 'System Status' && <AdminSystem system={adminSystem} health={health} />}
        {page === 'Profile' && <Profile user={user} onSave={async (values) => { try { const result = await api('/api/profile', { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(values) }); onUserUpdate(result.user); setToast('Profile updated.'); } catch (error) { setToast(error.message); } }} />}
        {page === 'Model Performance' && <UnavailableModel />}
        {page === 'About System' && <About />}
        {page === 'Settings' && <SettingsPage theme={theme} setTheme={setTheme} health={health} notifications={notifications} setNotifications={(value) => { setNotifications(value); localStorage.setItem('cybershield-notifications', String(value)); }} compact={compact} setCompact={(value) => { setCompact(value); localStorage.setItem('cybershield-compact', String(value)); }} onClearHistory={clearRetrievalHistory} reset={() => { setTheme('dark'); setNotifications(true); setCompact(false); localStorage.removeItem('cybershield-theme'); localStorage.removeItem('cybershield-notifications'); localStorage.removeItem('cybershield-compact'); setToast('Preferences reset to defaults.'); }} />}
      </section>
    </main>
    {toast && <div className="toast"><Check size={16} />{toast}<button onClick={() => setToast('')} aria-label="Dismiss"><X size={15} /></button></div>}
    {modal && <IncidentModal incident={modal} close={() => setModal(null)} />}
    <FloatingChatbot type="cyber" />
  </div>;
}

function Heading({ eyebrow, title, description, action }) { return <div className="page-heading"><div><small className="eyebrow">{eyebrow}</small><h1>{title}</h1><p>{description}</p></div>{action}</div>; }
function Panel({ title, subtitle, action, className = '', children }) { return <section className={`panel ${className}`}><div className="panel-title"><div><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div>{action}</div>{children}</section>; }
function Tag({ children, tone = 'neutral' }) { return <span className={`tag ${tone}`}>{children}</span>; }
function DemoNotice({ children }) { return <div className="notice"><AlertTriangle size={17} /><span>{children}</span></div>; }
function Empty({ title, text }) { return <div className="empty"><Database size={24} /><b>{title}</b><span>{text}</span></div>; }

function Dashboard({ user, complaints, documents, queries, health, onNavigate, onOpen, refresh, today, highRisk }) {
  const stats = [
    ['My complaints', complaints.length, 'Complaint records in the database', FileText, 'cyan'],
    ['RAG queries today', today, 'Knowledge questions retrieved today', Sparkles, 'violet'],
    ['High-risk reports', highRisk, 'Complaints marked High or Critical', ShieldAlert, 'coral'],
    ['Total RAG queries', queries.length, 'Persisted knowledge retrieval log', MessageSquareText, 'blue'],
    ['Knowledge documents', documents.length, 'Indexed guidance documents', BookOpen, 'amber'],
    ['System status', health ? 'Online' : 'Offline', health ? 'Flask and SQLite connected' : 'Retry API connection', health ? Zap : AlertTriangle, health ? 'green' : 'amber'],
  ];
  const categories = Object.entries(complaints.reduce((acc, item) => ({ ...acc, [item.category]: (acc[item.category] || 0) + 1 }), {})).map(([name, value]) => ({ name, value }));
  const hasData = complaints.length > 0;
  return (
    <>
      <Heading
        eyebrow={user.role === 'ADMIN' ? 'ADMINISTRATOR / OVERVIEW' : 'YOUR WORKSPACE / OVERVIEW'}
        title={`Welcome back, ${user.full_name.split(' ')[0]}`}
        description="Your cybercrime reports, knowledge queries, and safety workspace."
        action={<>
          <button className="button secondary" onClick={refresh}><RefreshCw size={15} /> Refresh</button>
          <button className="button primary" onClick={() => onNavigate('Cybercrime Prediction')}><Sparkles size={15} /> Analyze incident</button>
        </>}
      />
      {!health && <DemoNotice><b>Backend offline.</b> Start the Flask backend to load complaint records and enable RAG queries.</DemoNotice>}
      {health && !hasData && (
        <div className="welcome-callout">
          <ShieldCheck size={22} />
          <div>
            <b>You are all set.</b>
            <p>No complaints submitted yet. Use <button className="inline-action" onClick={() => onNavigate('Cybercrime Prediction')}>Cybercrime Prediction</button> to analyze an incident, or visit <button className="inline-action" onClick={() => onNavigate('RAG Intelligence')}>RAG Intelligence</button> to ask a cybersecurity question.</p>
          </div>
        </div>
      )}
      <div className="stat-grid">{stats.map(([label, value, note, Icon, tone]) => <article className="stat" key={label}><div><span>{label}</span><i className={`stat-icon ${tone}`}><Icon size={17} /></i></div><strong>{value}</strong><small>{note}</small></article>)}</div>
      {hasData && <>
        <div className="two-col">
          <Panel title="Complaint activity" subtitle="Monthly counts from your submitted reports">{complaints.length ? <ActivityChart incidents={complaints} /> : <Empty title="No complaint history yet" text="Submit a complaint to see monthly trends." />}</Panel>
          <Panel title="Crime category distribution" subtitle={categories.length ? 'Breakdown of your submitted complaints' : 'No records yet'}>{categories.length ? <Distribution data={categories} /> : <Empty title="No incident data" text="Categories appear after complaints are registered." />}</Panel>
        </div>
        <div className="two-col lower-grid">
          <Panel title="Recent incidents" subtitle={hasData ? 'Your saved complaint records' : 'No complaints yet'} action={<button className="text-btn" onClick={() => onNavigate('My Reports')}>All reports <ArrowRight size={14} /></button>}>{hasData ? <IncidentTable rows={complaints.slice(0, 5)} onOpen={onOpen} /> : <Empty title="Nothing to review yet" text="Submit a complaint through the Cybercrime Prediction page." />}</Panel>
          <Panel title="Risk level distribution" subtitle="Reported severity of your complaints">{hasData ? <SeverityDistribution incidents={complaints} /> : <Empty title="No severity data" text="Severity distribution appears from saved complaint records." />}</Panel>
          <Panel title="Recent RAG queries" subtitle="Your knowledge retrieval history" action={<button className="text-btn" onClick={() => onNavigate('RAG Intelligence')}>Ask a question <ArrowRight size={14} /></button>}>{queries.length ? <div className="query-list">{queries.slice(0, 4).map((item) => <div key={item.id}><MessageSquareText size={15} /><span>{item.query}</span><small>{new Date(item.created_at).toLocaleTimeString()}</small></div>)}</div> : <Empty title="No queries yet" text="Ask a cybersecurity question in RAG Intelligence." />}</Panel>
        </div>
      </>}
    </>
  );
}

function AdminDashboard({ overview, system, onNavigate }) {
  const counts = overview?.counts;
  const ml = system?.ml_metrics;
  return (
    <>
      <Heading eyebrow="CYBERNEXA / ADMIN CONSOLE" title="Administration overview" description="Account activity, complaint records, and service health." action={<button className="button secondary" onClick={() => onNavigate('System Status')}><Zap size={14} /> System status</button>} />
      <div className="stat-grid">
        {[['Total users', counts?.users, 'Registered accounts', ShieldCheck], ['Total complaints', counts?.complaints, 'All saved complaint records', FileText], ['RAG analyses', counts?.rag_queries, 'Retrieved knowledge queries', MessageSquareText]].map(([label, value, note, Icon]) => (
          <article className="stat" key={label}><div><span>{label}</span><i className="stat-icon cyan"><Icon size={17} /></i></div><strong>{value ?? '—'}</strong><small>{note}</small></article>
        ))}
      </div>
      <div className="two-col">
        <Panel title="Recent complaints" subtitle="System-wide records with submitter attribution" action={<button className="text-btn" onClick={() => onNavigate('Complaints')}>Manage complaints <ArrowRight size={14} /></button>}>
          {overview?.recent_complaints?.length ? (
            <div className="table-wrap"><table><thead><tr><th>ID</th><th>Category</th><th>Severity</th><th>Owner</th><th>Status</th><th>Date</th></tr></thead>
              <tbody>{overview.recent_complaints.map((item) => (
                <tr key={item.id}>
                  <td className="mono">INC-{String(item.id).padStart(4, '0')}</td>
                  <td className="strong-cell">{item.category}</td>
                  <td><Tag tone={severityTone(item.severity)}>{item.severity}</Tag></td>
                  <td>{item.username || 'Legacy record'}</td>
                  <td>{item.status}</td>
                  <td>{item.created_at ? new Date(`${item.created_at.replace(' ', 'T')}Z`).toLocaleDateString() : '—'}</td>
                </tr>
              ))}</tbody>
            </table></div>
          ) : <Empty title="No recent complaints" text="New user reports will appear here." />}
        </Panel>
        <Panel title="Service health" subtitle="Live local service checks">
          <div className="admin-health">
            <span><i className={`pulse ${system ? '' : 'offline'}`} />Backend and database</span>
            <Tag tone={system ? 'green' : 'amber'}>{system ? 'CONNECTED' : 'UNAVAILABLE'}</Tag>
            <span><Database size={15} />{system?.rag?.vector_store || 'RAG status unavailable'}</span>
            <span><Bot size={15} />ML model</span>
            <Tag tone={ml ? 'green' : 'neutral'}>{ml ? `${(ml.accuracy * 100).toFixed(1)}% accuracy` : 'Unavailable'}</Tag>
          </div>
        </Panel>
      </div>
      <div className="admin-shortcuts">
        <button className="button secondary" onClick={() => onNavigate('Users')}>Manage users <ArrowRight size={14} /></button>
        <button className="button secondary" onClick={() => onNavigate('Analytics')}>Review analytics <ArrowRight size={14} /></button>
        <button className="button secondary" onClick={() => onNavigate('Knowledge Base')}>Knowledge base <ArrowRight size={14} /></button>
        <button className="button secondary" onClick={() => onNavigate('System Status')}>Model performance <ArrowRight size={14} /></button>
      </div>
    </>
  );
}

function AdminUsers({ users, onUpdate, onDelete, currentUser }) {
  const [query, setQuery] = useState('');
  const visible = (users || []).filter((account) => [account.full_name, account.username, account.email, account.role].some((value) => value.toLowerCase().includes(query.toLowerCase())));
  return <><Heading eyebrow="ADMIN CONSOLE / ACCESS CONTROL" title="User management" description="Search accounts, change roles, and control access. Passwords and hashes are never returned." /><Panel title="Accounts" subtitle={users === null ? 'Loading accounts...' : `${visible.length} matching accounts`}><label className="report-search user-search"><Search size={14} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search name, username, email" /></label>{users === null ? <Empty title="Loading account records" text="User records are retrieved from the protected administrator API." /> : visible.length ? <div className="table-wrap"><table><thead><tr><th>Account</th><th>Email</th><th>Role</th><th>Created</th><th>Status</th><th>Actions</th></tr></thead><tbody>{visible.map((account) => <tr key={account.id}><td className="strong-cell">{account.full_name}<small className="user-handle">@{account.username}</small></td><td>{account.email}</td><td><select aria-label={`Role for ${account.username}`} value={account.role} disabled={account.id === currentUser.id} onChange={(event) => { const nextRole = event.target.value; if (nextRole !== 'ADMIN' || window.confirm(`Grant administrator access to ${account.full_name}?`)) onUpdate(account.id, { role: nextRole }); }}><option value="USER">USER</option><option value="ADMIN">ADMIN</option></select></td><td>{new Date(account.created_at).toLocaleDateString()}</td><td><Tag tone={account.is_active ? 'green' : 'neutral'}>{account.is_active ? 'Active' : 'Inactive'}</Tag></td><td><div className="user-actions"><button className="text-btn" disabled={account.id === currentUser.id} onClick={() => onUpdate(account.id, { is_active: !account.is_active })}>{account.is_active ? 'Deactivate' : 'Activate'}</button><button className="text-btn danger-text" disabled={account.id === currentUser.id} onClick={() => onDelete(account)}>Delete</button></div></td></tr>)}</tbody></table></div> : <Empty title="No matching users" text="Try a different search." />}</Panel></>;
}

function AdminSystem({ system, health }) {
  const ml = system?.ml_metrics;
  return (
    <>
      <Heading eyebrow="ADMIN CONSOLE / OPERATIONS" title="System status" description="Live status of the Flask backend, SQLite database, RAG retrieval service, and ML classifier." />
      <div className="stat-grid">
        <article className="stat"><div><span>Backend</span><i className={`stat-icon ${health ? 'green' : 'coral'}`}><Zap size={17} /></i></div><strong>{health ? 'Online' : 'Offline'}</strong><small>GET /api/health</small></article>
        <article className="stat"><div><span>Database</span><i className="stat-icon cyan"><Database size={17} /></i></div><strong>{system?.database || 'Unavailable'}</strong><small>SQLite connection</small></article>
        <article className="stat"><div><span>ML Model</span><i className={`stat-icon ${ml ? 'green' : 'amber'}`}><Bot size={17} /></i></div><strong>{ml ? 'Loaded' : 'Unavailable'}</strong><small>{ml ? ml.model_type?.split(' + ')[0] : 'Run python train_model.py'}</small></article>
      </div>
      {ml && (
        <>
          <Panel title="Classifier performance" subtitle={`${ml.model_type} · trained on ${ml.train_samples} samples · evaluated on ${ml.test_samples} samples`}>
            <div className="metrics-grid">
              <article><span>Accuracy</span><strong>{(ml.accuracy * 100).toFixed(1)}%</strong><small>Overall correct</small></article>
              <article><span>Precision</span><strong>{(ml.precision * 100).toFixed(1)}%</strong><small>Weighted avg</small></article>
              <article><span>Recall</span><strong>{(ml.recall * 100).toFixed(1)}%</strong><small>Weighted avg</small></article>
              <article><span>F1 Score</span><strong>{(ml.f1_score * 100).toFixed(1)}%</strong><small>Weighted avg</small></article>
            </div>
            <div className="table-wrap">
              <table>
                <thead><tr><th>Category</th><th>Precision</th><th>Recall</th><th>F1</th><th>Support</th></tr></thead>
                <tbody>
                  {ml.categories?.map((cat) => {
                    const r = ml.classification_report?.[cat] || {};
                    return (
                      <tr key={cat}>
                        <td className="strong-cell">{cat}</td>
                        <td>{r.precision != null ? (r.precision * 100).toFixed(1) + '%' : '—'}</td>
                        <td>{r.recall != null ? (r.recall * 100).toFixed(1) + '%' : '—'}</td>
                        <td>{r['f1-score'] != null ? (r['f1-score'] * 100).toFixed(1) + '%' : '—'}</td>
                        <td>{r.support ?? '—'}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Panel>
        </>
      )}
      <Panel title="RAG service">
        <div className="admin-health">
          <span><Database size={15} />Vector store</span><b>{system?.rag?.vector_store || 'Unavailable'}</b>
          <span><BookOpen size={15} />Documents and chunks</span><b>{system?.rag ? `${system.rag.documents} documents · ${system.rag.chunks} chunks` : 'Unavailable'}</b>
        </div>
      </Panel>
    </>
  );
}

const fallbackSafetySettings = {
  four_tap_enabled: true,
  tap_window_seconds: 4,
  countdown_seconds: 8,
  instant_alert_mode: false,
  quick_alert_enabled: true,
  loud_alarm_enabled: true,
  trip_monitoring_enabled: false,
  trip_update_interval: 60,
};

function requestDeviceLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Location is not available in this browser.'));
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (position) => resolve({
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
        location_accuracy: position.coords.accuracy,
        updated_at: new Date().toISOString(),
      }),
      () => reject(new Error('Enable location in browser.')),
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 },
    );
  });
}

function WomenSafety({ onToast }) {
  const [settings, setSettings] = useState(fallbackSafetySettings);
  const [contacts, setContacts] = useState([]);
  const [activeTrip, setActiveTrip] = useState(null);
  const [location, setLocation] = useState(null);
  const [locationState, setLocationState] = useState('not-requested');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tapCount, setTapCount] = useState(0);
  const [contactSelection, setContactSelection] = useState([]);
  const [trigger, setTrigger] = useState(null);
  const [countdown, setCountdown] = useState(-1);
  const [lastAlert, setLastAlert] = useState(null);
  const [showContacts, setShowContacts] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [contactDraft, setContactDraft] = useState({ name: '', relationship: '', phone: '' });
  const [editingContact, setEditingContact] = useState(null);
  const [busy, setBusy] = useState(false);
  const [alarmOn, setAlarmOn] = useState(false);
  const tapTimes = useRef([]);
  const holdTimer = useRef(null);
  const holdFired = useRef(false);
  const alarmContext = useRef(null);
  const alarmOscillator = useRef(null);

  const refreshSafety = async () => {
    setLoading(true);
    try {
      const [status, preferences, trusted] = await Promise.all([
        api('/api/safety/status'), api('/api/safety/settings'), api('/api/safety/contacts'),
      ]);
      setSettings(preferences.data);
      setContacts(trusted.data);
      setContactSelection(trusted.data.filter((contact) => contact.is_active).map((contact) => contact.id));
      setActiveTrip(status.trip);
    } catch (requestError) {
      setError(requestError.message || 'Unable to connect to the safety service.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { refreshSafety(); }, []);

  useEffect(() => {
    if (!trigger || countdown < 0 || countdown === 0) return undefined;
    const timer = window.setTimeout(() => setCountdown((seconds) => seconds - 1), 1000);
    return () => window.clearTimeout(timer);
  }, [trigger, countdown]);

  useEffect(() => {
    if (!trigger || countdown !== 0) return;
    const current = trigger;
    setTrigger(null);
    sendEmergency(current.type, current.contactIds);
  }, [trigger, countdown]);

  useEffect(() => {
    if (!activeTrip || !settings.trip_monitoring_enabled) return undefined;
    const interval = window.setInterval(async () => {
      try {
        const current = await requestDeviceLocation();
        setLocation(current);
        setLocationState('available');
        await api(`/api/safety/trip/${activeTrip.id}/location`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(current),
        });
      } catch {
        setLocationState('unavailable');
      }
    }, settings.trip_update_interval * 1000);
    return () => window.clearInterval(interval);
  }, [activeTrip, settings.trip_monitoring_enabled, settings.trip_update_interval]);

  useEffect(() => () => {
    window.clearTimeout(holdTimer.current);
    if (alarmOscillator.current) {
      try { alarmOscillator.current.stop(); } catch { /* oscillator may already have stopped */ }
    }
    if (alarmContext.current) alarmContext.current.close();
  }, []);

  const recordEvent = async (eventType) => {
    try {
      await api('/api/safety/events', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ event_type: eventType }) });
    } catch { /* event logging must not block user-controlled alarm actions */ }
  };

  const refreshLocation = async () => {
    setLocationState('requesting');
    try {
      const current = await requestDeviceLocation();
      setLocation(current);
      setLocationState('available');
      setError('');
    } catch (requestError) {
      setLocation(null);
      setLocationState('unavailable');
      setError(requestError.message);
    }
  };

  const sendEmergency = async (alertType, contactIds) => {
    setBusy(true);
    setLastAlert(null);
    let currentLocation = location;
    if (!currentLocation) {
      try {
        setLocationState('requesting');
        currentLocation = await requestDeviceLocation();
        setLocation(currentLocation);
        setLocationState('available');
      } catch {
        setLocationState('unavailable');
      }
    }
    try {
      const result = await api('/api/safety/alert', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          alert_type: alertType,
          contact_ids: contactIds,
          message: 'I may be in danger and need assistance. Please check on me.',
          ...(currentLocation || {}),
        }),
      });
      setLastAlert(result);
      onToast('Emergency alert request created in DEMO / SIMULATION mode. No contacts or services were contacted.');
    } catch (requestError) {
      setError(`Unable to connect to the safety service. ${requestError.message}`);
      setLastAlert({ alert_status: 'FAILED', notification_mode: 'DEMO / SIMULATION', message: 'The alert request could not reach the safety service.' });
    } finally {
      setBusy(false);
    }
  };

  const startConfirmation = (type) => {
    setTrigger({ type, contactIds: [...contactSelection] });
    setCountdown(-1);
  };

  const handleEmergencyTap = () => {
    if (!settings.four_tap_enabled) {
      startConfirmation('EMERGENCY');
      return;
    }
    const now = Date.now();
    const validTaps = tapTimes.current.filter((time) => now - time <= settings.tap_window_seconds * 1000);
    validTaps.push(now);
    tapTimes.current = validTaps;
    setTapCount(validTaps.length);
    if (validTaps.length >= 4) {
      tapTimes.current = [];
      setTapCount(0);
      setTrigger({ type: 'FOUR_TAP', contactIds: [...contactSelection] });
      setCountdown(-1);
      void recordEvent('EMERGENCY_TRIGGERED');
    }
  };

  const beginCountdown = () => {
    if (settings.instant_alert_mode) {
      const selected = [...trigger.contactIds];
      setTrigger(null);
      setCountdown(-1);
      void sendEmergency(trigger.type, selected);
      return;
    }
    setCountdown(settings.countdown_seconds);
  };

  const cancelPending = async () => {
    setTrigger(null);
    setCountdown(-1);
    setTapCount(0);
    try {
      await api('/api/safety/alert/cancel-pending', { method: 'POST' });
      onToast('Alert cancelled. No request was created.');
    } catch {
      onToast('Alert cancelled on this device. The safety service could not confirm the event.');
    }
  };

  const startTrip = async () => {
    setBusy(true);
    let currentLocation = null;
    try {
      setLocationState('requesting');
      currentLocation = await requestDeviceLocation();
      setLocation(currentLocation);
      setLocationState('available');
    } catch {
      setLocationState('unavailable');
    }
    try {
      const result = await api('/api/safety/trip/start', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(currentLocation || {}) });
      setActiveTrip(result.trip);
      onToast('Trip started. Location monitoring remains off unless enabled in Safety Settings.');
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  };

  const endTrip = async () => {
    if (!activeTrip) return;
    try {
      await api(`/api/safety/trip/${activeTrip.id}/end`, { method: 'POST' });
      setActiveTrip(null);
      onToast('Trip ended.');
    } catch (requestError) { setError(requestError.message); }
  };

  const markSafe = async () => {
    try {
      await api('/api/safety/safe', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ contact_ids: contactSelection }) });
      setActiveTrip(null);
      setLastAlert({ alert_status: 'SAFE', notification_mode: 'DEMO / SIMULATION', message: 'Safe status recorded. No contacts were messaged.' });
      onToast('Your SAFE status is recorded. No contacts were messaged.');
    } catch (requestError) { setError(requestError.message); }
  };

  const activateAlarm = async () => {
    try {
      const context = new window.AudioContext();
      const oscillator = context.createOscillator();
      const gain = context.createGain();
      oscillator.type = 'square';
      oscillator.frequency.value = 880;
      gain.gain.value = 0.35;
      oscillator.connect(gain);
      gain.connect(context.destination);
      oscillator.start();
      alarmContext.current = context;
      alarmOscillator.current = oscillator;
      setAlarmOn(true);
      void recordEvent('ALARM_ACTIVATED');
    } catch {
      onToast('This browser could not start audio. Check device audio permissions.');
    }
  };

  const stopAlarm = async () => {
    if (alarmOscillator.current) {
      try { alarmOscillator.current.stop(); } catch { /* already stopped */ }
      alarmOscillator.current = null;
    }
    if (alarmContext.current) {
      await alarmContext.current.close();
      alarmContext.current = null;
    }
    setAlarmOn(false);
    void recordEvent('ALARM_STOPPED');
  };

  const saveContact = async (event) => {
    event.preventDefault();
    const path = editingContact ? `/api/safety/contacts/${editingContact.id}` : '/api/safety/contacts';
    const method = editingContact ? 'PATCH' : 'POST';
    try {
      await api(path, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(contactDraft) });
      setContactDraft({ name: '', relationship: '', phone: '' });
      setEditingContact(null);
      await refreshSafety();
      onToast('Emergency contact saved.');
    } catch (requestError) { setError(requestError.message); }
  };

  const deleteContact = async (contact) => {
    if (!window.confirm(`Remove ${contact.name} from your emergency contacts?`)) return;
    try {
      await api(`/api/safety/contacts/${contact.id}`, { method: 'DELETE' });
      await refreshSafety();
      onToast('Emergency contact removed.');
    } catch (requestError) { setError(requestError.message); }
  };

  const toggleContact = async (contact) => {
    try {
      await api(`/api/safety/contacts/${contact.id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ is_active: !contact.is_active }) });
      setContactSelection((current) => contact.is_active ? current.filter((id) => id !== contact.id) : [...current, contact.id]);
      await refreshSafety();
    } catch (requestError) { setError(requestError.message); }
  };

  const saveSettings = async (event) => {
    event.preventDefault();
    try {
      const result = await api('/api/safety/settings', { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(settings) });
      setSettings(result.data);
      setShowSettings(false);
      onToast('Safety settings saved.');
    } catch (requestError) { setError(requestError.message); }
  };

  const beginHold = () => {
    holdFired.current = false;
    window.clearTimeout(holdTimer.current);
    holdTimer.current = window.setTimeout(() => {
      holdFired.current = true;
      if (settings.quick_alert_enabled) setTrigger({ type: 'QUICK_ALERT', contactIds: [...contactSelection] });
    }, 2000);
  };
  const endHold = () => window.clearTimeout(holdTimer.current);

  return <main className="safety-page">
    <header className="safety-heading"><div><span className="safety-kicker"><Heart size={15} /> PERSONAL SAFETY</span><h1>Women Safety</h1><p>Your personal safety hub.</p></div><span className={`safety-state ${activeTrip ? 'trip' : ''}`}><i />{activeTrip ? 'TRIP ACTIVE' : 'NORMAL'}</span></header>
    {error && <div className="safety-error" role="alert"><AlertTriangle size={17} /><span>{error}</span><button onClick={() => setError('')} aria-label="Dismiss"><X size={15} /></button></div>}
    {loading ? <div className="safety-loading">Loading your private safety settings...</div> : <>
      <section className="safety-hero"><div className="safety-hero-copy"><span>EMERGENCY ASSISTANCE</span><h2>Emergency Alert</h2><p>Tap the button below to alert your trusted contacts.</p><button className="emergency-button" onClick={handleEmergencyTap} disabled={busy}><Siren size={19} />{settings.four_tap_enabled ? `Emergency Alert${tapCount ? ` · Tap ${tapCount} of 4` : ''}` : 'Emergency Alert'}</button><small>{settings.four_tap_enabled ? `Tap 4 times within ${settings.tap_window_seconds} seconds. A confirmation/countdown follows.` : 'Tap to open emergency confirmation.'}</small></div><div className="safety-status-box"><span className="status-symbol"><ShieldCheck size={22} /></span><div><b>{activeTrip ? 'Trip in progress' : 'Safety status normal'}</b><span>{activeTrip ? `Started ${new Date(activeTrip.started_at.replace(' ', 'T') + 'Z').toLocaleTimeString()}` : 'No active trip or alert.'}</span></div></div></section>
      <section className="safety-actions-grid"><button className="safety-action safe-action" onClick={markSafe}><Heart size={19} /><span><b>I'm Safe</b><small>Mark yourself safe.</small></span></button>{activeTrip ? <button className="safety-action" onClick={endTrip}><Square size={19} /><span><b>End Trip</b><small>Stop the active trip session.</small></span></button> : <button className="safety-action" disabled={busy} onClick={startTrip}><MapPin size={19} /><span><b>Start Trip</b><small>Share your trip with contacts.</small></span></button>}<button className="safety-action" onPointerDown={beginHold} onPointerUp={endHold} onPointerLeave={endHold} onPointerCancel={endHold} onClick={() => { if (holdFired.current) { holdFired.current = false; return; } onToast('Press and hold for 2 seconds to open quick emergency confirmation.'); }} disabled={!settings.quick_alert_enabled}><Timer size={19} /><span><b>Quick Alert</b><small>Hold 2 seconds to trigger.</small></span></button><button className="safety-action" onClick={() => setShowContacts(true)}><PhoneCall size={19} /><span><b>Emergency Contacts</b><small>{contacts.filter((contact) => contact.is_active).length} trusted contact(s).</small></span></button><button className="safety-action" onClick={() => setShowSettings(true)}><Settings size={19} /><span><b>Safety Settings</b><small>Configure safety triggers.</small></span></button><button className="safety-action" onClick={location ? () => setLocation(null) : refreshLocation}><LocateFixed size={19} /><span><b>{location ? 'Clear Location View' : 'Get Current Location'}</b><small>{locationState === 'requesting' ? 'Requesting device permission...' : location ? `${location.latitude.toFixed(4)}, ${location.longitude.toFixed(4)}` : locationState === 'unavailable' ? 'Enable location in browser.' : 'Request GPS location.'}</small></span></button></section>
      {location && <div className="location-readout"><MapPin size={16} /><span><b>Current location</b><small>Accuracy ±{Math.round(location.location_accuracy)} m · updated {new Date(location.updated_at).toLocaleTimeString()}</small></span></div>}
      <div className="safety-secondary-grid"><section className="safety-panel"><div className="safety-panel-heading"><div><h2>Emergency services</h2><p>Emergency services: Call 112</p></div><PhoneCall size={17} /></div><div className="service-callout"><p></p><a href="tel:112"><PhoneCall size={16} /> Call local emergency number (112, India)</a><small>Call availability depends on your device, network, and region.</small></div></section><section className={`safety-panel alarm-panel ${alarmOn ? 'alarm-active' : ''}`}><div className="safety-panel-heading"><div><h2>Loud emergency alarm</h2><p>Alarm is intended to attract attention. Contact emergency services when necessary.</p></div><Volume2 size={18} /></div>{alarmOn ? <button className="alarm-stop" onClick={stopAlarm}><Square size={17} /> Stop Alarm</button> : <button className="alarm-start" onClick={activateAlarm} disabled={!settings.loud_alarm_enabled}><Volume2 size={17} /> Activate Loud Alarm</button>}</section></div>
      {lastAlert && <section className="safety-result"><div><span className="safety-kicker">EMERGENCY ALERT</span><h2>{lastAlert.alert_status === 'REQUEST_CREATED' ? 'Alert request created' : lastAlert.alert_status === 'SAFE' ? 'SAFE status recorded' : 'Alert status'}</h2><p>{lastAlert.message}</p></div><div className="result-meta"><Tag tone="amber">{lastAlert.notification_mode || 'DEMO / SIMULATION'}</Tag><span>Location: {lastAlert.location_available ? 'Available' : 'Unavailable'}</span>{lastAlert.contact_count !== undefined && <span>Selected contacts: {lastAlert.contact_count}</span>}</div></section>}

      {/* Evidence Recorder */}
      <VoiceRecorder onToast={onToast} />

      {/* Location Sharing */}
      <LocationSharing onToast={onToast} />

    </>}
    {trigger && <div className="safety-modal-backdrop"><section className="safety-modal" role="dialog" aria-modal="true" aria-labelledby="safety-confirm-title"><div className="safety-modal-head"><span><AlertTriangle size={19} /></span><button className="icon-btn" onClick={cancelPending} aria-label="Close"><X size={17} /></button></div><h2 id="safety-confirm-title">{countdown >= 0 ? 'Emergency alert triggered.' : 'Confirm emergency alert'}</h2><p>The following active contacts will be included in a DEMO / SIMULATION request. No message is sent to them or to emergency services.</p><div className="confirm-contacts">{contacts.filter((contact) => trigger.contactIds.includes(contact.id) && contact.is_active).map((contact) => <div key={contact.id}><b>{contact.name}</b><span>{contact.relationship} · {contact.phone}</span></div>)}{!contacts.some((contact) => trigger.contactIds.includes(contact.id) && contact.is_active) && <span>No active contacts selected.</span>}</div>{countdown >= 0 && <div className="countdown-display"><strong>{countdown}</strong><span>seconds before request creation</span></div>}<div className="safety-modal-actions"><button className="secondary-safety-button" onClick={cancelPending}>Cancel Alert</button>{countdown < 0 && <button className="confirm-safety-button" disabled={busy} onClick={beginCountdown}>Send Emergency Alert</button>}</div></section></div>}
    {showContacts && <SafetyContactsModal contacts={contacts} selection={contactSelection} setSelection={setContactSelection} draft={contactDraft} setDraft={setContactDraft} editing={editingContact} setEditing={setEditingContact} onSave={saveContact} onDelete={deleteContact} onToggle={toggleContact} onClose={() => setShowContacts(false)} />}
    {showSettings && <SafetySettingsModal settings={settings} setSettings={setSettings} onSave={saveSettings} onClose={() => setShowSettings(false)} />}
    {/* Safety Chatbot */}
    <FloatingChatbot type="safety" />
  </main>;
}

function SafetyContactsModal({ contacts, selection, setSelection, draft, setDraft, editing, setEditing, onSave, onDelete, onToggle, onClose }) {
  return <div className="safety-modal-backdrop"><section className="safety-modal contacts-modal" role="dialog" aria-modal="true" aria-labelledby="contacts-title"><div className="safety-modal-head"><span><PhoneCall size={18} /></span><button className="icon-btn" onClick={onClose} aria-label="Close"><X size={17} /></button></div><h2 id="contacts-title">Emergency contacts</h2><p>Only you can view and manage these contacts. They are not contacted in simulation mode.</p><div className="contact-list">{contacts.map((contact) => <div className="contact-row" key={contact.id}><label><input type="checkbox" checked={selection.includes(contact.id)} disabled={!contact.is_active} onChange={() => setSelection((items) => items.includes(contact.id) ? items.filter((id) => id !== contact.id) : [...items, contact.id])} /><span><b>{contact.name}</b><small>{contact.relationship} · {contact.phone}{!contact.is_active ? ' · Disabled' : ''}</small></span></label><button className="text-btn" onClick={() => onToggle(contact)}>{contact.is_active ? 'Disable' : 'Enable'}</button><button className="text-btn" onClick={() => { setEditing(contact); setDraft({ name: contact.name, relationship: contact.relationship, phone: contact.phone }); }}>Edit</button><button className="text-btn danger-text" onClick={() => onDelete(contact)}>Delete</button></div>)}{!contacts.length && <div className="no-results">No trusted contacts added yet.</div>}</div><form className="contact-form" onSubmit={onSave}><h3>{editing ? 'Edit contact' : 'Add a trusted contact'}</h3><label>Name<input required maxLength={100} value={draft.name} onChange={(event) => setDraft({ ...draft, name: event.target.value })} /></label><label>Relationship<input required maxLength={60} value={draft.relationship} onChange={(event) => setDraft({ ...draft, relationship: event.target.value })} placeholder="Friend, parent, roommate" /></label><label>Phone number<input required type="tel" value={draft.phone} onChange={(event) => setDraft({ ...draft, phone: event.target.value })} placeholder="+1 555 0100" /></label><div className="safety-modal-actions"><button type="button" className="secondary-safety-button" onClick={() => { setEditing(null); setDraft({ name: '', relationship: '', phone: '' }); }}>Clear</button><button className="confirm-safety-button">{editing ? 'Save contact' : 'Add contact'}</button></div></form></section></div>;
}

function SafetySettingsModal({ settings, setSettings, onSave, onClose }) {
  const toggle = (key) => setSettings((current) => ({ ...current, [key]: !current[key] }));
  return <div className="safety-modal-backdrop"><section className="safety-modal safety-settings-modal" role="dialog" aria-modal="true" aria-labelledby="safety-settings-title"><div className="safety-modal-head"><span><Settings size={18} /></span><button className="icon-btn" onClick={onClose} aria-label="Close"><X size={17} /></button></div><h2 id="safety-settings-title">Safety settings</h2><p>Location access is controlled by your browser. Trip updates occur only while a trip is active and trip monitoring is enabled.</p><form onSubmit={onSave}><SafetyToggle title="Four-tap emergency trigger" detail="Four taps within the sensitivity window opens confirmation." checked={settings.four_tap_enabled} onChange={() => toggle('four_tap_enabled')} /><label className="setting-input">Tap sensitivity window<select value={settings.tap_window_seconds} onChange={(event) => setSettings({ ...settings, tap_window_seconds: Number(event.target.value) })}>{[2, 3, 4, 5, 6, 8].map((seconds) => <option key={seconds} value={seconds}>{seconds} seconds</option>)}</select></label><label className="setting-input">Cancellation countdown<select value={settings.countdown_seconds} onChange={(event) => setSettings({ ...settings, countdown_seconds: Number(event.target.value) })}>{[3, 5, 8, 10, 12, 15].map((seconds) => <option key={seconds} value={seconds}>{seconds} seconds</option>)}</select></label><SafetyToggle title="Instant alert mode" detail="Skips the countdown after you confirm. Use only if you understand the risk of accidental requests." checked={settings.instant_alert_mode} onChange={() => toggle('instant_alert_mode')} /><SafetyToggle title="Quick press-and-hold alert" detail="Hold the quick-alert control for 2 seconds to open confirmation." checked={settings.quick_alert_enabled} onChange={() => toggle('quick_alert_enabled')} /><SafetyToggle title="Loud alarm" detail="Enables the browser audio alarm. Device audio permissions still apply." checked={settings.loud_alarm_enabled} onChange={() => toggle('loud_alarm_enabled')} /><SafetyToggle title="Trip location updates" detail="Explicit opt-in. Location is requested periodically only while this page is open and a trip is active." checked={settings.trip_monitoring_enabled} onChange={() => toggle('trip_monitoring_enabled')} /><label className="setting-input">Trip update interval<select value={settings.trip_update_interval} onChange={(event) => setSettings({ ...settings, trip_update_interval: Number(event.target.value) })}>{[30, 60, 120, 300, 600].map((seconds) => <option key={seconds} value={seconds}>{seconds} seconds</option>)}</select></label><div className="safety-modal-actions"><button type="button" className="secondary-safety-button" onClick={onClose}>Close</button><button className="confirm-safety-button">Save settings</button></div></form></section></div>;
}

function SafetyToggle({ title, detail, checked, onChange }) {
  return <div className="safety-toggle-row"><span><b>{title}</b><small>{detail}</small></span><button type="button" className={`setting-toggle ${checked ? 'on' : ''}`} role="switch" aria-checked={checked} onClick={onChange}><i /></button></div>;
}

function SafetyHistory() {
  const [events, setEvents] = useState(null);
  useEffect(() => { api('/api/safety/history').then((result) => setEvents(result.data)).catch(() => setEvents([])); }, []);
  return <main className="safety-page"><header className="safety-heading"><div><span className="safety-kicker"><Clock3 size={15} /> PERSONAL SAFETY</span><h1>Safety History</h1><p>Your safety events are private to your account.</p></div></header><section className="safety-panel"><div className="safety-panel-heading"><div><h2>Recent events</h2><p>Location coordinates are not displayed in this history.</p></div></div>{events === null ? <div className="safety-loading">Loading your safety history...</div> : events.length ? <div className="safety-history-list">{events.map((event) => <article key={event.id}><span className="history-event-icon"><ShieldCheck size={17} /></span><div><b>{event.event_type.replaceAll('_', ' ')}</b><small>{new Date(`${event.event_time}Z`).toLocaleString()} · {event.status}</small></div><Tag tone={event.status === 'ALERT_CANCELLED' ? 'neutral' : event.status === 'REQUEST_CREATED' ? 'amber' : 'green'}>{event.status.replaceAll('_', ' ')}</Tag><small>{event.metadata?.location_available ? 'Location available' : 'Location unavailable'}</small></article>)}</div> : <div className="safety-empty"><Clock3 size={22} /><b>No safety history yet</b><span>Trip, alarm, and alert events appear here.</span></div>}</section></main>;
}

function AdminSafetyAlerts() {
  const [alerts, setAlerts] = useState(null);
  const [error, setError] = useState('');
  useEffect(() => { api('/api/admin/safety-alerts').then((result) => setAlerts(result.data)).catch((requestError) => setError(requestError.message)); }, []);
  return <><Heading eyebrow="ADMIN CONSOLE / SAFETY OPERATIONS" title="Safety alerts" description="Operational metadata only. Exact coordinates, phone numbers, and message contents are not exposed here." /><DemoNotice><b>DEMO / SIMULATION.</b> No emergency provider is connected; records show requests only, not delivered alerts.</DemoNotice><Panel title="Safety alert requests" subtitle={alerts ? `${alerts.length} records` : 'Loading authorized records'}>{error ? <Empty title="Unable to load safety alerts" text={error} /> : alerts === null ? <Empty title="Loading alerts" text="Reading administrator-visible metadata." /> : alerts.length ? <div className="table-wrap"><table><thead><tr><th>Alert ID</th><th>Date/time</th><th>User</th><th>Type</th><th>Location</th><th>Status</th><th>Cancelled</th></tr></thead><tbody>{alerts.map((alert) => <tr key={alert.alert_id}><td className="mono">SAFE-{alert.alert_id}</td><td>{new Date(`${alert.triggered_at}Z`).toLocaleString()}</td><td>{alert.user_identifier}</td><td>{alert.alert_type}</td><td>{alert.location_available ? 'Available' : 'Unavailable'}</td><td><Tag tone={alert.status === 'REQUEST_CREATED' ? 'amber' : 'neutral'}>{alert.status}</Tag></td><td>{alert.cancelled ? 'Yes' : 'No'}</td></tr>)}</tbody></table></div> : <Empty title="No safety requests" text="Alert request metadata will appear here; user locations are not tracked." />}</Panel></>;
}

function ReferenceDataset({ dataset, loading }) {
  if (loading) return <><Heading eyebrow="REFERENCE DATA / KAGGLE" title="Indian Job Fraud Dataset" description="Loading the local CC0 dataset snapshot..." /><Panel title="Dataset"><Empty title="Loading dataset rows" text="Reading the downloaded Kaggle CSV." /></Panel></>;
  if (!dataset) return <><Heading eyebrow="REFERENCE DATA / KAGGLE" title="Indian Job Fraud Dataset" description="The local dataset snapshot is unavailable." /><Panel title="Dataset unavailable"><Empty title="Dataset could not be loaded" text="Check that the Kaggle CSV exists under data/kaggle/indian-job-fraud-dataset." /></Panel></>;
  const labelDistribution = [
    { name: 'Fraud', value: dataset.labels.fraud },
    { name: 'Legitimate', value: dataset.labels.legitimate },
  ];
  return <><Heading eyebrow="REFERENCE DATA / KAGGLE" title={dataset.title} description="A separately stored public dataset for exploration; it is not used as complaint or prediction data." action={<Tag tone="amber">SYNTHETIC DATA</Tag>} /><div className="notice"><AlertTriangle size={17} /><span>These are generated job-posting examples, not real reports. They are kept separate from user complaints, dashboard incident counts, and ML prediction output.</span></div><div className="stat-grid"><article className="stat"><span>Rows</span><strong>{dataset.row_count}</strong><small>From downloaded CSV v{dataset.version}</small></article><article className="stat"><span>Fraud label</span><strong>{dataset.labels.fraud}</strong><small>Synthetic postings marked label 1</small></article><article className="stat"><span>Legitimate label</span><strong>{dataset.labels.legitimate}</strong><small>Synthetic postings marked label 0</small></article></div><div className="two-col"><Panel title="Label distribution" subtitle="Counts from the Kaggle CSV"><Distribution data={labelDistribution} /></Panel><Panel title="Fraud archetypes" subtitle="Actual category counts from the local CSV"><div className="table-wrap"><table><thead><tr><th>Archetype</th><th>Rows</th></tr></thead><tbody>{dataset.archetypes.map((entry) => <tr key={entry.name}><td className="strong-cell">{entry.name}</td><td>{entry.count}</td></tr>)}</tbody></table></div></Panel></div><Panel title="Sample rows" subtitle={`First ${dataset.preview.length} records; contact details and full descriptions are not displayed`}><div className="table-wrap"><table><thead><tr><th>Title</th><th>Company</th><th>Location</th><th>Archetype</th><th>Label</th><th>Source tag</th></tr></thead><tbody>{dataset.preview.map((row, index) => <tr key={`${row.title}-${index}`}><td className="strong-cell">{row.title}</td><td>{row.company}</td><td>{row.location}</td><td>{row.archetype}</td><td><Tag tone={row.label === '1' ? 'high' : 'green'}>{row.label === '1' ? 'FRAUD' : 'LEGITIMATE'}</Tag></td><td>{row.source}</td></tr>)}</tbody></table></div></Panel><div className="dataset-attribution">Source: <a href={dataset.url} target="_blank" rel="noreferrer">{dataset.source}</a> · License: {dataset.license} · Fields: {dataset.columns.join(', ')}</div></>;
}

function Profile({ user, onSave }) {
  const [form, setForm] = useState({ full_name: user.full_name, username: user.username, email: user.email });
  const [busy, setBusy] = useState(false);
  return <><Heading eyebrow="ACCOUNT / PROFILE" title="Your profile" description="Edit your account details. Role changes are restricted to administrator controls." /><Panel title="Account details" subtitle={`Member since ${new Date(user.created_at).toLocaleDateString()}`}><form className="profile-form" onSubmit={async (event) => { event.preventDefault(); setBusy(true); await onSave(form); setBusy(false); }}><label>Full name<input required maxLength={100} value={form.full_name} onChange={(event) => setForm({ ...form, full_name: event.target.value })} /></label><label>Username<input required minLength={3} maxLength={24} value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} /></label><label>Email<input type="email" required value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} /></label><label>Role<input value={user.role} readOnly /></label><button className="button primary" disabled={busy}>{busy ? 'Saving...' : 'Save profile'}</button></form></Panel></>;
}

function ActivityChart({ incidents }) {
  const data = Object.entries(incidents.reduce((acc, item) => {
    const month = String(item.created_at || '').slice(0, 7) || 'Unknown';
    acc[month] = (acc[month] || 0) + 1;
    return acc;
  }, {})).sort((first, second) => first[0].localeCompare(second[0])).map(([month, count]) => ({ month, incidents: count }));
  return <ResponsiveContainer width="100%" height={240}><AreaChart data={data} margin={{ top: 10, right: 10, left: -18, bottom: 0 }}><defs><linearGradient id="activity-fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#52d5e4" stopOpacity={0.3} /><stop offset="1" stopColor="#52d5e4" stopOpacity={0} /></linearGradient></defs><CartesianGrid stroke="#29394b" strokeDasharray="3 5" vertical={false} /><XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: '#91a1b4', fontSize: 11 }} /><YAxis allowDecimals={false} axisLine={false} tickLine={false} tick={{ fill: '#91a1b4', fontSize: 11 }} /><Tooltip contentStyle={{ background: '#111c29', border: '1px solid #34465b', borderRadius: 7, color: '#eaf1f8' }} /><Area dataKey="incidents" name="Complaints" stroke="#52d5e4" strokeWidth={2} fill="url(#activity-fill)" /></AreaChart></ResponsiveContainer>;
}

function Distribution({ data }) { return <div className="distribution"><div className="donut"><ResponsiveContainer width="100%" height={190}><PieChart><Pie data={data} dataKey="value" nameKey="name" innerRadius={58} outerRadius={82} paddingAngle={3} stroke="none">{data.map((item, index) => <Cell key={item.name} fill={palette[index % palette.length]} />)}</Pie><Tooltip contentStyle={{ background: '#111c29', border: '1px solid #34465b', borderRadius: 7, color: '#eaf1f8' }} /></PieChart></ResponsiveContainer><div className="donut-total"><b>{data.reduce((sum, item) => sum + item.value, 0)}</b><small>REPORTS</small></div></div><div className="legend-list">{data.map((item, index) => <div key={item.name}><i style={{ background: palette[index % palette.length] }} /><span>{item.name}</span><b>{item.value}</b></div>)}</div></div>; }

function SeverityDistribution({ incidents }) { const counts = ['Critical', 'High', 'Medium', 'Low'].map((severity) => ({ severity, count: incidents.filter((item) => severityTone(item.severity) === severity.toLowerCase()).length })); return <div className="severity-list">{counts.map(({ severity, count }) => <div key={severity}><span><i className={severity.toLowerCase()} />{severity}</span><div><b style={{ width: `${Math.max(0, count / incidents.length * 100)}%` }} /></div><strong>{count}</strong></div>)}</div>; }

function IncidentTable({ rows, onOpen, admin = false }) { return <div className="table-wrap"><table><thead><tr><th>Incident ID</th><th>Crime type</th>{admin && <th>Submitted by</th>}<th>Location</th><th>Risk</th><th>Date</th><th>Status</th><th /></tr></thead><tbody>{rows.map((item) => <tr key={item.id}><td className="mono">INC-{String(item.id).padStart(4, '0')}</td><td className="strong-cell">{item.category}</td>{admin && <td>{item.owner_name || item.owner_username || 'Legacy record'}</td>}<td>{item.location}</td><td><Tag tone={severityTone(item.severity)}>{item.severity}</Tag></td><td>{item.created_at ? new Date(`${item.created_at}Z`).toLocaleDateString() : 'Not available'}</td><td>{item.status}</td><td><button className="icon-btn" onClick={() => onOpen(item)} aria-label="View incident"><ArrowRight size={15} /></button></td></tr>)}</tbody></table></div>; }

function OfflinePreview({ form, setForm }) {
  const [preview, setPreview] = useState(false);
  const set = (key, value) => setForm((current) => ({ ...current, [key]: value }));
  return (
    <>
      <Heading eyebrow="DEMO MODE / OFFLINE INTAKE" title="Local incident preview" description="The Flask service is offline. You can review form behavior locally; nothing is saved or analyzed." />
      <DemoNotice><b>Backend unavailable.</b> This preview will not save a complaint, run a classifier, or retrieve knowledge.</DemoNotice>
      <div className="two-col prediction-grid">
        <Panel title="Incident description" subtitle="Form held in this browser session only — nothing is sent">
          <form className="form" onSubmit={(event) => { event.preventDefault(); setPreview(true); }}>
            <label>
              What happened?
              <textarea required rows={6} value={form.description} onChange={(e) => set('description', e.target.value)} placeholder="Describe the cyber incident..." />
            </label>
            <div className="form-split">
              <label>Location<input required value={form.location} onChange={(e) => set('location', e.target.value)} placeholder="City or region" /></label>
              <label>Reported severity
                <select value={form.severity} onChange={(e) => set('severity', e.target.value)}>
                  {['Low', 'Medium', 'High', 'Critical'].map((level) => <option key={level}>{level}</option>)}
                </select>
              </label>
            </div>
            <button className="button primary full"><Eye size={15} /> Preview fields</button>
          </form>
        </Panel>
        <Panel title="Offline preview" subtitle="No data is sent">
          <div className="unavailable">
            <ShieldAlert size={24} />
            <b>{preview ? 'Local-only preview' : 'No analysis performed'}</b>
            <span>{preview ? `Reported severity: ${form.severity}. Description entered (${form.description.length} chars).` : 'Complete the fields to view a local-only preview.'}</span>
            <div><span>Prediction</span><b>Not available — backend offline</b></div>
            <div><span>Knowledge retrieval</span><b>Not available — backend offline</b></div>
          </div>
        </Panel>
      </div>
    </>
  );
}

function Prediction({ form, setForm, submit, busy, rag, health, prediction, complaintId }) {
  const set = (key, value) => setForm((current) => ({ ...current, [key]: value }));

  const downloadReport = () => {
    if (!complaintId) return;
    window.open(`/api/complaints/${complaintId}/report`, '_blank');
  };

  const downloadCSV = () => {
    window.open('/api/export/complaints', '_blank');
  };

  return (
    <>
      <Heading
        eyebrow="ANALYSIS / CYBERCRIME PREDICTION"
        title="Cybercrime complaint analysis"
        description="Describe what happened. Get AI prediction, action steps and nearest police station."
        action={complaintId && (
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="button secondary" onClick={downloadReport}>
              <FileText size={14} /> Download Report
            </button>
            <button className="button secondary" onClick={downloadCSV}>
              <Database size={14} /> Export CSV
            </button>
          </div>
        )}
      />
      <DemoNotice>
        <b>TF-IDF + Logistic Regression classifier.</b> Prediction is based on a trained ML model using keyword features.
        Confidence reflects model probability — not a verified legal finding. No police integrations are active.
      </DemoNotice>
      <div className="two-col prediction-grid">
        <Panel title="Describe the incident" subtitle="Plain-text complaint — describe what happened">
          <form className="form" onSubmit={submit}>
            <label>
              What happened?
              <textarea
                required minLength={12} maxLength={2000} rows={6}
                value={form.description}
                onChange={(e) => set('description', e.target.value)}
                placeholder={'Example: I received a message claiming to be from my bank asking me to click a link and verify my account details.\n\nDescribe the incident without including passwords or sensitive details.'}
              />
            </label>
            <div className="form-split">
              <label>
                Location / City
                <input required maxLength={100} value={form.location} onChange={(e) => set('location', e.target.value)} placeholder="City or region" />
              </label>
              <label>
                Reported severity
                <select value={form.severity} onChange={(e) => set('severity', e.target.value)}>
                  {['Low', 'Medium', 'High', 'Critical'].map((v) => <option key={v}>{v}</option>)}
                </select>
              </label>
            </div>
            <button className="button primary full" disabled={busy || !health}>
              {busy ? <><span className="spinner" /> Analyzing complaint...</> : <><Sparkles size={16} /> Analyze Complaint</>}
            </button>
            <small className="hint">{health ? 'Your complaint is saved to the database before analysis.' : 'Connect the Flask backend to analyze complaints.'}</small>
          </form>
        </Panel>

        <div className="result-stack">
          <Panel title="Prediction result" subtitle={prediction ? 'TF-IDF + Logistic Regression classifier' : 'No analysis yet'}>
            {prediction ? (
              <div className="prediction-result">
                <div className="pred-row"><span>Predicted category</span><b className="pred-category">{prediction.predicted_category}</b></div>
                {prediction.confidence != null && (
                  <div className="pred-row" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                    <span style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                      <span>Model confidence</span>
                      <b style={{ color: prediction.confidence > 0.7 ? 'var(--green)' : prediction.confidence > 0.4 ? 'var(--amber)' : 'var(--coral)' }}>
                        {prediction.confidence_percent}
                      </b>
                    </span>
                    <div className="conf-bar-wrap" style={{ width: '100%' }}>
                      <div className="conf-bar" style={{ width: `${(prediction.confidence * 100).toFixed(1)}%` }} />
                    </div>
                  </div>
                )}
                <div className="pred-row"><span>Reported severity</span><b>{form.severity}</b></div>
                <div className="pred-row"><span>Method</span><b>{prediction.method}</b></div>
                {prediction.top_features?.length > 0 && (
                  <div className="pred-row"><span>Key indicators</span><b style={{ color: 'var(--muted)', fontSize: 9 }}>{prediction.top_features.join(', ')}</b></div>
                )}
                {Object.keys(prediction.all_probabilities || {}).length > 1 && (
                  <div style={{ marginTop: 10, paddingTop: 10, borderTop: '1px solid var(--line)' }}>
                    <small style={{ color: 'var(--dim)', fontSize: 8, letterSpacing: '.6px' }}>ALL CATEGORY PROBABILITIES</small>
                    <div className="all-probs" style={{ marginTop: 6 }}>
                      {Object.entries(prediction.all_probabilities).map(([cat, prob]) => (
                        <div className="all-probs-row" key={cat}>
                          <span>{cat}</span>
                          <span>{(prob * 100).toFixed(1)}%</span>
                          <div className="mini-bar" style={{ width: `${(prob * 100).toFixed(1)}%` }} />
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                <div className="pred-note">
                  <AlertTriangle size={13} />
                  <span>{prediction.note}</span>
                </div>
              </div>
            ) : (
              <div className="unavailable">
                <Bot size={24} />
                <b>No prediction yet</b>
                <span>Submit a complaint description to see the predicted cybercrime category and confidence score.</span>
              </div>
            )}
          </Panel>

          <Panel title="Knowledge base guidance" subtitle={rag?.mode || 'Retrieved from local knowledge base'}>
            {rag ? (
              <>
                <p className="answer-text">{rag.answer}</p>
                <h3 className="subhead">Retrieved knowledge</h3>
                <Sources sources={rag.sources} chunks={rag.retrieved_chunks} />
              </>
            ) : (
              <Empty title="No guidance retrieved yet" text="Submit a complaint to search the local knowledge base." />
            )}
          </Panel>

          {rag?.recommendations?.length > 0 && (
            <Panel title="Recommended actions" subtitle="Extracted from retrieved knowledge passages">
              <ul className="action-list">
                {rag.recommendations.map((action) => <li key={action}><ShieldCheck size={15} />{action}</li>)}
              </ul>
            </Panel>
          )}

          {prediction?.action_steps?.length > 0 && (
            <Panel title="What to do next" subtitle="Step-by-step guidance for this crime type">
              <ol className="action-list" style={{ paddingLeft: 14 }}>
                {prediction.action_steps.map((step, i) => (
                  <li key={i} style={{ marginBottom: 8 }}>
                    <ShieldCheck size={14} style={{ color: 'var(--green)', flexShrink: 0, marginTop: 1 }} />
                    {step}
                  </li>
                ))}
              </ol>
            </Panel>
          )}

          {prediction?.nearest_station && (
            <Panel title="Nearest Cybercrime Police Station" subtitle={`Based on location: ${form.location || 'not specified'}`}>
              <div className="police-station-box">
                <div className="ps-row"><span className="ps-label">Station</span><b>{prediction.nearest_station.station}</b></div>
                <div className="ps-row"><span className="ps-label">Address</span><span>{prediction.nearest_station.address}</span></div>
                <div className="ps-row"><span className="ps-label">Phone</span><a href={`tel:${prediction.nearest_station.phone}`}>{prediction.nearest_station.phone}</a></div>
                <div className="ps-row"><span className="ps-label">Helpline</span><a href="tel:1930" className="ps-helpline">1930 (National Cyber Crime Helpline)</a></div>
                {prediction.nearest_station.email && <div className="ps-row"><span className="ps-label">Email</span><span>{prediction.nearest_station.email}</span></div>}
                {prediction.nearest_station.note && <div className="ps-note"><AlertTriangle size={12} />{prediction.nearest_station.note}</div>}
                <a href="https://cybercrime.gov.in" target="_blank" rel="noreferrer" className="ps-portal-link">
                  File online at cybercrime.gov.in →
                </a>
              </div>
            </Panel>
          )}
        </div>
      </div>
    </>
  );
}

function Sources({ sources = [], chunks = [] }) { if (!sources.length) return <div className="no-results">No relevant knowledge-base information was retrieved.</div>; return <div className="source-list">{sources.map((source, index) => <article className="source" key={source.document_id + source.section}><div><Tag tone="cyan">{source.category}</Tag><b>{source.title}</b><span>{source.source_type} · {source.source} · {source.section}</span></div><Tag tone="neutral">{source.relevance.toFixed(3)} relevance</Tag><p>{chunks[index]?.content || 'No text passage returned.'}</p></article>)}</div>; }

function RagAssistant({ question, setQuestion, run, busy, result, history }) {
  const examples = [
    'What should I do after receiving a suspicious banking message?',
    'How do I protect myself from OTP fraud?',
    'What are the signs of a phishing attack?',
    'What steps should I take after a suspected ransomware infection?',
    'How can I secure my online accounts from takeover?',
    'What is social engineering and how do I avoid it?',
  ];
  return (
    <>
      <Heading
        eyebrow="INTELLIGENCE / KNOWLEDGE RETRIEVAL"
        title="Cyber intelligence assistant"
        description="Ask any cybersecurity question. AI-powered answers from the knowledge base."
      />
      <div className="chat-layout">
        <Panel className="chat-panel" title="Knowledge assistant" subtitle="RAG Retrieval Mode · local knowledge base · no external LLM">
          <div className="chat-intro">
            <span><MessageSquareText size={20} /></span>
            <div>
              <b>Answers grounded in retrieved documents</b>
              <p>Each response shows its source document, excerpt, and relevance score. If no matching source is found, no answer is fabricated.</p>
            </div>
          </div>
          {result && (
            <div className="chat-answer">
              <div className="chat-user"><span>You asked</span><p>{question}</p></div>
              <div className="chat-bot">
                <span><Sparkles size={15} /> RAG Retrieval Mode</span>
                <p>{result.answer}</p>
                <Sources sources={result.sources} chunks={result.retrieved_chunks} />
              </div>
            </div>
          )}
          <form className="chat-form" onSubmit={run}>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              rows={3}
              placeholder="e.g. What should I do after receiving a suspicious bank message?"
            />
            <div>
              <small>Queries are stored in the local SQLite database.</small>
              <button className="button primary" disabled={busy}>
                {busy ? <span className="spinner" /> : <ArrowRight size={15} />} Ask knowledge base
              </button>
            </div>
          </form>
        </Panel>

        <div>
          <Panel title="Example questions" subtitle="Click to pre-fill the query">
            <div className="query-list">
              {examples.map((ex) => (
                <button key={ex} onClick={() => setQuestion(ex)}>
                  <Sparkles size={13} /><span>{ex}</span>
                </button>
              ))}
            </div>
          </Panel>
          <Panel title="Recent queries" subtitle="Saved retrieval activity" className="mt-panel">
            {history.length ? (
              <div className="query-list">
                {history.slice(0, 6).map((item) => (
                  <button key={item.id} onClick={() => setQuestion(item.query)}>
                    <Clock3 size={14} /><span>{item.query}</span>
                  </button>
                ))}
              </div>
            ) : (
              <Empty title="No query history" text="Your retrieved questions will appear here." />
            )}
          </Panel>
        </div>
      </div>
    </>
  );
}

function Knowledge({ documents, stats, form, setForm, submit, busy, admin, onReindex, onDisable }) { const set = (key, value) => setForm((old) => ({ ...old, [key]: value })); return <><Heading eyebrow="INTELLIGENCE / SOURCE MANAGEMENT" title="Knowledge base" description="Curated local guidance documents used by the RAG retrieval system." action={<><Tag tone="green">{stats} DOCUMENTS</Tag>{admin && <button className="button secondary" onClick={onReindex}><RefreshCw size={14} /> Re-index</button>}</>} /><div className={`two-col knowledge-grid ${admin ? '' : 'read-only'}`}>{admin && <Panel className="knowledge-write" title="Add a text document" subtitle="Plain text and Markdown content via JSON API"><form className="form" onSubmit={submit}><label>Upload TXT or Markdown<input type="file" accept=".txt,.md,text/plain,text/markdown" onChange={(event) => { const file = event.target.files?.[0]; if (!file) return; if (file.size > 200000) { event.target.value = ''; return; } const reader = new FileReader(); reader.onload = () => { set('title', file.name.replace(/\.(txt|md)$/i, '')); set('source', file.name); set('text', String(reader.result || '')); }; reader.readAsText(file); }} /></label><label>Document title<input required value={form.title} onChange={(e) => set('title', e.target.value)} /></label><div className="form-split"><label>Category<input value={form.category} onChange={(e) => set('category', e.target.value)} /></label><label>Source label<input value={form.source} onChange={(e) => set('source', e.target.value)} /></label></div><label>Document text<textarea required rows={7} maxLength={200000} value={form.text} onChange={(e) => set('text', e.target.value)} placeholder="Paste educational cybersecurity guidance. Do not add unsupported claims or citations." /></label><button className="button primary" disabled={busy}><Plus size={15} /> Add &amp; index document</button><small className="hint">TXT/Markdown only, up to 200 KB. PDF upload is not enabled.</small></form></Panel>}<Panel title="Indexed documents" subtitle={admin ? 'Disable documents to remove them from retrieval' : 'Available local educational documents'}><div className="table-wrap"><table><thead><tr><th>Document</th><th>Category</th><th>Source</th><th>Chunks</th><th>State</th>{admin && <th />}</tr></thead><tbody>{documents.map((doc) => <tr key={doc.document_id}><td className="strong-cell">{doc.title}</td><td>{doc.category}</td><td>{doc.source}</td><td>{doc.chunks}</td><td><Tag tone={doc.enabled ? 'green' : 'neutral'}>{doc.enabled ? 'Enabled' : 'Disabled'}</Tag></td>{admin && <td>{doc.enabled ? <button className="text-btn" onClick={() => onDisable(doc.document_id)}>Disable</button> : null}</td>}</tr>)}</tbody></table></div>{!documents.length && <Empty title="Knowledge base unavailable" text="Start the Flask API to seed local guidance." />}</Panel></div><div className="stats-strip"><span><Database size={16} /> Vector store <b>SQLite hashed-term similarity</b></span><span><BookOpen size={16} /> Total chunks <b>{documents.reduce((sum, doc) => sum + (doc.chunks || 0), 0)}</b></span><span><Clock3 size={15} /> Last ingestion <b>{documents[0]?.created_at ? new Date(`${documents[0].created_at}Z`).toLocaleString() : 'No ingestion yet'}</b></span><span><LockKeyhole size={16} /> External API <b>Not required</b></span></div></>; }

function Threats() { const items = [['Phishing', 'Critical', 'Deceptive messages and misleading links', 'Unexpected urgency, sender mismatch', 'Verify through a known official channel.'], ['Ransomware', 'High', 'Malware that can deny access to data', 'Unexpected encryption, ransom note', 'Follow incident response and preserve evidence.'], ['Malware', 'High', 'Software that performs unwanted actions', 'Unknown attachment or unexpected alert', 'Contact your security support team.'], ['DDoS', 'Medium', 'Traffic flood that can affect service availability', 'Service outage or unusual errors', 'Report timing and affected service to its owner.'], ['Identity theft', 'High', 'Misuse of personal or account information', 'Unknown profile or account activity', 'Use the official account recovery process.'], ['Financial fraud', 'High', 'Deceptive payment or transaction request', 'Unexpected transfer or OTP request', 'Contact the provider via an official channel.'], ['Data breach', 'High', 'Suspected unauthorized exposure of information', 'Unexpected disclosure or access alert', 'Preserve details and notify the response team.'], ['Social engineering', 'Medium', 'Deception or pressure to influence action', 'Urgency, secrecy, credential request', 'Pause and verify through another known channel.']]; return <><Heading eyebrow="INTELLIGENCE / ATTACK PATTERNS" title="Threat intelligence" description="General educational descriptions. Verify context against cited local knowledge before acting." /><div className="threat-grid">{items.map(([name, severity, desc, indicators, action]) => <article className="threat-card" key={name}><div className="threat-head"><ShieldAlert size={18} /><Tag tone={severity.toLowerCase()}>{severity}</Tag></div><h3>{name}</h3><p>{desc}</p><small>COMMON INDICATORS</small><p>{indicators}</p><small>GENERAL ACTION</small><p>{action}</p><span className="source-foot">Educational overview · not a live feed</span></article>)}</div></>; }

function Reports({ incidents, filter, setFilter, onOpen, admin = false }) {
  const [query, setQuery] = useState('');
  const [page, setPage] = useState(1);
  const [newestFirst, setNewestFirst] = useState(true);
  const pageSize = 8;
  const matches = incidents.filter((item) => !query || `${item.category} ${item.location} ${item.status} ${item.id}`.toLowerCase().includes(query.toLowerCase())).sort((a, b) => newestFirst ? b.id - a.id : a.id - b.id);
  const pages = Math.max(1, Math.ceil(matches.length / pageSize));
  const visible = matches.slice((page - 1) * pageSize, page * pageSize);

  const exportCSV = () => window.open('/api/export/complaints', '_blank');

  return (
    <>
      <Heading
        eyebrow={admin ? 'ADMIN CONSOLE / COMPLAINTS' : 'MY ACCOUNT / REPORTS'}
        title={admin ? 'Complaint management' : 'My reports'}
        description={admin ? 'System-wide complaints with account attribution.' : 'Only complaints submitted by your account are shown.'}
        action={<button className="button secondary" onClick={exportCSV}><Database size={14} /> Export CSV</button>}
      />
      <Panel title={admin ? 'All complaints' : 'Your complaints'} subtitle={`${matches.length} matching reports`}>
        <div className="report-tools">
          <div className="filter-tabs">{['All', 'Critical', 'High', 'Medium', 'Low'].map((v) => <button key={v} className={filter === v ? 'selected' : ''} onClick={() => { setFilter(v); setPage(1); }}>{v}</button>)}</div>
          <label className="report-search"><Search size={14} /><input value={query} onChange={(event) => { setQuery(event.target.value); setPage(1); }} placeholder="Search reports" /></label>
          <button className="button secondary" onClick={() => setNewestFirst(!newestFirst)}><Clock3 size={14} />{newestFirst ? 'Newest first' : 'Oldest first'}</button>
        </div>
        {matches.length ? (
          <>
            <IncidentTable rows={visible} onOpen={onOpen} admin={admin} />
            <div className="pagination">
              <span>Showing {Math.min(matches.length, (page - 1) * pageSize + 1)}-{Math.min(matches.length, page * pageSize)} of {matches.length}</span>
              <div>
                <button className="icon-btn" disabled={page <= 1} onClick={() => setPage(page - 1)}><ChevronLeft size={15} /></button>
                <span>Page {page} of {pages}</span>
                <button className="icon-btn" disabled={page >= pages} onClick={() => setPage(page + 1)}><ChevronRight size={15} /></button>
              </div>
            </div>
          </>
        ) : <Empty title="No matching complaints" text="Try a different search or severity filter." />}
      </Panel>
    </>
  );
}

function History({ entries, onClear }) { const [query, setQuery] = useState(''); const [minimumSources, setMinimumSources] = useState('Any'); const filtered = entries.filter((item) => item.query.toLowerCase().includes(query.toLowerCase()) && (minimumSources === 'Any' || (item.sources?.length || 0) > 0)); return <><Heading eyebrow="ANALYSIS / RETRIEVAL LOG" title="Prediction & RAG history" description="The existing project has no model history. This view lists persisted RAG queries only." action={<button className="button secondary" disabled={!entries.length} onClick={onClear}><X size={14} /> Clear RAG history</button>} /><Panel title="RAG query history" subtitle={`${filtered.length} matching queries`}><div className="history-controls"><label className="search history-search"><Search size={14} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search questions" /></label><select value={minimumSources} onChange={(event) => setMinimumSources(event.target.value)}><option>Any</option><option value="Retrieved">Retrieved sources</option></select></div>{filtered.length ? <div className="table-wrap"><table><thead><tr><th>Query ID</th><th>Date</th><th>Question</th><th>Mode</th><th>Sources</th></tr></thead><tbody>{filtered.map((item) => <tr key={item.id}><td className="mono">RAG-{item.id}</td><td>{new Date(item.created_at).toLocaleString()}</td><td>{item.query}</td><td><Tag tone="cyan">{item.mode}</Tag></td><td>{Array.isArray(item.sources) ? item.sources.length : 0}</td></tr>)}</tbody></table></div> : <Empty title="No matching RAG queries" text="Run a question in the Cyber Intelligence Assistant." />}</Panel></>; }

function Analytics({ incidents, onOpen }) {
  const [analyticsData, setAnalyticsData] = useState(null);
  useEffect(() => {
    api('/api/analytics').then((r) => setAnalyticsData(r)).catch(() => setAnalyticsData(null));
  }, [incidents.length]);

  // Use backend-aggregated data when available, fall back to client-side
  const categories = analyticsData?.categories?.length
    ? analyticsData.categories.map((r) => ({ name: r.name, value: r.count }))
    : Object.entries(incidents.reduce((acc, item) => ({ ...acc, [item.category]: (acc[item.category] || 0) + 1 }), {})).map(([name, value]) => ({ name, value }));

  const severity = analyticsData?.severity?.length
    ? analyticsData.severity.map((r) => ({ name: r.name, value: r.count }))
    : Object.entries(incidents.reduce((acc, item) => ({ ...acc, [item.severity]: (acc[item.severity] || 0) + 1 }), {})).map(([name, value]) => ({ name, value }));

  const monthly = analyticsData?.monthly?.length
    ? analyticsData.monthly.map((r) => ({ month: r.month, complaints: r.count }))
    : Object.entries(incidents.reduce((acc, item) => { const key = String(item.created_at || '').slice(0, 7) || 'Unknown'; acc[key] = (acc[key] || 0) + 1; return acc; }, {})).sort((a, b) => a[0].localeCompare(b[0])).map(([month, complaints]) => ({ month, complaints }));

  const highRisk = incidents.filter((item) => ['high', 'critical'].includes(severityTone(item.severity)));
  const total = analyticsData?.total ?? incidents.length;

  return (
    <>
      <Heading eyebrow="ANALYTICS / DATABASE RECORDS" title="Crime analytics" description="Visualizations sourced directly from the SQLite database. Empty data stays empty." />
      {total > 0 ? (
        <>
          <div className="stat-grid" style={{ gridTemplateColumns: 'repeat(3, minmax(0,1fr))' }}>
            <article className="stat"><div><span>Total complaints</span><i className="stat-icon cyan"><FileText size={17} /></i></div><strong>{total}</strong><small>All time</small></article>
            <article className="stat"><div><span>High / Critical</span><i className="stat-icon coral"><ShieldAlert size={17} /></i></div><strong>{highRisk.length}</strong><small>Elevated risk</small></article>
            <article className="stat"><div><span>Categories</span><i className="stat-icon violet"><Radar size={17} /></i></div><strong>{categories.length}</strong><small>Distinct crime types</small></article>
          </div>
          <div className="two-col">
            <Panel title="Crime categories" subtitle="Counts from database records">
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={categories} margin={{ left: 5, bottom: 32 }}>
                  <CartesianGrid stroke="#29394b" strokeDasharray="3 5" vertical={false} />
                  <XAxis dataKey="name" angle={-22} textAnchor="end" interval={0} tick={{ fill: '#91a1b4', fontSize: 10 }} />
                  <YAxis allowDecimals={false} tick={{ fill: '#91a1b4', fontSize: 11 }} />
                  <Tooltip contentStyle={{ background: '#111c29', border: '1px solid #34465b', borderRadius: 7, color: '#eaf1f8' }} />
                  <Bar dataKey="value" name="Complaints" fill="#52d5e4" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Panel>
            <Panel title="Monthly trend" subtitle="Complaints by month">
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={monthly} margin={{ left: -15, right: 8, top: 10 }}>
                  <CartesianGrid stroke="#29394b" strokeDasharray="3 5" vertical={false} />
                  <XAxis dataKey="month" tick={{ fill: '#91a1b4', fontSize: 10 }} />
                  <YAxis allowDecimals={false} tick={{ fill: '#91a1b4', fontSize: 11 }} />
                  <Tooltip contentStyle={{ background: '#111c29', border: '1px solid #34465b', borderRadius: 7, color: '#eaf1f8' }} />
                  <Area dataKey="complaints" stroke="#738aff" fill="#738aff33" />
                </AreaChart>
              </ResponsiveContainer>
            </Panel>
          </div>
          <div className="two-col">
            <Panel title="Reported severity" subtitle="Counts from database records"><Distribution data={severity} /></Panel>
            <Panel title="High-risk incidents" subtitle="Records marked High or Critical">{highRisk.length ? <IncidentTable rows={highRisk.slice(0, 8)} onOpen={onOpen} /> : <Empty title="No high-risk reports" text="No complaints are marked High or Critical." />}</Panel>
          </div>
        </>
      ) : (
        <Panel title="Complaint analytics"><Empty title="No incident data" text="Analytics appear after complaints are stored in the database." /></Panel>
      )}
    </>
  );
}

function Risk({ complaints, highRisk }) { const percent = complaints.length ? Math.round(highRisk / complaints.length * 100) : null; return <><Heading eyebrow="ASSESSMENT / REPORTED SEVERITY" title="Risk analysis" description="Descriptive indicators based on submitted complaint severity, not a predictive score." /><div className="two-col"><Panel title="Overall reported severity" subtitle="High and critical reports divided by saved complaints"><div className="risk-score"><b>{percent === null ? 'N/A' : `${percent}%`}</b><span>{percent === null ? 'No connected data' : 'High / critical share'}</span><div className="factor-bar"><i style={{ width: `${percent || 0}%` }} /></div><p>{percent === null ? 'Connect the Flask API to inspect current complaints.' : `${highRisk} of ${complaints.length} saved complaint(s) are marked high or critical.`}</p></div></Panel><Panel title="Contributing factors" subtitle="Only fields present in complaint data are considered"><div className="factor"><b>Reported severity</b><span>Directly supplied by complaint submitter</span></div><div className="factor"><b>Complaint volume</b><span>{complaints.length} saved record(s)</span></div><DemoNotice>No model-derived impact or probability is available.</DemoNotice></Panel></div></>; }

function UnavailableModel() { return <><Heading eyebrow="MODEL OPERATIONS / VALIDATION" title="Model performance" description="Metrics are only shown when a trained model and evaluation data exist." /><DemoNotice><b>Model performance metrics are not currently configured.</b> There are no model files or evaluation reports in this project.</DemoNotice><div className="stat-grid">{['Accuracy', 'Precision', 'Recall', 'F1 score'].map((name) => <article className="stat" key={name}><span>{name}</span><strong>N/A</strong><small>Not available</small></article>)}</div><div className="two-col"><Panel title="Confusion matrix" subtitle="Evaluation data unavailable"><Empty title="No classifier configured" text="A labeled evaluation set is required to calculate a confusion matrix." /></Panel><Panel title="Classification report" subtitle="Per-class precision, recall, F1, and support"><Empty title="No report generated" text="Add a validated model and held-out evaluation data to display this report." /></Panel></div></>; }

function About() { return <><Heading eyebrow="PLATFORM / DOCUMENTATION" title="About CyberNexa" description="Cybercrime complaint analysis and source-grounded threat intelligence." /><div className="two-col"><Panel title="Project overview"><p className="body-copy">This application extends the CyberCrimePredict project, preserving its Flask complaint API and SQLite complaint records while adding a React analyst dashboard and a local retrieval knowledge base.</p><h3>Current limitations</h3><ul className="plain-list"><li>No trained ML model or prediction logic exists in this repository.</li><li>RAG uses deterministic hashed-term similarity, not a neural embedding model.</li><li>Fallback answers only reproduce retrieved source guidance.</li><li>Knowledge documents are plain text; PDF parsing is not configured.</li></ul></Panel><Panel title="Verified architecture"><div className="architecture">{['User complaint', 'React + Vite', 'Flask REST API', 'SQLite complaints + RAG chunks', 'Hashed-term retrieval', 'Grounded excerpts + sources'].map((step, i) => <div key={step}><i>{String(i + 1).padStart(2, '0')}</i><span>{step}</span>{i < 5 && <ArrowDownRight size={15} />}</div>)}</div></Panel></div></>; }

function SettingsPage({ theme, setTheme, health, notifications, setNotifications, compact, setCompact, onClearHistory, reset }) { return <><Heading eyebrow="WORKSPACE / PREFERENCES" title="Settings" description="Local display preferences and service information." /><Panel title="Preferences"><div className="setting"><div><b>Color theme</b><small>Changes are stored in this browser.</small></div><div className="segmented"><button className={theme === 'dark' ? 'selected' : ''} onClick={() => setTheme('dark')}>Dark</button><button className={theme === 'light' ? 'selected' : ''} onClick={() => setTheme('light')}>Light</button></div></div><div className="setting"><div><b>Notifications</b><small>In-app notification feedback.</small></div><button className={`setting-toggle ${notifications ? 'on' : ''}`} role="switch" aria-checked={notifications} onClick={() => setNotifications(!notifications)}><i /></button></div><div className="setting"><div><b>Compact dashboard</b><small>Reduce panel spacing.</small></div><button className={`setting-toggle ${compact ? 'on' : ''}`} role="switch" aria-checked={compact} onClick={() => setCompact(!compact)}><i /></button></div><div className="setting"><div><b>API status</b><small>GET /api/health · complaint and RAG endpoints</small></div><Tag tone={health ? 'green' : 'amber'}>{health ? 'CONNECTED' : 'OFFLINE'}</Tag></div><div className="setting"><div><b>Clear RAG query history</b><small>Preserves complaint and knowledge records.</small></div><button className="button secondary" onClick={onClearHistory}><X size={14} /> Clear history</button></div><div className="setting"><div><b>Reset local preferences</b><small>Database records are not changed.</small></div><button className="button secondary" onClick={reset}><RefreshCw size={15} /> Reset</button></div></Panel></>; }

function IncidentModal({ incident, close }) {
  const [detail, setDetail] = useState(null);
  useEffect(() => {
    api(`/api/complaints/${incident.id}`).then((result) => setDetail(result)).catch(() => setDetail(null));
  }, [incident.id]);
  const rag = detail?.rag_analysis;
  return <div className="modal-scrim" onMouseDown={(e) => e.target === e.currentTarget && close()}><section className="modal"><div className="modal-title"><div><small className="eyebrow">COMPLAINT RECORD</small><h2>Incident #{incident.id}</h2></div><button className="icon-btn" onClick={close} aria-label="Close"><X size={18} /></button></div><div className="modal-fields"><span>Category<b>{incident.category}</b></span><span>Location<b>{incident.location}</b></span><span>Reported severity<b>{incident.severity}</b></span><span>Status<b>{incident.status}</b></span><span>Date<b>{incident.created_at ? new Date(`${incident.created_at.replace(' ', 'T')}Z`).toLocaleString() : 'Not available'}</b></span></div><p className="modal-description">{incident.description}</p>{rag ? <><h3 className="subhead">RAG-based explanation · {rag.mode}</h3><p className="answer-text">{rag.answer}</p><Sources sources={rag.sources} chunks={rag.retrieved_chunks} /></> : <DemoNotice>{detail ? 'No RAG analysis is stored for this complaint.' : 'Loading saved RAG analysis, if available...'}</DemoNotice>}<DemoNotice>Model prediction confidence is shown on the Cybercrime Prediction page when a complaint is submitted.</DemoNotice><button className="button secondary" onClick={close}>Close</button></section></div>;
}

// -- Floating Chatbot --------------------------------------------------------
function FloatingChatbot({ type = 'cyber' }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'bot', text: type === 'cyber'
      ? 'Hi! Ask me about cybercrime, phishing, OTP fraud, ransomware, or how to report a complaint.'
      : 'Hi! I\'m your Safety Assistant. Ask me about emergency steps, recording evidence, sharing location, or what to do if you feel unsafe.' }
  ]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  const send = async (e) => {
    e.preventDefault();
    if (!input.trim() || busy) return;
    const userMsg = input.trim();
    setInput('');
    setMessages((m) => [...m, { role: 'user', text: userMsg }]);
    setBusy(true);
    try {
      const endpoint = type === 'cyber' ? '/api/chat/cyber' : '/api/chat/safety';
      const res = await api(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: userMsg }) });
      setMessages((m) => [...m, { role: 'bot', text: res.answer, source: res.source }]);
    } catch {
      setMessages((m) => [...m, { role: 'bot', text: 'Unable to reach the assistant. Please try again.' }]);
    } finally { setBusy(false); }
  };

  const isSafety = type === 'safety';
  return (
    <div className={`chatbot-wrap ${isSafety ? 'chatbot-safety' : ''}`}>
      {open && (
        <div className="chatbot-panel">
          <div className="chatbot-header">
            <span>{isSafety ? <Heart size={15} /> : <Sparkles size={15} />}</span>
            <b>{isSafety ? 'Safety Assistant' : 'Cyber Assistant'}</b>
            <button className="icon-btn" onClick={() => setOpen(false)} aria-label="Close chat"><X size={15} /></button>
          </div>
          <div className="chatbot-messages">
            {messages.map((m, i) => (
              <div key={i} className={`chat-bubble ${m.role}`}>
                <p>{m.text}</p>
                {m.source && <small>{m.source}</small>}
              </div>
            ))}
            {busy && <div className="chat-bubble bot"><p className="chat-typing"><span/><span/><span/></p></div>}
            <div ref={bottomRef} />
          </div>
          <form className="chatbot-input" onSubmit={send}>
            <input value={input} onChange={(e) => setInput(e.target.value)}
              placeholder={isSafety ? 'Ask about safety...' : 'Ask about cybercrime...'}
              disabled={busy} />
            <button type="submit" disabled={busy || !input.trim()}>
              <ArrowRight size={15} />
            </button>
          </form>
        </div>
      )}
      <button className={`chatbot-bubble ${isSafety ? 'bubble-safety' : ''}`} onClick={() => setOpen(!open)}
        aria-label="Open chat assistant">
        {open ? <X size={20} /> : isSafety ? <Heart size={20} /> : <MessageSquareText size={20} />}
      </button>
    </div>
  );
}

// -- Voice Recorder + Evidence Vault ----------------------------------------
function VoiceRecorder({ onToast }) {
  const [recording, setRecording] = useState(false);
  const [recordings, setRecordings] = useState([]);
  const [timer, setTimer] = useState(0);
  const mediaRef = useRef(null);
  const chunksRef = useRef([]);
  const intervalRef = useRef(null);

  const loadEvidence = async () => {
    try {
      const r = await api('/api/safety/evidence');
      setRecordings(r.data || []);
    } catch { /* offline */ }
  };

  useEffect(() => { loadEvidence(); }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      chunksRef.current = [];
      const mr = new MediaRecorder(stream);
      mr.ondataavailable = (e) => { if (e.data.size > 0) chunksRef.current.push(e.data); };
      mr.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const filename = `evidence_${new Date().toISOString().replace(/[:.]/g, '-')}.webm`;
        const url = URL.createObjectURL(blob);
        const localRec = { id: Date.now(), filename, url, blob, size: blob.size, recorded_at: new Date().toISOString(), local: true };
        setRecordings((r) => [localRec, ...r]);
        try {
          await api('/api/safety/evidence', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename, file_size_bytes: blob.size, mime_type: 'audio/webm', duration_seconds: timer }),
          });
        } catch { /* metadata save failed — recording still available locally */ }
        onToast('Evidence recording saved. Download it to preserve as evidence.');
      };
      mediaRef.current = mr;
      mr.start();
      setRecording(true);
      setTimer(0);
      intervalRef.current = setInterval(() => setTimer((t) => t + 1), 1000);
    } catch {
      onToast('Microphone access denied. Please allow microphone permission.');
    }
  };

  const stopRecording = () => {
    clearInterval(intervalRef.current);
    if (mediaRef.current?.state === 'recording') mediaRef.current.stop();
    setRecording(false);
  };

  const deleteRecording = async (rec) => {
    if (!rec.local && !window.confirm('Delete this evidence record?')) return;
    if (!rec.local) {
      try { await api(`/api/safety/evidence/${rec.id}`, { method: 'DELETE' }); } catch { /* ignore */ }
    }
    setRecordings((r) => r.filter((x) => x.id !== rec.id));
    onToast('Recording deleted.');
  };

  const fmt = (s) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;

  return (
    <section className="safety-panel evidence-panel">
      <div className="safety-panel-heading">
        <div>
          <h2>Evidence Recorder</h2>
          <p>Discreet audio evidence recording.</p>
        </div>
        <Volume2 size={18} />
      </div>

      <div className="evidence-controls">
        {recording ? (
          <div className="recording-active">
            <span className="rec-dot" />
            <span className="rec-timer">{fmt(timer)}</span>
            <button className="alarm-stop" onClick={stopRecording}><Square size={15} /> Stop Recording</button>
          </div>
        ) : (
          <button className="alarm-start" onClick={startRecording}>
            <Volume2 size={15} /> Start Recording
          </button>
        )}
        <small>Recording saved on your device only.</small>
      </div>

      {recordings.length > 0 && (
        <div className="evidence-list">
          <h3>Saved Recordings</h3>
          {recordings.map((rec) => (
            <div key={rec.id} className="evidence-item">
              <div>
                <b>{rec.filename}</b>
                <small>{new Date(rec.recorded_at).toLocaleString()} · {rec.size ? `${(rec.size / 1024).toFixed(1)} KB` : ''}</small>
              </div>
              <div className="evidence-actions">
                {rec.url && (
                  <a href={rec.url} download={rec.filename} className="text-btn">
                    Download
                  </a>
                )}
                {rec.url && <audio src={rec.url} controls style={{ height: 28 }} />}
                <button className="text-btn danger-text" onClick={() => deleteRecording(rec)}>Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

// -- Location Sharing Panel --------------------------------------------------
function LocationSharing({ onToast }) {
  const [location, setLocation] = useState(null);
  const [state, setState] = useState('idle'); // idle | requesting | available | unavailable
  const [shareResult, setShareResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  const getLocation = () => {
    setState('requesting');
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLocation({ latitude: pos.coords.latitude, longitude: pos.coords.longitude, accuracy: pos.coords.accuracy });
        setState('available');
      },
      () => { setState('unavailable'); onToast('Location unavailable. Enable location permission.'); },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  const shareLocation = async () => {
    if (!location) return;
    try {
      const r = await api('/api/safety/share-location', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latitude: location.latitude, longitude: location.longitude, location_accuracy: location.accuracy }),
      });
      setShareResult(r);
      onToast('Location saved. Copy the Maps link and send to trusted contacts.');
    } catch (e) { onToast(`Could not share location: ${e.message}`); }
  };

  const loadHistory = async () => {
    try {
      const r = await api('/api/safety/share-location/history');
      setHistory(r.data || []);
      setShowHistory(true);
    } catch { onToast('History unavailable.'); }
  };

  const copyLink = (url) => {
    navigator.clipboard.writeText(url).then(() => onToast('Maps link copied to clipboard.'));
  };

  return (
    <section className="safety-panel location-panel">
      <div className="safety-panel-heading">
        <div>
          <h2>Live Location Sharing</h2>
          <p>Share your location with contacts.</p>
        </div>
        <MapPin size={18} />
      </div>

      <div className="location-controls">
        {state === 'idle' && (
          <button className="safety-action" onClick={getLocation} style={{ minHeight: 44 }}>
            <LocateFixed size={17} /><span><b>Get My Location</b><small>Requests device GPS permission</small></span>
          </button>
        )}
        {state === 'requesting' && <p className="safety-loading">Requesting location permission...</p>}
        {state === 'unavailable' && (
          <div className="safety-error" role="alert">
            <AlertTriangle size={15} /><span>Location unavailable. Please enable location permission in browser settings.</span>
          </div>
        )}
        {state === 'available' && location && (
          <div className="location-available">
            <div className="location-readout">
              <MapPin size={16} />
              <span>
                <b>{location.latitude.toFixed(5)}, {location.longitude.toFixed(5)}</b>
                <small>Accuracy ±{Math.round(location.accuracy)}m</small>
              </span>
            </div>
            <button className="alarm-start" onClick={shareLocation}>
              <MapPin size={15} /> Share with Contacts
            </button>
          </div>
        )}

        {shareResult && (
          <div className="share-result">
            <p>Location saved. Send this link to your trusted contacts:</p>
            <div className="share-link-row">
              <a href={shareResult.maps_url} target="_blank" rel="noreferrer" className="share-link">
                {shareResult.maps_url}
              </a>
              <button className="text-btn" onClick={() => copyLink(shareResult.maps_url)}>Copy</button>
            </div>
          </div>
        )}

        <button className="text-btn" style={{ marginTop: 8 }} onClick={loadHistory}>
          <Clock3 size={13} /> View share history
        </button>
      </div>

      {showHistory && history.length > 0 && (
        <div className="evidence-list" style={{ marginTop: 12 }}>
          <h3>Recent shares</h3>
          {history.slice(0, 5).map((h) => (
            <div key={h.id} className="evidence-item">
              <div>
                <b>{h.latitude.toFixed(4)}, {h.longitude.toFixed(4)}</b>
                <small>{new Date(h.shared_at + 'Z').toLocaleString()}</small>
              </div>
              <div className="evidence-actions">
                <a href={h.maps_url} target="_blank" rel="noreferrer" className="text-btn">Open</a>
                <button className="text-btn" onClick={() => copyLink(h.maps_url)}>Copy</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

export default App;

function CrimeStatistics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api('/api/ncrb').then((r) => setData(r.data)).catch(() => setData(null)).finally(() => setLoading(false));
  }, []);

  if (loading) return <><Heading eyebrow="REAL-WORLD DATA / NCRB" title="India Cybercrime Statistics" description="Loading official NCRB data..." /></>;
  if (!data) return <><Heading eyebrow="REAL-WORLD DATA / NCRB" title="India Cybercrime Statistics" description="Data unavailable." /></>;

  const trendData = data.yearly_trend.map((y) => ({ year: String(y.year), cases: y.cases }));
  const catData = data.category_distribution.map((c) => ({ name: c.category.replace(' / ', '/'), value: c.cases }));

  return (
    <>
      <Heading
        eyebrow="REAL-WORLD DATA / NCRB INDIA"
        title="India Cybercrime Statistics"
        description="Official data from National Crime Records Bureau (NCRB) Crime in India 2022 Report."
        action={<Tag tone="cyan">SOURCE: NCRB GOV.IN</Tag>}
      />
      <DemoNotice>
        Data sourced from NCRB Crime in India 2022. These are national-level official figures, not from this application's complaint database.
      </DemoNotice>

      <div className="stat-grid" style={{ gridTemplateColumns: 'repeat(4, minmax(0,1fr))' }}>
        <article className="stat"><div><span>Cases in 2022</span><i className="stat-icon coral"><ShieldAlert size={17} /></i></div><strong>65,893</strong><small>NCRB 2022 official count</small></article>
        <article className="stat"><div><span>Financial loss</span><i className="stat-icon amber"><Zap size={17} /></i></div><strong>₹1,805 Cr</strong><small>Total reported loss in 2022</small></article>
        <article className="stat"><div><span>Online fraud share</span><i className="stat-icon cyan"><FileText size={17} /></i></div><strong>64.4%</strong><small>Largest category by cases</small></article>
        <article className="stat"><div><span>Women cyber cases</span><i className="stat-icon violet"><Heart size={17} /></i></div><strong>9,879</strong><small>Cyber crimes against women 2022</small></article>
      </div>

      <div className="two-col">
        <Panel title="Yearly trend (2018–2023)" subtitle="Registered cybercrime cases in India — NCRB">
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={trendData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <defs><linearGradient id="ncrb-fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#f17b98" stopOpacity={0.4} /><stop offset="1" stopColor="#f17b98" stopOpacity={0} /></linearGradient></defs>
              <CartesianGrid stroke="#29394b" strokeDasharray="3 5" vertical={false} />
              <XAxis dataKey="year" tick={{ fill: '#91a1b4', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#91a1b4', fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={(v) => `${(v/1000).toFixed(0)}K`} />
              <Tooltip contentStyle={{ background: '#111c29', border: '1px solid #34465b', borderRadius: 7, color: '#eaf1f8' }} formatter={(v) => [v.toLocaleString(), 'Cases']} />
              <Area dataKey="cases" stroke="#f17b98" strokeWidth={2} fill="url(#ncrb-fill)" />
            </AreaChart>
          </ResponsiveContainer>
        </Panel>

        <Panel title="Crime category distribution (2022)" subtitle="Percentage share by type">
          <Distribution data={catData.slice(0, 6)} />
        </Panel>
      </div>

      <div className="two-col">
        <Panel title="Top 10 states by cases (2022)" subtitle="NCRB Crime in India 2022">
          <div className="table-wrap">
            <table>
              <thead><tr><th>Rank</th><th>State</th><th>Cases</th></tr></thead>
              <tbody>
                {data.state_wise_top10.map((s) => (
                  <tr key={s.state}>
                    <td className="mono">#{s.rank}</td>
                    <td className="strong-cell">{s.state}</td>
                    <td>{s.cases.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>

        <Panel title="Top 10 cities by cases (2022)" subtitle="NCRB Table 7A.5">
          <div className="table-wrap">
            <table>
              <thead><tr><th>City</th><th>Cases</th></tr></thead>
              <tbody>
                {data.city_wise_top10.map((c) => (
                  <tr key={c.city}>
                    <td className="strong-cell">{c.city}</td>
                    <td>{c.cases.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>

      <Panel title="Crimes against women (Cyber) — 2022" subtitle="NCRB Chapter 5: Crimes Against Women">
        <div className="stat-grid" style={{ gridTemplateColumns: 'repeat(3, minmax(0,1fr))', marginBottom: 0 }}>
          <article className="stat"><span>Total cases</span><strong>{data.women_stats.total_cases.toLocaleString()}</strong><small>Women cyber crime 2022</small></article>
          <article className="stat"><span>Cyberbullying/Stalking</span><strong>{data.women_stats.cyber_bullying_stalking.toLocaleString()}</strong><small>Cases registered</small></article>
          <article className="stat"><span>Image morphing</span><strong>{data.women_stats.morphing_of_images.toLocaleString()}</strong><small>Cases registered</small></article>
        </div>
      </Panel>

      <div className="ncrb-source">
        <span>Source: {data.metadata.source}</span>
        <a href={data.metadata.url} target="_blank" rel="noreferrer">Official NCRB Report →</a>
        <span>{data.metadata.disclaimer}</span>
      </div>
    </>
  );
}
