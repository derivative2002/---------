# 论文目录说明

## 目录结构

根据项目规范 (`docs/project/PROJECT_STRUCTURE.md`)，本目录仅保留最终的论文草稿。

```
paper/
├── v24_paper_draft.md     # v2.4论文最终草稿 (Markdown)
├── README.md              # 本说明文件
└── versions/              # 历史版本与编译源文件归档
    └── v2.4/
        ├── v24_paper.tex
        ├── references.bib
        └── Makefile_v24
```

## v2.4 论文

**v2.4论文是当前项目最权威的学术成果。**

- **最终草稿**: `v24_paper_draft.md`
- **完整源文件**: 归档于 `versions/v2.4/` 目录，包含LaTeX版本、参考文献和Makefile，可用于编译生成PDF。

### 编译指南

如需编译PDF版本，请进入 `versions/v2.4/` 目录并使用 `Makefile_v24`。

## 历史版本

所有历史版本（如`v2.3`及更早版本）和其源文件都已归档在 `versions/` 目录中。

**重要声明**: 历史版本文件包含过时且不准确的数据，**请勿引用**。所有学术引用都应基于v2.4版本。

## 引用建议

如需引用本研究，请使用v2.4版本：

```bibtex
@article{sc2coop2025,
  title={基于精细化兰彻斯特-CEV模型的星际争霸II合作任务单位战斗效能评估},
  author={歪比歪比歪比巴卜},
  year={2025},
  version={v2.4},
  journal={星际争霸II合作模式研究}
}
```