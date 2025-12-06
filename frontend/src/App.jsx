import React, { useState } from 'react'
import { motion } from 'framer-motion'
import BlockPalette from './components/BlockPalette'
import Canvas from './components/Canvas'
import Chatbot from './components/Chatbot'
import GenerateButton from './components/GenerateButton'
import './App.css'

import NodeEditor from './components/NodeEditor'

function App() {
  const [blocks, setBlocks] = useState([])
  const [edges, setEdges] = useState([])
  const [selectedNodeId, setSelectedNodeId] = useState(null)
  const [chatMessages, setChatMessages] = useState([
    {
      id: 1,
      type: 'suggestion',
      text: "Hi! I am Pibble. Let's create your smart contract! What type of contract are you looking to build?",
      suggestions: [
        "Freelance payment contract",
        "Rental agreement",
        "Subscription service",
        "Service agreement"
      ]
    }
  ])

  const handleAddBlock = (blockType) => {
    const newBlock = {
      id: `block-${Date.now()}`,
      type: blockType,
      position: { x: Math.random() * 400 + 200, y: Math.random() * 300 + 100 },
      data: { label: blockType, content: '' }
    }
    setBlocks([...blocks, newBlock])
  }

  const handleBlocksChange = (updatedBlocks) => {
    setBlocks(updatedBlocks)
  }

  const handleDeleteBlock = (blockId) => {
    // Remove the block
    const updatedBlocks = blocks.filter((block) => block.id !== blockId)
    setBlocks(updatedBlocks)
    
    // Remove all edges connected to this block
    const updatedEdges = edges.filter(
      (edge) => edge.from !== blockId && edge.to !== blockId
    )
    setEdges(updatedEdges)
  }

  const handleNodeUpdate = (nodeId, updatedNode) => {
    const updatedBlocks = blocks.map((block) =>
      block.id === nodeId ? updatedNode : block
    )
    setBlocks(updatedBlocks)
  }

  const handleChatMessage = (message) => {
    setChatMessages([...chatMessages, message])
  }

  const handleGenerate = () => {
    console.log('Generating smart contract with blocks:', blocks)
    console.log('Edges:', edges)
    // This will be connected to backend later
  }

  return (
    <div className="app">
      <div className="app-content">
        {/* Left Sidebar - Block Palette */}
        <motion.div 
          className="sidebar-left"
          initial={{ x: -300 }}
          animate={{ x: 0 }}
          transition={{ type: 'spring', stiffness: 100 }}
        >
          <BlockPalette onAddBlock={handleAddBlock} />
        </motion.div>

        {/* Center - Canvas */}
        <div className="canvas-container">
          <div className="canvas-area">
            <Canvas 
              blocks={blocks} 
              onBlocksChange={handleBlocksChange}
              onNodeSelect={setSelectedNodeId}
              selectedNodeId={selectedNodeId}
              edges={edges}
              onEdgesChange={setEdges}
              onDeleteBlock={handleDeleteBlock}
            />
          </div>
          {/* Generate Button - Separate from canvas, underneath */}
          <div className="generate-button-container-wrapper">
            <GenerateButton 
              onClick={handleGenerate}
              disabled={blocks.length === 0}
            />
          </div>
        </div>

        {/* Node Editor (slides in when node is selected) */}
        {selectedNodeId && (
          <NodeEditor
            node={blocks.find((b) => b.id === selectedNodeId)}
            onUpdate={handleNodeUpdate}
            onClose={() => setSelectedNodeId(null)}
          />
        )}

        {/* Right Sidebar - Chatbot */}
        <motion.div 
          className="sidebar-right"
          initial={{ x: 300 }}
          animate={{ x: 0 }}
          transition={{ type: 'spring', stiffness: 100 }}
        >
          <Chatbot 
            messages={chatMessages}
            onMessage={handleChatMessage}
          />
        </motion.div>
      </div>
    </div>
  )
}

export default App

