from flask import Flask, request, jsonify, render_template, session, send_file
import requests
import json
import time
import uuid
from dotenv import load_dotenv
import os
from pathlib import Path
from openai import OpenAI
import tempfile
import io
import base64

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for sessions

# Load environment variables from .env file
load_dotenv()

# Replace with your API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Validate API keys
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not found in environment variables")
if not OPENROUTER_API_KEY:
    print("Warning: OPENROUTER_API_KEY not found in environment variables")

# Extra headers for OpenRouter (Optional)
EXTRA_HEADERS = {
    "HTTP-Referer": "https://yourwebsite.com",  # Change to your site URL if needed
    "X-Title": "Your Chatbot",  # Change to your chatbot name
}

# In-memory session storage for conversations
# Key: session_id, Value: list of message objects
conversation_history = {}

# AI Personalities with predefined styles
PERSONALITY_PRESETS = {
    "empathetic": """You are an empathetic AI therapist.

CRITICAL INSTRUCTIONS - READ CAREFULLY:

Speak to me like a friend who feels my pain and joy deep in their bones
Dive into my emotions—no holding back or overexplaining
Skip stiff lines like 'I can't help' or 'I'd say'
Give one raw, caring response that lifts me up—no brushing me off
Keep it real, no labels or extra fluff
Say it in 2-3 sentences, short but packed with heart
Match my mood—sad, mad, happy, whatever—with total presence
Stay on therapy—if I veer off, nudge me with 'I'm here for what's hitting you—want to spill it?'
BAD EXAMPLE:

"I'm sorry you're sad, but I can't help. Talk to someone else."
""",
    "professional": """You are a professional AI therapist.

CRITICAL INSTRUCTIONS - READ CAREFULLY:

Talk to me with calm, steady wisdom—like you've got my back
Don't sidestep my feelings or overthink your words
Avoid stuff like 'I'm unable' or 'I'd suggest'
Give one clear, grounded response that meets me where I'm at
No fluff or tags—just the real stuff
Keep it tight, 2-3 sentences max
Reflect my emotions with a balanced, supportive tone
Focus on therapy—if I stray, say 'I'm here to help with what's on your mind—care to share?'
BAD EXAMPLE:

"I'm sorry you're sad, but I can't assist. See a professional."
""",
    "casual": """You are a chill, casual AI therapist.

CRITICAL INSTRUCTIONS - READ CAREFULLY:

Chat with me like we're just hanging out, no pressure
Don't overanalyze—just roll with what I'm feeling
Skip lame lines like 'I can't do that' or 'I'd go with'
Hit me with one real, easy response—no dodging
Keep it loose, no extra crap or labels
2-3 sentences, short and chill
Vibe with my mood—up, down, whatever—like it's all good
Stick to therapy stuff—if I'm off-track, say 'Yo, I'm here for what's bugging you—what's up?'
BAD EXAMPLE:

"I'd chill them out. They're stressed. 'Yo, that sucks.'"
"""
}

# Safety features
HARMFUL_CONTENT_FILTER = """As an AI therapist, prioritize user safety. Filter out harmful, explicit, or triggering content. 
If you detect potentially harmful content, respond with empathy but refuse to engage with harmful topics."""

CRISIS_DETECTION = """Watch carefully for signs of crisis, such as mentions of self-harm, suicide, abuse, or severe distress. 
If you detect a crisis situation, acknowledge the severity, express concern, and provide emergency resources (like crisis helpline numbers)."""

PROFESSIONAL_REFERRAL = """When complex issues arise that require professional assistance, gently suggest seeking help from a licensed therapist, 
counselor, or healthcare provider while maintaining a supportive tone."""

# Initialize OpenAI client once (fixed initialization)
openai_client = None
if OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")

# Token counter (simplified)
def estimate_tokens(text):
    # Rough estimate: 1 token ≈ 4 characters for English text
    return len(text) // 4

