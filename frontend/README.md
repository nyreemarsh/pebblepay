# PebblePay Frontend

Modern dark mode, neon aesthetic frontend for smart contract generation.

## Features

- 🎨 Neon aesthetic with dark mode
- 💬 Interactive chatbot (Pibble) for contract guidance
- 🎯 Drag-and-drop canvas for visual contract building
- 📦 Block library with custom contract components
- ⚡ Smooth animations and micro-interactions
- 🎭 Helvetica font family

## Getting Started

### Install Dependencies

```bash
npm install
```

### Development

```bash
npm run dev
```

The app will open at `http://localhost:3000`

### Build

```bash
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── BlockPalette.jsx    # Left sidebar - block library
│   │   ├── Canvas.jsx          # Center - interactive canvas
│   │   ├── Chatbot.jsx         # Right sidebar - Pibble chatbot
│   │   └── GenerateButton.jsx  # Bottom - generate button
│   ├── App.jsx                 # Main app component
│   ├── main.jsx                # Entry point
│   └── index.css               # Global styles
├── assets/
│   ├── fonts/                  # Custom fonts
│   └── images/                 # Images, logos, icons
└── package.json
```

## Color Scheme

- **Neon Cyan**: `#00AEE1`
- **Neon Orange**: `#FA4530`
- **Neon Pink**: `#EA91E3`
- **Neon Purple**: `#9C2780`
- **Dark Background**: `#0a0a0f`
- **Secondary Background**: `#121218`

## Technologies

- React 18
- React Flow (canvas)
- Framer Motion (animations)
- Vite (build tool)
- Lucide React (icons)

