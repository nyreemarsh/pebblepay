/**
 * Contract Spec to Blocks Converter
 * Transforms the backend contract_spec into visual blocks for the canvas.
 */

/**
 * @typedef {'party' | 'deliverable' | 'payment' | 'timeline' | 'special_term' | 'meta' | 'quality' | 'protection'} BlockType
 * 
 * @typedef {Object} Block
 * @property {string} id - Unique block identifier
 * @property {BlockType} type - Type of block
 * @property {string} title - Main title of the block
 * @property {string} [subtitle] - Secondary text
 * @property {boolean} filled - Whether this block has data
 * @property {Object} position - {x, y} position on canvas
 * @property {Object} data - Block-specific data
 */

/**
 * @typedef {Object} Edge
 * @property {string} id - Unique edge identifier
 * @property {string} from - Source block ID
 * @property {string} to - Target block ID
 * @property {string} [fromSide] - Source handle side (default: 'right')
 * @property {string} [toSide] - Target handle side (default: 'left')
 */

/**
 * @typedef {Object} BlockViewModel
 * @property {Block[]} blocks - Array of blocks to render
 * @property {Edge[]} edges - Array of edges connecting blocks
 * @property {number} completeness - 0-100 completeness score
 */

// Block layout configuration - arranged in a nice visual pattern
const BLOCK_POSITIONS = {
  meta: { x: 400, y: 50 },
  freelancer: { x: 150, y: 180 },
  client: { x: 650, y: 180 },
  deliverables: { x: 400, y: 310 },
  payment: { x: 150, y: 440 },
  timeline: { x: 650, y: 440 },
  quality: { x: 400, y: 570 },
  protection: { x: 400, y: 700 },
}

// Colors for different block types
export const BLOCK_COLORS = {
  meta: { filled: '#1D838D', ghost: 'rgba(29, 131, 141, 0.3)' },
  party: { filled: '#4CAF50', ghost: 'rgba(76, 175, 80, 0.3)' },
  deliverable: { filled: '#FF9800', ghost: 'rgba(255, 152, 0, 0.3)' },
  payment: { filled: '#9C27B0', ghost: 'rgba(156, 39, 176, 0.3)' },
  timeline: { filled: '#2196F3', ghost: 'rgba(33, 150, 243, 0.3)' },
  quality: { filled: '#00BCD4', ghost: 'rgba(0, 188, 212, 0.3)' },
  protection: { filled: '#F44336', ghost: 'rgba(244, 67, 54, 0.3)' },
  special_term: { filled: '#607D8B', ghost: 'rgba(96, 125, 139, 0.3)' },
}

/**
 * Convert contract_spec to visual blocks
 * @param {Object} spec - The contract specification from backend
 * @returns {BlockViewModel}
 */
/**
 * Generate automatic edges connecting filled blocks in logical sequence
 * Each filled block connects to the most recent filled block before it in the flow order
 * @param {Block[]} blocks - Array of blocks
 * @returns {Edge[]} Array of edges
 */
function generateAutomaticEdges(blocks) {
  const edges = []
  
  // Define the logical flow order
  const flowOrder = [
    'block-meta',
    'block-freelancer',
    'block-client',
    'block-deliverables',
    'block-payment',
    'block-timeline',
    'block-quality',
    'block-protection',
  ]
  
  // Create a map of block IDs to their index in flow order for quick lookup
  const blockOrderMap = new Map()
  flowOrder.forEach((id, index) => {
    blockOrderMap.set(id, index)
  })
  
  // Get all filled blocks sorted by their flow order
  const filledBlocks = blocks
    .filter(block => block.filled)
    .sort((a, b) => {
      const orderA = blockOrderMap.get(a.id) ?? 999
      const orderB = blockOrderMap.get(b.id) ?? 999
      return orderA - orderB
    })
  
  // Connect each filled block to the previous filled block
  for (let i = 1; i < filledBlocks.length; i++) {
    const fromBlock = filledBlocks[i - 1]
    const toBlock = filledBlocks[i]
    
    edges.push({
      id: `edge-${fromBlock.id}-${toBlock.id}`,
      from: fromBlock.id,
      to: toBlock.id,
      fromSide: 'right',
      toSide: 'left',
    })
  }
  
  return edges
}

