# 数据收集与格式完整指南

## 快速开始

### 第一步：准备CSV文件
在 `data/units/` 目录下创建或编辑以下文件：
1. `units_master.csv` - 单位基础数据
2. `weapons.csv` - 武器系统数据
3. `unit_modes.csv` - 模式切换数据（可选）

### 第二步：填写数据
按照下方的字段说明和示例填写数据

### 第三步：验证和导入
```bash
# 验证数据格式
python3 -m src.data.advanced_data_loader

# 导入数据库
python3 -m src.database.migrate_to_db
```

## 官方指挥官名称（必须使用）

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

## 数据表详细说明

### 1. 单位主数据表 (units_master.csv)

| 字段名 | 说明 | 数据类型 | 必填 | 示例 |
|--------|------|----------|------|------|
| english_id | 英文ID。**重要：如果多个指挥官拥有同名但属性不同的单位，必须使用"指挥官姓氏"作为后缀以区分，如"SiegeTank_Swann"。** | string | ✓ | Marine |
| chinese_name | 中文名 | string | ✓ | 陆战队员 |
| commander | 指挥官 | string | ✓ | 吉姆·雷诺 |
| mineral_cost | 矿物成本 | integer | ✓ | 45 |
| gas_cost | 瓦斯成本 | integer | ✓ | 0 |
| supply_cost | 人口占用 | float | ✓ | 1 |
| hp | 生命值 | integer | ✓ | 55 |
| shields | 护盾 | integer | ✓ | 0 |
| armor | 护甲 | integer | ✓ | 0 |
| collision_radius | 碰撞半径 | float | ✗ | 0.375 |
| movement_speed | 移动速度 | float | ✓ | 3.15 |
| is_flying | 是否飞行 | boolean | ✓ | false |
| attributes | 属性标签 | string | ✓ | "生物,轻甲" |
| special_abilities | 特殊能力 | JSON | ✗ | 见下方 |

**属性标签列表**：
- 轻甲 (Light)
- 重甲 (Armored)
- 生物 (Biological)
- 机械 (Mechanical)
- 灵能 (Psionic)
- 巨型 (Massive)
- 英雄 (Heroic)
- 召唤物 (Summoned)

**示例行**：
```csv
Marine,陆战队员,吉姆·雷诺,45,0,1,55,0,0,0.375,3.15,false,"生物,轻甲","[{""name"":""兴奋剂"",""type"":""active"",""cost"":{""hp"":10},""effect"":{""buff"":{""attack_speed"":1.5,""movement_speed"":1.5}}}]"
```

### 2. 武器系统表 (weapons.csv)

| 字段名 | 说明 | 数据类型 | 必填 | 示例 |
|--------|------|----------|------|------|
| unit_id | 单位ID | string | ✓ | Marine |
| weapon_name | 武器名称 | string | ✓ | 高斯步枪 |
| weapon_type | 攻击类型 | string | ✓ | both |
| base_damage | 基础伤害 | float | ✓ | 6 |
| attack_count | 攻击次数 | integer | ✓ | 1 |
| attack_interval | 攻击间隔 | float | ✓ | 0.86 |
| range | 射程 | float | ✓ | 5 |
| bonus_damage | 伤害加成 | JSON | ✗ | {"重甲":10} |
| splash_type | 溅射类型 | string | ✓ | none |
| splash_params | 溅射参数 | JSON | ✗ | 见下方 |

**攻击类型**：ground / air / both

**溅射类型**：none / linear / circular / cone

**示例行**：
```csv
Marine,高斯步枪,both,6,1,0.86,5,{},none,{}
SiegeTank,震荡炮,ground,40,1,2.14,13,"{""重甲"":30}",circular,"{""radius"":[0.4687,0.7812,1.25],""damage"":[1.0,0.5,0.25]}"
```

### 3. 单位模式表 (unit_modes.csv)

| 字段名 | 说明 | 数据类型 | 必填 | 示例 |
|--------|------|----------|------|------|
| unit_id | 单位ID | string | ✓ | SiegeTank |
| mode_name | 模式名称 | string | ✓ | 攻城模式 |
| mode_type | 模式类型 | string | ✓ | alternate |
| stat_modifiers | 属性修正 | JSON | ✗ | {"armor":3} |
| weapon_config | 武器配置 | string | ✓ | 震荡炮 |
| switch_time | 切换时间 | float | ✓ | 3.0 |

**模式类型**：default / alternate

