# 星际争霸II数学模型 - 评估指标体系

## 当前已实现的指标

### 1. 核心指标 - CEV (Combat Effectiveness Value)
```python
CEV = (effective_dps * effective_hp) / effective_cost
```
- **动态化**: CEV随时间、指挥官、支援单位数量变化
- **λ(t)函数**: 反映资源价值随时间递减

### 2. 效率指标
- **resource_efficiency**: 资源效率 = effective_dps / effective_cost
- **supply_efficiency**: 人口效率 = effective_dps / supply_cost  
- **survivability**: 生存能力 = effective_hp / effective_cost

### 3. 战术价值指标
- **range_advantage**: 射程优势 = range / 5.0 (标准化)
- **mobility**: 机动性 = speed / 2.5 (标准化)
- **special_abilities**: 特殊能力数量

### 4. 综合评分 (Overall Score)
```python
overall_score = (
    weights["resource_efficiency"] * resource_efficiency * 100 +
    weights["combat_power"] * cev +
    weights["versatility"] * (range_advantage + mobility + special_abilities * 0.2)
)
```

权重根据游戏阶段调整：
- 早期: 重视资源效率
- 中期: 平衡各项指标
- 后期: 重视战斗力

## 需要补充的指标

根据论文，以下高级指标尚未完全实现：

### 1. 协同效应量化
- **治疗协同**: H = min(n_h * h_r, n_t * d_r) * η
- **增益叠加**: CEV_buffed = CEV_base * ∏(1 + B_k) * ∏A_j
- **控制削弱**: Θ = 1 - Σ(t_cc,i/T * p_hit,i * (1 - r_immune))

### 2. 特殊组合评分
- **运输协同** (如大力神-坦克)
- **光环效应** (如女王注能)
- **科技协同** (如钒合金板)

### 3. 战斗效能矩阵 (CEM)
- 单位间克制关系的完整矩阵
- 基于属性克制的DPS修正

### 4. 多维度平衡指标
- **生产约束指数**: 考虑建筑需求、科技需求
- **辅助效用值**: 侦查、控制、增益等非直接战斗贡献
- **情景适应性**: 对空/对地能力、AOE/单体等

## 建议实现优先级

1. **高优先级**
   - 完善CEM矩阵的属性克制计算
   - 实现基础的协同效应加成

2. **中优先级**  
   - 添加生产约束和科技需求评估
   - 实现特殊组合的额外加分

3. **低优先级**
   - 复杂的控制效果量化
   - 完整的辅助效用评估体系

## 使用建议

当前的overall_score已经能够较好地反映单位的综合价值，但在以下场景可能需要调整：

1. **评估支援单位**: 增加辅助效用权重
2. **评估高科技单位**: 考虑生产约束的影响
3. **评估组合阵容**: 需要额外的协同效应计算

## 数学模型扩展方向

1. **非线性效应**: 某些增益可能是非线性的（如递减效应）
2. **时序依赖**: 某些单位的价值随游戏进程变化（如侦察单位）
3. **不确定性**: 加入概率因素（如技能命中率、暴击等）