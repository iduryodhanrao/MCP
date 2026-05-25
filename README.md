# MCP PDF and DOCX Server

This MCP server provides tools to read PDFs, extract images, convert PDF to DOCX, create DOCX from text, and generate PDFs from DOCX or text or HTML.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```powershell
pip install -e .
```

## Run (stdio)

```powershell
python -m mcp_pdf_server
```

## VS Code Copilot MCP

If you want Copilot Agents to auto-install and run this server, use `uvx` in your MCP config:

```json
{
	"servers": {
		"pdf-docx-tools": {
			"type": "stdio",
			"command": "uvx",
			"args": ["--from", "git+https://github.com/iduryodhanrao/MCP.git", "python", "-m", "mcp_pdf_server"]
		}
	}
}
```

This requires `uv`/`uvx` to be installed on the machine.

## Notes

- DOCX to PDF conversion uses `docx2pdf`. On Windows, this requires Microsoft Word to be installed.
- HTML to PDF uses `weasyprint`. On Windows, additional system libraries may be required.

## Tools

- `read_pdf_text(path)` -> string
- `extract_pdf_images(path, output_dir)` -> list of image paths
- `pdf_to_docx(pdf_path, docx_path)` -> docx path
- `docx_to_pdf(docx_path, pdf_path)` -> pdf path
- `text_to_docx(text, docx_path)` -> docx path
- `text_or_html_to_pdf(content, pdf_path, content_type)` -> pdf path
