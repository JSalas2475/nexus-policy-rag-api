import re
from pathlib import Path

from bs4 import BeautifulSoup
from pypdf import PdfReader


def parse_document(file_path: Path) -> list[dict]:
    suffix = file_path.suffix.lower()
    if suffix in {".md", ".markdown"}:
        return _parse_markdown(file_path)
    if suffix == ".txt":
        return _parse_text(file_path)
    if suffix in {".html", ".htm"}:
        return _parse_html(file_path)
    if suffix == ".pdf":
        return _parse_pdf(file_path)
    raise ValueError(f"Unsupported file type: {suffix}")


def _base_metadata(file_path: Path) -> dict:
    doc_id = file_path.stem
    return {
        "doc_id": doc_id,
        "title": doc_id.replace("-", " ").title(),
        "source_path": str(file_path.as_posix()),
    }


def _parse_markdown(file_path: Path) -> list[dict]:
    text = file_path.read_text(encoding="utf-8")
    sections = _split_by_headings(text)
    base = _base_metadata(file_path)
    return [
        {
            **base,
            "section": section["heading"] or "Introduction",
            "content": section["content"].strip(),
            "page_or_heading": section["heading"] or "Introduction",
        }
        for section in sections
        if section["content"].strip()
    ]


def _parse_text(file_path: Path) -> list[dict]:
    text = file_path.read_text(encoding="utf-8")
    base = _base_metadata(file_path)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        return []
    return [
        {
            **base,
            "section": f"Section {idx + 1}",
            "content": paragraph,
            "page_or_heading": f"Section {idx + 1}",
        }
        for idx, paragraph in enumerate(paragraphs)
    ]


def _parse_html(file_path: Path) -> list[dict]:
    html = file_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    base = _base_metadata(file_path)
    sections: list[dict] = []
    current_heading = "Introduction"
    buffer: list[str] = []

    for element in soup.find_all(["h1", "h2", "h3", "p", "li", "td"]):
        if element.name in {"h1", "h2", "h3"}:
            if buffer:
                sections.append(
                    {
                        **base,
                        "section": current_heading,
                        "content": "\n".join(buffer).strip(),
                        "page_or_heading": current_heading,
                    }
                )
                buffer = []
            current_heading = element.get_text(" ", strip=True)
        else:
            text = element.get_text(" ", strip=True)
            if text:
                buffer.append(text)

    if buffer:
        sections.append(
            {
                **base,
                "section": current_heading,
                "content": "\n".join(buffer).strip(),
                "page_or_heading": current_heading,
            }
        )

    return [section for section in sections if section["content"]]


def _parse_pdf(file_path: Path) -> list[dict]:
    reader = PdfReader(str(file_path))
    base = _base_metadata(file_path)
    sections: list[dict] = []
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()
        if not text:
            continue
        sections.append(
            {
                **base,
                "section": f"Page {page_num}",
                "content": text,
                "page_or_heading": f"Page {page_num}",
            }
        )
    return sections


def _split_by_headings(text: str) -> list[dict]:
    pattern = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    if not matches:
        return [{"heading": "Introduction", "content": text}]

    sections: list[dict] = []
    if matches[0].start() > 0:
        preamble = text[: matches[0].start()].strip()
        if preamble:
            sections.append({"heading": "Introduction", "content": preamble})

    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        heading = match.group(2).strip()
        content = text[start:end].strip()
        sections.append({"heading": heading, "content": content})

    return sections


def load_all_documents(policies_dir: Path) -> list[dict]:
    documents: list[dict] = []
    supported = {".md", ".markdown", ".txt", ".html", ".htm", ".pdf"}
    for file_path in sorted(policies_dir.rglob("*")):
        if file_path.is_file() and file_path.suffix.lower() in supported:
            documents.extend(parse_document(file_path))
    return documents
