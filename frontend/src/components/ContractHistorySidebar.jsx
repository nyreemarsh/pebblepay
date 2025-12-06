import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { History, FileText, Trash2, RefreshCw, Plus } from 'lucide-react'
import './ContractHistorySidebar.css'

const API_BASE_URL = 'http://localhost:8000'

function ContractHistorySidebar({ onLoadContract, onNewContract, currentSessionId }) {
  const [contracts, setContracts] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  const fetchContracts = async () => {
    setIsLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/contracts`)
      const data = await response.json()
      setContracts(data.contracts || [])
    } catch (error) {
      console.error('Error fetching contracts:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchContracts()
    // Refresh every 30 seconds
    const interval = setInterval(fetchContracts, 30000)
    return () => clearInterval(interval)
  }, [])

  const handleDelete = async (sessionId, e) => {
    e.stopPropagation()
    if (!confirm('Delete this contract?')) return
    
    try {
      await fetch(`${API_BASE_URL}/api/contracts/${sessionId}`, {
        method: 'DELETE'
      })
      setContracts(contracts.filter(c => c.session_id !== sessionId))
    } catch (error) {
      console.error('Error deleting contract:', error)
    }
  }

  const handleLoad = (contract) => {
    if (onLoadContract) {
      onLoadContract(contract.session_id)
    }
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="contract-history-sidebar">
      {/* Logo Section */}
      <div className="logo-section">
        <div className="logo-container">
          <img 
            src="/assets/images/logos/pibble_coin.png" 
            alt="Pibble Coin" 
            className="pibble-coin"
            onError={(e) => {
              // Fallback if image not found
              e.target.style.display = 'none'
            }}
          />
          <div className="brand-container">
            <h1 className="app-title">pibblepay</h1>
            <p className="app-caption">your smart contract creation playground</p>
          </div>
        </div>
      </div>

      {/* Header */}
      <div className="history-sidebar-header">
        <div className="history-sidebar-title">
          <History size={20} />
          <h2>Saved Contracts</h2>
        </div>
        <div className="history-sidebar-actions">
          <button className="refresh-btn" onClick={fetchContracts} disabled={isLoading} title="Refresh">
            <RefreshCw size={16} className={isLoading ? 'spinning' : ''} />
          </button>
          <motion.button
            className="new-contract-btn"
            onClick={onNewContract}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            title="New Contract"
          >
            <Plus size={18} />
          </motion.button>
        </div>
      </div>

      {/* Contracts List */}
      <div className="history-sidebar-list">
        {isLoading ? (
          <div className="history-loading">Loading...</div>
        ) : contracts.length === 0 ? (
          <div className="history-empty">
            <FileText size={40} />
            <p>No saved contracts yet</p>
            <span>Your contracts will appear here</span>
          </div>
        ) : (
          contracts.map((contract) => (
            <motion.div
              key={contract.session_id}
              className={`history-sidebar-item ${contract.session_id === currentSessionId ? 'current' : ''}`}
              onClick={() => handleLoad(contract)}
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
            >
              <div className="history-item-icon">
                <FileText size={24} />
                {contract.has_contract && (
                  <span className="complete-badge">✓</span>
                )}
              </div>
              <div className="history-item-info">
                <h3>{contract.title || 'Untitled Contract'}</h3>
                <p>
                  {contract.freelancer_name && contract.client_name 
                    ? `${contract.freelancer_name} → ${contract.client_name}`
                    : contract.freelancer_name || contract.client_name || 'In progress...'}
                </p>
                <span className="history-date">{formatDate(contract.updated_at)}</span>
              </div>
              <div className="history-item-actions">
                <button
                  className="delete-btn"
                  onClick={(e) => handleDelete(contract.session_id, e)}
                  title="Delete"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  )
}

export default ContractHistorySidebar

