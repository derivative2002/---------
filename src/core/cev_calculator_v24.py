"""
精细化CEV计算器 v2.4
严格按照v2.4论文实现的战斗效能值计算器

核心公式：
CEV = (DPS_eff × Ψ × EHP × Ω × F_range) / C_eff × μ

其中：
- DPS_eff: 有效伤害输出
- Ψ: 过量击杀惩罚系数
- EHP: 有效生命值
- Ω: 操作难度系数
- F_range: 射程系数
- C_eff: 有效成本
- μ: 人口质量乘数
"""
import math
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
import logging
import yaml
from pathlib import Path
from copy import deepcopy

from src.data.yaml_loader import YAMLDataLoader, UnitData, WeaponData, CommanderData

# 设置日志
logger = logging.getLogger(__name__)


@dataclass
class CalculationConfig:
    """计算配置参数"""
    # 矿气转换率（默认值）
    mineral_gas_ratio: float = 2.5
    
    # 溅射系数配置
    splash_factors: Dict[str, float] = None
    
    # 操作难度系数
    operation_factors: Dict[str, float] = None
    
    # 过量击杀阈值
    overkill_thresholds: List[Tuple[float, float]] = None
    
    # 精通配置
    mastery_config: Dict[str, Any] = None
    
    # 场景配置
    scenario: str = "standard"
    
    # 人口税
    population_tax_per_supply: float = 12.5 # 每个supply对应12.5矿的建筑成本
    
    def __post_init__(self):
        """初始化默认值"""
        if self.splash_factors is None:
            self.splash_factors = {
                "SiegeTank": 1.25,       # 实际溅射效果
                "Liberator_AA": 2.5,     # 解放者AA模式AOE
                "Liberator_AG": 1.0,     # 解放者AG模式是单体
                "default": 1.0
            }
            
        if self.operation_factors is None:
            self.operation_factors = {
                "Wrathwalker": 1.1,      # 可移动射击
                "ColossusTaldarim": 1.1, # 天罚行者（内部ID）
                "SiegeTank": 0.8,        # 简单架设，但更笨重
                "Impaler": 0.9,          # 简单潜地
                "Liberator_AG": 0.75,    # 需要精确架设
                "Dragoon": 1.0,          # 标准操作
                "default": 1.0
            }
            
        if self.overkill_thresholds is None:
            # (伤害阈值, 惩罚系数)
            self.overkill_thresholds = [
                (200, 0.8),
                (150, 0.85),
                (100, 0.9),
                (0, 1.0)
            ]


