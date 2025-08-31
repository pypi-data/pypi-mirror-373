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
# !pip install nbformat nbconvert playwright pymupdf nest_asyncio
# !playwright install

# 针对Python 3.13在Windows下的修复
# 在 Notebook 首格运行：
import sys, asyncio

if sys.platform.startswith("win"):
    # SelectorEventLoop 无法启动 subprocess，改用 ProactorEventLoop
    asyncio.set_event_loop_policy(
        asyncio.WindowsProactorEventLoopPolicy()
    )


# 下面在Python < 3.13可正常运行
import os
import re
import tempfile
import asyncio

import nest_asyncio
import nbformat
from nbconvert import HTMLExporter
from playwright.async_api import async_playwright
import fitz  # PyMuPDF

nest_asyncio.apply()  # 使 asyncio.run 在 Notebook 中可用

def ipynb2pdf(ipynb_path: str) -> str:
    """
    将 .ipynb 转为带可跳转目录书签的 PDF。
    返回生成的 PDF 文件路径。
    """
    if not os.path.isfile(ipynb_path):
        raise FileNotFoundError(f"找不到文件：{ipynb_path}")
    output_pdf = ipynb_path[:-6] + ".pdf"

    print(f"Converting to PDF ...")

    # 1. 读 notebook → 提取目录结构
    nb = nbformat.read(ipynb_path, as_version=4)
    toc = _extract_toc(nb)

    # 2. nb → HTML
    exporter = HTMLExporter()
    html_body, _ = exporter.from_notebook_node(nb)

    # 3. 临时写 HTML / PDF
    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as th:
        th.write(html_body)
        html_path = th.name
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tp:
        tmp_pdf = tp.name

    # 4. Playwright 渲染 HTML → PDF
    asyncio.run(_html_to_pdf(html_path, tmp_pdf))

    # 5. PyMuPDF 添加书签
    _add_bookmarks(tmp_pdf, output_pdf, toc)

    # 6. 清理
    os.unlink(html_path)
    os.unlink(tmp_pdf)

    from pathlib import Path
    full_path = Path(output_pdf)
    # 提取文件名
    filename = full_path.name  # 'report.pdf'
    # 提取路径
    directory = full_path.parent  # PosixPath('/Users/peter/Documents')
    
    print(f"✅ {filename} is created with TOC")
    print(f"✅ It is in {directory}")
    
    #return output_pdf
    return

#==============================================================================
"""
# 异步版本1
async def _html_to_pdf(html_path: str, pdf_path: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"file://{html_path}")
        await page.pdf(
            path=pdf_path,
            #format="A4",
            format="A3",
            print_background=True,
            margin={"top":"20mm","bottom":"20mm","left":"20mm","right":"20mm"},
        )
        await browser.close()
"""
import nest_asyncio
import asyncio
from playwright.async_api import async_playwright

nest_asyncio.apply()

async def _html_to_pdf(html_path: str, pdf_path: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"file://{html_path}")
        await page.pdf(
            path=pdf_path,
            format="A3",
            print_background=True,
            margin={"top": "20mm", "bottom": "20mm", "left": "20mm", "right": "20mm"},
        )
        await browser.close()



"""
# 同步版本：不能在Jupyter中使用
from playwright.sync_api import sync_playwright

def _html_to_pdf(html_path: str, pdf_path: str):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file://{html_path}")
        page.pdf(
            path=pdf_path,
            format="A3",
            print_background=True,
            margin={"top": "20mm", "bottom": "20mm", "left": "20mm", "right": "20mm"},
        )
        browser.close()
"""
#==============================================================================

def _extract_toc(nb_node) -> list[tuple[int,str]]:
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

def _add_bookmarks(input_pdf: str, output_pdf: str, toc: list[tuple[int,str]]):
    """
    用 PyMuPDF 打开临时 PDF，按 toc 列表查找页码，
    然后用 set_toc() 批量写入书签。
    """
    doc = fitz.open(input_pdf)
    outline = []
    for level, title in toc:
        page_num = 1
        # 搜索标题出现在第几页（0-based → +1）
        for i in range(doc.page_count):
            if title in doc.load_page(i).get_text():
                page_num = i + 1
                break
        outline.append([level, title, page_num])

    # 批量设置目录书签
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