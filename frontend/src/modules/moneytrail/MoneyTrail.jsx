import React, { useState, useEffect } from 'react';
import {
  GitFork, ShieldAlert, Clock, ArrowRight, Download,
  CheckCircle2, AlertTriangle, FileText, Building2,
  Wallet, RefreshCw, Zap, Landmark, Smartphone, DollarSign,
  AlertOctagon, Check
} from 'lucide-react';
import { jsPDF } from 'jspdf';

export default function MoneyTrail({ apiBase = '/api/v1', lang = 'en', activeCaseId = 'CR-2026-98214' }) {
  const [trailData, setTrailData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [minutesElapsed, setMinutesElapsed] = useState(45);
  const [simulationData, setSimulationData] = useState(null);

  // Legal Notice Modal
  const [selectedMule, setSelectedMule] = useState(null);
  const [noticeData, setNoticeData] = useState(null);
  const [generatingNotice, setGeneratingNotice] = useState(false);
  const [showNoticeModal, setShowNoticeModal] = useState(false);

  // Fetch baseline trail
  useEffect(() => {
    async function loadTrail() {
      setLoading(true);
      try {
        const res = await fetch(`${apiBase}/moneytrail/trail/${activeCaseId}`);
        const json = await res.json();
        if (json.status === 'success') {
          setTrailData(json.data);
        }
      } catch (err) {
        console.error("Failed to load money trail:", err);
      } finally {
        setLoading(false);
      }
    }
    loadTrail();
  }, [apiBase, activeCaseId]);

  // Fetch simulation upon slider change
  useEffect(() => {
    async function updateSimulation() {
      try {
        const res = await fetch(`${apiBase}/moneytrail/simulate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            case_id: activeCaseId,
            minutes_elapsed: minutesElapsed
          })
        });
        const json = await res.json();
        if (json.status === 'success') {
          setSimulationData(json.data);
        }
      } catch (err) {
        console.error("Simulation error:", err);
      }
    }
    const t = setTimeout(updateSimulation, 150);
    return () => clearTimeout(t);
  }, [minutesElapsed, apiBase, activeCaseId]);

  // Generate Section 94 BNSS Notice
  const handleOpenNoticeGenerator = async (mule) => {
    setSelectedMule(mule);
    setGeneratingNotice(true);
    setShowNoticeModal(true);

    try {
      const res = await fetch(`${apiBase}/moneytrail/generate-notice`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          case_id: activeCaseId,
          mule_account: mule.account_no,
          bank_name: mule.bank || 'Beneficiary Institution',
          officer_name: 'Inspector Vikram Rathore',
          badge_no: 'MH-CYBER-9912'
        })
      });
      const json = await res.json();
      if (json.status === 'success') {
        setNoticeData(json.data);
      }
    } catch (err) {
      console.error("Notice error:", err);
    } finally {
      setGeneratingNotice(false);
    }
  };

  // Download PDF Notice
  const handleDownloadNoticePdf = () => {
    if (!noticeData) return;
    const doc = new jsPDF();

    doc.setFillColor(250, 247, 242);
    doc.rect(0, 0, 210, 297, 'F');

    // Header strip
    doc.setFillColor(31, 111, 107);
    doc.rect(0, 0, 210, 18, 'F');
    doc.setFont("helvetica", "bold");
    doc.setFontSize(11);
    doc.setTextColor(255, 255, 255);
    doc.text("GOVERNMENT OF INDIA • STATUTORY POLICE REQUISITION", 105, 12, { align: "center" });

    // Body Notice Text
    doc.setFont("courier", "normal");
    doc.setFontSize(9.5);
    doc.setTextColor(20, 20, 20);

    const splitText = doc.splitTextToSize(noticeData.notice_text, 180);
    doc.text(splitText, 15, 32);

    doc.save(`Section94_BNSS_Freeze_Order_${noticeData.order_reference}.pdf`);
  };

  const nodes = trailData?.nodes || [];
  const layer0 = nodes.filter(n => n.layer === 0);
  const layer1 = nodes.filter(n => n.layer === 1);
  const layer2 = nodes.filter(n => n.layer === 2);
  const layer3 = nodes.filter(n => n.layer === 3);

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
            MODULE 4 • MONEY TRAIL &amp; RAPID FREEZE
          </span>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-light)', fontStyle: 'italic' }}>
            Simulated / demo financial transaction dispersion graph based on Section 94 BNSS protocols
          </span>
        </div>

        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Active Investigation: <strong style={{ color: 'var(--text-main)' }}>{activeCaseId}</strong>
        </div>
      </div>

      {/* Golden Hour Time-Elapsed Slider */}
      <div className="app-card" style={{
        background: 'linear-gradient(135deg, #FAF7F2 0%, #FFFFFF 100%)',
        border: '2px solid var(--border-color)',
        padding: '20px 24px',
        marginBottom: 20
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12, marginBottom: 14 }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Clock size={20} color="var(--primary)" />
              <span>What-If Dispersion Simulator (Golden Hour Interdiction)</span>
            </h3>
            <p style={{ margin: '4px 0 0 0', fontSize: '0.86rem', color: 'var(--text-muted)' }}>
              Drag slider to simulate fund dispersion across layers as minutes tick away
            </p>
          </div>

          <div style={{
            background: minutesElapsed <= 60 ? '#E8F6F3' : minutesElapsed <= 120 ? '#FEF3C7' : '#FEE2E2',
            color: minutesElapsed <= 60 ? '#1F6F6B' : minutesElapsed <= 120 ? '#B45309' : '#DC2626',
            padding: '6px 16px',
            borderRadius: 20,
            fontWeight: 800,
            fontSize: '0.95rem',
            border: `1.5px solid ${minutesElapsed <= 60 ? '#1F6F6B' : minutesElapsed <= 120 ? '#F59E0B' : '#EF4444'}`
          }}>
            ⏱️ T+{minutesElapsed} Minutes Elapsed
          </div>
        </div>

        {/* Range Slider */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--primary)' }}>0m (Instant)</span>
          <input
            type="range"
            min="0"
            max="180"
            step="5"
            value={minutesElapsed}
            onChange={e => setMinutesElapsed(Number(e.target.value))}
            style={{ flex: 1, height: 8, cursor: 'pointer', accentColor: 'var(--primary)' }}
          />
          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#DC2626' }}>180m (Exfiltrated)</span>
        </div>

        {/* Simulation Output Metrics */}
        {simulationData && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: 16,
            marginTop: 18,
            padding: '14px',
            background: '#FFFFFF',
            borderRadius: 10,
            border: '1px solid var(--border-color)'
          }}>
            <div>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>PROJECTED RECOVERABLE:</span>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#16A34A' }}>
                ₹{simulationData.recoverable_amount.toLocaleString()} ({simulationData.recoverable_percent}%)
              </div>
            </div>
            <div>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>FUNDS IN LAYER 1 (EASY FREEZE):</span>
              <div style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--primary)' }}>
                ₹{simulationData.layer_distribution.layer_1_balance.toLocaleString()}
              </div>
            </div>
            <div>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>CASHED OUT / EXFILTRATED:</span>
              <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#DC2626' }}>
                ₹{simulationData.layer_distribution.cashed_out.toLocaleString()}
              </div>
            </div>
            <div>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>TACTICAL ACTION:</span>
              <div style={{ fontSize: '0.84rem', fontWeight: 600, color: 'var(--text-main)', marginTop: 2 }}>
                {simulationData.recommendation}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Multi-Hop Flow Visualization (Sankey / Flow Graph) */}
      <div className="app-card" style={{
        background: '#FFFFFF',
        border: '2px solid var(--border-color)',
        padding: '24px',
        marginBottom: 24
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: 8 }}>
            <GitFork size={20} />
            <span>Multi-Hop Flow Architecture (Victim ➔ Layer 1 ➔ Layer 2 ➔ Endpoints)</span>
          </h3>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Real-time interdiction pipeline
          </span>
        </div>

        {/* Directed Flow Columns */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: 16,
          alignItems: 'stretch'
        }}>
          {/* Column 0: Victim Source */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ fontSize: '0.82rem', fontWeight: 800, color: 'var(--primary)', letterSpacing: '0.5px' }}>
              ORIGIN (VICTIM)
            </div>
            {layer0.map(node => (
              <div key={node.id} style={{
                background: '#FAF7F2',
                border: '2px solid var(--primary)',
                borderRadius: 12,
                padding: '16px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                  <Landmark size={18} color="var(--primary)" />
                  <span style={{ fontWeight: 700, fontSize: '0.92rem' }}>{node.label}</span>
                </div>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Holder: {node.holder}</div>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>A/C: {node.account_no}</div>
                <div style={{ marginTop: 10, fontSize: '1.15rem', fontWeight: 800, color: '#DC2626' }}>
                  - ₹{node.amount.toLocaleString()}
                </div>
              </div>
            ))}
          </div>

          {/* Column 1: Layer 1 Mules */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ fontSize: '0.82rem', fontWeight: 800, color: '#D9825B', letterSpacing: '0.5px' }}>
              LAYER 1 (INTERMEDIATE MULES)
            </div>
            {layer1.map(node => (
              <div key={node.id} style={{
                background: '#FFFFFF',
                border: '2px solid #D9825B',
                borderRadius: 12,
                padding: '16px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                  <span style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-main)' }}>{node.bank}</span>
                  <span className="badge" style={{ background: '#FEF3C7', color: '#B45309', fontSize: '0.7rem', fontWeight: 700 }}>
                    FPS: {node.freeze_priority_score}
                  </span>
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Holder: {node.holder}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>A/C: {node.account_no}</div>
                <div style={{ marginTop: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--primary)' }}>
                    ₹{node.current_balance.toLocaleString()}
                  </div>
                  <button
                    onClick={() => handleOpenNoticeGenerator(node)}
                    className="btn-primary"
                    style={{ fontSize: '0.74rem', padding: '4px 10px', minHeight: 30, borderRadius: 14 }}
                  >
                    Freeze Order
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Column 2: Layer 2 Mules */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ fontSize: '0.82rem', fontWeight: 800, color: '#E3A83B', letterSpacing: '0.5px' }}>
              LAYER 2 (DISPERSED POOLS)
            </div>
            {layer2.map(node => (
              <div key={node.id} style={{
                background: '#FFFFFF',
                border: '1.5px solid #FCD34D',
                borderRadius: 12,
                padding: '16px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                  <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>{node.bank}</span>
                  <span className="badge" style={{ background: '#FEF3C7', color: '#B45309', fontSize: '0.7rem', fontWeight: 700 }}>
                    FPS: {node.freeze_priority_score}
                  </span>
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Holder: {node.holder}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>A/C: {node.account_no}</div>
                <div style={{ marginTop: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--primary)' }}>
                    ₹{node.current_balance.toLocaleString()}
                  </div>
                  <button
                    onClick={() => handleOpenNoticeGenerator(node)}
                    className="btn-secondary"
                    style={{ fontSize: '0.74rem', padding: '4px 10px', minHeight: 30, borderRadius: 14 }}
                  >
                    Freeze Order
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Column 3: Cashout / Crypto */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ fontSize: '0.82rem', fontWeight: 800, color: '#DC2626', letterSpacing: '0.5px' }}>
              ENDPOINTS (EXFILTRATION)
            </div>
            {layer3.map(node => (
              <div key={node.id} style={{
                background: '#FEF2F2',
                border: '1.5px solid #FCA5A5',
                borderRadius: 12,
                padding: '16px'
              }}>
                <div style={{ fontWeight: 700, fontSize: '0.9rem', color: '#991B1B', marginBottom: 4 }}>
                  {node.label}
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Endpoint: {node.holder}</div>
                <div style={{ marginTop: 8, fontSize: '1rem', fontWeight: 800, color: '#DC2626' }}>
                  ₹{node.initial_amount.toLocaleString()} Drained
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Freeze Priority Score (FPS) Actionable Leaderboard */}
      <div className="app-card" style={{
        background: '#FFFFFF',
        border: '2px solid var(--border-color)',
        padding: '24px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--primary)' }}>
              Freeze Priority Score (FPS) Interdiction Ranking
            </h3>
            <p style={{ margin: '4px 0 0 0', fontSize: '0.86rem', color: 'var(--text-muted)' }}>
              Prioritized by remaining balance, drain urgency, and jurisdictional interdiction ease
            </p>
          </div>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table className="data-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#FAF7F2', textAlign: 'left', fontSize: '0.85rem' }}>
                <th style={{ padding: '12px' }}>RANK</th>
                <th style={{ padding: '12px' }}>INSTITUTION &amp; BENEFICIARY</th>
                <th style={{ padding: '12px' }}>ACCOUNT NUMBER</th>
                <th style={{ padding: '12px' }}>AT-RISK BALANCE</th>
                <th style={{ padding: '12px' }}>TIME TO DRAIN</th>
                <th style={{ padding: '12px' }}>FREEZE PRIORITY</th>
                <th style={{ padding: '12px' }}>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {trailData?.freeze_priority_ranking?.map((mule, idx) => (
                <tr key={mule.id} style={{ borderBottom: '1px solid var(--border-color)', fontSize: '0.9rem' }}>
                  <td style={{ padding: '12px', fontWeight: 800 }}>#{idx + 1}</td>
                  <td style={{ padding: '12px' }}>
                    <div style={{ fontWeight: 700 }}>{mule.bank}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{mule.holder}</div>
                  </td>
                  <td style={{ padding: '12px', fontFamily: 'monospace', fontWeight: 600 }}>{mule.account_no}</td>
                  <td style={{ padding: '12px', fontWeight: 800, color: '#16A34A' }}>₹{mule.current_balance.toLocaleString()}</td>
                  <td style={{ padding: '12px', color: '#DC2626', fontWeight: 600 }}>~{mule.est_drain_time_mins} mins</td>
                  <td style={{ padding: '12px' }}>
                    <span style={{
                      background: mule.freeze_priority_score >= 90 ? '#FEE2E2' : '#FEF3C7',
                      color: mule.freeze_priority_score >= 90 ? '#DC2626' : '#B45309',
                      padding: '4px 10px',
                      borderRadius: 12,
                      fontWeight: 800,
                      fontSize: '0.82rem'
                    }}>
                      FPS {mule.freeze_priority_score}/100
                    </span>
                  </td>
                  <td style={{ padding: '12px' }}>
                    <button
                      onClick={() => handleOpenNoticeGenerator(mule)}
                      className="btn-primary"
                      style={{ padding: '6px 12px', fontSize: '0.82rem', borderRadius: 8 }}
                    >
                      Issue Sec 94 BNSS Order
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Statutory Section 94 BNSS Notice Modal */}
      {showNoticeModal && (
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
            borderRadius: 14,
            maxWidth: 720,
            width: '100%',
            padding: 28,
            boxShadow: '0 20px 40px rgba(0,0,0,0.2)',
            border: '3px solid var(--primary)',
            maxHeight: '90vh',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.35rem', color: 'var(--primary)' }}>
                  Statutory Bank Freeze Requisition (Sec 94 BNSS)
                </h3>
                <p style={{ margin: '2px 0 0 0', fontSize: '0.84rem', color: 'var(--text-muted)' }}>
                  Legally binding interdiction mandate under Bharatiya Nagarik Suraksha Sanhita 2023
                </p>
              </div>

              <button onClick={() => setShowNoticeModal(false)} className="control-btn">
                ✕ Close
              </button>
            </div>

            {generatingNotice ? (
              <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
                <RefreshCw size={28} className="spin" />
                <div style={{ marginTop: 10 }}>Generating cryptographically sealed requisition...</div>
              </div>
            ) : noticeData && (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                <div style={{
                  flex: 1,
                  overflowY: 'auto',
                  background: '#FAF7F2',
                  padding: '16px',
                  borderRadius: 8,
                  border: '1px solid var(--border-color)',
                  fontFamily: 'monospace',
                  fontSize: '0.82rem',
                  lineHeight: 1.5,
                  whiteSpace: 'pre-wrap',
                  marginBottom: 16
                }}>
                  {noticeData.notice_text}
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    Digital Seal: <code>{noticeData.digital_seal_hash?.slice(0, 24)}...</code>
                  </div>

                  <div style={{ display: 'flex', gap: 10 }}>
                    <button onClick={handleDownloadNoticePdf} className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <Download size={16} />
                      <span>Download Signed Notice (PDF)</span>
                    </button>
                    <button onClick={() => setShowNoticeModal(false)} className="btn-secondary">
                      <span>Done</span>
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
