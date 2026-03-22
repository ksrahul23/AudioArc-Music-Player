import React from 'react';
import { motion } from 'framer-motion';
import { Play, Pause, SkipForward, SkipBack, Settings, Rewind, FastForward, Maximize, Github, Info, ListPlus, Check } from 'lucide-react';
import { usePlayerStore } from '../store/usePlayerStore';
import { useState, useEffect } from 'react';

export const Player: React.FC = () => {
    const { currentTrack, isPlaying, setIsPlaying, playNext, playPrevious, progress, duration, streamUrl, setSeekTarget, setCurrentPage, playlists, addToPlaylist } = usePlayerStore();
    const [showSettings, setShowSettings] = useState(false);
    const [showPlaylists, setShowPlaylists] = useState(false);
    const [activeKey, setActiveKey] = useState<'left' | 'right' | null>(null);
    const [isDragging, setIsDragging] = useState(false);
    const [dragProgress, setDragProgress] = useState(0);

    // Quick and dirty click-outside for menus if needed, or just handle it simply with a backdrop
    const handleSeek = (amount: number) => {
        let newTime = progress + amount;
        if (newTime < 0) newTime = 0;
        if (newTime > duration) newTime = duration;
        setSeekTarget(newTime);
    };

    const handleFullscreen = () => {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(err => {
                console.error(`Error attempting to enable fullscreen: ${err.message}`);
            });
        } else {
            document.exitFullscreen();
        }
        setShowSettings(false);
    };

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            // Ignore if typing in an input
            if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;

            if (e.key.toLowerCase() === 'f') {
                handleFullscreen();
            } else if (e.key === 'ArrowLeft') {
                handleSeek(-10);
                setActiveKey('left');
            } else if (e.key === 'ArrowRight') {
                handleSeek(10);
                setActiveKey('right');
            }
        };

        const handleKeyUp = (e: KeyboardEvent) => {
            if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                setActiveKey(null);
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        window.addEventListener('keyup', handleKeyUp);

        return () => {
            window.removeEventListener('keydown', handleKeyDown);
            window.removeEventListener('keyup', handleKeyUp);
        };
    }, [progress, duration, setSeekTarget]); // Dependency on progress/duration for accurate seek calculations

    if (!currentTrack) return null;

    const formatTime = (seconds: number) => {
        if (isNaN(seconds)) return "0:00";
        const m = Math.floor(seconds / 60);
        const s = Math.floor(seconds % 60);
        return `${m}:${s < 10 ? '0' : ''}${s}`;
    };

    const progressPercent = duration > 0 ? (progress / duration) * 100 : 0;

    return (
        <div className="flex-1 flex flex-col items-center justify-center w-full max-w-md mx-auto px-6 py-4 relative z-10">

            {/* Vinyl Record */}
            <div className="relative w-64 h-64 sm:w-72 sm:h-72 mb-8">
                <motion.div
                    className="w-full h-full rounded-full border-[16px] border-[#111] bg-[#222] shadow-2xl flex items-center justify-center overflow-hidden"
                    animate={{ rotate: isPlaying && streamUrl ? 360 : 0 }}
                    transition={{ repeat: Infinity, duration: 10, ease: "linear", bounce: 0 }}
                    style={{ backgroundImage: 'repeating-radial-gradient(#111 0px, #1a1a1a 2px, #111 4px)' }}
                >
                    <img
                        src={currentTrack.thumbnail}
                        alt={currentTrack.title}
                        className="w-32 h-32 rounded-full object-cover shadow-inner pointer-events-none"
                    />
                    {/* Vinyl center hole */}
                    <div className="absolute w-4 h-4 bg-gray-300 rounded-full shadow-inner border border-gray-400"></div>
                </motion.div>
            </div>

            {/* Track Info */}
            <div className="text-center mb-6 w-full">
                <h2 className="text-2xl font-bold text-text-primary mb-1 truncate">{currentTrack.title}</h2>
                <p className="text-accent-color font-medium text-sm truncate">{currentTrack.artist}</p>
            </div>

            {/* Progress & Waveform (Mock waveform logic for style) */}
            <div className="w-full mb-8">
                <div className="h-4 w-full flex items-center justify-center space-x-[2px] mb-2 px-2 overflow-hidden opacity-50">
                    {/* Fake waveform bars */}
                    {Array.from({ length: 40 }).map((_, i) => (
                        <motion.div
                            key={i}
                            className="w-1 bg-accent-color rounded-full"
                            animate={{ height: isPlaying && streamUrl ? ['4px', `${Math.random() * 16 + 4}px`, '4px'] : '4px' }}
                            transition={{ repeat: Infinity, duration: Math.random() * 0.5 + 0.5 }}
                            style={{ height: '4px' }}
                        />
                    ))}
                </div>

                <div className="flex items-center justify-between text-xs text-text-muted mb-2 px-1">
                    <span>{formatTime(progress)}</span>
                    <span>{formatTime(duration)}</span>
                </div>

                <div className="relative w-full h-4 flex items-center -mt-2 group">
                    <input
                        type="range"
                        min={0}
                        max={duration || 100}
                        value={isDragging ? dragProgress : progress}
                        onMouseDown={() => setIsDragging(true)}
                        onMouseUp={() => {
                            setIsDragging(false);
                            setSeekTarget(dragProgress);
                        }}
                        onTouchStart={() => setIsDragging(true)}
                        onTouchEnd={() => {
                            setIsDragging(false);
                            setSeekTarget(dragProgress);
                        }}
                        onChange={(e) => setDragProgress(Number(e.target.value))}
                        className="absolute top-0 left-0 w-full h-full opacity-0 cursor-pointer z-20"
                    />
                    <div className="w-full h-1.5 bg-border-color rounded-full overflow-hidden pointer-events-none z-0">
                        <div
                            className="h-full bg-accent-color rounded-full transition-all duration-100 ease-linear"
                            style={{ width: `${isDragging ? (dragProgress / (duration || 100)) * 100 : progressPercent}%` }}
                        />
                    </div>
                    {/* The handle dot */}
                    <div
                        className="absolute top-1/2 -mt-2 w-4 h-4 bg-white border-2 border-accent-color rounded-full transition-all duration-100 ease-linear shadow-sm z-10 pointer-events-none group-active:scale-125 group-hover:scale-110"
                        style={{ left: `calc(${isDragging ? (dragProgress / (duration || 100)) * 100 : progressPercent}% - 8px)` }}
                    />
                </div>
            </div>

            {/* Playback Controls */}
            <div className="w-full grid grid-cols-3 items-center px-1 relative">

                {/* Left side: Settings */}
                <div className="flex justify-start">
                    <div className="relative">
                        <button
                            onClick={() => { setShowSettings(!showSettings); setShowPlaylists(false); }}
                            className="p-3 text-text-muted hover:text-text-primary transition-colors bg-white/5 dark:bg-black/20 rounded-xl"
                        >
                            <Settings size={20} />
                        </button>

                        {showSettings && (
                            <>
                                <div className="fixed inset-0 z-40" onClick={() => setShowSettings(false)}></div>
                                <div className="absolute bottom-full left-0 mb-4 w-48 bg-sheet-bg backdrop-blur-2xl border border-border-color rounded-2xl shadow-xl overflow-hidden z-50 animate-in fade-in slide-in-from-bottom-2">
                                    <button onClick={handleFullscreen} className="w-full text-left px-4 py-3 flex items-center gap-3 hover:bg-black/5 dark:hover:bg-white/5 transition-colors">
                                        <Maximize size={18} className="text-text-muted" />
                                        <span className="text-sm font-medium">Fullscreen</span>
                                    </button>
                                    <a href="https://github.com/ksrahul23/AudioArc-Music-Player" target="_blank" rel="noreferrer" onClick={() => setShowSettings(false)} className="w-full text-left px-4 py-3 flex items-center gap-3 hover:bg-black/5 dark:hover:bg-white/5 transition-colors">
                                        <Github size={18} className="text-text-muted" />
                                        <span className="text-sm font-medium">GitHub Repo</span>
                                    </a>
                                    <button onClick={() => { setCurrentPage('about'); setShowSettings(false); }} className="w-full text-left px-4 py-3 flex items-center gap-3 hover:bg-black/5 dark:hover:bg-white/5 transition-colors border-t border-border-color/50">
                                        <Info size={18} className="text-text-muted" />
                                        <span className="text-sm font-medium">About App</span>
                                    </button>
                                </div>
                            </>
                        )}
                    </div>
                </div>

                {/* Center Group */}
                <div className="flex flex-col items-center gap-2">
                    <div className="flex items-center gap-1.5 sm:gap-4 relative">
                        <button
                            onClick={() => handleSeek(-10)}
                            className={`transition-all text-[10px] sm:text-xs font-bold flex flex-col items-center ${activeKey === 'left' ? 'text-text-primary scale-110 opacity-100' : 'text-text-muted hover:text-text-primary opacity-60'}`}
                        >
                            <Rewind size={18} />
                            -10s
                        </button>

                        <button onClick={playPrevious} className="p-2 sm:p-3 text-text-primary hover:text-accent-color transition-colors bg-white/10 dark:bg-black/30 rounded-2xl">
                            <SkipBack className="w-5 h-5 sm:w-6 sm:h-6" fill="currentColor" />
                        </button>

                        <button
                            onClick={() => setIsPlaying(!isPlaying)}
                            className="w-14 h-14 sm:w-16 sm:h-16 flex items-center justify-center bg-accent-color text-white rounded-[20px] sm:rounded-[24px] shadow-lg hover:scale-105 active:scale-95 transition-all mx-1 sm:mx-2"
                        >
                            {isPlaying ? <Pause className="w-6 h-6 sm:w-7 sm:h-7" fill="currentColor" /> : <Play className="w-6 h-6 sm:w-7 sm:h-7 ml-1" fill="currentColor" />}
                        </button>

                        <button onClick={playNext} className="p-2 sm:p-3 text-text-primary hover:text-accent-color transition-colors bg-white/10 dark:bg-black/30 rounded-2xl">
                            <SkipForward className="w-5 h-5 sm:w-6 sm:h-6" fill="currentColor" />
                        </button>

                        <button
                            onClick={() => handleSeek(10)}
                            className={`transition-all text-[10px] sm:text-xs font-bold flex flex-col items-center ${activeKey === 'right' ? 'text-text-primary scale-110 opacity-100' : 'text-text-muted hover:text-text-primary opacity-60'}`}
                        >
                            <FastForward size={18} />
                            +10s
                        </button>
                    </div>
                </div>

                {/* Right side: Add to Playlist */}
                <div className="flex justify-end">
                    <div className="relative">
                        <button
                            onClick={() => { setShowPlaylists(!showPlaylists); setShowSettings(false); }}
                            className="p-3 text-text-muted hover:text-text-primary transition-colors bg-white/5 dark:bg-black/20 rounded-xl"
                        >
                            <ListPlus size={20} />
                        </button>

                        {showPlaylists && (
                            <>
                                <div className="fixed inset-0 z-40" onClick={() => setShowPlaylists(false)}></div>
                                <div className="absolute bottom-full right-0 mb-4 w-56 bg-sheet-bg backdrop-blur-2xl border border-border-color rounded-2xl shadow-xl z-50 flex flex-col max-h-64 animate-in fade-in slide-in-from-bottom-2">
                                    <div className="px-4 py-3 border-b border-border-color/50 font-bold text-sm">Add to Playlist</div>
                                    <div className="overflow-y-auto no-scrollbar py-2">
                                        {playlists.map(pl => {
                                            const isInPlaylist = pl.tracks.some(t => t.video_id === currentTrack?.video_id);
                                            return (
                                                <button
                                                    key={pl.id}
                                                    onClick={() => {
                                                        if (!isInPlaylist && currentTrack) {
                                                            addToPlaylist(pl.id, currentTrack);
                                                            setShowPlaylists(false);
                                                        }
                                                    }}
                                                    disabled={isInPlaylist}
                                                    className={`w-full text-left px-4 py-2.5 flex items-center justify-between transition-colors ${isInPlaylist ? 'opacity-50 cursor-not-allowed' : 'hover:bg-black/5 dark:hover:bg-white/5'}`}
                                                >
                                                    <span className="text-sm font-medium truncate pr-2">{pl.name}</span>
                                                    {isInPlaylist && <Check size={16} className="text-accent-color shrink-0" />}
                                                </button>
                                            );
                                        })}
                                    </div>
                                    <button
                                        onClick={() => { setCurrentPage('playlists'); setShowPlaylists(false); }}
                                        className="w-full text-center px-4 py-3 text-sm font-semibold text-accent-color border-t border-border-color/50 hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
                                    >
                                        Manage Playlists
                                    </button>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </div>

        </div>
    );
};
