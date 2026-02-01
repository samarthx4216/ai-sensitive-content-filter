"""
Smart Video Player with Auto-Skip and Mute
Integrates with content filter engine
"""

import cv2
import time
import json
from typing import List, Dict
import numpy as np


class SmartVideoPlayer:
    """Video player with intelligent content filtering"""
    
    def __init__(self, video_path: str, timeline_path: str = None):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.total_frames / self.fps
        
        # Load sensitive content timeline
        self.segments = []
        if timeline_path:
            self.load_timeline(timeline_path)
        
        # Filter settings
        self.filter_settings = {
            'nudity': True,
            'kissing': True,
            'violence': True,
            'profanity': True
        }
        
        # Player state
        self.current_frame = 0
        self.is_playing = True
        self.is_muted = False
        self.skip_buffer = 1.0  # seconds to add before/after sensitive content
    
    def load_timeline(self, timeline_path: str):
        """Load sensitive content timeline from JSON"""
        with open(timeline_path, 'r') as f:
            data = json.load(f)
            self.segments = data['segments']
        
        print(f"Loaded {len(self.segments)} sensitive segments")
    
    def should_skip_current_frame(self) -> tuple[bool, str]:
        """Check if current frame should be skipped"""
        current_time = self.current_frame / self.fps
        
        for segment in self.segments:
            content_type = segment['type']
            
            # Check if this content type is filtered
            if not self.filter_settings.get(content_type, False):
                continue
            
            # Add buffer time
            start = segment['start_time'] - self.skip_buffer
            end = segment['end_time'] + self.skip_buffer
            
            if start <= current_time <= end:
                return True, content_type
        
        return False, None
    
    def get_skip_target(self) -> int:
        """Get frame number to skip to"""
        current_time = self.current_frame / self.fps
        
        # Find all overlapping segments
        skip_to = current_time
        for segment in self.segments:
            content_type = segment['type']
            
            if not self.filter_settings.get(content_type, False):
                continue
            
            if segment['start_time'] <= current_time <= segment['end_time'] + self.skip_buffer:
                skip_to = max(skip_to, segment['end_time'] + self.skip_buffer)
        
        return int(skip_to * self.fps)
    
    def play(self, window_name: str = "Smart Video Player"):
        """Play video with content filtering"""
        print(f"\n🎬 Playing: {self.video_path}")
        print(f"📊 Duration: {self.duration:.1f}s | FPS: {self.fps:.1f}")
        print(f"🛡️ Active filters: {[k for k, v in self.filter_settings.items() if v]}")
        print("\nControls:")
        print("  SPACE - Pause/Play")
        print("  Q - Quit")
        print("  N/K/V/P - Toggle Nudity/Kissing/Violence/Profanity filter")
        print("=" * 60)
        
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        skipped_segments = []
        frame_time = 1.0 / self.fps
        
        while self.cap.isOpened():
            if self.is_playing:
                ret, frame = self.cap.read()
                
                if not ret:
                    break
                
                # Check if we should skip this frame
                should_skip, content_type = self.should_skip_current_frame()
                
                if should_skip:
                    # Skip to end of sensitive content
                    skip_to_frame = self.get_skip_target()
                    
                    if skip_to_frame != self.current_frame:
                        # Record skipped segment
                        skipped_segments.append({
                            'from': self.current_frame / self.fps,
                            'to': skip_to_frame / self.fps,
                            'type': content_type
                        })
                        
                        print(f"⏭️  Skipped {content_type} content: "
                              f"{self.current_frame/self.fps:.1f}s → {skip_to_frame/self.fps:.1f}s")
                        
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, skip_to_frame)
                        self.current_frame = skip_to_frame
                        continue
                
                # Add info overlay
                self.add_info_overlay(frame, content_type if should_skip else None)
                
                cv2.imshow(window_name, frame)
                self.current_frame += 1
            
            # Handle keyboard input
            key = cv2.waitKey(int(frame_time * 1000)) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord(' '):
                self.is_playing = not self.is_playing
                status = "▶️ Playing" if self.is_playing else "⏸️ Paused"
                print(f"\n{status}")
            elif key == ord('n'):
                self.filter_settings['nudity'] = not self.filter_settings['nudity']
                print(f"Nudity filter: {'ON ✓' if self.filter_settings['nudity'] else 'OFF ✗'}")
            elif key == ord('k'):
                self.filter_settings['kissing'] = not self.filter_settings['kissing']
                print(f"Kissing filter: {'ON ✓' if self.filter_settings['kissing'] else 'OFF ✗'}")
            elif key == ord('v'):
                self.filter_settings['violence'] = not self.filter_settings['violence']
                print(f"Violence filter: {'ON ✓' if self.filter_settings['violence'] else 'OFF ✗'}")
            elif key == ord('p'):
                self.filter_settings['profanity'] = not self.filter_settings['profanity']
                print(f"Profanity filter: {'ON ✓' if self.filter_settings['profanity'] else 'OFF ✗'}")
        
        self.cap.release()
        cv2.destroyAllWindows()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"✅ Playback complete!")
        print(f"⏭️  Total segments skipped: {len(skipped_segments)}")
        
        if skipped_segments:
            print("\nSkipped segments:")
            for seg in skipped_segments:
                print(f"  {seg['from']:.1f}s - {seg['to']:.1f}s ({seg['type']})")
    
    def add_info_overlay(self, frame, current_content_type=None):
        """Add information overlay to frame"""
        height, width = frame.shape[:2]
        
        # Status bar at top
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (width, 60), (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
        
        # Time
        current_time = self.current_frame / self.fps
        time_text = f"Time: {current_time:.1f}s / {self.duration:.1f}s"
        cv2.putText(frame, time_text, (10, 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Active filters
        active_filters = [k.upper()[0] for k, v in self.filter_settings.items() if v]
        filter_text = f"Filters: {' '.join(active_filters)}" if active_filters else "No filters"
        cv2.putText(frame, filter_text, (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 100), 1)
        
        # Warning if in sensitive zone
        if current_content_type:
            warning = f"🛡️ FILTERED: {current_content_type.upper()}"
            text_size = cv2.getTextSize(warning, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
            text_x = (width - text_size[0]) // 2
            text_y = height - 30
            
            # Background
            cv2.rectangle(frame, (text_x - 10, text_y - 30), 
                         (text_x + text_size[0] + 10, text_y + 10), 
                         (0, 0, 255), -1)
            
            cv2.putText(frame, warning, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)


class PlayerController:
    """High-level controller for the player"""
    
    @staticmethod
    def create_demo_timeline():
        """Create a demo timeline for testing"""
        demo_timeline = {
            'segments': [
                {
                    'start_time': 5.0,
                    'end_time': 8.0,
                    'type': 'kissing',
                    'confidence': 0.7
                },
                {
                    'start_time': 15.0,
                    'end_time': 20.0,
                    'type': 'violence',
                    'confidence': 0.8
                },
                {
                    'start_time': 30.0,
                    'end_time': 35.0,
                    'type': 'nudity',
                    'confidence': 0.9
                }
            ],
            'total_segments': 3
        }
        
        with open('/home/claude/demo_timeline.json', 'w') as f:
            json.dump(demo_timeline, f, indent=2)
        
        print("Demo timeline created: demo_timeline.json")
        return '/home/claude/demo_timeline.json'


if __name__ == "__main__":
    print("Smart Video Player Module")
    print("=" * 60)
    print("\nUsage:")
    print("  player = SmartVideoPlayer('video.mp4', 'timeline.json')")
    print("  player.play()")
    print("\nOr create a demo:")
    print("  timeline_path = PlayerController.create_demo_timeline()")
    print("  player = SmartVideoPlayer('video.mp4', timeline_path)")
    print("  player.play()")