class CEVCalculatorV24:
    """v2.4精细化CEV计算器"""
    
    def __init__(self, data_loader: YAMLDataLoader, config: Optional[CalculationConfig] = None):
        """
        初始化计算器
        
        Args:
            data_loader: YAML数据加载器
            config: 计算配置
        """
        self.data_loader = data_loader
        self.config = config or CalculationConfig()
        
    def calculate_cev(self, unit_id: str, weapon_mode: Optional[str] = None,
                     apply_mastery: bool = False, scenario: Optional[str] = None) -> Dict[str, Any]:
        """
        计算单位的CEV值
        
        Args:
            unit_id: 单位ID
            weapon_mode: 武器模式（如果单位有多种模式）
            apply_mastery: 是否应用精通加成
            scenario: 战斗场景 (e.g., 'standard', 'vs_armored')
            
        Returns:
            包含CEV值和详细计算过程的字典
        """
        current_scenario = scenario or self.config.scenario
        
        # 获取单位数据
        unit = self.data_loader.get_unit(unit_id)
        if not unit:
            raise ValueError(f"未找到单位: {unit_id}")
            
        # 创建单位数据的本地副本以避免修改原始数据
        unit_copy = deepcopy(unit)
            
        # 获取指挥官数据
        commander = self.data_loader.get_commander(unit_copy.commander)
        if not commander:
            raise ValueError(f"未找到指挥官: {unit_copy.commander}")
            
        # 获取武器数据
        weapon_data = self._get_weapon_for_mode(unit_copy, weapon_mode)
        if not weapon_data:
            raise ValueError(f"未找到武器数据: {unit_id} - {weapon_mode}")
            
        # 计算各项参数
        dps_eff = self._calculate_effective_dps(unit_copy, weapon_data, apply_mastery, commander, weapon_mode, current_scenario)
        psi = self._calculate_overkill_penalty(weapon_data)
        ehp = self._calculate_effective_hp(unit_copy, commander, apply_mastery)
        omega = self._calculate_operation_factor(unit_copy, weapon_mode)
        f_range = self._calculate_range_factor(weapon_data, unit_copy)
        c_eff = self._calculate_effective_cost(unit_copy, commander)
        mu = self._calculate_population_multiplier(commander)
        
        # 计算最终CEV
        # CEV (资源效率)
        cev = (dps_eff * psi * ehp * omega * f_range) / c_eff
        
        # CEV_per_pop (人口效率)
        effective_pop = unit_copy.supply * mu
        cev_per_pop = cev / effective_pop if effective_pop > 0 else 0
        
        # 返回详细结果
        return {
            "cev": round(cev, 2),
            "cev_per_pop": round(cev_per_pop, 2),
            "unit_name": unit_copy.name,
            "commander": commander.name,
            "weapon_mode": weapon_mode or "default",
            "scenario": current_scenario,
            "components": {
                "dps_eff": round(dps_eff, 2),
                "psi": round(psi, 2),
                "ehp": round(ehp, 2),
                "omega": round(omega, 2),
                "f_range": round(f_range, 2),
                "c_eff": round(c_eff, 2),
                "mu": round(mu, 2),
                "splash_factor": self._get_splash_factor(unit_copy, weapon_data, weapon_mode)
            },
            "details": {
                "base_damage": weapon_data.damage,
                "attacks": weapon_data.attacks,
                "period": weapon_data.period,
                "range": weapon_data.range,
                "life": unit_copy.life,
                "armor": unit_copy.armor,
                "shields": unit_copy.shields,
                "minerals": unit_copy.minerals,
                "vespene": unit_copy.vespene,
                "supply": unit_copy.supply
            }
        }
        
    def _get_weapon_for_mode(self, unit: UnitData, mode: Optional[str]) -> Optional[WeaponData]:
        """获取指定模式的武器数据"""
        if not unit.weapons:
            return None
            
        # 如果没有指定模式，使用默认武器
        if not mode:
            for weapon_config in unit.weapons:
                if weapon_config.get('is_default', False):
                    weapon_id = weapon_config.get('weapon_ref')
                    return self.data_loader.get_weapon(weapon_id)
            # 如果没有默认武器，使用第一个
            if unit.weapons:
                weapon_id = unit.weapons[0].get('weapon_ref')
                return self.data_loader.get_weapon(weapon_id)
                
        # 查找指定模式的武器
        for weapon_config in unit.weapons:
            if weapon_config.get('mode') == mode:
                weapon_id = weapon_config.get('weapon_ref')
                return self.data_loader.get_weapon(weapon_id)
                
        return None
        
    def _calculate_effective_dps(self, unit: UnitData, weapon: WeaponData,
                               apply_mastery: bool, commander: CommanderData, mode: Optional[str] = None,
                               scenario: str = "standard") -> float:
        """
        计算有效DPS
        DPS_eff = (基础伤害 × 攻击次数 × 溅射系数) / 攻击间隔
        """
        # 基础伤害
        damage = weapon.damage * weapon.attacks
        
        # 溅射系数
        splash_factor = self._get_splash_factor(unit, weapon, mode)
        
        # 攻击间隔
        period = weapon.period
        
        # 应用精通加成
        if apply_mastery:
            # 攻速加成
            attack_speed_bonus = self._get_mastery_attack_speed(commander)
            period = period / (1 + attack_speed_bonus)
            
        # 属性加成
        if hasattr(weapon, 'attribute_bonus'):
            if scenario == "vs_armored":
                damage += weapon.attribute_bonus.get("Armored", 0)
            elif scenario == "vs_light":
                damage += weapon.attribute_bonus.get("Light", 0)
            
        # 旋流弹加成
        if hasattr(weapon, 'upgrades') and "MaelstromRounds" in weapon.upgrades:
            damage += weapon.upgrades["MaelstromRounds"].get("bonus_damage_main_target", 0)
        
        # 计算DPS
        dps = (damage * splash_factor) / period
        
        return dps
        
    def _calculate_overkill_penalty(self, weapon: WeaponData) -> float:
        """
        计算过量击杀惩罚系数
        根据有效伤害判断惩罚程度
        """
        effective_damage = weapon.damage * weapon.attacks
        
        for threshold, penalty in self.config.overkill_thresholds:
            if effective_damage >= threshold:
                return penalty
                
        return 1.0
        
    def _calculate_effective_hp(self, unit: UnitData, commander: CommanderData, apply_mastery: bool) -> float:
        """
        计算有效生命值
        EHP = HP_eff + Shield_eff
        """
        life = unit.life
        
        # 斯旺生命值精通
        if apply_mastery and commander.id == "Swann":
            life *= (1 + self.config.mastery_config.get("Swann", {}).get("mech_life", 0.30))
        
        # 护甲减伤公式
        armor_reduction = unit.armor / (unit.armor + 10)
        hp_eff = life / (1 - armor_reduction)
        
        # 护盾（考虑回充）
        shield_eff = unit.shields * 1.4  # 40%额外价值
        
        return hp_eff + shield_eff
        
    def _calculate_operation_factor(self, unit: UnitData, mode: Optional[str]) -> float:
        """获取操作难度系数"""
        # 特殊模式处理
        if mode == "AG" and "Liberator" in unit.id:
            return self.config.operation_factors.get("Liberator_AG", 0.75)
            
        # 通用处理
        unit_type = unit.id.split('_')[0]
        # 兼容ImpalerDehaka
        if unit_type == "ImpalerDehaka":
            unit_type = "Impaler"
        # 兼容攻城坦克
        if unit_type == "SiegeTankSieged":
            unit_type = "SiegeTank"
        return self.config.operation_factors.get(unit_type, 
                                                self.config.operation_factors["default"])
        
    def _calculate_range_factor(self, weapon: WeaponData, unit: UnitData) -> float:
        """
        计算射程系数
        F_range = sqrt(射程 / 碰撞半径)
        """
        # 空军单位碰撞半径统一为0.5
        radius = 0.5 if unit.plane == "Air" else unit.radius
        
        return math.sqrt(weapon.range / radius)
        
    def _calculate_effective_cost(self, unit: UnitData, commander: CommanderData) -> float:
        """
        计算有效成本
        C_eff = (矿物 + 瓦斯 × α) + 人口税
        """
        minerals = unit.minerals
        vespene = unit.vespene
        supply = unit.supply

        # 使用指挥官的矿气转换率
        alpha = commander.mineral_gas_ratio
        base_cost = minerals + vespene * alpha

        # 计算人口税
        # 诺娃和德哈卡等指挥官没有补给建筑成本
        if not getattr(commander, 'no_supply_tax', False):
            population_tax = supply * self.config.population_tax_per_supply
            base_cost += population_tax

        return base_cost
        
    def _calculate_population_multiplier(self, commander: CommanderData) -> float:
        """
        计算人口质量乘数
        μ = 200 / 指挥官人口上限
        """
        return 200 / commander.population_cap
        
    def _get_splash_factor(self, unit: UnitData, weapon: WeaponData, mode: Optional[str] = None) -> float:
        """获取溅射系数"""
        if weapon.splash_radius > 0:
            unit_type = unit.id.split('_')[0]
            # 特殊处理解放者的不同模式
            if unit_type == "Liberator" and mode:
                key = f"{unit_type}_{mode}"
                return self.config.splash_factors.get(key,
                                                     self.config.splash_factors["default"])
            # 兼容攻城坦克
            if unit_type == "SiegeTankSieged":
                unit_type = "SiegeTank"
            return self.config.splash_factors.get(unit_type,
                                                 self.config.splash_factors["default"])
        return 1.0
        
    def _get_mastery_attack_speed(self, commander: CommanderData) -> float:
        """获取精通攻速加成"""
        # 这里简化处理，实际应该根据精通配置计算
        mastery_cfg = self.config.mastery_config.get(commander.id, {})
        return mastery_cfg.get("attack_speed", 0.0)


# 测试代码
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 加载数据
    loader = YAMLDataLoader()
    loader.load_all()
    
    # 创建计算器
    calculator = CEVCalculatorV24(loader)
    
    # 测试计算掠袭解放者
    try:
        # AA模式
        result_aa = calculator.calculate_cev("Liberator_BlackOps", "AA", apply_mastery=True)
        print(f"\n掠袭解放者 (AA模式):")
        print(f"CEV: {result_aa['cev']}")
        print(f"CEV_per_pop: {result_aa['cev_per_pop']}")
        print(f"详细参数: {result_aa['components']}")
        
        # AG模式
        result_ag = calculator.calculate_cev("Liberator_BlackOps", "AG", apply_mastery=True)
        print(f"\n掠袭解放者 (AG模式):")
        print(f"CEV: {result_ag['cev']}")
        print(f"CEV_per_pop: {result_ag['cev_per_pop']}")
        print(f"详细参数: {result_ag['components']}")
        
    except Exception as e:
        print(f"计算错误: {e}") 