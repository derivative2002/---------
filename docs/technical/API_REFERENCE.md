# API参考手册

本文档提供星际争霸II数学模型项目的API使用示例和参考。

## 目录

1. [核心计算API](#核心计算api)
2. [数据处理API](#数据处理api)
3. [数据库查询API](#数据库查询api)
4. [实验管理API](#实验管理api)
5. [可视化API](#可视化api)

## 核心计算API

### RefinedCEVCalculator（新增）

精细化的CEV计算器，包含操作难度、过量击杀、生产能力等实战因素。

```python
from src.core.refined_cev_calculator import RefinedCEVCalculator, COMBAT_SCENARIOS

# 初始化计算器
calculator = RefinedCEVCalculator()

# 使用预定义场景
scenario = COMBAT_SCENARIOS['vs_mixed']

# 计算CEV
result = calculator.calculate_cev(
    unit_data={
        'english_id': 'Wrathwalker',
        'mineral_cost': 300,
        'gas_cost': 200,
        'supply_cost': 6,
        'hp': 200,
        'shields': 150,
        'armor': 1,
        'collision_radius': 0.75,
        'can_move_attack': True
    },
    weapon_data={
        'base_damage': 100,
        'attack_interval': 1.304,
        'range': 12,
        'bonus_damage': '{"建筑": 75}'
    },
    commander='阿拉纳克',
    scenario=scenario
)

# 结果包含
print(f"CEV: {result['cev']:.1f}")
print(f"有效成本: {result['effective_cost']:.1f}")
print(f"有效DPS: {result['effective_dps']:.1f}")
print(f"各项系数: {result['factors']}")
```

#### 关键参数说明

- **指挥官特性**：不同指挥官的矿气转换率和生产能力
- **操作难度系数**：0.7（复杂架设）到1.1（移动射击）
- **过量击杀惩罚**：根据单体伤害与目标平均血量的比例
- **AOE系数**：考虑实际溅射效果和碰撞体积
- **协同需求**：单位独立作战能力的评估

### EnhancedCEVCalculator

增强的战斗效能值(CEV)计算器，支持动态时间因子、属性克制、溅射伤害等高级特性。

```python
from src.core.enhanced_cev_calculator import EnhancedCEVCalculator
from src.data.models import Unit, Weapon

# 初始化计算器
calculator = EnhancedCEVCalculator()

# 创建单位对象
unit = Unit(
    english_id="Marine",
    chinese_name="陆战队员",
    commander="吉姆·雷诺",
    mineral_cost=45,
    gas_cost=0,
    supply_cost=1,
    hp=55,
    shields=0,
    armor=0,
    movement_speed=3.15,
    is_flying=False,
    attributes=["生物", "轻甲"]
)

# 计算CEV
result = calculator.calculate_cev(
    unit=unit,
    time_seconds=600,  # 10分钟
    target_attributes=["重甲"],  # 目标属性
    n_support=2,  # 支援单位数量
    n_ally=15,    # 盟友单位数量
    army_composition=["陆战队员", "医疗兵", "掠夺者"]
)

print(f"CEV: {result['cev']:.2f}")
print(f"有效成本: {result['effective_cost']:.2f}")
print(f"总DPS: {result['total_dps']:.2f}")
```

### 批量比较单位

```python
# 比较多个单位
units = [unit1, unit2, unit3]
comparison = calculator.compare_units(units, time_seconds=600)

for idx, result in enumerate(comparison):
    print(f"{idx+1}. {result['chinese_name']}: CEV={result['cev']:.2f}")
```

## 数据处理API

### AdvancedDataLoader

支持新数据格式v2.0的高级数据加载器。

```python
from src.data.advanced_data_loader import AdvancedDataLoader

# 初始化加载器
loader = AdvancedDataLoader()

# 加载所有单位数据
units_dict = loader.load_units_data()

# 获取特定单位
marine = units_dict.get("Marine")
if marine:
    print(f"{marine.chinese_name}: HP={marine.hp}, DPS={marine.get_total_dps()}")

# 获取指挥官的所有单位
raynor_units = loader.get_commander_units("吉姆·雷诺")
```

### 数据验证

```python
# 验证数据完整性
validation_report = loader.validate_data()
if validation_report['errors']:
    for error in validation_report['errors']:
        print(f"错误: {error}")
```

## 数据库查询API

### QueryInterface

提供高级查询功能，包括克制分析、效率排名、协同效应等。

```python
from src.database.query_interface import QueryInterface

# 初始化查询接口
qi = QueryInterface()

# 1. 查找克制特定属性的单位
counter_units = qi.find_counter_units(
    target_attribute="重甲",
    min_bonus=10
)
print(counter_units[['chinese_name', 'bonus_damage', 'bonus_dps']])

# 2. 分析成本效率
efficiency_df = qi.analyze_cost_efficiency(phase='mid')
print(efficiency_df[['chinese_name', 'cev', 'dps_per_cost']].head(10))

# 3. 查找协同单位
synergies = qi.find_synergistic_units("陆战队员")
print(synergies[['chinese_name', 'synergy_type']])

# 4. 获取平衡建议
recommendations = qi.get_balance_recommendations()
for rec in recommendations:
    print(f"{rec['type']}: {rec['unit']} - {rec['suggestion']}")

# 5. 导出综合报告
qi.export_analysis_report("analysis_report.xlsx")
```

### 自定义查询

```python
from src.database.db_manager import DatabaseManager

db = DatabaseManager()

# 执行自定义SQL查询
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.chinese_name, COUNT(w.id) as weapon_count
        FROM units u
        LEFT JOIN weapons w ON u.id = w.unit_id
        GROUP BY u.id
        HAVING weapon_count > 1
    """)
    
    multi_weapon_units = cursor.fetchall()
```

## 实验管理API

### ExperimentManager

Hydra风格的实验管理系统，支持配置管理、结果追踪和报告生成。

```python
from src.experiment.experiment_manager import ExperimentManager, ExperimentConfig, ExperimentType

# 创建实验管理器
exp_manager = ExperimentManager()

# 定义实验配置
config = ExperimentConfig(
    name="人族单位评估",
    type=ExperimentType.UNIT_EVALUATION,
    description="评估吉姆·雷诺的所有单位",
    commanders=["吉姆·雷诺"],
    units=[],  # 空列表表示所有单位
    game_phases=["early_game", "mid_game", "late_game"],
    save_plots=True,
    generate_report=True,
    extra_params={
        "include_abilities": True,
        "synergy_analysis": True
    }
)

# 创建实验目录
exp_dir = exp_manager.create_experiment_dir(config)

# 运行实验（使用ExperimentRunner）
from src.experiment.experiment_runner import ExperimentRunner

runner = ExperimentRunner(exp_manager)
results = runner.run_experiment(config, exp_dir)

# 查看实验列表
experiments = exp_manager.list_experiments(
    exp_type=ExperimentType.UNIT_EVALUATION,
    status='completed'
)
```

### 批量实验

```python
from src.experiment.experiment_runner import run_batch_experiments, ExperimentTemplates

# 使用模板创建多个实验
configs = [
    ExperimentTemplates.unit_tier_list(["吉姆·雷诺", "凯瑞甘"]),
    ExperimentTemplates.commander_balance_check(["吉姆·雷诺", "阿拉纳克", "诺娃"]),
    ExperimentTemplates.unit_matchup_matrix(["陆战队员", "跳虫", "狂热者"])
]

# 批量运行
results_df = run_batch_experiments(configs)
print(results_df[['name', 'success', 'duration']])
```

## 可视化API

### CEMVisualizer

战斗效能矩阵(CEM)可视化工具。

```python
from src.core.cem_visualizer import CEMVisualizer

visualizer = CEMVisualizer()

# 1. 创建CEM热图
fig = visualizer.create_cem_heatmap(
    unit_names=["陆战队员", "掠夺者", "攻城坦克", "跳虫", "刺蛇"],
    title="战斗效能矩阵",
    save_path="cem_heatmap.png"
)

# 2. 单位对战分析
fig_matchup = visualizer.create_unit_matchup_chart(
    unit_name="陆战队员",
    top_n=10
)

# 3. 导出CEM数据
visualizer.export_cem_data(
    unit_names=["陆战队员", "跳虫", "狂热者"],
    output_path="cem_matrix.csv"
)
```

### 综合评估仪表板

```python
from src.analysis.comprehensive_evaluator import ComprehensiveEvaluator

evaluator = ComprehensiveEvaluator()

# 创建单位评估仪表板
evaluator.create_evaluation_dashboard(
    unit_name="攻城坦克",
    commander="吉姆·雷诺",
    save_path="siege_tank_dashboard.png"
)

# 指挥官对比
comparison_df = evaluator.compare_commanders(
    commanders=["吉姆·雷诺", "凯瑞甘", "阿塔尼斯"]
)
```

## 完整示例：端到端工作流

```python
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.data.advanced_data_loader import AdvancedDataLoader
from src.core.enhanced_cev_calculator import EnhancedCEVCalculator
from src.database.migrate_to_db import migrate_csv_to_database
from src.database.query_interface import QueryInterface
from src.experiment.experiment_runner import ExperimentRunner, ExperimentTemplates

# 1. 加载数据到数据库
print("1. 导入数据...")
migrate_csv_to_database()

# 2. 查询分析
print("\n2. 查询分析...")
qi = QueryInterface()
top_units = qi.analyze_cost_efficiency('mid').head(5)
print(top_units[['chinese_name', 'commander', 'cev']])

# 3. 运行实验
print("\n3. 运行实验...")
config = ExperimentTemplates.unit_tier_list(["吉姆·雷诺"])
runner = ExperimentRunner()
results = runner.run_experiment(config)

# 4. 生成报告
print("\n4. 生成报告...")
qi.export_analysis_report("final_report.xlsx")

print("\n完成！")
```

## 错误处理

所有API都包含错误处理机制：

```python
try:
    result = calculator.calculate_cev(unit)
except ValueError as e:
    print(f"参数错误: {e}")
except Exception as e:
    print(f"计算失败: {e}")
```

## 性能优化建议

1. **批量操作**：使用批量方法而不是循环单个操作
2. **数据库连接**：使用上下文管理器确保连接正确关闭
3. **内存管理**：处理大量数据时使用生成器
4. **并行计算**：CEV计算支持多线程处理

## 更多信息

- 数据格式规范：见 `DATA_GUIDE.md`
- 数据库设计：见 `DATABASE_SCHEMA.md`
- 项目结构：见 `PROJECT_STATUS.md`