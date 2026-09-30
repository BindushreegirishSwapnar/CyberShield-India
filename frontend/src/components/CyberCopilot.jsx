import React, { useState, useEffect, useRef } from 'react';
import {
  MessageSquare, Send, BookOpen, Shield, CheckCircle2,
  ChevronDown, ChevronUp, Sparkles, X, FileText, Pin,
  Cpu, Database, BarChart2, GitCommit, Copy, Check
} from 'lucide-react';
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer
} from 'recharts';

const AGENT_PRESETS = [
  "Show me a pie chart of top scam categories in Maharashtra where amount > 1 lakh",
  "Cross-reference phone +91 9876543210 against threat intelligence",
  "Draft Section 173 BNSS Case Diary for Case #CR-2026-98214",
  "What is the customer liability under RBI rules if reported within 3 days?",
  "How should an IO requisition CDR and IPDR logs under Section 94 BNSS?"
];

const COLORS = ['#1F6F6B', '#D9825B', '#8FB59B', '#C8553D', '#E3A83B', '#5A7D7C'];

export default function CyberCopilot({
  t,
  apiBase = '/api/v1',
  activeCaseContext,
  onClearCaseContext
}) {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'copilot',
      text: "Greetings, Officer. I am CyberShield's Autonomous Agentic Copilot. I execute database queries, cross-reference syndicate threat intel, draft Section 173 BNSS case diaries, and generate real-time BI charts. What investigation task shall I execute?",
      thinking_steps: [],
      timestamp: 'Just now'
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const [pinnedNotice, setPinnedNotice] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  useEffect(() => {
    if (activeCaseContext) {
      const q = `Draft Section 173 BNSS Case Diary for Case #${activeCaseContext.complaint_id} (${activeCaseContext.predicted_category || activeCaseContext.crime_type})`;
      setInputText(q);
    }
  }, [activeCaseContext]);

  const handleSendMessage = async (queryToSend) => {
    const query = (queryToSend || inputText).trim();
    if (!query || loading) return;

    const userMsgId = Date.now();
    const newMsgList = [
      ...messages,
      {
        id: userMsgId,
        sender: 'user',
        text: query,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ];
    setMessages(newMsgList);
    setInputText('');
    setLoading(true);

    try {
      const res = await fetch(`${apiBase}/agent/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: query,
          case_context: activeCaseContext,
          conversation_history: messages.map(m => ({
            role: m.sender === 'user' ? 'user' : 'assistant',
            content: m.text
          }))
        })
      });

      const json = await res.json();
      if (json.status === 'success') {
        const agentMsg = {
          id: Date.now() + 1,
          sender: 'copilot',
          text: json.final_response,
          thinking_steps: json.thinking_steps || [],
          inline_chart: json.inline_chart,
          case_diary: json.case_diary,
          sql_info: json.sql_info,
          timestamp: json.timestamp || 'Just now'
        };
        setMessages([...newMsgList, agentMsg]);
      }
    } catch (err) {
      console.error("Agent chat error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handlePinChart = (chart) => {
    try {
      const saved = JSON.parse(localStorage.getItem('cybershield_pinned_charts') || '[]');
      saved.push({ ...chart, pinnedAt: new Date().toISOString() });
      localStorage.setItem('cybershield_pinned_charts', JSON.stringify(saved));
      setPinnedNotice(`Pinned "${chart.title}" to PowerBI Studio!`);
      setTimeout(() => setPinnedNotice(null), 3000);
    } catch (e) {
      console.warn("Pin error:", e);
    }
  };

  const handleCopyText = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 170px)', minHeight: 650 }}>
      {/* Simulation / Demo Environment Warning Tag */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: 12,
        marginBottom: 14
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span className="demo-chip" style={{ background: '#1F6F6B', color: '#FFFFFF', fontWeight: 700 }}>
            MODULE 6 • AGENTIC COPILOT &amp; ASK YOUR DATA
          </span>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-light)', fontStyle: 'italic' }}>
            Autonomous multi-tool agent with transparent reasoning &amp; inline chart generation
          </span>
        </div>

        {activeCaseContext && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            background: 'var(--bg-sand)',
            padding: '4px 12px',
            borderRadius: 20,
            fontSize: '0.85rem'
          }}>
            <span>Active Case: <strong>#{activeCaseContext.complaint_id}</strong></span>
            <button onClick={onClearCaseContext} style={{ border: 'none', background: 'transparent', cursor: 'pointer' }}>
              <X size={14} />
            </button>
          </div>
        )}
      </div>

      {pinnedNotice && (
        <div style={{ background: '#DCFCE7', color: '#166534', padding: '8px 16px', borderRadius: 8, marginBottom: 12, fontSize: '0.85rem', fontWeight: 600 }}>
          📌 {pinnedNotice}
        </div>
      )}

      {/* Main Conversation Stream */}
      <div className="app-card" style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        padding: 0,
        background: '#FAF7F2',
        border: '2px solid var(--border-color)'
      }}>
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: 20 }}>
          {messages.map(m => (
            <div key={m.id} style={{ display: 'flex', justifyContent: m.sender === 'user' ? 'flex-end' : 'flex-start' }}>
              <div style={{
                maxWidth: m.sender === 'user' ? '70%' : '88%',
                background: m.sender === 'user' ? '#1F6F6B' : '#FFFFFF',
                color: m.sender === 'user' ? '#FFFFFF' : '#1F2937',
                borderRadius: m.sender === 'user' ? '18px 18px 2px 18px' : '18px 18px 18px 2px',
                padding: '18px 22px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
                border: m.sender === 'copilot' ? '1px solid var(--border-color)' : 'none'
              }}>
                {/* Copilot Header Badge */}
                {m.sender === 'copilot' && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                    <div style={{ width: 26, height: 26, borderRadius: '50%', background: '#E8F6F3', color: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Sparkles size={15} />
                    </div>
                    <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--primary)' }}>
                      AGENTIC COPILOT
                    </span>
                  </div>
                )}

                {/* Collapsible Transparent Thinking Process */}
                {m.thinking_steps && m.thinking_steps.length > 0 && (
                  <details style={{
                    background: '#FAF7F2',
                    border: '1px solid var(--border-color)',
                    borderRadius: 8,
                    padding: '10px 14px',
                    marginBottom: 14,
                    fontSize: '0.82rem'
                  }}>
                    <summary style={{ cursor: 'pointer', fontWeight: 700, color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: 6 }}>
                      <Cpu size={14} />
                      <span>Thinking Process &amp; Tool Invocations ({m.thinking_steps.length} steps)</span>
                    </summary>
                    <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 8 }}>
                      {m.thinking_steps.map((st, i) => (
                        <div key={i} style={{ borderLeft: '2px solid var(--primary)', paddingLeft: 10 }}>
                          <div style={{ fontWeight: 700, color: 'var(--text-main)' }}>
                            Step {st.step}: <code>{st.tool}</code>
                          </div>
                          <div style={{ color: 'var(--text-muted)', fontSize: '0.78rem' }}>{st.action}</div>
                        </div>
                      ))}
                    </div>
                  </details>
                )}

                {/* Synthesized Natural Language Response */}
                <div style={{ fontSize: '0.96rem', lineHeight: 1.6, whiteSpace: 'pre-line' }}>
                  {m.text}
                </div>

                {/* Inline Recharts Visualization */}
                {m.inline_chart && (
                  <div style={{
                    marginTop: 18,
                    background: '#FAF7F2',
                    border: '1.5px solid var(--border-color)',
                    borderRadius: 12,
                    padding: '18px'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                      <div>
                        <h4 style={{ margin: 0, fontSize: '1.05rem', color: 'var(--primary)' }}>
                          {m.inline_chart.title}
                        </h4>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                          {m.inline_chart.description}
                        </div>
                      </div>

                      <button
                        onClick={() => handlePinChart(m.inline_chart)}
                        className="btn-primary"
                        style={{ padding: '6px 12px', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: 6, borderRadius: 16 }}
                      >
                        <Pin size={14} />
                        <span>Pin to BI Studio</span>
                      </button>
                    </div>

                    <div style={{ width: '100%', height: 260 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        {m.inline_chart.chart_type === 'pie' ? (
                          <PieChart>
                            <Pie
                              data={m.inline_chart.data}
                              dataKey="count"
                              nameKey="name"
                              cx="50%"
                              cy="50%"
                              outerRadius={85}
                              label={entry => `${entry.name}: ${entry.count}`}
                            >
                              {m.inline_chart.data.map((_, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                              ))}
                            </Pie>
                            <Tooltip />
                          </PieChart>
                        ) : (
                          <BarChart data={m.inline_chart.data}>
                            <XAxis dataKey="name" stroke="#888" fontSize={11} interval={0} angle={-15} textAnchor="end" height={50} />
                            <YAxis stroke="#888" fontSize={11} />
                            <Tooltip />
                            <Bar dataKey="count" fill="var(--primary)" radius={[4, 4, 0, 0]} />
                          </BarChart>
                        )}
                      </ResponsiveContainer>
                    </div>
                  </div>
                )}

                {/* Section 173 BNSS Case Diary Preview */}
                {m.case_diary && (
                  <div style={{
                    marginTop: 18,
                    background: '#FAF7F2',
                    border: '1.5px solid var(--border-color)',
                    borderRadius: 12,
                    padding: '16px'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                      <span style={{ fontWeight: 700, fontSize: '0.88rem', color: 'var(--primary)' }}>
                        STATUTORY CASE DIARY (SECTION 173 BNSS)
                      </span>
                      <button
                        onClick={() => handleCopyText(m.id, m.case_diary)}
                        className="control-btn"
                        style={{ padding: '4px 10px', fontSize: '0.78rem', display: 'flex', alignItems: 'center', gap: 6 }}
                      >
                        {copiedId === m.id ? <Check size={14} color="#16A34A" /> : <Copy size={14} />}
                        <span>{copiedId === m.id ? 'Copied' : 'Copy Draft'}</span>
                      </button>
                    </div>
                    <pre style={{
                      margin: 0,
                      background: '#FFFFFF',
                      padding: '14px',
                      borderRadius: 8,
                      border: '1px solid var(--border-color)',
                      fontSize: '0.8rem',
                      fontFamily: 'monospace',
                      overflowX: 'auto',
                      whiteSpace: 'pre-wrap'
                    }}>
                      {m.case_diary}
                    </pre>
                  </div>
                )}

                <div style={{
                  fontSize: '0.72rem',
                  color: m.sender === 'user' ? 'rgba(255,255,255,0.7)' : '#9CA3AF',
                  textAlign: 'right',
                  marginTop: 8
                }}>
                  {m.timestamp}
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              <Cpu size={18} className="spin" />
              <span>Agent decomposing intent and invoking analytical tools...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Agent Presets */}
        <div style={{
          background: '#F5EFE6',
          padding: '10px 18px',
          borderTop: '1px solid var(--border-color)',
          display: 'flex',
          gap: 8,
          overflowX: 'auto',
          alignItems: 'center'
        }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--primary)', whiteSpace: 'nowrap' }}>
            AGENT PROMPTS:
          </span>
          {AGENT_PRESETS.map((preset, idx) => (
            <button
              key={idx}
              onClick={() => handleSendMessage(preset)}
              disabled={loading}
              style={{
                background: '#FFFFFF',
                border: '1px solid var(--border-color)',
                borderRadius: 16,
                padding: '4px 12px',
                fontSize: '0.78rem',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                color: 'var(--text-main)',
                fontWeight: 500
              }}
            >
              💬 {preset}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div style={{
          padding: '16px 20px',
          background: '#FFFFFF',
          borderTop: '1px solid var(--border-color)',
          display: 'flex',
          gap: 12,
          alignItems: 'center'
        }}>
          <input
            type="text"
            className="form-input"
            style={{ flex: 1, minHeight: 46, borderRadius: 24, paddingLeft: 18, fontSize: '0.98rem' }}
            placeholder="Ask your data or request legal drafting (e.g. 'Show me a pie chart of top scam categories in Maharashtra')..."
            value={inputText}
            onChange={e => setInputText(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSendMessage()}
            disabled={loading}
          />

          <button
            onClick={() => handleSendMessage()}
            className="btn-primary"
            style={{ borderRadius: 24, minHeight: 46, padding: '0 24px', display: 'flex', alignItems: 'center', gap: 8 }}
            disabled={loading || !inputText.trim()}
          >
            <span>Run Agent</span>
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
