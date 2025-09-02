# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="HoloLink",
    version="0.1.8",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pyperclip",
        "pyautogui",
        "python-dotenv",
        "google-genai",
        "uv",
        "HoloViro",
        "HoloSync",
        "HoloMem",
        "HoloLrn",
        "HoloLog",
        "requests",
    ],
    author="Tristan McBride Sr.",
    author_email="TristanMcBrideSr@users.noreply.github.com",
    description="Modern manager for AI skills, tools, loading, execution, and automation.",
)
