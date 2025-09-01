"""Module for handling EPUB file operations (extract, package, find files)."""

import os
import zipfile
import shutil
from dataclasses import dataclass
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from enum import Enum


class MediaType(Enum):
    """Enum for EPUB media types."""
    XHTML = "application/xhtml+xml"
    CSS = "text/css"
    NCX = "application/x-dtbncx+xml"
    JPEG = "image/jpeg"
    PNG = "image/png"
    GIF = "image/gif"
    SVG = "image/svg+xml"
    UNKNOWN = "unknown"

    @classmethod
    def from_string(cls, value: str) -> 'MediaType':
        """Convert string to MediaType."""
        try:
            return MediaType(value)
        except ValueError:
            return MediaType.UNKNOWN


@dataclass
class ManifestItem:
    """Class representing an item in the EPUB manifest."""
    id: str
    href: str
    media_type: MediaType
    abs_path: str  # Absolute path in the extracted EPUB


@dataclass
class EpubMetadata:
    """Class representing EPUB metadata."""
    title: str
    language: str
    creator: str
    publisher: str
    identifier: str


@dataclass
class EpubStructure:
    """Class representing the EPUB file structure."""
    metadata: EpubMetadata
    manifest_items: Dict[str, ManifestItem]  # id -> ManifestItem
    spine_order: List[str]  # List of manifest item IDs in spine order
    html_items: List[ManifestItem]  # HTML/XHTML items only
    ncx_item: Optional[ManifestItem]  # TOC NCX file
    css_items: List[ManifestItem]  # CSS files


