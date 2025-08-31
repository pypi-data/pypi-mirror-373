# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="HoloTTS",
    version="0.2.5",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pyttsx3',
        'pyttsx4',
        'python-dotenv',
        'pydub',
        'numpy',
        'kokoro',
        'SoundFile',
        'pygame',
        'pyautogui',
    ],
    author="Tristan McBride Sr.",
    author_email="TristanMcBrideSr@users.noreply.github.com",
    description="Modern, local TTS, advanced audio manipulation, pipeline automation, and flexible playback, pause, resume for modern AI-driven applications.",
)
