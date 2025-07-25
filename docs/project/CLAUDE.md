## 标准工作流程

1. **问题分析和规划**：首先分析问题，阅读相关代码，制定详细计划到 projectplan.md
2. **计划确认**：与用户确认计划后开始执行
3. **任务执行**：逐项完成待办事项，及时标记完成状态
4. **进度汇报**：每步都提供简洁的高层次说明
5. **简化原则**：每个任务和代码变更都尽可能简单，影响最小的代码范围
6. **最终总结**：在计划文件中添加变更总结和相关信息

## 项目概述

**项目名称**：星际争霸II合作任务单位数学模型  
**核心目标**：基于兰彻斯特方程构建动态CEV评估系统，为游戏平衡性分析提供数学支持

### 核心公式
- **动态CEV**: `CEV(t) = (DPS × HP × 协同系数) / 有效成本(t)`
- **有效成本**: `C_eff(t) = 矿物 + 瓦斯×2.5 + 人口×25×λ(t)`
- **时间因子**: `λ(t) = 1 / (1 + exp(-α(t-β)))`

## 当前系统架构

### 数据层
- **数据格式**: CSV文件 + SQLite数据库
- **核心表**: units_master.csv, weapons.csv, unit_modes.csv
- **数据模型**: src/data/models.py (支持多武器、模式切换、特殊能力)

### 计算层
- **CEV计算器**: src/core/enhanced_cev_calculator.py (最新版本)
- **特性支持**: 属性克制、溅射伤害、协同效应、时间动态
- **CEM可视化**: src/core/cem_visualizer.py

### 应用层
- **数据库查询**: src/database/query_interface.py
- **实验管理**: src/experiment/experiment_manager.py
- **平衡性分析**: 自动检测异常单位并给出建议

## 数据收集规范

### 官方指挥官名称（18个）
1. 吉姆·雷诺 (Jim Raynor)
2. 凯瑞甘 (Kerrigan)
3. 阿塔尼斯 (Artanis)
4. 斯旺 (Swann)
5. 扎加拉 (Zagara)
6. 沃拉尊 (Vorazun)
7. 凯拉克斯 (Karax)
8. 阿巴瑟 (Abathur)
9. 阿拉纳克 (Alarak)
10. 诺娃 (Nova)
11. 斯托科夫 (Stukov)
12. 菲尼克斯 (Fenix)
13. 德哈卡 (Dehaka)
14. 霍纳与汉 (Horner & Han)
15. 泰凯斯 (Tychus)
16. 泽拉图 (Zeratul)
17. 斯台特曼 (Stetmann)
18. 蒙斯克 (Mengsk)

### 数据格式要点
- **英文ID**: 使用游戏内部ID（如Marine, Zergling）
- **中文名**: 使用官方译名（如陆战队员，跳虫）
- **属性标签**: 轻甲、重甲、生物、机械、灵能、巨型、英雄
- **JSON字段**: 在CSV中使用双引号转义

### 关键文件
- `DATA_COLLECTION_GUIDE.md` - 详细的数据收集指南
- `data/units/` - CSV数据文件目录
- `data/starcraft2.db` - SQLite数据库

## 开发命令

```bash
# 验证数据格式
python3 -m src.data.advanced_data_loader

# 导入数据库
python3 -m src.database.migrate_to_db

# 运行查询分析
python3 -m src.database.query_interface

# 运行实验
python run_experiment.py run experiments/configs/examples/unit_evaluation.yaml
```

## 模型评估状态

### 已验证特性
- ✅ **核心公式实现**: 动态CEV、有效成本、人口压力因子与论文完全一致
- ✅ **属性克制系统**: 正确实现并应用于DPS计算
- ✅ **动态成本模型**: 有效反映游戏中后期单位的实际价值变化
- ✅ **数据验证机制**: 完整的数据加载和错误检查流程

### 待实现特性
- ❌ **高级效果**: 治疗(H)、控制(Θ)、增援(R)等机制
- ❌ **完整CEM矩阵**: 单位间克制关系的完整实现
- ❌ **全数据覆盖**: 当前仅部分指挥官数据完整

## 待完成任务

1. **数据收集**: 完成所有18个指挥官的单位数据
2. **高级特性实现**: 添加治疗、控制、增援等效果的计算模块
3. **CEM矩阵**: 实现完整的单位克制关系矩阵
4. **生产约束**: 添加建筑需求和科技树
5. **Web界面**: 开发交互式分析界面
6. **实战验证**: 收集游戏胜率数据进行模型验证

## 项目特色

1. **理论创新**: 首次将兰彻斯特方程应用于RTS游戏单位评估
2. **动态评估**: 引入时间因子λ(t)，实现单位价值的动态分析
3. **工程规范**: 完整的数据收集、处理、分析、可视化流程
4. **学术严谨**: 基于数学模型的客观评估，避免主观偏见
5. **易于扩展**: 模块化设计，支持新功能和新数据的快速集成
6. **实用价值**: 可用于游戏平衡性分析、版本迭代和策略制定

