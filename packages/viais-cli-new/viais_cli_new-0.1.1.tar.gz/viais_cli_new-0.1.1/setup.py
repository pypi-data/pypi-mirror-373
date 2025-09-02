from setuptools import setup, find_packages

def parse_requirements(filename):
    """Parse requirements.txt, bỏ qua các dòng comment và dòng rỗng."""
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
        # Loại bỏ comment và dòng rỗng
        reqs = [line for line in lines if line and not line.startswith('#')]
    return reqs

setup(
    name="viais-cli-new",
    version="0.1.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            # "viais-cli=viais_cli.__main__:main"
            "viais-cli-new=viais_cli_new.__main__:main"
        ]
    },
    install_requires=parse_requirements("./viais-cli/requirements.txt"),
    description="A CLI tool for VIAIS",
    author="Your Name",
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)