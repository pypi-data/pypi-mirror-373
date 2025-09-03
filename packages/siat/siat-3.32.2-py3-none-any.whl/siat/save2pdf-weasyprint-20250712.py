# -*- coding: utf-8 -*-
"""
本模块功能：转换ipynb文件为pdf，带有可跳转的目录（目前一级标题定位还不准确，二级以下目录定位较准确，但已可用）
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2025年7月8日
最新修订日期：2025年7月8日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""

#==============================================================================

# 首次运行前，请安装依赖：
# !pip install nbformat nbconvert weasyprint pymupdf nest_asyncio
# !playwright install

import os
import re
import tempfile
import nbformat
from nbconvert import HTMLExporter
from weasyprint import HTML, CSS
import fitz  # PyMuPDF

def ipynb2pdf(ipynb_path: str) -> str:
    """
    将 .ipynb 转为带可跳转目录书签的 PDF。
    返回生成的 PDF 文件路径。
    """
    if not os.path.isfile(ipynb_path):
        raise FileNotFoundError(f"找不到文件：{ipynb_path}")
    output_pdf = ipynb_path[:-6] + ".pdf"

    print(f"📄 正在转换为 PDF ...")

    # 1. 读取 notebook → 提取目录结构
    nb = nbformat.read(ipynb_path, as_version=4)
    toc = _extract_toc(nb)

    # 2. notebook → HTML
    exporter = HTMLExporter()
    html_body, _ = exporter.from_notebook_node(nb)

    # 3. 写入临时 HTML 文件
    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as th:
        th.write(html_body)
        html_path = th.name

    # 4. 使用 WeasyPrint 渲染 HTML → PDF
    tmp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name
    _html_to_pdf(html_path, tmp_pdf)

    # 5. 使用 PyMuPDF 添加书签
    _add_bookmarks(tmp_pdf, output_pdf, toc)

    # 6. 清理临时文件
    os.unlink(html_path)
    os.unlink(tmp_pdf)

    print(f"✅ PDF 已生成：{output_pdf}")
    return output_pdf

def _html_to_pdf(html_path: str, pdf_path: str):
    """
    使用 WeasyPrint 将 HTML 渲染为 PDF。
    """
    HTML(filename=html_path).write_pdf(
        pdf_path,
        stylesheets=[CSS(string="""
            @page {
                size: A4;
                margin: 20mm;
            }
            body {
                font-family: 'Arial', sans-serif;
                line-height: 1.6;
            }
        """)]
    )

def _extract_toc(nb_node) -> list[tuple[int, str]]:
    """
    从每个 markdown 单元首行提取 # 级别和标题文本，
    返回 [(level, title), …]
    """
    toc = []
    for cell in nb_node.cells:
        if cell.cell_type != "markdown":
            continue
        first = cell.source.strip().splitlines()[0]
        m = re.match(r"^(#{1,6})\s+(.*)", first)
        if m:
            toc.append((len(m.group(1)), m.group(2).strip()))
    return toc

def _add_bookmarks(input_pdf: str, output_pdf: str, toc: list[tuple[int, str]]):
    """
    用 PyMuPDF 打开临时 PDF，按 toc 列表查找页码，
    然后用 set_toc() 批量写入书签。
    """
    doc = fitz.open(input_pdf)
    outline = []
    for level, title in toc:
        page_num = 1
        for i in range(doc.page_count):
            if title in doc.load_page(i).get_text():
                page_num = i + 1
                break
        outline.append([level, title, page_num])
    doc.set_toc(outline)
    doc.save(output_pdf)


# 使用示例（另起一个 cell 运行）：
# ipynb = globals().get("__session__")
# ipynb2pdf(ipynb)


#==============================================================================

#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================