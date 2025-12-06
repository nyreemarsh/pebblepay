import React from 'react'
import { motion } from 'framer-motion'
import { 
  Wallet, 
  Users, 
  DollarSign, 
  Calendar, 
  FileText, 
  Shield,
  Zap
} from 'lucide-react'
import './CompactBlockPalette.css'

const blockTypes = [
  { type: 'party', label: 'party', icon: Users, color: '#E885A8', description: 'Define parties involved in the contract' },
  { type: 'asset', label: 'asset', icon: DollarSign, color: '#5BC4B8', description: 'Specify assets or deliverables' },
  { type: 'amount', label: 'amount', icon: DollarSign, color: '#E6C85C', description: 'Set payment amounts and pricing' },
  { type: 'condition', label: 'condition', icon: Shield, color: '#E69D6B', description: 'Add conditions and requirements' },
  { type: 'trigger', label: 'trigger', icon: Zap, color: '#B08BC4', description: 'Define event triggers' },
  { type: 'timeout', label: 'timeout', icon: Calendar, color: '#E85BA3', description: 'Set deadlines and time limits' },
  { type: 'module', label: 'module', icon: FileText, color: '#5DB885', description: 'Add contract modules' },
]

function CompactBlockPalette({ onAddBlock }) {
  return (
    <div className="compact-block-palette">
      <div className="compact-blocks-container">
        {blockTypes.map((block, index) => (
          <motion.div
            key={block.type}
            className="compact-block-wrapper"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.05 }}
          >
            <motion.button
              className="compact-block"
              draggable={true}
              onDragStart={(e) => {
                e.dataTransfer.setData('application/reactflow', block.type)
                e.dataTransfer.effectAllowed = 'move'
              }}
              onClick={() => onAddBlock(block.type)}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              style={{ '--block-color': block.color }}
            >
              <block.icon size={20} />
            </motion.button>
            <div className="compact-block-tooltip">
              <div className="tooltip-label">{block.label}</div>
              <div className="tooltip-description">{block.description}</div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

export default CompactBlockPalette

