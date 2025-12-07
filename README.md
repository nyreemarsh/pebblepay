# 🐾 PibblePay

*A playful smart-contract playground powered by SpoonOS + Neo.*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![SpoonOS](https://img.shields.io/badge/SpoonOS-Integrated-blueviolet.svg)](https://github.com/XSpoonAi/spoon-core)
[![License](https://img.shields.io/badge/License-Apache--2.0-green.svg)](LICENSE)

---

## 🏆 SpoonOS Hackathon Integration

> **This project satisfies all baseline technical requirements for the SpoonOS Hackathon.**

### ✅ Requirement 1: LLM via SpoonOS (Core Requirement)

PibblePay invokes LLM capabilities through SpoonOS's unified protocol layer.

**Flow:** `Agent → SpoonOS ChatBot → Google Gemini LLM`

**Implementation:** [`backend/app/llm.py`](backend/app/llm.py)

```python
from spoon_ai.chat import ChatBot

class GeminiLLM:
    def __init__(self, model_name: str = "models/gemini-2.0-flash"):
        # Initialize SpoonOS ChatBot with Google/Gemini provider
        # This creates the Agent → SpoonOS → LLM flow
        self.chatbot = ChatBot(
            model_name=model_name,
            llm_provider="google"
        )
    
    async def chat(self, prompt: str) -> str:
        # Use SpoonOS ChatBot for LLM invocation
        response = await self.chatbot.chat(prompt)
        return response
```

**Used for:**
- Natural language contract creation
- Smart contract code generation (Solidity & Neo Python)
- Contract explanation and summarization

---

### ✅ Requirement 2: SpoonOS Toolkit Module (4EVERLAND Storage)

PibblePay uses the **4EVERLAND Storage toolkit** from [SpoonOS Toolkit](https://xspoonai.github.io/Toolkit/) to save generated smart contracts to decentralized IPFS storage.

**Flow:** `API Request → SpoonOS 4EVERLAND Toolkit → IPFS Storage`

**Implementation:** [`backend/app/services/storage_service.py`](backend/app/services/storage_service.py)

```python
from spoon_ai.tools.storage import FourEverlandStorage

class ContractStorageService:
    def __init__(self):
        # Initialize SpoonOS 4EVERLAND toolkit
        self._storage = FourEverlandStorage(
            api_key=os.getenv("FOUREVERLAND_API_KEY"),
            bucket="pebblepay-contracts"
        )
    
    async def save_contract(self, contract_code: str, contract_name: str):
        # Upload to IPFS via SpoonOS toolkit
        result = await self._storage.upload(
            content=contract_code,
            filename=f"{contract_name}.sol"
        )
        return {
            "ipfs_hash": result.hash,
            "gateway_url": result.gateway_url
        }
```

**API Endpoint:** `POST /api/storage/save-contract`

**Response Example:**
```json
{
  "ipfs_hash": "Qm8e537f3923dbd5b856a6f72a5f17ef26907ca1f7b6eb54",
  "gateway_url": "https://4everland.io/ipfs/Qm8e537f3923dbd5b856a6f72a5f17ef26907ca1f7b6eb54",
  "filename": "MyContract_20251207_110406.sol",
  "status": "success"
}
```

---

### 🎁 Bonus: Neo Blockchain Integration

PibblePay generates **Neo Boa Python** smart contracts alongside Solidity, enabling deployment to the Neo blockchain.

**Implementation:** [`backend/app/agents/neo_agent.py`](backend/app/agents/neo_agent.py)

---

### 📚 SpoonOS References

| Resource | Link |
|----------|------|
| SpoonOS Core | [github.com/XSpoonAi/spoon-core](https://github.com/XSpoonAi/spoon-core) |
| SpoonOS Docs | [xspoonai.github.io](https://xspoonai.github.io/) |
| Toolkit Catalog | [xspoonai.github.io/Toolkit](https://xspoonai.github.io/Toolkit/) |
| LLM Reference | [spoon_ai/llm](https://github.com/XSpoonAi/spoon-core/tree/main/spoon_ai/llm) |
| Tools Reference | [spoon_ai/tools](https://github.com/XSpoonAi/spoon-core/tree/main/spoon_ai/tools) |

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

Create a `.env` file in the `pebblepay/pebblepay/pebblepay/` directory:

```env
# ===========================================
# REQUIRED: Google Gemini API (for SpoonOS LLM)
# ===========================================
GEMINI_API_KEY=your_gemini_api_key_here

# ===========================================
# OPTIONAL: ElevenLabs (for Text-to-Speech)
# ===========================================
ELEVENLABS_API_KEY=your_api_key_here
ELEVENLABS_VOICE_ID=your_voice_id_here

# ===========================================
# OPTIONAL: 4EVERLAND (for IPFS Storage)
# Works in demo mode without API key
# ===========================================
FOUREVERLAND_API_KEY=your_4everland_api_key_here
FOUREVERLAND_BUCKET=pebblepay-contracts
FOUREVERLAND_GATEWAY=https://4everland.io/ipfs
```

#### Getting API Keys

| Service | How to Get | Required? |
|---------|------------|-----------|
| **Gemini API** | [Google AI Studio](https://aistudio.google.com/apikey) → Create API key in new project | ✅ Yes |
| **ElevenLabs** | [ElevenLabs Dashboard](https://elevenlabs.io/) → Profile → API Key | Optional |
| **4EVERLAND** | [4EVERLAND Dashboard](https://dashboard.4everland.org/) → Bucket Storage | Optional |

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

## 🚀 Deployment

### Deploying to Production (Vercel + Railway)

PibblePay uses a split deployment: **Frontend on Vercel** + **Backend on Railway**.

#### Step 1: Push to GitHub

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

#### Step 2: Deploy Backend to Railway

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository
4. Configure the service:
   - **Root Directory:** `pebblepay/pebblepay/pebblepay/backend`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add **Environment Variables** in Railway dashboard:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   ELEVENLABS_API_KEY=your_elevenlabs_key (optional)
   ELEVENLABS_VOICE_ID=your_voice_id (optional)
   FOUREVERLAND_API_KEY=your_key (optional)
   ```
6. Click **Deploy** and wait for it to complete
7. Copy your Railway URL (e.g., `https://pebblepay-backend.railway.app`)

#### Step 3: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click **"Add New Project"** → Import your repository
3. Configure the project:
   - **Root Directory:** `pebblepay/pebblepay/pebblepay/frontend`
   - **Framework Preset:** Vite
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Add **Environment Variable**:
   ```
   VITE_API_URL=https://your-railway-backend-url.railway.app
   ```
5. Click **Deploy**

#### Step 4: Test Your Deployment

1. Visit your Vercel URL (e.g., `https://pebblepay.vercel.app`)
2. The frontend should connect to your Railway backend
3. Test the chat and contract generation features

### Alternative Backend Hosts

| Platform | Deployment |
|----------|------------|
| **Render** | [render.com](https://render.com) → New Web Service → Connect GitHub |
| **Fly.io** | `fly launch` in backend directory |
| **Heroku** | Uses the included `Procfile` |

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
