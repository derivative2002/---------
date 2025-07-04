# 数据提取脚本使用说明

## 快速开始

### 1. 找到游戏数据路径

**Windows:**
```
C:\Program Files (x86)\StarCraft II\Mods\AlliedCommanders.SC2Mod\Base.SC2Data\GameData
```

**Mac:**
```
/Applications/StarCraft II/Mods/AlliedCommanders.SC2Mod/Base.SC2Data/GameData
```

### 2. 运行提取脚本

```bash
# 基本用法
python scripts/extract_sc2_data.py "/路径/到/GameData"

# 提取并转换为数据库格式
python scripts/extract_sc2_data.py "/路径/到/GameData" --convert

# 指定输出目录
python scripts/extract_sc2_data.py "/路径/到/GameData" --output "data/my_extraction"
```

### 3. 输出文件

脚本会生成以下文件：
- `units_coop.csv` - 所有合作任务单位数据
- `weapons_coop.csv` - 武器系统数据
- `abilities_coop.csv` - 能力数据
- `upgrades_coop.csv` - 升级数据

如果使用 `--convert` 选项，还会生成：
- `units_master_auto.csv` - 符合项目格式的单位数据
- `weapons_auto.csv` - 符合项目格式的武器数据
- `abilities_auto.csv` - 符合项目格式的能力数据

## 数据处理流程

1. **提取原始数据**：从XML文件中读取游戏数据
2. **过滤合作任务内容**：只保留合作任务相关的单位
3. **转换为标准格式**：将游戏内部格式转换为项目使用的格式
4. **中文本地化**：应用中文翻译（需要额外的翻译表）

## 注意事项

1. **需要游戏安装**：必须安装了星际争霸II才能访问数据文件
2. **版本更新**：游戏更新后需要重新提取数据
3. **权限问题**：某些系统可能需要管理员权限访问游戏文件
4. **数据完整性**：提取的数据可能需要手动补充中文翻译

## 高级用法

### 只提取特定指挥官的数据

修改脚本中的 `COMMANDER_PREFIXES` 来只包含需要的指挥官。

### 添加自定义字段

在 `_parse_unit` 等方法中添加新的数据提取逻辑。

### 处理本地化

游戏的中文文本通常在单独的文件中：
```
/Mods/AlliedCommanders.SC2Mod/zhCN.SC2Data/LocalizedData/GameStrings.txt
```

可以解析这个文件来获取中文翻译。

## 故障排除

**找不到数据文件**
- 确认游戏安装路径正确
- 确认安装了合作任务模式

**解析错误**
- 检查游戏版本是否太新（XML格式可能变化）
- 查看日志文件了解具体错误

**数据不完整**
- 某些数据可能分散在多个XML文件中
- 需要交叉引用多个文件才能获得完整数据