"""
Agent configuration — all the knobs in one place.

When you want to try a different voice, model, or temperature, edit here.
Don't sprinkle magic strings across the codebase.
"""

# --- Gemini Live model settings ---

# Available models (Google AI Studio free tier):
#   gemini-2.0-flash-exp   - stable, recommended for this demo
#   gemini-2.5-flash-native-audio-preview - newer, more natural prosody
GEMINI_MODEL = "gemini-2.5-flash-native-audio-latest"

# Available voices: "Aoede", "Puck", "Charon", "Kore", "Fenrir"
# Aoede = warmer female; Puck = playful; Charon = deeper male.
GEMINI_VOICE = "Aoede"

# Lower = more deterministic. We want accurate numbers, not creativity.
GEMINI_TEMPERATURE = 0.6


# --- Logging ---

LOG_LEVEL = "INFO"


# --- Demo metadata ---

# Shown in greeting and refusal responses.
ASSISTANT_NAME = "Meera"
