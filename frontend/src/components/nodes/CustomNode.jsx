import React from 'react'
import { Handle, Position } from 'reactflow'
import './CustomNode.css'

// Node configuration with muted tropical colors
const NODE_CONFIG = {
  party: {
    color: '#E885A8', // muted coral pink
    width: 160,
    height: 80,
  },
  asset: {
    color: '#5BC4B8', // muted turquoise
    width: 160,
    height: 80,
  },
  amount: {
    color: '#E6C85C', // muted yellow
    width: 160,
    height: 80,
  },
  condition: {
    color: '#E69D6B', // muted orange
    width: 160,
    height: 80,
  },
  trigger: {
    color: '#B08BC4', // muted purple
    width: 160,
    height: 80,
  },
  timeout: {
    color: '#E85BA3', // muted hot pink
    width: 160,
    height: 80,
  },
  module: {
    color: '#5DB885', // muted green
    width: 160,
    height: 80,
  },
}

function CustomNode({ data, selected }) {
  const nodeType = data.type || 'party'
  const config = NODE_CONFIG[nodeType] || NODE_CONFIG.party
  const label = data.label || nodeType

  return (
    <div 
      className={`custom-node ${selected ? 'selected' : ''}`}
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
        <div className="node-label">{label}</div>
        {data.content && (
          <div className="node-content-text">{data.content}</div>
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

