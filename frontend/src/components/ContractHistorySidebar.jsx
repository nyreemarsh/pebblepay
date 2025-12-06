import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { History, FileText, Trash2, RefreshCw, Plus, AlertCircle } from 'lucide-react'
import './ContractHistorySidebar.css'

const API_BASE_URL = 'http://localhost:8000'

function ContractHistorySidebar({ onLoadContract, onNewContract, currentSessionId }) {
  const [contracts, setContracts] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [backendError, setBackendError] = useState(false)

  const fetchContracts = async () => {
    setIsLoading(true)
    setBackendError(false)
    try {
      const response = await fetch(`${API_BASE_URL}/api/contracts`)
      
      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`)
      }
      
      const data = await response.json()
      setContracts(data.contracts || [])
      setBackendError(false)
    } catch (error) {
      console.error('Error fetching contracts:', error)
      setBackendError(true)
      setContracts([])
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
            src="/assets/images/logos/pibblepay_logo.png" 
            alt="PibblePay" 
            className="pibblepay-logo"
            onError={(e) => {
              // Fallback if image not found
              e.target.style.display = 'none'
            }}
          />
        </div>
      </div>

      {/* Header */}
      <div className="history-sidebar-header">
        <div className="history-sidebar-title">
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
        ) : backendError ? (
          <div className="history-empty">
            <AlertCircle size={40} style={{ color: '#F7B2A8', marginBottom: '12px' }} />
            <p style={{ color: '#6B5353', fontWeight: 'bold' }}>Backend not connected</p>
            <span style={{ color: '#6B5353', fontSize: '0.85rem', textAlign: 'center', maxWidth: '200px' }}>
              Make sure the backend server is running on http://localhost:8000
            </span>
            <button 
              onClick={fetchContracts}
              style={{
                marginTop: '12px',
                padding: '8px 16px',
                backgroundColor: '#78BEB1',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '0.9rem',
                fontWeight: '500'
              }}
            >
              Retry Connection
            </button>
          </div>
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

