import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import StockCard from './components/StockCard';
import ChatBot from './components/ChatBot';
import Portfolio from './components/Portfolio';
import StockAnalytics from './components/StockAnalytics';

interface StockData {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  market_cap: number;
  pe_ratio: number;
}

function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'analytics' | 'portfolio' | 'chat'>('dashboard');
  const [stocks, setStocks] = useState<StockData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStock, setSelectedStock] = useState<string>('AAPL');

  const fetchStockData = useCallback(async () => {
    const watchlist = ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'];
    try {
      const promises = watchlist.map(symbol =>
        fetch(`${process.env.REACT_APP_API_URL || "http://localhost:8000"}/market/stock/${symbol}`)
          .then(res => res.json())
          .then(data => data.data)
      );
      const results = await Promise.all(promises);
      setStocks(results);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching stock data:', error);
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStockData();
    const interval = setInterval(fetchStockData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [fetchStockData]);

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="container">
          <div className="header-content">
            <div className="logo">
              <span className="logo-icon">📈</span>
              <h1 className="gradient-text">TradeBot</h1>
            </div>
            <nav className="nav">
              <button
                className={`nav-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
                onClick={() => setActiveTab('dashboard')}
              >
                <span className="nav-icon">📊</span>
                Dashboard
              </button>
              <button
                className={`nav-btn ${activeTab === 'analytics' ? 'active' : ''}`}
                onClick={() => setActiveTab('analytics')}
              >
                <span className="nav-icon">📈</span>
                Analytics
              </button>
              <button
                className={`nav-btn ${activeTab === 'portfolio' ? 'active' : ''}`}
                onClick={() => setActiveTab('portfolio')}
              >
                <span className="nav-icon">💼</span>
                Portfolio
              </button>
              <button
                className={`nav-btn ${activeTab === 'chat' ? 'active' : ''}`}
                onClick={() => setActiveTab('chat')}
              >
                <span className="nav-icon">🤖</span>
                AI Assistant
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <div className="container">
          {activeTab === 'dashboard' && (
            <div className="dashboard fade-in">
              <div className="dashboard-header">
                <h2>Market Overview</h2>
                <div className="market-status">
                  <span className="status-indicator"></span>
                  <span>Market Open</span>
                </div>
              </div>

              {loading ? (
                <div className="loading-container">
                  <div className="spinner"></div>
                  <p>Loading market data...</p>
                </div>
              ) : (
                <div className="stock-grid">
                  {stocks.map((stock, index) => (
                    <StockCard
                      key={stock.symbol}
                      stock={stock}
                      onClick={() => {
                        setSelectedStock(stock.symbol);
                        setActiveTab('analytics');
                      }}
                      delay={index * 100}
                    />
                  ))}
                </div>
              )}

              <div className="quick-actions">
                <h3>Quick Actions</h3>
                <div className="actions-grid">
                  <button className="action-card" onClick={() => setActiveTab('chat')}>
                    <span className="action-icon">💬</span>
                    <span className="action-title">Ask AI</span>
                    <span className="action-desc">Get trading insights</span>
                  </button>
                  <button className="action-card" onClick={() => setActiveTab('analytics')}>
                    <span className="action-icon">📊</span>
                    <span className="action-title">Analyze</span>
                    <span className="action-desc">Deep dive into stocks</span>
                  </button>
                  <button className="action-card" onClick={() => setActiveTab('portfolio')}>
                    <span className="action-icon">💰</span>
                    <span className="action-title">Portfolio</span>
                    <span className="action-desc">View your holdings</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'analytics' && (
            <StockAnalytics symbol={selectedStock} onSymbolChange={setSelectedStock} />
          )}

          {activeTab === 'portfolio' && <Portfolio />}

          {activeTab === 'chat' && <ChatBot />}
        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <p>© 2026 TradeBot - AI-Powered Trading Platform</p>
          <p className="footer-note">Real-time market data • Advanced Analytics • Smart Trading</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
