import concurrent.futures
import json
import re
from typing import Dict, List, Optional

from config import CRITIQUE_MODEL, KPI_DEFINITIONS, LANGUAGE_CONFIGS
from google import genai


class GoogleCritiqueGenerator:
    """Production-ready critique generator using Gemini 2.5 Flash"""

    def __init__(self):
        self.genai_client = None
        self._setup_genai_client()
        self.master_prompt = self._get_master_prompt()

    def _setup_genai_client(self):
        """Setup Gemini client for critique generation"""
        try:
            self.genai_client = genai.Client(
                vertexai=True, project="tough-cascade-402415", location="global"
            )
            print(" Gemini critique generator client initialized successfully")
        except Exception as e:
            print(f" Gemini critique generator client initialization failed: {e}")
            self.genai_client = None

    def _get_master_prompt(self) -> str:
        """Get the master critique prompt optimized for multilingual sales coaching"""
        prompt = "You are an expert Sales Pitch Analyst and Coach. Your audience is a non-technical sales representative. Adopt a constructive and encouraging coaching persona.\n\n"
        prompt += (
            "Your task is to analyze a {language} sales pitch. You will be given:\n"
        )
        prompt += "1. Detailed AGGREGATE acoustic/prosodic data\n"
        prompt += "2. A SEGMENTED breakdown of the speech with timestamps\n"
        prompt += (
            "3. A DETAILED VISUAL ANALYSIS SUMMARY with timestamped observations\n\n"
        )
        prompt += "CRITICAL INSTRUCTIONS:\n"
        prompt += "1. **SCORING**: Score every category on a scale of 1 to 5. DO NOT use scores outside this 1-5 range.\n"
        prompt += "2. **NO JARGON**: Translate all technical data into simple, descriptive language. For prosodic features, avoid raw numbers (e.g., Hz, RMS, words per second) entirely—focus on everyday descriptions like 'your voice had good energy' or 'you spoke at a quick pace.' Do not overwhelm with metrics; reference prosody sparingly (1-2 insights max per justification) and only if it directly explains the score. Examples: Instead of 'pitch std dev 90 Hz,' say 'your tone varied nicely, showing enthusiasm.' Instead of 'speech rate 5.5 wps,' say 'you spoke quickly, which added energy but might rush details.' Ignore complex terms like RMS unless simplified to 'volume was steady.'\n"  # Strengthened with prosody focus, examples, and minimization.
        prompt += "3. **USE ALL TIMESTAMPS**: Reference specific timestamps from both vocal and visual analysis.\n"
        prompt += "4. **EVIDENCE-BASED JUSTIFICATION**: Must reference specific timestamped examples from visual summary.\n"
        prompt += (
            "5. **CULTURAL CONTEXT**: Consider {cultural_context} in your analysis.\n"
        )
        prompt += "6. **ACTIONABLE SUGGESTIONS**: Make highly specific, actionable recommendations.\n"
        prompt += "7. **OUTPUT LANGUAGE**: Your entire final output, including all justifications and suggestions, MUST be in English.\n\n"

        prompt += "\nProduce a JSON object with the exact following structure:\n{\n"
        kpi_prompts = []
        for kpi in KPI_DEFINITIONS.keys():
            kpi_prompts.append(
                f'  "{kpi}": {{ "score": <integer (1-5)>, "justification": "<string>", "improvement_suggestion": "<string>" }}'
            )
        prompt += ",\n".join(kpi_prompts)
        prompt += ",\n"

        prompt += '  "dynamic_delivery_analysis": {\n'
        prompt += '      "highlights": "<string> (Describe moments using [MM:SS] timestamps. Include both vocal and visual aspects.)",\n'
        prompt += '      "lowlights": "<string> (Describe moments using [MM:SS] timestamps. Include both vocal and visual aspects.)"\n'
        prompt += "  },\n"
        prompt += '  "overall_summary": "<string> (Integrate both vocal and visual feedback)",\n'
        prompt += '  "final_improvement_suggestion": "<string> (Include both vocal and visual recommendations)",\n'
        prompt += '  "key_coaching_takeaway": "<string> (Provide a single, memorable \'golden nugget\' of advice.)"\n'
        prompt += "}\n\n"

        return prompt

    def _extract_json_from_text(self, text: str) -> Optional[Dict]:
        """Extract JSON from text using robust parsing"""
        try:
            # Try to find JSON object in the text
            json_match = re.search(r"\{[\s\S]*\}", text)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f" JSON parsing error: {e}")
            print(f" Problematic JSON string: {json_str[:200]}...")
            pass

        # Fallback: try to parse the entire text as JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        return None

    def _validate_critique_structure(self, critique: Dict) -> bool:
        """Validate the critique structure"""
        required_categories = list(KPI_DEFINITIONS.keys())

        required_fields = [
            "dynamic_delivery_analysis",
            "overall_summary",
            "final_improvement_suggestion",
            "key_coaching_takeaway",
        ]

        # Check required categories
        for category in required_categories:
            if category not in critique:
                print(f" Critique missing category: {category}")
                return False
            if not all(
                k in critique[category]
                for k in ["score", "justification", "improvement_suggestion"]
            ):
                print(f" Critique category {category} missing required fields")
                return False
            if not isinstance(critique[category]["score"], (int, float)) or not (
                1 <= critique[category]["score"] <= 5
            ):
                print(f" Invalid score for {category}: {critique[category]['score']}")
                return False

        # Check required fields
        for field in required_fields:
            if field not in critique:
                print(f" Critique missing field: {field}")
                return False

        return True

    def generate_critique(
        self,
        segmented_data: List[Dict],
        aggregate_features: Dict,
        english_translation: str,
        visual_summary: Dict,
        language: str = "hi",
    ) -> Optional[Dict]:
        """Generate comprehensive sales pitch critique using Gemini"""
        if not self.genai_client:
            print(" Gemini client not available for critique generation")
            return None

        print(
            f"\n--- Generating integrated audio-visual critique for {language.upper()} ---"
        )

        # Get language-specific configuration
        lang_config = LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS["hi"])

        # Prepare data without escaping (no .format() on large strings)
        agg_json = json.dumps(
            aggregate_features, indent=2, ensure_ascii=False, default=str
        )
        segmented_json = json.dumps(segmented_data, indent=2, ensure_ascii=False)
        visual_json = (
            json.dumps(visual_summary, indent=2, ensure_ascii=False)
            if visual_summary
            else "No visual analysis available."
        )

        # Build instructional text with small placeholders
        instruction_text = self.master_prompt.replace(
            "{language}", lang_config["name"]
        ).replace("{cultural_context}", lang_config["cultural_context"])

        # Build multi-part contents
        parts = [
            {"text": instruction_text},
            {
                "text": "Here is the AGGREGATE acoustic/prosodic data for the whole audio:\n---\n"
                + agg_json
                + "\n---\n\n"
            },
            {
                "text": "Here is the SEGMENTED speech breakdown with timestamps:\n---\n"
                + segmented_json
                + "\n---\n\n"
            },
            {
                "text": "Here is the DETAILED VISUAL ANALYSIS SUMMARY:\n---\n"
                + visual_json
                + "\n---\n\n"
            },
            {"text": "Provide your comprehensive analysis in valid JSON format.\n"},
        ]

        contents = [{"role": "user", "parts": parts}]

        try:
            response = self.genai_client.models.generate_content(
                model=CRITIQUE_MODEL, contents=contents
            )

            response_text = response.text.strip()
            print(" Gemini critique generation completed")

            # Extract and validate JSON
            parsed_critique = self._extract_json_from_text(response_text)
            if parsed_critique and self._validate_critique_structure(parsed_critique):
                print(" Integrated critique parsed and validated successfully")
                return parsed_critique
            else:
                print(" Could not parse or validate JSON from Gemini response")
                print(
                    "Raw response:",
                    response_text[:500] + "..."
                    if len(response_text) > 500
                    else response_text,
                )
                return None

        except Exception as e:
            print(f" Error calling Gemini for critique: {e}")
            return None

    def generate_segmented_critique(
        self,
        segments: List[Dict],
        prosodic_features: Dict,
        visual_summary: Dict,
        language: str = "hi",
    ) -> Optional[Dict]:
        """Generate segmented critique with timestamp-specific feedback using concurrent processing"""
        if not self.genai_client:
            return None

        print(f"--- Generating segmented critique for {len(segments)} segments ---")

        lang_config = LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS["hi"])

        # Process segments concurrently with ThreadPoolExecutor
        max_workers = min(5, len(segments))  # Limit concurrent workers
        print(f" Using {max_workers} concurrent workers for segment analysis")

        segmented_critique = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all segment analysis tasks
            future_to_segment = {
                executor.submit(
                    self._analyze_single_segment, segment, lang_config, i
                ): segment
                for i, segment in enumerate(segments)
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_segment):
                segment = future_to_segment[future]
                try:
                    segment_result = future.result()
                    if segment_result:
                        segmented_critique.append(segment_result)
                        print(" Segment critique generated")
                except Exception as e:
                    print(f" Failed to generate segment critique: {e}")
                    # Add placeholder
                    segmented_critique.append(
                        {
                            "segment_start": segment["start_time"],
                            "segment_end": segment["end_time"],
                            "clarity_score": 3,
                            "engagement_score": 3,
                            "technical_score": 3,
                            "observations": "Analysis unavailable",
                            "suggestions": "Review this segment for improvement opportunities",
                        }
                    )

        # Sort segments by start time to maintain order
        segmented_critique.sort(key=lambda x: x["segment_start"])

        return {
            "segmented_critique": segmented_critique,
            "segment_count": len(segmented_critique),
        }

    def _analyze_single_segment(
        self, segment: Dict, lang_config: Dict, segment_index: int
    ) -> Optional[Dict]:
        """Analyze a single segment for critique"""
        try:
            # Create segment-specific prompt
            segment_prompt = f"""
Analyze this specific segment from a {lang_config["name"]} sales presentation:

Segment Time: {self._format_timestamp(segment["start_time"])} - {self._format_timestamp(segment["end_time"])}
Duration: {segment["end_time"] - segment["start_time"]:.1f}s
Text: {segment["text"]}

Provide feedback on:
1. Clarity and effectiveness (1-5)
2. Customer engagement (1-5)
3. Technical accuracy (1-5)
4. Specific improvement suggestions

Format as JSON:
{{
  "segment_start": {segment["start_time"]},
  "segment_end": {segment["end_time"]},
  "clarity_score": <1-5>,
  "engagement_score": <1-5>,
  "technical_score": <1-5>,
  "observations": "<specific observations>",
  "suggestions": "<specific suggestions>"
}}
"""

            response = self.genai_client.models.generate_content(
                model=CRITIQUE_MODEL, contents=segment_prompt
            )

            segment_result = self._extract_json_from_text(response.text)
            if segment_result:
                return segment_result
            else:
                # Return default result if parsing failed
                return {
                    "segment_start": segment["start_time"],
                    "segment_end": segment["end_time"],
                    "clarity_score": 3,
                    "engagement_score": 3,
                    "technical_score": 3,
                    "observations": "Analysis unavailable",
                    "suggestions": "Review this segment for improvement opportunities",
                }

        except Exception as e:
            print(f" Failed to analyze segment {segment_index}: {e}")
            return {
                "segment_start": segment["start_time"],
                "segment_end": segment["end_time"],
                "clarity_score": 3,
                "engagement_score": 3,
                "technical_score": 3,
                "observations": "Analysis unavailable",
                "suggestions": "Review this segment for improvement opportunities",
            }

    def _format_timestamp(self, seconds: float) -> str:
        """Format timestamp in MM:SS format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def critique_with_llm(
        self,
        segmented_data: str,
        aggregate_features: dict,
        full_english_transcript: str,
        visual_summary: dict,
        language: str = "hi",
    ) -> Optional[dict]:
        """Legacy method - redirects to new implementation"""
        # Convert string data to expected format
        try:
            segments = (
                json.loads(segmented_data)
                if isinstance(segmented_data, str)
                else segmented_data
            )
        except:
            segments = []

        return self.generate_critique(
            segments,
            aggregate_features,
            full_english_transcript,
            visual_summary,
            language,
        )
