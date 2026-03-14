import React from 'react';
import { usePlayerStore } from '../store/usePlayerStore';
import { ArrowLeft, Github, Heart } from 'lucide-react';

export const About: React.FC = () => {
    const setCurrentPage = usePlayerStore(state => state.setCurrentPage);

    return (
        <div className="flex-1 flex flex-col h-full bg-bg-primary text-text-primary overflow-y-auto pb-24 px-6 pt-6">
            <div className="flex items-center gap-4 mb-8">
                <button
                    onClick={() => setCurrentPage('home')}
                    className="p-2 -ml-2 rounded-full hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
                >
                    <ArrowLeft size={24} className="text-text-primary" />
                </button>
                <h1 className="text-3xl font-bold">About the App</h1>
            </div>

            <div className="w-full max-w-md mx-auto space-y-6">
                <div className="bg-sheet-bg backdrop-blur-md rounded-3xl p-6 border border-border-color shadow-sm text-center">
                    <img src="/6d6995ce9ab543205bd05c224c95db2c.jpg" alt="Logo" className="w-20 h-20 mx-auto rounded-2xl mb-4 shadow-lg object-cover" onError={(e) => { e.currentTarget.style.display = 'none'; }} />
                    <h2 className="text-2xl font-bold mb-2">AudioArc</h2>
                    <p className="text-text-muted mb-4">Version 1.0.0</p>
                    <p className="text-sm leading-relaxed mb-6">
                        A beautiful, zero-latency streaming application designed to bring the
                        premium music experience straight to your browser. Built with a modern
                        tech stack including React, Vite, Framer Motion, and Tailwind CSS.
                    </p>

                    <div className="pt-6 border-t border-border-color">
                        <p className="text-sm text-text-muted mb-1">Created By</p>
                        <p className="text-lg font-bold bg-gradient-to-r from-accent-color to-pink-500 bg-clip-text text-transparent inline-flex items-center gap-2">
                            Rahul Kumar <Heart size={16} className="text-accent-color" fill="currentColor" />
                        </p>
                    </div>
                </div>

                <a
                    href="https://github.com/ksrahul23/AudioArc-Music-Player"
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center justify-between bg-sheet-bg backdrop-blur-md rounded-2xl p-4 border border-border-color shadow-sm hover:shadow-md transition-all active:scale-95"
                >
                    <div className="flex items-center gap-3">
                        <Github size={24} className="text-text-primary" />
                        <span className="font-semibold">View Source Code</span>
                    </div>
                    <ArrowLeft size={20} className="text-text-muted rotate-135" />
                </a>
            </div>
        </div>
    );
};
