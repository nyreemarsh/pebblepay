import React, { useState, useEffect, useRef, useCallback } from 'react'
import { motion } from 'framer-motion'
import ContractHistorySidebar from './components/ContractHistorySidebar'
import CompactBlockPalette from './components/CompactBlockPalette'
import Canvas from './components/Canvas'
import Chatbot from './components/Chatbot'
import GenerateButton from './components/GenerateButton'
import SolidityModal from './components/SolidityModal'
import './App.css'

import NodeEditor from './components/NodeEditor'
import { contractSpecToBlocks, getChangedBlockIds } from './utils/contractSpecToBlocks'

// API base URL - adjust if your backend runs on a different port
const API_BASE_URL = 'http://localhost:8000'

function App() {
  const [blocks, setBlocks] = useState([])
  const [edges, setEdges] = useState([])
  const [selectedNodeId, setSelectedNodeId] = useState(null)
  const [chatMessages, setChatMessages] = useState([])
  const [sessionId, setSessionId] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [contractData, setContractData] = useState(null)
  
  // Contract progress and generation state
  const [completeness, setCompleteness] = useState(0)
  const [changedBlocks, setChangedBlocks] = useState([])
  const prevBlocksRef = useRef([])
  const [solidityData, setSolidityData] = useState(null)
  const [showSolidityModal, setShowSolidityModal] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)

  // Resizable panel width for right sidebar
  const [rightWidth, setRightWidth] = useState(350)
  const [isResizingRight, setIsResizingRight] = useState(false)
  const resizeRightRef = useRef(null)