## 最新评估结果

### 五大精英单位基准（2025年7月更新）

#### 原始实验结果（未考虑精通）
1. 天罚行者（阿拉纳克）- CEV: 46.49
2. 掠袭解放者（诺娃）- CEV: 42.15
3. 攻城坦克（斯旺）- CEV: 24.94
4. 穿刺者（德哈卡）- CEV: 19.98
5. 龙骑士（阿塔尼斯）- CEV: 8.08

#### 准确评估结果（考虑精通和科技）
基于实际游戏配置的CEV计算：

1. **天罚行者**（阿拉纳克）- CEV: 88.8（对建筑113.5）
   - 场景：献祭+精通（满级可达113.5）
   - 关键：献祭替换武器（1.5秒攻速）+ 15%精通（1.304秒）
   - 配合：浩劫+1射程（实战12射程）

2. **掠袭解放者**（诺娃）- CEV: 52.6
   - 场景：满级精通（+3攻+15%攻速）
   - 关键：AG模式超高单体DPS

3. **穿刺者**（德哈卡）- CEV: 37.3
   - 场景：对重甲
   - 关键：+30%生命值精通，潜地能力

4. **攻城坦克**（斯旺）- CEV: 34.9
   - 场景：钨钢钉vs重甲
   - 关键：+30%机械生命值，钨钢钉科技

5. **龙骑士**（阿塔尼斯）- CEV: 16.5
   - 场景：对重甲
   - 关键：克制翻倍，护盾回充

**重要发现**：
- 精通和科技对CEV影响巨大（提升25%-104%）
- 天罚行者在特定条件下是最强单位
- 模型公式正确，但需要准确的游戏数据

详见 `calculate_accurate_cev.py` 和 `data_verification_report.md`

### 六大精英单位基准（2025-07-03更新）

#### 包含灵魂巧匠天罚行者的完整评估

1. **灵魂巧匠天罚行者**（阿拉纳克P1）- CEV: 102.9
   - 成本：1050矿 + 200气（含10个死徒）
   - 配置：满层灵魂+献祭+精通
   - DPS：306.67（对建筑536.67）
   - 特点：DPS是普通版4倍，但成本增加86%

2. **天罚行者**（阿拉纳克）- CEV: 50.2
   - 成本：300矿 + 200气
   - 配置：献祭+精通
   - DPS：76.69（对建筑134.20）
   - 特点：性价比极高的精英单位

3. **掠袭解放者**（诺娃）- CEV: 49.2
   - 成本：375矿 + 375气
   - 配置：+15%攻速精通
   - 特点：强大对地，对空能力有限

4. **攻城坦克**（斯旺）- CEV: 41.4
   - 成本：150矿 + 125气
   - 配置：+30%生命值精通
   - 特点：攻城模式溅射伤害

5. **穿刺者**（德哈卡）- CEV: 28.0
   - 成本：200矿 + 100气
   - 特点：潜地和基因突变系统

6. **龙骑士**（阿塔尼斯）- CEV: 14.4
   - 成本：125矿 + 50气
   - 特点：守护护盾，但DPS较低

**关键发现**：
- 灵魂巧匠机制：10层灵魂提供+100%攻速和+100%伤害
- 死徒成本必须计入：每个75矿，满层需要750额外矿物
- 灵魂巧匠CEV约为普通天罚行者的2倍（而非DPS的4倍）

详见 `src/analysis/final_six_units_evaluation.py` 和 `src/core/refined_cev_calculator.py`

### 精细化模型评估（2025-01-03更新）

#### 模型改进

1. **射程系数调整**
   - 从 log₂(1+R/r) 改为 √(R/r)
   - 避免远程单位获得过高加成

2. **操作难度系数**
   - 掠袭解放者：0.7（需要精确架设）
   - 攻城坦克/穿刺者：0.9（简单架设）
   - 天罚行者：1.1（可移动射击）

3. **过量击杀惩罚**
   - 200+伤害：0.8
   - 150伤害：0.85
   - 100伤害：0.9
   - 50以下：1.0

4. **指挥官特性**
   - 诺娃：矿气转换1:1（考虑面板技能）
   - 斯旺：生产能力×1.8（气矿骡）
   - 德哈卡：生产能力×1.3（快速孵化）

5. **AOE实际效果**
   - 攻城坦克：1.4（考虑碰撞体积，非理想3.0）

#### 精细化后的CEV排名

**综合场景**：
1. 灵魂巧匠天罚行者：133-167
2. 掠袭解放者：105-138  
3. 普通天罚行者：97-108
4. 穿刺者：85.5
5. 攻城坦克：83.5

**关键发现**：
- 除灵魂巧匠外，其他单位CEV差距从4倍缩小到1.3倍
- 更符合实战体验，各单位各有特色
- 模型预测与玩家感受基本一致