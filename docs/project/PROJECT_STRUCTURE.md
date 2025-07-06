# 项目结构

**最后更新**: 2025-01-15 (v2.4项目清理后)

本文档详细说明了星际争霸II合作任务单位数学模型项目的目录结构和文件组织。

## 目录结构概览

```
starcraft2-model/
├── README.md                    # 项目主文档
├── requirements.txt             # Python依赖
├── RELEASE_NOTES_v2.4.md        # v2.4发布说明
├── v24_project_summary.md       # 项目总结
├── run_v24_evaluation.py        # v2.4主评估程序
├── .gitignore                   # Git配置
│
├── src/                         # 核心源代码
├── data/                        # 数据文件
├── tests/                       # 测试文件
├── tools/                       # 辅助工具
├── docs/                        # 项目文档
├── experiments/                 # 实验记录
├── benchmarks/                  # 基准测试
├── notebooks/                   # Jupyter笔记本
├── configs/                     # 配置文件
└── output/                      # 输出文件
```

## 详细目录说明

### 📁 src/ - 核心源代码

```
src/
├── core/                        # 核心计算模块
│   └── refined_cev_calculator.py       # v2.4精炼CEV计算器
│
├── data/                        # 数据处理模块
│   ├── models.py                # 数据模型和精英单位数据
│   └── sac_loader.py            # SAC数据加载器
│
├── analysis/                    # 分析模块
│   ├── tank_vs_dragoon_analysis.py     # 坦克vs龙骑士分析
│   ├── ranking_analysis.py             # 排名分析
│   ├── v23_paper_data_generator.py     # v2.3论文数据生成
│   └── [其他分析脚本]
│
└── visualization/               # 可视化模块
    └── cev_charts.py            # CEV图表生成
```

### 📁 data/ - 数据文件

```
data/
├── elite_units.json            # 精英单位数据
└── standard_amon_compositions.yaml  # SAC数据
```

### 📁 tests/ - 测试系统

```
tests/
└── test_model_verification.py  # v2.4模型验证测试
```

### 📁 docs/ - 项目文档

```
docs/
├── project/                    # 项目管理文档
│   ├── PROJECT_STATUS.md       # 项目状态与进展
│   ├── PROJECT_STRUCTURE.md    # 本文档
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
│   └── v24_paper_draft.md      # v2.4版本论文
│
└── analysis/                   # 分析报告归档
    └── [分析报告文件]
```

### 📁 tools/ - 工具脚本

```
tools/
├── data_collection/            # 数据收集工具
│   └── [脚本待添加]
│
├── data_maintenance/           # 数据维护工具
│   ├── import_coop_data.py     # 数据导入
│   ├── correct_focus_data.py   # 数据修正
│   └── data_verification.py    # 数据验证
│
└── paper_helpers/              # 论文辅助工具
    └── paper_modification_helper.py
```

## 关键文件说明

### 主程序
- **run_v24_evaluation.py** - v2.4单位评估主程序，支持交互式评估

### 核心算法
- **refined_cev_calculator.py** - v2.4精炼CEV计算器，完整类型注解和文档

### 数据管理
- **models.py** - 包含精英单位数据和数据模型定义
- **elite_units.json** - 六大精英单位的完整数据

### 测试验证
- **test_model_verification.py** - v2.4模型验证测试套件

## 使用流程

1. **快速开始**
   ```bash
   # 安装依赖
   pip install -r requirements.txt
   
   # 运行v2.4评估
   python run_v24_evaluation.py
   ```

2. **运行测试**
   ```bash
   # 验证模型
   python -m tests.test_model_verification
   ```

3. **查看结果**
   - 评估结果保存在 `output/` 目录
   - 支持CSV和JSON格式导出
   - 包含交互式评估模式

## 开发指南

### 添加新功能
1. 在相应的 `src/` 子目录中创建模块
2. 更新 `__init__.py` 文件
3. 添加测试用例到 `tests/`
4. 更新文档

### 数据扩展
1. 按照 `docs/technical/DATA_GUIDE.md` 准备CSV数据
2. 使用 `tools/data_maintenance/` 工具导入验证
3. 运行评估确认数据正确性

### 实验配置
1. 在 `experiments/configs/` 创建YAML配置
2. 定义实验参数和评估指标
3. 使用 `run_experiment.py` 执行

## 版本控制说明

### 纳入版本控制
- 所有源代码 (`src/`)
- 实验配置 (`experiments/configs/`)
- 文档 (`docs/`)
- 数据定义文件 (`data/units/*.csv`)

### 不纳入版本控制
- 数据库文件 (`*.db`)
- 实验结果 (`experiments/results/`)
- 日志文件 (`*.log`)
- 临时文件和缓存

---

*本项目采用模块化设计，便于扩展和维护。如有问题请参考相关文档或提交Issue。*