# 星际争霸II合作任务单位数学模型

基于兰彻斯特方程的星际争霸II合作任务单位战斗效能评估系统。

## 🎯 项目概述

本项目实现了一个科学的数学建模框架，用于客观评估《星际争霸II》合作任务中各单位的战斗效能。通过精细化的CEV（Combat Effectiveness Value）模型，为游戏平衡性分析提供数据支持。

**核心特性**：
- 📊 基于兰彻斯特方程的战斗效能评估
- 🎮 考虑操作难度、过量击杀等实战因素
- 🗄️ 完整的SQLite数据库支持
- 📈 可视化分析工具
- 🧪 规范的实验管理系统

## 📖 快速导航

- **[项目状态](docs/project/PROJECT_STATUS.md)** - 当前进展和最新成果
- **[技术文档](docs/technical/)** - API参考、数据库架构等
- **[学术论文](docs/paper/versions/v2.3/)** - v2.3版本研究论文

## 🚀 最新成果（v2.3）

### 六大精英单位CEV排名
1. **灵魂巧匠天罚行者** (阿拉纳克P1) - CEV: 133-167
2. **掠袭解放者** (诺娃) - CEV: 105-138  
3. **普通天罚行者** (阿拉纳克) - CEV: 97-108
4. **穿刺者** (德哈卡) - CEV: 85.5
5. **攻城坦克** (斯旺) - CEV: 83.5
6. **龙骑士** (阿塔尼斯) - CEV: 68.3

**关键发现**：精细化模型将单位间差距从4倍缩小到1.3倍，与实战体验高度一致。

## 快速开始

### 环境要求
- Python 3.8+
- 必需依赖见 `requirements.txt`

### 安装
```bash
git clone https://github.com/yourusername/sc2-math-model.git
cd sc2-math-model
pip install -r requirements.txt
```

### 数据准备
1. 在 `data/units/` 目录下准备CSV数据文件
2. 运行数据迁移脚本导入数据库：
   ```bash
   python -m src.database.migrate_to_db
   ```

### 运行示例
```bash
# 运行单个实验 (推荐)
# 可以在 experiments/configs/examples/ 目录下找到更多示例
python3 run_experiment.py run configs/top_5_units_ranking.yaml

# 运行数据验证脚本
python3 -m src.data.advanced_data_loader

# 查询数据库
python3 -m src.database.query_interface

# 生成六大精英单位评估（使用精细化模型）
python3 -m src.analysis.final_six_units_evaluation

# 评估新单位（交互式）
python3 evaluate_new_unit.py
```

## 项目结构

详见 [PROJECT_STRUCTURE.md](docs/project/PROJECT_STRUCTURE.md)

## 数据收集

如需添加新的单位数据，请参考 [数据收集指南](docs/technical/DATA_GUIDE.md)。

支持的18个官方指挥官：
吉姆·雷诺、凯瑞甘、阿塔尼斯、斯旺、扎加拉、沃拉尊、凯拉克斯、阿巴瑟、阿拉纳克、诺娃、斯托科夫、菲尼克斯、德哈卡、霍纳与汉、泰凯斯、泽拉图、斯台特曼、蒙斯克

## 主要功能

### 1. CEV计算
```python
from src.core.enhanced_cev_calculator import EnhancedCEVCalculator

calculator = EnhancedCEVCalculator()
siege_tank = calculator.database.get_unit("吉姆·雷诺", "SiegeTank")
cev_result = calculator.calculate_cev(siege_tank, time_seconds=600)
```

### 2. 数据查询
```python
from src.database.query_interface import QueryInterface

qi = QueryInterface()
# 查找克制重甲的单位
counter_units = qi.find_counter_units('重甲', min_bonus=10)
```

### 3. 平衡性分析
```python
# 获取平衡性建议
recommendations = qi.get_balance_recommendations()
# 导出综合报告
qi.export_analysis_report()
```


## 核心算法

### 精细化CEV公式（v2.3）
```
CEV_refined = (DPS_eff × Ψ × EHP × Ω × F_range) / C_eff × μ
```

其中：
- `DPS_eff` - 有效DPS（含属性克制）
- `Ψ` - 过量击杀惩罚系数
- `EHP` - 有效生命值
- `Ω` - 操作难度系数
- `F_range` - 射程系数（√(R/r)）
- `C_eff` - 有效成本
- `μ` - 人口质量补偿

## 文档

### 项目文档
- [项目状态](docs/project/PROJECT_STATUS.md) - 当前进展和版本历史
- [项目结构](docs/project/PROJECT_STRUCTURE.md) - 详细的目录说明
- [CLAUDE配置](docs/project/CLAUDE.md) - AI助手使用指南

### 技术文档
- [数据收集指南](docs/technical/DATA_GUIDE.md) - 数据格式和收集规范
- [API参考](docs/technical/API_REFERENCE.md) - 核心API使用说明
- [数据库架构](docs/technical/DATABASE_SCHEMA.md) - 数据库设计文档
- [评估指标](docs/technical/EVALUATION_METRICS.md) - CEV计算详解

### 学术论文
- [v2.3版本](docs/paper/versions/v2.3/report.pdf) - 最新研究成果

## 贡献指南

欢迎提交Issue和Pull Request。贡献代码前请：
1. 遵循现有代码风格
2. 添加适当的测试
3. 更新相关文档
4. 确保数据使用官方命名

## 许可证

MIT License

## 致谢

- 星际争霸II社区的数据贡献者
- 兰彻斯特方程的理论基础
- Claude AI Assistant的技术支持

---

*"From Art to Science" - 让游戏平衡从艺术走向科学*