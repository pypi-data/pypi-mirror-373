# TemporalVoiceSDK

### Advanced Voice Pattern Recognition & Visualization  
© 2023–2025 Temporal AI Technologies Inc. All Rights Reserved.  
*Proprietary and Confidential. Subject to license terms.*

---

## 🧠 Overview

**TemporalVoiceSDK** is a comprehensive Python package for advanced voice analytics.  
It enables developers to extract, analyze, and visualize voice patterns — including clarity, emotion, and speech confidence — for real-time or offline applications.

---

## ✨ Features

- 🎙️ Process audio files to extract voice features and metrics  
- 🧠 Analyze speech clarity, emotion, confidence, and voice patterns  
- 📊 Generate interactive Plotly visualizations (radar charts, dashboards)  
- 📈 Track training progress and usage metrics  
- 🔌 Integrate easily with Streamlit, Flask, or other Python apps

---

## 🚀 Installation

### From GitHub (latest version)

```bash
pip install git+https://github.com/TemporalAITech/TemporalVoiceSDK.git
```

---

## ⚡ Quick Start

### Basic Voice Analysis

```python
from voice_analytics import VoiceAnalyzer
import io

# Initialize the analyzer
analyzer = VoiceAnalyzer()

# Analyze an audio file
with open('sample.wav', 'rb') as audio_file:
    metrics = analyzer.analyze_audio(audio_file)
    
print(metrics)
```

---

### Visualize Voice Patterns

```python
from voice_analytics import VoiceAnalyzer, VoiceVisualizer
import plotly.io as pio

# Initialize the analyzer and visualizer
analyzer = VoiceAnalyzer()
visualizer = VoiceVisualizer()

# Analyze voice patterns from audio
with open('sample.wav', 'rb') as audio_file:
    audio_data = audio_file.read()
    patterns = analyzer.analyze_voice_patterns(audio_data)

# Create radar chart
fig = visualizer.create_pattern_radar(patterns, title="Voice Pattern Analysis")
pio.write_html(fig, 'voice_patterns.html')
```

---

### Create a Metrics Dashboard

```python
from voice_analytics import VoiceAnalyzer, VoiceVisualizer
import plotly.io as pio

analyzer = VoiceAnalyzer()
visualizer = VoiceVisualizer(dark_mode=True)

for audio_file in ['sample1.wav', 'sample2.wav', 'sample3.wav']:
    with open(audio_file, 'rb') as f:
        analyzer.analyze_audio(f)

metrics = analyzer.get_training_metrics()
dashboard = visualizer.create_metrics_dashboard(metrics, title="Voice Performance")
pio.write_html(dashboard, 'voice_dashboard.html')
```

---

## 📊 Streamlit Integration Example

```python
import streamlit as st
from voice_analytics import VoiceAnalyzer, VoiceVisualizer

analyzer = VoiceAnalyzer()
visualizer = VoiceVisualizer()

uploaded_file = st.file_uploader("Upload audio sample", type=['wav', 'mp3'])

if uploaded_file:
    st.audio(uploaded_file)
    metrics = analyzer.analyze_audio(uploaded_file)
    st.write("Analysis Results:", metrics)

    if metrics and 'error' not in metrics:
        patterns = analyzer.analyze_voice_patterns(uploaded_file.getvalue())
        fig_radar = visualizer.create_pattern_radar(patterns, title="Voice Pattern Analysis")
        st.plotly_chart(fig_radar, use_container_width=True)

        if 'text' in metrics:
            st.subheader("Transcribed Text")
            st.write(metrics['text'])
```

---

## 📄 License

This software is licensed under a proprietary license.  
See the [LICENSE](./LICENSE) file for full terms.
