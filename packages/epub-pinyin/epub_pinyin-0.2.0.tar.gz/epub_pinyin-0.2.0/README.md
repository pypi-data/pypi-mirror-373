# EPUB Pinyin

A Python tool to add Pinyin annotations above Chinese characters in EPUB files. This tool helps Chinese language learners by automatically adding pronunciation guides to Chinese text while maintaining the EPUB format and structure.

## Features

- Automatically detects Chinese characters in EPUB content
- Adds Pinyin annotations using `<ruby>` tags
- Preserves original EPUB structure and formatting
- Supports tone marks in Pinyin
- Handles complex EPUB structures
- Maintains original file organization
- Processes files in correct spine order
- **NEW**: Convert EPUB to PDF with Pinyin annotations
- **NEW**: Smart context-aware pronunciation for polyphonic characters
- **NEW**: Custom font support for Chinese text and Pinyin
- **NEW**: Professional PDF layout with proper Chinese typography

## Installation

You can install the package directly from PyPI:

```bash
pip install epub-pinyin
```

Or install from source:

```bash
git clone https://github.com/tony-develop-2025/epub-pinyin.git
cd epub-pinyin
pip install -e .
```

## Usage

### EPUB Processing

#### Command Line

After installation, you can use the tool from the command line:

```bash
epub-pinyin input.epub -o output.epub
```

Or use the module directly:

```bash
python -m epub_pinyin.main input.epub -o output.epub
```

Where:
- `input.epub` is your source EPUB file containing Chinese text
- `-o output.epub` (optional) specifies the output file name (defaults to "input_annotated.epub")

#### Python API

You can also use the tool programmatically in your Python code:

```python
from epub_pinyin import process_epub

# Process an EPUB file
process_epub("input.epub", "output.epub")
```

### PDF Conversion

#### Command Line

Convert EPUB to PDF with Pinyin annotations:

```bash
python -m epub_pinyin.main input.epub --pdf output.pdf
```

Or use the dedicated PDF converter:

```bash
python -m epub_pinyin.pdf_converter input.epub output.pdf
```

#### Python API

```python
from epub_pinyin.pdf_converter import convert_epub_to_pdf

# Convert EPUB to PDF
convert_epub_to_pdf("input.epub", "output.pdf")
```

#### Advanced PDF Usage

For more control over PDF generation:

```python
from epub_pinyin.epub_parser import EpubParser
from epub_pinyin.pdf_converter import PdfConverter
import tempfile

# Extract EPUB content
with tempfile.TemporaryDirectory() as temp_dir:
    parser = EpubParser(temp_dir)
    parser.extract_epub("input.epub")
    
    # Convert to PDF with custom settings
    converter = PdfConverter(parser)
    converter.convert_to_pdf("output.pdf")
```

## Examples

### EPUB Output

When rendered in an EPUB reader, the Pinyin appears above each character:
```
 nǐ  hǎo    shì  jiè
你好，世界！
```
![alt text](image.png)

### PDF Output

The PDF conversion creates a professional document with:

- **Smart Pinyin**: Context-aware pronunciation for polyphonic characters
  - 长袍 (zhǎng páo) vs 长度 (cháng dù)
  - 银行 (yín háng) vs 行走 (xíng zǒu)
  - 觉得 (jué de) vs 得到 (dé dào)

- **Professional Layout**:
  - Custom Chinese fonts (SimSun, FangSong, STSong)
  - Separate font styling for Pinyin annotations
  - Proper Chinese typography rules
  - No punctuation at line start (except quotes)

- **Typography Features**:
  - Automatic line breaking with proper Chinese rules
  - Ruby text positioning for Pinyin
  - Optimized spacing and margins
  - Chapter and page organization

## Requirements

### Core Requirements
- Python 3.7 or higher
- beautifulsoup4
- pypinyin
- lxml

### PDF Conversion Requirements
- reportlab (for PDF generation)
- Custom Chinese fonts (optional, will use system fonts as fallback)

### Installation with PDF Support

```bash
# Install with PDF support
pip install epub-pinyin[pdf]

# Or install all dependencies
pip install epub-pinyin[dev]
```

## Development

To set up the development environment:

1. Clone the repository:
```bash
git clone https://github.com/tony-develop-2025/epub-pinyin.git
cd epub-pinyin
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

4. Run tests:
```bash
pytest tests/
```

5. Test PDF conversion:
```bash
# Create a test EPUB file first, then convert to PDF
python -m epub_pinyin.main test.epub --pdf test.pdf
```

## Configuration

### Custom Fonts

You can add custom Chinese fonts to improve PDF output quality:

1. Place your font files in the `epub_pinyin/fonts/` directory
2. Supported formats: `.ttf`, `.ttc`
3. The system will automatically detect and use available fonts

### PDF Settings

The PDF converter includes several configurable options:

- **Font sizes**: Adjustable for title, chapter, body, and Pinyin text
- **Margins**: Customizable page margins
- **Line spacing**: Configurable line height
- **Character width**: Uniform character spacing for Chinese text

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Areas for Contribution

- **Font Support**: Add support for more Chinese font formats
- **Typography**: Improve Chinese typography rules
- **Performance**: Optimize PDF generation speed
- **Testing**: Add more comprehensive test cases
- **Documentation**: Improve user guides and examples

## Troubleshooting

### Common Issues

#### PDF Generation Fails
- **Error**: "No Chinese fonts found"
  - **Solution**: Install ReportLab with PDF support: `pip install epub-pinyin[pdf]`
  - **Solution**: Add custom fonts to `epub_pinyin/fonts/` directory

#### Pinyin Accuracy Issues
- **Issue**: Incorrect pronunciation for polyphonic characters
  - **Solution**: The system uses context-aware pronunciation. For better accuracy, ensure proper word boundaries in your text.

#### Font Display Issues
- **Issue**: Chinese characters not displaying correctly in PDF
  - **Solution**: Check that your font files are valid and supported
  - **Solution**: Try different font formats (.ttf, .ttc)

### Performance Tips

- For large EPUB files, PDF conversion may take some time
- Consider processing chapters separately for very large documents
- Ensure sufficient disk space for temporary files during conversion

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


