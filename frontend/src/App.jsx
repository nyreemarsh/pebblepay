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
<<<<<<< Updated upstream
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
=======
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
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
    // This will be connected to backend later
=======
    
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
      
      console.log('[Frontend] Received contract data:', {
        hasSolidity: !!data.solidity,
        hasAbi: !!data.abi,
        hasNeoPython: !!data.neo_python,
        neoPythonLength: data.neo_python?.length || 0,
        neoPythonPreview: data.neo_python?.substring(0, 100) || 'N/A'
      })
      
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
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
=======
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
                <span style={{ fontFamily: "'shantell-sans-bouncy', 'Nunito', sans-serif" }}>(˶˃⤙˂˶) Ready to generate!</span>
              </motion.div>
            )}
          </div>
          
>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
<<<<<<< Updated upstream
        {/* Node Editor (slides in when node is selected) */}
        {selectedNodeId && (
          <NodeEditor
            node={blocks.find((b) => b.id === selectedNodeId)}
            onUpdate={handleNodeUpdate}
            onClose={() => setSelectedNodeId(null)}
          />
        )}
=======
=======
>>>>>>> Stashed changes
        {/* Right Resize Handle */}
        <div
          className="resize-handle resize-handle-right"
          onMouseDown={handleMouseDownRight}
          ref={resizeRightRef}
        />
>>>>>>> Stashed changes

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
    </div>
  )
}

export default App

