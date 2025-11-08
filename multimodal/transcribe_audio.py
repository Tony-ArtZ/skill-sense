#!/usr/bin/env python3
"""
Standalone Audio Transcription Script
Transcribes Hindi audio from video files using Google Cloud Speech-to-Text

Usage:
    python transcribe_audio.py --input "path/to/video.mp4" [--output "output.txt"] [--language hi]
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gcs_speech_to_text import GCSSpeechToTextTranscriber
from audio_processor import GoogleAudioProcessor


def extract_audio_from_video(video_path: str) -> str:
    """Extract audio from video file and return path to temporary audio file"""
    try:
        from moviepy import VideoFileClip

        print(f"Extracting audio from video: {os.path.basename(video_path)}")

        # Create temporary audio file
        temp_audio = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        temp_audio_path = temp_audio.name
        temp_audio.close()

        # Extract audio using moviepy
        video_clip = VideoFileClip(video_path)
        audio_clip = video_clip.audio

        if audio_clip is None:
            print("Error: No audio track found in video file")
            return None

        # Save audio as MP3
        audio_clip.write_audiofile(temp_audio_path, codec="mp3", bitrate="128k")

        # Clean up
        audio_clip.close()
        video_clip.close()

        print(f"Audio extracted to: {os.path.basename(temp_audio_path)}")
        return temp_audio_path

    except ImportError:
        print("Error: moviepy not installed. Please install it with: pip install moviepy")
        return None
    except Exception as e:
        print(f"Failed to extract audio from video: {e}")
        return None


def transcribe_video_audio(video_path: str, output_file: str, language: str = "te"):
    """
    Complete transcription pipeline for video file
    """
    print("=" * 60)
    print("HINDI AUDIO TRANSCRIPTION FROM VIDEO")
    print("=" * 60)
    print(f"Input video: {video_path}")
    print(f"Output file: {output_file}")
    print(f"Language: {language.upper()}")
    print("=" * 60)

    # Check if input file exists
    if not os.path.exists(video_path):
        print(f"Error: Input file not found: {video_path}")
        return False

    # Initialize transcriber
    transcriber = GCSSpeechToTextTranscriber()

    # Setup GCS bucket
    if not transcriber.setup_bucket():
        print("Error: Failed to setup Google Cloud Storage bucket")
        return False

    temp_audio_file = None
    gcs_uri = None

    try:
        # Step 1: Extract audio from video
        temp_audio_file = extract_audio_from_video(video_path)
        if not temp_audio_file:
            return False

        # Step 2: Upload to GCS
        print("\nUploading audio to Google Cloud Storage...")
        gcs_uri = transcriber.upload_audio_to_gcs(temp_audio_file)
        if not gcs_uri:
            print("Error: Failed to upload to Google Cloud Storage")
            return False

        # Step 3: Configure language-specific transcription
        from google.cloud import speech

        language_codes = {
            "hi": "hi-IN",
            "ta": "ta-IN",
            "te": "te-IN"
        }

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.MP3,
            language_code=language_codes.get(language, "te-IN"),
            enable_word_time_offsets=True,
            enable_automatic_punctuation=True,
            audio_channel_count=1,
            sample_rate_hertz=16000,
            model="latest_long",
            max_alternatives=1,
            profanity_filter=False,
            use_enhanced=True,
        )

        # Step 4: Transcribe from GCS
        print(f"\nTranscribing {language.upper()} audio...")
        results = transcriber.transcribe_from_gcs(gcs_uri, config)

        if not results or not results.get("words"):
            print("Error: No transcription results found")
            return False

        # Step 5: Format and save transcription
        print(f"\nTranscription completed successfully!")
        print(f"Words transcribed: {results['word_count']}")
        print(f"Duration: {results['total_duration']:.2f} seconds")
        print(f"Confidence: {results['confidence']:.2f}")

        # Create readable transcript with timestamps
        readable_transcript = transcriber.format_timestamped_transcript(results, "readable")

        # Save to output file
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(readable_transcript)

        print(f"\nTranscription saved to: {output_file}")

        # Show preview
        print("\nPreview of transcription:")
        print("-" * 40)
        lines = readable_transcript.split("\n")
        for line in lines[:10]:
            print(line)
        if len(lines) > 10:
            print("... (truncated)")
        print("-" * 40)

        return True

    except Exception as e:
        print(f"Error during transcription: {e}")
        return False

    finally:
        # Cleanup
        if temp_audio_file and os.path.exists(temp_audio_file):
            try:
                os.unlink(temp_audio_file)
                print("\nCleaned up temporary audio file")
            except Exception as e:
                print(f"Warning: Failed to clean up temp file: {e}")

        if gcs_uri:
            try:
                transcriber.cleanup_gcs_file(temp_audio_file)
                print("Cleaned up Google Cloud Storage file")
            except Exception as e:
                print(f"Warning: Failed to clean up GCS file: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe Hindi audio from video files using Google Cloud Speech-to-Text",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python transcribe_audio.py --input "video.mp4"
  python transcribe_audio.py --input "video.mp4" --output "transcript.txt"
  python transcribe_audio.py --input "video.mp4" --language hi --output "hindi_transcript.txt"
        """
    )

    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to the input video file"
    )

    parser.add_argument(
        "--output", "-o",
        default="transcription.txt",
        help="Output transcription file path (default: transcription.txt)"
    )

    parser.add_argument(
        "--language", "-l",
        choices=["hi", "ta", "te"],
        default="hi",
        help="Language code (hi=Hindi, ta=Tamil, te=Telugu) (default: hi)"
    )

    args = parser.parse_args()

    # Convert to absolute paths
    input_path = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)

    # Run transcription
    success = transcribe_video_audio(input_path, output_path, args.language)

    if success:
        print(f"\n✅ Transcription completed successfully!")
        print(f"📄 Output saved to: {output_path}")
    else:
        print(f"\n❌ Transcription failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()