class EpubParser:
    """Class for handling EPUB file operations."""

    def __init__(self, extract_dir: str):
        """Initialize EpubParser with extraction directory.
        
        Args:
            extract_dir: Directory where EPUB will be extracted/created
        """
        self.extract_dir = os.path.abspath(extract_dir)
        self.structure: Optional[EpubStructure] = None

    def _find_content_opf(self) -> Optional[str]:
        """Find content.opf file in the extracted EPUB."""
        # First check META-INF/container.xml
        container_path = os.path.join(self.extract_dir, "META-INF", "container.xml")
        if os.path.exists(container_path):
            try:
                with open(container_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'xml')
                    rootfile = soup.find('rootfile')
                    if rootfile and 'full-path' in rootfile.attrs:
                        opf_path = os.path.join(self.extract_dir, rootfile['full-path'])
                        if os.path.exists(opf_path):
                            return opf_path
            except Exception:
                pass

        # Fallback: search for content.opf
        for root, _, files in os.walk(self.extract_dir):
            if 'content.opf' in files:
                return os.path.join(root, 'content.opf')

        return None

    def _parse_metadata(self, metadata_tag) -> EpubMetadata:
        """Parse metadata from content.opf."""
        get_text = lambda tag, default="Unknown": tag.text if tag else default
        
        dc = metadata_tag.find_all(lambda tag: tag.prefix == 'dc')
        metadata = {}
        for tag in dc:
            metadata[tag.name] = tag.text

        return EpubMetadata(
            title=metadata.get('title', "Unknown Title"),
            language=metadata.get('language', "en"),
            creator=metadata.get('creator', "Unknown Author"),
            publisher=metadata.get('publisher', "Unknown Publisher"),
            identifier=metadata.get('identifier', "Unknown ID")
        )

    def _parse_content_opf(self, opf_path: str) -> EpubStructure:
        """Parse content.opf file."""
        opf_dir = os.path.dirname(opf_path)
        
        with open(opf_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'xml')

        # Parse metadata
        metadata = self._parse_metadata(soup.find('metadata'))

        # Parse manifest
        manifest_items = {}
        html_items = []
        css_items = []
        ncx_item = None

        for item in soup.find('manifest').find_all('item'):
            abs_path = os.path.join(opf_dir, item['href'])
            manifest_item = ManifestItem(
                id=item['id'],
                href=item['href'],
                media_type=MediaType.from_string(item['media-type']),
                abs_path=abs_path
            )
            manifest_items[item['id']] = manifest_item

            if manifest_item.media_type == MediaType.XHTML:
                html_items.append(manifest_item)
            elif manifest_item.media_type == MediaType.CSS:
                css_items.append(manifest_item)
            elif manifest_item.media_type == MediaType.NCX:
                ncx_item = manifest_item

        # Parse spine
        spine = soup.find('spine')
        spine_order = [item['idref'] for item in spine.find_all('itemref')] if spine else []

        return EpubStructure(
            metadata=metadata,
            manifest_items=manifest_items,
            spine_order=spine_order,
            html_items=html_items,
            ncx_item=ncx_item,
            css_items=css_items
        )

    def extract_epub(self, epub_path: str) -> None:
        """Extract the EPUB and parse its structure.
        
        Args:
            epub_path: Path to the input EPUB file
            
        Raises:
            ValueError: If content.opf is not found
        """
        # Create extraction directory
        if not os.path.exists(self.extract_dir):
            os.makedirs(self.extract_dir)

        # Extract the EPUB
        with zipfile.ZipFile(epub_path, 'r') as zip_ref:
            zip_ref.extractall(self.extract_dir)

        # Find and parse content.opf
        content_opf_path = self._find_content_opf()
        if not content_opf_path:
            raise ValueError("No content.opf found in EPUB. Invalid EPUB structure.")

        # Parse EPUB structure
        self.structure = self._parse_content_opf(content_opf_path)

    def get_html_files(self) -> List[str]:
        """Get list of HTML files in spine order.
        
        Returns:
            List of absolute paths to HTML files
        
        Raises:
            ValueError: If EPUB structure hasn't been parsed
        """
        if not self.structure:
            raise ValueError("EPUB structure not parsed. Call extract_epub() first.")

        # Get HTML files in spine order
        html_files = []
        for item_id in self.structure.spine_order:
            if item_id in self.structure.manifest_items:
                item = self.structure.manifest_items[item_id]
                if item.media_type == MediaType.XHTML:
                    html_files.append(item.abs_path)

        return html_files

    def get_css_files(self) -> List[str]:
        """Get list of CSS files.
        
        Returns:
            List of absolute paths to CSS files
        """
        if not self.structure:
            raise ValueError("EPUB structure not parsed. Call extract_epub() first.")
        
        return [item.abs_path for item in self.structure.css_items]

    def get_ncx_file(self) -> Optional[str]:
        """Get path to NCX file.
        
        Returns:
            Absolute path to NCX file or None if not found
        """
        if not self.structure or not self.structure.ncx_item:
            return None
        return self.structure.ncx_item.abs_path

    def package_epub(self, output_epub: str) -> None:
        """Package the modified files back into an EPUB.
        
        Args:
            output_epub: Path where the new EPUB will be saved
        """
        if os.path.exists(output_epub):
            os.remove(output_epub)

        with zipfile.ZipFile(output_epub, 'w') as zf:
            # Write mimetype with no compression
            mimetype_info = zipfile.ZipInfo("mimetype")
            mimetype_info.compress_type = zipfile.ZIP_STORED
            mimetype_path = os.path.join(self.extract_dir, "mimetype")
            if os.path.exists(mimetype_path):
                with open(mimetype_path, 'rb') as f:
                    zf.writestr(mimetype_info, f.read())
            else:
                zf.writestr(mimetype_info, "application/epub+zip")

            # Write the rest of the files with compression
            for root, _, files in os.walk(self.extract_dir):
                for file in files:
                    if file == "mimetype":
                        continue
                    filepath = os.path.join(root, file)
                    archive_name = os.path.relpath(filepath, self.extract_dir)
                    zf.write(filepath, archive_name)

    def cleanup(self) -> None:
        """Remove the temporary extraction directory."""
        if os.path.exists(self.extract_dir):
            shutil.rmtree(self.extract_dir) 