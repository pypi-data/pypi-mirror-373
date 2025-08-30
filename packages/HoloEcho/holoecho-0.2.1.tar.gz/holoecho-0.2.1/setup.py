# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="HoloEcho",
    version="0.2.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "python-dotenv",
        "HoloWave",
        "HoloTTS",
        "HoloSTT",
    ],
    author="Tristan McBride Sr.",
    author_email="TristanMcBrideSr@users.noreply.github.com",
    description="Modern STT AND TTS for modern AI-projects",
)
