# 项目结构概览

**生成日期**: 2025-01-15  
**项目版本**: v2.4

## 🗂️ 根目录结构

```
starcraft2-model/
├── README.md                    # 项目主文档
├── requirements.txt             # Python依赖
├── RELEASE_NOTES_v2.4.md        # v2.4发布说明
├── v24_project_summary.md       # 项目总结
├── run_v24_evaluation.py        # v2.4主评估程序
├── PROJECT_STRUCTURE_OVERVIEW.md # 本文档
├── .gitignore                   # Git配置
│
├── src/                         # 核心源代码
├── data/                        # 数据文件
├── tests/                       # 测试文件
├── tools/                       # 辅助工具
├── docs/                        # 项目文档
├── output/                      # 输出文件
├── archive/                     # 归档文件
└── .claude/                     # AI助手配置
```

## 📁 src/ - 核心源代码

```
src/
├── __init__.py
├── core/                        # 核心计算模块
│   ├── __init__.py
│   └── refined_cev_calculator.py    # v2.4精炼CEV计算器
│
├── data/                        # 数据处理模块
│   ├── __init__.py
│   ├── models.py                # 数据模型和精英单位数据
│   └── sac_loader.py            # SAC数据加载器
│
├── analysis/                    # 分析模块
│   ├── __init__.py
│   ├── tank_vs_dragoon_analysis.py  # 坦克vs龙骑士分析
│   └── ranking_analysis.py          # 排名分析
│
└── visualization/               # 可视化模块
    ├── __init__.py
    └── cev_charts.py            # CEV图表生成
```

## 📁 data/ - 数据文件

```
data/
├── elite_units.json                 # 精英单位数据
└── standard_amon_compositions.yaml  # SAC标准亚蒙组成
```

## 📁 tests/ - 测试系统

```
tests/
└── test_model_verification.py       # v2.4模型验证测试
```

## 📁 docs/ - 项目文档

```
docs/
├── project/                    # 项目管理文档
│   ├── PROJECT_STATUS.md       # 项目状态与进展
│   ├── PROJECT_STRUCTURE.md    # 项目结构规范
│   └── CLAUDE.md              # AI助手配置
│
├── technical/                  # 技术文档
│   ├── API_REFERENCE.md        # API使用指南
│   ├── DATABASE_SCHEMA.md      # 数据库设计
│   ├── DATA_GUIDE.md          # 数据收集指南
│   └── EVALUATION_METRICS.md   # 评估指标说明
│
├── specifications/             # 规范文档
│   ├── coding_spec.md          # 编码规范
│   └── modeling_spec.md        # 建模规范
│
├── paper/                      # 学术论文
│   ├── v24_paper_draft.md      # v2.4版本论文
│   ├── README.md               # 论文目录说明
│   └── versions/               # 历史版本归档
│
└── analysis/                   # 分析报告归档
    └── cev_gap_analysis_report.md
```

## 📁 tools/ - 工具脚本

```
tools/
└── paper_modification_helper.py     # 论文修改辅助工具
```

## 📁 output/ - 输出文件

```
output/
└── [运行时生成的结果文件]
```

## 📁 archive/ - 归档文件

```
archive/
├── data/                       # 历史数据归档
├── analysis_scripts/           # 历史分析脚本
├── benchmarks/                 # 基准测试归档
├── experiments/                # 实验记录归档
├── configs/                    # 配置文件归档
└── paper_modification_helper.py # 归档的工具脚本
```

## 🔑 关键文件说明

### 核心程序
- `run_v24_evaluation.py` - v2.4版本的主评估程序，提供交互式单位评估功能

### 核心算法
- `refined_cev_calculator.py` - 精炼的CEV计算器，包含溅射系数、操作难度等创新参数

### 数据文件
- `elite_units.json` - 六大精英单位的完整数据
- `standard_amon_compositions.yaml` - 标准亚蒙部队组成，用于目标评估

### 文档
- `README.md` - 项目主文档，包含快速开始指南
- `API_REFERENCE.md` - 详细的API使用文档
- `v24_paper_draft.md` - v2.4版本的学术论文

## ✅ 清理完成状态

- ✅ 删除了src/core中的所有旧版本计算器
- ✅ 删除了src/data中的冗余数据加载器
- ✅ 重建了standard_amon_compositions.yaml文件
- ✅ 保持了简洁的项目结构
- ✅ 所有目录都符合PROJECT_STRUCTURE.md规范

## 📊 项目统计

- **核心代码文件**: 7个
- **文档文件**: 15+个
- **测试文件**: 1个
- **数据文件**: 2个
- **总代码行数**: 约2000行（仅核心模块）

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行主程序
python run_v24_evaluation.py

# 运行测试
python -m tests.test_model_verification
```

---

*本文档由项目清理工具自动生成，反映了v2.4版本的最新项目结构。* 