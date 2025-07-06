"""
YAML数据加载器 - v2.4
负责加载和验证所有YAML格式的游戏数据
"""
import yaml
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import logging

# 设置日志
logger = logging.getLogger(__name__)

# 数据根目录
DATA_ROOT = Path(__file__).parent.parent.parent / "data"


@dataclass
class WeaponData:
    """武器数据结构"""
    id: str
    name: str
    name_en: str
    target_filters: List[str]
    exclude_filters: List[str]
    damage: float
    damage_type: str
    attacks: int
    period: float
    range: float
    splash_radius: float = 0.0
    splash_damage: List[float] = field(default_factory=list)
    arc: float = 0.0
    attribute_bonus: Dict[str, float] = field(default_factory=dict)
    upgrades: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WeaponData':
        """从字典创建武器数据"""
        stats = data.get('stats', {})
        properties = data.get('properties', {})
        
        return cls(
            id=data['id'],
            name=data['name'],
            name_en=data['name_en'],
            target_filters=data.get('target_filters', []),
            exclude_filters=data.get('exclude_filters', []),
            damage=stats.get('damage', 0),
            damage_type=stats.get('damage_type', 'Normal'),
            attacks=stats.get('attacks', 1),
            period=stats.get('period', 1.0),
            range=stats.get('range', 0),
            splash_radius=properties.get('splash_radius', 0.0),
            splash_damage=properties.get('splash_damage', []),
            arc=properties.get('arc', 0.0),
            attribute_bonus=data.get('attribute_bonus', {}),
            upgrades=data.get('upgrades', {})
        )


@dataclass
class UnitData:
    """单位数据结构"""
    id: str
    name: str
    name_en: str
    commander: str
    race: str
    # 基础属性
    life: float
    armor: float
    shields: float
    energy: float
    # 成本
    minerals: int
    vespene: int
    supply: int
    build_time: float
    # 移动
    speed: float
    acceleration: float
    turning_rate: float
    # 物理
    radius: float
    sight: float
    height: float
    # 类型
    plane: str
    attributes: List[str]
    # 武器
    weapons: List[Dict[str, Any]]
    # 能力
    abilities: List[str]
    # 模式
    modes: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnitData':
        """从字典创建单位数据"""
        unit = data['unit']
        stats = unit.get('stats', {})
        cost = unit.get('cost', {})
        movement = unit.get('movement', {})
        physics = unit.get('physics', {})
        
        return cls(
            id=unit['id'],
            name=unit['name'],
            name_en=unit['name_en'],
            commander=unit['commander'],
            race=unit['race'],
            # 基础属性
            life=stats.get('life', 0),
            armor=stats.get('armor', 0),
            shields=stats.get('shields', 0),
            energy=stats.get('energy', 0),
            # 成本
            minerals=cost.get('minerals', 0),
            vespene=cost.get('vespene', 0),
            supply=cost.get('supply', 0),
            build_time=cost.get('build_time', 0),
            # 移动
            speed=movement.get('speed', 0),
            acceleration=movement.get('acceleration', 0),
            turning_rate=movement.get('turning_rate', 0),
            # 物理
            radius=physics.get('radius', 0),
            sight=physics.get('sight', 0),
            height=physics.get('height', 0),
            # 类型
            plane=unit.get('plane', 'Ground'),
            attributes=unit.get('attributes', []),
            # 武器
            weapons=unit.get('weapons', []),
            # 能力
            abilities=unit.get('abilities', []),
            # 模式
            modes=unit.get('modes', {})
        )


@dataclass
class CommanderData:
    """指挥官数据结构"""
    id: str
    name: str
    name_en: str
    race: str
    population_cap: int
    mineral_gas_ratio: float
    production_efficiency: float
    masteries: Dict[str, Any]
    prestiges: List[Dict[str, Any]]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommanderData':
        """从字典创建指挥官数据"""
        commander = data['commander']
        properties = commander.get('properties', {})
        economy = commander.get('economy', {})
        
        return cls(
            id=commander['id'],
            name=commander['name'],
            name_en=commander['name_en'],
            race=commander['race'],
            population_cap=properties.get('population_cap', 200),
            mineral_gas_ratio=economy.get('mineral_gas_ratio', 2.5),
            production_efficiency=economy.get('production_efficiency', 1.0),
            masteries=commander.get('masteries', {}),
            prestiges=commander.get('prestiges', [])
        )


