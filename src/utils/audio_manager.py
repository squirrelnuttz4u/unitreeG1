"""
Audio Manager for Unitree G1 Windows App
Handles audio playback and voice recognition
"""

import logging
import threading
import queue
from typing import Optional, Callable

# Audio libraries
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    logging.warning("pyttsx3 not available. Text-to-speech disabled.")

try:
    import speech_recognition as sr
    STT_AVAILABLE = True
except ImportError:
    STT_AVAILABLE = False
    logging.warning("SpeechRecognition not available. Voice commands disabled.")


class AudioManager:
    """Manages audio playback and voice recognition"""

    def __init__(self):
        """Initialize audio manager"""
        self.logger = logging.getLogger(__name__)

        # Text-to-Speech
        self.tts_engine = None
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)  # Speed
                self.tts_engine.setProperty('volume', 0.9)  # Volume
            except Exception as e:
                self.logger.error(f"Failed to initialize TTS: {e}")
                self.tts_engine = None

        # Speech-to-Text
        self.recognizer = None
        self.microphone = None
        if STT_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
            except Exception as e:
                self.logger.error(f"Failed to initialize STT: {e}")
                self.recognizer = None

        # Voice command processing
        self.voice_thread = None
        self.is_listening = False
        self.command_callbacks = []

        # Audio queue for TTS
        self.tts_queue = queue.Queue()
        self.tts_thread = None
        self.tts_running = False

    def start(self):
        """Start audio manager"""
        self.logger.info("Starting audio manager")

        # Start TTS thread
        if self.tts_engine:
            self.tts_running = True
            self.tts_thread = threading.Thread(target=self._tts_loop, daemon=True)
            self.tts_thread.start()

    def stop(self):
        """Stop audio manager"""
        self.logger.info("Stopping audio manager")

        # Stop listening
        self.stop_listening()

        # Stop TTS
        self.tts_running = False
        if self.tts_thread:
            self.tts_thread.join(timeout=2.0)

    # Text-to-Speech Methods

    def speak(self, text: str, blocking: bool = False):
        """
        Speak text using TTS

        Args:
            text: Text to speak
            blocking: If True, wait for speech to complete
        """
        if not self.tts_engine:
            self.logger.warning("TTS not available")
            return

        if blocking:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                self.logger.error(f"TTS error: {e}")
        else:
            self.tts_queue.put(text)

    def _tts_loop(self):
        """TTS processing loop"""
        while self.tts_running:
            try:
                text = self.tts_queue.get(timeout=0.5)
                if text:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in TTS loop: {e}")

    # Speech-to-Text Methods

    def start_listening(self) -> bool:
        """
        Start listening for voice commands

        Returns:
            bool: True if listening started
        """
        if not self.recognizer or not self.microphone:
            self.logger.warning("STT not available")
            return False

        if self.is_listening:
            self.logger.warning("Already listening")
            return True

        self.is_listening = True
        self.voice_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.voice_thread.start()

        self.logger.info("Voice recognition started")
        return True

    def stop_listening(self):
        """Stop listening for voice commands"""
        if not self.is_listening:
            return

        self.is_listening = False
        if self.voice_thread:
            self.voice_thread.join(timeout=2.0)

        self.logger.info("Voice recognition stopped")

    def _listen_loop(self):
        """Voice recognition loop"""
        while self.is_listening:
            try:
                with self.microphone as source:
                    # Adjust for ambient noise
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                    # Listen for audio
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)

                    # Recognize speech
                    try:
                        command = self.recognizer.recognize_google(audio)
                        self.logger.info(f"Voice command recognized: {command}")
                        self._process_voice_command(command)
                    except sr.UnknownValueError:
                        # Speech not understood
                        pass
                    except sr.RequestError as e:
                        self.logger.error(f"Speech recognition error: {e}")

            except Exception as e:
                self.logger.error(f"Error in listen loop: {e}")

    def _process_voice_command(self, command: str):
        """
        Process recognized voice command

        Args:
            command: Recognized command text
        """
        command = command.lower().strip()

        # Notify callbacks
        for callback in self.command_callbacks:
            try:
                callback(command)
            except Exception as e:
                self.logger.error(f"Error in command callback: {e}")

    def register_command_callback(self, callback: Callable[[str], None]):
        """
        Register callback for voice commands

        Args:
            callback: Function to call with recognized commands
        """
        self.command_callbacks.append(callback)

    # Predefined Voice Commands

    def get_available_commands(self) -> list:
        """
        Get list of available voice commands

        Returns:
            list: List of command strings
        """
        return [
            "stand up",
            "sit down",
            "walk forward",
            "walk backward",
            "run",
            "stop",
            "wave hand",
            "shake hand",
            "turn left",
            "turn right",
            "connect",
            "disconnect"
        ]

    def parse_motion_command(self, command: str) -> Optional[dict]:
        """
        Parse voice command into motion parameters

        Args:
            command: Voice command text

        Returns:
            Optional[dict]: Motion parameters or None
        """
        command = command.lower()

        # Stand/Sit
        if "stand" in command or "stand up" in command:
            return {"action": "stand"}
        elif "sit" in command or "sit down" in command:
            return {"action": "sit"}

        # Motion
        elif "walk forward" in command or "move forward" in command:
            return {"action": "walk", "vx": 0.3, "vy": 0.0, "yaw": 0.0}
        elif "walk backward" in command or "move backward" in command:
            return {"action": "walk", "vx": -0.3, "vy": 0.0, "yaw": 0.0}
        elif "walk left" in command:
            return {"action": "walk", "vx": 0.0, "vy": 0.3, "yaw": 0.0}
        elif "walk right" in command:
            return {"action": "walk", "vx": 0.0, "vy": -0.3, "yaw": 0.0}
        elif "run" in command:
            return {"action": "run", "vx": 0.6, "vy": 0.0, "yaw": 0.0}
        elif "stop" in command or "halt" in command:
            return {"action": "stop"}

        # Rotation
        elif "turn left" in command or "rotate left" in command:
            return {"action": "walk", "vx": 0.0, "vy": 0.0, "yaw": 0.5}
        elif "turn right" in command or "rotate right" in command:
            return {"action": "walk", "vx": 0.0, "vy": 0.0, "yaw": -0.5}

        # Gestures
        elif "wave" in command:
            return {"action": "wave"}
        elif "shake hand" in command or "handshake" in command:
            return {"action": "shake_hand"}

        return None
