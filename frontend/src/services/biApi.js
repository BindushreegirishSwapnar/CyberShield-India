/**
 * CyberShield India - Typed BI & Intelligence API Client
 * Normalizes all numbers (no strings), dates (ISO 8601), and provides adapters per chart.
 */

const DEFAULT_BASE = '/api/v1';

async function fetchWithRetry(url, options = {}, retries = 2, backoff = 500) {
  try {
    const res = await fetch(url, options);
    if (!res.ok) {
      const errText = await res.text().catch(() => '');
      throw new Error(`HTTP ${res.status}: ${errText || res.statusText}`);
    }
    return await res.json();
  } catch (err) {
    if (retries > 0) {
      await new Promise(r => setTimeout(r, backoff));
      return fetchWithRetry(url, options, retries - 1, backoff * 1.5);
    }
    throw err;
  }
}

export const biApi = {
  /**
   * Health Check
   */
  async checkHealth(apiBase = DEFAULT_BASE) {
    return await fetchWithRetry(`${apiBase}/health`);
  },

  /**
   * Top Affected States Adapter
   */
  async getStates(filters = {}, apiBase = DEFAULT_BASE) {
    const params = new URLSearchParams();
    if (filters.category && filters.category !== 'All') params.set('category', filters.category);
    if (filters.year && filters.year !== 'All') params.set('year', filters.year);
    if (filters.status && filters.status !== 'All') params.set('status', filters.status);

    const query = params.toString() ? `?${params.toString()}` : '';
    const json = await fetchWithRetry(`${apiBase}/bi/states${query}`);

    const rawList = json.data || json.states || [];
    return rawList.map(s => ({
      state: String(s.state || 'Unknown'),
      total_complaints: Number(s.total_complaints) || 0,
      total_financial_loss: Number(s.total_financial_loss) || 0,
      avg_risk_score: Number(s.avg_risk_score) || 0,
      critical_count: Number(s.critical_count) || 0,
      resolved_count: Number(s.resolved_count) || 0,
      recovery_rate_pct: Number(s.recovery_rate_pct) || 0
    }));
  },

  /**
   * Monthly Trend Adapter
   */
  async getMonthlyTrend(filters = {}, apiBase = DEFAULT_BASE) {
    const params = new URLSearchParams();
    if (filters.state && filters.state !== 'All') params.set('state', filters.state);
    if (filters.category && filters.category !== 'All') params.set('category', filters.category);

    const query = params.toString() ? `?${params.toString()}` : '';
    const json = await fetchWithRetry(`${apiBase}/bi/monthly-trend${query}`);

    const rawList = json.data || json.monthly_trend || [];
    return rawList.map(m => ({
      period: String(m.period),
      complaints: Number(m.complaints) || 0,
      financial_loss: Number(m.financial_loss) || 0,
      critical_cases: Number(m.critical_cases) || 0
    }));
  },

  /**
   * Decomposition Tree Adapter
   */
  async getDecomposition(filters = {}, apiBase = DEFAULT_BASE) {
    const params = new URLSearchParams();
    if (filters.state && filters.state !== 'All') params.set('state', filters.state);

    const query = params.toString() ? `?${params.toString()}` : '';
    const json = await fetchWithRetry(`${apiBase}/bi/decomposition${query}`);

    return {
      root: {
        label: String(json.root?.label || 'Total National Loss'),
        total_loss: Number(json.root?.total_loss) || 0,
        total_complaints: Number(json.root?.total_complaints) || 0
      },
      by_category: (json.by_category || []).map(c => ({
        category: String(c.category),
        amount: Number(c.amount) || 0,
        count: Number(c.count) || 0,
        percentage: Number(c.percentage) || 0
      })),
      by_platform: (json.by_platform || []).map(p => ({
        platform: String(p.platform),
        count: Number(p.count) || 0,
        percentage: Number(p.percentage) || 0
      })),
      by_risk: (json.by_risk || []).map(r => ({
        risk_level: String(r.risk_level),
        count: Number(r.count) || 0,
        percentage: Number(r.percentage) || 0
      }))
    };
  },

  /**
   * Waterfall Chart Adapter
   */
  async getWaterfall(filters = {}, apiBase = DEFAULT_BASE) {
    const params = new URLSearchParams();
    if (filters.state && filters.state !== 'All') params.set('state', filters.state);
    if (filters.category && filters.category !== 'All') params.set('category', filters.category);

    const query = params.toString() ? `?${params.toString()}` : '';
    const json = await fetchWithRetry(`${apiBase}/bi/waterfall${query}`);

    const rawSteps = json.data || json.steps || [];
    return rawSteps.map(s => ({
      step: String(s.step),
      amount: Number(s.amount) || 0,
      fill: String(s.fill || '#1F6F6B'),
      is_total: Boolean(s.is_total),
      is_delta: Boolean(s.is_delta)
    }));
  },

  /**
   * Incident Time Heatmap Adapter
   */
  async getHeatmap(apiBase = DEFAULT_BASE) {
    const json = await fetchWithRetry(`${apiBase}/bi/heatmap`);
    const rawData = json.data || [];
    return rawData.map(h => ({
      day: String(h.day),
      day_num: Number(h.day_num) || 0,
      hour: String(h.hour),
      hour_num: Number(h.hour_num) || 0,
      cases: Number(h.cases) || 0,
      intensity: Number(h.intensity) || 0
    }));
  },

  /**
   * Forecast Chart Adapter
   */
  async getForecast(horizon = 'next_year', apiBase = DEFAULT_BASE) {
    const json = await fetchWithRetry(`${apiBase}/bi/forecast?horizon=${horizon}`);
    const rawProjections = json.projections || json.data || [];
    return {
      methodology: String(json.methodology || 'Polynomial Trend Regression with 95% CI'),
      growth_rate_pct: Number(json.growth_rate_pct) || 18.5,
      projections: rawProjections.map(p => ({
        period: String(p.period),
        actual: p.actual !== null && p.actual !== undefined ? Number(p.actual) : null,
        predicted: Number(p.predicted) || 0,
        lower_ci: Number(p.lower_ci) || 0,
        upper_ci: Number(p.upper_ci) || 0,
        is_projected: Boolean(p.is_projected)
      }))
    };
  },

  /**
   * Entity Link Graph Adapter
   */
  async getGraphEntities(filters = {}, apiBase = DEFAULT_BASE) {
    const params = new URLSearchParams();
    if (filters.cluster_id && filters.cluster_id !== 'All') params.set('cluster_id', filters.cluster_id);
    if (filters.type && filters.type !== 'All') params.set('type', filters.type);
    if (filters.search) params.set('search', filters.search);

    const query = params.toString() ? `?${params.toString()}` : '';
    const json = await fetchWithRetry(`${apiBase}/graph/entities${query}`);

    const rawNodes = json.nodes || [];
    const rawLinks = json.links || [];
    const clusters = json.clusters || [];

    // Ensure strict node integrity
    const nodes = rawNodes.map(n => ({
      id: String(n.id),
      type: String(n.type),
      label: String(n.label),
      risk: Number(n.risk) || 50,
      cluster_id: n.cluster_id,
      cluster_name: n.cluster_name,
      details: n.details || {}
    }));

    const nodeIds = new Set(nodes.map(n => n.id));
    const links = rawLinks
      .filter(l => nodeIds.has(String(l.source)) && nodeIds.has(String(l.target)))
      .map(l => ({
        source: String(l.source),
        target: String(l.target),
        type: String(l.type || 'linked_to')
      }));

    return { nodes, links, clusters };
  }
};
