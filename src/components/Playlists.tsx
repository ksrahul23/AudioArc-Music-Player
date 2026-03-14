import React, { useState } from 'react';
import { usePlayerStore, type Playlist } from '../store/usePlayerStore';
import { ArrowLeft, Plus, Play, Edit2, Check, Music } from 'lucide-react';

export const Playlists: React.FC = () => {
    const { playlists, setCurrentPage, createPlaylist, renamePlaylist, setQueue, setCurrentTrack } = usePlayerStore();
    const [isCreating, setIsCreating] = useState(false);
    const [newPlaylistName, setNewPlaylistName] = useState('');
    const [editingId, setEditingId] = useState<string | null>(null);
    const [editName, setEditName] = useState('');

    const handleCreate = (e: React.FormEvent) => {
        e.preventDefault();
        if (newPlaylistName.trim()) {
            createPlaylist(newPlaylistName.trim());
            setNewPlaylistName('');
            setIsCreating(false);
        }
    };

    const handleRename = (id: string) => {
        if (editName.trim()) {
            renamePlaylist(id, editName.trim());
        }
        setEditingId(null);
    };

    const playPlaylist = (playlist: Playlist) => {
        if (playlist.tracks.length > 0) {
            setQueue(playlist.tracks);
            setCurrentTrack(playlist.tracks[0]);
            setCurrentPage('home');
        }
    };

    return (
        <div className="flex-1 flex flex-col h-full bg-bg-primary text-text-primary overflow-y-auto pb-24 px-6 pt-6 relative">
            <div className="flex items-center justify-between mb-8 z-10">
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => setCurrentPage('home')}
                        className="p-2 -ml-2 rounded-full hover:bg-black/5 dark:hover:bg-white/10 transition-colors"
                    >
                        <ArrowLeft size={24} className="text-text-primary" />
                    </button>
                    <h1 className="text-3xl font-bold">Your Playlists</h1>
                </div>
                <button
                    onClick={() => setIsCreating(true)}
                    className="p-2 bg-text-primary text-bg-primary rounded-full hover:scale-105 active:scale-95 transition-transform shadow-md"
                >
                    <Plus size={24} />
                </button>
            </div>

            {isCreating && (
                <form onSubmit={handleCreate} className="mb-6 flex gap-2">
                    <input
                        autoFocus
                        type="text"
                        value={newPlaylistName}
                        onChange={(e) => setNewPlaylistName(e.target.value)}
                        placeholder="Playlist name..."
                        className="flex-1 bg-sheet-bg border border-border-color rounded-xl px-4 py-3 outline-none focus:border-accent-color shadow-sm"
                    />
                    <button type="submit" className="bg-accent-color text-white px-5 rounded-xl font-bold shadow-sm hover:opacity-90 active:scale-95 transition-all">
                        Create
                    </button>
                </form>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {playlists.map((pl) => (
                    <div key={pl.id} className="bg-sheet-bg backdrop-blur-md rounded-3xl border border-border-color p-5 shadow-sm flex flex-col group relative overflow-hidden">
                        {/* Artwork Mock */}
                        <div
                            onClick={() => playPlaylist(pl)}
                            className="w-full aspect-square rounded-2xl bg-gradient-to-br from-black/5 to-black/10 dark:from-white/10 dark:to-white/5 mb-5 flex items-center justify-center relative overflow-hidden cursor-pointer"
                        >
                            {pl.tracks.length > 0 ? (
                                <img src={pl.tracks[0].thumbnail} alt="Cover" className="w-full h-full object-cover blur-[2px] opacity-70 absolute inset-0 group-hover:scale-105 transition-transform duration-500" />
                            ) : null}
                            <Music size={40} className="text-text-primary/30 z-10 relative" />

                            {/* Play overlay overlay */}
                            <div className="absolute inset-0 bg-black/30 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity z-20 pointer-events-none">
                                <div className="w-12 h-12 bg-accent-color rounded-full flex items-center justify-center text-white shadow-xl hover:scale-110 active:scale-95 transition-transform pointer-events-auto">
                                    <Play size={20} className="ml-1" fill="currentColor" />
                                </div>
                            </div>
                        </div>

                        {editingId === pl.id ? (
                            <div className="flex items-center gap-2 mb-4">
                                <input
                                    autoFocus
                                    type="text"
                                    value={editName}
                                    onChange={(e) => setEditName(e.target.value)}
                                    className="w-full bg-black/10 dark:bg-white/10 rounded px-2 py-1 outline-none text-sm font-bold"
                                    onBlur={() => handleRename(pl.id)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleRename(pl.id)}
                                />
                                <button onClick={() => handleRename(pl.id)} className="text-accent-color p-1">
                                    <Check size={16} />
                                </button>
                            </div>
                        ) : (
                            <div className="flex items-start justify-between gap-2 mb-4">
                                <div className="min-w-0">
                                    <h3 className="font-bold text-lg truncate">{pl.name}</h3>
                                    <p className="text-sm text-text-muted mt-0.5">{pl.tracks.length} track{pl.tracks.length !== 1 ? 's' : ''}</p>
                                </div>
                                <button
                                    onClick={() => { setEditingId(pl.id); setEditName(pl.name); }}
                                    className="p-1.5 text-text-muted hover:text-text-primary rounded-md opacity-0 group-hover:opacity-100 transition-opacity"
                                >
                                    <Edit2 size={18} />
                                </button>
                            </div>
                        )}

                        {/* Track List Preview */}
                        <div className="flex-1 flex flex-col gap-2 overflow-y-auto max-h-[150px] pr-2 custom-scrollbar">
                            {pl.tracks.length > 0 ? (
                                pl.tracks.map((track, i) => (
                                    <div key={`${track.videoId}-${i}`} className="flex items-center gap-3 w-full group/track hover:bg-black/5 dark:hover:bg-white/5 rounded-lg p-2 transition-colors cursor-pointer" onClick={() => {
                                        setQueue(pl.tracks);
                                        setCurrentTrack(track);
                                        setCurrentPage('home');
                                    }}>
                                        <div className="w-8 h-8 rounded shrink-0 overflow-hidden bg-black/10 dark:bg-white/10 relative">
                                            <img src={track.thumbnail} alt={track.title} className="w-full h-full object-cover" />
                                            <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover/track:opacity-100 transition-opacity">
                                                <Play size={12} className="text-white ml-0.5" fill="currentColor" />
                                            </div>
                                        </div>
                                        <div className="min-w-0 flex-1">
                                            <p className="text-sm font-medium truncate text-text-primary group-hover/track:text-accent-color transition-colors">{track.title}</p>
                                            <p className="text-xs text-text-muted truncate">{track.artist}</p>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="flex-1 flex items-center justify-center text-sm text-text-muted py-4 border-t border-border-color border-dashed">
                                    Empty playlist
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {playlists.length === 0 && !isCreating && (
                <div className="flex-1 flex flex-col items-center justify-center text-text-muted text-center py-20">
                    <p>No playlists yet. Create one to start saving your favorite tracks!</p>
                </div>
            )}
        </div>
    );
};
