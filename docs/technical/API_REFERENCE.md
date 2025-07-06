# API参考文档 - v2.4

**版本**: 2.4.0  
**最后更新**: 2025-01-15  
**适用范围**: 星际争霸II合作任务单位战斗效能评估系统

## 概述

本文档提供了CEV评估系统v2.4版本的完整API参考，包括核心类、方法、数据结构和使用示例。

## 核心模块

### `src.core.refined_cev_calculator`

#### RefinedCEVCalculator

精细化CEV计算器，实现基于兰彻斯特方程的战斗效能评估。

##### 初始化

```python
RefinedCEVCalculator(
    gas_weight: float = 2.5,
    supply_base_value: float = 12.5,
    lambda_max: float = 2.0
) -> None
```

**参数**:
- `gas_weight`: 气体资源权重，默认2.5
- `supply_base_value`: 人口基础价值，默认12.5
- `lambda_max`: 最大人口压力因子，默认2.0

**示例**:
```python
calculator = RefinedCEVCalculator(gas_weight=2.5)
```

##### 方法

###### calculate_cev

```python
calculate_cev(
    unit: UnitStats,
    target_composition: Optional[TargetComposition] = None
) -> Dict[str, float]
```

计算单位的CEV值及各组成部分。

**参数**:
- `unit`: 单位属性数据
- `target_composition`: 目标组合，可选

**返回值**:
```python
{
    'cev': float,                    # CEV总值
    'dps_eff': float,               # 有效DPS
    'ehp': float,                   # 有效生命值
    'range_factor': float,          # 射程系数
    'effective_cost': float,        # 有效成本
    'operation_difficulty': float,  # 操作难度系数
    'population_multiplier': float, # 人口质量乘数
    'overkill_penalty': float      # 过量击杀惩罚
}
```

**异常**:
- `ValueError`: 当输入数据无效时

**示例**:
```python
unit = UnitStats(name="陆战队员", commander="雷诺", ...)
result = calculator.calculate_cev(unit)
print(f"CEV值: {result['cev']:.2f}")
```

###### batch_calculate_cev

```python
batch_calculate_cev(
    units: List[UnitStats],
    target_composition: Optional[TargetComposition] = None
) -> pd.DataFrame
```

批量计算多个单位的CEV值。

**参数**:
- `units`: 单位属性数据列表
- `target_composition`: 目标组合，可选

**返回值**: 包含所有单位CEV计算结果的DataFrame，按CEV值降序排列

**示例**:
```python
units = [marine_stats, zealot_stats, zergling_stats]
results = calculator.batch_calculate_cev(units)
print(results[['unit_name', 'commander', 'cev']])
```

###### calculate_effective_dps

```python
calculate_effective_dps(
    unit: UnitStats,
    target_armor: int = 0
) -> float
```

计算有效DPS，考虑溅射系数和护甲减免。

**参数**:
- `unit`: 单位属性数据
- `target_armor`: 目标护甲值，默认0

**返回值**: 有效DPS值

**公式**: `DPS_eff = (实际伤害 × 溅射系数) / 攻击间隔`

**示例**:
```python
dps = calculator.calculate_effective_dps(siege_tank, target_armor=1)
```

###### calculate_effective_hp

```python
calculate_effective_hp(unit: UnitStats) -> float
```

计算有效生命值，考虑护甲和护盾回复。

**参数**:
- `unit`: 单位属性数据

**返回值**: 有效生命值

**公式**: `EHP = HP_eff + Shield_eff × 1.4`

**示例**:
```python
ehp = calculator.calculate_effective_hp(protoss_unit)
```

###### calculate_range_factor

```python
calculate_range_factor(unit: UnitStats) -> float
```

计算射程系数。

**参数**:
- `unit`: 单位属性数据

**返回值**: 射程系数

**公式**: `F_range = sqrt(射程 / 碰撞半径)`

**注意**: 空军单位碰撞半径视为0.5

###### calculate_effective_cost

```python
calculate_effective_cost(unit: UnitStats) -> float
```

计算有效成本，考虑指挥官特殊效率。

**参数**:
- `unit`: 单位属性数据

**返回值**: 有效成本

**公式**: `C_eff = 矿物成本 + 矿气效率 × 瓦斯成本 + 特殊成本`

###### get_model_info

```python
get_model_info() -> Dict[str, Union[str, float]]
```

获取模型配置信息。

**返回值**:
```python
{
    'version': str,           # 模型版本号
    'gas_weight': float,      # 气体权重
    'supply_base_value': float, # 人口基础价值
    'lambda_max': float       # 最大人口压力因子
}
```

## 数据结构

### UnitStats

单位基础属性数据类。

```python
@dataclass
class UnitStats:
    name: str                    # 单位名称
    commander: str               # 指挥官名称
    mineral_cost: int           # 矿物成本
    gas_cost: int               # 瓦斯成本
    supply_cost: int            # 人口占用
    hp: float                   # 生命值
    shield: float = 0.0         # 护盾值
    armor: int = 0              # 护甲值
    damage: float = 0.0         # 基础伤害
    attack_speed: float = 1.0   # 攻击间隔
    range: float = 1.0          # 射程
    unit_type: UnitType = UnitType.GROUND  # 单位类型
    collision_radius: float = 0.5  # 碰撞半径
    splash_factor: float = 1.0  # 溅射系数
```

**验证规则**:
- `supply_cost` > 0
- `hp` > 0

