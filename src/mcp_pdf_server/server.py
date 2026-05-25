from __future__ import annotations

from pathlib import Path
from typing import List

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pdf-docx-tools")


def _ensure_input_path(path_str: str) -> Path:
    path = Path(path_str).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Input path does not exist: {path}")
    return path


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


@mcp.tool()
def read_pdf_text(path: str) -> str:
    """Read all text from a PDF and return it as a single string."""
    pdf_path = _ensure_input_path(path)

    import fitz

    text_parts: List[str] = []
    with fitz.open(str(pdf_path)) as doc:
        for page in doc:
            text_parts.append(page.get_text())

    return "\n".join(text_parts).strip()


@mcp.tool()
def extract_pdf_images(path: str, output_dir: str) -> List[str]:
    """Extract images from a PDF and return output file paths."""
    pdf_path = _ensure_input_path(path)
    out_dir = Path(output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    import fitz

    output_paths: List[str] = []
    with fitz.open(str(pdf_path)) as doc:
        for page_index in range(len(doc)):
            page = doc[page_index]
            images = page.get_images(full=True)
            for image_index, img in enumerate(images, start=1):
                xref = img[0]
                base = doc.extract_image(xref)
                ext = base.get("ext", "bin")
                image_bytes = base["image"]
                filename = f"page_{page_index + 1}_img_{image_index}.{ext}"
                output_path = out_dir / filename
                with open(output_path, "wb") as handle:
                    handle.write(image_bytes)
                output_paths.append(str(output_path))

    return output_paths


@mcp.tool()
def pdf_to_docx(pdf_path: str, docx_path: str) -> str:
    """Convert a PDF file to DOCX."""
    source = _ensure_input_path(pdf_path)
    target = Path(docx_path).expanduser().resolve()
    _ensure_parent(target)

    from pdf2docx import Converter

    converter = Converter(str(source))
    try:
        converter.convert(str(target), start=0, end=None)
    finally:
        converter.close()

    return str(target)


@mcp.tool()
def docx_to_pdf(docx_path: str, pdf_path: str) -> str:
    """Convert a DOCX file to PDF."""
    source = _ensure_input_path(docx_path)
    target = Path(pdf_path).expanduser().resolve()
    _ensure_parent(target)

    from docx2pdf import convert

    convert(str(source), str(target))
    return str(target)


@mcp.tool()
def text_to_docx(text: str, docx_path: str) -> str:
    """Create a DOCX file from plain text."""
    target = Path(docx_path).expanduser().resolve()
    _ensure_parent(target)

    from docx import Document

    document = Document()
    for line in text.splitlines() or [""]:
        document.add_paragraph(line)
    document.save(str(target))

    return str(target)


@mcp.tool()
def text_or_html_to_pdf(content: str, pdf_path: str, content_type: str = "text") -> str:
    """Create a PDF from plain text or HTML."""
    target = Path(pdf_path).expanduser().resolve()
    _ensure_parent(target)

    if content_type.lower() == "html":
        try:
            from weasyprint import HTML
        except Exception as exc:  # pragma: no cover - runtime dependency check
            raise RuntimeError("weasyprint is required for HTML to PDF output") from exc

        HTML(string=content).write_pdf(str(target))
        return str(target)

    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    canvas_obj = canvas.Canvas(str(target), pagesize=letter)
    _, height = letter
    y = height - 72

    for line in content.splitlines() or [""]:
        if y < 72:
            canvas_obj.showPage()
            y = height - 72
        canvas_obj.drawString(72, y, line[:1000])
        y -= 14

    canvas_obj.save()
    return str(target)