class YAMLDataLoader:
    """YAML数据加载器主类"""
    
    def __init__(self, data_root: Optional[Path] = None):
        """初始化数据加载器"""
        self.data_root = data_root or DATA_ROOT
        self.units: Dict[str, UnitData] = {}
        self.weapons: Dict[str, WeaponData] = {}
        self.commanders: Dict[str, CommanderData] = {}
        
        # 确保数据目录存在
        if not self.data_root.exists():
            raise FileNotFoundError(f"数据目录不存在: {self.data_root}")
            
    def load_all(self) -> None:
        """加载所有数据"""
        self.load_commanders()
        self.load_weapons()
        self.load_units()
        
    def load_units(self) -> Dict[str, UnitData]:
        """加载所有单位数据"""
        units_dir = self.data_root / "units"
        if not units_dir.exists():
            logger.warning(f"单位数据目录不存在: {units_dir}")
            return self.units
            
        for file_path in units_dir.glob("*.yaml"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    unit = UnitData.from_dict(data)
                    self.units[unit.id] = unit
                    logger.info(f"加载单位数据: {unit.name} ({unit.id})")
            except Exception as e:
                logger.error(f"加载单位数据失败 {file_path}: {e}")
                
        return self.units
        
    def load_weapons(self) -> Dict[str, WeaponData]:
        """加载所有武器数据"""
        weapons_dir = self.data_root / "weapons"
        if not weapons_dir.exists():
            logger.warning(f"武器数据目录不存在: {weapons_dir}")
            return self.weapons
            
        for file_path in weapons_dir.glob("*.yaml"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    for weapon_data in data.get('weapons', []):
                        weapon = WeaponData.from_dict(weapon_data)
                        self.weapons[weapon.id] = weapon
                        logger.info(f"加载武器数据: {weapon.name} ({weapon.id})")
            except Exception as e:
                logger.error(f"加载武器数据失败 {file_path}: {e}")
                
        return self.weapons
        
    def load_commanders(self) -> Dict[str, CommanderData]:
        """加载所有指挥官数据"""
        commanders_dir = self.data_root / "commanders"
        if not commanders_dir.exists():
            logger.warning(f"指挥官数据目录不存在: {commanders_dir}")
            return self.commanders
            
        for file_path in commanders_dir.glob("*.yaml"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    commander = CommanderData.from_dict(data)
                    self.commanders[commander.id] = commander
                    logger.info(f"加载指挥官数据: {commander.name} ({commander.id})")
            except Exception as e:
                logger.error(f"加载指挥官数据失败 {file_path}: {e}")
                
        return self.commanders
        
    def get_unit(self, unit_id: str) -> Optional[UnitData]:
        """获取单位数据"""
        return self.units.get(unit_id)
        
    def get_weapon(self, weapon_id: str) -> Optional[WeaponData]:
        """获取武器数据"""
        return self.weapons.get(weapon_id)
        
    def get_commander(self, commander_id: str) -> Optional[CommanderData]:
        """获取指挥官数据"""
        return self.commanders.get(commander_id)
        
    def validate_references(self) -> List[str]:
        """验证数据引用完整性"""
        errors = []
        
        # 验证单位的武器引用
        for unit_id, unit in self.units.items():
            for weapon_config in unit.weapons:
                weapon_ref = weapon_config.get('weapon_ref')
                if weapon_ref and weapon_ref not in self.weapons:
                    errors.append(f"单位 {unit.name} 引用了不存在的武器: {weapon_ref}")
                    
            # 验证指挥官引用
            if unit.commander not in self.commanders:
                errors.append(f"单位 {unit.name} 引用了不存在的指挥官: {unit.commander}")
                
        return errors


# 测试代码
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 创建加载器
    loader = YAMLDataLoader()
    
    # 加载所有数据
    loader.load_all()
    
    # 打印加载结果
    print(f"\n加载完成:")
    print(f"- 单位数量: {len(loader.units)}")
    print(f"- 武器数量: {len(loader.weapons)}")
    print(f"- 指挥官数量: {len(loader.commanders)}")
    
    # 验证引用
    errors = loader.validate_references()
    if errors:
        print(f"\n发现 {len(errors)} 个引用错误:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n数据引用验证通过！") 