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
                const response = await fetch(`${API_BASE_URL}/stream/${currentTrack.videoId}`);
                if (!response.ok) throw new Error("Failed to fetch stream");
                const data = await response.json();
                console.log("Fetched stream URL:", data.stream_url);
                if (active) {
                    setStreamUrl(data.stream_url);
                    setIsPlaying(true);
                }
            } catch (error) {
                console.error("Stream fetch error:", error);
                setIsPlaying(false);
            }
        };

        fetchStream();

        return () => { active = false; };
    }, [currentTrack?.videoId, setStreamUrl, setIsPlaying]);

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