**示例行**：
```csv
SiegeTank,坦克模式,default,{},90mm火炮,0
SiegeTank,攻城模式,alternate,"{""armor"":3,""movement_speed"":-2.25}",震荡炮,3.0
```

## JSON格式详解

### 特殊能力格式
```json
[{
  "name": "兴奋剂",
  "type": "active",  // active/passive/toggle
  "cost": {
    "energy": 0,
    "hp": 10,
    "cooldown": 0
  },
  "effect": {
    "damage": 0,
    "heal": 0,
    "buff": {
      "attack_speed": 1.5,
      "movement_speed": 1.5
    },
    "debuff": {
      "slow": 0.5
    }
  }
}]
```

### 伤害加成格式
```json
{
  "重甲": 10,
  "轻甲": 0,
  "生物": 5
}
```

### 溅射参数格式
```json
{
  "radius": [0.4687, 0.7812, 1.25],  // 内中外圈半径
  "damage": [1.0, 0.5, 0.25],        // 对应伤害比例
  "angle": 60                        // 仅用于cone类型
}
```

### 属性修正格式
```json
{
  "armor": 3,              // 护甲增加3
  "movement_speed": -2.25, // 移动速度减少2.25
  "damage": 1.5           // 伤害增加50%
}
```

## 特殊情况处理

### 1. 多武器单位
一个单位可能有多个武器，需要分别记录：
```csv
Battlecruiser,ATA激光炮,ground,8,1,0.16,6,{},none,{}
Battlecruiser,ATS激光炮,air,6,1,0.16,6,{},none,{}
```

### 2. 英雄单位
- 矿物成本和瓦斯成本都填0
- 人口占用通常也是0
- 必须包含"英雄"属性标签

### 3. 可变形单位
- 需要在unit_modes.csv中定义所有模式
- 每个模式对应不同的武器配置
- 注意记录模式切换时间

### 4. CSV中的JSON转义
在CSV中使用JSON时，需要用双引号转义：
- 原始：`{"重甲":10}`
- CSV中：`"{""重甲"":10}"`

### 5. 不同指挥官的同名单位
**这是数据准确性的关键。** 当两个或以上指挥官拥有名称相同但能力或属性有差异的单位时（如雷诺和斯旺的攻城坦克），必须通过修改`english_id`来区分。

**规则**：
- 保留一个指挥官的单位使用基础ID（通常是首次引入该单位的指挥官，如雷诺的`SiegeTank`）。
- 其他指挥官的同名单位，其`english_id`必须添加下划线和指挥官姓氏的英文，如`SiegeTank_Swann`。
- 对应的`weapons.csv`和`unit_modes.csv`中的`unit_id`也必须使用这个新的、唯一的ID。

**示例**：
`units_master.csv`:
```csv
SiegeTank_Raynor,攻城坦克,吉姆·雷诺,150,125,3,200,0,1,...
SiegeTank_Swann,攻城坦克,斯旺,150,125,3,192,0,1,...
```

`weapons.csv`:
```csv
SiegeTank_Raynor,90mm火炮,...
SiegeTank_Swann,90mm火炮,...
```

## 数据验证检查项

1. **必填字段完整性**
   - 所有标记为必填的字段都不能为空
   - 数值型字段必须为有效数字

2. **引用一致性**
   - weapons.csv中的unit_id必须存在于units_master.csv
   - unit_modes.csv中的weapon_config必须对应有效武器

3. **逻辑合理性**
   - 飞行单位可以没有碰撞半径
   - 地面单位必须有碰撞半径
   - DPS = (base_damage × attack_count) / attack_interval

4. **命名规范**
   - 使用官方中文译名
   - 英文ID与游戏内部一致
   - 指挥官名称必须在18个官方名称中

## 数据来源推荐

1. 游戏内单位信息面板（最准确）
2. [星际争霸中文维基](https://starcraft.huijiwiki.com/)
3. 合作任务社区数据库
4. 暴雪官方更新日志

## 常见错误和解决方案

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| JSON解析失败 | 引号转义错误 | 使用双引号转义 |
| 单位ID不匹配 | 拼写错误 | 检查英文ID大小写 |
| 数据验证失败 | 缺少必填字段 | 补充完整数据 |
| 导入失败 | 指挥官名称错误 | 使用官方18个名称 |

## 联系支持

如遇到数据格式问题，请：
1. 检查本指南的示例
2. 运行验证脚本查看错误信息
3. 在项目中创建Issue寻求帮助