// Initialize with empty placeholder blocks
useEffect(() => {
// ... rest of the file

// Contract progress
const [completeness, setCompleteness] = useState(0)
const [changedBlocks, setChangedBlocks] = useState([])
const prevBlocksRef = useRef([])

// Initialize with empty placeholder blocks
useEffect(() => {
  const { blocks: initialBlocks, edges: initialEdges, completeness: initialCompleteness } =
    contractSpecToBlocks(null)
  setBlocks(initialBlocks)
  setEdges(initialEdges)
  setCompleteness(initialCompleteness)
  prevBlocksRef.current = initialBlocks
}, [])

  // Fetch opening message on mount
  useEffect(() => {
    const fetchOpeningMessage = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/opening-message`)
        const data = await response.json()
        
        setChatMessages([
          {
            id: Date.now(),
            type: 'suggestion',
            text: data.message,
            suggestions: [
              "I'm designing a logo for a client",
              "I'm doing freelance writing work",
              "I'm providing consulting services",
              "I'm building a website"
            ]
          }
        ])
      } catch (error) {
        console.error('Error fetching opening message:', error)
        // Fallback message
        setChatMessages([
          {
            id: Date.now(),
            type: 'suggestion',
            text: "Hi there! 👋 I'm Pibble, your friendly contract assistant.\n\nHere's how I work: I'll ask you a few simple questions about your project, and then I'll create a comprehensive contract that protects both you and your client. I'll cover everything from payment terms to what happens if things don't go as planned.\n\nLet's get started! Tell me a bit about what you're working on - who's your client and what will you be delivering?",            suggestions: [
              "I'm designing a logo for a client",
              "I'm doing freelance writing work",
              "I'm providing consulting services",
              "I'm building a website"
            ]
          }
        ])
      }
    }
    
    fetchOpeningMessage()
  }, [])

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

  const handleChatMessage = async (message) => {
    // Add user message to chat immediately
    const userMessage = {
      ...message,
      type: 'user',
    }
    setChatMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Call the backend API - backend maintains chat history in database
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message.text,
          session_id: sessionId,
        }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()

      // Store session ID if this is a new session
      if (!sessionId && data.session_id) {
        setSessionId(data.session_id)
      }

      // Store contract data if available
      if (data.contract_spec || data.contract_text) {
        setContractData({
          spec: data.contract_spec,
          text: data.contract_text,
          summary: data.summary,
        })
        
        // Update blocks from contract_spec
        if (data.contract_spec) {
          const { blocks: newBlocks, edges: newEdges, completeness: newCompleteness } = contractSpecToBlocks(data.contract_spec)
          
          // Find which blocks changed for animation
          const changed = getChangedBlockIds(prevBlocksRef.current, newBlocks)
          setChangedBlocks(changed)
          
          // Mark changed blocks as "new" for animation
          const blocksWithAnimation = newBlocks.map(block => ({
            ...block,
            data: {
              ...block.data,
              isNew: changed.includes(block.id),
              type: block.type,
              title: block.title,
              subtitle: block.subtitle,
              filled: block.filled,
            }
          }))
          
          setBlocks(blocksWithAnimation)
          setEdges(newEdges) // Update edges automatically
          setCompleteness(newCompleteness)
          prevBlocksRef.current = newBlocks
          
          // Clear animation flags after a delay
          setTimeout(() => {
            setChangedBlocks([])
          }, 600)
        }
      }

      // Add assistant response to chat
      const assistantMessage = {
        id: Date.now(),
        type: 'suggestion',
        text: data.response,
        suggestions: data.suggestions || undefined,
        contractReady: data.contract_ready || false,
      }
      setChatMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      // Show error message to user
      const errorMessage = {
        id: Date.now(),
        type: 'suggestion',
        text: "Sorry, I encountered an error. Please try again or check if the backend server is running.",
      }
      setChatMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleGenerate = async () => {
    console.log('Generating smart contract with blocks:', blocks)
    console.log('Edges:', edges)
    
    setIsGenerating(true)
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/generate-solidity`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          blocks: blocks,
          edges: edges,
          contract_spec: contractData?.spec || null,
        }),
      })
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }
      
      const data = await response.json()
      
      setSolidityData(data)
      setShowSolidityModal(true)
      
    } catch (error) {
      console.error('Error generating Solidity:', error)
      // Show error in chat
      setChatMessages((prev) => [...prev, {
        id: Date.now(),
        type: 'suggestion',
        text: `Sorry, I couldn't generate the Solidity contract. Error: ${error.message}`,
      }])
    } finally {
      setIsGenerating(false)
    }
  }

  // Resize handlers for right sidebar
  const handleMouseDownRight = useCallback((e) => {
    e.preventDefault()
    setIsResizingRight(true)
  }, [])

  const handleMouseMove = useCallback((e) => {
    if (!isResizingRight) return

    const containerWidth = window.innerWidth - 32 // Account for padding
    const minWidth = 250
    const maxRightWidth = containerWidth * 0.5

    if (isResizingRight) {
      const newWidth = containerWidth - e.clientX - 16 // Account for padding
      if (newWidth >= minWidth && newWidth <= maxRightWidth) {
        setRightWidth(newWidth)
      }
    }
  }, [isResizingRight])

  const handleMouseUp = useCallback(() => {
    setIsResizingRight(false)
  }, [])

  useEffect(() => {
    if (isResizingRight) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      return () => {
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isResizingRight, handleMouseMove, handleMouseUp])

  // Handler to add messages directly (for explain contract)
  const handleAddMessage = (message) => {
    setChatMessages((prev) => [...prev, message])
  }

  // Load a saved contract
  const handleLoadContract = async (loadSessionId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/contracts/${loadSessionId}`)
      if (!response.ok) throw new Error('Failed to load contract')
      
      const data = await response.json()
      
      // Set session ID
      setSessionId(loadSessionId)
      
      // Load contract data
      if (data.contract_spec) {
        setContractData({
          spec: data.contract_spec,
          text: data.contract_text,
        })
        
        // Update blocks
        const { blocks: newBlocks, edges: newEdges, completeness: newCompleteness } = contractSpecToBlocks(data.contract_spec)
        setBlocks(newBlocks)
        setEdges(newEdges)
        setCompleteness(newCompleteness)
        prevBlocksRef.current = newBlocks
      }
      
      // Load chat history if available, otherwise show a welcome back message
      if (data.chat_history && data.chat_history.length > 0) {
        // Restore the full chat history
        setChatMessages(data.chat_history)
      } else {
        // Fallback message if no history
        setChatMessages([{
          id: Date.now(),
          type: 'suggestion',
          text: `Welcome back! I've loaded your contract "${data.contract_spec?.title || 'Untitled'}". ${data.contract_text ? 'The contract is complete - you can download it anytime.' : 'Let\'s continue where we left off!'}`,
          suggestions: data.contract_text ? undefined : ['Continue from here'],
          contractReady: !!data.contract_text
        }])
      }
      
    } catch (error) {
      console.error('Error loading contract:', error)
    }
  }

  // Start a new contract
  const handleNewContract = () => {
    setSessionId(null)
    setContractData(null)
    const { blocks: initialBlocks, edges: initialEdges, completeness: initialCompleteness } = contractSpecToBlocks(null)
    setBlocks(initialBlocks)
    setEdges(initialEdges)
    setCompleteness(initialCompleteness)
    prevBlocksRef.current = initialBlocks
    
    // Fetch fresh opening message
    fetch(`${API_BASE_URL}/api/opening-message`)
      .then(res => res.json())
      .then(data => {
        setChatMessages([{
          id: Date.now(),
          type: 'suggestion',
          text: data.message,
          suggestions: [
            "I'm designing a logo for a client",
            "I'm doing freelance writing work",
            "I'm providing consulting services",
            "I'm building a website"
          ]
        }])
      })
  }

  return (
    <div className="app">
      <div className="app-content">
        {/* Left Sidebar - Contract History */}
        <motion.div 
          className="sidebar-left"
          initial={{ x: -300 }}
          animate={{ x: 0 }}
          transition={{ type: 'spring', stiffness: 100 }}
        >
          <ContractHistorySidebar 
            onLoadContract={handleLoadContract}
            onNewContract={handleNewContract}
            currentSessionId={sessionId}
          />
        </motion.div>

        {/* Center - Canvas */}
        <div className="canvas-container">
          {/* Progress Bar */}
          <div className="progress-container">
            <div className="progress-label">
              <span>Contract Progress</span>
              <span className="progress-percent">{completeness}%</span>
            </div>
            <div className="progress-bar">
              <motion.div 
                className="progress-fill"
                initial={{ width: 0 }}
                animate={{ width: `${completeness}%` }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
              />
            </div>
            {completeness === 100 && (
              <motion.div 
                className="progress-complete"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
              >
                🎉 Ready to generate!
              </motion.div>
            )}
          </div>
          
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
          {/* Compact Block Palette - At bottom of canvas */}
          <CompactBlockPalette onAddBlock={handleAddBlock} />
          {/* Generate Button - Separate from canvas, underneath */}
          <div className="generate-button-container-wrapper">
            <GenerateButton 
              onClick={handleGenerate}
              disabled={completeness < 50 || isGenerating}
              isLoading={isGenerating}
            />
          </div>
        </div>

        {/* Solidity Modal */}
        {showSolidityModal && solidityData && (
          <SolidityModal
            data={solidityData}
            onClose={() => setShowSolidityModal(false)}
          />
        )}

        {/* Node Editor (slides in when node is selected) */}
        {selectedNodeId && (
          <NodeEditor
            node={blocks.find((b) => b.id === selectedNodeId)}
            onUpdate={handleNodeUpdate}
            onClose={() => setSelectedNodeId(null)}
          />
        )}

        {/* Right Resize Handle */}
        <div
          className="resize-handle resize-handle-right"
          onMouseDown={handleMouseDownRight}
          ref={resizeRightRef}
        />

        {/* Right Sidebar - Chatbot */}
        <motion.div 
          className="sidebar-right"
          style={{ width: `${rightWidth}px` }}
          initial={{ x: 300 }}
          animate={{ x: 0 }}
          transition={{ type: 'spring', stiffness: 100 }}
        >
          <Chatbot 
            messages={chatMessages}
            onMessage={handleChatMessage}
            sessionId={sessionId}
            onAddMessage={handleAddMessage}
            isLoading={isLoading}
          />
        </motion.div>
      </div>
    </div>
  )
}

export default App

