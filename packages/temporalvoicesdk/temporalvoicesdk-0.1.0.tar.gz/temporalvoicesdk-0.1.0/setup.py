from setuptools import setup, find_packages

setup(
    name="TemporalVoiceSDK",
    version="0.1.0",
    author="Temporal AI Technologies Inc.",
    author_email="jorgegonzalez@temporalaitechnologies.com",
    description="A proprietary SDK for biometric voice analysis and audio pattern visualization.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/TemporalAITech/TemporalVoiceSDK",
    packages=find_packages(include=["voice_analytics", "voice_analytics.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.19.0",
        "pandas>=1.1.0",
        "plotly>=4.14.0",
        "SpeechRecognition>=3.8.0",
        "scikit-learn>=0.24.0",
    ],
)
