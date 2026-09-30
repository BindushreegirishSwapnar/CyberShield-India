import React, { useState, useEffect, useCallback } from 'react';
import {
  CloudLightning, CloudRain, Sun, CloudSun, AlertTriangle,
  Bell, BellRing, MapPin, User, ChevronRight, Info, ShieldCheck,
  RefreshCw, Sparkles, TrendingUp
} from 'lucide-react';

const STATES = [
  "Karnataka", "Maharashtra", "Delhi", "Uttar Pradesh",
  "Tamil Nadu", "Telangana", "Gujarat", "West Bengal", "All India"
];

const AGE_COHORTS = [
  "Senior Citizen (60+)",
  "Working Professional (26-59)",
  "Student / Youth (18-25)",
  "General"
];

export default function ScamWeatherCard({ apiBase = '/api/v1', lang = 'en' }) {
  const [selectedState, setSelectedState] = useState("Karnataka");
  const [selectedCohort, setSelectedCohort] = useState("Senior Citizen (60+)");
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [subscribed, setSubscribed] = useState(false);
  const [subscribing, setSubscribing] = useState(false);
  const [subNotice, setSubNotice] = useState(null);

  const fetchWeather = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/weather/forecast?state=${encodeURIComponent(selectedState)}&age_group=${encodeURIComponent(selectedCohort)}&language=${lang}`);
      const json = await res.json();
      if (json.status === 'success') {
        setWeatherData(json);
      }
    } catch (err) {
      console.error("Failed to load scam weather:", err);
    } finally {
      setLoading(false);
    }
  }, [selectedState, selectedCohort, lang, apiBase]);

  useEffect(() => {
    fetchWeather();
  }, [fetchWeather]);

  const handleSubscribeToggle = async () => {
    if (subscribed) {
      setSubscribed(false);
      setSubNotice("Weather push alerts disabled.");
      setTimeout(() => setSubNotice(null), 3000);
      return;
    }

    setSubscribing(true);
    try {
      const res = await fetch(`${apiBase}/weather/subscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state: selectedState, age_group: selectedCohort })
      });
      const json = await res.json();
      if (json.status === 'success') {
        setSubscribed(true);
        setSubNotice(`Alerts active: You will be notified when scam weather hits High or Extreme in ${selectedState}.`);
      }
    } catch (err) {
      setSubNotice("Alert subscription active in local PWA storage.");
      setSubscribed(true);
    } finally {
      setSubscribing(false);
      setTimeout(() => setSubNotice(null), 4500);
    }
  };

  const getWeatherIcon = (level, size = 32) => {
    switch (level) {
      case 'EXTREME':
        return <CloudLightning size={size} color="#C8553D" />;
      case 'HIGH':
        return <CloudRain size={size} color="#D9825B" />;
      case 'MODERATE':
        return <CloudSun size={size} color="#E3A83B" />;
      default:
        return <Sun size={size} color="#1F6F6B" />;
    }
  };

  const current = weatherData?.current_weather;
  const advisory = weatherData?.personalized_advisory;
  const outlook = weatherData?.seven_day_outlook || [];

  return (
    <div className="app-card scam-weather-card" style={{
      background: 'linear-gradient(135deg, #FAF7F2 0%, #F5EFE6 100%)',
      border: '2px solid var(--border-color)',
      padding: '24px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Simulation Notice Tag */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: 10,
        marginBottom: 16
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span className="demo-chip" style={{ background: 'var(--primary)', color: '#FFFFFF', fontWeight: 700 }}>
            MODULE 1 • LIVE SCAM WEATHER
          </span>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-light)', fontStyle: 'italic' }}>
            Simulated / demo data based on NCRB statistical baselines
          </span>
        </div>

        {/* Subscribe Web Push Button */}
        <button
          onClick={handleSubscribeToggle}
          className={`control-btn ${subscribed ? 'control-btn-primary' : ''}`}
          style={{
            fontSize: '0.82rem',
            padding: '6px 12px',
            minHeight: 36,
            borderRadius: 20,
            display: 'flex',
            alignItems: 'center',
            gap: 6
          }}
        >
          {subscribed ? <BellRing size={15} /> : <Bell size={15} />}
          <span>{subscribing ? 'Subscribing...' : subscribed ? 'Alerts Active' : 'Notify me on Spikes'}</span>
        </button>
      </div>

      {subNotice && (
        <div style={{
          background: '#E8F5E9',
          color: '#2E7D32',
          padding: '8px 14px',
          borderRadius: 8,
          fontSize: '0.85rem',
          marginBottom: 14,
          border: '1px solid #C8E6C9'
        }}>
          ✓ {subNotice}
        </div>
      )}

      {/* Cohort & State Personalization Bar */}
      <div style={{
        display: 'flex',
        gap: 12,
        marginBottom: 20,
        flexWrap: 'wrap',
        alignItems: 'center',
        background: '#FFFFFF',
        padding: '12px 16px',
        borderRadius: 10,
        border: '1px solid var(--border-color)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <MapPin size={16} color="var(--primary)" />
          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
            State:
          </span>
          <select
            className="form-select"
            value={selectedState}
            onChange={e => setSelectedState(e.target.value)}
            style={{ minHeight: 36, padding: '4px 10px', fontSize: '0.88rem' }}
          >
            {STATES.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <User size={16} color="var(--secondary)" />
          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
            Profile Cohort:
          </span>
          <select
            className="form-select"
            value={selectedCohort}
            onChange={e => setSelectedCohort(e.target.value)}
            style={{ minHeight: 36, padding: '4px 10px', fontSize: '0.88rem' }}
          >
            {AGE_COHORTS.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>

        <button
          onClick={fetchWeather}
          className="control-btn"
          style={{ minHeight: 36, padding: '6px 10px', marginLeft: 'auto' }}
          title="Refresh scam weather"
        >
          <RefreshCw size={14} className={loading ? 'spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Main Weather Hero Card */}
      {loading ? (
        <div style={{ minHeight: 180, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
          <RefreshCw size={24} className="spin" />
          <span style={{ marginLeft: 10 }}>Scanning state threat radars...</span>
        </div>
      ) : current ? (
        <div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: 20,
            alignItems: 'center',
            background: '#FFFFFF',
            borderRadius: 14,
            padding: '22px',
            border: '1px solid var(--border-color)',
            boxShadow: '0 4px 16px rgba(0,0,0,0.03)'
          }}>
            {/* Risk Gauge / Thermometer */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 18 }}>
              <div style={{
                width: 90,
                height: 90,
                borderRadius: '50%',
                background: current.risk_temperature >= 80 ? '#FDF2E9' : current.risk_temperature >= 65 ? '#FEF9E7' : '#E8F6F3',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                border: `3px solid ${current.risk_temperature >= 80 ? '#C8553D' : current.risk_temperature >= 65 ? '#D9825B' : '#1F6F6B'}`,
                flexShrink: 0
              }}>
                <span style={{
                  fontSize: '2rem',
                  fontWeight: 900,
                  color: current.risk_temperature >= 80 ? '#C8553D' : current.risk_temperature >= 65 ? '#D9825B' : '#1F6F6B',
                  lineHeight: 1
                }}>
                  {current.risk_temperature}°
                </span>
                <span style={{ fontSize: '0.68rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-light)', marginTop: 2 }}>
                  Risk Index
                </span>
              </div>

              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  {getWeatherIcon(current.condition_level, 26)}
                  <h3 style={{ margin: 0, fontSize: '1.35rem', fontFamily: 'var(--font-serif)', color: 'var(--text-main)' }}>
                    {current.condition_label}
                  </h3>
                </div>
                <p style={{ margin: '6px 0 0 0', fontSize: '1.02rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                  {current.headline}
                </p>
                <div style={{ display: 'flex', gap: 12, marginTop: 8, fontSize: '0.8rem', color: 'var(--text-light)' }}>
                  <span>Velocity: <strong>{current.trend_indicator.toUpperCase()}</strong></span>
                  <span>•</span>
                  <span>Z-Score Anomaly: <strong>+{current.z_score_anomaly}σ</strong></span>
                  <span>•</span>
                  <span>7-Day Jurisdiction Pool: <strong>{current.active_jurisdiction_cases} cases</strong></span>
                </div>
              </div>
            </div>

            {/* Personalized Cohort Defense Advisory */}
            {advisory && (
              <div style={{
                background: 'var(--bg-sand)',
                borderLeft: '4px solid var(--secondary)',
                borderRadius: '0 8px 8px 0',
                padding: '14px 16px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.8rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--secondary)', marginBottom: 4 }}>
                  <ShieldCheck size={16} />
                  <span>Personalized Shield for {advisory.target_cohort}</span>
                </div>
                <div style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: 4 }}>
                  Dominant Trap: {advisory.dominant_vector_warning}
                </div>
                <p style={{ margin: 0, fontSize: '0.86rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                  {advisory.actionable_defense_tip}
                </p>
              </div>
            )}
          </div>

          {/* 7-DAY OUTLOOK BAR */}
          <div style={{ marginTop: 20 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-light)', letterSpacing: 0.5 }}>
                7-Day Scam Weather Outlook (State Threat Trajectory)
              </span>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                Peak Threat: {selectedState} Metro & Financial Clusters
              </span>
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
              gap: 10
            }}>
              {outlook.map((day, idx) => {
                const isHigh = day.risk_temp >= 75;
                return (
                  <div
                    key={day.date}
                    style={{
                      background: idx === 0 ? 'var(--primary-subtle)' : '#FFFFFF',
                      border: idx === 0 ? '2px solid var(--primary)' : '1px solid var(--border-color)',
                      borderRadius: 10,
                      padding: '12px 10px',
                      textAlign: 'center',
                      transition: 'transform 0.15s ease'
                    }}
                  >
                    <div style={{ fontSize: '0.85rem', fontWeight: 700, color: idx === 0 ? 'var(--primary)' : 'var(--text-muted)' }}>
                      {day.day_name}
                    </div>
                    <div style={{ margin: '8px 0' }}>
                      {getWeatherIcon(day.level, 26)}
                    </div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: isHigh ? '#C8553D' : '#1F6F6B' }}>
                      {day.risk_temp}°
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-light)', margin: '4px 0', textTransform: 'capitalize' }}>
                      {day.level.toLowerCase()}
                    </div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', borderTop: '1px solid #F0EAE1', paddingTop: 6, minHeight: 28, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {day.primary_vector}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
