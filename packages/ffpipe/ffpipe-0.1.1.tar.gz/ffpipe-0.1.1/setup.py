from setuptools import find_packages, setup

setup(
    name="ffpipe",
    version="0.1.1",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=[
        "numpy",
        "ffmpeg-python",
        "tqdm",
    ],
    author="Aryan Shekarlaban",
    author_email="arxyzan@gmail.com",
    description="FFPipe: Image processing in realtime using FFmpeg's pipe mechanism with a robust video/audio sync.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="Apache-2.0",
    python_requires=">=3.10",
)
