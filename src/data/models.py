"""
星际争霸II单位数据模型定义
基于数据格式规范v2.0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import json


class WeaponType(Enum):
    """武器攻击类型"""
    GROUND = "ground"
    AIR = "air"
    BOTH = "both"


class SplashType(Enum):
    """溅射类型"""
    NONE = "none"
    LINEAR = "linear"
    CIRCULAR = "circular"
    CONE = "cone"


class AbilityType(Enum):
    """能力类型"""
    ACTIVE = "active"
    PASSIVE = "passive"
    TOGGLE = "toggle"


class ModeType(Enum):
    """单位模式类型"""
    DEFAULT = "default"
    ALTERNATE = "alternate"


@dataclass
class SplashParams:
    """溅射参数"""
    radius: List[float] = field(default_factory=list)
    damage: List[float] = field(default_factory=list)
    type: SplashType = SplashType.NONE
    angle: Optional[float] = None  # 仅用于cone类型
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SplashParams':
        """从JSON字符串创建"""
        if not json_str or json_str == "{}":
            return cls()
        data = json.loads(json_str)
        return cls(
            radius=data.get('radius', []),
            damage=data.get('damage', []),
            type=SplashType(data.get('type', 'none')),
            angle=data.get('angle')
        )


@dataclass
class Weapon:
    """武器系统"""
    unit_id: str
    weapon_name: str
    weapon_type: WeaponType
    base_damage: float
    attack_count: int = 1
    attack_interval: float = 1.0
    range: float = 5.0
    bonus_damage: Dict[str, float] = field(default_factory=dict)
    splash_type: SplashType = SplashType.NONE
    splash_params: Optional[SplashParams] = None
    
    @property
    def dps(self) -> float:
        """计算基础DPS"""
        return (self.base_damage * self.attack_count) / self.attack_interval
    
    def effective_damage(self, target_attributes: List[str]) -> float:
        """计算对特定目标的有效伤害"""
        damage = self.base_damage
        for attr in target_attributes:
            damage += self.bonus_damage.get(attr, 0)
        return damage * self.attack_count


@dataclass
class AbilityEffect:
    """能力效果"""
    damage: float = 0
    heal: float = 0
    buff: Dict[str, float] = field(default_factory=dict)
    debuff: Dict[str, float] = field(default_factory=dict)
    chance: Optional[float] = None # 触发几率
    mutations: Optional[List[str]] = None # 基因突变列表
    # 新增: 允许未定义字段
    misc: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AbilityCost:
    """能力消耗"""
    energy: float = 0
    hp: float = 0
    cooldown: float = 0


@dataclass
class Ability:
    """特殊能力"""
    name: str
    type: AbilityType
    cost: AbilityCost = field(default_factory=AbilityCost)
    effect: AbilityEffect = field(default_factory=AbilityEffect)
    target: str = "self"  # self/ally/enemy
    range: float = 0
    radius: float = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Ability':
        """从字典创建"""
        effect_data = data.get('effect', {})
        known_effect_keys = {'damage', 'heal', 'buff', 'debuff', 'chance', 'mutations'}
        misc_effects = {k: v for k, v in effect_data.items() if k not in known_effect_keys}
        
        effect = AbilityEffect(
            damage=effect_data.get('damage', 0),
            heal=effect_data.get('heal', 0),
            buff=effect_data.get('buff', {}),
            debuff=effect_data.get('debuff', {}),
            chance=effect_data.get('chance'),
            mutations=effect_data.get('mutations'),
            misc=misc_effects
        )

        return cls(
            name=data['name'],
            type=AbilityType(data.get('type', 'active')),
            cost=AbilityCost(**data.get('cost', {})),
            effect=effect,
            target=data.get('target', 'self'),
            range=data.get('range', 0),
            radius=data.get('radius', 0)
        )


@dataclass
class UnitMode:
    """单位模式/形态"""
    unit_id: str
    mode_name: str
    mode_type: ModeType
    stat_modifiers: Dict[str, float] = field(default_factory=dict)
    weapon_config: str = ""
    switch_time: float = 0
    
    def apply_modifiers(self, base_stats: Dict[str, float]) -> Dict[str, float]:
        """应用属性修正"""
        modified_stats = base_stats.copy()
        for stat, modifier in self.stat_modifiers.items():
            if stat in modified_stats:
                # 如果是0，表示该属性被禁用（如攻城模式移动速度）
                if modifier == 0:
                    modified_stats[stat] = 0
                else:
                    modified_stats[stat] += modifier
        return modified_stats


@dataclass
class Unit:
    """单位完整数据模型"""
    # 基础信息
    english_id: str
    chinese_name: str
    commander: str
    
    # 资源成本
    mineral_cost: int
    gas_cost: int
    supply_cost: float
    
    # 战斗属性
    hp: int
    shields: int = 0
    armor: int = 0
    
    # 物理属性
    collision_radius: Optional[float] = None
    movement_speed: float = 2.5
    is_flying: bool = False
    
    # 标签和能力
    attributes: List[str] = field(default_factory=list)
    abilities: List[Ability] = field(default_factory=list)
    
    # 关联数据
    weapons: List[Weapon] = field(default_factory=list)
    modes: List[UnitMode] = field(default_factory=list)
    
    @property
    def equivalent_cost(self) -> float:
        """计算等效成本（矿物 + 2.5 * 瓦斯）"""
        return self.mineral_cost + 2.5 * self.gas_cost
    
    @property
    def effective_hp(self) -> float:
        """计算有效生命值（考虑护甲）"""
        armor_reduction = self.armor / (self.armor + 10)
        return self.shields + self.hp / (1 - armor_reduction)
    
    def get_weapon_for_target(self, is_air_target: bool) -> Optional[Weapon]:
        """获取针对特定目标类型的武器"""
        target_type = WeaponType.AIR if is_air_target else WeaponType.GROUND
        
        for weapon in self.weapons:
            if weapon.weapon_type == WeaponType.BOTH:
                return weapon
            elif weapon.weapon_type == target_type:
                return weapon
        return None
    
    def get_mode(self, mode_name: str) -> Optional[UnitMode]:
        """获取特定模式"""
        for mode in self.modes:
            if mode.mode_name == mode_name:
                return mode
        return None
    
    def get_ability(self, ability_name: str) -> Optional[Ability]:
        """获取特定能力"""
        for ability in self.abilities:
            if ability.name == ability_name:
                return ability
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'english_id': self.english_id,
            'chinese_name': self.chinese_name,
            'commander': self.commander,
            'mineral_cost': self.mineral_cost,
            'gas_cost': self.gas_cost,
            'supply_cost': self.supply_cost,
            'hp': self.hp,
            'shields': self.shields,
            'armor': self.armor,
            'collision_radius': self.collision_radius,
            'movement_speed': self.movement_speed,
            'is_flying': self.is_flying,
            'attributes': self.attributes,
            'abilities': [ability.__dict__ for ability in self.abilities],
            'weapons': [weapon.__dict__ for weapon in self.weapons],
            'modes': [mode.__dict__ for mode in self.modes]
        }


@dataclass
class CommanderConfig:
    """指挥官配置"""
    name: str
    population_cap: int = 200
    modifiers: Dict[str, float] = field(default_factory=dict)
    special_mechanics: List[str] = field(default_factory=list)
    
    def apply_modifier(self, unit: Unit) -> Unit:
        """应用指挥官修正到单位"""
        # 这里可以根据指挥官特性修改单位属性
        # 例如诺娃的单位有更高的伤害
        modified_unit = unit  # 实际实现时应该深拷贝
        
        # 应用通用修正
        if 'damage' in self.modifiers:
            for weapon in modified_unit.weapons:
                weapon.base_damage *= self.modifiers['damage']
        
        if 'hp' in self.modifiers:
            modified_unit.hp = int(modified_unit.hp * self.modifiers['hp'])
            
        return modified_unit


class UnitDatabase:
    """单位数据库管理器"""
    
    def __init__(self):
        self.units: Dict[str, Unit] = {}
        self.commanders: Dict[str, CommanderConfig] = {}
        
    def add_unit(self, unit: Unit):
        """添加单位到数据库"""
        key = f"{unit.commander}_{unit.english_id}"
        self.units[key] = unit
        
    def get_unit(self, commander: str, unit_id: str) -> Optional[Unit]:
        """获取特定单位"""
        key = f"{commander}_{unit_id}"
        return self.units.get(key)
        
    def get_commander_units(self, commander: str) -> List[Unit]:
        """获取指挥官的所有单位"""
        return [unit for unit in self.units.values() 
                if unit.commander == commander]
    
    def get_units_by_attribute(self, attribute: str) -> List[Unit]:
        """获取具有特定属性的单位"""
        return [unit for unit in self.units.values() 
                if attribute in unit.attributes]
    
    def validate_data(self) -> List[str]:
        """验证数据完整性"""
        errors = []
        
        for key, unit in self.units.items():
            # 检查必填字段
            if not unit.english_id:
                errors.append(f"{key}: 缺少english_id")
            if not unit.chinese_name:
                errors.append(f"{key}: 缺少chinese_name")
                
            # 检查数值合理性
            if unit.hp <= 0:
                errors.append(f"{key}: HP必须大于0")
            if unit.mineral_cost < 0 or unit.gas_cost < 0:
                errors.append(f"{key}: 成本不能为负")
                
            # 检查武器配置
            if not unit.weapons:
                errors.append(f"{key}: 没有配置武器")
                
            # 检查地面单位的碰撞半径
            if not unit.is_flying and unit.collision_radius is None:
                errors.append(f"{key}: 地面单位必须有碰撞半径")
                
        return errors