import os
import re

# Import our existing GCS functionality
import sys
import tempfile
from typing import Dict, List, Optional

import librosa
import numpy as np
from google import genai
from google.cloud import speech
from moviepy import VideoFileClip

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from GoogleAgent.gcs_speech_to_text import GCSSpeechToTextTranscriber


class GoogleAudioProcessor:
    """Production-ready audio processor using Google Cloud Speech-to-Text"""

    def __init__(self, bucket_name="tunir-ai-bucket"):
        self.gcs_transcriber = GCSSpeechToTextTranscriber(bucket_name)
        self.speech_client = speech.SpeechClient()
        self.genai_client = None
        self._setup_genai_client()

    def _setup_genai_client(self):
        """Setup Gemini client for translation tasks"""
        try:
            self.genai_client = genai.Client(
                vertexai=True, project="tough-cascade-402415", location="global"
            )
            print(" Gemini client initialized successfully")
        except Exception as e:
            print(f" Gemini client initialization failed: {e}")
            self.genai_client = None

    def transcribe_with_gcs(
        self, audio_path: str, language: str = "hi"
    ) -> Optional[Dict]:
        """
        Transcribe audio using GCS Speech-to-Text with perfect timestamps
        Returns transcription result with word-level timing
        """
        try:
            print(f" Starting GCS Speech-to-Text for {language} audio...")

            # Setup GCS bucket
            if not self.gcs_transcriber.setup_bucket():
                print(" Failed to setup GCS bucket")
                return None

            # Upload to GCS
            gcs_uri = self.gcs_transcriber.upload_audio_to_gcs(audio_path)
            if not gcs_uri:
                print(" Failed to upload to GCS")
                return None

            # Configure language-specific transcription
            language_codes = {"hi": "hi-IN", "ta": "ta-IN", "te": "te-IN"}

            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.MP3,
                language_code=language_codes.get(language, "hi-IN"),
                alternative_language_codes=["en-IN"],
                enable_word_time_offsets=True,
                enable_automatic_punctuation=True,
                audio_channel_count=1,
                sample_rate_hertz=16000,
                model="latest_long",
                max_alternatives=1,
                profanity_filter=False,
                use_enhanced=True,
            )

            # Transcribe from GCS
            results = self.gcs_transcriber.transcribe_from_gcs(gcs_uri, config)

            # Cleanup GCS file
            self.gcs_transcriber.cleanup_gcs_file(audio_path)

            if results and results.get("words"):
                print(
                    f" {language.upper()} transcription completed: {len(results['words'])} words"
                )
                return results
            else:
                print(" No transcription results found")
                return None

        except Exception as e:
            print(f" Error in GCS transcription: {e}")
            return None

    def translate_with_gemini(
        self, text: str, source_lang: str = "hi"
    ) -> Optional[str]:
        """Translate text using Gemini with cultural awareness"""
        if not self.genai_client:
            print(" Gemini client not available")
            return None

        try:
            language_prompts = {
                "hi": "Translate the following Hindi sales presentation text to natural, professional English.\nThe text includes timestamps in the format [MM:SS].\nPreserve the timestamps in the translated text, keeping them in the same format and position.\nReturn ONLY the translated text with the timestamps, without any introduction, commentary, or formatting.\nMaintain the sales context and professional tone.",
                "ta": "Translate the following Tamil sales presentation text to natural, professional English.\nThe text includes timestamps in the format [MM:SS].\nPreserve the timestamps in the translated text, keeping them in the same format and position.\nReturn ONLY the translated text with the timestamps, without any introduction, commentary, or formatting.\nMaintain the sales context and professional tone.",
                "te": "Translate the following Telugu sales presentation text to natural, professional English.\nThe text includes timestamps in the format [MM:SS].\nPreserve the timestamps in the translated text, keeping them in the same format and position.\nReturn ONLY the translated text with the timestamps, without any introduction, commentary, or formatting.\nMaintain the sales context and professional tone.",
            }

            prompt = f"{language_prompts.get(source_lang, language_prompts['hi'])}\n\nText to translate:\n{text}"

            response = self.genai_client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )

            translation = response.text.strip()
            # Remove any remaining introductory text
            if (
                translation.startswith("Here's")
                or translation.startswith("Okay,")
                or translation.startswith("**")
            ):
                # Try to extract just the translated content
                lines = translation.split("\n")
                cleaned_lines = []
                skip_intro = True
                for line in lines:
                    if skip_intro and (
                        line.strip().startswith("**")
                        or line.strip().startswith("Here")
                        or line.strip().startswith("Okay")
                    ):
                        continue
                    elif skip_intro and not line.strip():
                        continue
                    else:
                        skip_intro = False
                        cleaned_lines.append(line)
                translation = "\n".join(cleaned_lines).strip()

            print(f" {source_lang.upper()} → EN translation completed")
            return translation

        except Exception as e:
            print(f" Translation failed: {e}")
            return None

    def create_analysis_segments(
        self, transcription_result: Dict, max_pause: float = 0.7, min_words: int = 3
    ) -> List[Dict]:
        """Create segments from word-level timestamps for video analysis"""
        words = transcription_result.get("words", [])
        if not words:
            return []

        segments = []
        current_segment_words = []

        for i, word_info in enumerate(words):
            current_segment_words.append(word_info)

            # Check for natural breaks (pauses or end)
            is_long_pause = False
            if i + 1 < len(words):
                pause_duration = words[i + 1]["start_time"] - word_info["end_time"]
                if (
                    pause_duration > max_pause
                    and len(current_segment_words) >= min_words
                ):
                    is_long_pause = True

            if is_long_pause or i == len(words) - 1:
                if current_segment_words:
                    segments.append(
                        {
                            "text": " ".join(w["word"] for w in current_segment_words),
                            "start_time": current_segment_words[0]["start_time"],
                            "end_time": current_segment_words[-1]["end_time"],
                            "words": current_segment_words.copy(),
                        }
                    )
                    current_segment_words = []

        print(f" Created {len(segments)} analysis segments from {len(words)} words")
        return segments

    def extract_prosodic_features(self, audio_path: str, transcript: str) -> Dict:
        """Extract detailed prosodic features using librosa"""
        try:
            y, sr = librosa.load(audio_path, sr=16000)
            duration = librosa.get_duration(y=y, sr=sr)

            # Basic features
            rms = librosa.feature.rms(y=y)[0]
            f0 = librosa.yin(y, fmin=50, fmax=400, sr=sr)
            f0_valid = f0[~np.isnan(f0)]

            # Speech detection
            intervals = librosa.effects.split(y, top_db=30)
            speech_time = (
                sum((e - s) / sr for s, e in intervals) if len(intervals) else 0.0
            )
            pause_time = max(0.0, duration - speech_time)

            # Word and filler analysis
            words = re.findall(r"\w+", transcript or "")
            word_count = len(words)

            # Calculate rates
            speech_rate = word_count / duration if duration > 0 else 0
            articulation_rate = word_count / speech_time if speech_time > 0 else 0

            return {
                "duration_s": duration,
                "speech_time_s": speech_time,
                "pause_time_s": pause_time,
                "word_count": word_count,
                "speech_rate_wps": speech_rate,
                "articulation_rate_wps": articulation_rate,
                "rms_mean": float(np.mean(rms)) if rms.size > 0 else 0.0,
                "rms_std": float(np.std(rms)) if rms.size > 0 else 0.0,
                "pitch_mean_hz": float(np.mean(f0_valid)) if f0_valid.size else 0.0,
                "pitch_median_hz": float(np.median(f0_valid)) if f0_valid.size else 0.0,
                "pitch_std_hz": float(np.std(f0_valid)) if f0_valid.size else 0.0,
                "pause_count": max(0, len(intervals) - 1),
            }

        except Exception as e:
            print(f" Prosodic analysis failed: {e}")
            return self._get_default_prosodic_features()

    def _get_default_prosodic_features(self) -> Dict:
        """Return default prosodic features when analysis fails"""
        return {
            "duration_s": 0.0,
            "speech_time_s": 0.0,
            "pause_time_s": 0.0,
            "word_count": 0,
            "speech_rate_wps": 0.0,
            "articulation_rate_wps": 0.0,
            "rms_mean": 0.0,
            "rms_std": 0.0,
            "pitch_mean_hz": 0.0,
            "pitch_median_hz": 0.0,
            "pitch_std_hz": 0.0,
            "pause_count": 0,
        }

    def extract_audio_from_video(self, video_path: str) -> Optional[str]:
        """Extract audio from video file and return path to temporary audio file"""
        try:
            print(f" Extracting audio from video: {os.path.basename(video_path)}")

            # Create temporary audio file
            temp_audio = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            temp_audio_path = temp_audio.name
            temp_audio.close()

            # Extract audio using moviepy
            video_clip = VideoFileClip(video_path)
            audio_clip = video_clip.audio

            if audio_clip is None:
                print(" No audio track found in video file")
                return None

            # Save audio as MP3
            audio_clip.write_audiofile(temp_audio_path, codec="mp3", bitrate="128k")

            # Clean up
            audio_clip.close()
            video_clip.close()

            print(f" Audio extracted to: {os.path.basename(temp_audio_path)}")
            return temp_audio_path

        except Exception as e:
            print(f" Failed to extract audio from video: {e}")
            return None

    def analyze_segment_vocals(
        self, audio_path: str, start_time: float, end_time: float
    ) -> Dict:
        """Analyze vocal characteristics of a specific segment"""
        try:
            y, sr = librosa.load(audio_path, sr=16000)
            start_sample = int(start_time * sr)
            end_sample = int(end_time * sr)
            y_segment = y[start_sample:end_sample]

            if len(y_segment) == 0:
                return {"pitch": "normal", "energy": "normal"}

            # Pitch analysis
            pitches, _ = librosa.piptrack(y=y_segment, sr=sr)
            valid_pitches = pitches[pitches > 0]
            avg_pitch = np.mean(valid_pitches) if len(valid_pitches) > 0 else 0

            # Energy analysis
            rms_energy = np.mean(librosa.feature.rms(y=y_segment))

            # Categorize pitch and energy
            pitch_desc = (
                "high"
                if avg_pitch > 220
                else "low"
                if avg_pitch < 140 and avg_pitch > 0
                else "normal"
            )
            energy_desc = (
                "high"
                if rms_energy > 0.06
                else "low"
                if rms_energy < 0.02
                else "normal"
            )

            return {"pitch": pitch_desc, "energy": energy_desc}

        except Exception as e:
            print(f" Segment vocal analysis failed: {e}")
            return {"pitch": "normal", "energy": "normal"}

    def _format_readable_transcript(self, transcription_result: Dict) -> str:
        """Format readable transcript with timestamps every ~15 seconds"""
        words = transcription_result.get("words", [])
        if not words:
            return transcription_result.get("transcript", "")

        lines = []
        current_time = 0
        text_buffer = []

        for word in words:
            if word["start_time"] - current_time >= 15.0:  # New timestamp every ~15 seconds
                if text_buffer:
                    lines.append(" ".join(text_buffer))
                    text_buffer = []

                minutes = int(word["start_time"] // 60)
                seconds = int(word["start_time"] % 60)
                timestamp = f"[{minutes:02d}:{seconds:02d}]"
                lines.append(timestamp)
                current_time = word["start_time"]

            text_buffer.append(word["word"])

        # Add remaining text
        if text_buffer:
            lines.append(" ".join(text_buffer))

        return "\n".join(lines)

    def process_audio_pipeline(
        self, media_path: str, language: str = "hi"
    ) -> Optional[Dict]:
        """
        Complete audio processing pipeline:
        1. Extract audio if video file
        2. Transcribe with GCS Speech-to-Text
        3. Translate to English with Gemini
        4. Create analysis segments
        5. Extract prosodic features
        6. Clean up temporary files
        """
        print(f" Starting complete audio pipeline for {language.upper()}")

        # Handle video files by extracting audio first
        actual_audio_path = media_path
        temp_audio_file = None
        is_video = media_path.lower().endswith((".mp4", ".mov", ".avi", ".mkv"))

        if is_video:
            temp_audio_file = self.extract_audio_from_video(media_path)
            if not temp_audio_file:
                print(" Failed to extract audio from video")
                return None
            actual_audio_path = temp_audio_file

        try:
            # Step 1: Transcribe with perfect timestamps
            transcription_result = self.transcribe_with_gcs(actual_audio_path, language)
            if not transcription_result:
                return None

            # Step 2: Translate to English
            readable_transcript = self._format_readable_transcript(transcription_result)
            english_translation = self.translate_with_gemini(readable_transcript, language)

            # Step 3: Create analysis segments
            segments = self.create_analysis_segments(transcription_result)

            # Step 4: Extract prosodic features
            prosodic_features = self.extract_prosodic_features(
                actual_audio_path, transcription_result.get("transcript", "")
            )

            result = {
                "transcription_result": transcription_result,
                "original_text": transcription_result.get("transcript", ""),
                "english_translation": english_translation,
                "readable_transcript": readable_transcript,
                "segments": segments,
                "prosodic_features": prosodic_features,
                "language": language,
            }

            print(f" Audio pipeline completed for {language.upper()}")
            return result

        finally:
            # Clean up temporary audio file if it was created
            if temp_audio_file and os.path.exists(temp_audio_file):
                try:
                    os.unlink(temp_audio_file)
                    print(" Cleaned up temporary audio file")
                except Exception as e:
                    print(f" Failed to clean up temporary file: {e}")
