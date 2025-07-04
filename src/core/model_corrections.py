"""
模型修正：确保实现与论文设计一致
"""

class ModelCorrections:
    """模型参数修正"""
    
    # 论文中的标准参数
    STANDARD_PARAMS = {
        # 有效成本参数
        'mineral_gas_ratio': 2.5,      # α：矿气转换率
        'supply_base_value': 20,        # ρ：人口基准价值（论文中是20，不是25）
        
        # 人口压力因子
        'lambda_max_200': 1.0,          # 200人口指挥官的λ_max
        'lambda_max_100_base': 2.0,     # 100人口指挥官的基础λ_max
        
        # 护甲减伤公式参数
        'armor_constant': 10,           # 护甲公式中的常数
        
        # 标准速度
        'standard_speed': 2.95,         # v_ref：标准移动速度
        
        # 协同效应参数
        'synergy_params': {
            'herc_tank_mobility': 2.0,      # 大力神-坦克机动性提升
            'herc_tank_position': 0.5,      # 大力神-坦克位置优势
            'queen_muta_damage': 0.75,      # 女王-飞龙伤害加成
        }
    }
    
    @staticmethod
    def calculate_effective_cost(unit, lambda_value):
        """
        根据论文公式计算有效成本
        C_eff = C_m + α × C_g + λ(t) × S × ρ
        """
        params = ModelCorrections.STANDARD_PARAMS
        
        # 支持字典和对象两种格式
        if isinstance(unit, dict):
            mineral_cost = unit.get('mineral_cost', 0)
            gas_cost = unit.get('gas_cost', 0)
            supply_cost = unit.get('supply_cost', 0)
        else:
            mineral_cost = unit.mineral_cost
            gas_cost = unit.gas_cost
            supply_cost = unit.supply_cost
        
        resource_cost = (
            mineral_cost + 
            gas_cost * params['mineral_gas_ratio']
        )
        
        supply_pressure = (
            supply_cost * 
            params['supply_base_value'] *  # 使用20而不是25
            lambda_value
        )
        
        return resource_cost + supply_pressure
    
    @staticmethod
    def calculate_lambda_max(commander_config, free_unit_ratio=0.0):
        """
        根据论文计算λ_max
        - 200人口：λ_max = 1.0
        - 100人口：λ_max = 2.0 - ρ_free
        """
        params = ModelCorrections.STANDARD_PARAMS
        
        if commander_config.population_cap == 200:
            return params['lambda_max_200']
        elif commander_config.population_cap == 100:
            # 考虑免费单位占比
            return params['lambda_max_100_base'] - free_unit_ratio
        else:
            # 其他人口上限，线性插值
            ratio = commander_config.population_cap / 200.0
            return 2.0 - ratio
    
    @staticmethod
    def calculate_special_combo_bonus(unit1, unit2, combo_type):
        """
        计算特殊组合效应
        """
        params = ModelCorrections.STANDARD_PARAMS['synergy_params']
        
        if combo_type == "herc_tank":
            # 大力神-攻城坦克组合
            mobility_bonus = params['herc_tank_mobility']
            position_bonus = params['herc_tank_position']
            return (1 + mobility_bonus) * (1 + position_bonus)
            
        elif combo_type == "queen_muta":
            # 女王-飞龙注能组合
            damage_bonus = params['queen_muta_damage']
            return 1 + damage_bonus
            
        else:
            return 1.0
    
    @staticmethod
    def validate_cev_calculation(cev_result):
        """
        验证CEV计算是否符合论文要求
        """
        issues = []
        
        # 检查必要字段
        required_fields = [
            'cev', 'effective_cost', 'effective_hp', 
            'effective_dps', 'lambda', 'synergy_bonus'
        ]
        
        for field in required_fields:
            if field not in cev_result:
                issues.append(f"缺少必要字段: {field}")
        
        # 检查数值合理性
        if cev_result.get('lambda', 0) > 2.0:
            issues.append("λ值超过理论最大值2.0")
            
        if cev_result.get('synergy_bonus', 1.0) < 1.0:
            issues.append("协同加成不应小于1.0")
        
        return issues


# 修正后的五大精英单位数据
CORRECTED_ELITE_UNITS = {
    'Dragoon': {
        'chinese_name': '龙骑士',
        'commander': '阿塔尼斯',
        'effective_hp': 210,      # 考虑护盾回充
        'base_dps': 13.3,         # 对地基础DPS
        'vs_armored_dps': 26.6,   # 对重甲DPS（翻倍）
        'mineral_cost': 125,
        'gas_cost': 50,
        'supply_cost': 2,
        'ability_value': 0,       # 无特殊能力
        'synergy': 1.265          # 标准协同系数
    },
    'Wrathwalker': {
        'chinese_name': '天罚行者',
        'commander': '阿拉纳克',
        'effective_hp': 390,      # 基础HP，不含护盾回充
        'base_dps': 53.33,        # 高基础DPS
        'mineral_cost': 250,
        'gas_cost': 150,
        'supply_cost': 4,
        'ability_value': 12,      # 相位模式价值
        'synergy': 1.265
    },
    'SiegeTank_Swann': {
        'chinese_name': '攻城坦克',
        'commander': '斯旺',
        'effective_hp': 211.2,    # 考虑护甲
        'tank_mode_dps': 23.3,    # 坦克模式
        'siege_mode_dps': 46.7,   # 攻城模式基础
        'vs_armored_siege': 93.3, # 攻城模式对重甲
        'mineral_cost': 150,
        'gas_cost': 125,
        'supply_cost': 3,
        'ability_value': 10,      # 模式切换价值
        'synergy': 1.265
    },
    'Impaler': {
        'chinese_name': '穿刺者',
        'commander': '德哈卡',
        'effective_hp': 220,      # 潜地时更高
        'base_dps': 26.7,         # 对地DPS
        'vs_armored_dps': 40,     # 对重甲
        'mineral_cost': 100,
        'gas_cost': 100,
        'supply_cost': 2,
        'ability_value': 10,      # 潜地价值
        'synergy': 1.265
    },
    'RaidLiberator': {
        'chinese_name': '掠袭解放者',
        'commander': '诺娃',
        'effective_hp': 450,      # 高生命值
        'ag_mode_dps': 103.3,     # AG模式超高DPS
        'aa_mode_dps': 20,        # AA模式
        'mineral_cost': 150,
        'gas_cost': 150,
        'supply_cost': 3,
        'ability_value': 10,      # 模式切换
        'synergy': 1.265
    }
}