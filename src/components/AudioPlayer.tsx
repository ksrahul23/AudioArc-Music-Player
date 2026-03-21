import React, { useRef, useEffect } from 'react';
import { usePlayerStore } from '../store/usePlayerStore';
import { API_BASE_URL, CLOUDFLARE_WORKER_URL } from '../config';

export const AudioPlayer: React.FC = () => {
    const audioRef = useRef<HTMLAudioElement>(null);
    const { currentTrack, streamUrl, setStreamUrl, isPlaying, setIsPlaying, setProgress, setDuration, playNext, seekTarget, setSeekTarget } = usePlayerStore();

    // Fetch Stream URL whenever currentTrack changes
    useEffect(() => {
        let active = true;
        if (!currentTrack) return;

        const fetchStream = async () => {
            try {
                let streamUrl = '';
                
                // 1. CLOUDFLARE WORKER BRIDGE (The "Bulletproof" Method)
                try {
                    console.log("🌊 Attempting extraction via Cloudflare Worker Bridge...");
                    
                    // First, get the raw Google Video URL from Render
                    const metaResponse = await fetch(`${API_BASE_URL}/get_stream_link/${currentTrack.video_id}`);
                    if (metaResponse.ok) {
                        const data = await metaResponse.json();
                        const rawGoogleUrl = data.stream_url;
                        
                        if (rawGoogleUrl) {
                            // Only use Worker if it's not the default placeholder
                            if (CLOUDFLARE_WORKER_URL && !CLOUDFLARE_WORKER_URL.includes('your-worker.workers.dev')) {
                                streamUrl = `${CLOUDFLARE_WORKER_URL}/?url=${encodeURIComponent(rawGoogleUrl)}`;
                                console.log("✅ Using Cloudflare Worker Proxy for bytes.");
                            } else {
                                console.warn("⚠️ Cloudflare Worker URL not configured. See README.md.");
                            }
                        }
                    } else {
                        console.warn(`❌ Render metadata fetch failed with status ${metaResponse.status}`);
                    }
                } catch (e) {
                    console.warn("⚠️ Cloudflare method failed, falling back to backend bridge:", e);
                }

                // 2. BACKEND FALLBACK: If Cloudflare failed or not configured, use the Render bridge
                if (!streamUrl) {
                    console.log("📡 Falling back to backend bridge (Render IP)...");
                    const response = await fetch(`${API_BASE_URL}/stream/${currentTrack.video_id}`);
                    if (!response.ok) throw new Error("Failed to fetch stream from backend");
                    const data = await response.json();
                    streamUrl = data.stream_url;
                }

                if (active) {
                    setStreamUrl(streamUrl);
                    setIsPlaying(true);
                }
            } catch (error) {
                console.error("Stream fetch error:", error);
                setIsPlaying(false);
            }
        };

        fetchStream();

        return () => { active = false; };
    }, [currentTrack?.video_id, setStreamUrl, setIsPlaying]);

    // Handle Audio Element State Sync
    useEffect(() => {
        if (audioRef.current) {
            if (isPlaying && streamUrl) {
                // Only play if we have a valid source ready
                audioRef.current.play().catch(console.error);
            } else {
                audioRef.current.pause();
            }
        }
    }, [isPlaying, streamUrl]);

    // Handle Seeking
    useEffect(() => {
        if (seekTarget !== null && audioRef.current) {
            audioRef.current.currentTime = seekTarget;
            setSeekTarget(null);
        }
    }, [seekTarget, setSeekTarget]);

    return (
        <audio
            ref={audioRef}
            src={streamUrl || undefined}
            onTimeUpdate={(e) => setProgress(e.currentTarget.currentTime)}
            onDurationChange={(e) => setDuration(e.currentTarget.duration)}
            onEnded={playNext}
            onPause={() => setIsPlaying(false)}
            onPlay={() => setIsPlaying(true)}
        />
    );
};
