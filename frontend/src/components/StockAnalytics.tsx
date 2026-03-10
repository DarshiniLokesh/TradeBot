import React, { useState, useEffect } from 'react';
import './StockAnalytics.css';

interface StockAnalyticsProps {
    symbol: string;
    onSymbolChange: (symbol: string) => void;
}

interface AnalyticsData {
    symbol: string;
    technical_indicators: {
        sma_20: number;
        sma_50: number;
        rsi: number;
        macd: number;
        macd_signal: number;
        bb_upper: number;
        bb_lower: number;
        bb_middle: number;
    };
    fundamental_metrics: {
        market_cap: number;
        pe_ratio: number;
        pb_ratio: number;
        debt_to_equity: number;
        return_on_equity: number;
        profit_margins: number;
        revenue_growth: number;
        earnings_growth: number;
    };
    recommendations: string[];
    risk_score: number;
}

const StockAnalytics: React.FC<StockAnalyticsProps> = ({ symbol, onSymbolChange }) => {
    const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [searchSymbol, setSearchSymbol] = useState(symbol);

    useEffect(() => {
        fetchAnalytics(symbol);
    }, [symbol]);

    const fetchAnalytics = async (sym: string) => {
        setLoading(true);
        try {
            const response = await fetch(`http://localhost:8000/market/analytics/${sym}`);
            const data = await response.json();
            setAnalytics(data.data);
        } catch (error) {
            console.error('Error fetching analytics:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (searchSymbol.trim()) {
            onSymbolChange(searchSymbol.toUpperCase());
        }
    };

    const getRiskLevel = (score: number) => {
        if (score >= 80) return { label: 'High Risk', color: 'var(--danger)' };
        if (score >= 50) return { label: 'Medium Risk', color: 'var(--warning)' };
        return { label: 'Low Risk', color: 'var(--success)' };
    };

    const getRSIStatus = (rsi: number) => {
        if (rsi >= 70) return { label: 'Overbought', color: 'var(--danger)' };
        if (rsi <= 30) return { label: 'Oversold', color: 'var(--success)' };
        return { label: 'Neutral', color: 'var(--accent-primary)' };
    };

    if (loading) {
        return (
            <div className="analytics-loading">
                <div className="spinner"></div>
                <p>Loading analytics for {symbol}...</p>
            </div>
        );
    }

    if (!analytics) {
        return <div className="analytics-error">Failed to load analytics data.</div>;
    }

    const riskLevel = getRiskLevel(analytics.risk_score);
    const rsiStatus = getRSIStatus(analytics.technical_indicators.rsi);

    return (
        <div className="analytics-container fade-in">
            <div className="analytics-header">
                <h2>Stock Analytics</h2>
                <form onSubmit={handleSearch} className="symbol-search">
                    <input
                        type="text"
                        placeholder="Enter symbol (e.g., AAPL)"
                        value={searchSymbol}
                        onChange={(e) => setSearchSymbol(e.target.value)}
                        className="symbol-input"
                    />
                    <button type="submit" className="btn btn-primary">
                        Analyze
                    </button>
                </form>
            </div>

            <div className="current-symbol">
                <h1 className="gradient-text">{analytics.symbol}</h1>
                <div className="risk-badge" style={{ borderColor: riskLevel.color }}>
                    <span style={{ color: riskLevel.color }}>●</span>
                    {riskLevel.label}
                </div>
            </div>

            <div className="analytics-grid">
                {/* Technical Indicators */}
                <div className="analytics-card">
                    <h3>📊 Technical Indicators</h3>
                    <div className="indicators-grid">
                        <div className="indicator">
                            <span className="indicator-label">RSI (14)</span>
                            <div className="indicator-value-container">
                                <span className="indicator-value">{analytics.technical_indicators.rsi.toFixed(2)}</span>
                                <span className="indicator-status" style={{ color: rsiStatus.color }}>
                                    {rsiStatus.label}
                                </span>
                            </div>
                            <div className="progress-bar">
                                <div
                                    className="progress-fill"
                                    style={{
                                        width: `${analytics.technical_indicators.rsi}%`,
                                        background: rsiStatus.color,
                                    }}
                                />
                            </div>
                        </div>

                        <div className="indicator">
                            <span className="indicator-label">MACD</span>
                            <span className="indicator-value">{analytics.technical_indicators.macd.toFixed(2)}</span>
                            <span className="indicator-sub">Signal: {analytics.technical_indicators.macd_signal.toFixed(2)}</span>
                        </div>

                        <div className="indicator">
                            <span className="indicator-label">SMA 20</span>
                            <span className="indicator-value">${analytics.technical_indicators.sma_20.toFixed(2)}</span>
                        </div>

                        <div className="indicator">
                            <span className="indicator-label">SMA 50</span>
                            <span className="indicator-value">${analytics.technical_indicators.sma_50.toFixed(2)}</span>
                        </div>

                        <div className="indicator bollinger">
                            <span className="indicator-label">Bollinger Bands</span>
                            <div className="bb-values">
                                <span>Upper: ${analytics.technical_indicators.bb_upper.toFixed(2)}</span>
                                <span>Middle: ${analytics.technical_indicators.bb_middle.toFixed(2)}</span>
                                <span>Lower: ${analytics.technical_indicators.bb_lower.toFixed(2)}</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Fundamental Metrics */}
                <div className="analytics-card">
                    <h3>💼 Fundamental Metrics</h3>
                    <div className="metrics-grid">
                        <div className="metric-item">
                            <span className="metric-label">P/E Ratio</span>
                            <span className="metric-value">{analytics.fundamental_metrics.pe_ratio.toFixed(2)}</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-label">P/B Ratio</span>
                            <span className="metric-value">{analytics.fundamental_metrics.pb_ratio.toFixed(2)}</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-label">Debt/Equity</span>
                            <span className="metric-value">{analytics.fundamental_metrics.debt_to_equity.toFixed(2)}</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-label">ROE</span>
                            <span className="metric-value">{(analytics.fundamental_metrics.return_on_equity * 100).toFixed(2)}%</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-label">Profit Margin</span>
                            <span className="metric-value">{(analytics.fundamental_metrics.profit_margins * 100).toFixed(2)}%</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-label">Revenue Growth</span>
                            <span className="metric-value positive">{(analytics.fundamental_metrics.revenue_growth * 100).toFixed(2)}%</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-label">Earnings Growth</span>
                            <span className="metric-value positive">{(analytics.fundamental_metrics.earnings_growth * 100).toFixed(2)}%</span>
                        </div>
                    </div>
                </div>

                {/* AI Recommendations */}
                <div className="analytics-card recommendations-card">
                    <h3>🤖 AI Recommendations</h3>
                    <div className="recommendations-list">
                        {analytics.recommendations.map((rec, index) => (
                            <div key={index} className="recommendation-item">
                                <span className="rec-icon">
                                    {rec.includes('bullish') || rec.includes('growth') ? '✅' :
                                        rec.includes('risk') || rec.includes('High') ? '⚠️' : 'ℹ️'}
                                </span>
                                <span className="rec-text">{rec}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Risk Score */}
                <div className="analytics-card risk-card">
                    <h3>⚡ Risk Assessment</h3>
                    <div className="risk-score-container">
                        <div className="risk-score-circle" style={{ borderColor: riskLevel.color }}>
                            <span className="risk-score-value" style={{ color: riskLevel.color }}>
                                {analytics.risk_score}
                            </span>
                            <span className="risk-score-label">Risk Score</span>
                        </div>
                        <div className="risk-description">
                            <p style={{ color: riskLevel.color, fontWeight: 700 }}>{riskLevel.label}</p>
                            <p className="risk-note">
                                Based on technical indicators, fundamental metrics, and market conditions.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default StockAnalytics;
