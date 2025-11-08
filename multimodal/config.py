import os
import re

# --- Google Cloud Configuration ---
GCP_PROJECT_ID = "tough-cascade-402415"
GCP_LOCATION = "global"
GCS_BUCKET_NAME = "tunir-ai-bucket"

# --- AI Model Configuration ---
# Use Gemini 2.5 Flash for high-quality analysis
VISION_MODEL = "gemini-2.5-flash"
CRITIQUE_MODEL = "gemini-2.5-flash"
TRANSLATION_MODEL = "gemini-2.5-flash"

# Cost-effective option for high-volume frame analysis
# VISION_MODEL = "gemini-2.5-flash-lite"

# --- Language Support Configuration ---
LANGUAGE_CONFIGS = {
    "hi": {
        "name": "Hindi",
        "speech_code": "hi-IN",
        "alternative_codes": ["en-IN"],
        "cultural_context": "Hindi sales presentations, Indian business communication norms",
        "greeting_style": "Formal business greeting common in Indian sales contexts",
        "coaching_focus": [
            "Confidence",
            "Product knowledge",
            "Customer connection",
            "Professional demeanor",
        ],
    },
    "ta": {
        "name": "Tamil",
        "speech_code": "ta-IN",
        "alternative_codes": ["en-IN"],
        "cultural_context": "Tamil business culture, South Indian sales communication",
        "greeting_style": "Respectful formal greeting typical in Tamil business settings",
        "coaching_focus": [
            "Relationship building",
            "Technical expertise",
            "Trust establishment",
            "Clear communication",
        ],
    },
    "te": {
        "name": "Telugu",
        "speech_code": "te-IN",
        "alternative_codes": ["en-IN"],
        "cultural_context": "Telugu business etiquette, Andhra/Telangana sales practices",
        "greeting_style": "Professional greeting common in Telugu business environments",
        "coaching_focus": [
            "Product demonstration",
            "Customer engagement",
            "Persuasive communication",
            "Professional appearance",
        ],
    },
}

# --- File Processing Configuration ---
ALLOWED_AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg"}
ALLOWED_VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv"}
ALLOWED_EXTS = ALLOWED_AUDIO_EXTS | ALLOWED_VIDEO_EXTS

# --- Analysis Configuration ---
SEGMENT_CONFIG = {
    "max_pause_seconds": 0.7,  # Pause threshold for segment boundaries
    "min_words_per_segment": 3,  # Minimum words for a valid segment
    "max_words_per_segment": 50,  # Maximum words before forced split
}

# Video Analysis Configuration
VIDEO_ANALYSIS = {
    "frame_extraction": "sqrt_plus_one",  # sqrt(segment_time) + 1 formula
    "min_frame_interval": 3.0,  # Minimum seconds between frames
    "max_frames_per_segment": 10,  # Cap on frames per segment
    "parallel_workers": "dynamic",  # Dynamic thread pool sizing
    "max_workers_cap": 25,  # Maximum concurrent API calls
}

# --- Output Configuration ---
OUTPUT_FILES = {
    "transcription": "{base_name}_transcript_original.txt",
    "translation": "{base_name}_translation.txt",
    "word_timestamps": "{base_name}_word_timestamps.txt",
    "segment_timestamps": "{base_name}_segment_timestamps.txt",
    "readable_transcript": "{base_name}_readable_transcript.txt",
    "segments": "{base_name}_segments.json",
    "prosodic": "{base_name}_prosodic_features.json",
    "visual": "{base_name}_visual_analysis.json",
    "critique": "{base_name}_sales_coaching.json",
    "summary": "{base_name}_summary.json",
}

# --- Audio Processing Configuration ---
AUDIO_PROCESSING = {
    "target_sample_rate": 16000,
    "channels": 1,
    "noise_reduction": True,
    "volume_normalization": True,
    "pitch_range": {"min": 50, "max": 400},  # Hz range for pitch analysis
    "energy_thresholds": {"low": 0.02, "high": 0.06},  # RMS energy thresholds
}

