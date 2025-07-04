# 星际争霸II数学建模项目 - 代码开发规范

## 1. Python编码规范

### 1.1 基础规范

遵循PEP 8标准，具体要求：

- **缩进**：使用4个空格，禁用Tab
- **行长度**：最大120字符（比PEP 8的79字符宽松）
- **空行**：顶层函数间2行，类方法间1行
- **编码**：UTF-8

### 1.2 命名规范

```python
# 模块名：小写+下划线
unit_evaluator.py

# 类名：PascalCase
class UnitEvaluator:
    pass

# 函数名：小写+下划线
def calculate_effective_dps():
    pass

# 变量名：小写+下划线
effective_cost = 100

# 常量：大写+下划线
GAS_WEIGHT = 2.5
MAX_SUPPLY = 200

# 私有成员：前缀单下划线
_internal_cache = {}

# 特殊方法：前后双下划线
def __init__(self):
    pass
```

### 1.3 类型注解

Python 3.7+的类型注解是必需的：

```python
from typing import Dict, List, Optional, Tuple, Union

def evaluate_unit(
    unit_data: Dict[str, Union[int, float, str]], 
    lambda_weight: float = 0.5
) -> Dict[str, float]:
    """评估单位性能"""
    pass

class CombatModel:
    def __init__(self, gas_weight: float = 2.5) -> None:
        self.gas_weight: float = gas_weight
        self._cache: Dict[str, float] = {}
```

## 2. 文档规范

### 2.1 模块文档

每个Python文件开头必须包含：

```python
"""
模块名称：unit_evaluator.py
功能描述：提供星际争霸II单位战斗力评估的核心功能
作者：[姓名]
创建日期：2024-01-01
最后修改：2024-01-15

依赖：
    - numpy >= 1.20.0
    - pandas >= 1.3.0

使用示例：
    evaluator = UnitEvaluator()
    score = evaluator.evaluate(unit_data)
"""
```

### 2.2 函数文档

使用Google风格的docstring：

```python
def calculate_effective_cost(
    mineral: int, 
    gas: int, 
    supply: int,
    lambda_weight: float = 0.5
) -> float:
    """
    计算单位的有效成本，考虑资源和人口的动态权重。
    
    Args:
        mineral: 晶体矿成本
        gas: 高能瓦斯成本
        supply: 人口占用
        lambda_weight: 人口权重因子，0为纯资源权重，1为纯人口权重
        
    Returns:
        float: 有效成本值
        
    Raises:
        ValueError: 当输入参数为负数时
        
    Example:
        >>> calculate_effective_cost(100, 50, 2, 0.3)
        245.5
    """
    if mineral < 0 or gas < 0 or supply < 0:
        raise ValueError("成本参数不能为负数")
        
    # 实现细节...
```

### 2.3 类文档

```python
class UnitEvaluator:
    """
    单位评估器，用于计算星际争霸II单位的战斗力评分。
    
    该类实现了论文中提出的七维度评估模型，支持动态权重调整
    和多场景分析。
    
    Attributes:
        gas_weight (float): 气体资源权重，默认2.5
        supply_value (float): 单位人口价值，默认12.5
        _model_version (str): 模型版本号
        
    Example:
        >>> evaluator = UnitEvaluator(gas_weight=2.5)
        >>> marine_data = {"mineral": 50, "gas": 0, "supply": 1, "dps": 10}
        >>> score = evaluator.evaluate(marine_data)
    """
```

## 3. 代码组织规范

### 3.1 导入顺序

```python
# 1. 标准库
import os
import sys
from datetime import datetime

# 2. 第三方库
import numpy as np
import pandas as pd
from scipy import stats

# 3. 本地模块
from .base_model import BaseModel
from ..utils import helpers
```

### 3.2 模块结构

```python
"""模块文档字符串"""

# 导入
import ...

# 常量定义
CONSTANT_VALUE = 100

# 辅助函数
def _helper_function():
    pass

# 主要类
class MainClass:
    pass

# 公共函数
def public_function():
    pass

# 主程序入口
if __name__ == "__main__":
    main()
```

## 4. 错误处理规范

### 4.1 异常处理

