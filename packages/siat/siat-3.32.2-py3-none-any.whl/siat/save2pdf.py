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
import tempfile
import subprocess
import nbformat
from nbconvert import HTMLExporter
import fitz           # PyMuPDF
from pathlib import Path

import contextlib
import io

import time
from IPython.display import display, Javascript

# —— 新增：Notebook 强制保存 —— 
def _save_current_notebook():
    """
    在浏览器端触发一次保存：兼容 Classic Notebook、Lab 3.x/4.x。
    """
    js = """
    (function() {
      // Classic Notebook
      if (window.Jupyter && Jupyter.notebook) {
        Jupyter.notebook.save_checkpoint();
      }
      // JupyterLab >=3: 用 app.commands
      else if (window.jupyterapp && jupyterapp.commands) {
        jupyterapp.commands.execute('docmanager:save');
      }
      // JupyterLab <=2 或其他
      else if (window.require) {
        require(['@jupyterlab/docmanager'], function(docManager) {
          docManager.save();
        });
      }
    })();
    """
    try:
        display(Javascript(js))
        time.sleep(0.5)   # 给浏览器一点时间写盘
    except Exception:
        pass
    
    
def ipynb2pdf(ipynb_path: str) -> str:
    """
    将 .ipynb 转为带可跳转目录书签的 PDF。
    返回生成的 PDF 文件路径。
    """
    # 0. 强制保存当前 Notebook，貌似不管用，还是需要手动保存当前的Notebook
    #print("Saving current ipynb ...")
    #_save_current_notebook()
    
    if not os.path.isfile(ipynb_path):
        raise FileNotFoundError(f"找不到文件：{ipynb_path}")
    output_pdf = ipynb_path[:-6] + ".pdf"

    print("Converting to PDF ...")

    # 1. 读 notebook → 提取目录
    nb = nbformat.read(ipynb_path, as_version=4)
    toc = _extract_toc(nb)

    # 2. nb → HTML（同时关闭图 alt 检查错误信息）
    exporter = HTMLExporter()
    buf = io.StringIO()
    # 屏蔽 stderr
    with contextlib.redirect_stderr(buf):
        html_body, _ = exporter.from_notebook_node(nb)

    # 3. 临时写 HTML / PDF
    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as th:
        th.write(html_body)
        html_path = th.name
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tp:
        tmp_pdf = tp.name

    # 4. Playwright 渲染 HTML → PDF（在子进程中调用 sync API，避开 Jupyter 的 asyncio loop）
    script = f"""
import sys
from playwright.sync_api import sync_playwright

p = sync_playwright().start()
browser = p.chromium.launch()
page = browser.new_page()
page.goto(r"file://{html_path}")
page.pdf(
    path=r"{tmp_pdf}",
    format="A3",
    print_background=True,
    margin={{"top":"20mm","bottom":"20mm","left":"20mm","right":"20mm"}}
)
browser.close()
p.stop()
"""
    subprocess.run([sys.executable, "-c", script], check=True)

    # 5. PyMuPDF 添加书签
    _add_bookmarks(tmp_pdf, output_pdf, toc)

    # 6. 清理临时文件
    os.unlink(html_path)
    os.unlink(tmp_pdf)

    # 打印结果
    full_path = Path(output_pdf)
    print(f"✅ {full_path.name} is created with TOC")
    print(f"✅ It is in {full_path.parent}")

    #return output_pdf
    return


def _extract_toc(nb_node) -> list[tuple[int, str]]:
    """
    从每个 markdown 单元首行提取 # 级别和标题文本，
    返回 [(level, title), …]
    """
    toc = []
    for cell in nb_node.cells:
        if cell.cell_type != "markdown":
            continue

        lines = cell.source.strip().splitlines()
        if not lines:
            # 空 Markdown 单元，跳过
            continue

        first = lines[0]
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
        # 搜索标题出现在第几页（0-based → +1）
        page_num = next(
            (i+1 for i in range(doc.page_count)
             if title in doc.load_page(i).get_text()),
            1
        )
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