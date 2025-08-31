from setuptools import setup, find_packages

setup(
    name="anime_gif_random",
    version="0.1.0",
    description="Random anime GIF viewer",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your_email@example.com",
    url="https://github.com/yourusername/anime_gif_random",
    packages=find_packages(),
    install_requires=[
        "requests",
        "Pillow"
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
