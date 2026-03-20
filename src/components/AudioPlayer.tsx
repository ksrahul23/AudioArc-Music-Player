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
                console.log("🕊️ Attempting client-side extraction (Spotube Method) for ID:", currentTrack.video_id);
                const pipedInstances = [
                    "https://pipedapi.kavin.rocks",
                    "https://api.piped.victr.me",
                    "https://pipedapi.col7a.me",
                    "https://pipedapi.privacydev.net",
                    "https://piped-api.garudalinux.org"
                ];
                
                for (const instance of pipedInstances) {
                    try {
                        console.log(`🔗 Trying CORS-bypassed instance: ${instance}`);
                        // Wrap with AllOrigins CORS Proxy
                        const proxyUrl = `https://api.allorigins.win/get?url=${encodeURIComponent(`${instance}/streams/${currentTrack.video_id}`)}`;
                        const response = await fetch(proxyUrl);
                        
                        if (response.ok) {
                            const data = await response.json() as any;
                            // AllOrigins returns the actual response in the 'contents' field as a string
                            const pipedData = JSON.parse(data.contents);
                            const audioStreams = pipedData.audioStreams || [];
                            
                            if (audioStreams.length > 0) {
                                audioStreams.sort((a: any, b: any) => (b.bitrate || 0) - (a.bitrate || 0));
                                streamUrl = audioStreams[0].url;
                                console.log(`✅ Client-side extraction SUCCESS via ${instance} (CORS-bypassed)`);
                                break;
                            } else {
                                console.warn(`⚠️ Instance ${instance} returned no audio streams.`);
                            }
                        } else {
                            console.warn(`❌ Proxy returned status ${response.status} for ${instance}`);
                        }
                    } catch (e) {
                        console.warn(`❌ Failed to fetch from ${instance} through proxy:`, e);
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