**示例**:
```python
marine = UnitStats(
    name="陆战队员",
    commander="雷诺",
    mineral_cost=50,
    gas_cost=0,
    supply_cost=1,
    hp=45,
    damage=6,
    attack_speed=0.8608,
    range=5
)
```

### UnitType

单位类型枚举。

```python
class UnitType(Enum):
    GROUND = "ground"     # 地面单位
    AIR = "air"          # 空中单位
    DETECTOR = "detector" # 探测器
    MASSIVE = "massive"   # 巨型单位
```

### TargetComposition

目标组合数据类。

```python
@dataclass
class TargetComposition:
    name: str                                    # 组合名称
    units: List[Dict[str, Union[str, int, float]]]  # 单位列表
```

## 配置参数

### 操作难度系数

| 单位类型 | 系数值 | 说明 |
|----------|--------|------|
| 天罚行者 | 1.3 | 可移动射击优势 |
| 掠袭解放者 | 0.75 | 需要精确架设 |
| 攻城坦克 | 0.8 | 简单架设 |
| 穿刺者 | 0.8 | 简单潜地 |
| 其他单位 | 1.0 | 标准操作 |

### 人口质量乘数

| 指挥官类型 | 乘数值 | 说明 |
|------------|--------|------|
| 100人口指挥官 | 2.0 | 诺娃、泽拉图、扎加拉、泰凯斯 |
| 200人口指挥官 | 1.0 | 其他指挥官 |

### 过量击杀惩罚

| 有效伤害范围 | 惩罚系数 | 说明 |
|--------------|----------|------|
| ≥200 | 0.8 | 严重惩罚 |
| ≥150 | 0.85 | 中等惩罚 |
| ≥100 | 0.9 | 轻微惩罚 |
| <100 | 1.0 | 无惩罚 |

## 使用示例

### 基础使用

```python
from src.core.refined_cev_calculator import RefinedCEVCalculator, UnitStats, UnitType

# 创建计算器
calculator = RefinedCEVCalculator()

# 定义单位
marine = UnitStats(
    name="陆战队员",
    commander="雷诺",
    mineral_cost=50,
    gas_cost=0,
    supply_cost=1,
    hp=45,
    damage=6,
    attack_speed=0.8608,
    range=5
)

# 计算CEV
result = calculator.calculate_cev(marine)
print(f"陆战队员CEV: {result['cev']:.2f}")
```

### 批量评估

```python
# 创建单位列表
units = [
    UnitStats(name="陆战队员", commander="雷诺", ...),
    UnitStats(name="狂热者", commander="阿塔尼斯", ...),
    UnitStats(name="跳虫", commander="凯瑞甘", ...)
]

# 批量计算
results = calculator.batch_calculate_cev(units)

# 显示排名
print("单位CEV排名:")
for i, row in results.iterrows():
    print(f"{i+1}. {row['unit_name']} ({row['commander']}): {row['cev']:.2f}")
```

### 高级配置

```python
# 自定义参数
calculator = RefinedCEVCalculator(
    gas_weight=3.0,        # 提高气体权重
    supply_base_value=15.0, # 提高人口价值
    lambda_max=2.5         # 提高人口压力上限
)

# 获取模型信息
info = calculator.get_model_info()
print(f"模型版本: {info['version']}")
```

## 错误处理

### 常见异常

#### ValueError
- **原因**: 输入数据无效
- **示例**: 人口占用≤0、生命值≤0、攻击间隔≤0
- **处理**: 检查输入数据的有效性

```python
try:
    result = calculator.calculate_cev(unit)
except ValueError as e:
    print(f"数据验证失败: {e}")
```

#### AttributeError
- **原因**: 缺少必需属性
- **处理**: 确保UnitStats包含所有必需字段

#### TypeError
- **原因**: 类型不匹配
- **处理**: 检查参数类型是否正确

## 性能指标

### 计算性能
- **单位评估**: < 1ms/单位
- **批量处理**: > 1000单位/秒
- **内存占用**: < 100MB（1000单位）

### 使用建议
- 对于大量单位，使用`batch_calculate_cev`而非循环调用
- 复用计算器实例以避免重复初始化
- 使用适当的日志级别控制输出

## 日志配置

```python
import logging

# 配置日志级别
logging.basicConfig(
    level=logging.INFO,  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 使用计算器
calculator = RefinedCEVCalculator()
```

## 版本兼容性

### v2.4.0
- ✅ 完整的类型注解支持
- ✅ 改进的错误处理
- ✅ 新增溅射系数支持
- ✅ 优化的操作难度配置

### 迁移指南

从v2.3迁移到v2.4:

1. **导入路径**: 无变化
2. **接口变化**: 无破坏性变化
3. **新增功能**: 溅射系数、改进的文档
4. **建议**: 更新类型注解以获得更好的IDE支持

## 扩展开发

### 添加新的操作难度配置

```python
# 继承并扩展
class CustomCEVCalculator(RefinedCEVCalculator):
    def __init__(self):
        super().__init__()
        self._operation_difficulty.update({
            "新单位类型": 1.2
        })
```

### 自定义过量击杀惩罚

```python
class CustomCEVCalculator(RefinedCEVCalculator):
    def calculate_overkill_penalty(self, effective_damage: float) -> float:
        # 自定义逻辑
        if effective_damage >= 300:
            return 0.7
        return super().calculate_overkill_penalty(effective_damage)
```

---

**文档版本**: v2.4.0  
**维护者**: 歪比歪比歪比巴卜  
**最后更新**: 2025-01-15