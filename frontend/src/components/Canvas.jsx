import React, { useCallback, useRef, useState } from 'react'
import ReactFlow, {
  ReactFlowProvider,
  useNodesState,
  useEdgesState,
  Background,
} from 'reactflow'
import { motion } from 'framer-motion'
import { Trash2 } from 'lucide-react'
import 'reactflow/dist/style.css'
import CustomNode from './nodes/CustomNode'
import './Canvas.css'

// Register custom node type
const nodeTypes = {
  custom: CustomNode,
}

function CanvasFlow({
  blocks,
  onBlocksChange,
  onNodeSelect,
  selectedNodeId,
  edges: externalEdges,
  onEdgesChange,
  onDeleteBlock,
}) {
  const reactFlowWrapper = useRef(null)
  const [reactFlowInstance, setReactFlowInstance] = useState(null)
  const [isOverBin, setIsOverBin] = useState(false)
  const [draggedNodeId, setDraggedNodeId] = useState(null)

  // Convert blocks to React Flow nodes format
  const initialNodes = blocks.map((block) => ({
    id: block.id,
    type: 'custom',
    position: block.position,
    data: {
      ...block.data,
      type: block.type, // Ensure type is passed to the node
      label: block.data?.label || block.type,
    },
    selected: selectedNodeId === block.id,
  }))

  // Convert edges to React Flow edges format
  const initialEdges = (externalEdges || []).map((edge) => ({
    id: edge.id || `edge-${edge.from}-${edge.to}`,
    source: edge.from,
    target: edge.to,
    sourceHandle: edge.fromSide || 'right',
    targetHandle: edge.toSide || 'left',
    style: { stroke: '#FFFFFF', strokeWidth: 2 },
    markerEnd: {
      type: 'arrowclosed',
      color: '#FFFFFF',
    },
  }))

  const edgesRef = useRef(initialEdges)

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChangeInternal] = useEdgesState(initialEdges)

  // Sync external blocks/edges changes to React Flow state
  React.useEffect(() => {
    const newNodes = blocks.map((block) => ({
      id: block.id,
      type: 'custom',
      position: block.position,
      data: {
        ...block.data,
        type: block.type,
      },
      selected: selectedNodeId === block.id,
    }))
    setNodes(newNodes)
  }, [blocks, selectedNodeId, setNodes])

  React.useEffect(() => {
    const newEdges = (externalEdges || []).map((edge) => ({
      id: edge.id || `edge-${edge.from}-${edge.to}`,
      source: edge.from,
      target: edge.to,
      sourceHandle: edge.fromSide || 'right',
      targetHandle: edge.toSide || 'left',
      style: { stroke: '#FFFFFF', strokeWidth: 2 },
      markerEnd: {
        type: 'arrowclosed',
        color: '#FFFFFF',
      },
    }))
    setEdges(newEdges)
    edgesRef.current = newEdges
  }, [externalEdges, setEdges])

  // Handle edge changes from React Flow and sync to parent
  const handleEdgesChange = useCallback(
    (changes) => {
      onEdgesChangeInternal(changes)
      
      // Apply changes to get updated edges
      let updatedEdges = [...edgesRef.current]
      
      changes.forEach((change) => {
        if (change.type === 'remove') {
          updatedEdges = updatedEdges.filter((e) => e.id !== change.id)
        }
      })
      
      edgesRef.current = updatedEdges
      
      // Convert to our format and notify parent
      const convertedEdges = updatedEdges.map((edge) => ({
        id: edge.id,
        from: edge.source,
        fromSide: edge.sourceHandle || 'right',
        to: edge.target,
        toSide: edge.targetHandle || 'left',
      }))
      
      if (onEdgesChange) {
        onEdgesChange(convertedEdges)
      }
    },
    [onEdgesChangeInternal, onEdgesChange]
  )

  // Handle drag from sidebar
  const onDragOver = useCallback((event) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])

  const onDrop = useCallback(
    (event) => {
      event.preventDefault()

      const nodeType = event.dataTransfer.getData('application/reactflow')
      if (!nodeType || !reactFlowInstance) {
        return
      }

      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect()
      const position = reactFlowInstance.project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      })

    const newBlock = {
      id: `${nodeType}-${Date.now()}`,
      type: nodeType, // Block type (party, asset, etc.)
      position,
      data: {
        label: nodeType,
        content: '',
      },
    }

    onBlocksChange([...blocks, newBlock])
    },
    [reactFlowInstance, blocks, onBlocksChange]
  )

  // Handle node changes (position updates)
  const onNodesChangeInternal = useCallback(
    (changes) => {
      onNodesChange(changes)

      // Update block positions when nodes are dragged
      changes.forEach((change) => {
        if (change.type === 'position' && change.position) {
          const updatedBlocks = blocks.map((block) =>
            block.id === change.id
              ? { ...block, position: change.position }
              : block
          )
          onBlocksChange(updatedBlocks)
        }
      })
    },
    [blocks, onBlocksChange, onNodesChange]
  )

  // Handle edge connections
  const onConnect = useCallback(
    (params) => {
      const newEdge = {
        id: `edge-${params.source}-${params.target}-${Date.now()}`,
        from: params.source,
        fromSide: params.sourceHandle || 'right',
        to: params.target,
        toSide: params.targetHandle || 'left',
      }
      if (onEdgesChange) {
        onEdgesChange([...(externalEdges || []), newEdge])
      }
      // Also update the ref
      const rfEdge = {
        id: newEdge.id,
        source: params.source,
        target: params.target,
        sourceHandle: params.sourceHandle || 'right',
        targetHandle: params.targetHandle || 'left',
        style: { stroke: '#FFFFFF', strokeWidth: 2 },
        markerEnd: {
          type: 'arrowclosed',
          color: '#FFFFFF',
        },
      }
      edgesRef.current = [...edgesRef.current, rfEdge]
    },
    [externalEdges, onEdgesChange]
  )

  // Handle node selection
  const onNodeClick = useCallback(
    (event, node) => {
      if (onNodeSelect) {
        onNodeSelect(node.id === selectedNodeId ? null : node.id)
    }
    },
    [selectedNodeId, onNodeSelect]
  )

  // Handle pane click (deselect)
  const onPaneClick = useCallback(() => {
    if (onNodeSelect) {
      onNodeSelect(null)
    }
  }, [onNodeSelect])

  // Handle node drag to check if over bin
  const onNodeDrag = useCallback((event, node) => {
    if (!reactFlowWrapper.current) return
    
    const rect = reactFlowWrapper.current.getBoundingClientRect()
    const binAreaTop = rect.height - 100
    const nodeY = event.clientY - rect.top
    
    setIsOverBin(nodeY > binAreaTop)
    setDraggedNodeId(node.id)
  }, [])

  const onNodeDragStop = useCallback(
    (event, node) => {
    if (isOverBin && onDeleteBlock) {
        onDeleteBlock(node.id)
      setIsOverBin(false)
        setDraggedNodeId(null)
      return
    }
    
      setIsOverBin(false)
    setDraggedNodeId(null)
    },
    [isOverBin, onDeleteBlock]
  )

  return (
    <div className="canvas-wrapper" ref={reactFlowWrapper}>
      {/* Bokeh effect background */}
      <div className="bokeh-container">
        <div className="bokeh-circle bokeh-1"></div>
        <div className="bokeh-circle bokeh-2"></div>
        <div className="bokeh-circle bokeh-3"></div>
        <div className="bokeh-circle bokeh-4"></div>
        <div className="bokeh-circle bokeh-5"></div>
        <div className="bokeh-circle bokeh-6"></div>
      </div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChangeInternal}
        onEdgesChange={handleEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        onNodeDrag={onNodeDrag}
        onNodeDragStop={onNodeDragStop}
        onInit={setReactFlowInstance}
        onDrop={onDrop}
        onDragOver={onDragOver}
        nodeTypes={nodeTypes}
        fitView
        proOptions={{ hideAttribution: true }}
        style={{ background: 'transparent' }}
      >
        <Background color="transparent" gap={16} />
      </ReactFlow>

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
          scale: isOverBin ? 1.15 : 1,
        }}
        transition={{ type: 'spring', stiffness: 200 }}
      >
        <motion.div
          className="bin-icon"
          animate={{ 
            rotate: isOverBin ? [0, -10, 10, -10, 0] : 0,
            scale: isOverBin ? 1.2 : 1,
          }}
          transition={{ duration: 0.3 }}
        >
          <Trash2 size={24} />
        </motion.div>
      </motion.div>
    </div>
  )
}

function Canvas({
  blocks,
  onBlocksChange,
  onNodeSelect,
  selectedNodeId,
  edges,
  onEdgesChange,
  onDeleteBlock,
}) {
  return (
    <ReactFlowProvider>
      <CanvasFlow
        blocks={blocks}
        onBlocksChange={onBlocksChange}
        onNodeSelect={onNodeSelect}
        selectedNodeId={selectedNodeId}
        edges={edges}
        onEdgesChange={onEdgesChange}
        onDeleteBlock={onDeleteBlock}
      />
    </ReactFlowProvider>
  )
}

export default Canvas
