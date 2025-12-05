import React from 'react'
import { motion } from 'framer-motion'
import { Sparkles } from 'lucide-react'
import './GenerateButton.css'

function GenerateButton({ onClick, disabled }) {
  return (
    <motion.div
      className="generate-button-container"
      initial={{ y: 100 }}
      animate={{ y: 0 }}
      transition={{ type: 'spring', stiffness: 100 }}
    >
      <motion.button
        className={`generate-button ${disabled ? 'disabled' : ''}`}
        onClick={onClick}
        disabled={disabled}
        whileHover={!disabled ? { scale: 1.05 } : {}}
        whileTap={!disabled ? { scale: 0.95 } : {}}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <Sparkles size={20} />
        <span>Generate Smart Contract</span>
        {!disabled && (
          <motion.div
            className="button-glow"
            animate={{
              boxShadow: [
                '0 0 20px rgba(0, 174, 225, 0.5)',
                '0 0 40px rgba(0, 174, 225, 0.8)',
                '0 0 20px rgba(0, 174, 225, 0.5)',
              ],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
        )}
      </motion.button>
    </motion.div>
  )
}

export default GenerateButton

