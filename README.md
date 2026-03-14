# AudioArc: Modern Real-time Music Streaming

AudioArc is a premium, full-stack music streaming application designed for a seamless, high-performance user experience. It leverages a modern tech stack to provide instant search and streaming capabilities.

## 🚀 Project Architecture

The project is structured into two main components: a high-performance Python backend and a responsive React frontend.

### 🌐 Backend (`/backend`)
A FastAPI-powered service that interfaces with YouTube for real-time music discovery.
- **Tech Stack**: FastAPI, Python 3.10+, `yt-dlp`.
- **Key Features**:
  - `GET /api/search`: Real-time YouTube search and metadata extraction.
  - `GET /api/stream`: Dynamic extraction of high-quality audio stream URLs.
  - Asynchronous processing for reduced latency.

### 🎨 Frontend (Root)
A sleek, modern UI built for speed and visual excellence.
- **Tech Stack**: React 19, TypeScript, Vite, Tailwind CSS, Framer Motion.
- **State Management**: Zustand (with state persistence for playlists and user data).
- **Key Features**:
  - **Dynamic Player**: Interactive vinyl record animation synced with playback.
  - **Theming**: Premium Dark and Light modes with unique HSL-tailored palettes.
  - **Playlist Management**: Local persistence of user-created playlists and "Liked Songs".
  - **Keyboard Shortcuts**: `F` for fullscreen, `Arrow keys` for seeking (+/- 10s).
  - **Zero-Latency Feel**: Optimized streaming logic for instant playback.

## 🛠️ Getting Started

### Prerequisites
- Node.js & npm
- Python 3.10+
- `ffmpeg` (for audio processing via yt-dlp)

### Running the Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Running the Frontend
```bash
npm install
npm run dev
```

## ✍️ Author
**Rahul Kumar**
