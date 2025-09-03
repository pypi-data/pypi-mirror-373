# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Core Framework Development
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r dev-requirements.txt

# Install pre-commit hooks
pre-commit install

# Install package in editable mode with optional dependencies
pip install -e ".[daily,deepgram,cartesia,openai,silero]"
```

### Testing and Code Quality
```bash
# Run tests
pip install -r test-requirements.txt
pytest

# Format code (pre-commit hook)
ruff format

# Check code quality
ruff check --select I

# Pre-commit script
./scripts/pre-commit.sh
```

### Release Management
**🚀 Smart Auto-Release System** - Automated version management and deployment

```bash
# Developer workflow (unchanged):
# 1. Make changes to src/pipecat
# 2. Create PR to dv-stage → Merge
# 3. Everything else is automatic!

# Manual version utilities (if needed):
python scripts/version-utils.py info      # Check version status
python scripts/version-utils.py check     # Verify version consistency
python scripts/version-utils.py update 0.0.75.dev123  # Manual version update
```

**How it works:**
- ✅ **Auto-detects** when `src/pipecat` changes
- ✅ **Smart versioning** - only releases when needed
- ✅ **PyPI publishing** with error handling and retries
- ✅ **Deployment coordination** with package verification
- ✅ **Zero developer overhead** - respects manual versioning

See **[docs/AUTO_RELEASE.md](docs/AUTO_RELEASE.md)** for complete documentation.

### Ringg Chatbot Development (Primary Codebase)
The main development work happens in `examples/ringg-chatbot/`, which is a production telephony chatbot system.

```bash
# Navigate to the main codebase
cd examples/ringg-chatbot

# Install dependencies
pip install -r requirements.txt

# Run the server (main entry point)
python server.py

# Run bot directly for testing
python bot.py
```

### Example Running
```bash
# Run foundational examples
cd examples/foundational
python 07-interruptible.py

