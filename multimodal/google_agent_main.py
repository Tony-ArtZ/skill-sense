import os
import json
import argparse
from typing import Optional, Dict, List
from pathlib import Path
#python main.py --input "AkashX.ai Regional Language Demo GAD/ZT3_CE31477.mp4" --language hi
from audio_processor import GoogleAudioProcessor
from visual_analyzer import GoogleVisualAnalyzer
from critique_generator import GoogleCritiqueGenerator
from config import DEFAULT_INPUT_PATH, DEFAULT_OUTPUT_PATH, LANGUAGE_CONFIGS, OUTPUT_FILES

class GoogleSalesPitchAnalyzer:
    """Main orchestrator for multilingual sales pitch analysis using Google AI"""

    def __init__(self):
        self.audio_processor = GoogleAudioProcessor()
        self.visual_analyzer = GoogleVisualAnalyzer()
        self.critique_generator = GoogleCritiqueGenerator()
        self.output_path = DEFAULT_OUTPUT_PATH

    def detect_language(self, file_path: str) -> str:
        """Detect language based on file path patterns"""
        file_path_lower = file_path.lower()

        # Check for language indicators in file path
        if any(indicator in file_path_lower for indicator in ['tamil', 'ta']):
            return 'ta'
        elif any(indicator in file_path_lower for indicator in ['telugu', 'te']):
            return 'te'
        else:
            # Default to Hindi for Indian sales pitches
            return 'hi'

    def get_output_file_path(self, base_name: str, file_type: str) -> str:
        """Generate standardized output file paths"""
        filename = OUTPUT_FILES[file_type].format(base_name=base_name)
        return os.path.join(self.output_path, filename)

    def process_media_file(self, file_path: str, language: Optional[str] = None) -> Dict:
        """Process a single media file (audio or video)"""
        print(f"\n{'='*60}")
        print(f" Processing: {os.path.basename(file_path)}")
        print(f"{'='*60}")

        # Detect language if not specified
        detected_language = language or self.detect_language(file_path)
        lang_config = LANGUAGE_CONFIGS[detected_language]
        print(f" Language: {lang_config['name']} ({detected_language})")

        # Get base name for output files
        base_name = Path(file_path).stem
        results = {}

        # Determine video file path for visual analysis
        video_file_path = self._find_video_file(file_path)

        try:
            # Step 1: Audio processing pipeline
            print("\n Step 1: Audio Processing Pipeline")
            audio_result = self.audio_processor.process_audio_pipeline(file_path, detected_language)

            if not audio_result:
                print(" Audio processing failed")
                return {"status": "error", "message": "Audio processing failed"}

            # Extract components
            segments = audio_result.get("segments", [])
            prosodic_features = audio_result.get("prosodic_features", {})
            english_translation = audio_result.get("english_translation", "")
            original_text = audio_result.get("original_text", "")

            # Save basic outputs
            self._save_transcript_results(base_name, audio_result, detected_language)

            # Step 2: Visual analysis (if video file exists)
            visual_summary = {}
            if video_file_path and segments:
                print(f"\n Step 2: Visual Analysis (using video: {os.path.basename(video_file_path)})")
                try:
                    visual_summary = self.visual_analyzer.analyze_video_segments(video_file_path, segments)

                    # Validate and save visual analysis
                    if self.visual_analyzer.validate_visual_analysis(visual_summary):
                        visual_path = self.get_output_file_path(base_name, "visual")
                        with open(visual_path, "w", encoding="utf-8") as vf:
                            json.dump(visual_summary, vf, indent=2, ensure_ascii=False)
                        print(f" Visual analysis saved: {visual_path}")
                        results["visual_analysis"] = visual_summary
                    else:
                        print(" Visual analysis validation failed")

                except Exception as e:
                    print(f" Visual analysis failed: {e}")
            elif not video_file_path:
                print("\n Step 2: Visual Analysis (skipped - no video file found)")
            else:
                print("\n Step 2: Visual Analysis (skipped - no segments for analysis)")

            # Step 3: Critique generation
            if segments and prosodic_features:
                print("\n Step 3: Sales Coaching Critique")
                try:
                    critique = self.critique_generator.generate_critique(
                        segments, prosodic_features, english_translation,
                        visual_summary, detected_language
                    )

                    if critique:
                        critique_path = self.get_output_file_path(base_name, "critique")
                        with open(critique_path, "w", encoding="utf-8") as cf:
                            json.dump(critique, cf, indent=2, ensure_ascii=False)
                        print(f" Sales coaching critique saved: {critique_path}")
                        results["critique"] = critique

                        # Generate segmented critique for detailed feedback
                        segmented_critique = self.critique_generator.generate_segmented_critique(
                            segments, prosodic_features, visual_summary, detected_language
                        )

                        if segmented_critique:
                            segmented_path = self.get_output_file_path(base_name, "segments")
                            with open(segmented_path, "w", encoding="utf-8") as sf:
                                json.dump(segmented_critique, sf, indent=2, ensure_ascii=False)
                            print(f" Segmented critique saved: {segmented_path}")
                            results["segmented_critique"] = segmented_critique

                    else:
                        print(" Critique generation failed")

                except Exception as e:
                    print(f" Critique generation failed: {e}")

            # Step 4: Generate summary report
            print("\n Step 4: Summary Report")
            summary = self._generate_summary_report(
                base_name, detected_language, segments, prosodic_features,
                english_translation, visual_summary, results.get("critique", {})
            )

            summary_path = self.get_output_file_path(base_name, "summary")
            with open(summary_path, "w", encoding="utf-8") as sf:
                json.dump(summary, sf, indent=2, ensure_ascii=False)
            print(f" Summary report saved: {summary_path}")

            results.update({
                "status": "success",
                "language": detected_language,
                "file_path": file_path,
                "base_name": base_name,
                "segments_count": len(segments),
                "duration_seconds": prosodic_features.get("duration_s", 0),
                "word_count": prosodic_features.get("word_count", 0),
                "summary": summary
            })

            print(f"\n Analysis completed successfully for {base_name}")
            return results

        except Exception as e:
            print(f" Error processing {file_path}: {e}")
            return {"status": "error", "message": str(e)}

    def _save_transcript_results(self, base_name: str, audio_result: Dict, language: str):
        """Save transcript results with timestamps"""
        transcription_result = audio_result.get("transcription_result", {})

        # Save original transcript with timestamps
        original_text = audio_result.get("original_text", "")
        if original_text and transcription_result:
            # Save plain transcript
            transcript_path = self.get_output_file_path(base_name, "transcription")
            with open(transcript_path, "w", encoding="utf-8") as tf:
                tf.write(original_text)
            print(f" Original transcript saved: {transcript_path}")

            # Save word-level timestamps
            if "words" in transcription_result:
                word_timestamps = self._format_word_timestamps(transcription_result["words"])
                word_timestamps_path = self.get_output_file_path(base_name, "word_timestamps")
                with open(word_timestamps_path, "w", encoding="utf-8") as wf:
                    wf.write(word_timestamps)
                print(f" Word timestamps saved: {word_timestamps_path}")

            # Save segment-level timestamps
            if "segments" in transcription_result:
                segment_timestamps = self._format_segment_timestamps(transcription_result["segments"])
                segment_timestamps_path = self.get_output_file_path(base_name, "segment_timestamps")
                with open(segment_timestamps_path, "w", encoding="utf-8") as sf:
                    sf.write(segment_timestamps)
                print(f" Segment timestamps saved: {segment_timestamps_path}")

            # Save readable transcript with timestamps
            readable_transcript = audio_result.get("readable_transcript", "")
            if readable_transcript:
                readable_path = self.get_output_file_path(base_name, "readable_transcript")
                with open(readable_path, "w", encoding="utf-8") as rf:
                    rf.write(readable_transcript)
                print(f" Readable transcript saved: {readable_path}")

        # Save English translation
        english_translation = audio_result.get("english_translation", "")
        if english_translation:
            translation_path = self.get_output_file_path(base_name, "translation")
            with open(translation_path, "w", encoding="utf-8") as tf:
                tf.write(english_translation)
            print(f" English translation saved: {translation_path}")

        # Save prosodic features
        prosodic_features = audio_result.get("prosodic_features", {})
        if prosodic_features:
            prosodic_path = self.get_output_file_path(base_name, "prosodic")
            with open(prosodic_path, "w", encoding="utf-8") as pf:
                json.dump(prosodic_features, pf, indent=2, ensure_ascii=False)
            print(f" Prosodic features saved: {prosodic_path}")

    def _format_word_timestamps(self, words: List[Dict]) -> str:
        """Format word-level timestamps for output"""
        lines = []
        for word in words:
            start_time = word["start_time"]
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            milliseconds = int((start_time % 1) * 100)
            timestamp = f"[{minutes:02d}:{seconds:02d}.{milliseconds:02d}]"
            lines.append(f"{timestamp} {word['word']}")
        return "\n".join(lines)

    def _format_segment_timestamps(self, segments: List[Dict]) -> str:
        """Format segment-level timestamps for output"""
        lines = []
        for segment in segments:
            start_time = segment["start_time"]
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            timestamp = f"[{minutes:02d}:{seconds:02d}]"
            lines.append(f"{timestamp} {segment['text']}")
        return "\n".join(lines)



    def _find_video_file(self, audio_file_path: str) -> Optional[str]:
        """Find corresponding video file for audio file"""
        audio_path = Path(audio_file_path)
        base_name = audio_path.stem

        # Check if it's already a video file
        if audio_path.suffix.lower() in {".mp4", ".mov", ".avi", ".mkv"}:
            return audio_file_path

        # Look for video file with same name in same directory
        video_extensions = [".mp4", ".mov", ".avi", ".mkv"]
        for ext in video_extensions:
            video_path = audio_path.with_suffix(ext)
            if video_path.exists():
                return str(video_path)

        # Look in FINAL DEMO directory
        final_demo_dir = Path(audio_file_path).parent / "Video" / "FINAL DEMO"
        if final_demo_dir.exists():
            for ext in video_extensions:
                video_path = final_demo_dir / f"{base_name}{ext}"
                if video_path.exists():
                    return str(video_path)

        # Look in parent Video directory
        parent_video_dir = Path(audio_file_path).parent / "Video"
        if parent_video_dir.exists():
            for ext in video_extensions:
                video_path = parent_video_dir / f"{base_name}{ext}"
                if video_path.exists():
                    return str(video_path)

        return None

    def _generate_summary_report(self, base_name: str, language: str, segments: List[Dict],
                               prosodic_features: Dict, english_translation: str,
                               visual_summary: Dict, critique: Dict) -> Dict:
        """Generate comprehensive summary report"""
        lang_config = LANGUAGE_CONFIGS[language]

        # Calculate key metrics
        duration = prosodic_features.get("duration_s", 0)
        word_count = prosodic_features.get("word_count", 0)
        speech_rate = prosodic_features.get("speech_rate_wps", 0)

        # Get critique scores
        critique_scores = {}
        if critique:
            for category in ["pitch_adherence", "confidence", "technical_knowledge",
                           "customer_pain_points_connection", "active_demonstration",
                           "body_language", "eye_contact", "gestures", "appearance"]:
                if category in critique:
                    critique_scores[category] = critique[category].get("score", 3)

        # Calculate overall score
        overall_score = sum(critique_scores.values()) / len(critique_scores) if critique_scores else 3.0

        # Get visual scores
        visual_scores = {}
        if visual_summary:
            for category in ["body_language", "eye_contact", "gestures", "appearance"]:
                if category in visual_summary:
                    visual_scores[category] = visual_summary[category].get("score", 3)

        return {
            "file_info": {
                "filename": base_name,
                "language": lang_config["name"],
                "language_code": language,
                "duration_seconds": duration,
                "word_count": word_count,
                "segments_count": len(segments),
                "speech_rate_words_per_second": round(speech_rate, 2)
            },
            "performance_scores": {
                "overall_score": round(overall_score, 1),
                "critique_scores": critique_scores,
                "visual_scores": visual_scores
            },
            "coaching_focus": lang_config["coaching_focus"],
            "key_insights": {
                "strengths": self._extract_strengths(critique, visual_summary),
                "improvement_areas": self._extract_improvements(critique, visual_summary)
            },
            "files_generated": [
                OUTPUT_FILES[file_type].format(base_name=base_name)
                for file_type in OUTPUT_FILES.keys()
            ]
        }

    def _extract_strengths(self, critique: Dict, visual_summary: Dict) -> List[str]:
        """Extract key strengths from critique and visual analysis"""
        strengths = []

        # High-scoring categories from critique
        if critique:
            for category, data in critique.items():
                if isinstance(data, dict) and data.get("score", 0) >= 4:
                    strengths.append(f"Strong {category.replace('_', ' ')}")

        # High-scoring visual categories
        if visual_summary:
            for category, data in visual_summary.items():
                if isinstance(data, dict) and data.get("score", 0) >= 4:
                    strengths.append(f"Strong visual {category.replace('_', ' ')}")

        return strengths if strengths else ["Areas for further development identified"]

    def _extract_improvements(self, critique: Dict, visual_summary: Dict) -> List[str]:
        """Extract improvement areas from critique and visual analysis"""
        improvements = []

        # Low-scoring categories from critique
        if critique:
            for category, data in critique.items():
                if isinstance(data, dict) and data.get("score", 0) <= 2:
                    improvements.append(f"Improve {category.replace('_', ' ')}")

        # Low-scoring visual categories
        if visual_summary:
            for category, data in visual_summary.items():
                if isinstance(data, dict) and data.get("score", 0) <= 2:
                    improvements.append(f"Improve visual {category.replace('_', ' ')}")

        return improvements if improvements else ["Continue developing all presentation skills"]

    def process_directory(self, directory_path: str, language: Optional[str] = None,
                         file_limit: Optional[int] = None) -> List[Dict]:
        """Process all media files in a directory"""
        print(f" Starting batch processing of directory: {directory_path}")

        supported_extensions = {".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg", ".mp4", ".mov", ".avi", ".mkv"}
        media_files = []

        for ext in supported_extensions:
            media_files.extend(Path(directory_path).glob(f"*{ext}"))

        # Apply file limit if specified
        if file_limit:
            media_files = media_files[:file_limit]

        print(f" Found {len(media_files)} media files to process")

        results = []
        for i, file_path in enumerate(media_files, 1):
            print(f"\n Processing file {i}/{len(media_files)}")
            result = self.process_media_file(str(file_path), language)
            results.append(result)

        # Generate batch summary
        batch_summary = self._generate_batch_summary(results)
        batch_path = os.path.join(self.output_path, "batch_summary.json")
        with open(batch_path, "w", encoding="utf-8") as bf:
            json.dump(batch_summary, bf, indent=2, ensure_ascii=False)
        print(f" Batch summary saved: {batch_path}")

        return results

    def _generate_batch_summary(self, results: List[Dict]) -> Dict:
        """Generate summary for batch processing"""
        total_files = len(results)
        successful_files = len([r for r in results if r.get("status") == "success"])
        failed_files = total_files - successful_files

        # Calculate aggregate metrics
        total_duration = sum(r.get("duration_seconds", 0) for r in results)
        total_words = sum(r.get("word_count", 0) for r in results)
        total_segments = sum(r.get("segments_count", 0) for r in results)

        # Language distribution
        language_counts = {}
        for r in results:
            lang = r.get("language", "unknown")
            language_counts[lang] = language_counts.get(lang, 0) + 1

        return {
            "batch_info": {
                "total_files": total_files,
                "successful_files": successful_files,
                "failed_files": failed_files,
                "success_rate": round((successful_files / total_files * 100) if total_files > 0 else 0, 1)
            },
            "aggregate_metrics": {
                "total_duration_seconds": total_duration,
                "total_words_processed": total_words,
                "total_segments_analyzed": total_segments,
                "average_duration_seconds": round(total_duration / successful_files, 1) if successful_files > 0 else 0
            },
            "language_distribution": language_counts,
            "files_processed": [r.get("file_path", "unknown") for r in results]
        }

