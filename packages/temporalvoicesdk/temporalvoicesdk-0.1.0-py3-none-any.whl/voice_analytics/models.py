# Copyright (c) 2023–2025 Temporal AI Technologies Inc. All rights reserved.
# Proprietary and Confidential. Subject to license terms.
# Contact: jorgegonzalez@temporalaitechnologies.com

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime

@dataclass
class VoicePattern:
    """Data class for voice pattern analysis results."""
    pitch_control: float = 0.0
    volume_stability: float = 0.0
    speech_clarity: float = 0.0
    rhythm: float = 0.0
    pronunciation: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        """Convert pattern to dictionary."""
        return {
            'Pitch_Control': self.pitch_control,
            'Volume_Stability': self.volume_stability,
            'Speech_Clarity': self.speech_clarity,
            'Rhythm': self.rhythm,
            'Pronunciation': self.pronunciation
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'VoicePattern':
        """Create pattern from dictionary."""
        return cls(
            pitch_control=data.get('Pitch_Control', 0.0),
            volume_stability=data.get('Volume_Stability', 0.0),
            speech_clarity=data.get('Speech_Clarity', 0.0),
            rhythm=data.get('Rhythm', 0.0),
            pronunciation=data.get('Pronunciation', 0.0)
        )

@dataclass
class AudioFeatures:
    """Data class for extracted audio features."""
    mean: float = 0.0
    std: float = 0.0
    max_amplitude: float = 0.0
    min_amplitude: float = 0.0
    energy: float = 0.0
    zero_crossing_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        """Convert features to dictionary."""
        return {
            'mean': self.mean,
            'std': self.std,
            'max_amplitude': self.max_amplitude,
            'min_amplitude': self.min_amplitude,
            'energy': self.energy,
            'zero_crossing_rate': self.zero_crossing_rate
        }

@dataclass
class TrainingResult:
    """Data class for voice training results."""
    clarity: float
    emotion: float
    confidence: float
    duration: float
    text: str
    timestamp: datetime = field(default_factory=datetime.now)
    patterns: Optional[VoicePattern] = None
    features: Optional[AudioFeatures] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert training result to dictionary."""
        result = {
            'clarity': self.clarity,
            'emotion': self.emotion,
            'confidence': self.confidence,
            'duration': self.duration,
            'text': self.text,
            'timestamp': self.timestamp.isoformat()
        }
        
        if self.patterns:
            result['patterns'] = self.patterns.to_dict()
            
        if self.features:
            result['features'] = self.features.to_dict()
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrainingResult':
        """Create training result from dictionary."""
        patterns = None
        if 'patterns' in data:
            patterns = VoicePattern.from_dict(data['patterns'])
            
        features = None
        if 'features' in data:
            features_dict = data['features']
            features = AudioFeatures(
                mean=features_dict.get('mean', 0.0),
                std=features_dict.get('std', 0.0),
                max_amplitude=features_dict.get('max_amplitude', 0.0),
                min_amplitude=features_dict.get('min_amplitude', 0.0),
                energy=features_dict.get('energy', 0.0),
                zero_crossing_rate=features_dict.get('zero_crossing_rate', 0.0)
            )
            
        timestamp = data.get('timestamp')
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif not isinstance(timestamp, datetime):
            timestamp = datetime.now()
            
        return cls(
            clarity=data.get('clarity', 0.0),
            emotion=data.get('emotion', 0.0),
            confidence=data.get('confidence', 0.0),
            duration=data.get('duration', 0.0),
            text=data.get('text', ''),
            timestamp=timestamp,
            patterns=patterns,
            features=features
        )
