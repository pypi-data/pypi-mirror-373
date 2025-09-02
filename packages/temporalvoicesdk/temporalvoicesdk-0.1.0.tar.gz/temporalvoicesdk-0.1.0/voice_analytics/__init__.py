# Copyright (c) 2023–2025 Temporal AI Technologies Inc. All rights reserved.
# Proprietary and Confidential. Subject to license terms.
# Contact: Support@temporalaitechnologies.com

"""
Voice Analytics Package

A package for advanced voice pattern recognition and visualization.
"""

from voice_analytics.processor import VoiceAnalyzer
from voice_analytics.realtime_analyzer import RealTimeVoiceAnalyzer
from voice_analytics.models import VoicePattern, TrainingResult, AudioFeatures

__version__ = '0.1.0'
__author__ = 'Temporal AI Technologies Inc.'
__email__ = 'jorgegonzalez@temporalaitechnologies.com'
__all__ = [
    'VoiceAnalyzer',
    'RealTimeVoiceAnalyzer',
    'VoicePattern',
    'TrainingResult',
    'AudioFeatures',
]
