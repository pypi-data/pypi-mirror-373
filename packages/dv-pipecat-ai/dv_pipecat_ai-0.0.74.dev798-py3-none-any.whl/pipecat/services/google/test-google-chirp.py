import asyncio
import os

from pipecat.frames.frames import TTSAudioRawFrame
from pipecat.services.google.tts import GoogleTTSService


async def test_chirp_tts():
    # Get credentials from environment variable
    credentials_path = (
        "/Users/kalicharanvemuru/Documents/Code/pipecat/examples/ringg-chatbot/creds.json"
    )

    if not credentials_path or not os.path.exists(credentials_path):
        raise ValueError(
            "Please set GOOGLE_APPLICATION_CREDENTIALS environment variable to your service account key file"
        )

    # Initialize the TTS service with Chirp voice
    tts = GoogleTTSService(
        credentials_path=credentials_path,
        voice_id="en-US-Chirp3-HD-Charon",  # Using Chirp3 HD Charon voice
        sample_rate=24000,
    )

    # Test text
    test_text = "Hello, this is a test of the Google TTS service with Chirp voice."

    print(f"Testing TTS with text: {test_text}")

    # Generate speech
    try:
        async for frame in tts.run_tts(test_text):
            if isinstance(frame, TTSAudioRawFrame):
                print(f"Received audio chunk of size: {len(frame.audio)} bytes")
            else:
                print(f"Received frame: {frame.__class__.__name__}")

        print("TTS generation completed successfully!")
    except Exception as e:
        print(f"Error during TTS generation: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_chirp_tts())