def main():
    parser = argparse.ArgumentParser(description="Google AI Sales Pitch Analyzer")
    parser.add_argument("--input", "-i", help="Input file or directory path")
    parser.add_argument("--language", "-l", choices=["hi", "ta", "te"], help="Language code (hi=Hindi, ta=Tamil, te=Telugu)")
    parser.add_argument("--batch", "-b", action="store_true", help="Process all files in directory")
    parser.add_argument("--limit", type=int, help="Limit number of files to process in batch mode")
    parser.add_argument("--output", "-o", help="Output directory path")

    args = parser.parse_args()

    analyzer = GoogleSalesPitchAnalyzer()

    # Override output path if specified
    if args.output:
        analyzer.output_path = args.output
        os.makedirs(analyzer.output_path, exist_ok=True)

    input_path = args.input or DEFAULT_INPUT_PATH

    if not os.path.exists(input_path):
        print(f" Input path not found: {input_path}")
        return

    if args.batch or os.path.isdir(input_path):
        # Batch processing
        results = analyzer.process_directory(input_path, args.language, args.limit)
        print(f"\n Batch processing completed: {len(results)} files processed")
    else:
        # Single file processing
        result = analyzer.process_media_file(input_path, args.language)
        if result.get("status") == "success":
            print(f"\n Processing completed successfully!")
        else:
            print(f"\n Processing failed: {result.get('message', 'Unknown error')}")

if __name__ == "__main__":
    main()