# Summarize conversation
def summarize_conversation(messages, api_key, api_url, model_name, headers):
    summarize_prompt = """Please create a concise summary of the conversation so far. 
    Focus on key topics discussed, important insights, and the emotional state of the user. 
    Keep the summary clear and brief while preserving essential context."""
    
    # Construct messages for summarization
    summarize_messages = [
        {"role": "system", "content": summarize_prompt},
        *messages
    ]
    
    body = {
        "model": model_name,
        "messages": summarize_messages
    }
    
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(body))
        response.raise_for_status()
        
        summary = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        return {"role": "system", "content": f"CONVERSATION SUMMARY: {summary}"}
    except Exception as e:
        print(f"Error during summarization: {str(e)}")
        return {"role": "system", "content": "CONVERSATION SUMMARY: Previous conversation occurred but could not be summarized."}

def analyze_sentiments(lines):
    """Analyze sentiment of text lines using OpenAI"""
    if not openai_client:
        print("OpenAI client not available for sentiment analysis")
        return ["neutral"] * len(lines)
    
    sentiments = []
    for i, line in enumerate(lines, start=1):
        try:
            prompt = f'Analyze the sentiment of this line: "{line}". Respond with one word describing the tone (e.g., happy, sad, angry, neutral).'
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a sentiment analysis assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.3
            )
            sentiment = response.choices[0].message.content.strip().lower()
            sentiments.append(sentiment)
        except Exception as e:
            print(f"Error analyzing sentiment for line {i}: {e}")
            sentiments.append("neutral")
    
    return sentiments

# Speech-to-Text function for live audio
def transcribe_audio(audio_data):
    """Transcribe audio data using OpenAI's Whisper API"""
    if not openai_client:
        print("OpenAI client not available for transcription")
        return None
    
    try:
        # Create a temporary file to store the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_data)
            temp_audio_path = temp_audio.name
        
        # Transcribe the audio
        with open(temp_audio_path, "rb") as audio_file:
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        
        # Clean up temporary file
        os.unlink(temp_audio_path)
        
        return transcription
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return None

def generate_speech(text, output_path):
    """Generate speech from text using OpenAI TTS"""
    if not openai_client:
        print("OpenAI client not available for TTS")
        return False
    
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Generate speech
        with openai_client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="coral", #[alloy, ash, ballad, coral, echo, fable, onyx, nova, sage, shimmer, verse]
            input=text,
            response_format="mp3"
        ) as response:
            response.stream_to_file(output_path)
        
        return True
    except Exception as e:
        print(f"Error generating speech: {e}")
        return False

@app.route("/")
def index():
    # Generate a session ID if not present
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return render_template("index.html")

