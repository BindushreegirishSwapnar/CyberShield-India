import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Share2, Shield, Search, ZoomIn, ZoomOut, RefreshCw,
  AlertTriangle, Phone, Globe, CreditCard, Layers, X, ExternalLink,
  Info, Maximize2, AlertCircle
} from 'lucide-react';
import { biApi } from '../services/biApi';

export default function LinkAnalysisGraph({
  t,
  apiBase = '/api/v1',
  onSelectCase
}) {
  const [graphData, setGraphData] = useState({ nodes: [], links: [], clusters: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedCluster, setSelectedCluster] = useState('All');
  const [searchFilter, setSearchFilter] = useState('');
  const [entityFilter, setEntityFilter] = useState('All');

  // DOM Refs
  const containerRef = useRef(null);
  const canvasRef = useRef(null);
  const transformRef = useRef({ x: 0, y: 0, scale: 1 });
  const isDraggingRef = useRef(false);
  const dragStartRef = useRef({ x: 0, y: 0 });
  const simulationTimerRef = useRef(null);

  // Zoom to Fit calculation
  const zoomToFit = useCallback((nodes, width, height) => {
    if (!nodes || nodes.length === 0) return;
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;

    nodes.forEach(n => {
      if (n.x < minX) minX = n.x;
      if (n.x > maxX) maxX = n.x;
      if (n.y < minY) minY = n.y;
      if (n.y > maxY) maxY = n.y;
    });

    const padding = 80;
    const graphWidth = Math.max(100, maxX - minX + padding * 2);
    const graphHeight = Math.max(100, maxY - minY + padding * 2);

    const scaleX = width / graphWidth;
    const scaleY = height / graphHeight;
    const scale = Math.max(0.4, Math.min(1.4, Math.min(scaleX, scaleY)));

    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;

    transformRef.current = {
      x: width / 2 - centerX * scale,
      y: height / 2 - centerY * scale,
      scale: scale
    };
  }, []);

  // Fetch Graph Data from /api/v1/graph/entities
  const fetchGraph = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const filters = {
        cluster_id: selectedCluster,
        type: entityFilter,
        search: searchFilter
      };

      const json = await biApi.getGraphEntities(filters, apiBase);
      const canvas = canvasRef.current;
      const width = canvas ? canvas.width : 1000;
      const height = canvas ? canvas.height : 600;

      // Layout nodes using radial cluster arrangement
      const clusterCenters = {
        1: { x: width * 0.25, y: height * 0.3 },
        2: { x: width * 0.75, y: height * 0.3 },
        3: { x: width * 0.25, y: height * 0.75 },
        4: { x: width * 0.75, y: height * 0.75 },
        5: { x: width * 0.5, y: height * 0.25 },
        6: { x: width * 0.5, y: height * 0.78 },
        0: { x: width * 0.5, y: height * 0.5 }
      };

      const nodes = json.nodes.map((n, i) => {
        const center = clusterCenters[n.cluster_id] || { x: width / 2, y: height / 2 };
        const angle = (i * 1.37) % (2 * Math.PI);
        const spread = n.type === 'complaint' ? 90 + (i % 4) * 20 : 40 + (i % 3) * 15;

        return {
          ...n,
          x: center.x + Math.cos(angle) * spread,
          y: center.y + Math.sin(angle) * spread,
          vx: 0,
          vy: 0,
          radius: n.type === 'complaint' ? 14 : 18
        };
      });

      // Simple physics relaxation (25 iterations)
      for (let iter = 0; iter < 25; iter++) {
        for (let i = 0; i < nodes.length; i++) {
          for (let j = i + 1; j < nodes.length; j++) {
            const dx = nodes[j].x - nodes[i].x;
            const dy = nodes[j].y - nodes[i].y;
            const dist = Math.hypot(dx, dy) || 1;
            const minDist = nodes[i].radius + nodes[j].radius + 35;
            if (dist < minDist) {
              const force = (minDist - dist) / dist * 0.35;
              nodes[i].x -= dx * force;
              nodes[i].y -= dy * force;
              nodes[j].x += dx * force;
              nodes[j].y += dy * force;
            }
          }
        }
      }

      setGraphData({
        nodes,
        links: json.links,
        clusters: json.clusters
      });

      // Fit in view
      zoomToFit(nodes, width, height);

    } catch (err) {
      console.error("Failed to load entity graph:", err);
      setError(err.message || 'Unable to load entity relationship graph.');
    } finally {
      setLoading(false);
    }
  }, [selectedCluster, entityFilter, searchFilter, apiBase, zoomToFit]);

  useEffect(() => {
    fetchGraph();
  }, [fetchGraph]);

  // ResizeObserver to dynamically adjust Canvas dimensions
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleResize = () => {
      const canvas = canvasRef.current;
      if (!canvas || !container) return;
      const rect = container.getBoundingClientRect();
      const newWidth = Math.max(700, Math.floor(rect.width));
      const newHeight = 600;

      if (canvas.width !== newWidth || canvas.height !== newHeight) {
        canvas.width = newWidth;
        canvas.height = newHeight;
        if (graphData.nodes.length > 0) {
          zoomToFit(graphData.nodes, newWidth, newHeight);
        }
      }
    };

    const ro = new ResizeObserver(handleResize);
    ro.observe(container);
    handleResize();

    return () => ro.disconnect();
  }, [graphData.nodes, zoomToFit]);

  // Canvas Render Loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || graphData.nodes.length === 0) return;

    const ctx = canvas.getContext('2d');
    let animationFrameId;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.save();
      ctx.translate(transformRef.current.x, transformRef.current.y);
      ctx.scale(transformRef.current.scale, transformRef.current.scale);

      const nodeMap = new Map(graphData.nodes.map(n => [n.id, n]));

      // 1. Draw Links
      graphData.links.forEach(link => {
        const source = nodeMap.get(link.source);
        const target = nodeMap.get(link.target);
        if (!source || !target) return;

        const isHighlight = selectedNode && (selectedNode.id === source.id || selectedNode.id === target.id);

        ctx.beginPath();
        ctx.moveTo(source.x, source.y);
        ctx.lineTo(target.x, target.y);
        ctx.strokeStyle = isHighlight ? '#C8553D' : '#D5CFC7';
        ctx.lineWidth = isHighlight ? 2.5 : 1.3;
        ctx.stroke();

        // Optional arrow midpoint indicator
        if (isHighlight) {
          const midX = (source.x + target.x) / 2;
          const midY = (source.y + target.y) / 2;
          ctx.fillStyle = '#C8553D';
          ctx.beginPath();
          ctx.arc(midX, midY, 3, 0, 2 * Math.PI);
          ctx.fill();
        }
      });

      // 2. Draw Nodes
      graphData.nodes.forEach(node => {
        const isSelected = selectedNode && selectedNode.id === node.id;

        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius, 0, 2 * Math.PI);

        // Color coding by entity type
        if (node.type === 'complaint') {
          ctx.fillStyle = node.risk >= 75 ? '#C8553D' : node.risk >= 50 ? '#E3A83B' : '#1F6F6B';
        } else if (node.type === 'upi_vpa') {
          ctx.fillStyle = '#8FB59B';
        } else if (node.type === 'phone') {
          ctx.fillStyle = '#D9825B';
        } else if (node.type === 'url') {
          ctx.fillStyle = '#4AA9A5';
        } else if (node.type === 'bank_account') {
          ctx.fillStyle = '#5E81AC';
        } else {
          ctx.fillStyle = '#9BA7B5';
        }

        ctx.fill();
        ctx.lineWidth = isSelected ? 4 : 2;
        ctx.strokeStyle = isSelected ? '#1F6F6B' : '#FFFFFF';
        ctx.stroke();

        // Node Label
        ctx.font = isSelected ? 'bold 12px Inter, sans-serif' : '11px Inter, sans-serif';
        ctx.fillStyle = '#23272A';
        ctx.textAlign = 'center';
        const displayLabel = node.label.length > 20 ? node.label.slice(0, 18) + '...' : node.label;
        ctx.fillText(displayLabel, node.x, node.y + node.radius + 14);
      });

      ctx.restore();
      animationFrameId = requestAnimationFrame(render);
    };

    render();
    return () => cancelAnimationFrame(animationFrameId);
  }, [graphData, selectedNode]);

  // Click on Node Handler
  const handleCanvasClick = (e) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mouseX = (e.clientX - rect.left - transformRef.current.x) / transformRef.current.scale;
    const mouseY = (e.clientY - rect.top - transformRef.current.y) / transformRef.current.scale;

    let found = null;
    for (const node of graphData.nodes) {
      const dist = Math.hypot(node.x - mouseX, node.y - mouseY);
      if (dist <= node.radius + 6) {
        found = node;
        break;
      }
    }
    setSelectedNode(found);
  };

  // Zoom Controls
  const handleZoom = (factor) => {
    transformRef.current.scale = Math.max(0.3, Math.min(3.5, transformRef.current.scale * factor));
  };

  const handleResetZoom = () => {
    const canvas = canvasRef.current;
    if (canvas && graphData.nodes.length > 0) {
      zoomToFit(graphData.nodes, canvas.width, canvas.height);
    } else {
      transformRef.current = { x: 0, y: 0, scale: 1 };
    }
  };

  return (
    <div className="app-card">
      <div className="card-header">
        <div>
          <h3 className="card-title" style={{ fontSize: '1.4rem' }}>
            {t.linkGraphTitle || "Mule Syndicate Link Analysis Graph"}
          </h3>
          <p className="card-subtitle">
            {t.linkGraphSub || "Multi-jurisdiction correlation engine exposing shared UPIs, mule bank accounts, and phone rings"}
          </p>
        </div>

        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <button onClick={fetchGraph} className="control-btn" title="Refresh Graph">
            <RefreshCw size={16} className={loading ? 'spin' : ''} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* ERROR STATE */}
      {error && (
        <div style={{ background: '#FFF5F5', border: '1px solid var(--danger)', padding: '12px 16px', borderRadius: 8, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 10, color: 'var(--danger)' }}>
          <AlertCircle size={20} />
          <span>{error}</span>
          <button onClick={fetchGraph} className="control-btn" style={{ marginLeft: 'auto', background: 'var(--danger)', color: '#FFFFFF' }}>
            Retry
          </button>
        </div>
      )}

      {/* Graph Filter & Cluster Selector Bar */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 16, flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ flex: 1, minWidth: 220 }}>
          <input
            type="text"
            className="form-input"
            placeholder="Search phone, UPI, account or complaint ID..."
            value={searchFilter}
            onChange={e => setSearchFilter(e.target.value)}
            style={{ minHeight: 42, padding: '8px 12px', fontSize: '0.9rem' }}
          />
        </div>

        <select
          className="form-select"
          value={selectedCluster}
          onChange={e => setSelectedCluster(e.target.value)}
          style={{ minHeight: 42, width: 280, fontSize: '0.9rem' }}
        >
          <option value="All">All Detected Mule Rings ({graphData.clusters.length})</option>
          {graphData.clusters.map(cl => (
            <option key={cl.cluster_id} value={cl.cluster_id}>
              {cl.cluster_name} ({cl.complaints_count} cases — ₹{Math.round(cl.total_loss_inr / 1000)}k)
            </option>
          ))}
        </select>

        <select
          className="form-select"
          value={entityFilter}
          onChange={e => setEntityFilter(e.target.value)}
          style={{ minHeight: 42, width: 200, fontSize: '0.9rem' }}
        >
          <option value="All">All Entity Types</option>
          <option value="complaint">Complaints Only</option>
          <option value="upi_vpa">UPI Handles Only</option>
          <option value="phone">Phone Numbers Only</option>
          <option value="bank_account">Bank Accounts Only</option>
          <option value="url">URLs / Domains</option>
        </select>

        <div style={{ display: 'flex', gap: 6 }}>
          <button onClick={() => handleZoom(1.25)} className="control-btn" title="Zoom In" style={{ minWidth: 42, padding: 8 }}>
            <ZoomIn size={18} />
          </button>
          <button onClick={() => handleZoom(0.8)} className="control-btn" title="Zoom Out" style={{ minWidth: 42, padding: 8 }}>
            <ZoomOut size={18} />
          </button>
          <button onClick={handleResetZoom} className="control-btn" title="Fit to Screen" style={{ minWidth: 42, padding: 8 }}>
            <Maximize2 size={18} />
          </button>
        </div>
      </div>

      {/* Main Interactive Canvas & Detail Side Panel */}
      <div
        ref={containerRef}
        style={{
          position: 'relative',
          width: '100%',
          height: 600,
          background: 'var(--bg-card)',
          borderRadius: 12,
          border: '1px solid var(--border-color)',
          overflow: 'hidden'
        }}
      >
        {loading && (
          <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(255, 255, 255, 0.75)', zIndex: 10 }}>
            <RefreshCw size={28} className="spin" />
            <span style={{ marginLeft: 12, fontWeight: 700 }}>Synthesizing Mule Rings...</span>
          </div>
        )}

        <canvas
          ref={canvasRef}
          onClick={handleCanvasClick}
          style={{ width: '100%', height: '100%', cursor: 'pointer', display: 'block' }}
        />

        {/* Legend Overlay */}
        <div style={{
          position: 'absolute',
          bottom: 14,
          left: 14,
          background: 'rgba(255, 255, 255, 0.95)',
          padding: '10px 16px',
          borderRadius: 8,
          border: '1px solid var(--border-color)',
          fontSize: '0.82rem',
          display: 'flex',
          gap: 16,
          flexWrap: 'wrap',
          boxShadow: '0 2px 8px rgba(0,0,0,0.06)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 12, height: 12, borderRadius: '50%', background: '#C8553D', display: 'inline-block' }}></span>
            <span>Critical Complaint</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 12, height: 12, borderRadius: '50%', background: '#1F6F6B', display: 'inline-block' }}></span>
            <span>Standard Incident</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 12, height: 12, borderRadius: '50%', background: '#8FB59B', display: 'inline-block' }}></span>
            <span>UPI VPA</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 12, height: 12, borderRadius: '50%', background: '#5E81AC', display: 'inline-block' }}></span>
            <span>Bank Account</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 12, height: 12, borderRadius: '50%', background: '#D9825B', display: 'inline-block' }}></span>
            <span>Phone</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 12, height: 12, borderRadius: '50%', background: '#4AA9A5', display: 'inline-block' }}></span>
            <span>URL / APK</span>
          </div>
        </div>

        {/* Selected Entity Side Drawer */}
        {selectedNode && (
          <div style={{
            position: 'absolute',
            top: 14,
            right: 14,
            width: 320,
            maxHeight: '92%',
            overflowY: 'auto',
            background: '#FFFFFF',
            border: '1px solid var(--border-color)',
            borderRadius: 10,
            padding: 18,
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.12)',
            zIndex: 20
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <span className={`status-badge ${selectedNode.risk >= 75 ? 'status-critical' : 'status-medium'}`}>
                Risk Score: {selectedNode.risk}/100
              </span>
              <button
                onClick={() => setSelectedNode(null)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4 }}
              >
                <X size={18} />
              </button>
            </div>

            <h4 style={{ margin: '0 0 6px 0', fontSize: '1.1rem', wordBreak: 'break-all' }}>
              {selectedNode.label}
            </h4>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-light)', textTransform: 'uppercase', fontWeight: 700, marginBottom: 14 }}>
              Entity Type: {selectedNode.type}
            </div>

            {selectedNode.cluster_name && (
              <div style={{ background: 'var(--bg-sand)', padding: 10, borderRadius: 6, marginBottom: 14, fontSize: '0.85rem' }}>
                <strong>Syndicate Affiliation:</strong>
                <div>{selectedNode.cluster_name}</div>
              </div>
            )}

            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: '0.85rem' }}>
              {Object.entries(selectedNode.details || {}).map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #F1EBDD', paddingBottom: 4 }}>
                  <span style={{ color: 'var(--text-muted)', textTransform: 'capitalize' }}>{k.replace('_', ' ')}:</span>
                  <span style={{ fontWeight: 600, textAlign: 'right', maxWidth: 170, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {typeof v === 'number' && k.includes('loss') ? `₹${v.toLocaleString('en-IN')}` : String(v)}
                  </span>
                </div>
              ))}
            </div>

            <div style={{ marginTop: 18, display: 'flex', flexDirection: 'column', gap: 8 }}>
              {selectedNode.type === 'complaint' && onSelectCase && (
                <button
                  onClick={() => onSelectCase({ id: selectedNode.id.replace('case_', ''), complaint_id: selectedNode.label })}
                  className="btn-primary"
                  style={{ width: '100%', padding: '8px 12px', fontSize: '0.85rem' }}
                >
                  Open Case Dossier
                </button>
              )}
              <button
                onClick={() => alert(`Lien freeze notice initiated for ${selectedNode.label} via CFCFRMS 1930 integration.`)}
                className="control-btn"
                style={{ width: '100%', padding: '8px 12px', fontSize: '0.85rem' }}
              >
                Mark Lien / Freeze Handle
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
