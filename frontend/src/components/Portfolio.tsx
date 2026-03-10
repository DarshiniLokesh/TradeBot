import React, { useState, useEffect } from 'react';
import './Portfolio.css';

interface PortfolioData {
    total_value: number;
    total_invested: number;
    total_profit_loss: number;
    profit_loss_percent: number;
    holdings: Array<{
        symbol: string;
        quantity: number;
        avg_price: number;
        current_price: number;
        total_value: number;
        profit_loss: number;
        profit_loss_percent: number;
    }>;
}

const Portfolio: React.FC = () => {
    const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchPortfolio();
    }, []);

    const fetchPortfolio = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/market/portfolio/default_user');
            const data = await response.json();
            setPortfolio(data.data);
        } catch (error) {
            console.error('Error fetching portfolio:', error);
            setPortfolio(null);
        } finally {
            setLoading(false);
        }
    };

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
        }).format(amount);
    };

    if (loading) {
        return (
            <div className="portfolio-loading">
                <div className="spinner"></div>
                <p>Loading your portfolio...</p>
            </div>
        );
    }

    if (!portfolio) {
        return <div className="portfolio-error">Failed to load portfolio data.</div>;
    }

    const isProfitable = portfolio.total_profit_loss >= 0;

    return (
        <div className="portfolio-container fade-in">
            <div className="portfolio-header">
                <h2>My Portfolio</h2>
                <button className="btn btn-primary" onClick={fetchPortfolio}>
                    🔄 Refresh
                </button>
            </div>

            {/* Portfolio Summary */}
            <div className="portfolio-summary">
                <div className="summary-card total-value">
                    <div className="summary-icon">💰</div>
                    <div className="summary-content">
                        <span className="summary-label">Total Value</span>
                        <span className="summary-value">{formatCurrency(portfolio?.total_value || 0)}</span>
                    </div>
                </div>

                <div className="summary-card total-invested">
                    <div className="summary-icon">💵</div>
                    <div className="summary-content">
                        <span className="summary-label">Total Invested</span>
                        <span className="summary-value">{formatCurrency(portfolio?.total_invested || 0)}</span>
                    </div>
                </div>

                <div className={`summary-card total-pl ${isProfitable ? 'positive' : 'negative'}`}>
                    <div className="summary-icon">{isProfitable ? '📈' : '📉'}</div>
                    <div className="summary-content">
                        <span className="summary-label">Total P/L</span>
                        <span className="summary-value">
                            {formatCurrency(portfolio?.total_profit_loss || 0)}
                        </span>
                        <span className="summary-percent">
                            ({isProfitable ? '+' : ''}{(portfolio?.profit_loss_percent || 0).toFixed(2)}%)
                        </span>
                    </div>
                </div>
            </div>

            {/* Holdings Table */}
            <div className="holdings-section">
                <h3>Holdings</h3>
                {portfolio.holdings && portfolio.holdings.length > 0 ? (
                    <div className="holdings-table">
                        <div className="table-header">
                            <div className="th">Symbol</div>
                            <div className="th">Quantity</div>
                            <div className="th">Avg Price</div>
                            <div className="th">Current Price</div>
                            <div className="th">Total Value</div>
                            <div className="th">P/L</div>
                            <div className="th">P/L %</div>
                        </div>
                        {portfolio.holdings.map((holding) => {
                            const isHoldingProfitable = (holding?.profit_loss || 0) >= 0;
                            return (
                                <div key={holding.symbol} className="table-row">
                                    <div className="td symbol-cell">
                                        <span className="symbol-badge">{holding.symbol}</span>
                                    </div>
                                    <div className="td">{holding.quantity || 0}</div>
                                    <div className="td">{formatCurrency(holding?.avg_price || 0)}</div>
                                    <div className="td">{formatCurrency(holding?.current_price || 0)}</div>
                                    <div className="td total-value-cell">{formatCurrency(holding?.total_value || 0)}</div>
                                    <div className={`td ${isHoldingProfitable ? 'positive' : 'negative'}`}>
                                        {isHoldingProfitable ? '+' : ''}{formatCurrency(holding?.profit_loss || 0)}
                                    </div>
                                    <div className={`td ${isHoldingProfitable ? 'positive' : 'negative'}`}>
                                        {isHoldingProfitable ? '+' : ''}{(holding?.profit_loss_percent || 0).toFixed(2)}%
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                ) : (
                    <div className="empty-portfolio">
                        <span className="empty-icon">📊</span>
                        <h3>No Holdings Yet</h3>
                        <p>Start trading to build your portfolio!</p>
                        <button className="btn btn-primary">Start Trading</button>
                    </div>
                )}
            </div>

            {/* Performance Chart Placeholder */}
            <div className="performance-section">
                <h3>Performance Overview</h3>
                <div className="chart-placeholder">
                    <div className="chart-bars">
                        {[65, 85, 70, 90, 75, 95, 80].map((height, index) => (
                            <div key={index} className="chart-bar" style={{ height: `${height}%` }} />
                        ))}
                    </div>
                    <p className="chart-label">Last 7 Days Performance</p>
                </div>
            </div>
        </div>
    );
};

export default Portfolio;
