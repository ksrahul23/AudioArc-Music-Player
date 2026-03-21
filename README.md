# AudioArc: Modern Real-time Music Streaming

AudioArc is a premium, full-stack music streaming application designed for a seamless, high-performance user experience. It leverages a modern tech stack to provide instant search and "bulletproof" streaming via a Cloudflare Worker bridge.

## 🚀 Project Architecture

The project is structured into three main components:
1.  **Render Backend (`/backend`)**: A FastAPI service for high-speed YouTube search and metadata extraction.
2.  **Cloudflare Worker (`worker.js`)**: A streaming proxy that fetches audio bytes from YouTube's global network, bypassing data center IP blocks.
3.  **React Frontend (Root)**: A sleek, modern UI that combines metadata from Render with audio streams from Cloudflare.

## 🛠️ Features
- **"Bulletproof" Streaming**: Uses Cloudflare Workers to bypass YouTube IP blocks on cloud providers like Render.
- **Instant Search**: Optimized `yt-dlp` search with persistent cookie handling.
- **Dynamic Player**: Interactive vinyl record animation synced with playback.
- **Playlist Management**: Local persistence for Liked Songs and custom playlists.
- **Zero-Latency Feel**: High-speed chunked streaming for instant music playback.

## 🛠️ Getting Started

### 1. Cloudflare Worker Setup (Required)
This is essential for playback to work on a deployed site.
- Deploy the code in `backend/worker.js` to a new Cloudflare Worker.
- Add your Worker URL to `src/config.ts`.
- See `deployment_guide.md` for the step-by-step guide.

### 2. Running Locally
```bash
npm run dev:all
```

## ✍️ Author
**Rahul Kumar**
