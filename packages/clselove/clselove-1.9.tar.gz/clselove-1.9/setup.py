from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="clselove",
    version="1.9",
    description="A simple library for Android UI automation using UIAutomator and ADB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="CodeMaster",
    author_email="theloveme400@gmail.com",
    url="https://pypi.org/project/myuiautomator/",
    packages=find_packages(),
    install_requires=["uiautomator","pydub","phonenumbers","selenium","seleniumbase","requests","pycountry","numpy","Pillow","SpeechRecognition","names","websocket-client"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
