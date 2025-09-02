# Copyright (c) 2023–2025 Temporal AI Technologies Inc. All rights reserved.
# Proprietary and Confidential. Subject to license terms.
# Contact: jorgegonzalez@temporalaitechnologies.com

import numpy as np
import speech_recognition as sr
from datetime import datetime
import pandas as pd
import logging
from typing import Dict, Any, List, Optional, BinaryIO, Union
from voice_analytics.models import VoicePattern, TrainingResult, AudioFeatures

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceAnalyzer:
    """
    Core voice analysis engine for processing audio files and extracting voice patterns.

    This class provides functionality to analyze voice recordings, extract features,
    and generate training metrics for voice pattern recognition.
    """

    def __init__(self):
        """Initialize the voice analyzer with a new recognizer instance."""
        self.recognizer = sr.Recognizer()
        self.training_history = []
        self.current_epoch = 0

    def analyze_audio(self, audio_file: BinaryIO) -> Dict[str, Any]:
        """
        Analyze audio file using real speech recognition.

        Args:
            audio_file: An audio file object (must be in a format supported by speech_recognition)

        Returns:
            Dictionary containing analysis metrics
        """
        try:
            logger.info(f"Processing audio file: {audio_file.name}")
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)

                # Get actual audio data metrics
                audio_data = audio.get_raw_data()
                audio_length = len(audio_data) / (audio.sample_rate * audio.sample_width)

                # Perform real speech recognition
                text = self.recognizer.recognize_google(audio)

                # Calculate real metrics based on audio analysis
                metrics = {
                    'clarity': self._calculate_clarity(audio_data),
                    'emotion': self._analyze_emotion(text),
                    'confidence': self._calculate_confidence(audio_data),
                    'duration': audio_length,
                    'timestamp': datetime.now(),
                    'text': text
                }

                self.training_history.append(metrics)
                logger.info(f"Analysis complete. Metrics: {metrics}")
                return metrics

        except sr.UnknownValueError:
            logger.error("Speech recognition could not understand the audio")
            return {'error': 'Speech could not be recognized'}
        except sr.RequestError as e:
            logger.error(f"Could not request results from service: {str(e)}")
            return {'error': f'Service error: {str(e)}'}
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            return {'error': str(e)}

    def _calculate_clarity(self, audio_data: bytes) -> float:
        """
        Calculate actual audio clarity score.

        Args:
            audio_data: Raw audio data bytes

        Returns:
            Clarity score between 0 and 1
        """
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        normalized = audio_array / float(max(abs(audio_array)) or 1)  # Avoid division by zero
        return float(np.mean(abs(normalized)) * 0.8 + 0.2)  # Scale to reasonable range

    def _analyze_emotion(self, text: str) -> float:
        """
        Analyze emotion from speech text.

        Args:
            text: Transcribed text from speech

        Returns:
            Emotion score between 0 and 1
        """
        words = text.lower().split()
        positive_words = {'good', 'great', 'happy', 'excellent'}
        negative_words = {'bad', 'poor', 'unhappy', 'terrible'}

        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        total = len(words)

        if total == 0:
            return 0.5
        return (positive_count - negative_count + total) / (total * 2)

    def _calculate_confidence(self, audio_data: bytes) -> float:
        """
        Calculate confidence score based on audio quality.

        Args:
            audio_data: Raw audio data bytes

        Returns:
            Confidence score between 0 and 1
        """
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        # Real implementation would analyze various audio quality metrics
        signal_power = np.mean(np.square(audio_array))
        if signal_power <= 0:
            return 0.5
        return min(0.95, max(0.5, np.log10(signal_power) / 10))

    def get_training_metrics(self) -> Optional[Dict[str, Any]]:
        """
        Get actual training history metrics.

        Returns:
            Dictionary containing aggregate training metrics or None if no history exists
        """
        if not self.training_history:
            return None

        metrics_df = pd.DataFrame(self.training_history)
        return {
            'avg_clarity': metrics_df['clarity'].mean(),
            'avg_emotion': metrics_df['emotion'].mean(),
            'avg_confidence': metrics_df['confidence'].mean(),
            'total_samples': len(metrics_df),
            'total_duration': metrics_df['duration'].sum()
        }

    def analyze_voice_patterns(self, audio_data: bytes) -> Dict[str, float]:
        """
        Analyze actual voice patterns from audio data.

        Args:
            audio_data: Raw audio data bytes

        Returns:
            Dictionary of voice pattern measurements
        """
        if audio_data is None or len(audio_data) == 0:
            return {}

        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            pattern = VoicePattern(
                pitch_control=self._analyze_pitch(audio_array),
                volume_stability=self._analyze_volume(audio_array),
                speech_clarity=self._analyze_clarity(audio_array),
                rhythm=self._analyze_rhythm(audio_array),
                pronunciation=self._analyze_pronunciation(audio_array)
            )

            return {
                'Pitch_Control': pattern.pitch_control,
                'Volume_Stability': pattern.volume_stability,
                'Speech_Clarity': pattern.speech_clarity,
                'Rhythm': pattern.rhythm,
                'Pronunciation': pattern.pronunciation
            }
        except Exception as e:
            logger.error(f"Error analyzing voice patterns: {str(e)}")
            return {}

    def _analyze_pitch(self, audio_array: np.ndarray) -> float:
        """
        Analyze pitch variations in audio.

        Args:
            audio_array: Audio data as numpy array

        Returns:
            Pitch control score between 0 and 1
        """
        # Real implementation would use pitch detection algorithms
        return np.clip(np.mean(np.abs(np.diff(audio_array))) / 32768, 0, 1)

    def _analyze_volume(self, audio_array: np.ndarray) -> float:
        """
        Analyze volume stability.

        Args:
            audio_array: Audio data as numpy array

        Returns:
            Volume stability score between 0 and 1
        """
        # Calculate RMS volume variations
        return np.clip(1 - np.std(np.abs(audio_array)) / 32768, 0, 1)

    def _analyze_rhythm(self, audio_array: np.ndarray) -> float:
        """
        Analyze speech rhythm.

        Args:
            audio_array: Audio data as numpy array

        Returns:
            Rhythm score between 0 and 1
        """
        # Real implementation would analyze speech rate and pauses
        return np.clip(np.mean(np.abs(audio_array)) / 32768, 0, 1)

    def _analyze_pronunciation(self, audio_array: np.ndarray) -> float:
        """
        Analyze pronunciation quality.

        Args:
            audio_array: Audio data as numpy array

        Returns:
            Pronunciation score between 0 and 1
        """
        # Real implementation would use phoneme recognition
        return np.clip(np.max(np.abs(audio_array)) / 32768, 0, 1)

    def reset_training(self):
        """Reset training progress and history."""
        self.training_history = []
        self.current_epoch = 0
        logger.info("Training history and progress reset")

    def extract_audio_features(self, audio_data: bytes) -> AudioFeatures:
        """
        Extract comprehensive set of audio features from raw audio data.

        Args:
            audio_data: Raw audio data bytes

        Returns:
            AudioFeatures object containing extracted features
        """
        if audio_data is None or len(audio_data) == 0:
            return AudioFeatures()

        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)

            # Basic features
            mean = float(np.mean(audio_array))
            std = float(np.std(audio_array))
            max_amplitude = float(np.max(np.abs(audio_array)))
            min_amplitude = float(np.min(np.abs(audio_array)))

            # Energy features
            energy = float(np.sum(audio_array**2))

            # Simple frequency analysis
            # In a real implementation, you'd use librosa or another audio processing library
            # for more sophisticated frequency analysis (FFT, MFCC, etc.)
            zero_crossings = np.sum(np.abs(np.diff(np.signbit(audio_array)))) / len(audio_array)

            return AudioFeatures(
                mean=mean,
                std=std,
                max_amplitude=max_amplitude,
                min_amplitude=min_amplitude,
                energy=energy,
                zero_crossing_rate=float(zero_crossings)
            )

        except Exception as e:
            logger.error(f"Error extracting audio features: {str(e)}")
            return AudioFeatures()


class VoiceProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.logger = logging.getLogger(__name__)

    def analyze_audio(self, audio_data):
        try:
            # Convert audio to text
            text = self.recognizer.recognize_google(audio_data)

            # Calculate metrics
            clarity_score = self._calculate_clarity(audio_data)
            emotion_score = self._analyze_emotion(audio_data)
            confidence_score = self._calculate_confidence(audio_data)

            return {
                'text': text,
                'clarity': clarity_score,
                'emotion': emotion_score,
                'confidence': confidence_score,
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            self.logger.error(f"Error analyzing audio: {e}")
            return {'error': str(e)}

    def _calculate_clarity(self, audio_data):
        # Implement clarity calculation logic
        return np.random.uniform(0.7, 1.0)  # Placeholder

    def _analyze_emotion(self, audio_data):
        # Implement emotion analysis logic
        return np.random.uniform(0.6, 0.9)  # Placeholder

    def _calculate_confidence(self, audio_data):
        # Implement confidence calculation logic
        return np.random.uniform(0.8, 1.0)  # Placeholder
