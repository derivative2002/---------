"""
增强的CEV计算器
支持新的数据格式和高级战斗效果
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

from ..data.models import Unit, Weapon, Ability, UnitMode, CommanderConfig
from ..data.advanced_data_loader import AdvancedDataLoader


class EnhancedCEVCalculator:
    """增强的战斗效能值计算器"""
    
    def __init__(self, data_dir: str = "data/units"):
        self.logger = logging.getLogger(__name__)
        self.loader = AdvancedDataLoader(data_dir)
        self.database = self.loader.load_all_data()
        
        # 时间衰减参数
        self.lambda_params = {
            'alpha': 0.00125,  # 衰减速率
            'beta': 300,       # 中值时间（秒）
        }
        
        # 协同效应参数
        self.synergy_params = {
            'support_bonus': 0.05,      # 每个支援单位的加成
            'ally_bonus': 0.01,         # 每个盟友单位的加成
            'max_support_bonus': 0.5,   # 最大支援加成
            'max_ally_bonus': 0.3,      # 最大盟友加成
        }
        
    def calculate_lambda(self, time_seconds: float) -> float:
        """计算时间依赖的人口压力因子"""
        alpha = self.lambda_params['alpha']
        beta = self.lambda_params['beta']
        return 1 / (1 + np.exp(-alpha * (time_seconds - beta)))
    
    def calculate_effective_cost(self, unit: Unit, lambda_value: float) -> float:
        """计算有效成本 - 已根据论文公式(2)修正"""
        # 基础资源成本，应用矿气转换率 alpha = 2.5
        resource_cost = unit.mineral_cost + 2.5 * unit.gas_cost
        
        # 考虑人口压力，人口基准价值 rho = 20
        supply_pressure = unit.supply_cost * 20 * lambda_value
        
        return resource_cost + supply_pressure
    
    def calculate_effective_hp(self, unit: Unit, commander_config: Optional[CommanderConfig] = None) -> float:
        """计算有效生命值 - 已根据论文公式(3)修正"""
        # 护甲减伤效果
        if unit.armor > 0:
            # 移除简化的0.5系数
            damage_reduction = unit.armor / (unit.armor + 10)
            hp_armor_factor = 1 / (1 - damage_reduction)
        else:
            hp_armor_factor = 1.0

        effective_hp_part = unit.hp * hp_armor_factor

        # 护盾部分 - 引入护盾回复率
        # 假设战斗持续10秒，计算这段时间的等效回复量
        # TODO: 将shield_regen_rate添加到Unit模型中
        shield_regen_rate = getattr(unit, 'shield_regen_rate', 0)
        # 为星灵单位设置默认回复率 (如果数据中没有)
        if unit.shields > 0 and shield_regen_rate == 0:
            if any(attr in unit.attributes for attr in ["灵能", "机械"]): # 简单判断是否为星灵单位
                 shield_regen_rate = 2.0 # 默认值

        # 简化模型：将10秒战斗内的回复量等效为额外护盾
        effective_shield_part = unit.shields + shield_regen_rate * 10
        
        # 总有效生命值
        effective_hp = effective_hp_part + effective_shield_part

        # 应用指挥官修正
        if commander_config and 'hp' in commander_config.modifiers:
            effective_hp *= commander_config.modifiers['hp']
            
        return effective_hp
    
    def calculate_effective_dps(self, 
                               unit: Unit, 
                               target_attributes: List[str] = None,
                               mode: Optional[UnitMode] = None,
                               commander_config: Optional[CommanderConfig] = None) -> float:
        """计算有效DPS"""
        if not unit.weapons:
            return 0
        
        # 获取当前模式下的武器
        if mode:
            # 根据模式配置选择武器
            active_weapons = [w for w in unit.weapons if mode.weapon_config in w.weapon_name]
            if not active_weapons:
                active_weapons = unit.weapons
        else:
            active_weapons = unit.weapons
        
        # 计算总DPS
        total_dps = 0
        for weapon in active_weapons:
            # 基础DPS
            base_dps = weapon.dps
            
            # 属性克制加成
            if target_attributes:
                bonus_multiplier = 1.0
                for attr in target_attributes:
                    if attr in weapon.bonus_damage:
                        bonus_multiplier += weapon.bonus_damage[attr] / weapon.base_damage
                base_dps *= bonus_multiplier
            
            # 溅射效果加成（简化计算）
            if weapon.splash_type.value != "none" and weapon.splash_params:
                splash_bonus = 1.2  # 假设平均溅射效果为20%额外伤害
                base_dps *= splash_bonus
            
            total_dps += base_dps
        
        # 应用指挥官修正
        if commander_config and 'damage' in commander_config.modifiers:
            total_dps *= commander_config.modifiers['damage']
        
        # 应用模式修正
        if mode and 'damage' in mode.stat_modifiers:
            total_dps *= (1 + mode.stat_modifiers['damage'])
            
        return total_dps
    
    def calculate_special_abilities_value(self, unit: Unit) -> float:
        """计算特殊能力的价值"""
        ability_value = 0
        
        for ability in unit.abilities:
            # 主动技能价值
            if ability.type.value == "active":
                # 伤害技能
                if ability.effect.damage > 0:
                    # 假设每10秒使用一次
                    cooldown = ability.cost.cooldown if ability.cost.cooldown > 0 else 10
                    ability_value += ability.effect.damage / cooldown
                
                # 治疗技能
                if ability.effect.heal > 0:
                    ability_value += ability.effect.heal / cooldown * 0.5  # 治疗价值降权
            
            # 被动技能价值
            elif ability.type.value == "passive":
                # 增益效果
                for stat, value in ability.effect.buff.items():
                    if stat == "attack_speed":
                        ability_value += 10 * value  # 攻速加成价值
                    elif stat == "movement_speed":
                        ability_value += 5 * value   # 移速加成价值
                    elif stat == "damage_reduction":
                        ability_value += value * 0.1  # 减伤价值
            
            # 切换技能（模式切换）
            elif ability.type.value == "toggle":
                ability_value += 10  # 固定价值
        
        return ability_value
    
    def calculate_synergy_bonus(self, 
                               unit: Unit,
                               n_support: int = 0,
                               n_ally: int = 0,
                               army_composition: List[str] = None) -> float:
        """计算协同效应加成"""
        synergy_multiplier = 1.0
        
        # 支援单位加成
        support_bonus = min(
            n_support * self.synergy_params['support_bonus'],
            self.synergy_params['max_support_bonus']
        )
        synergy_multiplier *= (1 + support_bonus)
        
        # 盟友单位加成
        ally_bonus = min(
            n_ally * self.synergy_params['ally_bonus'],
            self.synergy_params['max_ally_bonus']
        )
        synergy_multiplier *= (1 + ally_bonus)
        
        # TODO: 实现基于army_composition的特定组合加成
        
        return synergy_multiplier
    
    def calculate_cev(self,
                     unit: Unit,
                     time_seconds: float = 600,
                     target_attributes: List[str] = None,
                     mode_name: Optional[str] = None,
                     n_support: int = 0,
                     n_ally: int = 0,
                     army_composition: List[str] = None) -> Dict[str, float]:
        """
        计算单位的战斗效能值
        
        参数:
            unit: 单位对象
            time_seconds: 游戏时间（秒）
            target_attributes: 目标属性列表
            mode_name: 单位模式名称
            n_support: 支援单位数量
            n_ally: 盟友单位数量
            army_composition: 军队组成
        """
        # 获取指挥官配置
        commander_config = self.database.commanders.get(unit.commander)
        
        # 获取单位模式
        mode = None
        if mode_name:
            mode = unit.get_mode(mode_name)
        
        # 计算λ值
        base_lambda = self.calculate_lambda(time_seconds)
        
        # 根据指挥官人口上限应用lambda_max
        lambda_max = 1.0
        # 论文中定义，100人口指挥官的基础lambda_max为2.0
        # 暂不实现更复杂的rho_free（免费单位占比）扣减
        if commander_config and commander_config.population_cap == 100:
            lambda_max = 2.0
        
        lambda_value = base_lambda * lambda_max
        
        # 计算有效成本
        effective_cost = self.calculate_effective_cost(unit, lambda_value)
        
        # 计算有效HP
        effective_hp = self.calculate_effective_hp(unit, commander_config)
        
        # 计算有效DPS
        effective_dps = self.calculate_effective_dps(
            unit, target_attributes, mode, commander_config
        )
        
        # 计算特殊能力价值
        ability_value = self.calculate_special_abilities_value(unit)
        
        # 将能力价值加入DPS
        total_dps = effective_dps + ability_value
        
        # 计算协同效应
        synergy_bonus = self.calculate_synergy_bonus(
            unit, n_support, n_ally, army_composition
        )
        
        # 计算最终CEV
        if effective_cost > 0:
            cev = (total_dps * effective_hp * synergy_bonus) / effective_cost
        else:
            cev = float('inf')  # 免费单位
        
        # 额外指标
        results = {
            'cev': cev,
            'effective_cost': effective_cost,
            'effective_hp': effective_hp,
            'effective_dps': total_dps,
            'base_dps': effective_dps,
            'ability_value': ability_value,
            'lambda': lambda_value,
            'synergy_bonus': synergy_bonus,
            
            # 效率指标
            'resource_efficiency': total_dps / effective_cost if effective_cost > 0 else float('inf'),
            'supply_efficiency': total_dps / unit.supply_cost if unit.supply_cost > 0 else float('inf'),
            'survivability': effective_hp / effective_cost if effective_cost > 0 else float('inf'),
            
            # 战术指标
            'range_score': self._calculate_range_score(unit),
            'mobility_score': unit.movement_speed / 3.0,  # 标准化
            'versatility_score': self._calculate_versatility_score(unit)
        }
        
        return results
    
    def _calculate_range_score(self, unit: Unit) -> float:
        """计算射程分数"""
        if not unit.weapons:
            return 0
        
        max_range = max(w.range for w in unit.weapons)
        
        # 考虑碰撞半径的影响
        if unit.collision_radius:
            effective_range = max_range - unit.collision_radius
        else:
            effective_range = max_range
        
        # 标准化（假设最大有效射程为15）
        return min(effective_range / 15.0, 1.0)
    
    def _calculate_versatility_score(self, unit: Unit) -> float:
        """计算多功能性分数"""
        score = 0
        
        # 对空对地能力
        can_attack_ground = any(w.weapon_type.value in ["ground", "both"] for w in unit.weapons)
        can_attack_air = any(w.weapon_type.value in ["air", "both"] for w in unit.weapons)
        
        if can_attack_ground and can_attack_air:
            score += 0.3
        elif can_attack_ground or can_attack_air:
            score += 0.1
        
        # 特殊能力
        score += min(len(unit.abilities) * 0.1, 0.3)
        
        # 模式切换
        if unit.modes:
            score += 0.2
        
        # 飞行单位额外加分
        if unit.is_flying:
            score += 0.2
        
        return score
    
    def calculate_unit_matchup(self, 
                              attacker: Unit,
                              defender: Unit,
                              time_seconds: float = 600) -> Dict[str, float]:
        """计算单位对战效果"""
        # 获取防御方属性
        defender_attributes = defender.attributes
        
        # 计算攻击方对防御方的CEV
        attacker_cev = self.calculate_cev(
            attacker,
            time_seconds=time_seconds,
            target_attributes=defender_attributes
        )
        
        # 计算防御方对攻击方的CEV
        defender_cev = self.calculate_cev(
            defender,
            time_seconds=time_seconds,
            target_attributes=attacker.attributes
        )
        
        # 计算优势比
        if defender_cev['cev'] > 0:
            advantage_ratio = attacker_cev['cev'] / defender_cev['cev']
        else:
            advantage_ratio = float('inf')
        
        return {
            'attacker_cev': attacker_cev['cev'],
            'defender_cev': defender_cev['cev'],
            'advantage_ratio': advantage_ratio,
            'attacker_dps_vs_defender': attacker_cev['effective_dps'],
            'defender_dps_vs_attacker': defender_cev['effective_dps']
        }


# 使用示例
if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建计算器
    calculator = EnhancedCEVCalculator()
    
    # 测试单位CEV计算
    print("=== 测试增强CEV计算器 ===\n")
    
    # 获取攻城坦克
    siege_tank = calculator.database.get_unit("吉姆·雷诺", "SiegeTank")
    if siege_tank:
        print(f"1. {siege_tank.chinese_name} CEV计算:")
        
        # 坦克模式
        tank_mode_cev = calculator.calculate_cev(siege_tank, mode_name="坦克模式")
        print(f"   坦克模式 CEV: {tank_mode_cev['cev']:.2f}")
        print(f"   - DPS: {tank_mode_cev['effective_dps']:.1f}")
        print(f"   - HP: {tank_mode_cev['effective_hp']:.0f}")
        
        # 攻城模式
        siege_mode_cev = calculator.calculate_cev(
            siege_tank, 
            mode_name="攻城模式",
            target_attributes=["重甲"]
        )
        print(f"   攻城模式 CEV (vs 重甲): {siege_mode_cev['cev']:.2f}")
        print(f"   - DPS: {siege_mode_cev['effective_dps']:.1f}")
        
    # 测试对战计算
    marine = calculator.database.get_unit("吉姆·雷诺", "Marine")
    stalker = calculator.database.get_unit("阿塔尼斯", "Stalker")
    
    if marine and stalker:
        print(f"\n2. 对战测试: {marine.chinese_name} vs {stalker.chinese_name}")
        matchup = calculator.calculate_unit_matchup(marine, stalker)
        print(f"   - 陆战队员 CEV: {matchup['attacker_cev']:.2f}")
        print(f"   - 追猎者 CEV: {matchup['defender_cev']:.2f}")
        print(f"   - 优势比: {matchup['advantage_ratio']:.2f}")