import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { API_BASE_URL } from '../config';

export interface Track {
    videoId: string;
    title: string;
    artist: string;
    thumbnail: string;
    duration: number;
}

export interface Playlist {
    id: string;
    name: string;
    tracks: Track[];
}

interface PlayerState {
    currentTrack: Track | null;
    queue: Track[];
    isPlaying: boolean;
    progress: number;
    duration: number;
    streamUrl: string | null;
    volume: number;
    seekTarget: number | null;

    searchResults: Track[];
    isSearching: boolean;
    searchError: string | null;
    isSheetOpen: boolean;

    userName: string;
    currentPage: 'home' | 'about' | 'playlists';
    playlists: Playlist[];

    setCurrentTrack: (track: Track) => void;
    setQueue: (queue: Track[]) => void;
    setIsPlaying: (isPlaying: boolean) => void;
    setProgress: (progress: number) => void;
    setDuration: (duration: number) => void;
    setStreamUrl: (url: string | null) => void;
    setVolume: (volume: number) => void;
    setSeekTarget: (target: number | null) => void;
    searchTracks: (query: string) => Promise<void>;
    setIsSheetOpen: (isOpen: boolean) => void;
    setSearchError: (error: string | null) => void;

    setUserName: (name: string) => void;
    setCurrentPage: (page: 'home' | 'about' | 'playlists') => void;
    createPlaylist: (name: string) => void;
    renamePlaylist: (id: string, name: string) => void;
    addToPlaylist: (playlistId: string, track: Track) => void;

    playNext: () => void;
    playPrevious: () => void;
}

export const usePlayerStore = create<PlayerState>()(
    persist(
        (set, get) => ({
            currentTrack: null,
            queue: [],
            isPlaying: false,
            progress: 0,
            duration: 0,
            streamUrl: null,
            volume: 1,
            seekTarget: null,
            searchResults: [],
            isSearching: false,
            searchError: null,
            isSheetOpen: false,

            userName: '',
            currentPage: 'home',
            playlists: [
                { id: 'liked', name: 'Liked Songs', tracks: [] }
            ],

            setCurrentTrack: (track: Track) => set((state) => ({
                currentTrack: track,
                streamUrl: state.currentTrack?.videoId === track.videoId ? state.streamUrl : null,
                progress: 0,
                isPlaying: true,
                seekTarget: state.currentTrack?.videoId === track.videoId ? 0 : null
            })),
            setQueue: (queue: Track[]) => set({ queue }),
            setIsPlaying: (isPlaying: boolean) => set({ isPlaying }),
            setProgress: (progress: number) => set({ progress }),
            setDuration: (duration: number) => set({ duration }),
            setStreamUrl: (streamUrl: string | null) => set({ streamUrl }),
            setVolume: (volume: number) => set({ volume }),
            setSeekTarget: (seekTarget: number | null) => set({ seekTarget }),
            setIsSheetOpen: (isOpen: boolean) => set({ isSheetOpen: isOpen }),
            setSearchError: (error: string | null) => set({ searchError: error }),

            setUserName: (name: string) => set({ userName: name }),
            setCurrentPage: (page) => set({ currentPage: page }),

            createPlaylist: (name: string) => set((state) => ({
                playlists: [...state.playlists, { id: Date.now().toString(), name, tracks: [] }]
            })),

            renamePlaylist: (id: string, name: string) => set((state) => ({
                playlists: state.playlists.map(pl => pl.id === id ? { ...pl, name } : pl)
            })),

            addToPlaylist: (playlistId: string, track: Track) => set((state) => ({
                playlists: state.playlists.map(pl => {
                    if (pl.id === playlistId) {
                        // Avoid duplicates
                        if (pl.tracks.find(t => t.videoId === track.videoId)) return pl;
                        return { ...pl, tracks: [...pl.tracks, track] };
                    }
                    return pl;
                })
            })),

            searchTracks: async (query: string) => {
                set({ isSearching: true, isSheetOpen: true, searchError: null });
                try {
                    const res = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(query)}`);
                    if (!res.ok) {
                        const errData = await res.json().catch(() => ({}));
                        throw new Error(errData.detail || `Server error: ${res.status}`);
                    }
                    const data = await res.json();
                    set({ searchResults: data.results || [], isSearching: false });
                } catch (error: any) {
                    console.error('Search failed', error);
                    const isNetworkError = error instanceof TypeError && error.message.includes('fetch');
                    set({
                        searchResults: [],
                        isSearching: false,
                        searchError: isNetworkError
                            ? 'Cannot connect to backend. Make sure the local server is running, or configure VITE_API_URL in .env to use a remote backend.'
                            : (error.message || 'Search failed. Please try again.')
                    });
                }
            },

            playNext: () => {
                const { queue, currentTrack } = get();
                if (!currentTrack || queue.length === 0) return;
                const currentIndex = queue.findIndex((t: Track) => t.videoId === currentTrack.videoId);
                if (currentIndex !== -1 && currentIndex < queue.length - 1) {
                    set({ currentTrack: queue[currentIndex + 1], streamUrl: null, progress: 0 });
                }
            },

            playPrevious: () => {
                const { queue, currentTrack } = get();
                if (!currentTrack || queue.length === 0) return;
                const currentIndex = queue.findIndex((t: Track) => t.videoId === currentTrack.videoId);
                if (currentIndex > 0) {
                    set({ currentTrack: queue[currentIndex - 1], streamUrl: null, progress: 0 });
                }
            }
        }),
        {
            name: 'audioarc-storage', // unique name
            storage: createJSONStorage(() => localStorage),
            partialize: (state) => ({ userName: state.userName, playlists: state.playlists }),
        }
    )
);
