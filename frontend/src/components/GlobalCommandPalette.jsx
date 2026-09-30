import React, { useState, useEffect, useRef } from 'react';
import { Search, Command, ArrowRight, Shield, Zap, FileText, X } from 'lucide-react';

export default function GlobalCommandPalette({
  isOpen,
  onClose,
  onNavigateTab,
  apiBase = '/api/v1'
}) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
      handleSearch('');
    }
  }, [isOpen]);

  const handleSearch = async (q) => {
    setQuery(q);
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/agent/quick-command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q })
      });
      const json = await res.json();
      if (json.status === 'success') {
        setResults(json.results || []);
      }
    } catch (err) {
      console.error("Quick command error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (item) => {
    if (item.tab) {
      onNavigateTab(item.tab);
    } else if (item.action === 'open_freeze') {
      onNavigateTab('moneytrail');
    } else if (item.action === 'open_scan') {
      onNavigateTab('citizen');
    } else if (item.case_id) {
      onNavigateTab('copilot');
    }
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.6)',
      display: 'flex',
      alignItems: 'flex-start',
      justifyContent: 'center',
      paddingTop: '12vh',
      zIndex: 2000
    }} onClick={onClose}>
      <div style={{
        background: '#FFFFFF',
        borderRadius: 14,
        maxWidth: 620,
        width: '92%',
        boxShadow: '0 25px 50px rgba(0,0,0,0.25)',
        border: '2px solid var(--border-color)',
        overflow: 'hidden'
      }} onClick={e => e.stopPropagation()}>
        {/* Search Input Bar */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          padding: '16px 20px',
          borderBottom: '1px solid var(--border-color)',
          background: '#FAF7F2'
        }}>
          <Search size={20} color="var(--primary)" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Type a command, case ID, or investigation tool (Ctrl+K)..."
            value={query}
            onChange={e => handleSearch(e.target.value)}
            style={{
              flex: 1,
              border: 'none',
              background: 'transparent',
              fontSize: '1.05rem',
              outline: 'none',
              fontFamily: 'inherit'
            }}
          />
          <span style={{ fontSize: '0.75rem', background: '#E5E7EB', padding: '2px 8px', borderRadius: 6, fontWeight: 700 }}>
            ESC
          </span>
        </div>

        {/* Results List */}
        <div style={{ maxHeight: 380, overflowY: 'auto', padding: '8px 0' }}>
          {results.map((item, idx) => (
            <div
              key={idx}
              onClick={() => handleSelect(item)}
              style={{
                padding: '12px 20px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                cursor: 'pointer',
                transition: 'background 0.15s'
              }}
              onMouseEnter={e => e.currentTarget.style.background = '#FAF7F2'}
              onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <Zap size={16} color="var(--primary)" />
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-main)' }}>
                    {item.title}
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    {item.category}
                  </div>
                </div>
              </div>
              <ArrowRight size={16} color="var(--text-light)" />
            </div>
          ))}
          {results.length === 0 && !loading && (
            <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              No matching commands or cases found.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
