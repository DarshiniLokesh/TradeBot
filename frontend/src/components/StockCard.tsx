import React from 'react';
import './StockCard.css';

interface StockCardProps {
    stock: {
        symbol: string;
        price: number;
        change: number;
        change_percent: number;
        volume: number;
        market_cap: number;
        pe_ratio?: number;
    };
    onClick: () => void;
    delay?: number;
}

const StockCard: React.FC<StockCardProps> = ({ stock, onClick, delay = 0 }) => {
    const isPositive = stock.change >= 0;
    const formatNumber = (num: number) => {
        if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
        if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
        if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
        return `$${num.toFixed(2)}`;
    };

    const formatVolume = (vol: number) => {
        if (vol >= 1e6) return `${(vol / 1e6).toFixed(2)}M`;
        if (vol >= 1e3) return `${(vol / 1e3).toFixed(2)}K`;
        return vol.toString();
    };

    return (
        <div
            className="stock-card"
            onClick={onClick}
            style={{ animationDelay: `${delay}ms` }}
        >
            <div className="stock-header">
                <div className="stock-symbol-container">
                    <h3 className="stock-symbol">{stock.symbol}</h3>
                    <span className={`stock-badge ${isPositive ? 'positive' : 'negative'}`}>
                        {isPositive ? '↑' : '↓'}
                    </span>
                </div>
                <div className={`stock-change ${isPositive ? 'positive' : 'negative'}`}>
                    <span className="change-value">
                        {isPositive ? '+' : ''}{stock.change.toFixed(2)}
                    </span>
                    <span className="change-percent">
                        ({isPositive ? '+' : ''}{stock.change_percent.toFixed(2)}%)
                    </span>
                </div>
            </div>

            <div className="stock-price">
                <span className="price-label">Current Price</span>
                <span className="price-value">${stock.price.toFixed(2)}</span>
            </div>

            <div className="stock-metrics">
                <div className="metric">
                    <span className="metric-label">Volume</span>
                    <span className="metric-value">{formatVolume(stock.volume)}</span>
                </div>
                <div className="metric">
                    <span className="metric-label">Market Cap</span>
                    <span className="metric-value">{formatNumber(stock.market_cap)}</span>
                </div>
                {stock.pe_ratio && (
                    <div className="metric">
                        <span className="metric-label">P/E Ratio</span>
                        <span className="metric-value">{stock.pe_ratio.toFixed(2)}</span>
                    </div>
                )}
            </div>

            <div className="stock-footer">
                <button className="view-details-btn">
                    View Details →
                </button>
            </div>
        </div>
    );
};

export default StockCard;
