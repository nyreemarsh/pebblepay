import React from 'react'
import { Handle, Position } from 'reactflow'
import { motion } from 'framer-motion'
import { User, Users, Package, CreditCard, Clock, CheckCircle, Shield, FileText } from 'lucide-react'
import './CustomNode.css'

// Node configuration with colors for filled and ghost states
const NODE_CONFIG = {
  // Contract visualization blocks
  meta: {
    filledColor: '#81BDF7',
    ghostColor: 'rgba(129, 189, 247, 0.25)',
    icon: FileText,
    width: 180,
    height: 90,
  },
  party: {
    filledColor: '#78BEB1',
    ghostColor: 'rgba(120, 190, 177, 0.25)',
    icon: User,
    width: 160,
    height: 85,
  },
  deliverable: {
    filledColor: '#D29AE7',
    ghostColor: 'rgba(210, 154, 231, 0.25)',
    icon: Package,
    width: 180,
    height: 90,
  },
  payment: {
    filledColor: '#DD70B4',
    ghostColor: 'rgba(221, 112, 180, 0.25)',
    icon: CreditCard,
    width: 160,
    height: 85,
  },
  timeline: {
    filledColor: '#FBD43B',
    ghostColor: 'rgba(251, 212, 59, 0.25)',
    icon: Clock,
    width: 160,
    height: 85,
  },
  quality: {
    filledColor: '#F7B2A8',
    ghostColor: 'rgba(247, 178, 168, 0.25)',
    icon: CheckCircle,
    width: 180,
    height: 90,
  },
  protection: {
    filledColor: '#F5E6FB',
    ghostColor: 'rgba(245, 230, 251, 0.25)',
    icon: Shield,
    width: 180,
    height: 90,
  },
  special_term: {
    filledColor: '#81BDF7',
    ghostColor: 'rgba(129, 189, 247, 0.25)',
    icon: FileText,
    width: 160,
    height: 80,
  },
  // Legacy block types for manual blocks
  asset: {
    filledColor: '#D29AE7',
    ghostColor: 'rgba(210, 154, 231, 0.25)',
    icon: Package,
    width: 160,
    height: 80,
  },
  amount: {
    filledColor: '#DD70B4',
    ghostColor: 'rgba(221, 112, 180, 0.25)',
    icon: CreditCard,
    width: 160,
    height: 80,
  },
  condition: {
    filledColor: '#81BDF7',
    ghostColor: 'rgba(129, 189, 247, 0.25)',
    icon: CheckCircle,
    width: 160,
    height: 80,
  },
  trigger: {
    filledColor: '#F5E6FB',
    ghostColor: 'rgba(245, 230, 251, 0.25)',
    icon: Clock,
    width: 160,
    height: 80,
  },
  timeout: {
    filledColor: '#FBD43B',
    ghostColor: 'rgba(251, 212, 59, 0.25)',
    icon: Clock,
    width: 160,
    height: 80,
  },
  module: {
    filledColor: '#F7B2A8',
    ghostColor: 'rgba(247, 178, 168, 0.25)',
    icon: Package,
    width: 160,
    height: 80,
  },
}

function CustomNode({ data, selected }) {
  const nodeType = data.type || 'party'
  const config = NODE_CONFIG[nodeType] || NODE_CONFIG.party
  const label = data.label || data.title || nodeType
  const subtitle = data.subtitle || data.content || ''
  const filled = data.filled !== undefined ? data.filled : true
  const isNew = data.isNew || false
  
  const Icon = config.icon || FileText
  const bgColor = filled ? config.filledColor : config.ghostColor
  const borderColor = filled ? config.filledColor : 'rgba(255, 255, 255, 0.3)'
  
  // Special handling for trigger and protection blocks (F5E6FB) - use dark text
  const isTrigger = nodeType === 'trigger'
  const isProtection = nodeType === 'protection'
  const needsDarkText = isTrigger || isProtection
  const textColor = needsDarkText ? '#6B5353' : '#FFFFFF'
  const iconColor = needsDarkText ? '#6B5353' : '#FFFFFF'

  return (
    <motion.div 
      className={`custom-node ${selected ? 'selected' : ''} ${filled ? 'filled' : 'ghost'} ${needsDarkText ? 'trigger-block' : ''}`}
      style={{
        width: config.width,
        height: config.height,
        backgroundColor: bgColor,
        borderColor: borderColor,
      }}
      initial={isNew ? { scale: 0, opacity: 0 } : { scale: 1, opacity: 1 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ 
        type: 'spring', 
        stiffness: 500, 
        damping: 25,
        duration: 0.4 
      }}
    >
      {/* Left handle (target) */}
      <Handle
        type="target"
        position={Position.Left}
        id="left"
        style={{
          width: 16,
          height: 16,
          borderRadius: '50%',
          backgroundColor: filled ? config.filledColor : 'rgba(255,255,255,0.3)',
          border: '2px solid white',
        }}
      />

      {/* Node content */}
      <div className="node-content">
        <div className="node-header">
          <Icon size={18} className="node-icon" style={{ color: iconColor }} />
          <div className="node-label" style={{ color: textColor }}>{label}</div>
        </div>
        {subtitle && (
          <div className="node-subtitle" style={{ color: textColor }}>{subtitle}</div>
        )}
        {filled && (
          <motion.div 
            className="filled-indicator"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2 }}
            style={{ color: textColor }}
          >
            ✓
          </motion.div>
        )}
      </div>

      {/* Right handle (source) */}
      <Handle
        type="source"
        position={Position.Right}
        id="right"
        style={{
          width: 16,
          height: 16,
          borderRadius: '50%',
          backgroundColor: filled ? config.filledColor : 'rgba(255,255,255,0.3)',
          border: '2px solid white',
        }}
      />
    </motion.div>
  )
}

export default CustomNode