# --- Scoring Configuration ---
SCALES = {
    "performance": {"min": 1, "max": 5, "default": 3},
    "confidence": {"min": 1, "max": 5, "default": 3},
    "clarity": {"min": 1, "max": 5, "default": 3},
    "engagement": {"min": 1, "max": 5, "default": 3},
}

# --- Cultural Filler Words (Language Specific) ---
HINDI_FILLERS = [
    "अच्छा",
    "हम्म",
    "हँ",
    "हाँ",
    "नहीं",
    "मतलब",
    "यानि",
    "तो",
    "बस",
    "वो",
    "ये",
    "देखो",
    "ठीक",
    "ठीक है",
    "देखिए",
    "सुनिए",
    "समझे",
    "समझा",
    "रहा",
    "achha",
    "accha",
    "hmm",
    "haan",
    "nahi",
    "matlab",
    "yaani",
    "toh",
    "bas",
    "actually",
    "basically",
    "like",
    "you know",
    "so",
]

TAMIL_FILLERS = [
    "அச்சு",
    "ஹம்",
    "ஆமாம்",
    "இல்லை",
    "மற்றும்",
    "அல்லது",
    "இந்த",
    "அந்த",
    "நீங்கள்",
    "நான்",
    "என்ன",
    "எப்படி",
    "ஏன்",
    "எப்போது",
    "எங்கே",
]

TELUGU_FILLERS = [
    "అచ్చు",
    "హమ్మ్",
    "ఆమామ్",
    "కాదు",
    "మరియు",
    "లేదా",
    "ఈ",
    "ఆ",
    "మీరు",
    "నేను",
    "ఏమి",
    "ఎలా",
    "ఎందుకు",
    "ఎప్పుడు",
    "ఎక్కడ",
]

# Compile regex patterns for filler detection
FILLER_PATTERNS = {
    "hi": re.compile(
        r"\b(" + "|".join(re.escape(f) for f in HINDI_FILLERS) + r")\b", re.I
    ),
    "ta": re.compile(
        r"\b(" + "|".join(re.escape(f) for f in TAMIL_FILLERS) + r")\b", re.I
    ),
    "te": re.compile(
        r"\b(" + "|".join(re.escape(f) for f in TELUGU_FILLERS) + r")\b", re.I
    ),
}

# --- API Rate Limiting Configuration ---
RATE_LIMITING = {
    "vision_api": {"calls_per_minute": 15, "burst_limit": 3},
    "critique_api": {"calls_per_minute": 30, "burst_limit": 5},
    "translation_api": {"calls_per_minute": 60, "burst_limit": 10},
}

# --- Error Handling Configuration ---
ERROR_HANDLING = {
    "max_retries": 3,
    "retry_delay": 1.0,  # seconds
    "fallback_to_default": True,
    "log_errors": True,
}

# --- Development/Production Flags ---
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
PRODUCTION_MODE = os.getenv("PRODUCTION_MODE", "false").lower() == "true"

# --- Paths Configuration ---
DEFAULT_INPUT_PATH = r"C:\Users\KIIT0001\Downloads\chirpcomparison-20251013T133300Z-1-001\chirpcomparison\chirp2\HI\ZT3_CE31477\ZT3_CE31477.mp4"
DEFAULT_OUTPUT_PATH = r"C:\Users\KIIT0001\Downloads\chirpcomparison-20251013T133300Z-1-001\chirpcomparison\chirp2\HI\ZT3_CE31477"

# Create output directory if it doesn't exist
os.makedirs(DEFAULT_OUTPUT_PATH, exist_ok=True)

print(
    f"Configuration loaded for {'Production' if PRODUCTION_MODE else 'Development'} mode"
)
print(f"Supported languages: {', '.join(LANGUAGE_CONFIGS.keys())}")
print(f"Using {VISION_MODEL} for visual analysis")
print(f"Using {CRITIQUE_MODEL} for coaching feedback")

