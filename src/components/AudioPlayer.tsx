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
                console.log(`🎵 Fetching stream for ${currentTrack.video_id} from local backend...`);
                const response = await fetch(`${API_BASE_URL}/stream/${currentTrack.video_id}`);
                
                if (!response.ok) {
                    throw new Error(`Failed to fetch stream: ${response.statusText}`);
                }
                
                const data = await response.json();
                const streamUrl = data.stream_url;

                if (active) {
                    setStreamUrl(streamUrl);
                    // No need to set isPlaying(true) here if it's already handled by the user/store
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
                const playPromise = audioRef.current.play();
                if (playPromise !== undefined) {
                    playPromise.catch(error => {
                        if (error.name !== 'AbortError') {
                            console.error("Playback error:", error);
                        }
                    });
                }
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
            onPause={() => {
                // Only sync pause to store if we actually have a source.
                // This prevents the "pause" event triggered by changing the 'src' 
                // from resetting our global 'isPlaying' state.
                if (streamUrl) setIsPlaying(false);
            }}
            onPlay={() => setIsPlaying(true)}
        />
    );
};
