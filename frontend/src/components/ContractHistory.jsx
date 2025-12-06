import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { History, FileText, Trash2, X, RefreshCw, Plus } from 'lucide-react'
import './ContractHistory.css'

const API_BASE_URL = 'http://localhost:8000'

function ContractHistory({ onLoadContract, onNewContract, currentSessionId }) {
  const [isOpen, setIsOpen] = useState(false)
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
    if (isOpen) {
      fetchContracts()
    }
  }, [isOpen])

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
    setIsOpen(false)
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
    <>
      {/* Action Buttons */}
      <div className="history-buttons">
        <motion.button
          className="new-contract-button"
          onClick={onNewContract}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Plus size={18} />
          <span>New Contract</span>
        </motion.button>
        <motion.button
          className="history-toggle-button"
          onClick={() => setIsOpen(true)}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <History size={18} />
          <span>Saved Contracts</span>
        </motion.button>
      </div>

      {/* Modal */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="history-modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsOpen(false)}
          >
            <motion.div
              className="history-modal"
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              onClick={e => e.stopPropagation()}
            >
              <div className="history-header">
                <h2>
                  <History size={20} />
                  Saved Contracts
                </h2>
                <div className="history-header-actions">
                  <button className="refresh-btn" onClick={fetchContracts} disabled={isLoading}>
                    <RefreshCw size={16} className={isLoading ? 'spinning' : ''} />
                  </button>
                  <button className="close-btn" onClick={() => setIsOpen(false)}>
                    <X size={20} />
                  </button>
                </div>
              </div>

              <div className="history-list">
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
                      className={`history-item ${contract.session_id === currentSessionId ? 'current' : ''}`}
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
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}

export default ContractHistory

