from .docx import parse as parse_docx
from .pdf import parse as parse_pdf
from .xhtml import parse as parse_xhtml

__all__ = [
	'parse_docx',
	'parse_pdf',
	'parse_xhtml',
]