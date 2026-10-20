#!/usr/bin/env python3
"""Build a local Markdown review index from source manifests and available previews."""
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / '.local'


def link(path):
    return quote(str(path.relative_to(LOCAL)), safe='/')


def section(source, label):
    pdf = (ROOT / source['local_file']).resolve()
    pdf.relative_to(LOCAL.resolve())
    preview_dir = LOCAL / 'previews' / source['id']
    preview = preview_dir / 'contact-sheet.jpg'
    title = source['title']
    lines = [f'## {label} · {title}', '', f"用途：{source.get('role', '风格参考')}。", '']
    if pdf.exists():
        lines += [f"[打开完整 PDF]({link(pdf)}) · {source.get('pages', '待核实')} 页 · {pdf.stat().st_size / 1024 / 1024:.1f} MiB", '']
    else:
        lines += ['原件尚未下载或导入。', '']
    if source.get('page_url'):
        lines += [f"[官方或作者来源]({source['page_url']})", '']
    if source.get('notes'):
        lines += [source['notes'], '']
    if preview.exists():
        lines += [f'![{label} 的代表页缩略图]({link(preview)})', '']
        meta = preview_dir / 'preview.json'
        if meta.exists():
            pages = json.loads(meta.read_text())['rendered_pages']
            lines += ['单页放大：' + ' · '.join(f'[p.{p}]({link(preview_dir / f"page-{p:03d}.png")})' for p in pages), '']
    else:
        lines += ['缩略图尚未生成，可运行 scripts/preview_pdf.py。', '']
    return lines


def main():
    public = json.loads((ROOT / 'references/sources.json').read_text())
    lines = [
        '# PPT 参考样例确认页', '',
        f"样例检索日期：{public['checked_on']}。当前选择状态：待你确认。", '',
        '技术版建议优先选择 T2（Berkeley 白底简洁），借鉴 T1 的架构图讲法。T4 更适合黑白强标题和动作条件视频入门。T3/T5 可作为算法和 Dreamer 编排补充。', '',
        '非技术版可优先参考 N1 的深蓝科技视觉；N2 是白底产品/技术方案风格，适合产业交流，面向非技术听众时应减少内容密度。', '',
        '这些文件都是原始 PDF 风格参考，尚未重建成可编辑 PPTX 母版。缩略图只覆盖每份选取的代表页，完整内容请打开 PDF。所有文件、截图和本页均保存在被 Git 忽略的本地目录。', '',
        '可确认：技术版偏好 T2 / T4 / T1；非技术版偏好 N1 深色 / N2 浅色 / 深色封面配浅色内容。也可以指定喜欢的具体页码。', ''
    ]
    for i, source in enumerate(public['sources'], 1):
        lines.extend(section(source, f'T{i}'))
    users = LOCAL / 'user-references.json'
    if users.exists():
        for i, source in enumerate(json.loads(users.read_text())['sources'], 1):
            lines.extend(section(source, f'N{i}'))
    else:
        lines += ['## 用户案例', '', '本机尚未配置用户案例；参见 README 中的本地导入方法。', '']
    LOCAL.mkdir(exist_ok=True)
    dest = LOCAL / 'REVIEW.md'
    dest.write_text('\n'.join(lines), encoding='utf-8')
    print(dest)


if __name__ == '__main__':
    main()
