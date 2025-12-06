import React from 'react'
import { Handle, Position } from 'reactflow'
import { motion } from 'framer-motion'
import { User, Users, Package, CreditCard, Clock, CheckCircle, Shield, FileText } from 'lucide-react'
import './CustomNode.css'

// Node configuration with colors for filled and ghost states
const NODE_CONFIG = {
  // Contract visualization blocks
  meta: {
    filledColor: '#1D838D',
    ghostColor: 'rgba(29, 131, 141, 0.25)',
    icon: FileText,
    width: 180,
    height: 90,
  },
  party: {
    filledColor: '#4CAF50',
    ghostColor: 'rgba(76, 175, 80, 0.25)',
    icon: User,
    width: 160,
    height: 85,
  },
  deliverable: {
    filledColor: '#FF9800',
    ghostColor: 'rgba(255, 152, 0, 0.25)',
    icon: Package,
    width: 180,
    height: 90,
  },
  payment: {
    filledColor: '#9C27B0',
    ghostColor: 'rgba(156, 39, 176, 0.25)',
    icon: CreditCard,
    width: 160,
    height: 85,
  },
  timeline: {
    filledColor: '#2196F3',
    ghostColor: 'rgba(33, 150, 243, 0.25)',
    icon: Clock,
    width: 160,
    height: 85,
  },
  quality: {
    filledColor: '#00BCD4',
    ghostColor: 'rgba(0, 188, 212, 0.25)',
    icon: CheckCircle,
    width: 180,
    height: 90,
  },
  protection: {
    filledColor: '#F44336',
    ghostColor: 'rgba(244, 67, 54, 0.25)',
    icon: Shield,
    width: 180,
    height: 90,
  },
  special_term: {
    filledColor: '#607D8B',
    ghostColor: 'rgba(96, 125, 139, 0.25)',
    icon: FileText,
    width: 160,
    height: 80,
  },
  // Legacy block types for manual blocks
  asset: {
    filledColor: '#5BC4B8',
    ghostColor: 'rgba(91, 196, 184, 0.25)',
    icon: Package,
    width: 160,
    height: 80,
  },
  amount: {
    filledColor: '#E6C85C',
    ghostColor: 'rgba(230, 200, 92, 0.25)',
    icon: CreditCard,
    width: 160,
    height: 80,
  },
  condition: {
    filledColor: '#E69D6B',
    ghostColor: 'rgba(230, 157, 107, 0.25)',
    icon: CheckCircle,
    width: 160,
    height: 80,
  },
  trigger: {
    filledColor: '#B08BC4',
    ghostColor: 'rgba(176, 139, 196, 0.25)',
    icon: Clock,
    width: 160,
    height: 80,
  },
  timeout: {
    filledColor: '#E85BA3',
    ghostColor: 'rgba(232, 91, 163, 0.25)',
    icon: Clock,
    width: 160,
    height: 80,
  },
  module: {
    filledColor: '#5DB885',
    ghostColor: 'rgba(93, 184, 133, 0.25)',
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

  return (
    <motion.div 
      className={`custom-node ${selected ? 'selected' : ''} ${filled ? 'filled' : 'ghost'}`}
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
          <Icon size={18} className="node-icon" />
          <div className="node-label">{label}</div>
        </div>
        {subtitle && (
          <div className="node-subtitle">{subtitle}</div>
        )}
        {filled && (
          <motion.div 
            className="filled-indicator"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2 }}
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

