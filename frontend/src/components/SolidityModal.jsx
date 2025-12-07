import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Copy, Check, Download, Code, FileText, Zap, FileCode, Maximize2, Minimize2 } from 'lucide-react'
import './SolidityModal.css'

function SolidityModal({ data, onClose }) {
  const [copied, setCopied] = useState(false)
  const [activeTab, setActiveTab] = useState('solidity')
  const [isCodeExpanded, setIsCodeExpanded] = useState(false)

  const handleCopy = async () => {
    try {
      let textToCopy
      if (activeTab === 'solidity') {
        textToCopy = data.solidity
      } else if (activeTab === 'neo') {
        textToCopy = data.neo_python || ''
      } else {
        textToCopy = data.abi
      }
      await navigator.clipboard.writeText(textToCopy)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const handleDownload = () => {
    let content, filename, mimeType
    if (activeTab === 'solidity') {
      content = data.solidity
      filename = `${data.contractName || 'Contract'}.sol`
      mimeType = 'text/plain'
    } else if (activeTab === 'neo') {
      content = data.neo_python || ''
      filename = `${data.contractName || 'Contract'}.py`
      mimeType = 'text/plain'
    } else {
      content = data.abi
      filename = `${data.contractName || 'Contract'}_abi.json`
      mimeType = 'application/json'
    }
    
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

  // Simple syntax highlighting for Python (Neo Boa)
  const highlightPython = (code) => {
    if (!code) return ''
    
    // Escape HTML first to prevent injection
    const escapeHtml = (text) => {
      const div = document.createElement('div')
      div.textContent = text
      return div.innerHTML
    }
    
    let highlighted = escapeHtml(code)
    
    // Python keywords (must come before types to avoid conflicts)
    const keywords = ['def', 'class', 'if', 'else', 'elif', 'for', 'while', 'try', 'except',
                     'finally', 'with', 'as', 'import', 'from', 'return', 'yield', 'pass',
                     'break', 'continue', 'assert', 'raise', 'lambda', 'and', 'or', 'not',
                     'in', 'is', 'None', 'True', 'False', 'async', 'await', 'global', 'nonlocal']
    
    // Neo Boa specific keywords and decorators
    const neoKeywords = ['@public', '@private', 'CreateNewEvent', 'CheckWitness', 'get', 'put']
    
    // Types (must come after keywords)
    const types = ['UInt160', 'UInt256', 'ByteString', 'int', 'str', 'bool', 'bytes', 'list', 'dict']
    
    // Process in order: comments first, then strings, then keywords/types, then numbers
    // Comments (handle # comments)
    highlighted = highlighted.replace(/(#.*$)/gm, '<span class="comment">$1</span>')
    
    // Docstrings (handle """ and ''' docstrings)
    highlighted = highlighted.replace(/("""[\s\S]*?""")/g, '<span class="comment">$1</span>')
    highlighted = highlighted.replace(/('''[\s\S]*?''')/g, '<span class="comment">$1</span>')
    
    // Strings (but skip if already in a comment span)
    highlighted = highlighted.replace(/(&quot;.*?&quot;)/g, '<span class="string">$1</span>')
    highlighted = highlighted.replace(/(&#x27;.*?&#x27;)/g, '<span class="string">$1</span>')
    
    // Neo Boa keywords first (more specific)
    neoKeywords.forEach(kw => {
      const escapedKw = escapeHtml(kw)
      const regex = new RegExp(`\\b(${escapedKw.replace('@', '&#64;')})\\b`, 'g')
      highlighted = highlighted.replace(regex, '<span class="keyword">$1</span>')
    })
    
    // Python keywords
    keywords.forEach(kw => {
      const escapedKw = escapeHtml(kw)
      const regex = new RegExp(`\\b(${escapedKw})\\b`, 'g')
      highlighted = highlighted.replace(regex, '<span class="keyword">$1</span>')
    })
    
    // Types
    types.forEach(t => {
      const escapedT = escapeHtml(t)
      const regex = new RegExp(`\\b(${escapedT})\\b`, 'g')
      highlighted = highlighted.replace(regex, '<span class="type">$1</span>')
    })
    
    // Numbers (last, to avoid conflicts)
    highlighted = highlighted.replace(/\b(\d+)\b/g, '<span class="number">$1</span>')
    
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
              <img 
                src="/assets/images/logos/pibble_coin_real.png" 
                alt="Pibble Coin" 
                className="modal-logo"
                onError={(e) => {
                  e.target.style.display = 'none'
                }}
              />
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
            <button
              className={`tab ${activeTab === 'neo' ? 'active' : ''}`}
              onClick={() => setActiveTab('neo')}
            >
              <FileCode size={16} />
              Neo Python
            </button>
          </div>

          {/* Code Display */}
          <div className="code-container">
            <div className="code-header">
              <span className="filename">
                {activeTab === 'solidity' 
                  ? `${data.contractName || 'Contract'}.sol`
                  : activeTab === 'neo'
                  ? `${data.contractName || 'Contract'}.py`
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
                  className="action-btn expand-btn"
                  onClick={() => setIsCodeExpanded(!isCodeExpanded)}
                  title={isCodeExpanded ? "Minimize" : "Expand code view"}
                >
                  {isCodeExpanded ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
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
              ) : activeTab === 'neo' ? (
                <code 
                  dangerouslySetInnerHTML={{ 
                    __html: highlightPython(data.neo_python || '# Neo contract code will appear here\n# If this message appears, the Neo contract generation may have failed.\n# Check the backend terminal for error details.')
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

        {/* Expanded Code Popup */}
        <AnimatePresence>
          {isCodeExpanded && (
            <motion.div
              className="code-expanded-overlay"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsCodeExpanded(false)}
            >
              <motion.div
                className="code-expanded-popup"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                onClick={(e) => e.stopPropagation()}
              >
                <div className="code-expanded-header">
                  <span className="code-expanded-filename">
                    {activeTab === 'solidity' 
                      ? `${data.contractName || 'Contract'}.sol`
                      : activeTab === 'neo'
                      ? `${data.contractName || 'Contract'}.py`
                      : `${data.contractName || 'Contract'}_abi.json`}
                  </span>
                  <div className="code-expanded-actions">
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
                    <button 
                      className="action-btn expand-btn"
                      onClick={() => setIsCodeExpanded(false)}
                      title="Close expanded view"
                    >
                      <Minimize2 size={16} />
                    </button>
                  </div>
                </div>
                <pre className="code-expanded-content">
                  {activeTab === 'solidity' ? (
                    <code 
                      dangerouslySetInnerHTML={{ 
                        __html: highlightSolidity(data.solidity) 
                      }} 
                    />
                  ) : activeTab === 'neo' ? (
                    <code 
                      dangerouslySetInnerHTML={{ 
                        __html: data.neo_python 
                          ? highlightPython(data.neo_python)
                          : highlightPython('# Neo contract code will appear here\n# If this message appears, the Neo contract generation may have failed.\n# Check the backend terminal for error details.')
                      }} 
                    />
                  ) : (
                    <code>{data.abi}</code>
                  )}
                </pre>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </AnimatePresence>
  )
}

export default SolidityModal

