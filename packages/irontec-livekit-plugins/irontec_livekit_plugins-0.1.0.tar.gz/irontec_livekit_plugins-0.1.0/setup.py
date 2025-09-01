from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="livekit-plugins",
    version="0.1.0",
    author="Irontec S.L.",
    author_email="communications@irontec.com",
    description="Custom Livekit Agents plugins for STT and TTS services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/livekit-plugins",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "black",
            "flake8",
            "mypy",
        ],
    },
    keywords="livekit, agents, stt, tts, speech, audio, ai",
    project_urls={
        "Bug Reports": "https://github.com/your-org/livekit-plugins/issues",
        "Source": "https://github.com/your-org/livekit-plugins",
        "Documentation": "https://github.com/your-org/livekit-plugins#readme",
    },
)