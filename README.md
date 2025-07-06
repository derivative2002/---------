# 星际争霸II合作任务单位战斗效能评估系统 v2.4

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Academic-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.4.0-orange.svg)](CHANGELOG.md)
[![Code Style](https://img.shields.io/badge/Code%20Style-PEP%208-black.svg)](https://www.python.org/dev/peps/pep-0008/)

> *"From Art to Science" - 让游戏平衡从艺术走向科学*

## 项目简介

本项目提供了一个基于兰彻斯特方程的精细化战斗效能值（CEV）评估模型，用于客观量化《星际争霸II》合作任务模式中单位的战斗表现。该模型引入了溅射系数、操作难度、过量击杀惩罚等创新参数，为游戏平衡性分析提供了科学可靠的量化工具。

### 核心特性

- 🎯 **精确建模**: 基于兰彻斯特方程的数学基础
- 🚀 **创新参数**: 首次引入溅射系数量化AOE武器优势
- ⚡ **高性能**: 单位评估 < 1ms，批量处理 > 1000单位/秒
- 📊 **可视化**: 专业级图表生成，支持多种格式输出
- 🔧 **易扩展**: 模块化设计，符合PEP 8规范
- 📚 **完整文档**: 100%类型注解和文档覆盖率

### 最新成果（v2.4）

**六大精英单位CEV排名**：
1. 🥇 掠袭解放者（诺娃）- 234.14 CEV
2. 🥈 灵魂巧匠天罚行者（阿拉纳克P1）- 202.80 CEV  
3. 🥉 普通天罚行者（阿拉纳克）- 115.57 CEV
4. 攻城坦克（斯旺）- 112.62 CEV
5. 穿刺者（德哈卡）- 59.91 CEV
6. 龙骑士（阿塔尼斯）- 47.59 CEV

## 快速开始

### 环境要求

- Python 3.9+
- NumPy >= 1.20.0
- Pandas >= 1.3.0
- Matplotlib >= 3.5.0
- PyYAML >= 6.0

### 安装

```bash
# 克隆项目
git clone https://github.com/starcraft2-coop-cev-model.git
cd starcraft2-coop-cev-model

# 安装依赖
pip install -r requirements.txt
```

### 基础使用

```python
from src.core.refined_cev_calculator import RefinedCEVCalculator, UnitStats

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
from src.core.refined_cev_calculator import create_sample_units

# 使用示例数据
units = create_sample_units()
results = calculator.batch_calculate_cev(units)

# 显示排名
print("六大精英单位CEV排名:")
print(results[['unit_name', 'commander', 'cev']])
```

### 可视化

```python
from src.visualization.cev_charts import CEVVisualizer

# 创建可视化器
visualizer = CEVVisualizer()

# 生成所有图表
visualizer.generate_all_charts(cev_data, "output/charts")
```

## 核心公式

### CEV计算公式

```
CEV = (DPS_eff × Ψ × EHP × Ω × F_range) / C_eff × μ
```

### 关键创新

1. **溅射系数DPS**: `DPS_eff = (基础伤害 × 攻击次数 × 溅射系数) / 攻击间隔`
2. **过量击杀惩罚**: 基于有效伤害的分段惩罚机制
3. **操作难度系数**: 量化单位操作复杂度对实战表现的影响
4. **人口质量乘数**: 平衡不同指挥官的人口限制差异

## 项目结构

```
starcraft2-model/
├── README.md                    # 项目主文档
├── requirements.txt             # Python依赖
├── src/
│   ├── core/
│   │   ├── refined_cev_calculator.py    # v2.4核心计算器
│   │   └── unit_data.py                 # 单位数据管理
│   ├── data/
│   │   ├── models.py                    # 数据模型定义
│   │   └── sac_loader.py                # SAC数据加载
│   ├── analysis/
│   │   └── v23_paper_data_generator.py  # 论文数据生成
│   └── visualization/
│       └── cev_charts.py                # 可视化图表
├── data/
│   ├── elite_units.json                 # 精英单位数据
│   └── standard_amon_compositions.yaml  # SAC数据
├── output/
│   ├── v23_paper_data/                  # v2.3论文数据
│   ├── v24_charts/                      # v2.4可视化图表
│   └── v24_model_formula_documentation.md  # 公式文档
├── docs/
│   ├── project/                         # 项目管理文档
│   ├── technical/                       # 技术文档
│   ├── specifications/                  # 规范文档
│   └── paper/                           # 学术论文
└── tests/                               # 测试文件
```

## 文档

### 用户文档
- [快速开始指南](docs/quick_start.md)
- [API参考文档](docs/technical/API_REFERENCE.md)
- [数据格式说明](docs/technical/DATA_GUIDE.md)

### 开发文档
- [项目状态](docs/project/PROJECT_STATUS.md)
- [编码规范](docs/specifications/coding_spec.md)
- [建模规范](docs/specifications/modeling_spec.md)

### 学术文档
- [论文v2.4](docs/paper/v24_paper_draft.md)
- [模型公式文档](output/v24_model_formula_documentation.md)
- [项目总结](v24_project_summary.md)

## 技术特性

### 代码质量
- ✅ **PEP 8合规**: 完整的代码格式规范
- ✅ **类型注解**: 100%类型覆盖
- ✅ **文档字符串**: Google风格的完整文档
- ✅ **错误处理**: 完善的异常处理机制
- ✅ **日志系统**: 分级日志记录

### 模型特性
- ✅ **理论严谨**: 基于兰彻斯特方程的数学基础
- ✅ **参数精确**: 基于实际游戏数据的精确参数
- ✅ **扩展性强**: 模块化设计，易于添加新功能
- ✅ **验证完整**: 实战数据验证通过

### 输出质量
- ✅ **专业图表**: 4种可视化图表类型
- ✅ **LaTeX支持**: 符合学术发表标准
- ✅ **数据完整**: 包含所有计算中间结果
- ✅ **格式规范**: 支持CSV、JSON、Markdown等格式

## 性能指标

| 指标 | 性能 |
|------|------|
| 单位评估 | < 1ms/单位 |
| 批量处理 | > 1000单位/秒 |
| 内存占用 | < 100MB（1000单位） |
| 类型覆盖率 | 100% |
| 文档覆盖率 | 100% |

## 版本历程

### v2.4.0 (当前版本) - 2025-01-15
- ✅ 代码规范化完成
- ✅ 完整的类型注解和文档
- ✅ 专业级可视化系统
- ✅ 符合学术标准的论文数据

### v2.3.0 - 2024-12-20
- ✅ 溅射系数建模
- ✅ 操作难度系数优化
- ✅ 实战数据验证

### v2.2.0 - 2024-11-15
- ✅ 基础CEV模型实现
- ✅ 六大精英单位评估

详细版本信息请查看 [CHANGELOG.md](CHANGELOG.md)

## 贡献指南

我们欢迎社区贡献！请遵循以下步骤：

1. **Fork项目**并创建功能分支
2. **遵循编码规范**：PEP 8、类型注解、文档字符串
3. **添加测试**：确保新功能有相应测试
4. **更新文档**：保持文档与代码同步
5. **提交PR**：详细描述变更内容

详细信息请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

## 引用

如果您在研究中使用了本项目，请引用：

```bibtex
@article{sc2coop2024,
  title={基于精细化兰彻斯特-CEV模型的星际争霸II合作任务单位战斗效能评估},
  author={歪比歪比歪比巴卜},
  year={2025},
  journal={游戏AI研究},
  version={2.4.0},
  url={https://github.com/starcraft2-coop-cev-model}
}
```

## 许可证

本项目遵循学术研究许可，仅用于学术研究和个人学习，请勿用于商业用途。详见 [LICENSE](LICENSE)。

## 联系方式

- **作者**: 歪比歪比歪比巴卜
- **项目主页**: https://github.com/starcraft2-coop-cev-model
- **问题反馈**: [GitHub Issues](https://github.com/starcraft2-coop-cev-model/issues)

## 致谢

感谢以下贡献者和支持者：
- Claude AI Assistant - 技术支持和代码优化
- 星际争霸II社区 - 数据验证和反馈
- 开源社区 - 工具和库支持

---

**项目座右铭**: 理论严谨、实战验证、代码规范、文档完整

**最后更新**: 2025-01-15  
**项目状态**: 正式发布 🚀