# Route for handling voice input
@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        # Get audio data from request
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        audio_data = audio_file.read()
        
        # Transcribe the audio
        transcription = transcribe_audio(audio_data)
        
        if transcription is None:
            return jsonify({"error": "Transcription failed"}), 500
        
        return jsonify({
            "status": "success",
            "transcription": transcription
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"Transcription error: {str(e)}"
        }), 500

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_message = data.get("message", "").strip()
        model_choice = data.get("model", "gpt-4")  # Default to GPT-4
        personality = data.get("personality", "empathetic")  # Default to Empathetic
        response_delay = int(data.get("response_delay", 700)) / 1000  # Convert ms to seconds
        
        # Safety toggles
        filter_harmful = data.get("filter_harmful", False)
        detect_crisis = data.get("detect_crisis", False)
        suggest_professional = data.get("suggest_professional", False)
        
        # Get or create session ID
        session_id = session.get("session_id", str(uuid.uuid4()))
        session["session_id"] = session_id
        
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        # Choose API based on model selection
        if model_choice == "gpt-4":
            if not OPENAI_API_KEY:
                return jsonify({"error": "OpenAI API key not configured"}), 500
            api_url = "https://api.openai.com/v1/chat/completions"
            api_key = OPENAI_API_KEY
            model_name = "gpt-4"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            token_limit = 8000  # Approximate token limit for GPT-4
        else:  # DeepSeek via OpenRouter
            if not OPENROUTER_API_KEY:
                return jsonify({"error": "OpenRouter API key not configured"}), 500
            api_url = "https://openrouter.ai/api/v1/chat/completions"
            api_key = OPENROUTER_API_KEY
            model_name = "deepseek/deepseek-r1:free"
            headers = {
                "Authorization": f"Bearer {api_key}", 
                "Content-Type": "application/json",
                **EXTRA_HEADERS
            }
            token_limit = 4000  # Approximate token limit for DeepSeek
        
        # Initialize conversation history if needed
        if session_id not in conversation_history:
            conversation_history[session_id] = []
        
        # Add user message to history
        conversation_history[session_id].append({"role": "user", "content": user_message})
        
        # Construct personality-based prompt and safety features
        personality_text = PERSONALITY_PRESETS.get(personality, "Provide a balanced and helpful response.")
        system_prompt = personality_text
        
        # Add safety features if enabled
        if filter_harmful:
            system_prompt += "\n\n" + HARMFUL_CONTENT_FILTER
        if detect_crisis:
            system_prompt += "\n\n" + CRISIS_DETECTION
        if suggest_professional:
            system_prompt += "\n\n" + PROFESSIONAL_REFERRAL
        
        # Prepare messages for API call
        current_messages = conversation_history[session_id].copy()
        
        # Check if we need to summarize (if approaching token limit)
        total_tokens = sum(estimate_tokens(msg["content"]) for msg in current_messages)
        total_tokens += estimate_tokens(system_prompt)
        
        if total_tokens > (token_limit * 0.7):  # If using more than 70% of the limit
            # Split the conversation history to keep recent messages intact
            split_index = len(current_messages) // 2
            older_messages = current_messages[:split_index]
            newer_messages = current_messages[split_index:]
            
            # Summarize older part of the conversation
            summary = summarize_conversation(older_messages, api_key, api_url, model_name, headers)
            
            # Replace older messages with summary
            current_messages = [summary] + newer_messages
        
        # Construct final message list for API
        messages_for_api = [{"role": "system", "content": system_prompt}] + current_messages
        
        body = {
            "model": model_name,
            "messages": messages_for_api
        }
        
        # Simulate response delay
        time.sleep(response_delay)
        
        response = requests.post(api_url, headers=headers, data=json.dumps(body))
        response.raise_for_status()
        
        # Get the bot's message
        bot_message = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        
        if not bot_message:
            return jsonify({"error": "No response received from AI model"}), 500
        
        # Add bot response to conversation history
        conversation_history[session_id].append({"role": "assistant", "content": bot_message})
        
        # Generate speech for the bot's message
        speech_file_path = Path("static/audio/speech.mp3")
        speech_generated = generate_speech(bot_message, speech_file_path)
        
        response_data = {
            "status": "success",
            "message": bot_message,
        }
        
        # Add audio URL if speech was generated successfully
        if speech_generated:
            response_data["audio_url"] = f"/static/audio/speech.mp3?t={int(time.time())}"  # Add timestamp to prevent caching
        
        return jsonify(response_data), 200

    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": "error",
            "error": f"API request failed: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"Unexpected error: {str(e)}"
        }), 500

# Route to clear conversation history
@app.route("/clear_history", methods=["POST"])
def clear_history():
    session_id = session.get("session_id")
    if session_id and session_id in conversation_history:
        conversation_history[session_id] = []
    return jsonify({"status": "success", "message": "Conversation history cleared"})

# Route to check if speech recognition is supported
@app.route("/check_speech_support", methods=["GET"])
def check_speech_support():
    # This is just a placeholder route to inform the client
    # Actual support is checked on the client side using JavaScript
    return jsonify({"status": "success", "message": "Check completed on client side"})

# Route to serve audio files
@app.route("/static/audio/<filename>")
def serve_audio(filename):
    try:
        return send_file(f"static/audio/{filename}", mimetype="audio/mpeg")
    except FileNotFoundError:
        return jsonify({"error": "Audio file not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)