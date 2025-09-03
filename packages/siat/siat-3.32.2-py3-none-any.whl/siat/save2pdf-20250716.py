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

#关闭所有警告
import warnings; warnings.filterwarnings('ignore')

# 能够在Python 3.13下运行了！
import os
import re
import sys
import time
import tempfile
import subprocess
import nbformat
from nbconvert import HTMLExporter
import fitz                    # PyMuPDF
from pathlib import Path
import contextlib
import io
from IPython import get_ipython
from ipykernel.zmqshell import ZMQInteractiveShell
from nbformat.notebooknode import NotebookNode
from playwright.sync_api import sync_playwright

# ----------------------------------------------------------------
# 1) 新增：把内存中的 NotebookNode 写到临时 .ipynb
# ----------------------------------------------------------------
def _dump_notebook_to_file(nb_node: NotebookNode) -> str:
    """
    把传进来的 NotebookNode（如 globals().get("__session__")）写到一个临时 .ipynb 文件，
    返回该临时文件的路径。
    """
    tf = tempfile.NamedTemporaryFile(
        suffix=".ipynb", delete=False, mode="w", encoding="utf-8"
    )
    nbformat.write(nb_node, tf)
    tf.flush()
    tf.close()
    return tf.name

# ----------------------------------------------------------------
# 2) 主函数：接受文件路径或 NotebookNode
# ----------------------------------------------------------------
def ipynb2pdf(source, *, temp_cleanup: bool = True) -> str:
    """
    将 .ipynb 转为带书签的 PDF，返回最终 PDF 路径。
    
    参数 source:
      - 如果是字符串，视为已有 .ipynb 文件的路径；
      - 如果是 NotebookNode，就把它 dump 到临时 .ipynb，再做后续处理。
    
    temp_cleanup：是否清理临时 .ipynb 文件，默认为 True。
    """
    # —— 如果传进来的是 NotebookNode，先 dump 到临时文件 —— 
    if isinstance(source, NotebookNode):
        ipynb_path = _dump_notebook_to_file(source)
        # 后面用完，最后再删
        cleanup_ipynb = temp_cleanup
    else:
        ipynb_path = str(source)
        cleanup_ipynb = False

    if not os.path.isfile(ipynb_path):
        raise FileNotFoundError(f"找不到文件：{ipynb_path}")
    output_pdf = ipynb_path[:-6] + ".pdf"

    print("Converting to PDF ...")

    # 3. 读内存/磁盘中的 notebook，提取 TOC
    nb = nbformat.read(ipynb_path, as_version=4)
    toc = _extract_toc(nb)

    # 4. 转 HTML，吞掉 alt‐text 警告
    exporter = HTMLExporter()
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        html_body, _ = exporter.from_notebook_node(nb)

    # 5. 写临时 HTML / PDF
    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as th:
        th.write(html_body)
        html_path = th.name
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tp:
        tmp_pdf = tp.name

    # 6. 子进程里用 Playwright 同步渲染 PDF
    script = f"""
import sys
from playwright.sync_api import sync_playwright
p = sync_playwright().start()
b = p.chromium.launch()
pg = b.new_page()
pg.goto(r"file://{html_path}")
pg.pdf(path=r"{tmp_pdf}", format="A3", print_background=True,
       margin={{"top":"20mm","bottom":"20mm","left":"20mm","right":"20mm"}})
b.close(); p.stop()
"""
    subprocess.run([sys.executable, "-c", script], check=True)

    # 7. 用 PyMuPDF 加书签
    _add_bookmarks(tmp_pdf, output_pdf, toc)

    # 8. 清理临时文件
    os.unlink(html_path)
    os.unlink(tmp_pdf)
    if cleanup_ipynb:
        os.unlink(ipynb_path)

    print(f"✅ {Path(output_pdf).name} created with TOC")
    print(f"✅ in {Path(output_pdf).parent}")
    return output_pdf

# ----------------------------------------------------------------
# 3) 工具函数：提取目录、写书签
# ----------------------------------------------------------------
def _extract_toc(nb_node) -> list[tuple[int, str]]:
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
    doc = fitz.open(input_pdf)
    outline = []
    for level, title in toc:
        pg = next(
            (i+1 for i in range(doc.page_count)
             if title in doc.load_page(i).get_text()),
            1
        )
        outline.append([level, title, pg])
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