"""setup.py -- note use setuptools==73.0.1; older versions fuck up the data files, newer versions include resources."""
from pathlib import Path
from setuptools import setup, find_packages

NAME = "vre-video"
VERSION = "0.3.7"
DESCRIPTION = "Video Representations Extractor (VRE) Video reader"
URL = "https://gitlab.com/video-representations-extractor/vre-video"

CWD = Path(__file__).absolute().parent
with open(CWD/"README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

REQUIRED = [
    "numpy>=1.21.6,<2.0.0",
    "tqdm==4.66.5",
    "Pillow==10.3.0",
    "natsort==8.2.0",
    "loggez>=0.4.4",
]

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=URL,
    packages=find_packages(),
    install_requires=REQUIRED,
    dependency_links=[],
    license="MIT",
    python_requires=">=3.8",
    scripts=["cli/vre_video_player.py"],
)
