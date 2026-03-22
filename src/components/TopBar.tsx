import React, { useState, useEffect } from 'react';
import { Search, Sun, Moon, X } from 'lucide-react';
import { usePlayerStore } from '../store/usePlayerStore';

export const TopBar: React.FC = () => {
    const [query, setQuery] = useState('');
    const isDark = usePlayerStore(state => state.isDark);
    const toggleTheme = usePlayerStore(state => state.toggleTheme);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const searchTracks = usePlayerStore(state => state.searchTracks);
    const userName = usePlayerStore(state => state.userName);

    useEffect(() => {
        const onFullscreenChange = () => {
            setIsFullscreen(!!document.fullscreenElement);
        };
        document.addEventListener('fullscreenchange', onFullscreenChange);
        return () => document.removeEventListener('fullscreenchange', onFullscreenChange);
    }, []);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;
        searchTracks(query);
    };

    const clearSearch = () => {
        setQuery('');
        // Also might want to clear search results or close sheet depending on preference
    }

    if (isFullscreen) return null;

    return (
        <div className="w-full flex flex-col gap-2 z-10 relative mt-4 px-4">
            {userName && (
                <div className="text-xl font-bold bg-gradient-to-r from-accent-color to-pink-500 bg-clip-text text-transparent">
                    Hi, {userName}!
                </div>
            )}
            <div className="w-full flex items-center gap-3">
                <form onSubmit={handleSearch} className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={18} />
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Search songs, artists..."
                        className="w-full bg-sheet-bg backdrop-blur-md rounded-full py-3 pl-10 pr-10 text-[15px] outline-none border border-border-color shadow-sm transition-all focus:shadow-md"
                    />
                    {query && (
                        <button
                            type="button"
                            onClick={clearSearch}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-text-primary p-1"
                        >
                            <X size={16} />
                        </button>
                    )}
                </form>
                <button onClick={toggleTheme} className="p-3 bg-sheet-bg backdrop-blur-md rounded-full border border-border-color shadow-sm text-text-primary">
                    {isDark ? <Sun size={20} /> : <Moon size={20} />}
                </button>
            </div>
        </div>
    );
};
