from setuptools import setup, find_packages

setup(
    name="linxploit",               # pip3 install linxploit
    version="0.0.1",
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[],            
    author="DarkShadow",
    author_email="darkshadow2bd@gmail.com",
    description="A powerful Linux exploitation framework for ethical hacking",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/darkshadow2bd/LinXploit",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    entry_points={
        "console_scripts": [
            "linxploit=linxploit.main:main",
        ],
    },
)