```python
def parse_unit_data(file_path: str) -> pd.DataFrame:
    """解析单位数据文件"""
    try:
        data = pd.read_excel(file_path)
    except FileNotFoundError:
        logger.error(f"文件未找到: {file_path}")
        raise
    except pd.errors.EmptyDataError:
        logger.error("数据文件为空")
        raise ValueError("数据文件不能为空")
    except Exception as e:
        logger.error(f"解析数据时发生未知错误: {e}")
        raise
        
    return data
```

### 4.2 输入验证

```python
def validate_unit_stats(stats: Dict[str, float]) -> None:
    """验证单位属性的合法性"""
    required_keys = ['mineral', 'gas', 'supply', 'dps']
    
    # 检查必需字段
    missing_keys = set(required_keys) - set(stats.keys())
    if missing_keys:
        raise KeyError(f"缺少必需字段: {missing_keys}")
    
    # 检查数值范围
    if stats['supply'] <= 0:
        raise ValueError("人口占用必须大于0")
        
    if stats['dps'] < 0:
        raise ValueError("DPS不能为负数")
```

## 5. 测试规范

### 5.1 单元测试

```python
# test_unit_evaluator.py
import unittest
from unittest.mock import Mock, patch

class TestUnitEvaluator(unittest.TestCase):
    """UnitEvaluator的单元测试"""
    
    def setUp(self):
        """每个测试前的初始化"""
        self.evaluator = UnitEvaluator()
        self.test_data = {
            'mineral': 100,
            'gas': 50,
            'supply': 2,
            'dps': 15
        }
    
    def test_calculate_effective_cost(self):
        """测试有效成本计算"""
        cost = self.evaluator.calculate_effective_cost(
            100, 50, 2, lambda_weight=0.5
        )
        self.assertAlmostEqual(cost, 237.5, places=1)
    
    def test_invalid_input(self):
        """测试无效输入处理"""
        with self.assertRaises(ValueError):
            self.evaluator.calculate_effective_cost(-100, 50, 2)
```

### 5.2 测试覆盖率要求

- 核心模块：>90%
- 工具函数：>80%
- 整体项目：>85%

## 6. 版本控制规范

### 6.1 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

类型（type）：
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 重构
- test: 测试相关
- chore: 构建过程或辅助工具的变动

示例：
```
feat(evaluator): 添加动态权重计算功能

- 实现了基于游戏阶段的λ权重自适应
- 添加了S型曲线平滑过渡
- 更新了相关单元测试

Closes #12
```

### 6.2 分支策略

- `main`: 稳定版本
- `develop`: 开发分支
- `feature/*`: 功能分支
- `bugfix/*`: 修复分支
- `release/*`: 发布分支

## 7. 性能规范

### 7.1 性能要求

- 单位评估：< 1ms/单位
- 批量处理：> 1000单位/秒
- 内存占用：< 100MB（1000单位）

### 7.2 优化原则

```python
# 使用numpy向量化操作
# 差
results = []
for unit in units:
    results.append(calculate_score(unit))

# 好
results = np.vectorize(calculate_score)(units)

# 缓存重复计算
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(param: float) -> float:
    # 复杂计算...
    return result
```

## 8. 日志规范

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 使用示例
logger.debug("详细调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")
```

## 9. 配置管理

### 9.1 配置文件格式

使用YAML或JSON：

```yaml
# config.yaml
model:
  version: "1.0.0"
  parameters:
    gas_weight: 2.5
    supply_value: 12.5
    lambda_max: 2.0
    
evaluation:
  scenarios:
    - early_game
    - mid_game
    - late_game
```

### 9.2 环境变量

```python
import os
from pathlib import Path

# 使用环境变量配置
DATA_DIR = Path(os.getenv('SC2_DATA_DIR', './data'))
MODEL_VERSION = os.getenv('SC2_MODEL_VERSION', '1.0.0')
```

## 10. 发布检查清单

发布前必须完成：

- [ ] 所有测试通过
- [ ] 代码格式检查（flake8, black）
- [ ] 类型检查（mypy）
- [ ] 文档生成（sphinx）
- [ ] 版本号更新
- [ ] CHANGELOG更新
- [ ] 性能基准测试
- [ ] 示例代码验证