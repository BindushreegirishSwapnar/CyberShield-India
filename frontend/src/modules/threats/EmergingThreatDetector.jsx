import React, { useState, useEffect } from 'react';
import {
  Sparkles, AlertTriangle, CheckCircle2, RefreshCw,
  TrendingDown, TrendingUp, Cpu, Award, ArrowRight,
  ShieldAlert, Tag, Check, Database, Zap, Layers
} from 'lucide-react';

export default function EmergingThreatDetector({ apiBase = '/api/v1', lang = 'en' }) {
  const [threatData, setThreatData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [approvingId, setApprovingId] = useState(null);
  const [retraining, setRetraining] = useState(false);
  const [retrainSuccess, setRetrainSuccess] = useState(null);

  const fetchClusters = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/threats/clusters`);
      const json = await res.json();
      if (json.status === 'success') {
        setThreatData(json);
      }
    } catch (err) {
      console.error("Failed to load clusters:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClusters();
  }, [apiBase]);

  const handleApproveCategory = async (clusterId) => {
    setApprovingId(clusterId);
    try {
      const res = await fetch(`${apiBase}/threats/approve-category`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cluster_id: clusterId })
      });
      const json = await res.json();
      if (json.status === 'success') {
        fetchClusters();
      }
    } catch (err) {
      console.error("Approval error:", err);
    } finally {
      setApprovingId(null);
    }
  };

  const handleTriggerRetrain = async () => {
    setRetraining(true);
    setRetrainSuccess(null);
    try {
      const res = await fetch(`${apiBase}/threats/retrain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const json = await res.json();
      if (json.status === 'success') {
        setRetrainSuccess(`Retraining Complete: Model baseline accuracy boosted to ${json.new_accuracy_pct}%!`);
        fetchClusters();
      }
    } catch (err) {
      console.error("Retrain error:", err);
    } finally {
      setRetraining(false);
      setTimeout(() => setRetrainSuccess(null), 5000);
    }
  };

  const drift = threatData?.drift_telemetry;
  const clusters = threatData?.clusters || [];

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
            MODULE 5 • EMERGING THREAT DETECTOR
          </span>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-light)', fontStyle: 'italic' }}>
            Simulated unsupervised HDBSCAN clustering &amp; concept drift monitor on 5,000 complaints
          </span>
        </div>

        <button
          onClick={fetchClusters}
          className="control-btn"
          style={{ minHeight: 34, padding: '4px 10px', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: 6 }}
        >
          <RefreshCw size={14} className={loading ? 'spin' : ''} />
          <span>Refresh Clusters</span>
        </button>
      </div>

      {/* Model Drift & Accuracy Decay Monitor */}
      <div className="app-card" style={{
        background: 'linear-gradient(135deg, #FAF7F2 0%, #FFFFFF 100%)',
        border: '2px solid var(--border-color)',
        padding: '24px',
        marginBottom: 24
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 14, marginBottom: 18 }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: 8 }}>
              <TrendingDown size={22} color={drift?.drift_status === 'RETRAINED_STABLE' ? '#16A34A' : '#DC2626'} />
              <span>Model Drift &amp; Classification Confidence Telemetry</span>
            </h3>
            <p style={{ margin: '4px 0 0 0', fontSize: '0.86rem', color: 'var(--text-muted)' }}>
              Tracking classifier accuracy decay as novel cyber extortion slang and vectors emerge in complaints
            </p>
          </div>

          <button
            onClick={handleTriggerRetrain}
            disabled={retraining}
            className="btn-primary"
            style={{
              background: drift?.drift_status === 'RETRAINED_STABLE' ? '#16A34A' : 'var(--primary)',
              borderColor: drift?.drift_status === 'RETRAINED_STABLE' ? '#15803D' : 'var(--primary)',
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              padding: '10px 20px',
              borderRadius: 20
            }}
          >
            <Cpu size={18} className={retraining ? 'spin' : ''} />
            <span>{retraining ? 'Retraining Neural Classifier...' : 'Trigger Model Retraining'}</span>
          </button>
        </div>

        {retrainSuccess && (
          <div style={{ background: '#DCFCE7', borderLeft: '4px solid #16A34A', padding: '12px 16px', borderRadius: 6, marginBottom: 16, color: '#14532D', fontWeight: 600 }}>
            {retrainSuccess}
          </div>
        )}

        {/* Drift Metrics Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: 16,
          marginBottom: 20
        }}>
          <div style={{ background: '#FFFFFF', padding: '16px', borderRadius: 10, border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 700 }}>BASELINE ACCURACY</span>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--primary)' }}>
              {drift?.baseline_accuracy_pct || 93.4}%
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-light)', marginTop: 4 }}>Standard 10-Class Benchmark</div>
          </div>

          <div style={{ background: '#FFFFFF', padding: '16px', borderRadius: 10, border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 700 }}>CURRENT PRODUCTION CONFIDENCE</span>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: drift?.current_accuracy_pct >= 90 ? '#16A34A' : '#DC2626' }}>
              {drift?.current_accuracy_pct || 84.8}%
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-light)', marginTop: 4 }}>
              Decay: <strong>-{drift?.accuracy_decay_pct || 0}%</strong> due to unseen vocabulary
            </div>
          </div>

          <div style={{ background: '#FFFFFF', padding: '16px', borderRadius: 10, border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 700 }}>POPULATION STABILITY INDEX</span>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: drift?.population_stability_index > 0.2 ? '#DC2626' : '#16A34A' }}>
              {drift?.population_stability_index || 0.28}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-light)', marginTop: 4 }}>
              Status: <strong>{drift?.drift_status?.replace(/_/g, ' ')}</strong>
            </div>
          </div>

          <div style={{ background: '#FFFFFF', padding: '16px', borderRadius: 10, border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 700 }}>LAST INCREMENTAL SYNC</span>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', marginTop: 4 }}>
              {drift?.last_retrained_at}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-light)', marginTop: 6 }}>Model Version: 3.5.2-Hotfix</div>
          </div>
        </div>

        {/* Vocabulary Shift Pills */}
        <div>
          <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase' }}>
            Unmapped Emerging Terms Driving Model Drift:
          </div>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            {drift?.vocabulary_shift?.map((v, i) => (
              <div key={i} style={{
                background: '#FEF3C7',
                border: '1px solid #FCD34D',
                padding: '6px 12px',
                borderRadius: 20,
                fontSize: '0.82rem',
                display: 'flex',
                alignItems: 'center',
                gap: 6
              }}>
                <span style={{ fontWeight: 700, color: '#B45309' }}>"{v.term}"</span>
                <span style={{ color: '#DC2626', fontWeight: 800, fontSize: '0.78rem' }}>{v.frequency_increase}</span>
                <span style={{ color: '#78350F', fontSize: '0.72rem', opacity: 0.8 }}>({v.drift_type})</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Discovered Zero-Day Clusters (Unsupervised Discovery) */}
      <div style={{ marginBottom: 16 }}>
        <h3 style={{ margin: '0 0 4px 0', fontSize: '1.3rem', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: 8 }}>
          <Sparkles size={20} color="var(--primary)" />
          <span>Discovered Zero-Day Scam Clusters ({clusters.length} Patterns Found)</span>
        </h3>
        <p style={{ margin: 0, fontSize: '0.88rem', color: 'var(--text-muted)' }}>
          Unsupervised clustering over recent complaint descriptions that do not cleanly match existing taxonomy.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
        {clusters.map((cluster) => (
          <div
            key={cluster.cluster_id}
            className="app-card"
            style={{
              background: '#FFFFFF',
              border: `2px solid ${cluster.status === 'APPROVED' || cluster.status === 'ABSORBED_IN_MODEL' ? '#16A34A' : '#D9825B'}`,
              padding: '24px',
              boxShadow: '0 4px 16px rgba(0,0,0,0.03)'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12, marginBottom: 14 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <span className="badge" style={{
                  background: cluster.status === 'APPROVED' ? '#DCFCE7' : cluster.status === 'ABSORBED_IN_MODEL' ? '#E8F6F3' : '#FEE2E2',
                  color: cluster.status === 'APPROVED' ? '#15803D' : cluster.status === 'ABSORBED_IN_MODEL' ? '#1F6F6B' : '#B91C1C',
                  fontWeight: 800,
                  fontSize: '0.82rem',
                  padding: '6px 12px',
                  borderRadius: 16
                }}>
                  {cluster.cluster_id} • {cluster.weekly_count} COMPLAINTS THIS WEEK
                </span>

                <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  First detected: {cluster.first_detected}
                </span>
              </div>

              {/* Status Badge / Action Button */}
              {cluster.status === 'APPROVED' ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#16A34A', fontWeight: 700, fontSize: '0.9rem' }}>
                  <CheckCircle2 size={18} />
                  <span>Approved as Official Category ({cluster.approved_at})</span>
                </div>
              ) : cluster.status === 'ABSORBED_IN_MODEL' ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--primary)', fontWeight: 700, fontSize: '0.9rem' }}>
                  <Check size={18} />
                  <span>Absorbed into Active Neural Weights</span>
                </div>
              ) : (
                <button
                  onClick={() => handleApproveCategory(cluster.cluster_id)}
                  disabled={approvingId === cluster.cluster_id}
                  className="btn-primary"
                  style={{
                    padding: '8px 18px',
                    borderRadius: 20,
                    fontSize: '0.88rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8
                  }}
                >
                  <Award size={16} />
                  <span>{approvingId === cluster.cluster_id ? 'Promoting...' : 'Approve as New Category'}</span>
                </button>
              )}
            </div>

            <h4 style={{ margin: '0 0 10px 0', fontSize: '1.25rem', color: 'var(--text-main)' }}>
              {cluster.title}
            </h4>

            {/* Keyword Chips */}
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 14 }}>
              {cluster.primary_keywords.map((kw, i) => (
                <span key={i} style={{ background: '#FAF7F2', border: '1px solid var(--border-color)', color: 'var(--text-body)', padding: '4px 10px', borderRadius: 8, fontSize: '0.82rem', fontWeight: 600 }}>
                  🏷️ {kw}
                </span>
              ))}
            </div>

            {/* Complaint Sample Snippet */}
            <div style={{
              background: '#FAF7F2',
              borderLeft: '4px solid var(--primary)',
              padding: '12px 16px',
              borderRadius: 6,
              fontSize: '0.9rem',
              color: 'var(--text-body)',
              fontStyle: 'italic',
              marginBottom: 12
            }}>
              "{cluster.sample_snippet}"
            </div>

            <div style={{ fontSize: '0.84rem', color: 'var(--text-muted)' }}>
              <strong>Recommended Policy Action:</strong> {cluster.recommended_action}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
