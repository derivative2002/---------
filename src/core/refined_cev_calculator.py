"""
精细化CEV计算器
基于实战经验调整的模型参数
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple
import json
from pathlib import Path


class RefinedCEVCalculator:
    """精细化的战斗效能值(CEV)计算器"""
    
    def __init__(self):
        """初始化计算器参数"""
        # 基础参数
        self.alpha = 2.5  # 矿气转换率（默认）
        self.rho = 25     # 人口基准价值
        self.lambda_mid = 0.593  # 中期游戏因子
        
        # 指挥官特性
        self.commander_traits = {
            '吉姆·雷诺': {'gas_value': 2.5, 'production': 1.0},
            '凯瑞甘': {'gas_value': 2.5, 'production': 1.0},
            '阿塔尼斯': {'gas_value': 2.5, 'production': 1.1},
            '斯旺': {'gas_value': 2.5, 'production': 1.8},  # 气矿骡
            '扎加拉': {'gas_value': 2.5, 'production': 1.3},
            '沃拉尊': {'gas_value': 2.5, 'production': 1.0},
            '凯拉克斯': {'gas_value': 2.5, 'production': 0.9},
            '阿巴瑟': {'gas_value': 2.5, 'production': 1.0},
            '阿拉纳克': {'gas_value': 2.5, 'production': 1.0},
            '阿拉纳克P1': {'gas_value': 2.5, 'production': 0.8},  # 需要死徒
            '诺娃': {'gas_value': 1.0, 'production': 1.2},  # 矿气1:1，批量部署
            '斯托科夫': {'gas_value': 2.5, 'production': 1.2},
            '菲尼克斯': {'gas_value': 2.5, 'production': 1.0},
            '德哈卡': {'gas_value': 2.5, 'production': 1.3},  # 快速孵化
            '霍纳与汉': {'gas_value': 2.5, 'production': 1.0},
            '泰凯斯': {'gas_value': 2.5, 'production': 0.7},
            '泽拉图': {'gas_value': 2.5, 'production': 0.8},
            '斯台特曼': {'gas_value': 2.5, 'production': 1.1},
            '蒙斯克': {'gas_value': 2.5, 'production': 1.0}
        }
        
        # 操作难度系数
        self.operation_factors = {
            'default': 1.0,
            'move_attack': 1.1,      # 可移动射击加成
            'simple_siege': 0.9,     # 简单架设（坦克、穿刺者）
            'complex_siege': 0.7,    # 复杂架设（解放者）
            'auto_cast': 1.05        # 自动施法单位
        }
        
        # AOE系数
        self.aoe_factors = {
            'SiegeTank_Swann': 1.4,  # 考虑碰撞体积的实际AOE
            'SiegeTank_Raynor': 1.4,
            'Ultralisk': 1.3,
            'Colossus': 1.5,
            'default': 1.0
        }
        
        # 过量击杀阈值
        self.overkill_thresholds = {
            'low': (50, 1.0),      # 50以下伤害无惩罚
            'medium': (100, 0.9),  # 100伤害轻微惩罚
            'high': (150, 0.85),   # 150伤害中等惩罚
            'extreme': (200, 0.8)  # 200+伤害严重惩罚
        }
        
        # 协同需求系数
        self.synergy_requirements = {
            'independent': 1.1,    # 独立作战能力强
            'normal': 1.0,         # 正常
            'dependent': 0.8       # 高度依赖协同
        }
    
    def calculate_effective_cost(self, unit_data: Dict, commander: str) -> float:
        """计算单位的有效成本"""
        traits = self.commander_traits.get(commander, {'gas_value': 2.5, 'production': 1.0})
        
        mineral = unit_data.get('mineral_cost', 0)
        gas = unit_data.get('gas_cost', 0)
        supply = unit_data.get('supply_cost', 0)
        
        # 资源成本（考虑指挥官特性）
        resource_cost = mineral + traits['gas_value'] * gas
        
        # 人口压力
        population_pressure = supply * self.rho * self.lambda_mid
        
        return resource_cost + population_pressure
    
    def calculate_effective_hp(self, unit_data: Dict, masteries: Dict = None) -> float:
        """计算单位的有效生命值"""
        hp = unit_data.get('hp', 0)
        shields = unit_data.get('shields', 0)
        armor = unit_data.get('armor', 0)
        
        # 精通加成
        if masteries:
            if 'mech_hp' in masteries and '机械' in unit_data.get('attributes', ''):
                hp *= (1 + masteries['mech_hp'])
            elif 'bio_hp' in masteries and '生物' in unit_data.get('attributes', ''):
                hp *= (1 + masteries['bio_hp'])
            elif 'primal_hp' in masteries and '生物' in unit_data.get('attributes', ''):
                hp *= (1 + masteries['primal_hp'])
        
        # 护甲修正
        armor_factor = 1 + armor / 10
        effective_hp = hp * armor_factor + shields
        
        # 护盾回充（20秒战斗）
        if shields > 0:
            shield_regen = 2 * 20
            effective_hp += shield_regen
        
        # 特殊单位加成
        unit_id = unit_data.get('english_id', '')
        if unit_id == 'RaidLiberator' and '诺娃' in unit_data.get('commander', ''):
            effective_hp *= 1.3  # 诺娃的无人机支援
        elif unit_id == 'SiegeTank_Swann':
            effective_hp += 20  # 再生型生物钢
        
        return effective_hp
    
    def calculate_range_factor(self, weapon_range: float, collision_radius: float) -> float:
        """计算射程系数（使用平方根公式）"""
        return np.sqrt(weapon_range / collision_radius)
    
    def calculate_collision_factor(self, collision_radius: float) -> float:
        """计算碰撞体积系数"""
        return 1 / (1 + collision_radius * 0.2)
    
    def get_operation_factor(self, unit_data: Dict) -> float:
        """获取操作难度系数"""
        unit_id = unit_data.get('english_id', '')
        
        # 特定单位的操作难度
        if unit_id in ['RaidLiberator', 'Liberator']:
            return self.operation_factors['complex_siege']
        elif unit_id in ['SiegeTank_Swann', 'SiegeTank_Raynor', 'Impaler']:
            return self.operation_factors['simple_siege']
        elif unit_data.get('can_move_attack', False):
            return self.operation_factors['move_attack']
        
        return self.operation_factors['default']
    
    def get_aoe_factor(self, unit_id: str) -> float:
        """获取AOE系数"""
        return self.aoe_factors.get(unit_id, self.aoe_factors['default'])
    
    def get_overkill_factor(self, damage: float, target_avg_hp: float = 100) -> float:
        """计算过量击杀系数"""
        if damage <= target_avg_hp * 0.5:
            return 1.0  # 伤害过低，无惩罚
        
        for threshold, factor in sorted(self.overkill_thresholds.values(), reverse=True):
            if damage >= threshold:
                return factor
        
        return 1.0
    
    def get_synergy_factor(self, unit_data: Dict) -> float:
        """获取协同需求系数"""
        unit_id = unit_data.get('english_id', '')
        
        # 独立作战能力强的单位
        if unit_id in ['SiegeTank_Swann', 'Impaler', 'Ultralisk']:
            return self.synergy_requirements['independent']
        # 高度依赖协同的单位
        elif unit_id in ['Wrathwalker', 'RaidLiberator', 'Marine']:
            return self.synergy_requirements['dependent']
        
        return self.synergy_requirements['normal']
    
    def calculate_dps(self, weapon_data: Dict, vs_attribute: Optional[str] = None) -> float:
        """计算DPS"""
        base_damage = weapon_data.get('base_damage', 0)
        attack_count = weapon_data.get('attack_count', 1)
        attack_interval = weapon_data.get('attack_interval', 1.0)
        
        # 基础DPS
        damage_per_attack = base_damage * attack_count
        
        # 属性克制加成
        if vs_attribute and weapon_data.get('bonus_damage'):
            try:
                bonus_dict = json.loads(weapon_data['bonus_damage'])
                if vs_attribute in bonus_dict:
                    damage_per_attack += bonus_dict[vs_attribute] * attack_count
            except:
                pass
        
        return damage_per_attack / attack_interval
    
    def calculate_cev(self, unit_data: Dict, weapon_data: Dict, 
                     commander: str, scenario: Dict = None) -> Dict:
        """计算完整的CEV"""
        # 默认场景
        if scenario is None:
            scenario = {
                'target_avg_hp': 100,
                'target_count': 5,
                'vs_attribute': None
            }
        
        # 获取指挥官特性
        traits = self.commander_traits.get(commander, {'gas_value': 2.5, 'production': 1.0})
        
        # 成本计算
        effective_cost = self.calculate_effective_cost(unit_data, commander)
        
        # HP计算
        effective_hp = self.calculate_effective_hp(unit_data)
        
        # DPS计算
        base_dps = self.calculate_dps(weapon_data, scenario.get('vs_attribute'))
        
        # AOE修正
        unit_id = unit_data.get('english_id', '')
        aoe_factor = self.get_aoe_factor(unit_id)
        
        # 如果是AOE单位且目标数量多，增加有效DPS
        if aoe_factor > 1 and scenario['target_count'] > 1:
            # 实际AOE效果取决于目标数量，但有上限
            actual_aoe = min(aoe_factor, 1 + (scenario['target_count'] - 1) * 0.2)
            effective_dps = base_dps * actual_aoe
        else:
            effective_dps = base_dps
        
        # 过量击杀修正
        damage_per_shot = weapon_data.get('base_damage', 0)
        overkill_factor = self.get_overkill_factor(damage_per_shot, scenario['target_avg_hp'])
        effective_dps *= overkill_factor
        
        # 射程系数
        weapon_range = weapon_data.get('range', 6)
        collision_radius = unit_data.get('collision_radius', 0.75)
        range_factor = self.calculate_range_factor(weapon_range, collision_radius)
        
        # 碰撞体积系数
        collision_factor = self.calculate_collision_factor(collision_radius)
        
        # 操作系数
        operation_factor = self.get_operation_factor(unit_data)
        
        # 协同系数
        synergy_factor = self.get_synergy_factor(unit_data)
        
        # 生产系数
        production_factor = traits['production']
        
        # 最终CEV计算
        cev = (effective_dps * effective_hp * range_factor * collision_factor * 
               operation_factor * synergy_factor * production_factor) / effective_cost
        
        return {
            'cev': cev,
            'effective_cost': effective_cost,
            'effective_hp': effective_hp,
            'base_dps': base_dps,
            'effective_dps': effective_dps,
            'factors': {
                'range': range_factor,
                'collision': collision_factor,
                'operation': operation_factor,
                'synergy': synergy_factor,
                'production': production_factor,
                'aoe': aoe_factor,
                'overkill': overkill_factor
            }
        }


# 预定义的战斗场景
COMBAT_SCENARIOS = {
    'vs_elite': {
        'name': '对精英单位',
        'target_avg_hp': 200,
        'target_count': 3,
        'description': '少量高血量目标'
    },
    'vs_swarm': {
        'name': '对虫群',
        'target_avg_hp': 50,
        'target_count': 20,
        'description': '大量低血量目标'
    },
    'vs_mixed': {
        'name': '对混合部队',
        'target_avg_hp': 100,
        'target_count': 8,
        'description': '中等数量中等血量'
    },
    'vs_armored': {
        'name': '对重甲',
        'target_avg_hp': 150,
        'target_count': 5,
        'vs_attribute': '重甲',
        'description': '重甲单位'
    }
}