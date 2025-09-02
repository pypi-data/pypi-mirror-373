import logging
logger = logging.getLogger(__name__)

import io
import base64
from pydantic import BaseModel

import zipfile
import xml.etree.ElementTree as ET
import html as html_lib


class WordReaderArgs(BaseModel):
    file_path: str
    page_range: tuple[int, int] | None = None
    

class WordReaderFunction():
    def __init__(self, max_pages: int = 10, dpi: int = 200):      
        self.max_pages = max_pages
        self.dpi = dpi
    
    
    def __call__(self, **kwargs) -> dict:
        args = WordReaderArgs(**kwargs)
        return {"text": read_word(args.file_path, args.page_range)}
    
    
def read_word(filepath: str, page_range: tuple[int, int] | None = None) -> str:
    """Read a .docx file and return simple HTML for the requested page range.

    Notes on pages: .docx does not have a fixed page concept. We approximate
    pages by detecting explicit page breaks (w:br w:type="page") and certain
    section breaks. If no explicit breaks exist, the whole document is treated
    as a single page.
    """
    # Namespaces used in .docx XML
    W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    NS = {"w": W_NS, "r": R_NS}

    def _attrib(elem, local_name: str):
        return elem.get(f"{{{W_NS}}}{local_name}")

    def _attrib_rel(elem, local_name: str):
        return elem.get(f"{{{R_NS}}}{local_name}")

    def _flush_page(pages_list: list[str], current_parts: list[str]) -> None:
        html = "".join(current_parts).strip()
        if html:
            pages_list.append(html)
        current_parts.clear()

    def _wrap(tag: str, content: str) -> str:
        return f"<{tag}>{content}</{tag}>"

    def _style_to_heading_tag(p_elem) -> str | None:
        ppr = p_elem.find("w:pPr", NS)
        if ppr is None:
            return None
        pstyle = ppr.find("w:pStyle", NS)
        if pstyle is None:
            return None
        val = _attrib(pstyle, "val") or ""
        if not val:
            return None
        val_lower = val.lower()
        for i in range(1, 7):
            if val_lower in (f"heading{i}", f"h{i}"):
                return f"h{i}"
        return None

    # Simple file type check
    if not str(filepath).lower().endswith(".docx"):
        raise ValueError("Unsupported file type. Only .docx is supported.")

    # Build relationships map for hyperlinks
    rels_map: dict[str, str] = {}
    with zipfile.ZipFile(filepath) as zf:
        with zf.open("word/document.xml") as doc_xml:
            root = ET.fromstring(doc_xml.read())

        try:
            with zf.open("word/_rels/document.xml.rels") as rels_xml:
                rels_root = ET.fromstring(rels_xml.read())
                for rel in rels_root.findall(".//", {}):
                    # relationship elements generally have tag ending with 'Relationship'
                    if rel.tag.endswith("Relationship"):
                        rid = rel.get("Id")
                        target = rel.get("Target")
                        if rid and target:
                            rels_map[rid] = target
        except KeyError:
            # relationships file may not exist
            rels_map = {}

    body = root.find("w:body", NS)
    if body is None:
        return ""

    pages: list[str] = []
    current: list[str] = []

    # Iterate paragraphs and tables in document order; extract HTML and detect page breaks
    for child in list(body):
        tag = child.tag
        if tag == f"{{{W_NS}}}p":  # paragraph
            # Page break before paragraph?
            ppr = child.find("w:pPr", NS)
            if ppr is not None and ppr.find("w:pageBreakBefore", NS) is not None:
                _flush_page(pages, current)

            # Determine paragraph wrapper (heading vs paragraph)
            heading_tag = _style_to_heading_tag(child)
            para_inner_parts: list[str] = []

            # Walk paragraph children to preserve hyperlinks and line breaks
            for pel in list(child):
                if pel.tag == f"{{{W_NS}}}r":  # run
                    rpr = pel.find("w:rPr", NS)
                    is_bold = rpr is not None and rpr.find("w:b", NS) is not None
                    is_italic = rpr is not None and rpr.find("w:i", NS) is not None
                    is_underline = rpr is not None and rpr.find("w:u", NS) is not None

                    # handle breaks first
                    for br in pel.findall("w:br", NS):
                        br_type = _attrib(br, "type")
                        if br_type == "page":
                            # flush current paragraph content to page and start new page
                            if para_inner_parts:
                                content = "".join(para_inner_parts)
                                if heading_tag:
                                    current.append(_wrap(heading_tag, content))
                                else:
                                    current.append(_wrap("p", content))
                                para_inner_parts.clear()
                            _flush_page(pages, current)
                        else:
                            para_inner_parts.append("<br/>")

                    # text nodes
                    r_text_parts: list[str] = []
                    for t in pel.findall("w:t", NS):
                        if t.text:
                            r_text_parts.append(html_lib.escape(t.text))
                    r_text = "".join(r_text_parts)
                    if r_text:
                        if is_bold:
                            r_text = _wrap("strong", r_text)
                        if is_italic:
                            r_text = _wrap("em", r_text)
                        if is_underline:
                            r_text = f"<u>{r_text}</u>"
                        para_inner_parts.append(r_text)

                elif pel.tag == f"{{{W_NS}}}hyperlink":
                    href = None
                    rid = _attrib_rel(pel, "id")
                    if rid and rid in rels_map:
                        href = rels_map.get(rid)
                    anchor = _attrib(pel, "anchor")
                    if href is None and anchor:
                        href = f"#{html_lib.escape(anchor)}"
                    link_text_parts: list[str] = []
                    for run in pel.findall("w:r", NS):
                        for t in run.findall("w:t", NS):
                            if t.text:
                                link_text_parts.append(html_lib.escape(t.text))
                    link_text = "".join(link_text_parts)
                    if link_text:
                        if href:
                            para_inner_parts.append(f"<a href=\"{html_lib.escape(href)}\">{link_text}</a>")
                        else:
                            para_inner_parts.append(link_text)

            # Wrap paragraph content
            if para_inner_parts:
                content = "".join(para_inner_parts)
                if heading_tag:
                    current.append(_wrap(heading_tag, content))
                else:
                    current.append(_wrap("p", content))

            # Section properties within the paragraph can imply a page break after
            if ppr is not None and ppr.find("w:sectPr", NS) is not None:
                _flush_page(pages, current)

        elif tag == f"{{{W_NS}}}tbl":  # table → render as simple HTML table
            rows_html: list[str] = []
            for row in child.findall(".//w:tr", NS):
                cells_html: list[str] = []
                for cell in row.findall(".//w:tc", NS):
                    # gather paragraph texts inside the cell
                    cell_parts: list[str] = []
                    for p in cell.findall(".//w:p", NS):
                        p_text_parts: list[str] = []
                        for t in p.findall(".//w:t", NS):
                            if t.text:
                                p_text_parts.append(html_lib.escape(t.text))
                        if p_text_parts:
                            cell_parts.append("".join(p_text_parts))
                    cell_html = "<br/>".join(cell_parts)
                    cells_html.append(f"<td>{cell_html}</td>")
                rows_html.append(f"<tr>{''.join(cells_html)}</tr>")
            table_html = f"<table>{''.join(rows_html)}</table>"
            current.append(table_html)

        elif tag == f"{{{W_NS}}}sectPr":
            # section break at body level – treat as a page break
            _flush_page(pages, current)

    # Flush remaining content
    _flush_page(pages, current)

    if not pages:
        return ""

    total_pages = len(pages)

    # Handle page range (1-based, inclusive)
    if page_range is None:
        start_page, end_page = 1, total_pages
    else:
        start_page, end_page = page_range
        if start_page < 1 or end_page < 1:
            raise ValueError("Page range must be positive")
        if start_page > end_page:
            raise ValueError("Start page larger than end page")
        if start_page > total_pages or end_page > total_pages:
            return f"Valid page range of this Word document is 1 to {total_pages}"

    selected = pages[start_page - 1 : end_page]
    return "\n".join(selected)