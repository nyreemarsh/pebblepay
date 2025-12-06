import React from 'react'
import { motion } from 'framer-motion'
import { 
  Wallet, 
  Users, 
  DollarSign, 
  Calendar, 
  FileText, 
  Shield,
  Link as LinkIcon,
  Zap
} from 'lucide-react'
import './BlockPalette.css'

const blockTypes = [
  { type: 'party', label: 'party', icon: Users, color: 'var(--neon-cyan)' },
  { type: 'asset', label: 'asset', icon: DollarSign, color: 'var(--neon-pink)' },
  { type: 'amount', label: 'amount', icon: DollarSign, color: 'var(--neon-green)' },
  { type: 'condition', label: 'condition', icon: Shield, color: 'var(--neon-purple)' },
  { type: 'trigger', label: 'trigger', icon: Zap, color: 'var(--neon-cyan)' },
  { type: 'timeout', label: 'timeout', icon: Calendar, color: 'var(--neon-pink)' },
  { type: 'module', label: 'module', icon: FileText, color: 'var(--neon-green)' },
]

function BlockPalette({ onAddBlock }) {
  return (
    <div className="block-palette">
      {/* Fixed Logo Section */}
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

      {/* Scrollable Block Garden Section */}
      <div className="palette-scrollable">
        <div className="palette-header">
          <h2>Pibble's Block Garden</h2>
        </div>
        
        <div className="palette-blocks">
          {blockTypes.map((block, index) => (
            <motion.div
              key={block.type}
              className="palette-block"
              draggable={true}
              onDragStart={(e) => {
                e.dataTransfer.setData('application/reactflow', block.type)
                e.dataTransfer.effectAllowed = 'move'
              }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onAddBlock(block.type)}
              style={{ '--block-color': block.color }}
            >
              <div className="block-icon-wrapper">
                <block.icon size={24} />
              </div>
              <span className="block-label">{block.label}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default BlockPalette

