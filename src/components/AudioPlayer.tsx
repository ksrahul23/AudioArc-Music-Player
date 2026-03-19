import React, { useRef, useEffect } from 'react';
import { usePlayerStore } from '../store/usePlayerStore';
import { API_BASE_URL } from '../config';

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
                
                // 1. SPOTUBE METHOD: Try client-side extraction via Piped API first
                // Uses user's IP to bypass Render's cloud blocks
                console.log("🕊️ Attempting client-side extraction (Spotube Method)...");
                const pipedInstances = [
                    "https://pipedapi.kavin.rocks",
                    "https://api.piped.victr.me",
                    "https://pipedapi.col7a.me"
                ];
                
                for (const instance of pipedInstances) {
                    try {
                        const pipedRes = await fetch(`${instance}/streams/${currentTrack.video_id}`);
                        if (pipedRes.ok) {
                            const pipedData = await pipedRes.json();
                            const audioStreams = pipedData.audioStreams || [];
                            if (audioStreams.length > 0) {
                                // Sort by bitrate and pick the best one
                                audioStreams.sort((a: any, b: any) => (b.bitrate || 0) - (a.bitrate || 0));
                                streamUrl = audioStreams[0].url;
                                console.log(`✅ Client-side extraction successful via ${instance}`);
                                break;
                            }
                        }
                    } catch (e) {
                        continue;
                    }
                }

                // 2. BACKEND FALLBACK: If client-side failed, use the Render bridge
                if (!streamUrl) {
                    console.log("📡 Falling back to backend bridge...");
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
