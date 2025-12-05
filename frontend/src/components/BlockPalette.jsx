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
  { type: 'payment', label: 'Payment', icon: DollarSign, color: 'var(--neon-cyan)' },
  { type: 'party', label: 'Party', icon: Users, color: 'var(--neon-pink)' },
  { type: 'condition', label: 'Condition', icon: Shield, color: 'var(--neon-green)' },
  { type: 'milestone', label: 'Milestone', icon: Calendar, color: 'var(--neon-purple)' },
  { type: 'termination', label: 'Termination', icon: FileText, color: 'var(--neon-cyan)' },
  { type: 'connection', label: 'Connection', icon: LinkIcon, color: 'var(--neon-pink)' },
  { type: 'action', label: 'Action', icon: Zap, color: 'var(--neon-green)' },
]

function BlockPalette({ onAddBlock }) {
  return (
    <div className="block-palette">
      <div className="palette-header">
        <h2>Block Library</h2>
        <p className="palette-subtitle">Drag blocks to canvas</p>
      </div>
      
      <div className="palette-blocks">
        {blockTypes.map((block, index) => (
          <motion.div
            key={block.type}
            className="palette-block"
            draggable={true}
            onDragStart={(e) => {
              e.dataTransfer.setData('nodeType', block.type)
              e.dataTransfer.effectAllowed = 'copy'
            }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.05, y: -5 }}
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
  )
}

export default BlockPalette

