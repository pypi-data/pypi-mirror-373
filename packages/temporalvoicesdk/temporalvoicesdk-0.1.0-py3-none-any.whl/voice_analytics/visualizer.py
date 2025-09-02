# Copyright (c) 2023–2025 Temporal AI Technologies Inc. All rights reserved.
# Proprietary and Confidential. Subject to license terms.
# Contact: jorgegonzalez@temporalaitechnologies.com

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from voice_analytics.models import VoicePattern, TrainingResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceVisualizer:
    """
    Voice visualization engine for creating interactive visualizations of voice analysis data.

    This class provides methods to create various types of visualizations for voice patterns,
    training metrics, and audio features.
    """

    def __init__(self, dark_mode=False):
        """
        Initialize the voice visualizer.

        Args:
            dark_mode: Whether to use dark mode for visualizations
        """
        self.dark_mode = dark_mode
        self.bg_color = '#1a1a1a' if dark_mode else '#ffffff'
        self.text_color = '#ffffff' if dark_mode else '#000000'

    def create_pattern_radar(self, patterns, title=None):
        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=list(patterns.values()),
            theta=list(patterns.keys()),
            fill='toself',
            name='Voice Pattern'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=False,
            title=title,
            paper_bgcolor=self.bg_color,
            plot_bgcolor=self.bg_color,
            font_color=self.text_color
        )

        return fig

    def create_training_trends(self, 
                              history: List[Dict[str, Any]],
                              metrics: List[str] = ['clarity', 'emotion', 'confidence'],
                              rolling_window: int = 7,
                              title: Optional[str] = None,
                              height: int = 400,
                              width: Optional[int] = None) -> go.Figure:
        """
        Create a line chart showing training metric trends over time.

        Args:
            history: List of training result dictionaries
            metrics: List of metrics to include in the chart
            rolling_window: Window size for rolling average
            title: Optional title for the chart
            height: Height of the chart in pixels
            width: Optional width of the chart in pixels

        Returns:
            Plotly Figure object
        """
        if not history:
            logger.warning("No training history provided for visualization")
            fig = go.Figure()
            fig.update_layout(
                title="No training data available",
                height=height,
                width=width,
                paper_bgcolor=self.bg_color,
                plot_bgcolor=self.bg_color,
                font_color=self.text_color
            )
            return fig

        try:
            df = pd.DataFrame(history)
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.sort_values('timestamp', inplace=True)

            fig = go.Figure()

            colors = [
                '#6236FF',
                '#00C4B4',
                '#FF7676'
            ]

            for i, metric in enumerate(metrics):
                if metric not in df.columns:
                    continue

                color_idx = i % len(colors)

                # Add raw data
                fig.add_trace(go.Scatter(
                    x=df.index if 'timestamp' not in df.columns else df['timestamp'],
                    y=df[metric],
                    mode='markers+lines',
                    name=metric.title(),
                    line=dict(color=colors[color_idx], width=1, dash='dot'),
                    opacity=0.5
                ))

                # Add rolling average if enough data points
                if len(df) >= rolling_window:
                    df[f'{metric}_rolling'] = df[metric].rolling(window=rolling_window).mean()
                    fig.add_trace(go.Scatter(
                        x=df.index if 'timestamp' not in df.columns else df['timestamp'],
                        y=df[f'{metric}_rolling'],
                        mode='lines',
                        name=f'{metric.title()} ({rolling_window}-pt avg)',
                        line=dict(color=colors[color_idx], width=2)
                    ))

            fig.update_layout(
                title=title,
                height=height,
                width=width,
                xaxis_title="Training Progress" if 'timestamp' not in df.columns else "Date",
                yaxis_title="Score",
                hovermode="x unified",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                paper_bgcolor=self.bg_color,
                plot_bgcolor=self.bg_color,
                font_color=self.text_color
            )

            return fig

        except Exception as e:
            logger.error(f"Error creating training trends visualization: {str(e)}")
            fig = go.Figure()
            fig.update_layout(
                title="Error creating visualization",
                height=height,
                width=width,
                paper_bgcolor=self.bg_color,
                plot_bgcolor=self.bg_color,
                font_color=self.text_color
            )
            return fig

    def create_audio_waveform(self, 
                             audio_array: np.ndarray,
                             sample_rate: int = 22050,
                             title: Optional[str] = None,
                             height: int = 200,
                             width: Optional[int] = None) -> go.Figure:
        """
        Create an audio waveform visualization.

        Args:
            audio_array: Audio data as numpy array
            sample_rate: Audio sample rate in Hz
            title: Optional title for the chart
            height: Height of the chart in pixels
            width: Optional width of the chart in pixels

        Returns:
            Plotly Figure object
        """
        try:
            # Create time axis
            time = np.arange(0, len(audio_array)) / sample_rate

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=time,
                y=audio_array,
                mode='lines',
                line=dict(color=self.theme_colors['primary'], width=1)
            ))

            fig.update_layout(
                title=title,
                height=height,
                width=width,
                xaxis_title="Time (s)",
                yaxis_title="Amplitude",
                paper_bgcolor=self.bg_color,
                plot_bgcolor=self.bg_color,
                font_color=self.text_color
            )

            return fig

        except Exception as e:
            logger.error(f"Error creating audio waveform visualization: {str(e)}")
            fig = go.Figure()
            fig.update_layout(
                title="Error creating waveform",
                height=height,
                width=width,
                paper_bgcolor=self.bg_color,
                plot_bgcolor=self.bg_color,
                font_color=self.text_color
            )
            return fig

    def create_metrics_dashboard(self, metrics, title=None):
        df = pd.DataFrame(metrics)

        fig = go.Figure()

        # Add time series traces
        for column in ['clarity', 'emotion', 'confidence']:
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df[column],
                    name=column.capitalize(),
                    mode='lines+markers'
                )
            )

        fig.update_layout(
            title=title,
            height=400,
            hovermode='x unified',
            paper_bgcolor=self.bg_color,
            plot_bgcolor=self.bg_color,
            font_color=self.text_color,
            xaxis_title='Time',
            yaxis_title='Score',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )

        return fig
