# 🐾 PibblePay

*A playful smart-contract playground powered by SpoonOS + Neo.*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-Apache--2.0-green.svg)](LICENSE)

---

## 📖 About

PibblePay is an experimental **visual and natural-language smart contract builder** designed for beginners, creators, freelancers, and small businesses who want to use Web3 without touching complex code.

Users describe what they want in **plain English**, and PibblePay converts it into:
- A **structured smart-contract visualisation** using an intuitive drag-and-drop interface
- Clean **smart-contract logic** generated automatically
- Optional **on-chain deployment** to the Neo testnet

PibblePay aims to make Web3 feel like a **creative playground**, not a command line.

---

## ✨ Features

### 🎯 Natural-Language → Smart Contract Agent
- Type a simple prompt (e.g., *"Hold £50 until work is approved"*)
- The agent identifies roles, conditions, actions, and outputs a contract structure
- Powered by [SpoonOS](https://github.com/XSpoonAi/spoon-core)

### 🎨 Visual Smart-Contract Builder
- Drag-and-drop interface using React Flow
- Build contracts by stacking visual "pebbles" (blocks)
- Real-time visualisation of parties, conditions, triggers, and flows
- Great for beginners and non-technical users

### 🔊 Voice Interface
- Text-to-speech powered by ElevenLabs
- Pibble (the AI assistant) speaks responses automatically
- Click-to-replay audio for all messages

### 🔗 Neo Blockchain Integration (Optional)
- Convert generated logic into Neo-compatible smart contract code
- Deploy or test on Neo testnet

### 🧩 Modular Architecture
- NLP agent for natural language processing
- Contract-logic generator
- Visualisation builder
- Optional on-chain deployment agent

---

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** and **npm** - [Download Node.js](https://nodejs.org/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **ElevenLabs API account** (for TTS functionality) - [Sign up here](https://elevenlabs.io/)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/pebblepay.git
   cd pebblepay
   ```

2. **Set up the backend:**
   ```bash
   # Install Python dependencies (includes SpoonOS from GitHub)
   pip install -r requirements.txt
   
   # Create a .env file in the root directory
   cp .env.example .env  # If you have an example file
   # Or create .env manually with:
   ```
   
   Add the following to your `.env` file:
   ```env
   # ElevenLabs API Configuration
   ELEVENLABS_API_KEY=your_api_key_here
   ELEVENLABS_VOICE_ID=your_voice_id_here
   ```
   
   Get your credentials from:
   - **API Key**: [ElevenLabs Dashboard](https://elevenlabs.io/) → Profile → API Key
   - **Voice ID**: [ElevenLabs Voices](https://elevenlabs.io/app/voices) → Select a voice → Copy the Voice ID

3. **Set up the frontend:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

---

## 🎮 Usage

### Running the Application

You'll need **two terminal windows** running simultaneously:

#### Terminal 1 - Backend Server

```bash
cd backend
python main.py
```

The backend API will start at `http://localhost:8000`

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### Terminal 2 - Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will start at `http://localhost:3000` (or another port if 3000 is busy)

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

### Using the Application

1. **Open your browser** and navigate to `http://localhost:3000`

2. **Chat with Pibble:**
   - Pibble will greet you with an initial message
   - Type your smart contract idea in plain English
   - Pibble will respond and suggest actions

3. **Build your contract visually:**
   - Drag blocks from the left sidebar ("Pibble's Block Garden") onto the canvas
   - Available block types: `party`, `asset`, `amount`, `condition`, `trigger`, `timeout`, `module`
   - Connect blocks by dragging from connection points (left/right handles)
   - Click on blocks to edit their properties in the side panel

4. **Generate your smart contract:**
   - Once you've added blocks to the canvas, the "Generate Smart Contract" button will become active
   - Click it to generate the contract code

5. **Listen to Pibble:**
   - Pibble's messages are automatically spoken using ElevenLabs TTS
   - Click the 🔊 audio button next to any message to replay it

---

## 📁 Project Structure

```
pebblepay/
├── backend/                 # FastAPI backend server
│   ├── main.py             # Main application entry point & CORS setup
│   └── tts.py              # Text-to-speech API endpoint (ElevenLabs)
│
├── frontend/                # React frontend application
│   ├── src/
│   │   ├── App.jsx         # Main app component
│   │   ├── components/     # React components
│   │   │   ├── BlockPalette.jsx    # Left sidebar - block selection
│   │   │   ├── Canvas.jsx         # Center - React Flow canvas
│   │   │   ├── Chatbot.jsx         # Right sidebar - chat interface
│   │   │   ├── GenerateButton.jsx # Generate contract button
│   │   │   ├── NodeEditor.jsx     # Node property editor
│   │   │   └── nodes/
│   │   │       └── CustomNode.jsx # Custom React Flow node component
│   │   └── main.jsx        # React entry point
│   ├── package.json        # Node.js dependencies
│   └── vite.config.js      # Vite configuration
│
├── agents/                  # Agent modules (SpoonOS integration)
│   └── __init__.py
│
├── .env                     # Environment variables (create this)
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# ElevenLabs API Configuration (Required for TTS)
ELEVENLABS_API_KEY=your_api_key_here
ELEVENLABS_VOICE_ID=your_voice_id_here
```

### Backend Configuration

The backend server runs on port `8000` by default. To change this, edit `backend/main.py`:

```python
uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

### Frontend Configuration

The frontend runs on port `3000` by default (configured in `frontend/vite.config.js`). To change this:

```javascript
export default defineConfig({
  server: {
    port: 3000,  // Change this
    open: true
  }
})
```

---

## 🛠️ Development

### Running in Development Mode

Both servers support hot-reload:
- **Backend**: Automatically reloads when Python files change (via `uvicorn --reload`)
- **Frontend**: Automatically reloads when React files change (via Vite HMR)

### Building for Production

**Frontend:**
```bash
cd frontend
npm run build
```

The production build will be in `frontend/dist/`

**Backend:**
The backend is ready for production. You can use:
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

Or deploy using a production ASGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Dependencies

**Python Dependencies** (`requirements.txt`):
- `fastapi` - Modern web framework
- `uvicorn` - ASGI server
- `python-dotenv` - Environment variable management
- `requests` - HTTP library
- `pydantic` - Data validation
- `spoon-core` - Installed from [XSpoonAi/spoon-core](https://github.com/XSpoonAi/spoon-core)

**Node Dependencies** (`frontend/package.json`):
- `react` & `react-dom` - UI framework
- `reactflow` - Node-based editor
- `framer-motion` - Animations
- `lucide-react` - Icons
- `vite` - Build tool

---

## 🐛 Troubleshooting

### Backend Issues

**"ElevenLabs API key or Voice ID not configured"**
- Make sure your `.env` file exists in the root directory
- Verify the variable names are exactly: `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID`
- Restart the backend server after creating/updating `.env`

**"Failed to fetch" or CORS errors**
- Ensure the backend is running on port 8000
- Check that CORS is configured in `backend/main.py` for your frontend port
- Verify both servers are running

**"Module not found: spoon-core"**
- Run `pip install -r requirements.txt` again
- If using a local spoon-core, uncomment the local path line in `requirements.txt`

### Frontend Issues

**"Cannot find module" errors**
- Run `npm install` in the `frontend/` directory
- Delete `node_modules/` and `package-lock.json`, then run `npm install` again

**Port already in use**
- Change the port in `frontend/vite.config.js`
- Or kill the process using port 3000: `lsof -ti:3000 | xargs kill`

**Audio not playing**
- Check browser console for errors
- Verify ElevenLabs API credentials are correct
- Ensure backend is running and accessible

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[SpoonOS](https://github.com/XSpoonAi/spoon-core)** - Core developer framework for AI agents
- **[ElevenLabs](https://elevenlabs.io/)** - Text-to-speech API
- **[React Flow](https://reactflow.dev/)** - Node-based editor library
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[Neo Blockchain](https://neo.org/)** - Smart contract platform

---

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/pebblepay/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/pebblepay/discussions)

---

**I am Pibble. Wash my belly.** 🐾
