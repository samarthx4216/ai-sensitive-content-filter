#!/usr/bin/env python3
"""
Quick Start Example - Use this to get started immediately
"""

from content_filter import ContentFilterEngine
from smart_player import SmartVideoPlayer
import os

def example_1_analyze_video():
    """Example 1: Analyze a video file"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Analyze Video")
    print("="*60)
    
    # Path to your video
    video_path = "your_video.mp4"
    
    # Check if file exists
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        print("📝 Please update 'video_path' with your actual video file")
        return None
    
    print(f"📹 Analyzing: {video_path}")
    
    # Create engine
    engine = ContentFilterEngine()
    
    # Analyze video
    print("🔍 Scanning for sensitive content...")
    segments = engine.analyze_video(video_path, sample_rate=30)
    
    # Save timeline
    timeline_path = video_path.replace('.mp4', '_timeline.json')
    engine.save_timeline(segments, timeline_path)
    
    print(f"✅ Analysis complete!")
    print(f"📊 Found {len(segments)} sensitive segments")
    print(f"💾 Timeline saved to: {timeline_path}")
    
    # Display results
    if segments:
        print("\n📋 Detected Content:")
        for i, seg in enumerate(segments, 1):
            print(f"  {i}. {seg.content_type.upper()}")
            print(f"     Time: {seg.start_time:.1f}s - {seg.end_time:.1f}s")
            print(f"     Confidence: {seg.confidence*100:.0f}%")
    
    return timeline_path


def example_2_play_filtered_video():
    """Example 2: Play video with filtering"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Play Filtered Video")
    print("="*60)
    
    video_path = "your_video.mp4"
    timeline_path = "your_video_timeline.json"
    
    # Check files
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return
    
    if not os.path.exists(timeline_path):
        print(f"❌ Timeline not found: {timeline_path}")
        print("💡 Run Example 1 first to create timeline")
        return
    
    print(f"📹 Video: {video_path}")
    print(f"📋 Timeline: {timeline_path}")
    
    # Create player
    player = SmartVideoPlayer(video_path, timeline_path)
    
    # Customize filters (optional)
    player.filter_settings = {
        'nudity': True,     # Skip nudity
        'kissing': True,    # Skip kissing
        'violence': True,   # Skip violence
        'profanity': True   # Mute profanity
    }
    
    print("\n🎮 Controls:")
    print("  SPACE - Pause/Play")
    print("  Q - Quit")
    print("  N - Toggle Nudity filter")
    print("  K - Toggle Kissing filter")
    print("  V - Toggle Violence filter")
    print("  P - Toggle Profanity filter")
    
    # Play
    print("\n▶️ Starting playback...")
    player.play()


def example_3_custom_detection():
    """Example 3: Use custom detection settings"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Custom Detection Settings")
    print("="*60)
    
    # Create engine with custom thresholds
    engine = ContentFilterEngine()
    
    # Adjust sensitivity
    engine.thresholds = {
        'nudity': 0.7,      # More strict (higher threshold = harder to trigger)
        'kissing': 0.3,     # More lenient
        'violence': 0.5,    # Normal
        'profanity': 0.9    # Very strict
    }
    
    print("🎛️ Custom Thresholds:")
    for content_type, threshold in engine.thresholds.items():
        sensitivity = "Strict" if threshold > 0.6 else "Lenient" if threshold < 0.4 else "Normal"
        print(f"  {content_type.capitalize()}: {threshold} ({sensitivity})")
    
    video_path = "your_video.mp4"
    
    if os.path.exists(video_path):
        segments = engine.analyze_video(video_path)
        print(f"\n✅ Found {len(segments)} segments with custom settings")


def example_4_batch_process():
    """Example 4: Process multiple videos"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Batch Processing")
    print("="*60)
    
    # Folder containing videos
    video_folder = "./videos"
    
    if not os.path.exists(video_folder):
        print(f"❌ Folder not found: {video_folder}")
        print("💡 Create a 'videos' folder and add MP4 files")
        return
    
    # Get all MP4 files
    video_files = [f for f in os.listdir(video_folder) if f.endswith('.mp4')]
    
    if not video_files:
        print(f"❌ No MP4 files found in {video_folder}")
        return
    
    print(f"📁 Found {len(video_files)} videos")
    
    engine = ContentFilterEngine()
    
    for i, filename in enumerate(video_files, 1):
        print(f"\n[{i}/{len(video_files)}] Processing {filename}...")
        
        video_path = os.path.join(video_folder, filename)
        timeline_path = video_path.replace('.mp4', '_timeline.json')
        
        # Analyze
        segments = engine.analyze_video(video_path)
        engine.save_timeline(segments, timeline_path)
        
        print(f"  ✅ Found {len(segments)} sensitive segments")
    
    print(f"\n✅ Batch processing complete!")


def main():
    """Main menu"""
    print("\n" + "="*60)
    print("🛡️  CONTENT FILTER - QUICK START EXAMPLES")
    print("="*60)
    
    print("\nAvailable Examples:")
    print("1. Analyze a video file")
    print("2. Play filtered video")
    print("3. Custom detection settings")
    print("4. Batch process multiple videos")
    print("5. Run all examples")
    print("0. Exit")
    
    choice = input("\nSelect example (0-5): ").strip()
    
    if choice == '1':
        example_1_analyze_video()
    elif choice == '2':
        example_2_play_filtered_video()
    elif choice == '3':
        example_3_custom_detection()
    elif choice == '4':
        example_4_batch_process()
    elif choice == '5':
        example_1_analyze_video()
        example_2_play_filtered_video()
        example_3_custom_detection()
        example_4_batch_process()
    elif choice == '0':
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid choice")
    
    print("\n" + "="*60)
    print("✅ Example complete!")
    print("="*60)


if __name__ == "__main__":
    # Quick tips
    print("\n💡 QUICK TIPS:")
    print("  - Update 'video_path' in the examples with your actual video file")
    print("  - Supported formats: MP4, AVI, MKV, MOV")
    print("  - First time? Start with Example 1")
    print("  - Need help? Check README.md or IMPLEMENTATION_GUIDE.md")
    
    main()