# Run with specific AI services
pip install "pipecat-ai[openai,deepgram,cartesia]"
```

## Core Architecture

Pipecat is a **pipeline-based real-time AI conversation framework** for building voice-enabled, multimodal AI applications. Built around these key architectural concepts:

### Framework Philosophy
- **Real-time Processing**: Conversational interactions without noticeable delays
- **Multimodal Support**: Combines audio, video, images, and text in interactions
- **Pipeline Architecture**: Sequential frame processing with concurrent input/output handling
- **Service Orchestration**: Complex coordination of AI services, network transport, and audio processing

### Frame-Based Data Flow System
- **Frames** (`src/pipecat/frames/frames.py`) are the fundamental data units
- Frame types: `DataFrame`, `ControlFrame`, `SystemFrame`
- Specialized frames: `TextFrame`, `AudioRawFrame`, `TranscriptionFrame`, `LLMTextFrame`
- Frames flow through processors in a reactive pipeline architecture

### Pipeline Architecture
- **FrameProcessor** (`src/pipecat/processors/frame_processor.py`) - base class for all processing components
- **Pipeline** (`src/pipecat/pipeline/pipeline.py`) - linear processor chains
- **ParallelPipeline** - concurrent processing paths
- **PipelineTask** (`src/pipecat/pipeline/task.py`) - execution lifecycle management
- Bidirectional data flow: `FrameDirection.DOWNSTREAM` and `FrameDirection.UPSTREAM`

### AI Services Integration
- **AIService** base class with common functionality
- **LLMService**, **STTService**, **TTSService**, **VisionService** for different AI capabilities
- Context aggregators manage conversation state
- Function calling support with result callbacks
- Multiple providers: OpenAI, Anthropic, Google, AWS, Azure, Deepgram, ElevenLabs, etc.

### Transport Layer
- **BaseTransport** provides input/output interface
- Real-time support: WebRTC (Daily), WebSocket, telephony (Twilio, Plivo)
- **BaseInputTransport** and **BaseOutputTransport** handle media streams
- VAD (Voice Activity Detection) and turn analysis

### Serialization
- **FrameSerializer** enables protocol adaptation for different communication platforms
- Provider-specific serializers in `src/pipecat/serializers/`

## Supported AI Services

Pipecat supports extensive AI service integrations:

### Speech-to-Text (STT)
AssemblyAI, AWS Transcribe, Azure, Cartesia, Deepgram, Fal Wizper, Gladia, Google, Groq (Whisper), NVIDIA Riva, OpenAI (Whisper), SambaNova, Speechmatics, Ultravox, Whisper

### Large Language Models (LLM)
Anthropic, AWS Bedrock, Azure, Cerebras, DeepSeek, Fireworks AI, Google Gemini/Vertex AI, Grok, Groq, NVIDIA NIM, Ollama, OpenAI, OpenPipe, OpenRouter, Perplexity, Qwen, SambaNova, Together AI

### Text-to-Speech (TTS)
AWS Polly, Azure, Cartesia, Deepgram, ElevenLabs, Fish, Google, Groq, LMNT, MiniMax, Neuphonic, NVIDIA Riva, OpenAI, Piper, PlayHT, Rime, Sarvam, XTTS

### Transport & Communication
Daily (WebRTC), SmallWebRTC, FastAPI WebSocket, WebSocket Server, Tavus

### Additional Services
- **Speech-to-Speech**: AWS Nova Sonic, Gemini, OpenAI
- **Image Generation**: fal, Google Imagen, OpenAI
- **Video**: Simli, Tavus
- **Memory**: Mem0
- **Vision**: Moondream
- **Analytics**: Sentry

## Typical Data Flow Pattern

1. **Input Transport** receives audio/video/text and converts to frames
2. **Frame Processors** transform and route frames through pipeline
3. **AI Services** process frames (STT → LLM → TTS workflow)
4. **Aggregators** collect and contextualize related frames
5. **Output Transport** converts frames back to media streams

## Frame Types Reference

Based on Pipecat documentation, key frame types include:

### Base Frame Classes
- **Frame**: Base class with `id`, `name`, `pts` (presentation timestamp)
- **DataFrame**: Base for most data-carrying frames
- **SystemFrame**: System-level frames (`StartFrame`, `CancelFrame`, `ErrorFrame`, etc.)
- **ControlFrame**: Control-flow frames (`EndFrame`, `UserStartedSpeakingFrame`, etc.)

### Data Frames
- **AudioRawFrame**: Raw audio data with `sample_rate` and `num_channels`
  - Subclasses: `InputAudioRawFrame`, `OutputAudioRawFrame`, `TTSAudioRawFrame`
- **ImageRawFrame**: Image data with `size` and `format`
  - Subclasses: `InputImageRawFrame`, `VisionImageRawFrame`, `URLImageRawFrame`
- **TextFrame**: Text chunks for processing
- **TranscriptionFrame**: Speech transcriptions with `user_id`, `timestamp`, `language`
- **LLMMessagesFrame**: Message arrays for LLM processing

### System Control
- **StartFrame/EndFrame**: Pipeline lifecycle control
- **StartInterruptionFrame/StopInterruptionFrame**: User speech interruption handling
- **BotStartedSpeakingFrame/BotStoppedSpeakingFrame**: Bot speech activity
- **FunctionCallInProgressFrame/FunctionCallResultFrame**: LLM function calling

## Common Development Patterns

### Creating a New Service
- Extend appropriate base class (`AIService`, `LLMService`, `STTService`, etc.)
- Implement required abstract methods
- Handle frame processing in `process_frame()` method
- Add to `src/pipecat/services/` directory

### Building a Pipeline
```python
pipeline = Pipeline([
    transport.input(),
    stt,
    llm,
    tts,
    transport.output()
])

task = PipelineTask(pipeline)
await task.run()
```

### Adding New Frame Types
- Define in `src/pipecat/frames/frames.py`
- Extend appropriate base frame class
- Update processors to handle new frame types

## Project Structure Notes

- **`src/pipecat/`** - Core Pipecat framework code
- **`examples/ringg-chatbot/`** - **Primary development codebase** - Production telephony chatbot system
  - `server.py` - FastAPI server handling webhooks and WebSocket connections
  - `bot.py` - Main bot implementation with Pipecat pipeline
  - `utils/` - Core utilities (LLM, STT, TTS, pipeline helpers)
  - `utils/llm_functions/` - Function calling implementations (call transfer, DTMF, etc.)
  - `rag/` - RAG implementation with Weaviate
  - `templates/` - XML templates for Plivo/Twilio telephony
  - `PIPECAT_ARCHITECTURE.md` - **Deep technical analysis of Pipecat framework** (frames, pipelines, AI services)
- `examples/foundational/` - Simple examples and tutorials
- `tests/` - Unit and integration tests
- `scripts/` - Development and deployment scripts
- `docs/` - API documentation generation

## Testing Specific Components

```bash
# Test specific modules
pytest tests/test_pipeline.py
pytest tests/test_llm_service.py

