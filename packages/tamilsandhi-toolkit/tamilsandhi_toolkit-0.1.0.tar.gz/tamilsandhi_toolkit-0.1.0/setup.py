from setuptools import setup, find_packages

setup(
    name="tamilsandhi-toolkit",  
    version="0.1.0",     
    packages=find_packages(),  
    install_requires=[
        "open-tamil",
        "pytest"
    ],
    author="Yazhmozhi VM, Annalu Waller and Jacky Visser",
    author_email="yazh.connect@gmail.com",
    description="A Python library to detect and correct Tamil Sandhi errors using rule-based methods.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/TamilGeekGirl/TamilSandhiNeuroSymbolicAI/",  
    license="MIT",
    license_files=["LICENSE"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Tamil",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Linguistic"
    ],
    python_requires='>=3.6',
)