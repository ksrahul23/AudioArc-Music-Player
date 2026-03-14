import { useEffect, useState, useRef, lazy, Suspense } from 'react';
import { usePlayerStore } from './store/usePlayerStore';
import { TopBar } from './components/TopBar';
import { Player } from './components/Player';
import { BottomSheet } from './components/BottomSheet';
import { AudioPlayer } from './components/AudioPlayer';

// Lazy load new pages
const About = lazy(() => import('./components/About').then(module => ({ default: module.About })));
const Playlists = lazy(() => import('./components/Playlists').then(module => ({ default: module.Playlists })));

function App() {
  const { currentTrack, userName, setUserName, currentPage } = usePlayerStore();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const promptShown = useRef(false);

  useEffect(() => {
    // Fullscreen listener
    const onFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    document.addEventListener('fullscreenchange', onFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', onFullscreenChange);
  }, []);

  useEffect(() => {
    // Prompt for username if not set and not in a completely silent mode
    if (!userName && !promptShown.current) {
      promptShown.current = true;
      setTimeout(() => {
        const name = window.prompt("What is your name?");
        if (name) setUserName(name);
      }, 500); // slight delay so the page can mount fully
    }
  }, [userName, setUserName]);

  return (
    <div className="h-[100svh] w-full flex flex-col relative overflow-hidden bg-[var(--bg-primary)]">
      {/* Dynamic Gradient Background (Mock for now, could use dominant color extraction) */}
      <div className="absolute inset-0 opacity-40 bg-gradient-to-b from-[var(--color-brand-light)] to-transparent dark:from-black dark:to-transparent pointer-events-none transition-colors duration-1000" />

      {currentPage === 'home' && <TopBar />}

      <main className="flex-1 flex flex-col relative z-0 pb-[80px]">
        <Suspense fallback={<div className="flex-1 flex items-center justify-center">Loading...</div>}>
          {currentPage === 'home' && (
            currentTrack ? (
              <Player />
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-text-muted px-6 text-center">
                <img src="/6d6995ce9ab543205bd05c224c95db2c.svg" alt="Logo" className="w-32 h-32 mb-6 opacity-80" onError={(e) => { e.currentTarget.style.display = 'none'; }} />
                <h2 className="text-2xl font-bold mb-2 text-text-primary">Discover Music</h2>
                <p>Search for a song, artist, or album to start streaming.</p>
              </div>
            )
          )}
          {currentPage === 'about' && <About />}
          {currentPage === 'playlists' && <Playlists />}
        </Suspense>
      </main>

      {currentPage === 'home' && !isFullscreen && <BottomSheet />}
      <AudioPlayer />
    </div>
  );
}

export default App;
