import React from 'react'
import { Handle, Position } from 'reactflow'
import './CustomNode.css'

// Node configuration matching the original design
const NODE_CONFIG = {
  party: {
    color: '#31A667', // green
    width: 160,
    height: 80,
  },
  asset: {
    color: '#A8D6A8', // light green (neon-pink in vars)
    width: 160,
    height: 80,
  },
  amount: {
    color: '#31A667', // green
    width: 160,
    height: 80,
  },
  condition: {
    color: '#B7D0E3', // light blue (neon-purple in vars)
    width: 160,
    height: 80,
  },
  trigger: {
    color: '#1D838D', // teal (neon-cyan)
    width: 160,
    height: 80,
  },
  timeout: {
    color: '#A8D6A8', // light green (neon-pink in vars)
    width: 160,
    height: 80,
  },
  module: {
    color: '#31A667', // green
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