export function contractSpecToBlocks(spec) {
  if (!spec) {
    return { blocks: getEmptyBlocks(), edges: [], completeness: 0 }
  }

  const blocks = []
  let completenessScore = 0

  // 1. Meta block (Contract Title)
  const title = spec.title || ''
  blocks.push({
    id: 'block-meta',
    type: 'meta',
    title: title || 'Contract Title',
    subtitle: title ? '✓ Named' : 'Waiting for details...',
    filled: !!title,
    position: BLOCK_POSITIONS.meta,
    data: { label: 'Contract', content: title },
  })

  // 2. Party blocks - Freelancer
  const freelancer = spec.freelancer || {}
  const freelancerFilled = !!(freelancer.name || freelancer.email)
  blocks.push({
    id: 'block-freelancer',
    type: 'party',
    title: 'Freelancer',
    subtitle: freelancer.name || 'Who are you?',
    filled: freelancerFilled,
    position: BLOCK_POSITIONS.freelancer,
    data: { 
      label: 'Freelancer', 
      content: freelancer.name || '',
      role: 'freelancer',
      email: freelancer.email,
    },
  })

  // 3. Party blocks - Client
  const client = spec.client || {}
  const clientFilled = !!(client.name || client.email)
  blocks.push({
    id: 'block-client',
    type: 'party',
    title: 'Client',
    subtitle: client.name || 'Who is your client?',
    filled: clientFilled,
    position: BLOCK_POSITIONS.client,
    data: { 
      label: 'Client', 
      content: client.name || '',
      role: 'client',
      email: client.email,
    },
  })

  // 4. Deliverables block
  const deliverables = spec.deliverables || []
  const hasDeliverables = deliverables.length > 0
  const deliverableText = hasDeliverables 
    ? deliverables.map(d => typeof d === 'string' ? d : d.item).filter(Boolean).join(', ')
    : ''
  blocks.push({
    id: 'block-deliverables',
    type: 'deliverable',
    title: 'Deliverables',
    subtitle: hasDeliverables 
      ? `${deliverables.length} item${deliverables.length > 1 ? 's' : ''}` 
      : 'What will you deliver?',
    filled: hasDeliverables,
    position: BLOCK_POSITIONS.deliverables,
    data: { 
      label: 'Deliverables', 
      content: deliverableText,
      items: deliverables,
    },
  })

  // 5. Payment block
  const payment = spec.payment || {}
  const paymentFilled = !!(payment.amount && payment.currency)
  const paymentSubtitle = paymentFilled
    ? `${payment.currency === 'GBP' ? '£' : payment.currency === 'USD' ? '$' : ''}${payment.amount} ${payment.schedule || ''}`
    : 'How much & when?'
  blocks.push({
    id: 'block-payment',
    type: 'payment',
    title: 'Payment',
    subtitle: paymentSubtitle.trim(),
    filled: paymentFilled,
    position: BLOCK_POSITIONS.payment,
    data: { 
      label: 'Payment', 
      content: paymentSubtitle,
      amount: payment.amount,
      currency: payment.currency,
      schedule: payment.schedule,
    },
  })

  // 6. Timeline block
  const timeline = spec.timeline || {}
  const timelineFilled = !!(timeline.deadline)
  blocks.push({
    id: 'block-timeline',
    type: 'timeline',
    title: 'Timeline',
    subtitle: timeline.deadline || 'When is it due?',
    filled: timelineFilled,
    position: BLOCK_POSITIONS.timeline,
    data: { 
      label: 'Timeline', 
      content: timeline.deadline || '',
      deadline: timeline.deadline,
      start_date: timeline.start_date,
    },
  })

  // 7. Quality block (revisions, acceptance criteria)
  const quality = spec.quality_standards || {}
  const qualityFilled = quality.max_revisions !== null && quality.max_revisions !== undefined
  blocks.push({
    id: 'block-quality',
    type: 'quality',
    title: 'Quality',
    subtitle: qualityFilled 
      ? `${quality.max_revisions} revisions` 
      : 'Revisions & standards',
    filled: qualityFilled,
    position: BLOCK_POSITIONS.quality,
    data: { 
      label: 'Quality', 
      content: qualityFilled ? `${quality.max_revisions} revisions included` : '',
      max_revisions: quality.max_revisions,
      acceptance_criteria: quality.acceptance_criteria,
    },
  })

  // 8. Protection block (failure scenarios, disputes)
  const failure = spec.failure_scenarios || {}
  const dispute = spec.dispute_resolution || {}
  const protectionFilled = !!(failure.late_delivery?.penalty_type || dispute.method)
  blocks.push({
    id: 'block-protection',
    type: 'protection',
    title: 'Protections',
    subtitle: protectionFilled 
      ? 'Terms defined' 
      : 'What if things go wrong?',
    filled: protectionFilled,
    position: BLOCK_POSITIONS.protection,
    data: { 
      label: 'Protections', 
      content: protectionFilled ? 'Failure scenarios & disputes' : '',
      failure_scenarios: failure,
      dispute_resolution: dispute,
    },
  })

  // Calculate completeness score
  // +15 for each major section filled
  if (title) completenessScore += 10
  if (freelancerFilled) completenessScore += 15
  if (clientFilled) completenessScore += 15
  if (hasDeliverables) completenessScore += 15
  if (paymentFilled) completenessScore += 15
  if (timelineFilled) completenessScore += 15
  if (qualityFilled) completenessScore += 10
  if (protectionFilled) completenessScore += 5

  // Generate automatic edges connecting filled blocks in sequence
  const edges = generateAutomaticEdges(blocks)

  return {
    blocks,
    edges,
    completeness: Math.min(100, completenessScore),
  }
}

