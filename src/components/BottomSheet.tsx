import React, { useRef } from 'react';
import { motion, useDragControls, type PanInfo } from 'framer-motion';
import { usePlayerStore, type Track } from '../store/usePlayerStore';
import { Play } from 'lucide-react';

export const BottomSheet: React.FC = () => {
    const {
        isSheetOpen,
        setIsSheetOpen,
        searchResults,
        isSearching,
        searchError,
        setCurrentTrack,
        setQueue,
        currentTrack
    } = usePlayerStore();

    const controls = useDragControls();
    const sheetRef = useRef<HTMLDivElement>(null);

    const handleDragEnd = (_: any, info: PanInfo) => {
        if (info.offset.y > 100) {
            setIsSheetOpen(false);
        } else if (info.offset.y < -50) {
            setIsSheetOpen(true);
        }
    };

    const handleTrackSelect = (track: Track) => {
        setCurrentTrack(track);
        // Set queue to the search results starting from current track
        setQueue(searchResults);
        // Optionally close sheet for smaller screens so music player is visible
        if (window.innerWidth < 1024) setIsSheetOpen(false);
    };

    // 0% translates to resting position (peek)
    // -100% or similar translates to full open
    const variants = {
        closed: { y: "85%", transition: { type: "spring" as const, damping: 25, stiffness: 200 } },
        open: { y: "10%", transition: { type: "spring" as const, damping: 25, stiffness: 200 } }
    };

    return (
        <motion.div
            ref={sheetRef}
            initial="closed"
            animate={isSheetOpen ? "open" : "closed"}
            variants={variants}
            drag="y"
            dragControls={controls}
            dragConstraints={{ top: 0, bottom: 0 }}
            dragElastic={0.2}
            onDragEnd={handleDragEnd}
            className="absolute bottom-0 left-0 right-0 h-[90svh] bg-sheet-bg backdrop-blur-2xl rounded-t-3xl shadow-[0_-10px_40px_rgba(0,0,0,0.1)] dark:shadow-[0_-10px_40px_rgba(0,0,0,0.5)] border border-border-color flex flex-col z-50 overflow-hidden"
        >
            {/* Drag Handle */}
            <div
                className="w-full h-12 flex items-center justify-center cursor-grab active:cursor-grabbing pb-2 pt-4"
                onPointerDown={(e) => controls.start(e)}
            >
                <div className="w-12 h-1.5 bg-text-muted rounded-full opacity-50" />
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-y-auto px-6 pb-20 no-scrollbar">
                <h3 className="text-sm font-bold text-text-muted mb-4 tracking-wider uppercase">
                    {searchResults.length > 0 ? 'Search Results' : 'Up Next'}
                </h3>

                {isSearching ? (
                    <div className="flex justify-center items-center py-10">
                        <div className="w-8 h-8 border-4 border-accent-color border-t-transparent rounded-full animate-spin"></div>
                    </div>
                ) : searchError ? (
                    <div className="text-center py-10 px-4">
                        <p className="text-red-400 font-semibold text-sm mb-1">Search failed</p>
                        <p className="text-text-muted text-xs">{searchError}</p>
                    </div>
                ) : searchResults.length > 0 ? (
                    <div className="space-y-2">
                        {searchResults.map((track, i) => (
                            <div
                                key={track.videoId + i}
                                onClick={() => handleTrackSelect(track)}
                                className={`flex items-center gap-4 p-3 rounded-2xl cursor-pointer transition-colors hover:bg-black/5 dark:hover:bg-white/5 ${currentTrack?.videoId === track.videoId ? 'bg-accent-bg' : ''}`}
                            >
                                <div className="relative w-12 h-12 rounded-xl overflow-hidden shrink-0 shadow-sm">
                                    <img src={track.thumbnail} alt={track.title} className="w-full h-full object-cover" />
                                    <div className="absolute inset-0 bg-black/20 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                                        <Play size={16} className="text-white ml-0.5" fill="currentColor" />
                                    </div>
                                </div>
                                <div className="flex-1 min-w-0">
                                    <h4 className={`text-[15px] font-semibold truncate ${currentTrack?.videoId === track.videoId ? 'text-accent-color' : 'text-text-primary'}`}>
                                        {track.title}
                                    </h4>
                                    <p className="text-xs text-text-muted truncate mt-0.5">{track.artist}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-10 text-text-muted">
                        <p>No tracks in queue. Search to add some!</p>
                    </div>
                )}
            </div>
        </motion.div>
    );
};
