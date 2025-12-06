import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X } from 'lucide-react'
import './NodeEditor.css'

function NodeEditor({ node, onUpdate, onClose }) {
  const [label, setLabel] = useState(node?.data?.label || '')
  const [content, setContent] = useState(node?.data?.content || '')

  useEffect(() => {
    if (node) {
      setLabel(node.data?.label || '')
      setContent(node.data?.content || '')
    }
  }, [node])

  const handleSave = () => {
    if (node) {
      onUpdate(node.id, {
        ...node,
        data: {
          ...node.data,
          label,
          content,
        },
      })
    }
  }

  if (!node) return null

  return (
    <AnimatePresence>
      <motion.div
        className="node-editor-backdrop"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.2 }}
        onClick={onClose}
      >
        <motion.div
          className="node-editor"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          transition={{ duration: 0.2 }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="editor-header">
            <h3>Edit Block</h3>
            <button className="close-button" onClick={onClose}>
              <X size={20} />
            </button>
          </div>

          <div className="editor-content">
            <div className="editor-field">
              <label>Block Type</label>
              <input
                type="text"
                value={node.type}
                disabled
                className="disabled-input"
              />
            </div>

            <div className="editor-field">
              <label>Label</label>
              <input
                type="text"
                value={label}
                onChange={(e) => setLabel(e.target.value)}
                placeholder="Enter block label"
                onBlur={handleSave}
              />
            </div>

            <div className="editor-field">
              <label>Content</label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Enter block content"
                rows={4}
                onBlur={handleSave}
              />
            </div>

            <div className="editor-actions">
              <button className="save-button" onClick={handleSave}>
                Save Changes
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

export default NodeEditor

