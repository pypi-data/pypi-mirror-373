"""Module for converting EPUB to PDF using ReportLab."""

import os
import tempfile
from typing import List, Optional
from pathlib import Path
from bs4 import BeautifulSoup

# Import ReportLab conditionally to avoid dependency issues
REPORTLAB_AVAILABLE = False
LINE_SPACE_TIMES = 2.2
CHAR_WIDTH = 24
PINYIN_FONT_SIZE = 0.6
def _import_reportlab():
    """Import ReportLab when needed."""
    global REPORTLAB_AVAILABLE
    if not REPORTLAB_AVAILABLE:
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib.colors import black
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            REPORTLAB_AVAILABLE = True
        except ImportError:
            pass
    return REPORTLAB_AVAILABLE

from .epub_parser import EpubParser, EpubStructure


class PdfConverter:
    """Class for converting EPUB content to PDF."""
    
    def __init__(self, epub_parser: EpubParser):
        """Initialize PDF converter with an EPUB parser.
        
        Args:
            epub_parser: EpubParser instance with extracted content
        """
        if not _import_reportlab():
            raise ImportError(
                "ReportLab is required for PDF conversion. "
                "Install it with: pip install reportlab"
            )
        
        self.epub_parser = epub_parser
        self.structure = epub_parser.structure
        
        if not self.structure:
            raise ValueError("EPUB parser must have extracted content before PDF conversion")
    
    def _get_combined_css(self) -> str:
        """Combine all CSS files from the EPUB into a single CSS string."""
        combined_css = []
        
        # Default CSS for better PDF formatting
        default_css = """
        @page {
            margin: 1in;
            size: A4;
        }
        
        body {
            font-family: "Noto Sans CJK SC", "Source Han Sans SC", sans-serif;
            font-size: 14pt;
            line-height: 1.4;
            color: #000;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #000;
            margin-top: 1em;
            margin-bottom: 0.5em;
            page-break-after: avoid;
        }
        
        h1 { font-size: 24pt; }
        h2 { font-size: 20pt; }
        h3 { font-size: 16pt; }
        h4 { font-size: 14pt; }
        h5 { font-size: 12pt; }
        h6 { font-size: 10pt; }
        
        p {
            margin-bottom: 1em;
            text-align: justify;
        }
        
        ruby {
            ruby-align: center;
        }
        
        rt {
            font-size: 0.7em;
            color: #666;
        }
        
        img {
            max-width: 100%;
            height: auto;
        }
        
        .page-break {
            page-break-before: always;
        }
        
        blockquote {
            margin: 1em 2em;
            padding-left: 1em;
            border-left: 3px solid #ccc;
        }
        """
        
        combined_css.append(default_css)
        
        # Add CSS from EPUB
        for css_item in self.structure.css_items:
            try:
                with open(css_item.abs_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                    combined_css.append(css_content)
            except Exception as e:
                print(f"Warning: Could not read CSS file {css_item.href}: {e}")
        
        return '\n'.join(combined_css)
    
    def _prepare_html_content(self, html_files: List[str]) -> str:
        """Prepare combined HTML content for PDF conversion.
        
        Args:
            html_files: List of HTML file paths in reading order
            
        Returns:
            Combined HTML content as string
        """
        combined_html = []
        
        # HTML document structure
        combined_html.append(f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <title>{self.structure.metadata.title}</title>
    <style>
{self._get_combined_css()}
    </style>
</head>
<body>
''')
        
        # Add title page
        combined_html.append(f'''
    <div class="title-page" style="text-align: center; margin: 2em 0 4em 0;">
        <h1 style="font-size: 32pt; margin-bottom: 1em;">{self.structure.metadata.title}</h1>
        <p style="font-size: 16pt; color: #666;">作者: {self.structure.metadata.creator}</p>
        <p style="font-size: 14pt; color: #666;">出版社: {self.structure.metadata.publisher}</p>
    </div>
    <div class="page-break"></div>
''')
        
        # Process each HTML file
        for i, html_file in enumerate(html_files):
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse HTML content
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract body content or fall back to entire content
                body = soup.find('body')
                if body:
                    # Remove any existing title tags within body
                    for title in body.find_all('title'):
                        title.decompose()
                    content_html = str(body)
                    # Remove body tags but keep content
                    content_html = content_html.replace('<body>', '').replace('</body>', '')
                else:
                    # If no body tag, extract everything except head
                    head = soup.find('head')
                    if head:
                        head.decompose()
                    html_tag = soup.find('html')
                    if html_tag:
                        content_html = str(html_tag)
                        content_html = content_html.replace('<html>', '').replace('</html>', '')
                    else:
                        content_html = str(soup)
                
                # Add page break between chapters (except for first)
                if i > 0:
                    combined_html.append('<div class="page-break"></div>')
                
                # Add content
                combined_html.append(f'    <div class="chapter" data-chapter="{i+1}">')
                combined_html.append(content_html)
                combined_html.append('    </div>')
                
            except Exception as e:
                print(f"Warning: Could not process HTML file {html_file}: {e}")
                continue
        
        combined_html.append('</body>\n</html>')
        
        return '\n'.join(combined_html)
    
    def _register_chinese_fonts(self):
        """Register Chinese fonts for PDF generation."""
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import platform
        import os
        
        # Try to find and register Chinese fonts
        font_paths = []
        
        # First, try to use the local fonts in the fonts directory
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        font_paths = [
             os.path.join(script_dir, "fonts", "SimSun.ttc"),
            os.path.join(script_dir, "fonts", "FangSong.ttf"),
            os.path.join(script_dir, "fonts", "STSong.ttf")
        ]
        
        # Register main Chinese font
        main_font_registered = False
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    if font_path.endswith('.ttc'):
                        # For TTC files, try different subfont indices
                        for i in range(4):  # Try first 4 subfonts
                            try:
                                pdfmetrics.registerFont(TTFont('ChineseFont', font_path, subfontIndex=i))
                                print(f"Registered Chinese font: {font_path} (subfont {i})")
                                main_font_registered = True
                                break
                            except Exception:
                                continue
                    else:
                        pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                        print(f"Registered Chinese font: {font_path}")
                        main_font_registered = True
                        break
                except Exception as e:
                    print(f"Failed to register font {font_path}: {e}")
                    continue
            if main_font_registered:
                break
        
        # Register pinyin font (using a different font for pinyin)
        pinyin_font_registered = False
        pinyin_font_paths = [
            os.path.join(script_dir, "fonts", "SimSun.ttc"),  # Fallback to SimSun
            os.path.join(script_dir, "fonts", "STSong.ttf"),  # Use STSong for pinyin
            os.path.join(script_dir, "fonts", "STHeiti Light.ttc"),  # Use STSong for pinyin
            os.path.join(script_dir, "fonts", "FangSong.ttf"),  # Fallback to FangSong
        ]
        
        for font_path in pinyin_font_paths:
            if os.path.exists(font_path):
                try:
                    if font_path.endswith('.ttc'):
                        # For TTC files, try different subfont indices
                        for i in range(4):  # Try first 4 subfonts
                            try:
                                pdfmetrics.registerFont(TTFont('PinyinFont', font_path, subfontIndex=i))
                                print(f"Registered Pinyin font: {font_path} (subfont {i})")
                                pinyin_font_registered = True
                                break
                            except Exception:
                                continue
                    else:
                        pdfmetrics.registerFont(TTFont('PinyinFont', font_path))
                        print(f"Registered Pinyin font: {font_path}")
                        pinyin_font_registered = True
                        break
                except Exception as e:
                    print(f"Failed to register pinyin font {font_path}: {e}")
                    continue
            if pinyin_font_registered:
                break
        
        if not main_font_registered:
            raise Exception("No Chinese fonts found")
        
        if not pinyin_font_registered:
            # If pinyin font registration failed, use the main font for pinyin too
            print("Warning: Could not register separate pinyin font, using main font for pinyin")
            pdfmetrics.registerFontFamily('PinyinFont', normal='ChineseFont')
    
    def _extract_ruby_elements(self, element):
        """Extract ruby elements and their structure from an HTML element.
        
        Args:
            element: BeautifulSoup element that may contain ruby tags
            
        Returns:
            List of dictionaries with text segments and ruby annotations
        """
        result = []
        element_copy = element.__copy__()
        
        # Find all ruby elements in the entire element tree
        ruby_elements = element_copy.find_all('ruby')
        

        if not ruby_elements:
            # No ruby elements, just return plain text
            text = element_copy.get_text(strip=True)
            if text:
                result.append({
                    'type': 'text',
                    'content': text
                })
            return result
        
        # Process the element by walking through its structure
        # and replacing ruby elements with our format
        for ruby in ruby_elements:
            # Extract ruby content
            base_text = ''
            pinyin_text = ''
            
            # Find base text and pinyin
            rt_element = ruby.find('rt')
            if rt_element:
                pinyin_text = rt_element.get_text(strip=True)
                # Remove rt element to get base text
                rt_element.decompose()
            
            base_text = ruby.get_text(strip=True)
            
            # Replace the ruby element with a special marker
            marker = f"__RUBY__{len(result)}__"
            ruby.replace_with(marker)
            
            if base_text:
                result.append({
                    'type': 'ruby',
                    'base_text': base_text,
                    'pinyin': pinyin_text
                })
        
        # Now get the text with markers and split it
        full_text = element_copy.get_text()
        
        # Split by ruby markers and rebuild the structure
        final_result = []
        current_text = full_text
        
        for i in range(len(result)):
            marker = f"__RUBY__{i}__"
            if marker in current_text:
                parts = current_text.split(marker, 1)
                
                # Add text before ruby (if any)
                if parts[0].strip():
                    final_result.append({
                        'type': 'text',
                        'content': parts[0].strip()
                    })
                
                # Add the ruby element
                final_result.append(result[i])
                
                # Continue with remaining text
                current_text = parts[1] if len(parts) > 1 else ''
        
        # Add any remaining text
        if current_text.strip():
            final_result.append({
                'type': 'text',
                'content': current_text.strip()
            })
        

        return final_result
    
    def _compress_continuous_punctuation(self, segments):
        """Compress continuous punctuation to use single character width."""
        if not segments:
            return segments
            
        compressed = []
        i = 0
        
        while i < len(segments):
            current_segment = segments[i]
            
            if current_segment['type'] == 'text' and len(current_segment['content']) == 1:
                # Check if this and next segments are both punctuation
                continuous_punct = current_segment['content']
                j = i + 1
                
                # Collect continuous punctuation
                while (j < len(segments) and 
                       segments[j]['type'] == 'text' and 
                       len(segments[j]['content']) == 1 and 
                       segments[j]['content'] in '。，！？；：""''（）【】《》'):
                    continuous_punct += segments[j]['content']
                    j += 1
                
                if len(continuous_punct) > 1:
                    # Compress multiple punctuation into one segment
                    compressed.append({
                        'type': 'text',
                        'content': continuous_punct,
                        'compressed_punctuation': True
                    })
                    i = j  # Skip all processed segments
                else:
                    # Single character, keep as is
                    compressed.append(current_segment)
                    i += 1
            else:
                # Non-punctuation segment, keep as is
                compressed.append(current_segment)
                i += 1
        
        return compressed
    
    def _split_long_segments(self, segments, max_segments=100):
        """Split very long segment lists into smaller chunks to avoid page overflow."""
        if len(segments) <= max_segments:
            return [segments]
        
        chunks = []
        current_chunk = []
        
        for segment in segments:
            current_chunk.append(segment)
            
            # Split at sentence boundaries when possible
            if (len(current_chunk) >= max_segments and 
                segment['type'] == 'text' and 
                any(punct in segment['content'] for punct in '。！？；')):
                chunks.append(current_chunk)
                current_chunk = []
        
        # Add remaining segments
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _create_ruby_flowable(self, segments, style):
        """Create a custom flowable that handles ruby text rendering.
        
        Args:
            segments: List of text segments with ruby annotations
            style: Text style to use
            
        Returns:
            RubyParagraph flowable
        """
        # Compress continuous punctuation before creating flowable
        segments = self._compress_continuous_punctuation(segments)
        from reportlab.platypus.flowables import Flowable
        from reportlab.lib.units import inch
        
        class RubyParagraph(Flowable):
            def __init__(self, segments, style):
                self.segments = segments
                self.style = style
                self.width = 0
                self.height = 0
                self.lines = []  # Store lines for wrapping
                self.uniform_char_width = 0  # Uniform width for all characters
                
            def _calculate_uniform_width(self):
                """Calculate uniform character width based on longest pinyin."""
                from reportlab.pdfbase.pdfmetrics import stringWidth
                
                max_base_width = 0
                max_pinyin_width = 0
                
                # Find the widest base character and longest pinyin
                for segment in self.segments:
                    if segment['type'] == 'ruby':
                        base_width = stringWidth(segment['base_text'], self.style.fontName, self.style.fontSize)
                        pinyin_width = stringWidth(segment['pinyin'], 'PinyinFont', self.style.fontSize * PINYIN_FONT_SIZE)
                        
                        max_base_width = max(max_base_width, base_width)
                        max_pinyin_width = max(max_pinyin_width, pinyin_width)
                
                # Set uniform character width to exactly 30 units
                self.uniform_char_width = CHAR_WIDTH
                
            def wrap(self, availWidth, availHeight):
                # Calculate uniform character width first
                self._calculate_uniform_width()
                
                # Calculate line wrapping
                from reportlab.pdfbase.pdfmetrics import stringWidth
                
                self.lines = []
                current_line = []
                current_width = 0
                line_height = self.style.fontSize * LINE_SPACE_TIMES  # Much more space to prevent line collisions
                
                for segment in self.segments:
                    if segment['type'] == 'ruby':
                        # Use uniform width for ruby segments
                        segment_width = self.uniform_char_width
                    else:
                        # Handle regular text - may need to split by characters for Chinese
                        text = segment['content']
                        
                        # For regular text, check if it needs character-by-character splitting
                        if any('\u4e00' <= char <= '\u9fff' for char in text) or any(char in '。，！？；：""''（）【】《》' for char in text):
                            # Contains Chinese characters or punctuation, split character by character
                            for char in text:
                                # Chinese characters and punctuation use uniform width
                                if '\u4e00' <= char <= '\u9fff' or char in '。，！？；：""''（）【】《》':
                                    char_width = self.uniform_char_width
                                else:
                                    char_width = stringWidth(char, self.style.fontName, self.style.fontSize)
                                
                                if current_width + char_width > availWidth:
                                    # Start new line
                                    if current_line:
                                        self.lines.append(current_line)
                                        current_line = []
                                        current_width = 0
                                
                                current_line.append({
                                    'type': 'text',
                                    'content': char,
                                    'width': char_width
                                })
                                current_width += char_width
                            continue
                        else:
                            # Handle compressed punctuation
                            if segment.get('compressed_punctuation', False):
                                # Multiple punctuation marks use only one character width
                                segment_width = self.uniform_char_width
                            else:
                                # Non-Chinese text, use actual width
                                segment_width = stringWidth(text, self.style.fontName, self.style.fontSize)
                            
                            # If text segment is too wide, split it character by character
                            if segment_width > availWidth and not segment.get('compressed_punctuation', False):
                                for char in text:
                                    char_width = stringWidth(char, self.style.fontName, self.style.fontSize)
                                    if current_width + char_width > availWidth:
                                        # Check if this character is forbidden punctuation at line start
                                        if (char in '。，！？；：''）】》' and current_line):
                                            # Don't start new line with punctuation, add to current line
                                            pass
                                        else:
                                            # Start new line
                                            if current_line:
                                                self.lines.append(current_line)
                                                current_line = []
                                                current_width = 0
                                    
                                    current_line.append({
                                        'type': 'text',
                                        'content': char,
                                        'width': char_width
                                    })
                                    current_width += char_width
                                continue
                    
                    # Check if current segment fits on current line
                    if current_width + segment_width > availWidth:
                        # Special handling for Chinese punctuation - don't leave it orphaned at line start
                        if (segment['type'] == 'text' and 
                            len(segment['content']) == 1 and 
                            segment['content'] in '。，！？；：''）】》' and  # Exclude opening quotes
                            current_line):
                            # Move one character from previous line to make room for punctuation
                            if len(current_line) > 1:
                                moved_segment = current_line.pop()
                                current_width -= moved_segment.get('width', segment_width)
                                # Start new line with moved segment
                                self.lines.append(current_line)
                                current_line = [moved_segment]
                                current_width = moved_segment.get('width', segment_width)
                            else:
                                # If only one item, still move to new line
                                self.lines.append(current_line)
                                current_line = []
                                current_width = 0
                        else:
                            # Normal line break
                            if current_line:
                                self.lines.append(current_line)
                                current_line = []
                                current_width = 0
                    
                    # Add width info to segment for later use
                    segment_copy = segment.copy()
                    segment_copy['width'] = segment_width
                    current_line.append(segment_copy)
                    current_width += segment_width
                
                # Add the last line
                if current_line:
                    self.lines.append(current_line)
                
                # Post-process lines to fix punctuation at line start
                self._fix_punctuation_at_line_start()
                
                # Calculate how many lines fit in available height
                max_lines = max(1, int(availHeight // line_height))
                
                if len(self.lines) <= max_lines:
                    # All lines fit
                    self.height = len(self.lines) * line_height
                    self.width = availWidth
                    return (self.width, self.height)
                else:
                    # Need to split - return what fits
                    self.lines = self.lines[:max_lines]
                    self.height = max_lines * line_height
                    self.width = availWidth
                    return (self.width, self.height)
            
            def _fix_punctuation_at_line_start(self):
                """Fix punctuation that appears at the start of lines."""
                # Chinese punctuation that should not appear at line start (except opening quotes)
                forbidden_start_punctuation = '，、；：——……”’）》？！！？…？…！—‧·/。'
                
                for i in range(len(self.lines) - 1):
                    current_line = self.lines[i]
                    next_line = self.lines[i + 1]
                    
                    # Check if next line starts with forbidden punctuation
                    if (next_line and 
                        next_line[0]['type'] == 'text' and 
                        len(next_line[0]['content']) == 1 and 
                        next_line[0]['content'] in forbidden_start_punctuation):
                        
                        # Move the punctuation to the end of current line
                        punctuation_segment = next_line.pop(0)
                        current_line.append(punctuation_segment)
                        
                        # If next line is now empty, remove it
                        if not next_line:
                            self.lines.pop(i + 1)
                
                # Also check for punctuation in ruby elements at line start
                for i in range(len(self.lines) - 1):
                    current_line = self.lines[i]
                    next_line = self.lines[i + 1]
                    
                    # Check if next line starts with ruby element that has forbidden punctuation
                    if (next_line and 
                        next_line[0]['type'] == 'ruby' and 
                        next_line[0]['base_text'] in forbidden_start_punctuation):
                        
                        # Move the ruby punctuation to the end of current line
                        punctuation_ruby = next_line.pop(0)
                        current_line.append(punctuation_ruby)
                        
                        # If next line is now empty, remove it
                        if not next_line:
                            self.lines.pop(i + 1)
            
            def split(self, availWidth, availHeight):
                """Split the flowable if it's too large for the available space."""
                # First, do a full wrap to calculate all lines
                line_height = self.style.fontSize * LINE_SPACE_TIMES
                self._calculate_uniform_width()
                
                # Calculate all lines (temporarily store original)
                original_lines = self.lines
                self.wrap(availWidth, 9999)  # Large height to get all lines
                all_lines = self.lines[:]
                
                # Calculate how many lines fit in available height
                max_lines = max(1, int(availHeight // line_height))
                
                if len(all_lines) <= max_lines:
                    # Everything fits, no split needed
                    return []
                
                # Create the part that fits on current page
                self.lines = all_lines[:max_lines]
                self.height = max_lines * line_height
                
                # Create continuation flowables for remaining lines
                continuations = []
                remaining_lines = all_lines[max_lines:]
                
                # Split remaining lines into chunks that fit on pages
                while remaining_lines:
                    # Calculate available height for continuation (full page minus margins)
                    cont_max_lines = max(1, int(availHeight // line_height))
                    
                    # Take the next chunk of lines
                    chunk_lines = remaining_lines[:cont_max_lines]
                    remaining_lines = remaining_lines[cont_max_lines:]
                    
                    # Check if chunk has actual content
                    has_content = False
                    for line in chunk_lines:
                        for segment in line:
                            if segment['type'] == 'text' and segment['content'].strip():
                                has_content = True
                                break
                            elif segment['type'] == 'ruby' and segment['base_text'].strip():
                                has_content = True
                                break
                        if has_content:
                            break
                    
                    # Only create continuation if there's actual content
                    if has_content:
                        cont_flowable = RubyParagraph([], self.style)
                        cont_flowable.segments = []  # Empty since we're setting lines directly
                        cont_flowable.uniform_char_width = self.uniform_char_width
                        cont_flowable.lines = chunk_lines
                        cont_flowable.height = len(chunk_lines) * line_height
                        cont_flowable.width = availWidth
                        
                        continuations.append(cont_flowable)
                
                return continuations
            
            def draw(self):
                from reportlab.pdfbase.pdfmetrics import stringWidth
                canvas = self.canv
                line_height = self.style.fontSize * LINE_SPACE_TIMES
                
                # Set font
                canvas.setFont(self.style.fontName, self.style.fontSize)
                
                # Draw each line
                for line_num, line_segments in enumerate(self.lines):
                    x = 0
                    # Ensure proper vertical spacing - start from top and work down
                    y = self.height - (line_num * line_height) - self.style.fontSize * 1.5  # Better baseline positioning
                    
                    for segment in line_segments:
                        if segment['type'] == 'ruby':
                            # Draw base text
                            base_text = segment['base_text']
                            pinyin_text = segment['pinyin']
                            
                            # Use uniform width for all ruby characters
                            char_width = self.uniform_char_width
                            
                            # Calculate actual text widths for centering
                            base_width = stringWidth(base_text, self.style.fontName, self.style.fontSize)
                            pinyin_width = stringWidth(pinyin_text, 'PinyinFont', self.style.fontSize * PINYIN_FONT_SIZE)
                            
                            # Draw base character (centered in uniform width)
                            canvas.drawString(x + (char_width - base_width) / 2, y, base_text)
                            
                            # Draw pinyin above (centered in uniform width)
                            if pinyin_text:
                                canvas.setFont('PinyinFont', self.style.fontSize * PINYIN_FONT_SIZE)
                                canvas.drawString(x + (char_width - pinyin_width) / 2, y + self.style.fontSize * 0.96, pinyin_text)  # Reduced by 20% (1.2 * 0.8 = 0.96)
                                canvas.setFont(self.style.fontName, self.style.fontSize)
                            
                            x += char_width
                        else:
                            # Draw regular text
                            text = segment['content']
                            segment_width = segment.get('width', stringWidth(text, self.style.fontName, self.style.fontSize))
                            
                            # Handle different text types
                            if segment.get('compressed_punctuation', False):
                                # Multiple punctuation in one character width - draw compressed
                                actual_width = stringWidth(text, self.style.fontName, self.style.fontSize)
                                canvas.drawString(x + (segment_width - actual_width) / 2, y, text)
                            elif len(text) == 1 and ('\u4e00' <= text <= '\u9fff' or text in '。，！？；：""''（）【】《》'):
                                # Single Chinese characters and punctuation, center them in uniform width
                                actual_width = stringWidth(text, self.style.fontName, self.style.fontSize)
                                canvas.drawString(x + (segment_width - actual_width) / 2, y, text)
                            else:
                                # Non-Chinese text, draw normally
                                canvas.drawString(x, y, text)
                            
                            x += segment_width
        
        return RubyParagraph(segments, style)
    
    def _is_nested_in_processed_element(self, element, processed_elements):
        """Check if an element is nested inside any already processed element."""
        for processed_elem in processed_elements:
            if element in processed_elem.descendants:
                return True
        return False
    def convert_to_pdf(self, output_path: str) -> None:
        """Convert the EPUB content to PDF.
        
        Args:
            output_path: Path where the PDF file will be saved
        """
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.colors import black
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import platform
        import re
        
        # Get HTML files in reading order
        html_files = self.epub_parser.get_html_files()
        
        if not html_files:
            raise ValueError("No HTML files found in EPUB")
        
        # Register Chinese fonts
        self._register_chinese_fonts()
        
        # Create PDF document with reduced margins to use more page width
        from reportlab.lib.units import inch
        doc = SimpleDocTemplate(
            output_path, 
            pagesize=A4,
            leftMargin=0.75*inch,    # Reduced from default 1 inch
            rightMargin=0.75*inch,   # Reduced from default 1 inch  
            topMargin=0.5*inch,    # Reduced from default 1 inch
            bottomMargin=0.5*inch  # Reduced from default 1 inch
        )
        styles = getSampleStyleSheet()
        story = []
        
        # Create custom styles with Chinese font support
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Center alignment
            fontName='ChineseFont',
        )
        
        chapter_style = ParagraphStyle(
            'ChapterTitle',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=12,
            spaceBefore=20,
            fontName='ChineseFont',
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=16,
            spaceAfter=6,
            alignment=0,  # Left alignment
            fontName='ChineseFont',
        )
        
        # Add title page
        story.append(Paragraph(self.structure.metadata.title, title_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"作者: {self.structure.metadata.creator}", body_style))
        story.append(Paragraph(f"出版社: {self.structure.metadata.publisher}", body_style))
        story.append(PageBreak())
        
        # Process each HTML file
        for i, html_file in enumerate(html_files):
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse HTML content
                soup = BeautifulSoup(content, 'html.parser')
                
                # print("file, ", html_file)
                # Extract text content, preserving some formatting
                body = soup.find('body') or soup
                processed_elements = set()

                # Process headings and paragraphs
                for element in body.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
                    # Skip elements that are nested inside other elements we've already processed
                    if self._is_nested_in_processed_element(element, processed_elements):
                        continue

                    # print(f"Element: {element}")
                    # Extract ruby elements and create appropriate flowables
                    segments = self._extract_ruby_elements(element)
                    if not segments:
                        continue
                    
                    # Mark this element as processed
                    processed_elements.add(element)

                    # Check if this element contains ruby annotations
                    has_ruby = any(seg['type'] == 'ruby' for seg in segments)
                    
                    if has_ruby:
                        # Split long segments into manageable chunks
                        segment_chunks = self._split_long_segments(segments)
                        
                        for chunk in segment_chunks:
                            # Use custom ruby flowable for elements with pinyin
                            if element.name.startswith('h'):
                                ruby_flowable = self._create_ruby_flowable(chunk, chapter_style)
                            else:
                                ruby_flowable = self._create_ruby_flowable(chunk, body_style)
                            
                            story.append(ruby_flowable)
                            
                            # Add small spacing between chunks if multiple chunks
                            if len(segment_chunks) > 1:
                                story.append(Spacer(1, 3))
                    else:
                        # Use regular paragraph for plain text
                        plain_text = ' '.join(seg['content'] for seg in segments if seg['type'] == 'text')
                        if plain_text:
                            if element.name.startswith('h'):
                                story.append(Paragraph(plain_text, chapter_style))
                            else:
                                story.append(Paragraph(plain_text, body_style))
                
                # Add page break between chapters (except for last)
                if i < len(html_files) - 1:
                    story.append(PageBreak())
                    
            except Exception as e:
                print(f"Warning: Could not process HTML file {html_file}: {e}")
                continue
        
        # Remove empty pages by filtering out empty flowables and unnecessary page breaks
        filtered_story = []
        consecutive_page_breaks = 0
        for i, item in enumerate(story):
            # Skip empty paragraphs and unnecessary page breaks
            if hasattr(item, '__class__'):
                if item.__class__.__name__ == 'Paragraph':
                    # Check if paragraph has content
                    if hasattr(item, 'text') and item.text.strip():
                        filtered_story.append(item)
                elif item.__class__.__name__ == 'RubyParagraph':
                    # Check if ruby paragraph has segments
                    if hasattr(item, 'segments') and item.segments:
                        filtered_story.append(item)
                elif item.__class__.__name__ == 'PageBreak':
                    # Only add page break if previous item exists and next item will exist
                    if (filtered_story and 
                        i < len(story) - 1 and 
                        any(self._has_content(story[j]) for j in range(i + 1, len(story)))):
                        # Check if there's actual content after this page break
                        has_content_after = False
                        for j in range(i + 1, len(story)):
                            if self._has_content(story[j]):
                                has_content_after = True
                                break
                        if has_content_after and consecutive_page_breaks < 1:
                            filtered_story.append(item)
                            consecutive_page_breaks += 1
                        else:
                            consecutive_page_breaks = 0
                elif item.__class__.__name__ == 'Spacer':
                    # Keep spacers only between content items
                    if filtered_story:
                        filtered_story.append(item)
                else:
                    # Keep other items as is
                    filtered_story.append(item)
                    consecutive_page_breaks = 0
            else:
                # Keep non-object items
                filtered_story.append(item)
        
        # Build PDF with filtered content
        if filtered_story:  # Only build if there's content
            doc.build(filtered_story)
        else:
            # Create minimal document if no content
            from reportlab.platypus import Paragraph
            minimal_story = [Paragraph("No content found", body_style)]
            doc.build(minimal_story)
    
    def _has_content(self, item):
        """Check if a story item has actual content."""
        if hasattr(item, '__class__'):
            if item.__class__.__name__ == 'Paragraph':
                return hasattr(item, 'text') and item.text.strip()
            elif item.__class__.__name__ == 'RubyParagraph':
                # Check if RubyParagraph has actual content in its lines
                if hasattr(item, 'lines') and item.lines:
                    for line in item.lines:
                        for segment in line:
                            if segment['type'] == 'text' and segment['content'].strip():
                                return True
                            elif segment['type'] == 'ruby' and segment['base_text'].strip():
                                return True
                    return False
                return hasattr(item, 'segments') and item.segments
            elif item.__class__.__name__ == 'PageBreak':
                return False  # PageBreak itself is not content
            elif item.__class__.__name__ == 'Spacer':
                return False  # Spacer itself is not content
        return True  # Assume other items have content
    
    @staticmethod
    def is_available() -> bool:
        """Check if PDF conversion is available (ReportLab installed).
        
        Returns:
            True if ReportLab is available, False otherwise
        """
        return _import_reportlab()


def convert_epub_to_pdf(epub_path: str, pdf_path: str) -> None:
    """Convert an EPUB file to PDF.
    
    Args:
        epub_path: Path to the input EPUB file
        pdf_path: Path where the output PDF will be saved
    """
    if not _import_reportlab():
        raise ImportError(
            "ReportLab is required for PDF conversion. "
            "Install it with: pip install reportlab"
        )
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract EPUB
        parser = EpubParser(temp_dir)
        parser.extract_epub(epub_path)
        
        # Convert to PDF
        converter = PdfConverter(parser)
        converter.convert_to_pdf(pdf_path)


def convert_epub_with_pinyin_to_pdf(epub_path: str, pdf_path: str) -> None:
    """Convert an EPUB file to PDF with pinyin annotations.
    
    Args:
        epub_path: Path to the input EPUB file
        pdf_path: Path where the output PDF will be saved
    """
    if not _import_reportlab():
        raise ImportError(
            "ReportLab is required for PDF conversion. "
            "Install it with: pip install reportlab"
        )
    
    from .text_processor import annotate_file_with_pinyin
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract EPUB
        parser = EpubParser(temp_dir)
        parser.extract_epub(epub_path)
        
        # Add pinyin annotations
        html_files = parser.get_html_files()
        for html_file in html_files:
            annotate_file_with_pinyin(html_file)
        
        # Convert to PDF
        converter = PdfConverter(parser)
        converter.convert_to_pdf(pdf_path)