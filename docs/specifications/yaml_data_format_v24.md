# v2.4 YAML数据格式规范

**版本**: 2.4  
**最后更新**: 2025-01-15  
**作者**: AI Assistant

## 概述

本文档定义了星际争霸II合作任务单位评估系统v2.4版本的YAML数据格式规范。所有数据文件必须严格遵循此规范以确保系统的正确运行。

## 目录结构

```
data/
├── units/          # 单位数据文件
├── weapons/        # 武器数据文件  
├── compositions/   # 标准化埃蒙部队配置
└── commanders/     # 指挥官配置文件
```

## 1. 单位数据格式 (units/)

### 文件命名规则
- 格式：`{unit_name}_{commander}.yaml`
- 示例：`liberator_nova.yaml`, `wrathwalker_alarak.yaml`

### 数据结构

```yaml
unit:
  # 基础标识
  id: string              # 游戏内部ID
  name: string            # 中文名称
  name_en: string         # 英文名称
  commander: string       # 所属指挥官
  race: string            # 种族 (Terr/Prot/Zerg)
  
  # 基础属性
  stats:
    life: number          # 生命值
    armor: number         # 护甲值
    shields: number       # 护盾值（神族单位）
    energy: number        # 能量值（如果有）
    
  # 成本信息
  cost:
    minerals: number      # 矿物成本
    vespene: number       # 瓦斯成本
    supply: number        # 人口占用
    build_time: number    # 建造时间（秒）
    
  # 移动属性
  movement:
    speed: number         # 移动速度
    acceleration: number  # 加速度
    turning_rate: number  # 转向速率
    
  # 物理属性
  physics:
    radius: number        # 碰撞半径
    sight: number         # 视野范围
    height: number        # 单位高度
    
  # 单位类型和属性
  plane: string           # 移动平面 (Ground/Air)
  attributes:             # 属性标签列表
    - string
    
  # 武器配置
  weapons:
    - mode: string        # 武器模式标识
      weapon_ref: string  # 武器数据引用
      is_default: boolean # 是否默认武器
      
  # 特殊能力
  abilities:              # 能力列表
    - string
    
  # 模式切换（如果有）
  modes:
    mode_name:
      unit_id: string
      sight: number
      can_move: boolean
      weapons: [string]
```

## 2. 武器数据格式 (weapons/)

### 文件命名规则
- 格式：`{unit_name}_weapons.yaml`
- 示例：`liberator_weapons.yaml`

### 数据结构

```yaml
weapons:
  - id: string            # 武器ID
    name: string          # 中文名称
    name_en: string       # 英文名称
    
    # 目标类型
    target_filters:       # 可攻击目标
      - string
    exclude_filters:      # 不可攻击目标
      - string
      
    # 武器属性
    stats:
      damage: number      # 基础伤害
      damage_type: string # 伤害类型
      attacks: number     # 攻击次数
      period: number      # 攻击间隔（秒）
      range: number       # 攻击射程
      
    # 攻击特性
    properties:
      splash_radius: number  # 溅射半径（如果有）
      splash_damage: array   # 溅射伤害衰减
      arc: number           # 攻击角度
```

## 3. 指挥官配置格式 (commanders/)

### 文件命名规则
- 格式：`{commander_name}.yaml`
- 示例：`nova.yaml`, `alarak.yaml`

### 数据结构

```yaml
commander:
  id: string              # 指挥官ID
  name: string            # 中文名称
  name_en: string         # 英文名称
  race: string            # 种族
  
  # 基础属性
  properties:
    population_cap: number     # 人口上限
    starting_minerals: number  # 起始矿物
    starting_vespene: number   # 起始瓦斯
    
  # 经济特性
  economy:
    mineral_gas_ratio: number      # 矿气价值比
    production_efficiency: number  # 生产效率
    
  # 精通系统
  masteries:
    set1/set2/set3:
      option1/option2:
        name: string
        max_level: number
        bonus_per_level: number
        affects: [string]
        calculation: string  # additive/multiplicative
        
  # 威望系统
  prestiges:
    - id: string
      name: string
      description: string
      bonuses: object
```

## 4. 标准化埃蒙部队配置 (compositions/)

### 文件命名规则
- 格式：`sac_{type}.yaml`
- 示例：`sac_terran.yaml`, `sac_zerg.yaml`

### 数据结构

```yaml
composition:
  id: string              # SAC标识
  name: string            # 名称
  description: string     # 描述
  
  # 单位组成
  units:
    - unit_id: string
      weight: number      # 权重（百分比）
      count: number       # 数量
      
  # 属性分布
  attribute_distribution:
    light: number         # 轻甲比例
    armored: number       # 重甲比例
    biological: number    # 生物比例
    mechanical: number    # 机械比例
    
  # 平均属性
  average_stats:
    ehp: number          # 平均有效生命值
    dps: number          # 平均DPS
```

## 5. 数据验证规则

### 必填字段
- 所有标记为 `string` 或 `number` 的字段都是必填的
- 可选字段会明确标注

### 数据类型
- `string`: 文本字符串
- `number`: 数字（整数或浮点数）
- `boolean`: 布尔值（true/false）
- `array`: 数组
- `object`: 对象

### 引用完整性
- `weapon_ref` 必须指向存在的武器ID
- `commander` 必须是有效的指挥官名称
- `unit_id` 在模式切换中必须有效

## 6. 最佳实践

1. **注释**：使用 `#` 添加注释说明数据来源
2. **TODO标记**：对于缺失数据使用 `# TODO:` 标记
3. **版本控制**：在文件头部标注最后更新时间
4. **数据来源**：明确标注数据来源（XML/游戏测试/理论计算）
5. **单位一致**：
   - 时间：秒
   - 距离：游戏单位
   - 百分比：小数形式（如0.15表示15%）

## 7. 扩展性考虑

本格式设计考虑了未来的扩展需求：
- 支持新的单位属性
- 支持新的武器类型
- 支持新的指挥官机制
- 支持版本化数据管理 