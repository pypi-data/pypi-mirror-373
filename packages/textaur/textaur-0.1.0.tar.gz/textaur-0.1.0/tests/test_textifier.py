import os
import sys
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from textaur.core.textifier import Textifier, PDF_MAGIC_HEADER, FileType
from unittest.mock import patch, mock_open, MagicMock
from pdfminer.layout import LTTextContainer, LTTextLineHorizontal

mock_open_pdf = mock_open(read_data=PDF_MAGIC_HEADER)
mock_text_content = "mock text content"
mock_open_text = mock_open(read_data=mock_text_content)
mock_extracted_pages = ["first page", "second_page"]
mock_extract_pages = lambda x: mock_extracted_pages

class TestFiletype:
    textifier = Textifier(log=lambda x: x, progress_fn=None)

    def test_gets_pdf_filetype(self):
        with patch("builtins.open", mock_open_pdf):
            filetype = self.textifier.filetype(Path("whatever"))
        assert filetype == FileType.PDF


    def test_gets_text_filetype(self):
        with patch("builtins.open", mock_open_text):
            filetype = self.textifier.filetype(Path("whatever"))
        assert filetype == FileType.TEXT


    def test_gets_text_filetype(self):
        with patch("builtins.open", mock_open_text):
            filetype = self.textifier.filetype(Path("whatever"))
        assert filetype == FileType.TEXT


class TestExtractText:
    textifier = Textifier(log=lambda x: x, progress_fn=None)

    def test_extract_text_with_text_file(self):
        with patch("builtins.open", mock_open_text):
            file = self.textifier.extract_text(
                file=Path("whatever"),
                use_ocr=False,
            )
        assert file.filetype == FileType.TEXT
        assert file.pages == None
        assert file.text == mock_text_content


    def test_direct_pdf_extraction(self):
        res = ["expected", "pdf", "pages"]
        with (
            patch("builtins.open", mock_open_pdf),
            patch("textaur.core.textifier.Textifier.text_from_pdf_extraction", return_value=res)
        ):
            file = self.textifier.extract_text(
                file=Path("whatever"),
                use_ocr=False,
            )
        assert file.filetype == FileType.PDF
        assert file.pages == res


    def test_pdf_ocr_extraction(self):
        res = ["expected", "pdf", "pages"]
        with (
            patch("builtins.open", mock_open_pdf),
            patch("textaur.core.textifier.Textifier.text_from_pdf_ocr", return_value=res)
        ):
            file = self.textifier.extract_text(
                file=Path("whatever"),
                use_ocr=True,
            )
        assert file.filetype == FileType.PDF
        assert file.pages == res


class TestPdfTextExtractionWithoutOCR:
    textifier = Textifier()

    def test_text_from_pdf_extraction(self):
        fake_line1 = MagicMock(y0=200, get_text=lambda: "Hello Cruel ")
        fake_line2 = MagicMock(y0=100, get_text=lambda: "World")
        fake_line1.__class__ = LTTextLineHorizontal
        fake_line2.__class__ = LTTextLineHorizontal
        fake_container = MagicMock(spec=LTTextContainer)
        fake_container.__iter__.return_value = [fake_line1, fake_line2]

        with patch("textaur.core.textifier.extract_pages", return_value=[[fake_container]]):
            pages = self.textifier.text_from_pdf_extraction(file=Path("whatever"))

        assert isinstance(pages, list)
        assert len(pages) == 1
        assert pages[0] == "Hello Cruel World"


class TestPdfTextExtractionWithOCR:
    textifier = Textifier()

    def test_text_from_pdf_ocr(self):
        converted_pages = ["converted", "pages"]

        with (
            patch("textaur.core.textifier.convert_from_path", return_value=converted_pages),
            patch("textaur.core.textifier.pytesseract.image_to_string", lambda x: x)
        ):
            pages = self.textifier.text_from_pdf_ocr(file=Path("whatever"))

        assert pages == converted_pages

