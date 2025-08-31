from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="md2pdf-cli",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A command-line tool to convert Markdown files to PDF",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/md2pdf",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Documentation",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires=">=3.7",
    install_requires=[
        "markdown2",
        "pdfkit",
    ],
    entry_points={
        "console_scripts": [
            "md2pdf=md2pdf.cli:main",
        ],
    },
    keywords="markdown pdf conversion cli",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/md2pdf/issues",
        "Source": "https://github.com/yourusername/md2pdf",
    },
)