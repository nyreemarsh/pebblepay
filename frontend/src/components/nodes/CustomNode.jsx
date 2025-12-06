import React from 'react'
import { Handle, Position } from 'reactflow'
import './CustomNode.css'

// Node configuration with muted tropical colors
const NODE_CONFIG = {
<<<<<<< Updated upstream
  party: {
    color: '#E885A8', // muted coral pink
=======
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
>>>>>>> Stashed changes
    width: 160,
    height: 80,
  },
  asset: {
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    color: '#5BC4B8', // muted turquoise
=======
=======
>>>>>>> Stashed changes
    filledColor: '#D29AE7',
    ghostColor: 'rgba(210, 154, 231, 0.25)',
    icon: Package,
>>>>>>> Stashed changes
    width: 160,
    height: 80,
  },
  amount: {
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    color: '#E6C85C', // muted yellow
=======
=======
>>>>>>> Stashed changes
    filledColor: '#DD70B4',
    ghostColor: 'rgba(221, 112, 180, 0.25)',
    icon: CreditCard,
>>>>>>> Stashed changes
    width: 160,
    height: 80,
  },
  condition: {
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    color: '#E69D6B', // muted orange
=======
=======
>>>>>>> Stashed changes
    filledColor: '#81BDF7',
    ghostColor: 'rgba(129, 189, 247, 0.25)',
    icon: CheckCircle,
>>>>>>> Stashed changes
    width: 160,
    height: 80,
  },
  trigger: {
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    color: '#B08BC4', // muted purple
=======
=======
>>>>>>> Stashed changes
    filledColor: '#F5E6FB',
    ghostColor: 'rgba(245, 230, 251, 0.25)',
    icon: Clock,
>>>>>>> Stashed changes
    width: 160,
    height: 80,
  },
  timeout: {
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    color: '#E85BA3', // muted hot pink
=======
=======
>>>>>>> Stashed changes
    filledColor: '#FBD43B',
    ghostColor: 'rgba(251, 212, 59, 0.25)',
    icon: Clock,
>>>>>>> Stashed changes
    width: 160,
    height: 80,
  },
  module: {
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    color: '#5DB885', // muted green
=======
=======
>>>>>>> Stashed changes
    filledColor: '#F7B2A8',
    ghostColor: 'rgba(247, 178, 168, 0.25)',
    icon: Package,
>>>>>>> Stashed changes
    width: 160,
    height: 80,
  },
}

function CustomNode({ data, selected }) {
  const nodeType = data.type || 'party'
  const config = NODE_CONFIG[nodeType] || NODE_CONFIG.party
<<<<<<< Updated upstream
  const label = data.label || nodeType

  return (
    <div 
      className={`custom-node ${selected ? 'selected' : ''}`}
=======
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
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
      style={{
        width: config.width,
        height: config.height,
        backgroundColor: config.color,
      }}
    >
      {/* Left handle (target) */}
      <Handle
        type="target"
        position={Position.Left}
        id="left"
        style={{
          width: 20,
          height: 20,
          borderRadius: '50%',
          backgroundColor: config.color,
          border: '2px solid white',
        }}
      />

      {/* Node content */}
      <div className="node-content">
<<<<<<< Updated upstream
        <div className="node-label">{label}</div>
        {data.content && (
          <div className="node-content-text">{data.content}</div>
=======
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
>>>>>>> Stashed changes
        )}
      </div>

      {/* Right handle (source) */}
      <Handle
        type="source"
        position={Position.Right}
        id="right"
        style={{
          width: 20,
          height: 20,
          borderRadius: '50%',
          backgroundColor: config.color,
          border: '2px solid white',
        }}
      />
    </div>
  )
}

export default CustomNode