/**
 * Get empty placeholder blocks for initial state
 */
function getEmptyBlocks() {
  return [
    {
      id: 'block-meta',
      type: 'meta',
      title: 'Contract Title',
      subtitle: 'Start chatting to build...',
      filled: false,
      position: BLOCK_POSITIONS.meta,
      data: { label: 'Contract', content: '' },
    },
    {
      id: 'block-freelancer',
      type: 'party',
      title: 'Freelancer',
      subtitle: 'You',
      filled: false,
      position: BLOCK_POSITIONS.freelancer,
      data: { label: 'Freelancer', content: '', role: 'freelancer' },
    },
    {
      id: 'block-client',
      type: 'party',
      title: 'Client',
      subtitle: 'Your client',
      filled: false,
      position: BLOCK_POSITIONS.client,
      data: { label: 'Client', content: '', role: 'client' },
    },
    {
      id: 'block-deliverables',
      type: 'deliverable',
      title: 'Deliverables',
      subtitle: 'What you\'ll deliver',
      filled: false,
      position: BLOCK_POSITIONS.deliverables,
      data: { label: 'Deliverables', content: '' },
    },
    {
      id: 'block-payment',
      type: 'payment',
      title: 'Payment',
      subtitle: 'How much & when',
      filled: false,
      position: BLOCK_POSITIONS.payment,
      data: { label: 'Payment', content: '' },
    },
    {
      id: 'block-timeline',
      type: 'timeline',
      title: 'Timeline',
      subtitle: 'Deadline',
      filled: false,
      position: BLOCK_POSITIONS.timeline,
      data: { label: 'Timeline', content: '' },
    },
    {
      id: 'block-quality',
      type: 'quality',
      title: 'Quality',
      subtitle: 'Standards',
      filled: false,
      position: BLOCK_POSITIONS.quality,
      data: { label: 'Quality', content: '' },
    },
    {
      id: 'block-protection',
      type: 'protection',
      title: 'Protections',
      subtitle: 'Safety terms',
      filled: false,
      position: BLOCK_POSITIONS.protection,
      data: { label: 'Protections', content: '' },
    },
  ]
}

/**
 * Check which blocks changed between old and new specs
 * @param {Block[]} oldBlocks 
 * @param {Block[]} newBlocks 
 * @returns {string[]} IDs of blocks that changed
 */
export function getChangedBlockIds(oldBlocks, newBlocks) {
  const changedIds = []
  
  for (const newBlock of newBlocks) {
    const oldBlock = oldBlocks.find(b => b.id === newBlock.id)
    if (!oldBlock) {
      changedIds.push(newBlock.id)
    } else if (oldBlock.filled !== newBlock.filled || oldBlock.subtitle !== newBlock.subtitle) {
      changedIds.push(newBlock.id)
    }
  }
  
  return changedIds
}

export default contractSpecToBlocks

