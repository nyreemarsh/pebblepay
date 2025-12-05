import React, { useRef, useState, useCallback, useEffect } from 'react'
import { Stage, Layer, Group, Rect, Text, Circle, Arrow, Line } from 'react-konva'
import { motion } from 'framer-motion'
import { Trash2 } from 'lucide-react'
import './Canvas.css'

// Node configuration with new color palette
const NODE_CONFIG = {
  payment: {
    color: '#1D838D', // teal
    icon: '💰',
    width: 160,
    height: 80,
  },
  party: {
    color: '#31A667', // green
    icon: '👥',
    width: 160,
    height: 80,
  },
  condition: {
    color: '#A8D6A8', // light green
    icon: '🛡️',
    width: 160,
    height: 80,
  },
  milestone: {
    color: '#B7D0E3', // light blue
    icon: '📅',
    width: 160,
    height: 80,
  },
  termination: {
    color: '#1D838D', // teal
    icon: '📄',
    width: 160,
    height: 80,
  },
  connection: {
    color: '#31A667', // green
    icon: '🔗',
    width: 160,
    height: 80,
  },
  action: {
    color: '#A8D6A8', // light green
    icon: '⚡',
    width: 160,
    height: 80,
  },
}

function Canvas({ blocks, onBlocksChange, onNodeSelect, selectedNodeId, edges = [], onEdgesChange, onDeleteBlock }) {
  const stageRef = useRef(null)
  const [isDragging, setIsDragging] = useState(false)
  const [connectingFrom, setConnectingFrom] = useState(null)
  const [tempLineEnd, setTempLineEnd] = useState(null)
  const [draggedNodeId, setDraggedNodeId] = useState(null)
  const [isOverBin, setIsOverBin] = useState(false)
  const [draggedBlockId, setDraggedBlockId] = useState(null)
  const [stageSize, setStageSize] = useState({
    width: window.innerWidth - 630,
    height: window.innerHeight - 80,
  })

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      setStageSize({
        width: window.innerWidth - 630,
        height: window.innerHeight - 80,
      })
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // Get connection point position
  const getConnectionPoint = useCallback((nodeId, side) => {
    const node = blocks.find((n) => n.id === nodeId)
    if (!node) return { x: 0, y: 0 }
    const config = NODE_CONFIG[node.type] || NODE_CONFIG.payment
    return {
      x: node.position.x + (side === 'left' ? 0 : config.width),
      y: node.position.y + config.height / 2,
    }
  }, [blocks])

  // Get node center for edge calculations
  const getNodeCenter = useCallback((nodeId) => {
    const node = blocks.find((n) => n.id === nodeId)
    if (!node) return { x: 0, y: 0 }
    const config = NODE_CONFIG[node.type] || NODE_CONFIG.payment
    return {
      x: node.position.x + config.width / 2,
      y: node.position.y + config.height / 2,
    }
  }, [blocks])

  // Handle drop from palette
  const handleDrop = useCallback((e) => {
    e.preventDefault()
    const nodeType = e.dataTransfer.getData('nodeType')
    if (!nodeType || !stageRef.current) return

    const stage = stageRef.current.getStage()
    const pos = stage.getPointerPosition()
    if (!pos) return

    const config = NODE_CONFIG[nodeType] || NODE_CONFIG.payment
    const newNode = {
      id: `${nodeType}-${Date.now()}`,
      type: nodeType,
      position: {
        x: pos.x - config.width / 2,
        y: pos.y - config.height / 2,
      },
      data: {
        label: nodeType.charAt(0).toUpperCase() + nodeType.slice(1),
        content: '',
      },
    }

    onBlocksChange([...blocks, newNode])
  }, [blocks, onBlocksChange])

  // Handle drag over
  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'copy'
  }, [])

  // Handle connection point drag start or click
  const handleConnectionStart = useCallback((nodeId, side, e) => {
    if (e) {
      e.cancelBubble = true
      e.evt?.stopPropagation()
    }
    setConnectingFrom({ nodeId, side })
    const point = getConnectionPoint(nodeId, side)
    setTempLineEnd(point)
  }, [getConnectionPoint])

  // Handle connection point click (alternative to drag)
  const handleConnectionClick = useCallback((nodeId, side, e) => {
    e.cancelBubble = true
    e.evt?.stopPropagation()
    
    if (connectingFrom && connectingFrom.nodeId !== nodeId) {
      // Complete connection
      const newEdge = {
        id: `edge-${connectingFrom.nodeId}-${nodeId}-${Date.now()}`,
        from: connectingFrom.nodeId,
        fromSide: connectingFrom.side,
        to: nodeId,
        toSide: side,
      }
      
      if (onEdgesChange) {
        onEdgesChange([...edges, newEdge])
      }
      setConnectingFrom(null)
      setTempLineEnd(null)
    } else if (!connectingFrom) {
      // Start new connection
      handleConnectionStart(nodeId, side, e)
    } else {
      // Cancel connection if clicking same point
      setConnectingFrom(null)
      setTempLineEnd(null)
    }
  }, [connectingFrom, edges, onEdgesChange, handleConnectionStart])

  // Handle connection point drag
  const handleConnectionDrag = useCallback((e) => {
    if (!connectingFrom || !stageRef.current) return
    const stage = stageRef.current.getStage()
    const pos = stage.getPointerPosition()
    if (pos) {
      setTempLineEnd(pos)
    }
  }, [connectingFrom])

  // Handle connection point drag end
  const handleConnectionEnd = useCallback((targetNodeId, targetSide, e) => {
    if (!connectingFrom) return
    e.cancelBubble = true

    // Check if dropped on a connection point
    if (targetNodeId && targetNodeId !== connectingFrom.nodeId) {
      const newEdge = {
        id: `edge-${connectingFrom.nodeId}-${targetNodeId}-${Date.now()}`,
        from: connectingFrom.nodeId,
        fromSide: connectingFrom.side,
        to: targetNodeId,
        toSide: targetSide,
      }
      
      if (onEdgesChange) {
        onEdgesChange([...edges, newEdge])
      }
    }

    setConnectingFrom(null)
    setTempLineEnd(null)
  }, [connectingFrom, edges, onEdgesChange])

  // Handle node drag
  const handleNodeDragStart = useCallback((nodeId, e) => {
    setIsDragging(true)
    setDraggedNodeId(nodeId)
    setDraggedBlockId(nodeId)
  }, [])

  const handleNodeDrag = useCallback((nodeId, e) => {
    // Check if over bin area (bottom 100px of canvas)
    const stage = e.target.getStage()
    const pointerPos = stage.getPointerPosition()
    if (pointerPos) {
      const binAreaTop = stageSize.height - 100
      setIsOverBin(pointerPos.y > binAreaTop)
    }
  }, [stageSize.height])

  const handleNodeDragEnd = useCallback((nodeId, newX, newY) => {
    // Check if dropped over bin
    if (isOverBin && onDeleteBlock) {
      onDeleteBlock(nodeId)
      setIsOverBin(false)
      setDraggedBlockId(null)
      setIsDragging(false)
      return
    }
    
    // Update block position to new location
    onBlocksChange(blocks.map((block) =>
      block.id === nodeId
        ? { ...block, position: { x: newX, y: newY } }
        : block
    ))
    
    setIsDragging(false)
    setDraggedNodeId(null)
    setDraggedBlockId(null)
    setIsOverBin(false)
  }, [blocks, isOverBin, onBlocksChange, onDeleteBlock])

  // Handle node click
  const handleNodeClick = useCallback((nodeId, e) => {
    if (e) e.cancelBubble = true
    if (onNodeSelect) {
      onNodeSelect(nodeId === selectedNodeId ? null : nodeId)
    }
  }, [selectedNodeId, onNodeSelect])

  // Handle stage click (deselect)
  const handleStageClick = useCallback((e) => {
    const clickedOnEmpty = e.target === e.target.getStage()
    if (clickedOnEmpty) {
      if (onNodeSelect) onNodeSelect(null)
      if (connectingFrom) {
        setConnectingFrom(null)
        setTempLineEnd(null)
      }
    }
  }, [connectingFrom, onNodeSelect])

  // Handle mouse move for connection line
  useEffect(() => {
    if (!connectingFrom) return

    const handleMouseMove = (e) => {
      if (!stageRef.current) return
      const stage = stageRef.current.getStage()
      const pointerPos = stage.getPointerPosition()
      if (pointerPos) {
        setTempLineEnd(pointerPos)
      }
    }

    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [connectingFrom])

  return (
    <div
      className="canvas-wrapper"
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onMouseMove={handleConnectionDrag}
    >
      <Stage
        ref={stageRef}
        width={stageSize.width}
        height={stageSize.height}
        onClick={handleStageClick}
        onTap={handleStageClick}
        style={{ background: 'var(--bg-primary)' }}
      >
        <Layer>
          {/* Draw edges BEFORE nodes (so they appear behind) */}
          {edges.map((edge) => {
            const fromPoint = getConnectionPoint(edge.from, edge.fromSide || 'right')
            const toPoint = getConnectionPoint(edge.to, edge.toSide || 'left')
            return (
              <Group key={edge.id}>
                <Arrow
                  points={[
                    fromPoint.x,
                    fromPoint.y,
                    toPoint.x,
                    toPoint.y,
                  ]}
                  stroke="#1D838D"
                  strokeWidth={2}
                  fill="#1D838D"
                  pointerLength={10}
                  pointerWidth={8}
                />
              </Group>
            )
          })}

          {/* Temporary connection line while dragging */}
          {connectingFrom && tempLineEnd && (
            <Line
              points={[
                getConnectionPoint(connectingFrom.nodeId, connectingFrom.side).x,
                getConnectionPoint(connectingFrom.nodeId, connectingFrom.side).y,
                tempLineEnd.x,
                tempLineEnd.y,
              ]}
              stroke="#1D838D"
              strokeWidth={2}
              dash={[5, 5]}
            />
          )}

          {/* Render nodes */}
          {blocks.map((node) => {
            const config = NODE_CONFIG[node.type] || NODE_CONFIG.payment
            const isSelected = selectedNodeId === node.id
            const isBeingDragged = draggedNodeId === node.id

            return (
              <Group
                key={node.id}
                id={`node-${node.id}`}
                x={node.position.x}
                y={node.position.y}
                draggable
                onDragStart={(e) => {
                  // Don't drag if clicking on connection point
                  if (e.target.name() === 'connection-point') {
                    e.cancelBubble = true
                    e.evt?.stopPropagation()
                    return false
                  }
                  handleNodeDragStart(node.id, e)
                }}
                onDragMove={(e) => handleNodeDrag(node.id, e)}
                onDragEnd={(e) => {
                  handleNodeDragEnd(node.id, e.target.x(), e.target.y())
                }}
                onClick={(e) => {
                  // Don't select if clicking on connection point
                  if (e.target.name() === 'connection-point') {
                    return
                  }
                  handleNodeClick(node.id, e)
                }}
                onTap={(e) => {
                  if (e.target.name() === 'connection-point') {
                    return
                  }
                  handleNodeClick(node.id, e)
                }}
              >
                {/* Selection highlight */}
                {isSelected && (
                  <Rect
                    x={-6}
                    y={-6}
                    width={config.width + 12}
                    height={config.height + 12}
                    stroke="#31A667"
                    strokeWidth={2}
                    cornerRadius={12}
                    fill="rgba(49, 166, 103, 0.1)"
                  />
                )}

                {/* Base rectangle (flat color) */}
                <Rect
                  width={config.width}
                  height={config.height}
                  cornerRadius={8}
                  fill={config.color}
                />

                {/* Label */}
                <Text
                  x={12}
                  y={20}
                  text={node.data?.label || node.type}
                  fontSize={14}
                  fontFamily="Inter, sans-serif"
                  fontStyle="600"
                  fill="#FFFFFF"
                />

                {/* Content text (if any) */}
                {node.data?.content && (
                  <Text
                    x={12}
                    y={50}
                    text={node.data.content}
                    fontSize={11}
                    fontFamily="Inter, sans-serif"
                    fill="rgba(255, 255, 255, 0.8)"
                    width={config.width - 24}
                    ellipsis
                  />
                )}

                {/* Connection points - Left */}
                <Circle
                  name="connection-point"
                  x={0}
                  y={config.height / 2}
                  radius={10}
                  fill={connectingFrom?.nodeId === node.id && connectingFrom?.side === 'left' ? '#31A667' : config.color}
                  stroke="#FFFFFF"
                  strokeWidth={2}
                  draggable
                  hitFunc={(context, shape) => {
                    // Increase hit area to 20px radius for easier clicking
                    context.beginPath()
                    context.arc(0, 0, 20, 0, Math.PI * 2, true)
                    context.fillStrokeShape(shape)
                  }}
                  onClick={(e) => {
                    e.cancelBubble = true
                    e.evt?.stopPropagation()
                    handleConnectionClick(node.id, 'left', e)
                  }}
                  onTap={(e) => {
                    e.cancelBubble = true
                    e.evt?.stopPropagation()
                    handleConnectionClick(node.id, 'left', e)
                  }}
                  onDragStart={(e) => {
                    e.cancelBubble = true
                    e.evt?.stopPropagation()
                    handleConnectionStart(node.id, 'left', e)
                  }}
                  onDragMove={(e) => {
                    if (!connectingFrom) return
                    const stage = e.target.getStage()
                    const pos = stage.getPointerPosition()
                    if (pos) {
                      setTempLineEnd(pos)
                    }
                  }}
                  onDragEnd={(e) => {
                    e.cancelBubble = true
                    e.evt?.stopPropagation()
                    const stage = e.target.getStage()
                    const pos = stage.getPointerPosition()
                    if (!pos) {
                      setConnectingFrom(null)
                      setTempLineEnd(null)
                      return
                    }
                    // Find which node/connection point was under the cursor
                    let targetNodeId = null
                    let targetSide = null
                    let minDist = 30 // Increased hit radius for easier connection
                    blocks.forEach((block) => {
                      if (block.id === node.id) return
                      const leftPoint = getConnectionPoint(block.id, 'left')
                      const rightPoint = getConnectionPoint(block.id, 'right')
                      const leftDist = Math.sqrt(
                        Math.pow(pos.x - leftPoint.x, 2) + Math.pow(pos.y - leftPoint.y, 2)
                      )
                      const rightDist = Math.sqrt(
                        Math.pow(pos.x - rightPoint.x, 2) + Math.pow(pos.y - rightPoint.y, 2)
                      )
                      if (leftDist < minDist) {
                        minDist = leftDist
                        targetNodeId = block.id
                        targetSide = 'left'
                      } else if (rightDist < minDist) {
                        minDist = rightDist
                        targetNodeId = block.id
                        targetSide = 'right'
                      }
                    })
                    handleConnectionEnd(targetNodeId, targetSide, e)
                  }}
                  onMouseEnter={(e) => {
                    const stage = e.target.getStage()
                    stage.container().style.cursor = 'crosshair'
                  }}
                  onMouseLeave={(e) => {
                    const stage = e.target.getStage()
                    stage.container().style.cursor = 'default'
                  }}
                />

                {/* Connection points - Right */}
                <Circle
                  name="connection-point"
                  x={config.width}
                  y={config.height / 2}
                  radius={10}
                  fill={connectingFrom?.nodeId === node.id && connectingFrom?.side === 'right' ? '#31A667' : config.color}
                  stroke="#FFFFFF"
                  strokeWidth={2}
                  draggable
                  hitFunc={(context, shape) => {
                    // Increase hit area to 20px radius for easier clicking
                    context.beginPath()
                    context.arc(0, 0, 20, 0, Math.PI * 2, true)
                    context.fillStrokeShape(shape)
                  }}
                  onClick={(e) => {
                    e.cancelBubble = true
                    e.evt?.stopPropagation()
                    handleConnectionClick(node.id, 'right', e)
                  }}
                  onTap={(e) => {
                    e.cancelBubble = true
                    e.evt?.stopPropagation()
                    handleConnectionClick(node.id, 'right', e)
                  }}
                  onDragStart={(e) => {
                    e.cancelBubble = true
                    e.evt?.stopPropagation()
                    handleConnectionStart(node.id, 'right', e)
                  }}
                  onDragMove={(e) => {
                    if (!connectingFrom) return
                    const stage = e.target.getStage()
                    const pos = stage.getPointerPosition()
                    if (pos) {
                      setTempLineEnd(pos)
                    }
                  }}
                  onDragEnd={(e) => {
                    e.cancelBubble = true
                    e.evt?.stopPropagation()
                    const stage = e.target.getStage()
                    const pos = stage.getPointerPosition()
                    if (!pos) {
                      setConnectingFrom(null)
                      setTempLineEnd(null)
                      return
                    }
                    let targetNodeId = null
                    let targetSide = null
                    let minDist = 30 // Increased hit radius for easier connection
                    blocks.forEach((block) => {
                      if (block.id === node.id) return
                      const leftPoint = getConnectionPoint(block.id, 'left')
                      const rightPoint = getConnectionPoint(block.id, 'right')
                      const leftDist = Math.sqrt(
                        Math.pow(pos.x - leftPoint.x, 2) + Math.pow(pos.y - leftPoint.y, 2)
                      )
                      const rightDist = Math.sqrt(
                        Math.pow(pos.x - rightPoint.x, 2) + Math.pow(pos.y - rightPoint.y, 2)
                      )
                      if (leftDist < minDist) {
                        minDist = leftDist
                        targetNodeId = block.id
                        targetSide = 'left'
                      } else if (rightDist < minDist) {
                        minDist = rightDist
                        targetNodeId = block.id
                        targetSide = 'right'
                      }
                    })
                    handleConnectionEnd(targetNodeId, targetSide, e)
                  }}
                  onMouseEnter={(e) => {
                    const stage = e.target.getStage()
                    stage.container().style.cursor = 'crosshair'
                  }}
                  onMouseLeave={(e) => {
                    const stage = e.target.getStage()
                    stage.container().style.cursor = 'default'
                  }}
                />
              </Group>
            )
          })}
        </Layer>
      </Stage>

      {blocks.length === 0 && (
        <motion.div
          className="canvas-empty"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <p>Drag blocks from the left panel to start building your contract</p>
        </motion.div>
      )}

      {/* Bin/Trash Button */}
      <motion.div
        className={`canvas-bin ${isOverBin ? 'bin-active' : ''}`}
        initial={{ x: 100, opacity: 0 }}
        animate={{ 
          x: 0, 
          opacity: 1,
          scale: isOverBin ? 1.15 : 1
        }}
        transition={{ type: 'spring', stiffness: 200 }}
      >
        <motion.div
          className="bin-icon"
          animate={{ 
            rotate: isOverBin ? [0, -10, 10, -10, 0] : 0,
            scale: isOverBin ? 1.2 : 1
          }}
          transition={{ duration: 0.3 }}
        >
          <Trash2 size={24} />
        </motion.div>
      </motion.div>
    </div>
  )
}

export default Canvas
