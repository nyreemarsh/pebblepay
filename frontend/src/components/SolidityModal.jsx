import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Copy, Check, Download, Code, FileText, Zap } from 'lucide-react'
import './SolidityModal.css'

function SolidityModal({ data, onClose }) {
  const [copied, setCopied] = useState(false)
  const [activeTab, setActiveTab] = useState('solidity')

  const handleCopy = async () => {
    try {
      const textToCopy = activeTab === 'solidity' ? data.solidity : data.abi
      await navigator.clipboard.writeText(textToCopy)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const handleDownload = () => {
    const content = activeTab === 'solidity' ? data.solidity : data.abi
    const filename = activeTab === 'solidity' 
      ? `${data.contractName || 'Contract'}.sol`
      : `${data.contractName || 'Contract'}_abi.json`
    const mimeType = activeTab === 'solidity' ? 'text/plain' : 'application/json'
    
    const blob = new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  // Simple syntax highlighting for Solidity
  const highlightSolidity = (code) => {
    if (!code) return ''
    
    // Keywords
    const keywords = ['pragma', 'solidity', 'contract', 'function', 'modifier', 'event', 
                     'constructor', 'returns', 'return', 'if', 'else', 'for', 'while',
                     'require', 'revert', 'emit', 'public', 'private', 'internal', 'external',
                     'view', 'pure', 'payable', 'memory', 'storage', 'calldata', 'virtual',
                     'override', 'abstract', 'interface', 'library', 'using', 'is', 'new',
                     'delete', 'this', 'super', 'import', 'from', 'as', 'struct', 'enum',
                     'mapping', 'indexed', 'anonymous', 'constant', 'immutable']
    
    // Types
    const types = ['address', 'bool', 'string', 'bytes', 'uint', 'int', 'uint256', 'uint128',
                  'uint64', 'uint32', 'uint16', 'uint8', 'int256', 'int128', 'int64', 'int32',
                  'int16', 'int8', 'bytes32', 'bytes4', 'bytes1']
    
    let highlighted = code
      // Comments
      .replace(/(\/\/.*$)/gm, '<span class="comment">$1</span>')
      .replace(/(\/\*[\s\S]*?\*\/)/g, '<span class="comment">$1</span>')
      // Strings
      .replace(/(".*?")/g, '<span class="string">$1</span>')
      // Numbers
      .replace(/\b(\d+)\b/g, '<span class="number">$1</span>')
    
    // Keywords
    keywords.forEach(kw => {
      const regex = new RegExp(`\\b(${kw})\\b`, 'g')
      highlighted = highlighted.replace(regex, '<span class="keyword">$1</span>')
    })
    
    // Types
    types.forEach(t => {
      const regex = new RegExp(`\\b(${t})\\b`, 'g')
      highlighted = highlighted.replace(regex, '<span class="type">$1</span>')
    })
    
    return highlighted
  }

  return (
    <AnimatePresence>
      <motion.div
        className="solidity-modal-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="solidity-modal"
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="modal-header">
            <div className="modal-title">
              <Code size={24} />
              <div>
                <h2>{data.contractName || 'Generated Contract'}</h2>
                <p className="contract-status">
                  {data.status === 'success' ? (
                    <>
                      <Check size={14} className="success-icon" />
                      Successfully generated
                    </>
                  ) : (
                    <>
                      <X size={14} className="error-icon" />
                      Generation failed
                    </>
                  )}
                </p>
              </div>
            </div>
            <button className="close-button" onClick={onClose}>
              <X size={20} />
            </button>
          </div>

          {/* Explanation */}
          {data.explanation && (
            <div className="explanation-section">
              <FileText size={16} />
              <p>{data.explanation}</p>
            </div>
          )}

          {/* Tabs */}
          <div className="modal-tabs">
            <button
              className={`tab ${activeTab === 'solidity' ? 'active' : ''}`}
              onClick={() => setActiveTab('solidity')}
            >
              <Code size={16} />
              Solidity
            </button>
            <button
              className={`tab ${activeTab === 'abi' ? 'active' : ''}`}
              onClick={() => setActiveTab('abi')}
            >
              <Zap size={16} />
              ABI
            </button>
          </div>

          {/* Code Display */}
          <div className="code-container">
            <div className="code-header">
              <span className="filename">
                {activeTab === 'solidity' 
                  ? `${data.contractName || 'Contract'}.sol`
                  : `${data.contractName || 'Contract'}_abi.json`}
              </span>
              <div className="code-actions">
                <button 
                  className="action-btn" 
                  onClick={handleCopy}
                  title="Copy to clipboard"
                >
                  {copied ? <Check size={16} /> : <Copy size={16} />}
                  {copied ? 'Copied!' : 'Copy'}
                </button>
                <button 
                  className="action-btn download"
                  onClick={handleDownload}
                  title="Download file"
                >
                  <Download size={16} />
                  Download
                </button>
              </div>
            </div>
            <pre className="code-content">
              {activeTab === 'solidity' ? (
                <code 
                  dangerouslySetInnerHTML={{ 
                    __html: highlightSolidity(data.solidity) 
                  }} 
                />
              ) : (
                <code>{data.abi}</code>
              )}
            </pre>
          </div>

          {/* Functions and Events */}
          {(data.functions?.length > 0 || data.events?.length > 0) && (
            <div className="contract-info">
              {data.functions?.length > 0 && (
                <div className="info-section">
                  <h4>Functions</h4>
                  <div className="tag-list">
                    {data.functions.map((fn, i) => (
                      <span key={i} className="tag function-tag">{fn}</span>
                    ))}
                  </div>
                </div>
              )}
              {data.events?.length > 0 && (
                <div className="info-section">
                  <h4>Events</h4>
                  <div className="tag-list">
                    {data.events.map((ev, i) => (
                      <span key={i} className="tag event-tag">{ev}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

export default SolidityModal

