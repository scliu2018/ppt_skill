# ppt_skill

面向技术分享与非技术介绍的 PPT 技能库，重点收集世界模型相关课件。

仓库位置按用户指定为 `.agent/ppt_skill`，技能名为 `ppt-skill`。入口是 [SKILL.md](SKILL.md)。这是初版候选库，样例的最终风格选择尚待确认。

## 已包含

- 技术版：简洁版式、算法图解、实验与证据组织。
- 非技术版：更精美的场景、价值与融资叙事，另支持白底产品/方案介绍。
- 世界模型主题编排与 5 份国外课件的 [来源索引](references/catalog.md)。
- PDF 下载、校验、预览与本地确认页生成脚本。
- 原创 [设计参数](references/design-presets.json)，作为后续制作的起点。

当前没有制作可编辑 PPTX 母版。下载的 PDF 用于风格参考，不能直接当作可编辑的 PowerPoint 模板。

## 查看与确认

本机已准备好 [.local/REVIEW.md](.local/REVIEW.md)，内含 5 份技术课件和用户提供的 2 份案例，每份有原件入口和 9 页缩略图。原件分别放在 `.local/technical/` 和 `.local/nontechnical/`。

`.local/` 被 Git 忽略，GitHub 上不会显示这个本地链接的目标。公开仓库只包含技能、原创指南、来源信息和脚本，不包含用户案例、提取文本、来源课件或其截图。

## 使用技能

在支持项目技能目录的环境中，将仓库链接到项目的 `.agents/skills/ppt-skill`，或者在请求中给出 `SKILL.md` 路径。已有同名技能时先检查，不覆盖。

本项目示例，从工作区根目录执行：

```bash
mkdir -p .agents/skills
ln -s ../../.agent/ppt_skill .agents/skills/ppt-skill
```

示例请求：

> 使用 $ppt-skill，面向工程团队制作 20 分钟世界模型分享，采用简洁风格，重点解释方法与实验。

> 使用 $ppt-skill，面向非技术投资人制作技术项目介绍，参考我提供的案例，采用更精美的视觉，商业数字只使用我提供的数据。

若当前会话未重新加载技能，可直接指定仓库中的 `SKILL.md`。这个仓库不依赖机器特定的绝对路径。

## 下载和预览

Python 3.9+；下载工具没有额外 Python 依赖。预览需要 Pillow 和系统 Poppler（`pdfinfo`、`pdftoppm`）。优先使用已有运行时；缺少时安装相应依赖。

```bash
python3 scripts/fetch_references.py
python3 scripts/preview_pdf.py .local/technical/berkeley-model-based-rl-2023.pdf \
  --output .local/previews/berkeley-model-based-rl-2023 --pages 1,5,9,14,21,29,30,33,40
python3 scripts/build_review.py
```

下载器只接受清单内来源，下载到临时文件后检查 PDF 签名和已记录的 SHA-256。远端文件改变时会停止替换，需人工核对新版本后更新清单。确认页可在缺少预览或原件时生成，并明确标注缺项。

新机器不会自动获得用户的案例。可将获得授权的 PDF 放入 `.local/nontechnical/` 并创建 `.local/user-references.json`：

```json
{
  "sources": [{
    "id": "user-example",
    "title": "用户案例",
    "local_file": ".local/nontechnical/example.pdf",
    "pages": 10,
    "role": "风格参考",
    "review_pages": [1, 3, 6]
  }]
}
```

渲染时用 `.local/previews/user-example` 作为输出目录，再运行确认页生成脚本。
