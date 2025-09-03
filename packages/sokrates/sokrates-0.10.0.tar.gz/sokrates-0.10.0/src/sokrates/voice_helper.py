# This script provides utilities for voice interaction, including
# audio recording, playback, and speech-to-text transcription using
# the Whisper model. It integrates with LLM API for voice-based chat
# and uses `pyaudio` for audio input/output.

import os
import time
import re
import asyncio
import logging
import sys
import tempfile
import traceback

# debug
import threading

from enum import Enum
from .colors import Colors
from .output_printer import OutputPrinter
from pathlib import Path

# Configure logging
logging.basicConfig(filename='sokrates_voice.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

DEFAULT_WHISPER_LANGUAGE = 'en'

# Try to import voice libs, but don't fail if they are not available
try:
    import whisper
    import pyaudio
    import wave
    VOICE_MODE_AVAILABLE = True
except ImportError:
    VOICE_MODE_AVAILABLE = False

class WhisperModel(Enum):
    """
    Enum for available Whisper models.
    
    Attributes:
        BASE (str): The base model size
        TINY (str): The tiny model size  
        MEDIUM (str): The medium model size
        LARGE (str): The large model size
    
    This enum defines the available models that can be used for speech-to-text transcription.
    """
    BASE = "base"
    TINY = "tiny"
    MEDIUM = "medium"
    LARGE = "large"

class AudioRecorder:
    """
    Handles audio recording and saving to a WAV file.
    """
    def __init__(self, model: str = WhisperModel.BASE.value):
        """
        Initializes the AudioRecorder.

        Args:
            model (str): The Whisper model to use for speech-to-text. Defaults to "base".
        """
        self.chunk = 1024
        self.sample_format = pyaudio.paInt16 if VOICE_MODE_AVAILABLE else None
        self.channels = 1
        self.fs = 44100
        self.recording = False
        self.frames = []
        self.speech_to_text_model = model
        self.acknowledge_signal_filepath = str(Path(f"{Path(__file__).parent.resolve()}/../assets/signal.wav").resolve())
        
    def record_audio(self):
        """
        Records audio from the microphone until `self.recording` is set to False.
        """
        if not VOICE_MODE_AVAILABLE:
            OutputPrinter.print_error("Voice mode is not available. Audio recording is not possible.")
            return

        p = pyaudio.PyAudio()
        stream = p.open(format=self.sample_format,
                      channels=self.channels,
                      rate=self.fs,
                      frames_per_buffer=self.chunk,
                      input=True)
        
        self.frames = []
        while self.recording:
            data = stream.read(self.chunk)
            self.frames.append(data)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
    
    def save_recording(self, filename: str):
        """
        Saves the recorded audio frames to a WAV file.

        Args:
            filename (str): The path to the output WAV file.
        """
        if not VOICE_MODE_AVAILABLE:
            OutputPrinter.print_error("Voice mode is not available. Audio recording is not possible.")
            return

        p = pyaudio.PyAudio()
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(p.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        p.terminate()

def play_audio_file(filename: str):
    """
    Plays an audio file.

    Args:
        filename (str): The path to the audio file to play.
    """
    if not VOICE_MODE_AVAILABLE:
        OutputPrinter.print_error("Voice mode is not available. Audio playback is not possible.")
        return

    chunk = 1024
    wf = wave.open(filename, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)
    stream.stop_stream()
    stream.close()
    p.terminate()

def play_audio_file_interruptible(filename: str):
    """
    Plays an audio file that can be interrupted by pressing Enter.

    Args:
        filename (str): The path to the audio file to play.
    """
    if not VOICE_MODE_AVAILABLE:
        OutputPrinter.print_error("Voice mode is not available. Audio playback is not possible.")
        return

    import threading
    import queue

    # Create a queue to signal when to stop playback
    stop_queue = queue.Queue()
    
    def wait_for_enter():
        """
        Waits for the Enter key to be pressed and signals to stop audio playback.
        
        This function is used in interruptible audio playback operations to allow
        the user to stop playback manually.
        """
        input()
        stop_queue.put(True)
        OutputPrinter.print(f"{Colors.YELLOW}Audio playback stopped by user.{Colors.RESET}")

    # Start a thread to wait for Enter key
    input_thread = threading.Thread(target=wait_for_enter)
    input_thread.daemon = True
    input_thread.start()

    chunk = 1024
    wf = wave.open(filename, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)
    
    try:
        data = wf.readframes(chunk)
        while data and stop_queue.empty():
            stream.write(data)
            data = wf.readframes(chunk)
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf.close()

def handle_talk_command(conversation_history: list, refiner):
    """
    Handles the /talk command by converting the last LLM response to speech and playing it.
    
    Args:
        conversation_history (list): A list of message dictionaries representing the conversation history.
        refiner: An instance of PromptRefiner for cleaning LLM responses.
        
    Returns:
        bool: True if the command was handled successfully, False otherwise.
    """
    # Check if we have a recent LLM response to play
    if len(conversation_history) >= 2:
        # Get the last LLM response (assistant message)
        last_response = None
        for message in reversed(conversation_history):
            if message["role"] == "assistant":
                last_response = message["content"]
                break
        
        if last_response:
            # Play the last response as synthesized speech
            OutputPrinter.print("Playing the last LLM response as synthesized speech...")
            OutputPrinter.print(f"{Colors.YELLOW}Press Enter to stop the audio playback.{Colors.RESET}")
            try:
                # Import TextToSpeech class
                from sokrates.text_to_speech import TextToSpeech
                # Initialize TTS instance
                tts = TextToSpeech()
                
                # Filter out the think block
                tts_text = refiner.clean_response(last_response)

                # Create a temporary file for the audio
                temp_audio_file = Path("temp_response.wav")
                
                # Convert text to speech and save to file
                audio_data = tts.tts_to_file(tts_text, str(temp_audio_file))
                
                # Play the audio file with interruptible functionality
                play_audio_file_interruptible(str(temp_audio_file))
                
                # Clean up the temporary file
                temp_audio_file.unlink(missing_ok=True)
                
                OutputPrinter.print("Last LLM response played successfully.")
                return True
            except Exception as e:
                OutputPrinter.print_error(f"Failed to play the last LLM response: {e}")
                return False
    else:
        OutputPrinter.print_error("No LLM response available to play. Please have a conversation first.")
        return False

async def run_voice_chat(llm_api, model: str, temperature: float, max_tokens: int, conversation_history: list, log_files: list, hide_reasoning: bool, verbose: bool, refiner, whisper_model_language: str = DEFAULT_WHISPER_LANGUAGE):
    """
    Runs a voice-based chat interaction with an LLM.

    Args:
        llm_api: An instance of LLMApi for interacting with the LLM.
        model (str): The LLM model to use for chat.
        temperature (float): The sampling temperature for LLM responses.
        max_tokens (int): The maximum number of tokens for LLM responses.
        conversation_history (list): A list of message dictionaries representing the conversation history.
        log_files (list): A list of file objects to log the conversation.
        hide_reasoning (bool): If True, hides LLM's internal reasoning (e.g., <tool_call> tags).
        verbose (bool): If True, enables verbose output.
        refiner: An instance of PromptRefiner for cleaning LLM responses.
        whisper_model_language: The language to use for voice input and according transcription (e.g. en, de, ...)
    """
    # Check if pyaudio is available
    if not VOICE_MODE_AVAILABLE:
        OutputPrinter.print_error("Voice mode is not available. Voice functionality is not available.")
        return "voice_disabled"

    recorder = AudioRecorder()
    OutputPrinter.print("Loading Whisper model...")
    try:
        whisper_model = whisper.load_model(recorder.speech_to_text_model)
    except Exception as e:
        OutputPrinter.print_error(f"Failed to load Whisper model: {e}")
        OutputPrinter.print_error("Please ensure you have installed the necessary Whisper dependencies.")
        OutputPrinter.print_error("You might need to run: pip install 'whisper-cpp-python[all]' or 'pip install openai-whisper'")
        return # Exit if model cannot be loaded
        
    # Main loop for voice chat
    while True:
        # Get user input
        user_input = input("Enter command (/talk, /voice, /add <filepath>, or press Enter to record): ").strip()
        
        # Check if we have a recent LLM response to play
        if len(conversation_history) >= 2:
            # Get the last LLM response (assistant message)
            last_response = None
            for message in reversed(conversation_history):
                if message["role"] == "assistant":
                    last_response = message["content"]
                    break
            
            # Process user input based on the command
            if last_response and user_input == "/talk":
                # Play the last response as synthesized speech
                OutputPrinter.print("Playing the last LLM response as synthesized speech...")
                OutputPrinter.print(f"{Colors.YELLOW}Press Enter to stop the audio playback.{Colors.RESET}")
                try:
                    # Import TextToSpeech class
                    from sokrates.text_to_speech import TextToSpeech
                    # Initialize TTS instance
                    tts = TextToSpeech()
                    
                    # Filter out the think block
                    tts_text = refiner.clean_response(last_response)

                    # Create a temporary file for the audio
                    temp_audio_file = Path("temp_response.wav")
                    
                    # Convert text to speech and save to file
                    audio_data = tts.tts_to_file(tts_text, str(temp_audio_file))
                    
                    # Play the audio file with interruptible functionality
                    play_audio_file_interruptible(str(temp_audio_file))
                    
                    # Clean up the temporary file
                    temp_audio_file.unlink(missing_ok=True)
                    
                    OutputPrinter.print("Last LLM response played successfully.")
                except Exception as e:
                    OutputPrinter.print_error(f"Failed to play the last LLM response: {e}")
                continue  # Skip to next iteration
        
        # Process user commands
        if user_input == "exit":
            return "exit"  # Signal to exit the voice chat
        elif user_input == "/voice":
            return "toggle_voice" # Signal to toggle voice mode
        elif user_input.startswith("/add "):
            filepath = user_input[5:].strip()
            return "add_context", filepath # Signal to add context
        elif user_input == "": # User pressed Enter to record
            OutputPrinter.print(f"{Colors.BRIGHT_RED}{Colors.BOLD}║Recording... Press Enter to stop.║{Colors.RESET}")
            recorder.recording = True
            record_thread = threading.Thread(target=recorder.record_audio)
            record_thread.start()
            
            input() # Wait for Enter key
            
            play_audio_file(recorder.acknowledge_signal_filepath)
            
            recorder.recording = False
            record_thread.join()
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                temp_filename = tmp_file.name
            
            recorder.save_recording(temp_filename)
            
            start_time = time.time()
            
            OutputPrinter.print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}⟳ Transcribing...{Colors.RESET}")
            try:
                result = whisper_model.transcribe(temp_filename, language=whisper_model_language)
            except Exception as e:
                OutputPrinter.print_error(f"Error during transcription: {e}")
                logging.error(f"Error during transcription: {traceback.format_exc()}")
                os.unlink(temp_filename)
                continue # Continue to next loop iteration
                
            transcribed_text = result['text']
            OutputPrinter.print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}✓ Recognized text:{Colors.RESET}")
            OutputPrinter.print(f"{Colors.CYAN}{Colors.BOLD}{transcribed_text}{Colors.RESET}")
            
            end_time = time.time()
            duration = end_time - start_time
            OutputPrinter.print(f"{Colors.CYAN}{Colors.BOLD}Transcription Duration: {duration:.2f} seconds{Colors.RESET}")
            
            if transcribed_text:
                conversation_history.append({"role": "user", "content": transcribed_text})
                
                OutputPrinter.print("Sending request to LLM...")
                    
                response_content_full = llm_api.chat_completion(
                    messages=conversation_history,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                if response_content_full:
                    for lf in log_files:
                        lf.write(f"User (Voice): {transcribed_text}\n---\n")
                        lf.write(f"LLM: {response_content_full}\n---\n")
                        lf.flush()
                        
                    display_content = response_content_full
                    play_audio_file(recorder.acknowledge_signal_filepath)
                    
                    # Extract and colorize  (^)( block for display if not hidden
                    think_match = re.search(r'\(\)(.*?)\(\)', display_content, re.DOTALL)
                    if think_match:
                        think_content = think_match.group(1)
                        colored_think_content = f"{Colors.DIM} (^)({think_content}) (^)({Colors.RESET}"
                        display_content = display_content.replace(think_match.group(0), colored_think_content)
                        
                    if hide_reasoning:
                        display_content = refiner.clean_response(display_content)
                        
                    OutputPrinter.print(f"{Colors.GREEN}LLM", f"{display_content}{Colors.RESET}")
                    conversation_history.append({"role": "assistant", "content": response_content_full})
                else:
                    OutputPrinter.print_error("No response from LLM.")
                    for lf in log_files:
                        lf.write(f"User (Voice): {transcribed_text}\n---\n")
                        lf.write("LLM: No response\n---\n")
                        lf.flush()
                        
            os.unlink(temp_filename) # Clean up temp file
        else:
            OutputPrinter.print_error("Invalid input. Please type 'exit', 'enter', '/voice', or '/add <filepath>'.")