# Run integration tests
pytest tests/integration/
```

## Ringg Chatbot Architecture

The `examples/ringg-chatbot/` system is a **production telephony chatbot** with these key components:

### Telephony Integration
- **Multi-provider support**: Plivo, Twilio, Exotel for voice calls
- **WebSocket streaming**: Real-time audio processing via WebSocket connections
- **XML templates**: Dynamic call flow generation for telephony providers
- **Call management**: Status callbacks, call transfer, DTMF handling

### Core Components
- **FastAPI server** (`server.py`): Handles webhooks, WebSocket connections, Redis caching
- **Bot pipeline** (`bot.py`): Pipecat-based conversation pipeline with AI services
- **Function calling**: Advanced LLM functions (call transfer, knowledge base queries, language switching)
- **RAG system**: Weaviate-based knowledge retrieval for contextual responses

### Key Features
- **Multi-language support**: Dynamic language switching during calls
- **Voicemail detection**: Automated detection and handling
- **Hold detection**: Detects when users put calls on hold
- **Backchannel processing**: Filler words and conversation flow enhancement
- **Caching system**: Redis-based TTS caching for performance
- **Audio recording**: Local and cloud-based call recording

### Dependencies
Uses specialized dependencies: `plivo`, `twilio`, `weaviate-client`, `redis`, `groq`, etc.

## Additional Resources

### Comprehensive Technical Documentation

For deep understanding of the Pipecat framework architecture:
- **`examples/ringg-chatbot/PIPECAT_ARCHITECTURE.md`** - Complete technical deep dive covering:
  - Frame system architecture (SystemFrame, DataFrame, ControlFrame hierarchy)
  - Pipeline processing patterns (sequential vs parallel)  
  - AI services integration (LLMService, STTService, TTSService)
  - Complete code flow patterns and when to use different approaches

## Performance & Async Requirements

### Critical Performance Considerations

**⚡ Async Processing - Never Block the Event Loop**
- **MANDATORY**: All operations must be async and non-blocking
- Use `await` for I/O operations (file reads, network calls, database queries)
- Use `asyncio.create_task()` or `asyncio.gather()` for concurrent operations
- Never use blocking calls like `time.sleep()` - use `asyncio.sleep()` instead
- Avoid synchronous file I/O - use `aiofiles` or async equivalents
- Database operations must use async drivers (asyncpg, aiomysql, etc.)

**🎯 Ultra-Low Latency Voice AI**
- **Target**: Minimize time from "user stops speaking" → "bot starts speaking"
- **Critical Path**: STT processing → LLM response → TTS generation → audio output
- Every millisecond matters for natural conversation flow
- Optimize each pipeline stage for minimal latency:
  - STT: Use streaming transcription services (Deepgram, AssemblyAI)
  - LLM: Choose fast models, optimize prompts, use streaming responses
  - TTS: Cache common responses, use low-latency providers (Cartesia, ElevenLabs)
  - Audio: Minimize buffering, use real-time transport protocols

### Async Best Practices
```python
# ✅ Good - Non-blocking async operations
async def process_audio(audio_data):
    tasks = [
        asyncio.create_task(stt_service.transcribe(audio_data)),
        asyncio.create_task(cache.get(cache_key))
    ]
    results = await asyncio.gather(*tasks)
    return results

# ❌ Bad - Blocking operations that freeze the event loop
def process_audio_bad(audio_data):
    time.sleep(0.1)  # Blocks entire event loop!
    response = requests.get(url)  # Synchronous HTTP call
    with open('file.txt', 'r') as f:  # Synchronous file I/O
        data = f.read()
```

## Common Gotchas

- **For framework development**: Always activate virtual environment and use `pip install -e ".[provider,...]"`
- **For ringg-chatbot**: Navigate to `examples/ringg-chatbot/` and install with `pip install -r requirements.txt`
- Pre-commit hooks enforce code formatting with Ruff
- Frame processors must handle both downstream and upstream flow
- Pipeline lifecycle: StartFrame → processing → EndFrame/StopFrame
- **Telephony**: WebSocket connections require proper call_id tracking and cleanup
- **Async**: Never block the event loop - use async/await for all I/O operations
- **Latency**: Voice AI requires sub-second response times - optimize every pipeline stage