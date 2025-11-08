import json
import os
import time
from typing import Dict

from google.cloud import speech, storage


class GCSSpeechToTextTranscriber:
    def __init__(self, bucket_name="tunir-ai-bucket"):
        self.speech_client = speech.SpeechClient()
        self.storage_client = storage.Client()
        self.bucket_name = bucket_name
        self.bucket = None

    def setup_bucket(self):
        """Get the existing bucket"""
        try:
            self.bucket = self.storage_client.bucket(self.bucket_name)
            if self.bucket.exists():
                print(f" Using existing bucket: {self.bucket_name}")
                return True
            else:
                print(f" Bucket {self.bucket_name} does not exist")
                return False
        except Exception as e:
            print(f" Error accessing bucket: {e}")
            return False

    def upload_audio_to_gcs(self, audio_path: str) -> str:
        """Upload audio file to Google Cloud Storage"""
        try:
            blob_name = os.path.basename(audio_path)
            blob = self.bucket.blob(blob_name)

            print(f"  Uploading {blob_name} to GCS...")
            blob.upload_from_filename(audio_path)

            # Return GCS URI
            gcs_uri = f"gs://{self.bucket_name}/{blob_name}"
            print(f" Uploaded to: {gcs_uri}")
            return gcs_uri

        except Exception as e:
            print(f" Error uploading to GCS: {e}")
            return None

    def transcribe_from_gcs(self, gcs_uri: str, config: dict = None) -> Dict:
        """
        Transcribe audio from GCS URI using Long Running Recognition
        This handles files of any size
        """
        try:
            print(" Starting Speech-to-Text from GCS...")
            print(" Using GCS URI - no file size limits!")

            start_time = time.time()

            # Configure audio to use GCS URI
            audio = speech.RecognitionAudio(uri=gcs_uri)

            # Configure Speech-to-Text
            if config is None:
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.MP3,
                    language_code="hi-IN",
                    alternative_language_codes=["en-IN"],
                    enable_word_time_offsets=True,  # CRITICAL for real timestamps
                    enable_automatic_punctuation=True,
                    audio_channel_count=1,
                    sample_rate_hertz=16000,
                    model="latest_long",
                    max_alternatives=1,
                    profanity_filter=False,
                    use_enhanced=True,
                )

            print("Starting Long Running Recognition...")
            print("Processing audio waveform for genuine timestamps...")

            # Use Long Running Recognition (no size limits with GCS)
            operation = self.speech_client.long_running_recognize(
                config=config, audio=audio
            )

            print("Processing asynchronously...")

            # Wait for completion (this can take several minutes)
            response = operation.result(timeout=600)  # 10 minute timeout

            processing_time = time.time() - start_time
            print(f" Speech-to-Text completed in {processing_time:.1f} seconds")

            # Process results
            results = {
                "transcript": "",
                "words": [],
                "segments": [],
                "confidence": 0.0,
                "total_duration": 0.0,
                "word_count": 0,
            }

            if not response.results:
                print(" No speech recognition results found")
                return results

            print(f" Found {len(response.results)} result segments")

            # Extract transcription data
            full_transcript = []
            all_words = []
            total_confidence = 0
            segment_count = 0

            for result in response.results:
                if not result.alternatives:
                    continue

                alternative = result.alternatives[0]
                segment_confidence = alternative.confidence
                total_confidence += segment_confidence
                segment_count += 1

                # Add segment transcript
                segment_text = alternative.transcript
                full_transcript.append(segment_text)

                # Extract word-level timestamps
                segment_words = []
                for word_info in alternative.words:
                    word_data = {
                        "word": word_info.word,
                        "start_time": word_info.start_time.total_seconds(),
                        "end_time": word_info.end_time.total_seconds(),
                        "confidence": segment_confidence,
                    }
                    segment_words.append(word_data)
                    all_words.append(word_data)

                # Create segment info
                if segment_words:
                    segment_info = {
                        "text": segment_text,
                        "start_time": segment_words[0]["start_time"],
                        "end_time": segment_words[-1]["end_time"],
                        "words": segment_words,
                        "confidence": segment_confidence,
                    }
                    results["segments"].append(segment_info)

            # Compile final results
            results["transcript"] = " ".join(full_transcript)
            results["words"] = all_words
            results["confidence"] = (
                total_confidence / segment_count if segment_count > 0 else 0.0
            )
            results["word_count"] = len(all_words)

            # Calculate total duration
            if all_words:
                results["total_duration"] = all_words[-1]["end_time"]
                total_minutes = int(results["total_duration"] // 60)
                total_seconds = int(results["total_duration"] % 60)
                print(
                    f" Total audio duration: {total_minutes}:{total_seconds:02d} ({results['total_duration']:.2f} seconds)"
                )

            print(" Results Summary:")
            print(f"   Word count: {results['word_count']}")
            print(f"   Average confidence: {results['confidence']:.2f}")
            print(f"   Number of segments: {len(results['segments'])}")

            return results

        except Exception as e:
            print(f" Error during GCS Speech-to-Text: {e}")
            return {
                "transcript": "",
                "words": [],
                "segments": [],
                "confidence": 0.0,
                "total_duration": 0.0,
                "word_count": 0,
            }

    def cleanup_gcs_file(self, audio_path: str):
        """Remove uploaded file from GCS"""
        try:
            blob_name = os.path.basename(audio_path)
            blob = self.bucket.blob(blob_name)
            if blob.exists():
                blob.delete()
                print(f" Cleaned up GCS file: {blob_name}")
        except Exception as e:
            print(f"  Error cleaning up GCS file: {e}")

    def format_timestamped_transcript(
        self, results: Dict, format_type: str = "readable"
    ) -> str:
        """Format transcript with timestamps"""
        if not results["words"]:
            return "No transcription results available"

        if format_type == "words":
            # Word-level timestamps
            lines = []
            for word in results["words"]:
                start_time = word["start_time"]
                minutes = int(start_time // 60)
                seconds = int(start_time % 60)
                milliseconds = int((start_time % 1) * 100)
                timestamp = f"[{minutes:02d}:{seconds:02d}.{milliseconds:02d}]"
                lines.append(f"{timestamp} {word['word']}")
            return "\n".join(lines)

        elif format_type == "segments":
            # Segment-level timestamps
            lines = []
            for segment in results["segments"]:
                start_time = segment["start_time"]
                minutes = int(start_time // 60)
                seconds = int(start_time % 60)
                timestamp = f"[{minutes:02d}:{seconds:02d}]"
                lines.append(f"{timestamp} {segment['text']}")
            return "\n".join(lines)

        else:  # readable format
            # Natural language format with timestamps every ~15 seconds
            lines = []
            current_time = 0
            text_buffer = []

            for word in results["words"]:
                if (
                    word["start_time"] - current_time >= 15.0
                ):  # New timestamp every ~15 seconds
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

    def analyze_timestamp_accuracy(self, results: Dict):
        """Analyze timestamp accuracy"""
        if not results["words"]:
            print(" No word data to analyze")
            return

        words = results["words"]
        total_duration = results["total_duration"]

        print("\n TIMESTAMP ACCURACY ANALYSIS:")
        print("=" * 50)

        # Duration analysis
        expected_duration = 361  # 6:01 in seconds
        duration_accuracy = abs(total_duration - expected_duration)
        print(f"Expected duration: {expected_duration} seconds (6:01)")
        print(
            f"Actual duration: {total_duration:.2f} seconds ({int(total_duration // 60)}:{int(total_duration % 60):02d})"
        )
        print(f"Duration difference: {duration_accuracy:.2f} seconds")

        if duration_accuracy <= 2.0:
            print(" PERFECT timestamp accuracy!")
        elif duration_accuracy <= 5.0:
            print(" EXCELLENT timestamp accuracy")
        elif duration_accuracy <= 10.0:
            print(" GOOD timestamp accuracy")
        else:
            print(" POOR timestamp accuracy")

        # Word distribution analysis
        print("\n Word Distribution:")
        print(f"   Total words: {len(words)}")
        print(f"   Words per minute: {len(words) / (total_duration / 60):.1f}")
        print(f"   Average word duration: {total_duration / len(words):.2f} seconds")

        # Show actual timing samples
        if len(words) >= 10:
            print("\nActual Timing Samples:")
            # Show first few words
            for i in range(min(3, len(words))):
                word = words[i]
                print(
                    f"   [{int(word['start_time']) // 60:02d}:{int(word['start_time']) % 60:02d}.{int((word['start_time'] % 1) * 100):02d}] {word['word']}"
                )

            # Show last few words
            print("   ...")
            for i in range(max(0, len(words) - 3), len(words)):
                word = words[i]
                print(
                    f"   [{int(word['start_time']) // 60:02d}:{int(word['start_time']) % 60:02d}.{int((word['start_time'] % 1) * 100):02d}] {word['word']}"
                )


def main():
    # Initialize transcriber
    transcriber = GCSSpeechToTextTranscriber()

    # Setup GCS bucket
    if not transcriber.setup_bucket():
        print(" Failed to setup GCS bucket")
        return

    # Path to your audio file
    audio_file = r"C:\Users\KIIT0001\Downloads\chirpcomparison-20251013T133300Z-1-001\chirpcomparison\chirp2\HI\ZT3_CE31477\ZT3_CE31477.mp4"
    #C:\Users\KIIT0001\Downloads\chirpcomparison-20251013T133300Z-1-001\chirpcomparison\chirp2\HI\ZT3_CE31477\ZT3_CE31477.mp4
    print(" GCS SPEECH-TO-TEXT WITH REAL TIMESTAMPS")
    print("=" * 60)
    print(" Using Google Cloud Storage for large file support")
    print(" Background noise may affect transcription quality")
    print(" But timestamps will be GENUINELY accurate")
    print("=" * 60)

    gcs_uri = None

    try:
        # Upload to GCS
        gcs_uri = transcriber.upload_audio_to_gcs(audio_file)
        if not gcs_uri:
            print(" Failed to upload to GCS")
            return

        # Transcribe from GCS
        results = transcriber.transcribe_from_gcs(gcs_uri)

        if results and results["words"]:
            # Analyze timestamp accuracy
            transcriber.analyze_timestamp_accuracy(results)

            # Save results
            print("\n Saving results...")

            # Save raw JSON data
            with open("gcs_speech_to_text_results.json", "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            # Save different formats
            word_level = transcriber.format_timestamped_transcript(results, "words")
            with open("gcs_word_timestamps.txt", "w", encoding="utf-8") as f:
                f.write(word_level)

            segment_level = transcriber.format_timestamped_transcript(
                results, "segments"
            )
            with open("gcs_segment_timestamps.txt", "w", encoding="utf-8") as f:
                f.write(segment_level)

            readable_format = transcriber.format_timestamped_transcript(
                results, "readable"
            )
            with open("gcs_readable_transcript.txt", "w", encoding="utf-8") as f:
                f.write(readable_format)

            print(" Files saved:")
            print("   - gcs_speech_to_text_results.json (complete data)")
            print("   - gcs_word_timestamps.txt (word-level timing)")
            print("   - gcs_segment_timestamps.txt (segment-level timing)")
            print("   - gcs_readable_transcript.txt (human-readable)")

            # Show sample
            print("\n Sample of REAL timestamped transcript:")
            print("-" * 50)
            sample_lines = readable_format.split("\n")[:20]
            for line in sample_lines:
                print(line)
            if len(readable_format.split("\n")) > 20:
                print("... (truncated)")
            print("-" * 50)

        else:
            print(" GCS Speech-to-Text transcription failed")

    finally:
        # Cleanup GCS file
        if gcs_uri:
            transcriber.cleanup_gcs_file(audio_file)


if __name__ == "__main__":
    main()