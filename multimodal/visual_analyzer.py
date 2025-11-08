import base64
import concurrent.futures
import io
import math
from typing import Dict, List, Tuple

import cv2
import numpy as np
from config import KPI_DEFINITIONS, VIDEO_ANALYSIS, VISION_MODEL
from google import genai
from PIL import Image


class GoogleVisualAnalyzer:
    """Production-ready visual analyzer using Gemini 2.5 Flash"""

    def __init__(self):
        self.genai_client = None
        self._setup_genai_client()
        self.vision_prompt = self._get_vision_prompt()

    def _setup_genai_client(self):
        """Setup Gemini client for visual analysis"""
        try:
            self.genai_client = genai.Client(
                vertexai=True, project="tough-cascade-402415", location="global"
            )
            print(" Gemini visual analyzer client initialized successfully")
        except Exception as e:
            print(f" Gemini visual analyzer client initialization failed: {e}")
            self.genai_client = None

    def _get_vision_prompt(self) -> str:
        """Get the vision analysis prompt optimized for sales coaching"""
        prompt = "You are analyzing a sales presentation video frame for coaching purposes. The person is speaking about: {transcript_snippet}\n\n"
        prompt += "Analyze this frame and provide feedback on these specific categories. For each category, provide:\n"
        prompt += "1. A score from 1-5 (5 being excellent)\n"
        prompt += "2. Specific observations about what you see\n"
        prompt += "3. Actionable suggestions for improvement\n\n"
        prompt += "Format your response exactly like this:\n"

        for kpi, definition in KPI_DEFINITIONS.items():
            prompt += f"{kpi}: SCORE|OBSERVATION|SUGGESTION\n"

        prompt += "\nScore guidelines:\n"
        for i in range(5, 0, -1):
            prompt += f"- {i}: {KPI_DEFINITIONS['eye_contact']['scoring_criteria'][5 - i].split(': ')[1]}\n"

        prompt += "\nFocus on sales presentation context and professional communication standards.\n"

        for kpi, definition in KPI_DEFINITIONS.items():
            if "special_instructions" in definition:
                prompt += f"\nFor {kpi}: {definition['special_instructions']}\n"

        # New addition for fairness in video production
        prompt += "\nAdditional Guidelines:\n"
        prompt += "- For eye contact and body language: Do not penalize if the presenter's face/head is out of frame or gaze is downward due to close-up shots of the product—these are common in demo videos to show details and may be the cameraman's choice, not the presenter's fault. Only deduct if it seems like unnecessary avoidance (e.g., looking away without purpose). Infer from context: If the transcript snippet discusses product internals, assume downward gaze is intentional for demonstration.\n"
        prompt += "- Always prioritize practical, encouraging feedback over harsh judgments on production elements.\n"

        return prompt

    def analyze_single_frame(
        self, timestamp: float, frame_b64: str, transcript_snippet: str
    ) -> Dict:
        """Analyze a single video frame using Gemini 2.5 Flash"""
        if not self.genai_client:
            return {
                "timestamp": timestamp,
                "raw_analysis": "Gemini client not available",
            }

        try:
            # Format the prompt with transcript context
            formatted_prompt = self.vision_prompt.format(
                transcript_snippet=transcript_snippet
            )

            # Decode the base64 string to bytes
            image_bytes = base64.b64decode(frame_b64)
            img = Image.open(io.BytesIO(image_bytes))

            # Generate content with both image and text
            response = self.genai_client.models.generate_content(
                model=VISION_MODEL, contents=[formatted_prompt, img]
            )

            analysis_text = response.text.strip()
            print(f" Frame analysis completed at {self._format_timestamp(timestamp)}")

            return {"timestamp": timestamp, "raw_analysis": analysis_text}

        except Exception as e:
            print(
                f" Frame analysis failed at {self._format_timestamp(timestamp)}: {str(e)}"
            )
            return {"timestamp": timestamp, "raw_analysis": "Analysis unavailable"}

    def parse_vision_analysis(self, response_text: str, timestamp: float) -> Dict:
        """Parse Gemini response into structured dict"""
        result = {
            "timestamp": timestamp,
            "eye_contact_score": 3,
            "eye_contact_obs": "Analysis unavailable",
            "eye_contact_suggestion": "Maintain consistent eye contact.",
            "facial_score": 3,
            "facial_obs": "Analysis unavailable",
            "facial_suggestion": "Use expressions that match your content's tone.",
            "gestures_score": 3,
            "gestures_obs": "Analysis unavailable",
            "gestures_suggestion": "Use purposeful hand gestures to emphasize key points.",
            "posture_score": 3,
            "posture_obs": "Analysis unavailable",
            "posture_suggestion": "Maintain an open, confident posture.",
            "appearance_score": 3,
            "appearance_obs": "Analysis unavailable",
            "appearance_suggestion": "Ensure a professional appearance.",
        }

        if response_text == "Analysis unavailable":
            return result

        lines = response_text.strip().split("\n")
        for line in lines:
            if ":" not in line or "|" not in line:
                continue

            category, content = line.split(":", 1)
            category = category.strip().lower()

            key_map = {
                "eye_contact": (
                    "eye_contact_score",
                    "eye_contact_obs",
                    "eye_contact_suggestion",
                ),
                "facial": ("facial_score", "facial_obs", "facial_suggestion"),
                "gestures": ("gestures_score", "gestures_obs", "gestures_suggestion"),
                "posture": ("posture_score", "posture_obs", "posture_suggestion"),
                "appearance": (
                    "appearance_score",
                    "appearance_obs",
                    "appearance_suggestion",
                ),
                "professional appearance": (
                    "appearance_score",
                    "appearance_obs",
                    "appearance_suggestion",
                ),
            }

            found_key = None
            for key_word, keys in key_map.items():
                if key_word in category:
                    found_key = keys
                    break

            if not found_key:
                continue

            score_key, obs_key, suggestion_key = found_key
            parts = content.split("|", 2)

            if len(parts) == 3:
                try:
                    score = int(parts[0].strip())
                    if 1 <= score <= 5:
                        result[score_key] = score
                except ValueError:
                    pass

                result[obs_key] = parts[1].strip()
                result[suggestion_key] = parts[2].strip()

        return result

    def summarize_visual_analysis(self, frame_analyses: List[Dict]) -> Dict:
        """Summarize parsed frame analyses into a visual report"""
        parsed_analyses = []
        for fa in frame_analyses:
            if "raw_analysis" in fa and fa["raw_analysis"] != "Analysis unavailable":
                parsed = self.parse_vision_analysis(fa["raw_analysis"], fa["timestamp"])
                parsed_analyses.append(parsed)

        if not parsed_analyses:
            print(" No valid visual analyses found - using placeholder data")
            return {
                "body_language": {
                    "score": 3,
                    "justification": "Visual analysis unavailable",
                    "improvement_suggestion": "Focus on maintaining open and confident body language.",
                },
                "eye_contact": {
                    "score": 3,
                    "justification": "Visual analysis unavailable",
                    "improvement_suggestion": "Aim for consistent eye contact with the audience.",
                },
                "gestures": {
                    "score": 3,
                    "justification": "Visual analysis unavailable",
                    "improvement_suggestion": "Use purposeful hand gestures to emphasize key points.",
                },
                "appearance": {
                    "score": 3,
                    "justification": "Visual analysis unavailable",
                    "improvement_suggestion": "Ensure professional appearance aligns with the context.",
                },
                "visual_highlights": "No visual highlights available.",
                "visual_lowlights": "No visual lowlights available.",
            }

        categories = ["eye_contact", "facial", "gestures", "posture", "appearance"]
        scores = {cat: [] for cat in categories}
        observations = {cat: [] for cat in categories}
        suggestions = {cat: [] for cat in categories}

        for entry in parsed_analyses:
            for cat in categories:
                score_key = f"{cat}_score"
                obs_key = f"{cat}_obs"
                sug_key = f"{cat}_suggestion"

                if score_key in entry and isinstance(entry[score_key], (int, float)):
                    scores[cat].append(entry[score_key])
                if obs_key in entry and entry[obs_key] != "Analysis unavailable":
                    observations[cat].append((entry["timestamp"], entry[obs_key]))
                if sug_key in entry and entry[sug_key].strip():
                    suggestions[cat].append(
                        (entry["timestamp"], entry[sug_key], entry[score_key])
                    )

        final_scores = {
            cat: int(round(np.mean(scores[cat]))) if scores[cat] else 3
            for cat in categories
        }

        highlights, lowlights = [], []
        for cat in categories:
            if not observations[cat]:
                continue

            cat_scores = sorted(
                [
                    (entry["timestamp"], entry[f"{cat}_score"])
                    for entry in parsed_analyses
                    if f"{cat}_score" in entry
                ],
                key=lambda x: x[1],
                reverse=True,
            )

            if not cat_scores:
                continue

            # Best moment (if score >=4)
            if cat_scores[0][1] >= 4:
                best_ts = cat_scores[0][0]
                best_obs = next(
                    (obs for ts, obs in observations[cat] if ts == best_ts), None
                )
                if best_obs:
                    highlights.append(
                        f"At {self._format_timestamp(best_ts)} ({cat.replace('_', ' ')}): {best_obs}"
                    )

            # Worst moment (if score <=2)
            if cat_scores[-1][1] <= 2:
                worst_ts = cat_scores[-1][0]
                worst_obs = next(
                    (obs for ts, obs in observations[cat] if ts == worst_ts), None
                )
                if worst_obs:
                    lowlights.append(
                        f"At {self._format_timestamp(worst_ts)} ({cat.replace('_', ' ')}): {worst_obs}"
                    )

        visual_highlights_text = (
            " ".join(highlights) if highlights else "No notable visual highlights."
        )
        visual_lowlights_text = (
            " ".join(lowlights) if lowlights else "No notable visual lowlights."
        )

        def get_justification(cat_name: str, score: int, cat_observations: list) -> str:
            """Generate justification based on score and observations"""
            if score >= 4:
                return f"{cat_name.capitalize()} was strong overall, with positive examples like: {'; '.join([f'At {self._format_timestamp(ts)}: {obs}' for ts, obs in cat_observations[:2]])}."
            elif score <= 2:
                return f"{cat_name.capitalize()} needs improvement, with issues like: {'; '.join([f'At {self._format_timestamp(ts)}: {obs}' for ts, obs in cat_observations[:2]])}."
            return f"{cat_name.capitalize()} was average, with mixed observations such as: {'; '.join([f'At {self._format_timestamp(ts)}: {obs}' for ts, obs in cat_observations[:2]])}."

        def get_best_suggestion(cat: str) -> str:
            """Pick the best suggestion (highest score if available, else any)"""
            if not suggestions[cat]:
                return "No specific suggestion available."
            best = max(suggestions[cat], key=lambda x: x[2])
            return best[1]

        return {
            "body_language": {
                "score": final_scores["posture"],
                "justification": get_justification(
                    "posture", final_scores["posture"], observations["posture"]
                ),
                "improvement_suggestion": get_best_suggestion("posture"),
            },
            "eye_contact": {
                "score": final_scores["eye_contact"],
                "justification": get_justification(
                    "eye_contact",
                    final_scores["eye_contact"],
                    observations["eye_contact"],
                ),
                "improvement_suggestion": get_best_suggestion("eye_contact"),
            },
            "gestures": {
                "score": final_scores["gestures"],
                "justification": get_justification(
                    "gestures", final_scores["gestures"], observations["gestures"]
                ),
                "improvement_suggestion": get_best_suggestion("gestures"),
            },
            "appearance": {
                "score": final_scores["appearance"],
                "justification": get_justification(
                    "appearance", final_scores["appearance"], observations["appearance"]
                ),
                "improvement_suggestion": get_best_suggestion("appearance"),
            },
            "visual_highlights": visual_highlights_text,
            "visual_lowlights": visual_lowlights_text,
        }

    def calculate_analysis_points(
        self, segment_start: float, segment_end: float, min_interval: float = 3.0
    ) -> List[float]:
        """Calculate optimal analysis points using sqrt(segment_time) + 1 formula"""
        segment_duration = segment_end - segment_start

        # Calculate base number of points using sqrt + 1
        base_points = int(math.sqrt(segment_duration)) + 1

        # Calculate natural spacing
        natural_spacing = (
            segment_duration / (base_points - 1)
            if base_points > 1
            else segment_duration
        )

        # Apply minimum interval constraint
        if natural_spacing < min_interval:
            max_points = int(segment_duration / min_interval) + 1
            actual_spacing = (
                segment_duration / (max_points - 1)
                if max_points > 1
                else segment_duration
            )
            num_points = max_points
        else:
            actual_spacing = natural_spacing
            num_points = base_points

        # Generate analysis times
        analysis_times = []
        for i in range(num_points):
            timestamp = segment_start + (i * actual_spacing)
            analysis_times.append(timestamp)

        return analysis_times

    def extract_keyframes_for_segments(
        self, video_path: str, segments: List[Dict]
    ) -> List[Tuple[float, str, str]]:
        """Extract base64-encoded frames with optimized analysis points"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f" Could not open video file: {video_path}")
            return []

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_data = []
        total_frames = 0

        for segment in segments:
            # Calculate analysis points
            analysis_times = self.calculate_analysis_points(
                segment["start_time"],
                segment["end_time"],
                VIDEO_ANALYSIS.get("min_frame_interval", 3.0),
            )

            # Cap at maximum frames per segment
            max_frames = VIDEO_ANALYSIS.get("max_frames_per_segment", 10)
            if len(analysis_times) > max_frames:
                step = len(analysis_times) / max_frames
                analysis_times = [
                    analysis_times[int(i * step)] for i in range(max_frames)
                ]

            print(
                f" Segment {segment['start_time']:.1f}-{segment['end_time']:.1f}s: {len(analysis_times)} analysis points"
            )

            for target_time in analysis_times:
                frame_idx = int(target_time * fps)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if not ret:
                    continue

                _, buffer = cv2.imencode(".jpg", frame)
                frame_b64 = base64.b64encode(buffer).decode("utf-8")

                # Get transcript context
                segment_progress = (target_time - segment["start_time"]) / (
                    segment["end_time"] - segment["start_time"]
                )
                if segment_progress <= 0.5:
                    transcript_snippet = (
                        segment["text"][:150] + "..."
                        if len(segment["text"]) > 150
                        else segment["text"]
                    )
                else:
                    transcript_snippet = (
                        "..." + segment["text"][-150:]
                        if len(segment["text"]) > 150
                        else segment["text"]
                    )

                frame_data.append((target_time, frame_b64, transcript_snippet))
                total_frames += 1

        cap.release()
        print(f" Total frames extracted: {total_frames}")
        return frame_data

    def analyze_frames_parallel(
        self, frames_data: List[Tuple[float, str, str]], max_workers: int = None
    ) -> List[Dict]:
        """Analyze multiple frames in parallel using dynamic thread pool"""
        if not frames_data:
            return []

        # Dynamic thread pool sizing
        if max_workers is None:
            workers_config = VIDEO_ANALYSIS.get("parallel_workers", "dynamic")
            if workers_config == "dynamic":
                max_workers = max(1, len(frames_data) // 2)
                max_workers = min(
                    max_workers, VIDEO_ANALYSIS.get("max_workers_cap", 25)
                )
            else:
                max_workers = int(workers_config)

        print(
            f" Starting parallel analysis with {max_workers} workers for {len(frames_data)} frames"
        )

        frame_analyses = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all frame analysis tasks
            future_to_frame = {
                executor.submit(
                    self.analyze_single_frame, timestamp, frame_b64, transcript_snippet
                ): (timestamp, frame_b64, transcript_snippet)
                for timestamp, frame_b64, transcript_snippet in frames_data
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_frame):
                try:
                    result = future.result()
                    frame_analyses.append(result)
                    print(
                        f" Frame analysis completed: {self._format_timestamp(result['timestamp'])}"
                    )
                except Exception as e:
                    timestamp, _, _ = future_to_frame[future]
                    print(
                        f" Frame analysis failed at {self._format_timestamp(timestamp)}: {e}"
                    )
                    frame_analyses.append(
                        {"timestamp": timestamp, "raw_analysis": "Analysis unavailable"}
                    )

        print(f" Parallel analysis completed: {len(frame_analyses)} frames processed")
        return frame_analyses

    def analyze_video_segments(self, video_path: str, segments: List[Dict]) -> Dict:
        """Complete video analysis pipeline"""
        print(f" Starting visual analysis for {len(segments)} segments")

        # Extract keyframes
        frames_data = self.extract_keyframes_for_segments(video_path, segments)
        if not frames_data:
            print(" No frames extracted for analysis")
            return self.summarize_visual_analysis([])

        # Analyze frames in parallel
        frame_analyses = self.analyze_frames_parallel(frames_data)

        # Summarize results
        visual_summary = self.summarize_visual_analysis(frame_analyses)

        print(
            f" Visual analysis completed with summary scores: "
            f"Body Language: {visual_summary['body_language']['score']}, "
            f"Eye Contact: {visual_summary['eye_contact']['score']}, "
            f"Gestures: {visual_summary['gestures']['score']}, "
            f"Appearance: {visual_summary['appearance']['score']}"
        )

        return visual_summary

    def _format_timestamp(self, seconds: float) -> str:
        """Format timestamp in MM:SS format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def validate_visual_analysis(self, analysis: Dict) -> bool:
        """Validate visual summary structure and scores"""
        required_categories = ["body_language", "eye_contact", "gestures", "appearance"]
        for category in required_categories:
            if category not in analysis:
                print(f" Visual analysis missing required category: {category}")
                return False
            if not all(k in analysis[category] for k in ["score", "justification"]):
                print(f" Visual analysis for {category} missing required fields")
                return False
            if not isinstance(analysis[category]["score"], (int, float)) or not (
                1 <= analysis[category]["score"] <= 5
            ):
                print(f" Invalid score for {category}: {analysis[category]['score']}")
                return False
        return True
