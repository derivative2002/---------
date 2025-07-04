# 星际争霸II单位评估实验管理系统

本系统提供类似[Hydra](https://hydra.cc/)的实验管理功能，专门为数学建模和单位评估实验设计。

## 快速开始

### 1. 运行示例实验

```bash
# 运行单位评估实验
python run_experiment.py run configs/examples/unit_evaluation.yaml

# 运行指挥官对比实验
python run_experiment.py run configs/examples/commander_comparison.yaml

# 运行参数扫描实验
python run_experiment.py run configs/examples/parameter_sweep.yaml
```

### 2. 批量运行实验

```bash
# 运行完整分析套件
python run_experiment.py batch configs/batch/full_analysis.yaml
```

### 3. 查看实验结果

```bash
# 列出最近的实验
python run_experiment.py list

# 查看特定类型的实验
python run_experiment.py list -t unit_eval

# 查看实验报告
python run_experiment.py report
```

## 实验类型

系统支持以下7种实验类型：

1. **unit_eval** - 单位评估
   - 评估单位在不同游戏阶段的表现
   - 生成排名和效率分析

2. **cmd_comp** - 指挥官对比
   - 比较多个指挥官的整体实力
   - 生成雷达图和平衡性分析

3. **balance** - 平衡性分析
   - 检测游戏平衡性问题
   - 提供调整建议

4. **cem_viz** - CEM可视化
   - 生成单位克制关系矩阵
   - 创建对战优劣势分析

5. **param_sweep** - 参数扫描
   - 测试模型参数敏感性
   - 寻找最优参数组合

6. **synergy** - 协同效应分析
   - 分析单位组合的协同加成
   - 量化团队配合效果

7. **meta** - 元分析
   - 分析和比较多个实验结果
   - 发现趋势和模式

## 配置文件格式

### 基础配置示例

```yaml
# 实验基本信息
name: "我的单位评估实验"
type: "unit_eval"
description: "评估特定单位的战斗效能"

# 评估目标
commanders:
  - "吉姆·雷诺"
  - "凯瑞甘"
units:
  - "陆战队员"
  - "跳虫"

# 游戏阶段
game_phases:
  - "early_game"
  - "mid_game"
  - "late_game"

# 输出设置
save_plots: true
save_raw_data: true
generate_report: true

# 额外参数（可选）
extra_params:
  detailed_analysis: true
```

### 批量配置示例

```yaml
batch_name: "完整分析套件"
description: "运行多个相关实验"

experiments:
  - name: "基础评估"
    type: "unit_eval"
    commanders: ["all"]
    
  - name: "平衡性检查"
    type: "balance"
    
  - name: "可视化分析"
    type: "cem_viz"
    units: ["陆战队员", "跳虫", "狂热者"]
```

## 输出目录结构

每个实验都会创建独立的时间戳目录：

```
experiments/results/
└── {实验类型}/
    └── {日期}/
        └── {时间}_{名称}_{ID}/
            ├── .experiment/      # 元数据
            │   ├── config.yaml   # 实验配置
            │   ├── metadata.json # 实验信息
            │   └── results_summary.json
            ├── data/            # 数据文件
            │   ├── raw/         # 原始数据
            │   └── processed/   # 处理后数据
            ├── plots/           # 图表
            ├── models/          # 模型文件
            └── report/          # 实验报告
                └── experiment_report.md
```

## 高级功能

### 创建自定义配置

```bash
# 从模板创建新配置
python run_experiment.py create -t basic_unit_eval -o my_config.yaml

# 列出可用模板
python run_experiment.py create --list-templates
```

### 参数覆盖

```bash
# 运行时覆盖参数
python run_experiment.py run config.yaml \
  --name "新实验名称" \
  --commanders "吉姆·雷诺,凯瑞甘" \
  --no-plots
```

### 实验对比

```python
from src.experiment.experiment_manager import ExperimentManager

manager = ExperimentManager()

# 获取最近的实验
experiments = manager.list_experiments(limit=5)

# 比较实验结果
comparison_df = manager.compare_experiments([exp['path'] for exp in experiments])
```

## 常见问题

### Q: 如何查看所有可用的配置文件？

```bash
python run_experiment.py configs
```

### Q: 如何重新生成实验报告？

```bash
python run_experiment.py report --regenerate
```

### Q: 如何归档旧实验？

```python
from src.experiment.experiment_manager import ExperimentManager

manager = ExperimentManager()
manager.archive_experiment("experiments/results/unit_eval/2025-06-30/...")
```

## 与Hydra的对比

| 功能 | 本系统 | Hydra |
|------|--------|--------|
| 自动创建时间戳目录 | ✓ | ✓ |
| YAML/JSON配置 | ✓ | ✓ |
| 参数覆盖 | ✓ | ✓ |
| 批量实验 | ✓ | ✓ (multirun) |
| 实验类型模板 | ✓ | ✗ |
| 内置可视化 | ✓ | ✗ |
| 实验报告生成 | ✓ | ✗ |
| 针对领域优化 | ✓ (数学建模) | ✗ (通用) |

## 扩展开发

### 添加新的实验类型

1. 在 `ExperimentType` 枚举中添加新类型
2. 在 `ExperimentRunner` 中实现处理函数
3. 创建对应的配置模板

```python
# src/experiment/experiment_runner.py
def _run_my_experiment(self, config: ExperimentConfig, exp_dir: Path) -> Dict[str, Any]:
    # 实现你的实验逻辑
    results = {}
    # ...
    return results
```

### 自定义输出格式

通过继承 `ExperimentManager` 类可以自定义输出格式和目录结构。

## 相关链接

- [项目主页](../)
- [论文文档](../docs/paper/)
- [API文档](../src/)

## 许可证

本项目采用与主项目相同的许可证。