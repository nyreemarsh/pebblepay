import React from 'react'
import { motion } from 'framer-motion'
import { Loader2 } from 'lucide-react'
import './GenerateButton.css'

function GenerateButton({ onClick, disabled, isLoading }) {
  return (
    <motion.div
      className="generate-button-container"
      initial={{ y: 100 }}
      animate={{ y: 0 }}
      transition={{ type: 'spring', stiffness: 100 }}
    >
      <motion.button
        className={`generate-button ${disabled ? 'disabled' : ''} ${isLoading ? 'loading' : ''}`}
        onClick={onClick}
        disabled={disabled || isLoading}
        whileHover={!disabled && !isLoading ? { scale: 1.05 } : {}}
        whileTap={!disabled && !isLoading ? { scale: 0.95 } : {}}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        {isLoading ? (
          <>
            <Loader2 className="spinner" size={20} />
            <span>Generating...</span>
          </>
        ) : (
          <span>Generate Smart Contract</span>
        )}
      </motion.button>
    </motion.div>
  )
}

export default GenerateButton