# --- KPI Logic Configuration ---
KPI_DEFINITIONS = {
    "pitch_adherence": {
        "description": "Measures how well the presenter adheres to the main topic and structure of the pitch.",
        "scoring_criteria": [
            "5: Excellent - The pitch is focused, logical, and easy to follow.",
            "4: Good - The pitch is mostly focused, with minor deviations.",
            "3: Average - The pitch is generally on topic, but with occasional digressions or omissions.",  # Softened from "some noticeable" to "occasional" for less harsh feel.
            "2: Below average - The pitch is unfocused and difficult to follow.",
            "1: Poor - The pitch is completely unstructured and off-topic.",
        ],
        "special_instructions": "Evaluate whether the presenter stays on track and if the flow of information is logical. In Indian retail contexts like Tamil Nadu, allow flexibility for relational digressions that build rapport, as long as core features are covered.",  # Added cultural nuance to avoid penalizing enthusiasm/building connections.
    },
    "confidence": {
        "description": "Assesses the presenter's self-assurance and command of the material.",
        "scoring_criteria": [
            "5: Excellent - Appears highly confident, speaks clearly and authoritatively.",
            "4: Good - Appears confident, with only minor signs of nervousness.",
            "3: Average - Appears somewhat confident, but with occasional hesitation or nervousness.",  # Softened for practicality.
            "2: Below average - Appears nervous and lacks conviction.",
            "1: Poor - Appears extremely nervous and unconvincing.",
        ],
        "special_instructions": "Consider vocal tone, pace, and body language as indicators of confidence. In high-energy Indian sales environments, faster speech may signal enthusiasm rather than nervousness—score accordingly if it maintains engagement.",  # Added to address pacing issues in your example, drawing from cultural research on expressive Indian communication.
    },
    "technical_knowledge": {
        "description": "Evaluates the presenter's understanding and explanation of the product's technical aspects.",
        "scoring_criteria": [
            "5: Excellent - Demonstrates deep technical knowledge and explains complex features clearly.",
            "4: Good - Shows good technical knowledge and explains most features well.",
            "3: Average - Shows basic technical knowledge but may overlook some explanations in a demo setting.",  # Adjusted to forgive minor omissions in live demos.
            "2: Below average - Shows limited technical knowledge and makes errors in explanations.",
            "1: Poor - Shows no technical knowledge and cannot explain the product.",
        ],
        "special_instructions": "Assess the accuracy and clarity of the technical information presented. Prioritize practical explanations over exhaustive detail, especially in relational Indian sales where customer benefits trump jargon.",  # Emphasized benefits-focus per cultural norms.
    },
    "customer_pain_points_connection": {
        "description": "Measures how well the presenter connects product features to customer needs and pain points.",
        "scoring_criteria": [
            "5: Excellent - Consistently and effectively links features to customer benefits.",
            "4: Good - Often links features to customer benefits.",
            "3: Average - Sometimes links features to customer benefits, but not consistently.",
            "2: Below average - Rarely links features to customer benefits.",
            "1: Poor - Makes no attempt to connect features to customer benefits.",
        ],
        "special_instructions": "Look for instances where the presenter explains how a feature solves a specific problem for the customer. In Tamil Nadu contexts, reward connections to everyday household concerns like energy savings or family needs.",  # Added regional relevance.
    },
    "active_demonstration": {
        "description": "Assesses how effectively the presenter uses the product in a live demonstration.",
        "scoring_criteria": [
            "5: Excellent - The demonstration is smooth, clear, and effectively showcases the product.",
            "4: Good - The demonstration is mostly effective, with minor issues.",
            "3: Average - The demonstration is okay, but could be clearer or more engaging in a busy setting.",  # Added showroom practicality.
            "2: Below average - The demonstration is confusing or poorly executed.",
            "1: Poor - The demonstration is a failure and does not work.",
        ],
        "special_instructions": "Evaluate the clarity and effectiveness of the product demonstration. Allow for natural product-focused glances or movements in hands-on retail demos.",  # Ties back to visual engagement issues.
    },
    "eye_contact": {  # No major changes—already aligns with boss's input.
        "description": "Measures how well the presenter maintains eye contact with the audience, prioritizing engagement with a customer over direct camera focus.",
        "scoring_criteria": [
            "5: Excellent - Consistent, engaging eye contact with the customer/audience, creating a strong rapport.",
            "4: Good - Mostly consistent eye contact, with only minor, brief lapses.",
            "3: Average - Eye contact is inconsistent; presenter sometimes looks away, at notes, or at the product for extended periods.",
            "2: Below average - Frequent breaks in eye contact, making the presenter appear disengaged or nervous.",
            "1: Poor - Actively avoids eye contact, reads heavily from notes, or seems disconnected from the audience.",
        ],
        "special_instructions": "Prioritize engagement with a customer in the room over direct-to-camera contact. A presenter engaging with a person is more valuable than one staring blankly at a lens. Score higher if the presenter is looking towards a person, even if off-camera. In Indian showrooms, brief product glances during demos are normal and should not heavily penalize.",  # Minor addition for practicality.
    },
    "body_language": {
        "description": "Assesses the presenter's posture, stance, and overall physical presence.",
        "scoring_criteria": [
            "5: Excellent - Open, confident, and relaxed posture; uses space effectively.",
            "4: Good - Generally good posture with minor issues like slight slouching or fidgeting.",
            "3: Average - Posture is okay, but may appear somewhat closed off, stiff, or defensive in a dynamic setting.",  # Added for retail flexibility.
            "2: Below average - Slouching, excessive fidgeting, or defensive posture that detracts from the message.",
            "1: Poor - Appears visibly uncomfortable, tense, or completely disengaged.",
        ],
        "special_instructions": "Look for an upright but natural stance. Leaning slightly forward can indicate engagement. Crossed arms or hands in pockets are negative indicators. In Tamil Nadu retail, allow for animated, relational movements that build warmth.",  # Cultural tweak for expressiveness.
    },
    "gestures": {
        "description": "Evaluates the use of hand and arm movements to emphasize points and illustrate concepts.",
        "scoring_criteria": [
            "5: Excellent - Purposeful, natural, and varied gestures that enhance the message.",
            "4: Good - Effective use of gestures, with occasional moments of stillness or repetitive movement.",
            "3: Average - Some use of gestures, but they may be small, repetitive, or not always aligned with the content.",
            "2: Below average - Gestures are distracting, nervous (e.g., fidgeting), or largely absent.",
            "1: Poor - No effective gestures; hands are kept still, hidden, or used in a distracting manner.",
        ],
        "special_instructions": "Gestures should be open and used to illustrate points. For example, using hands to show size or to count points. Avoid pointing directly at the audience. In Indian sales, enthusiastic gestures are common and should be viewed positively if they aid engagement.",  # Added to reduce harshness on "absent" gestures.
    },
    "appearance": {  # Minimal change—already strong.
        "description": "Assesses the presenter's professional attire and grooming.",
        "scoring_criteria": [
            "5: Excellent - Professional, neat, and appropriate attire and grooming for the context.",
            "4: Good - Generally professional appearance with one minor issue.",
            "3: Average - Appearance is acceptable but could be more polished or professional.",
            "2: Below average - Appearance is distracting or unprofessional.",
            "1: Poor - Appearance is highly unprofessional and detracts significantly from credibility.",
        ],
        "special_instructions": "Consider the context of the sale. A polo shirt in a showroom is acceptable, while a suit might be required in a boardroom. Focus on neatness, grooming, and appropriateness. In Tamil Nadu, culturally respectful attire (e.g., modest, regional styles) builds trust.",  # Minor cultural addition.
    },
}
