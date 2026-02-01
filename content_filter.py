"""
AI-Based Sensitive Content Filter
Main content analysis engine
"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
import json

@dataclass
class SensitiveSegment:
    """Represents a sensitive content segment"""
    start_time: float
    end_time: float
    content_type: str  # 'nudity', 'kissing', 'violence', 'profanity'
    confidence: float
    
    def to_dict(self):
        return {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'type': self.content_type,
            'confidence': self.confidence
        }


class VideoSceneDetector:
    """Detects sensitive visual content in video"""
    
    def __init__(self):
        self.skin_lower = np.array([0, 20, 70], dtype=np.uint8)
        self.skin_upper = np.array([20, 255, 255], dtype=np.uint8)
    
    def detect_skin_ratio(self, frame):
        """Calculate percentage of skin-colored pixels"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        skin_mask = cv2.inRange(hsv, self.skin_lower, self.skin_upper)
        skin_ratio = np.count_nonzero(skin_mask) / (frame.shape[0] * frame.shape[1])
        return skin_ratio
    
    def detect_scene_brightness(self, frame):
        """Detect dim lighting (bedroom scenes often darker)"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return np.mean(gray) / 255.0
    
    def detect_motion(self, prev_frame, curr_frame):
        """Detect rapid motion (violence indicator)"""
        if prev_frame is None:
            return 0.0
        
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        
        diff = cv2.absdiff(prev_gray, curr_gray)
        motion_score = np.mean(diff) / 255.0
        return motion_score
    
    def analyze_frame(self, frame, prev_frame=None):
        """
        Analyze single frame for sensitive content
        Returns: dict with scores
        """
        skin_ratio = self.detect_skin_ratio(frame)
        brightness = self.detect_scene_brightness(frame)
        motion = self.detect_motion(prev_frame, frame) if prev_frame is not None else 0.0
        
        # Simple heuristic scoring
        scores = {
            'nudity_score': 0.0,
            'kissing_score': 0.0,
            'violence_score': 0.0
        }
        
        # High skin exposure
        if skin_ratio > 0.3:
            scores['nudity_score'] = min(skin_ratio * 2, 1.0)
        
        # Moderate skin + close-up (darker background)
        if 0.15 < skin_ratio < 0.35 and brightness < 0.4:
            scores['kissing_score'] = 0.6
        
        # High motion
        if motion > 0.15:
            scores['violence_score'] = min(motion * 4, 1.0)
        
        return scores


class AudioProfanityDetector:
    """Detects profanity in audio"""
    
    def __init__(self):
        # Common profanity list (you can expand this)
        self.bad_words = {
            'fuck', 'fucking', 'shit', 'bitch', 'bastard', 'damn', 
            'ass', 'asshole', 'dick', 'cock', 'pussy', 'cunt',
            'motherfucker', 'hell', 'piss', 'slut', 'whore'
        }
        
        # Hindi/Hinglish profanity
        self.bad_words.update({
            'chutiya', 'madarchod', 'behenchod', 'gandu', 'saala',
            'kamina', 'harami', 'kutte', 'kutta'
        })
    
    def detect_profanity(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Detect bad words in text
        Returns: list of (word, start_pos, end_pos)
        """
        text_lower = text.lower()
        words = text_lower.split()
        
        detections = []
        current_pos = 0
        
        for word in words:
            # Remove punctuation
            clean_word = ''.join(c for c in word if c.isalnum())
            
            if clean_word in self.bad_words:
                start = text_lower.find(word, current_pos)
                end = start + len(word)
                detections.append((clean_word, start, end))
            
            current_pos += len(word) + 1
        
        return detections


class ContentFilterEngine:
    """Main engine that coordinates video and audio analysis"""
    
    def __init__(self):
        self.video_detector = VideoSceneDetector()
        self.audio_detector = AudioProfanityDetector()
        self.thresholds = {
            'nudity': 0.6,
            'kissing': 0.5,
            'violence': 0.5,
            'profanity': 0.8
        }
    
    def analyze_video(self, video_path: str, sample_rate: int = 30) -> List[SensitiveSegment]:
        """
        Analyze video file for sensitive content
        sample_rate: analyze every Nth frame (30 = analyze 1 frame per second for 30fps video)
        """
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        segments = []
        frame_count = 0
        prev_frame = None
        
        current_segment = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Sample frames to reduce processing
            if frame_count % sample_rate != 0:
                frame_count += 1
                continue
            
            timestamp = frame_count / fps
            
            # Analyze frame
            scores = self.video_detector.analyze_frame(frame, prev_frame)
            
            # Check for sensitive content
            for content_type, score in scores.items():
                threshold_key = content_type.replace('_score', '')
                
                if score > self.thresholds.get(threshold_key, 0.5):
                    # Start new segment or extend current
                    if current_segment is None or \
                       current_segment.content_type != threshold_key or \
                       timestamp - current_segment.end_time > 2.0:
                        
                        # Save previous segment
                        if current_segment:
                            segments.append(current_segment)
                        
                        # Start new segment
                        current_segment = SensitiveSegment(
                            start_time=timestamp,
                            end_time=timestamp + 1.0,
                            content_type=threshold_key,
                            confidence=score
                        )
                    else:
                        # Extend current segment
                        current_segment.end_time = timestamp + 1.0
                        current_segment.confidence = max(current_segment.confidence, score)
            
            prev_frame = frame.copy()
            frame_count += 1
        
        # Add final segment
        if current_segment:
            segments.append(current_segment)
        
        cap.release()
        return segments
    
    def save_timeline(self, segments: List[SensitiveSegment], output_path: str):
        """Save detected segments to JSON file"""
        timeline = {
            'segments': [seg.to_dict() for seg in segments],
            'total_segments': len(segments)
        }
        
        with open(output_path, 'w') as f:
            json.dump(timeline, f, indent=2)
        
        print(f"Timeline saved to {output_path}")
        return timeline


# Example usage
if __name__ == "__main__":
    engine = ContentFilterEngine()
    
    # Test with a video file
    print("Content Filter Engine Ready!")
    print("Usage: engine.analyze_video('video.mp4')")
    print("\nSupported content types:")
    print("  - Nudity (high skin exposure)")
    print("  - Kissing (moderate skin, close-up)")
    print("  - Violence (rapid motion)")
    print("  - Profanity (audio transcription required)")
