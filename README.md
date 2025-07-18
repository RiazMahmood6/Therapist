# Voice-Enabled AI Therapist 🎤🧠

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v2.0+-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

A sophisticated Flask-based web application that provides AI-powered therapeutic conversations with advanced voice capabilities, multiple personality modes, and comprehensive safety features.

## 📋 Table of Contents

- [Demo](#-demo)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [Configuration](#-configuration)
- [Project Structure](#-project-structure)
- [API Endpoints](#-api-endpoints)
- [Security](#-security-considerations)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 📸 Demo

> **Note**: Add screenshots of your application here

![Main Interface](path/to/screenshot1.png)
*Main chat interface with voice controls*

![Voice Recording](path/to/screenshot2.png) 
*Voice recording in action*

## ✨ Features

### 🎙️ Voice Capabilities
- **Speech-to-Text**: Real-time voice transcription using OpenAI Whisper
- **Text-to-Speech**: AI-generated voice responses with natural-sounding speech
- **Voice Controls**: Interactive microphone interface with visual feedback
- **Audio Playback**: Automatic playback of AI responses with audio controls

### 🤖 AI Models & Personalities
- **Multiple AI Models**: Choose between GPT-4 (OpenAI) and DeepSeek (via OpenRouter)
- **Personality Presets**: 
  - **Empathetic**: Warm, caring responses with emotional depth
  - **Professional**: Balanced, clinical therapeutic approach
  - **Casual**: Relaxed, friendly conversational style
- **Context-Aware**: Maintains conversation history and context throughout sessions

### 🛡️ Safety & Security
- **Harmful Content Filter**: Automatically filters inappropriate or triggering content
- **Crisis Detection**: Identifies potential crisis situations and provides appropriate resources
- **Professional Referral**: Suggests professional help when needed
- **Session Management**: Secure session handling with conversation isolation

### ⚙️ Advanced Features
- **Conversation Summarization**: Automatic summarization when approaching token limits
- **Configurable Response Delays**: Customizable AI response timing
- **Token Management**: Efficient token usage with smart conversation truncation
- **Real-time Transcription**: Live audio processing with status feedback
- **Responsive Design**: Mobile-friendly interface with adaptive layouts

## 🏗️ Technology Stack

- **Backend**: Flask (Python)
- **AI Models**: OpenAI GPT-4, DeepSeek (via OpenRouter)
- **Speech Processing**: OpenAI Whisper API, OpenAI TTS
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Audio Processing**: Web Audio API, MediaRecorder API
- **Session Management**: Flask Sessions
- **Environment Management**: Python-dotenv

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- OpenRouter API key (for DeepSeek)
- Modern web browser with microphone support
- HTTPS connection (required for microphone access in production)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR-USERNAME/voice-ai-therapist.git
cd voice-ai-therapist
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

Create a `requirements.txt` file with the following content:
```txt
flask==2.3.3
requests==2.31.0
python-dotenv==1.0.0
openai==1.3.0
pathlib2==2.3.7
```

Or install manually:
```bash
pip install flask requests python-dotenv openai pathlib tempfile uuid
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 5. Create Required Directories
```bash
mkdir -p static/audio
mkdir -p templates
```

### 6. Add HTML Template
Place the provided HTML file in the `templates/` directory as `index.html`.

## ⚡ Quick Start

### 1. Run the Application
```bash
python app.py
```

### 2. Access the Interface
Open your browser and navigate to:
```
http://localhost:5000
```

### 3. Enable Microphone
Allow microphone access when prompted by your browser.

### 4. Start Chatting
- **Text Input**: Type your message and click "Send"
- **Voice Input**: Click the microphone button, speak, then click again to stop
- **Settings**: Adjust AI model, personality, and safety features as needed

## 🎯 Usage Guide

### Voice Interaction
1. **Start Recording**: Click the microphone button (turns red while recording)
2. **Stop Recording**: Click the microphone button again
3. **Processing**: Wait for transcription (button shows loading spinner)
4. **Auto-Send**: Transcribed text is automatically sent to the AI

### Chat Controls
- **Model Selection**: Choose between GPT-4 and DeepSeek
- **Personality**: Select empathetic, professional, or casual mode
- **Response Delay**: Adjust AI response timing (0-5000ms)
- **Safety Features**: Toggle content filtering, crisis detection, and professional referrals

### Session Management
- **Conversation History**: Automatically maintained during session
- **Clear History**: Reset conversation using the "Clear Conversation" button
- **Session Isolation**: Each browser session maintains separate conversation history

## 🔧 Configuration

### API Keys
Ensure your `.env` file contains valid API keys:
- **OpenAI**: Required for GPT-4, Whisper, and TTS
- **OpenRouter**: Required for DeepSeek model access

### Model Settings
```python
# Modify these in app.py
PERSONALITY_PRESETS = {
    "custom": "Your custom personality prompt here..."
}

# Token limits
token_limit = 8000  # GPT-4
token_limit = 4000  # DeepSeek
```

### Voice Settings
```python
# TTS Voice options (in generate_speech function)
voice="coral"  # Options: alloy, ash, ballad, coral, echo, fable, onyx, nova, sage, shimmer, verse
```

## 📁 Project Structure

```
voice-ai-therapist/
├── app.py                 # Main Flask application
├── .env                   # Environment variables (create this)
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Frontend interface
├── static/
│   └── audio/            # Generated audio files
└── README.md            # This file
```

## 🔌 API Endpoints

### `/` (GET)
- **Description**: Main application interface
- **Returns**: HTML template with chat interface

### `/chat` (POST)
- **Description**: Process chat messages and return AI responses
- **Body**: 
  ```json
  {
    "message": "User message",
    "model": "gpt-4|deepseek",
    "personality": "empathetic|professional|casual",
    "response_delay": 700,
    "filter_harmful": false,
    "detect_crisis": false,
    "suggest_professional": false
  }
  ```
- **Returns**: AI response with optional audio URL

### `/transcribe` (POST)
- **Description**: Convert audio to text using Whisper
- **Body**: Form data with audio file
- **Returns**: Transcribed text

### `/clear_history` (POST)
- **Description**: Clear conversation history for current session
- **Returns**: Success confirmation

### `/static/audio/<filename>` (GET)
- **Description**: Serve generated audio files
- **Returns**: Audio file (MP3 format)

## 🔒 Security Considerations

- **API Key Protection**: Store API keys in environment variables
- **Session Security**: Unique session IDs with secure random generation
- **Input Validation**: Sanitize user inputs before processing
- **HTTPS**: Use HTTPS in production for microphone access
- **Content Filtering**: Enable safety features for public deployments

## 🐛 Troubleshooting

### Common Issues

**Microphone Not Working**
- Ensure HTTPS connection in production
- Check browser microphone permissions
- Verify Web Audio API support

**API Errors**
- Verify API keys in `.env` file
- Check API rate limits and quotas
- Ensure proper network connectivity

**Audio Playback Issues**
- Check browser audio permissions
- Verify audio file generation in `static/audio/`
- Try different browsers for compatibility

**Memory Issues**
- Monitor conversation history length
- Adjust token limits for your use case
- Clear sessions periodically

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] Voice customization options
- [ ] Conversation export functionality
- [ ] Advanced analytics and insights
- [ ] Integration with calendar systems
- [ ] Mood tracking and visualization
- [ ] Therapist dashboard for monitoring

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### How to Contribute

1. **Fork** the repository
2. **Clone** your fork locally
   ```bash
   git clone https://github.com/YOUR-USERNAME/voice-ai-therapist.git
   ```
3. **Create** a feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```
4. **Make** your changes
5. **Test** your changes thoroughly
6. **Commit** your changes
   ```bash
   git commit -m 'Add amazing feature'
   ```
7. **Push** to the branch
   ```bash
   git push origin feature/amazing-feature
   ```
8. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/voice-ai-therapist.git
cd voice-ai-therapist

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
pip install -r requirements-dev.txt  # If you have dev dependencies

# Run tests
python -m pytest

# Start development server
python app.py
```

## ⭐ Show Your Support

Give a ⭐️ if this project helped you!

[![GitHub stars](https://img.shields.io/github/stars/YOUR-USERNAME/voice-ai-therapist.svg?style=social&label=Star)](https://github.com/YOUR-USERNAME/voice-ai-therapist)
[![GitHub forks](https://img.shields.io/github/forks/YOUR-USERNAME/voice-ai-therapist.svg?style=social&label=Fork)](https://github.com/YOUR-USERNAME/voice-ai-therapist/fork)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This application is for educational and research purposes. It is not a replacement for professional mental health services. If you're experiencing a mental health crisis, please contact emergency services or a qualified mental health professional immediately.

## 🆘 Emergency Resources

- **National Suicide Prevention Lifeline**: 988
- **Crisis Text Line**: Text HOME to 741741
- **International Association for Suicide Prevention**: https://www.iasp.info/resources/Crisis_Centres/

## 📞 Support

For technical support or questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation

---

**Built with ❤️ for mental health awareness and AI-assisted therapy research.**
