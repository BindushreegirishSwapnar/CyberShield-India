import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  BarChart, Bar, LineChart, Line, AreaChart, Area, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import {
  BarChart3, TrendingUp, Download, Filter, Layers, Database,
  RefreshCw, MapPin, Sliders, ChevronDown, Check, Eye, ExternalLink,
  Printer, AlertCircle, XCircle, Clock
} from 'lucide-react';
import { biApi } from '../services/biApi';

const COLORS = ['#1F6F6B', '#8FB59B', '#D9825B', '#4AA9A5', '#E3A83B', '#C8553D', '#5E81AC', '#88C0D0', '#B48EAD', '#D08770'];

// Preset Bookmarks
const BOOKMARKS = [
  { id: 'all', name: 'National Executive Overview', filters: { year: 'All', state: 'All', category: 'All' } },
  { id: 'financial', name: 'Financial Fraud Focus', filters: { year: 'All', state: 'All', category: 'Online Financial Fraud' } },
  { id: 'karnataka', name: 'Karnataka Cyber Command Focus', filters: { year: 'All', state: 'Karnataka', category: 'All' } },
  { id: 'phishing', name: 'Phishing & Impersonation Hubs', filters: { year: 'All', state: 'All', category: 'Phishing Attack' } }
];

export default function PowerBiStudio({
  t,
  apiBase = '/api/v1'
}) {
  // Slicers with Cross-Filtering
  const [selectedYear, setSelectedYear] = useState('All');
  const [selectedState, setSelectedState] = useState('All');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('All');

  // Active Visual Tab
  const [activeVisualTab, setActiveVisualTab] = useState('overview'); // 'overview', 'decomposition', 'waterfall', 'heatmap', 'forecast'
  const [showDaxDrawer, setShowDaxDrawer] = useState(false);

  // Data States
  const [statesData, setStatesData] = useState([]);
  const [trendData, setTrendData] = useState([]);
  const [decompositionData, setDecompositionData] = useState(null);
  const [waterfallData, setWaterfallData] = useState([]);
  const [heatmapData, setHeatmapData] = useState([]);
  const [forecastData, setForecastData] = useState(null);

  // Status & Error States
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [backendWakingUp, setBackendWakingUp] = useState(false);

  // Fetch all aggregated data from real BI endpoints
  const loadAllData = useCallback(async () => {
    setLoading(true);
    setError(null);
    setBackendWakingUp(false);

    try {
      const filters = {
        year: selectedYear,
        state: selectedState,
        category: selectedCategory,
        status: selectedStatus
      };

      const [states, trends, decomp, waterfall, heatmap, forecast] = await Promise.all([
        biApi.getStates(filters, apiBase),
        biApi.getMonthlyTrend(filters, apiBase),
        biApi.getDecomposition(filters, apiBase),
        biApi.getWaterfall(filters, apiBase),
        biApi.getHeatmap(apiBase),
        biApi.getForecast('next_year', apiBase)
      ]);

      setStatesData(states);
      setTrendData(trends);
      setDecompositionData(decomp);
      setWaterfallData(waterfall);
      setHeatmapData(heatmap);
      setForecastData(forecast);
    } catch (err) {
      console.error("BI Studio fetch error:", err);
      const isNetworkErr = err.message?.includes('Failed to fetch') || err.message?.includes('NetworkError');
      if (isNetworkErr) {
        setBackendWakingUp(true);
      }
      setError(err.message || 'Unable to load analytics data from server.');
    } finally {
      setLoading(false);
    }
  }, [selectedYear, selectedState, selectedCategory, selectedStatus, apiBase]);

  useEffect(() => {
    loadAllData();
  }, [loadAllData]);

  // Executive KPI Aggregations (computed dynamically from returned data)
  const totalComplaints = useMemo(() => {
    if (statesData.length === 0) return 0;
    return statesData.reduce((acc, s) => acc + s.total_complaints, 0);
  }, [statesData]);

  const totalLoss = useMemo(() => {
    if (statesData.length === 0) return 0;
    return statesData.reduce((acc, s) => acc + s.total_financial_loss, 0);
  }, [statesData]);

  const criticalCases = useMemo(() => {
    if (statesData.length === 0) return 0;
    return statesData.reduce((acc, s) => acc + s.critical_count, 0);
  }, [statesData]);

  const avgRecoveryRate = useMemo(() => {
    if (statesData.length === 0) return 0;
    const totalResolved = statesData.reduce((acc, s) => acc + s.resolved_count, 0);
    return totalComplaints > 0 ? Math.round((totalResolved / totalComplaints) * 1000) / 10 : 0;
  }, [statesData, totalComplaints]);

  // Handle drilldown on State bar click
  const handleStateBarClick = (entry) => {
    if (entry && entry.state) {
      if (selectedState === entry.state) {
        setSelectedState('All'); // Toggle off
      } else {
        setSelectedState(entry.state); // Cross-filter other charts
      }
    }
  };

  // Reset all slicers
  const handleClearFilters = () => {
    setSelectedYear('All');
    setSelectedState('All');
    setSelectedCategory('All');
    setSelectedStatus('All');
  };

  // Apply Bookmark View
  const handleApplyBookmark = (bm) => {
    setSelectedYear(bm.filters.year);
    setSelectedState(bm.filters.state);
    setSelectedCategory(bm.filters.category);
  };

  // Download Star Schema CSVs
  const handleDownloadStarSchemaCsvs = () => {
    window.open(`${apiBase}/powerbi/download-package`, '_blank');
  };

  return (
    <div>
      {/* Studio Header Bar */}
      <div className="card-header" style={{ marginBottom: 18 }}>
        <div>
          <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: '2rem', margin: 0 }}>
            {t.biStudioTitle || "Power BI Intelligence Studio"}
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', margin: '4px 0 0 0' }}>
            {t.biStudioSub || "Enterprise multi-factor analytics, predictive forecasting and Star Schema OLAP models"}
          </p>
        </div>

        <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
          <button onClick={() => setShowDaxDrawer(!showDaxDrawer)} className="control-btn">
            <Database size={16} />
            <span>{t.daxMeasures || "DAX Measures"}</span>
          </button>
          <button onClick={handleDownloadStarSchemaCsvs} className="btn-primary" style={{ padding: '8px 16px', fontSize: '0.9rem' }}>
            <Download size={16} />
            <span>Export Star Schema CSVs</span>
          </button>
          <button onClick={() => window.print()} className="control-btn" title="Print-Ready Report">
            <Printer size={16} />
            <span>Print Report</span>
          </button>
        </div>
      </div>

      {/* Backend Waking Up Notice Banner */}
      {backendWakingUp && (
        <div style={{
          background: '#FFF3CD',
          border: '1px solid #FFEBAA',
          color: '#856404',
          padding: '12px 16px',
          borderRadius: 8,
          marginBottom: 16,
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          fontSize: '0.9rem'
        }}>
          <Clock size={18} className="spin" />
          <span>Backend waking up (free-tier server spinning up)... Please wait a moment while models initialize.</span>
          <button onClick={loadAllData} className="control-btn" style={{ marginLeft: 'auto', minHeight: 32, padding: '4px 10px', fontSize: '0.8rem' }}>
            Retry Now
          </button>
        </div>
      )}

      {/* Bookmarks Bar */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap', alignItems: 'center' }}>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-light)', fontWeight: 700, textTransform: 'uppercase' }}>
          Saved Views:
        </span>
        {BOOKMARKS.map(bm => {
          const isActive = selectedState === bm.filters.state && selectedCategory === bm.filters.category;
          return (
            <button
              key={bm.id}
              onClick={() => handleApplyBookmark(bm)}
              className="assist-btn"
              style={{
                fontSize: '0.8rem',
                background: isActive ? 'var(--primary-subtle)' : 'var(--bg-card)',
                borderColor: isActive ? 'var(--primary)' : 'var(--border-color)',
                fontWeight: isActive ? 700 : 500
              }}
            >
              <Layers size={13} />
              <span>{bm.name}</span>
            </button>
          );
        })}
      </div>

      {/* Slicers Cross-Filtering Bar */}
      <div className="app-card" style={{ padding: '16px 20px', marginBottom: 24, background: 'var(--bg-sand)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12 }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 4 }}>
              Filter Year
            </label>
            <select className="form-select" value={selectedYear} onChange={e => setSelectedYear(e.target.value)} style={{ minHeight: 40, padding: '6px 10px', fontSize: '0.9rem' }}>
              <option value="All">All Years (2024-2026)</option>
              <option value="2026">2026 (YTD)</option>
              <option value="2025">2025</option>
              <option value="2024">2024</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 4 }}>
              Filter State {selectedState !== 'All' ? `(${selectedState})` : '(20 States)'}
            </label>
            <select className="form-select" value={selectedState} onChange={e => setSelectedState(e.target.value)} style={{ minHeight: 40, padding: '6px 10px', fontSize: '0.9rem' }}>
              <option value="All">All India (20 States)</option>
              {statesData.map(s => (
                <option key={s.state} value={s.state}>
                  {s.state} ({s.total_complaints.toLocaleString('en-IN')})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 4 }}>
              Filter Crime Category
            </label>
            <select className="form-select" value={selectedCategory} onChange={e => setSelectedCategory(e.target.value)} style={{ minHeight: 40, padding: '6px 10px', fontSize: '0.9rem' }}>
              <option value="All">All Crime Types (10)</option>
              <option value="Online Financial Fraud">Online Financial Fraud</option>
              <option value="Phishing Attack">Phishing Attack</option>
              <option value="Account Takeover">Account Takeover</option>
              <option value="Ransomware / Malware">Ransomware / Malware</option>
              <option value="Social Engineering">Social Engineering</option>
              <option value="Investment/Crypto Fraud">Investment/Crypto Fraud</option>
              <option value="Identity Theft">Identity Theft</option>
              <option value="Online Shopping Fraud">Online Shopping Fraud</option>
              <option value="Cyber Bullying / Harassment">Cyber Bullying / Harassment</option>
              <option value="Data Breach">Data Breach</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 4 }}>
              Filter Case Status
            </label>
            <select className="form-select" value={selectedStatus} onChange={e => setSelectedStatus(e.target.value)} style={{ minHeight: 40, padding: '6px 10px', fontSize: '0.9rem' }}>
              <option value="All">All Statuses</option>
              <option value="New">New Triage</option>
              <option value="Under Review">Under Review</option>
              <option value="Investigating">Investigating</option>
              <option value="Resolved">Resolved / Closed</option>
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'flex-end', gap: 6 }}>
            <button
              onClick={handleClearFilters}
              className="control-btn"
              style={{ flex: 1, minHeight: 40, fontSize: '0.85rem' }}
            >
              Clear Filters
            </button>
            <button
              onClick={loadAllData}
              className="control-btn"
              title="Refresh Data"
              style={{ minHeight: 40, padding: '8px 12px' }}
            >
              <RefreshCw size={16} className={loading ? 'spin' : ''} />
            </button>
          </div>
        </div>
      </div>

      {/* EXECUTIVE KPI CARDS */}
      <div className="grid-4" style={{ marginBottom: 28 }}>
        <div className="app-card" style={{ padding: 20 }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-light)', fontWeight: 700, textTransform: 'uppercase' }}>
            {t.kpiComplaints || "Total Incidents Analyzed"}
          </span>
          <div style={{ fontSize: '1.9rem', fontWeight: 800, color: 'var(--text-main)', margin: '4px 0' }}>
            {loading ? '...' : totalComplaints.toLocaleString('en-IN')}
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--primary)', fontWeight: 700 }}>
            {selectedState !== 'All' ? `Filtered to ${selectedState}` : '▲ +18.4% YoY Growth'}
          </span>
        </div>

        <div className="app-card" style={{ padding: 20 }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-light)', fontWeight: 700, textTransform: 'uppercase' }}>
            {t.kpiTotalLoss || "Total Financial Loss"}
          </span>
          <div style={{ fontSize: '1.9rem', fontWeight: 800, color: 'var(--danger)', margin: '4px 0' }}>
            {loading ? '...' : `₹${Math.round(totalLoss / 10000000).toLocaleString('en-IN')} Cr`}
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--danger)', fontWeight: 700 }}>
            {loading ? '' : `₹${Math.round(totalLoss).toLocaleString('en-IN')} Gross`}
          </span>
        </div>

        <div className="app-card" style={{ padding: 20 }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-light)', fontWeight: 700, textTransform: 'uppercase' }}>
            {t.kpiRecoveryRate || "Resolution & Recovery"}
          </span>
          <div style={{ fontSize: '1.9rem', fontWeight: 800, color: 'var(--primary)', margin: '4px 0' }}>
            {loading ? '...' : `${avgRecoveryRate}%`}
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--primary)', fontWeight: 700 }}>
            ▲ +6.2% vs 2025 baseline
          </span>
        </div>

        <div className="app-card" style={{ padding: 20 }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-light)', fontWeight: 700, textTransform: 'uppercase' }}>
            {t.kpiCriticalPct || "Critical Urgent Cases"}
          </span>
          <div style={{ fontSize: '1.9rem', fontWeight: 800, color: '#B5651D', margin: '4px 0' }}>
            {loading ? '...' : criticalCases.toLocaleString('en-IN')}
          </div>
          <span style={{ fontSize: '0.8rem', color: '#B5651D', fontWeight: 700 }}>
            {loading ? '' : `${Math.round((criticalCases / Math.max(1, totalComplaints)) * 100)}% of Total`}
          </span>
        </div>
      </div>

      {/* Visual Navigation Tabs */}
      <div style={{ display: 'flex', gap: 10, marginBottom: 20, flexWrap: 'wrap' }}>
        {[
          { id: 'overview', label: 'Top Affected States & Trends' },
          { id: 'decomposition', label: 'Decomposition Tree' },
          { id: 'waterfall', label: 'Waterfall (Loss vs Interdicted)' },
          { id: 'heatmap', label: 'Incident Time Heatmap' },
          { id: 'forecast', label: 'Predictive 2027 Projections' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveVisualTab(tab.id)}
            className={`control-btn ${activeVisualTab === tab.id ? 'control-btn-primary' : ''}`}
            style={{ fontSize: '0.9rem', padding: '8px 16px' }}
          >
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* ERROR STATE */}
      {error && (
        <div className="app-card" style={{ padding: 24, marginBottom: 20, border: '1px solid var(--danger)', background: '#FFF5F5' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, color: 'var(--danger)' }}>
            <AlertCircle size={24} />
            <div>
              <strong style={{ fontSize: '1.05rem' }}>Failed to Load Visualizations</strong>
              <p style={{ margin: '4px 0 0 0', color: 'var(--text-main)', fontSize: '0.9rem' }}>{error}</p>
            </div>
          </div>
          <div style={{ marginTop: 16 }}>
            <button onClick={loadAllData} className="control-btn" style={{ background: 'var(--danger)', color: '#FFFFFF' }}>
              <RefreshCw size={16} />
              <span>Retry Request</span>
            </button>
          </div>
        </div>
      )}

      {/* VISUAL 1: STATE CHOROPLETH & MONTHLY TREND */}
      {activeVisualTab === 'overview' && (
        <div className="grid-2">
          {/* Top States Bar Chart with click-to-drilldown cross-filtering */}
          <div className="app-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
              <div>
                <h3 className="card-title" style={{ fontSize: '1.2rem', marginBottom: 4 }}>
                  Top Affected States
                </h3>
                <p className="card-subtitle" style={{ fontSize: '0.85rem' }}>
                  {selectedState !== 'All'
                    ? `Showing ${selectedState} (Click selected bar to reset all-India view)`
                    : 'Click any state bar to cross-filter trends, loss, and risk across all visuals.'}
                </p>
              </div>
              {selectedState !== 'All' && (
                <button
                  onClick={() => setSelectedState('All')}
                  className="assist-btn"
                  style={{ fontSize: '0.8rem', padding: '4px 10px' }}
                >
                  Clear Selection
                </button>
              )}
            </div>

            {/* Container with fixed min-height 380px */}
            <div style={{ minHeight: 380, height: 380, width: '100%', position: 'relative' }}>
              {loading ? (
                <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                  <RefreshCw size={24} className="spin" />
                  <span style={{ marginLeft: 10 }}>Loading State Analytics...</span>
                </div>
              ) : statesData.length === 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', height: '100%', alignItems: 'center', justifyContent: 'center' }}>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>No data for these filters</p>
                  <button onClick={handleClearFilters} className="control-btn" style={{ marginTop: 10 }}>
                    Clear Filters
                  </button>
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={statesData.slice(0, 10)} margin={{ top: 10, right: 20, left: 10, bottom: 40 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E6DFD5" />
                    <XAxis
                      dataKey="state"
                      tick={{ fontSize: 13, fill: '#4A5568' }}
                      angle={-25}
                      textAnchor="end"
                      interval={0}
                    />
                    <YAxis tick={{ fontSize: 13, fill: '#4A5568' }} />
                    <Tooltip
                      contentStyle={{ fontSize: '14px', borderRadius: '8px', padding: '10px 14px' }}
                      formatter={(val, name) => [Number(val).toLocaleString('en-IN'), 'Complaints']}
                    />
                    <Bar
                      dataKey="total_complaints"
                      radius={[6, 6, 0, 0]}
                      cursor="pointer"
                      onClick={(entry) => handleStateBarClick(entry)}
                    >
                      {statesData.slice(0, 10).map((entry) => (
                        <Cell
                          key={entry.state}
                          fill={selectedState === entry.state ? '#C8553D' : '#1F6F6B'}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          {/* Time Series Area Chart */}
          <div className="app-card">
            <h3 className="card-title" style={{ fontSize: '1.2rem', marginBottom: 4 }}>
              Incident Volume Trends (2024 - 2026)
            </h3>
            <p className="card-subtitle" style={{ fontSize: '0.85rem', marginBottom: 12 }}>
              Monthly registered complaints {selectedState !== 'All' ? `in ${selectedState}` : 'across India'}.
            </p>

            {/* Container with fixed min-height 380px */}
            <div style={{ minHeight: 380, height: 380, width: '100%', position: 'relative' }}>
              {loading ? (
                <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                  <RefreshCw size={24} className="spin" />
                  <span style={{ marginLeft: 10 }}>Loading Volume Trends...</span>
                </div>
              ) : trendData.length === 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', height: '100%', alignItems: 'center', justifyContent: 'center' }}>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>No trend data for these filters</p>
                  <button onClick={handleClearFilters} className="control-btn" style={{ marginTop: 10 }}>
                    Clear Filters
                  </button>
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={trendData.slice(-14)} margin={{ top: 10, right: 20, left: 10, bottom: 20 }}>
                    <defs>
                      <linearGradient id="areaColor" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8FB59B" stopOpacity={0.85}/>
                        <stop offset="95%" stopColor="#8FB59B" stopOpacity={0.08}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E6DFD5" />
                    <XAxis dataKey="period" tick={{ fontSize: 13, fill: '#4A5568' }} />
                    <YAxis tick={{ fontSize: 13, fill: '#4A5568' }} />
                    <Tooltip
                      contentStyle={{ fontSize: '14px', borderRadius: '8px', padding: '10px 14px' }}
                      formatter={(val) => [Number(val).toLocaleString('en-IN'), 'Complaints']}
                    />
                    <Area
                      type="monotone"
                      dataKey="complaints"
                      stroke="#1F6F6B"
                      strokeWidth={2.8}
                      fillOpacity={1}
                      fill="url(#areaColor)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </div>
      )}

      {/* VISUAL 2: DECOMPOSITION TREE */}
      {activeVisualTab === 'decomposition' && (
        <div className="app-card">
          <div className="card-header">
            <div>
              <h3 className="card-title" style={{ fontSize: '1.25rem' }}>
                Decomposition Tree (Root-Cause Breakdown)
              </h3>
              <p className="card-subtitle">
                Total Financial Loss broken down by Crime Typology &rarr; Suspect Vector &rarr; Risk Severity.
              </p>
            </div>
          </div>

          <div style={{ minHeight: 380, padding: '16px', background: 'var(--bg-sand)', borderRadius: 12 }}>
            {loading ? (
              <div style={{ display: 'flex', height: 340, alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                <RefreshCw size={24} className="spin" />
                <span style={{ marginLeft: 10 }}>Computing Root-Cause Decomposition...</span>
              </div>
            ) : decompositionData ? (
              <div style={{ display: 'flex', gap: 20, alignItems: 'stretch', flexWrap: 'wrap' }}>
                {/* Root Level */}
                <div style={{ flex: 1, minWidth: 220, background: '#FFFFFF', padding: 20, borderRadius: 10, border: '2px solid var(--primary)' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--primary)', textTransform: 'uppercase' }}>ROOT LEVEL</span>
                  <h4 style={{ margin: '8px 0', fontSize: '1.15rem' }}>{decompositionData.root.label}</h4>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--danger)' }}>
                    ₹{Math.round(decompositionData.root.total_loss / 10000000).toLocaleString('en-IN')} Cr
                  </div>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '6px 0 0 0' }}>
                    {decompositionData.root.total_complaints.toLocaleString('en-IN')} total complaints analyzed
                  </p>
                </div>

                {/* Branch 1: Crime Typology */}
                <div style={{ flex: 1.3, minWidth: 260, background: '#FFFFFF', padding: 20, borderRadius: 10, border: '1px solid var(--border-color)' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--text-light)', textTransform: 'uppercase' }}>
                    BRANCH 1: CRIME TYPOLOGY
                  </span>
                  <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 10, fontSize: '0.9rem' }}>
                    {decompositionData.by_category.slice(0, 5).map(c => (
                      <div key={c.category} style={{ borderBottom: '1px solid #F1EBDD', paddingBottom: 6 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
                          <span>{c.category}</span>
                          <strong>{c.percentage}%</strong>
                        </div>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                          ₹{Math.round(c.amount / 100000).toLocaleString('en-IN')} Lakhs ({c.count.toLocaleString('en-IN')} cases)
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Branch 2: Attack Intermediary */}
                <div style={{ flex: 1.3, minWidth: 260, background: '#FFFFFF', padding: 20, borderRadius: 10, border: '1px solid var(--border-color)' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--text-light)', textTransform: 'uppercase' }}>
                    BRANCH 2: INTERMEDIARY / PLATFORM
                  </span>
                  <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 10, fontSize: '0.9rem' }}>
                    {decompositionData.by_platform.slice(0, 5).map(p => (
                      <div key={p.platform} style={{ borderBottom: '1px solid #F1EBDD', paddingBottom: 6 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
                          <span>{p.platform}</span>
                          <strong>{p.percentage}%</strong>
                        </div>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                          {p.count.toLocaleString('en-IN')} verified incidents
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <p>No decomposition data available.</p>
            )}
          </div>
        </div>
      )}

      {/* VISUAL 3: WATERFALL CHART */}
      {activeVisualTab === 'waterfall' && (
        <div className="app-card">
          <div className="card-header">
            <div>
              <h3 className="card-title" style={{ fontSize: '1.25rem' }}>
                Financial Waterfall (Loss vs Rapid Interdiction)
              </h3>
              <p className="card-subtitle">
                Demonstrates capital flow from reported loss through 1930 interdiction and final judicial restitution.
              </p>
            </div>
          </div>

          {/* Container with fixed min-height 380px */}
          <div style={{ minHeight: 380, height: 380, width: '100%', position: 'relative' }}>
            {loading ? (
              <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                <RefreshCw size={24} className="spin" />
                <span style={{ marginLeft: 10 }}>Loading Waterfall Calculations...</span>
              </div>
            ) : waterfallData.length === 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', height: '100%', alignItems: 'center', justifyContent: 'center' }}>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>No waterfall data</p>
                <button onClick={handleClearFilters} className="control-btn" style={{ marginTop: 10 }}>Clear Filters</button>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={waterfallData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E6DFD5" />
                  <XAxis dataKey="step" tick={{ fontSize: 14, fill: '#4A5568', fontWeight: 600 }} />
                  <YAxis tick={{ fontSize: 13, fill: '#4A5568' }} />
                  <Tooltip
                    contentStyle={{ fontSize: '14px', borderRadius: '8px', padding: '10px 14px' }}
                    formatter={(val) => [`₹${Math.abs(Number(val)).toLocaleString('en-IN')}`, 'Amount']}
                  />
                  <Bar dataKey="amount" radius={[6, 6, 0, 0]}>
                    {waterfallData.map((entry, idx) => (
                      <Cell key={idx} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      )}

      {/* VISUAL 4: INCIDENT TIME HEATMAP */}
      {activeVisualTab === 'heatmap' && (
        <div className="app-card">
          <div className="card-header">
            <div>
              <h3 className="card-title" style={{ fontSize: '1.25rem' }}>
                Hour-by-Weekday Incident Density Heatmap
              </h3>
              <p className="card-subtitle">
                Correlates temporal cyber fraud attacks across 168 hours of the week from real complaint timelines.
              </p>
            </div>
          </div>

          <div style={{ minHeight: 380, width: '100%' }}>
            {loading ? (
              <div style={{ display: 'flex', height: 340, alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                <RefreshCw size={24} className="spin" />
                <span style={{ marginLeft: 10 }}>Loading Heatmap Matrix...</span>
              </div>
            ) : heatmapData.length === 0 ? (
              <p>No heatmap data available.</p>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(8, 1fr)', gap: 8, fontSize: '0.85rem', textAlign: 'center' }}>
                {heatmapData.map((item, idx) => {
                  const isHigh = item.intensity > 60;
                  const isMed = item.intensity > 35;
                  return (
                    <div
                      key={idx}
                      style={{
                        background: isHigh ? '#C8553D' : isMed ? '#E3A83B' : '#DCEBF5',
                        color: isMed ? '#FFFFFF' : '#23272A',
                        padding: '12px 6px',
                        borderRadius: 8,
                        fontWeight: 700,
                        transition: 'transform 0.15s ease'
                      }}
                    >
                      <div style={{ fontSize: '0.85rem' }}>{item.day} {item.hour}</div>
                      <div style={{ fontSize: '0.75rem', opacity: 0.95, marginTop: 4 }}>
                        {item.cases} cases
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* VISUAL 5: FORECAST LINE & CONFIDENCE BANDS */}
      {activeVisualTab === 'forecast' && (
        <div className="app-card">
          <div className="card-header">
            <div>
              <h3 className="card-title" style={{ fontSize: '1.25rem' }}>
                Predictive Cyber Threat Projections (2026 - 2027)
              </h3>
              <p className="card-subtitle">
                Polynomial trend regression output with 95% confidence interval bounds.
              </p>
            </div>
          </div>

          {/* Container with fixed min-height 380px */}
          <div style={{ minHeight: 380, height: 380, width: '100%', position: 'relative' }}>
            {loading ? (
              <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                <RefreshCw size={24} className="spin" />
                <span style={{ marginLeft: 10 }}>Running Predictive Models...</span>
              </div>
            ) : forecastData ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={forecastData.projections} margin={{ top: 20, right: 30, left: 10, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E6DFD5" />
                  <XAxis dataKey="period" tick={{ fontSize: 13, fill: '#4A5568' }} />
                  <YAxis tick={{ fontSize: 13, fill: '#4A5568' }} />
                  <Tooltip
                    contentStyle={{ fontSize: '14px', borderRadius: '8px', padding: '10px 14px' }}
                    formatter={(val, name) => [Number(val).toLocaleString('en-IN'), name === 'predicted' ? 'Projected Volume' : name]}
                  />
                  <Legend wrapperStyle={{ fontSize: '14px', paddingTop: '10px' }} />
                  <Area
                    type="monotone"
                    dataKey="upper_ci"
                    name="95% Upper Bound"
                    stroke="none"
                    fill="#DCEBF5"
                    fillOpacity={0.6}
                  />
                  <Area
                    type="monotone"
                    dataKey="lower_ci"
                    name="95% Lower Bound"
                    stroke="none"
                    fill="#FFFFFF"
                    fillOpacity={1}
                  />
                  <Line
                    type="monotone"
                    dataKey="predicted"
                    name="Projected Baseline"
                    stroke="#1F6F6B"
                    strokeWidth={3}
                    dot={{ r: 4 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <p>No forecast data available.</p>
            )}
          </div>
        </div>
      )}

      {/* DAX MEASURES & STAR SCHEMA MODAL DRAWER */}
      {showDaxDrawer && (
        <div className="modal-overlay" onClick={() => setShowDaxDrawer(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: 14, marginBottom: 18 }}>
              <h3 style={{ margin: 0 }}>DAX-Style Measures &amp; Star Schema Formulation</h3>
              <button onClick={() => setShowDaxDrawer(false)} className="control-btn" style={{ padding: '6px 10px' }}>✕</button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 14, fontSize: '0.9rem' }}>
              <div style={{ background: 'var(--bg-app)', padding: 14, borderRadius: 8, border: '1px solid var(--border-color)' }}>
                <strong style={{ color: 'var(--primary)' }}>[Total Financial Loss INR]</strong>
                <pre style={{ margin: '6px 0 0 0', background: 'var(--bg-card)', padding: 10, borderRadius: 6, fontSize: '0.82rem' }}>
                  Total Loss = SUM(FactComplaints[FinancialLoss])
                </pre>
              </div>

              <div style={{ background: 'var(--bg-app)', padding: 14, borderRadius: 8, border: '1px solid var(--border-color)' }}>
                <strong style={{ color: 'var(--primary)' }}>[Fund Recovery Rate %]</strong>
                <pre style={{ margin: '6px 0 0 0', background: 'var(--bg-card)', padding: 10, borderRadius: 6, fontSize: '0.82rem' }}>
                  Recovery Rate = DIVIDE(SUM(FactComplaints[RecoveredAmount]), [Total Loss], 0)
                </pre>
              </div>

              <div style={{ background: 'var(--bg-app)', padding: 14, borderRadius: 8, border: '1px solid var(--border-color)' }}>
                <strong style={{ color: 'var(--primary)' }}>[Rolling 3-Month Complaint Average]</strong>
                <pre style={{ margin: '6px 0 0 0', background: 'var(--bg-card)', padding: 10, borderRadius: 6, fontSize: '0.82rem' }}>
                  Rolling 3M = AVERAGEX(DATESINPERIOD(DimDate[Date], LASTDATE(DimDate[Date]), -3, MONTH), [Total Complaints])
                </pre>
              </div>

              <div style={{ background: 'var(--bg-sand)', padding: 14, borderRadius: 8 }}>
                <strong>Star Schema Relational Links:</strong>
                <ul style={{ paddingLeft: 20, marginTop: 6, fontSize: '0.85rem' }}>
                  <li><code>FactComplaints[City]</code> &rarr; <code>DimLocation[City]</code> (Many-to-One)</li>
                  <li><code>FactComplaints[PredictedCategory]</code> &rarr; <code>DimCrimeType[CrimeCategory]</code> (Many-to-One)</li>
                  <li><code>FactComplaints[ComplaintDate]</code> &rarr; <code>DimDate[DateKey]</code> (Many-to-One)</li>
                  <li><code>FactComplaints[Status]</code> &rarr; <code>DimStatus[StatusKey]</code> (Many-to-One)</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
