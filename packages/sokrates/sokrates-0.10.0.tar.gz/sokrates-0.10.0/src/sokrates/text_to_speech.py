"""
Text-to-Speech implementation using Coqui TTS library.
"""

import re

from pathlib import Path
from typing import Optional, Union
import time
from .output_printer import OutputPrinter
from .colors import Colors

# Try to import voice libs, but don't fail if they are not available
try:
    import torch
    import numpy as np
    TTS_ENABLED = True
except ImportError:
    TTS_ENABLED = False

class TextToSpeech:
    """
    A wrapper class for Coqui TTS library with integration to existing voice_helper.py.
    
    Args:
        model_name (str): Name of the pre-trained TTS model to use
    Attributes:
        tts_api: Instance of TTS API from Coqui TTS library
    Example:
        >>> tts = TextToSpeech(model_name="tts_models/en/ljspeech/tacotron2-DDC")
        >>> audio_data = tts.tts_to_file(text="Hello world", file_path="output.wav")
    """
    
    # vacation internet model :D
    DEFAULT_TTS_MODEL = "tts_models/en/ljspeech/tacotron2-DDC"
    
    # better model
    # DEFAULT_TTS_MODEL = "tts_models/en/ljspeech/vits"
    
    def __init__(self, model_name: str = DEFAULT_TTS_MODEL):
        """
        Initialize the TextToSpeech class with the specified model.
        
        Args:
            model_name (str): Name of the pre-trained TTS model to use
        """
        self.model_name = model_name
        self.tts_api = None
        self._initialize_tts_api()
    
    def _initialize_tts_api(self):
        """
        Initialize the Coqui TTS API with proper device handling.
        
        This method checks for CUDA availability and initializes the TTS API
        with the appropriate device configuration.
        """
        
        if not TTS_ENABLED:
            OutputPrinter.print_error("TTS is not available.")
            return

        try:
            # Import TTS API from Coqui TTS library
            from TTS.api import TTS

            # Check if CUDA is available
            if torch.cuda.is_available():
                device = "cuda"
                OutputPrinter.print("CUDA is available. Using GPU for TTS.")
            # Check if apple metal is available
            elif torch.backends.mps.is_available():
                device = "mps"
                OutputPrinter.print("Apple Metal Performance Shaders (MPS) is available. The model will be loaded to the GPU.")
            else:
                device = "cpu"
                OutputPrinter.print("CUDA is not available. Using CPU for TTS.")
            
            # Initialize TTS API with the specified model
            self.tts_api = TTS(model_name=self.model_name, progress_bar=True).to(device)
        except ImportError as e:
            OutputPrinter.print_error(f"Coqui TTS library not installed: {e}")
            raise RuntimeError("Coqui TTS library is required for text-to-speech functionality.")
        except Exception as e:
            OutputPrinter.print_error(f"Failed to initialize TTS API: {e}")
            raise RuntimeError(f"Failed to initialize TTS API: {e}")
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text to make it compatible with TTS model requirements.
        
        This method handles:
        1. Removing or replacing emojis and unsupported characters
        2. Ensuring sentences are not too short for the model
        3. Cleaning up text formatting
        
        Args:
            text (str): Original text to preprocess
            
        Returns:
            str: Preprocessed text suitable for TTS conversion
        """
        try:
            # Remove emojis and other non-ASCII characters that might not be in the vocabulary
            # Keep basic punctuation and alphanumeric characters
            text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\/\@\#\$\%\^\&\*\+\=\~\`]', '', text)
            
            # Split text into sentences
            sentences = re.split(r'(?<=[.!?])\s+', text)
            
            # Filter out empty sentences and very short ones
            processed_sentences = []
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 0:  # Keep non-empty sentences
                    # If sentence is too short (less than 5 characters), combine it with the next one
                    if len(sentence) < 5 and processed_sentences:
                        # Append to the previous sentence
                        processed_sentences[-1] = processed_sentences[-1] + " " + sentence
                    else:
                        processed_sentences.append(sentence)
            
            # Join the processed sentences
            processed_text = ' '.join(processed_sentences)
            
            # Final cleanup - remove extra spaces
            processed_text = re.sub(r'\s+', ' ', processed_text).strip()
            
            # If the text is still too short, pad it with a period
            if len(processed_text) < 5:
                processed_text = processed_text + "."
            
            OutputPrinter.print(f"Original text length: {len(text)}, Processed text length: {len(processed_text)}")
            return processed_text
            
        except Exception as e:
            OutputPrinter.print_error(f"Error preprocessing text: {e}")
            # If preprocessing fails, return a simple fallback text
            return "Hello."
    
    def tts_to_file(self, text: str, file_path: str) -> bytes:
        """
        Convert text to speech and save as WAV file.
        
        Args:
            text (str): Text to convert to speech
            file_path (str): Path to save the output WAV file
            
        Returns:
            bytes: Audio data in WAV format
            
        Raises:
            RuntimeError: If TTS API initialization fails or file I/O errors occur
        Example:
            >>> audio_data = tts.tts_to_file(text="Hello world", file_path="output.wav")
        """
        if not TTS_ENABLED:
            OutputPrinter.print_error("TTS is not available.")
            return None
        
        try:
            start_time = time.time()
            # Preprocess the text to make it compatible with TTS model
            processed_text = self._preprocess_text(text)
            
            # Ensure the output directory exists
            output_dir = Path(file_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate audio file
            self.tts_api.tts_to_file(text=processed_text, file_path=file_path)
            
            # Read the generated audio file
            with open(file_path, 'rb') as f:
                audio_data = f.read()
            
            OutputPrinter.print("Text-to-speech conversion completed.")
            end_time = time.time()
            total_seconds = round(end_time - start_time, 2)
            OutputPrinter.print_info("Total TTS execution time", f"{total_seconds} seconds", Colors.BRIGHT_MAGENTA, Colors.GREEN)
            return audio_data
            
        except Exception as e:
            OutputPrinter.print_error(f"Failed to convert text to speech: {e}")
            raise RuntimeError(f"Text-to-speech conversion failed: {e}")
    
    def tts(self, text: str) -> np.ndarray:
        """
        Convert text to speech and return as numpy array.
        
        Args:
            text (str): Text to convert to speech
            
        Returns:
            np.ndarray: Audio data as numpy array
            
        Example:
            >>> audio_array = tts.tts(text="Hello world")
        """
        if not TTS_ENABLED:
            OutputPrinter.print_error("TTS is not available.")
            return None
        
        try:
            # Preprocess the text to make it compatible with TTS model
            processed_text = self._preprocess_text(text)
            
            # Generate audio data
            audio_data = self.tts_api.tts(processed_text)
            
            # Convert to numpy array
            audio_array = np.array(audio_data, dtype=np.float32)
            
            OutputPrinter.print("Text-to-speech conversion completed successfully.")
            return audio_array
            
        except Exception as e:
            OutputPrinter.print_error(f"Failed to convert text to speech: {e}")
            raise RuntimeError(f"Text-to-speech conversion failed: {e}")
    
    def play_audio(self, text: str, file_path: str) -> None:
        """
        Convert text to speech and play the audio file.
        
        Args:
            text (str): Text to convert to speech
            file_path (str): Path to save the output WAV file
            
        Example:
            >>> tts.play_audio(text="Hello world", file_path="output.wav")
        """
        if not TTS_ENABLED:
            OutputPrinter.print_error("TTS is not available.")
            return 
        
        try:
            # Convert text to speech and save to file
            audio_data = self.tts_to_file(text, file_path)
            
            # Ensure the file exists before playing
            if not Path(file_path).exists():
                raise FileNotFoundError(f"Audio file not found at {file_path}")
            
            # Play the audio file using the existing play_audio_file function
            from .voice_helper import play_audio_file
            play_audio_file(file_path)
            
            OutputPrinter.print(f"Audio played successfully from {file_path}")
            
        except Exception as e:
            OutputPrinter.print_error(f"Failed to play audio: {e}")
            raise RuntimeError(f"Failed to play audio: {e}")