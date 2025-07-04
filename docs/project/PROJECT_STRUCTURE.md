# 项目结构

**最后更新**: 2025-01-04

本文档详细说明了星际争霸II合作任务单位数学模型项目的目录结构和文件组织。

## 目录结构概览

```
starcraft2-model/
├── README.md                    # 项目主文档
├── requirements.txt             # Python依赖
├── run_evaluation.py            # 单位评估主程序
├── run_experiment.py            # 实验框架启动器
├── evaluate_new_unit.py         # 新单位评估工具
│
├── src/                         # 核心源代码
├── data/                        # 数据文件
├── experiments/                 # 实验配置和结果
├── tools/                       # 辅助工具
├── docs/                        # 项目文档
├── examples/                    # 使用示例
└── tests/                       # 测试文件
```

## 详细目录说明

### 📁 src/ - 核心源代码

```
src/
├── core/                        # 核心计算模块
│   ├── enhanced_cev_calculator.py      # 动态CEV计算器
│   ├── refined_cev_calculator.py       # v2.3精细化计算器
│   ├── cem_visualizer.py              # 战斗效能矩阵可视化
│   ├── model_corrections.py           # 模型修正配置
│   └── mastery_configs.py             # 精通系统配置
│
├── data/                        # 数据处理模块
│   ├── models.py                # 数据模型定义（Unit, Weapon等）
│   └── advanced_data_loader.py  # 高级数据加载器
│
├── database/                    # 数据库模块
│   ├── db_manager.py            # 数据库连接管理
│   ├── migrate_to_db.py         # CSV导入工具
│   └── query_interface.py       # 高级查询接口
│
├── experiment/                  # 实验管理模块
│   ├── experiment_manager.py    # 实验生命周期管理
│   ├── experiment_runner.py     # 实验执行器
│   └── config_loader.py         # YAML配置加载器
│
├── analysis/                    # 分析模块
│   ├── comprehensive_evaluator.py      # 综合评估器
│   ├── v23_cev_calculations.py        # v2.3模型计算
│   └── final_six_units_evaluation.py  # 六大单位评估
│
└── visualization/               # 可视化模块
    └── enhanced_unit_comparison.py     # 单位对比图表
```

### 📁 data/ - 数据文件

```
data/
├── starcraft2.db               # SQLite主数据库
├── units/                      # 单位数据CSV
│   ├── units_master.csv        # 单位基础数据
│   ├── weapons.csv             # 武器系统数据
│   └── unit_modes.csv          # 模式切换数据
├── exports/                    # 导出数据
│   └── *_corrected.csv         # 修正后的数据
└── backups/                    # 数据备份
```

### 📁 experiments/ - 实验系统

```
experiments/
├── configs/                    # 实验配置文件
│   ├── examples/               # 示例配置
│   └── production/             # 生产配置
├── results/                    # 实验结果
│   └── unit_eval/              # 单位评估结果
└── logs/                       # 实验日志
```

### 📁 docs/ - 项目文档

```
docs/
├── project/                    # 项目管理文档
│   ├── PROJECT_STATUS.md       # 项目状态与进展
│   ├── PROJECT_STRUCTURE.md    # 本文档
│   ├── CLAUDE.md              # AI助手配置
│   └── CLEANUP_SUMMARY.md      # 清理记录
│
├── technical/                  # 技术文档
│   ├── API_REFERENCE.md        # API使用指南
│   ├── DATABASE_SCHEMA.md      # 数据库设计
│   ├── DATA_GUIDE.md          # 数据收集指南
│   └── EVALUATION_METRICS.md   # 评估指标说明
│
└── paper/                      # 学术论文
    └── versions/               # 论文版本
        └── v2.3/               # 最新版本
```

### 📁 tools/ - 工具脚本

```
tools/
├── data_collection/            # 数据收集工具
│   ├── coop_data_collector.py  # 交互式数据收集
│   └── focus_units_collector.py # 重点单位收集
│
├── data_maintenance/           # 数据维护工具
│   ├── import_coop_data.py     # 数据导入
│   ├── correct_focus_data.py   # 数据修正
│   └── data_verification.py    # 数据验证
│
└── paper_modification_helper.py # 论文修改辅助
```

## 关键文件说明

### 主程序
- **run_evaluation.py** - 单位评估主入口，支持命令行参数
- **run_experiment.py** - 实验框架，支持批量实验和参数扫描
- **evaluate_new_unit.py** - 交互式新单位评估工具

### 核心算法
- **enhanced_cev_calculator.py** - 实现动态CEV公式，考虑时间因子
- **refined_cev_calculator.py** - v2.3精细化模型，含操作难度等参数

### 数据管理
- **starcraft2.db** - 包含所有单位、武器、技能数据的SQLite数据库
- **query_interface.py** - 提供单位查询、平衡性分析等高级功能

## 使用流程

1. **数据准备**
   ```bash
   # 收集数据
   python tools/data_collection/coop_data_collector.py
   
   # 导入数据库
   python -m src.database.migrate_to_db
   ```

2. **运行评估**
   ```bash
   # 单个单位评估
   python run_evaluation.py --commander "阿拉纳克" --unit "天罚行者"
   
   # 批量实验
   python run_experiment.py run experiments/configs/examples/unit_evaluation.yaml
   ```

3. **查看结果**
   - 实验结果保存在 `experiments/results/`
   - 可视化图表自动生成

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