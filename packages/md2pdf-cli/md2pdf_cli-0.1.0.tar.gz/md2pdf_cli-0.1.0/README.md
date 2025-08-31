# Markdown to PDF Converter

A command-line tool to convert Markdown files to PDF using Python.

## Installation

```bash
pip install .    
pip install md2pdf-cli
```

## Usage
 
 need to install wkhtmltox from 

```
https://gitlink.org.cn/dnrops/my_tools/releases/download/0.0.1/wkhtmltox-0.12.6-1.mxe-cross-win64.7z
```


```
# Basic conversion
md2pdf input.md output.pdf

# With custom CSS
md2pdf input.md output.pdf --style style.css
```



Sample CSS

```css
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 2cm;
}
h1 { color: #2c3e50; }
h2 { color: #34495e; }
code {
    background-color: #f8f8f8;
    padding: 2px 4px;
    border-radius: 3px;
}
pre {
    background-color: #f8f8f8;
    padding: 10px;
    border-radius: 5px;
    overflow-x: auto;
}
```

```bash
md2pdf/
├── setup.py
├── README.md
└── md2pdf/
    ├── __init__.py
    └── cli.py
```