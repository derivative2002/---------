"""
六大精英单位最终评估
严格按照论文模型公式计算
包含所有修正因子
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

class FinalSixUnitsEvaluation:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / 'data' / 'units'
        self.units_df = pd.read_csv(self.data_dir / 'units_master.csv')
        self.weapons_df = pd.read_csv(self.data_dir / 'weapons.csv')
        
        # 六大精英单位
        self.elite_units = {
            'Dragoon': {
                'name': '龙骑士',
                'commander': '阿塔尼斯',
                'weapon_config': 'base',
                'can_move_attack': False,  # 不能移动射击
                'siege_mode': False,
                'technologies': {}
            },
            'Wrathwalker': {
                'name': '天罚行者',
                'commander': '阿拉纳克',
                'weapon_config': 'sacrifice_mastery',  # 献祭+精通
                'can_move_attack': True,  # 可以移动射击
                'siege_mode': False,
                'technologies': {
                    'sacrifice': True,
                    'havoc_synergy': True  # +1射程
                }
            },
            'Wrathwalker_SoulArtificer': {
                'name': '灵魂巧匠天罚行者',
                'commander': '阿拉纳克P1',
                'weapon_config': 'soul_sacrifice_mastery',
                'can_move_attack': True,
                'siege_mode': False,
                'technologies': {
                    'sacrifice': True,
                    'havoc_synergy': True,
                    'soul_stacks': 10  # 10层灵魂
                }
            },
            'SiegeTank_Swann': {
                'name': '攻城坦克',
                'commander': '斯旺',
                'weapon_config': 'siege_mode',
                'can_move_attack': False,
                'siege_mode': True,  # 需要架设
                'technologies': {
                    'maelstrom_rounds': True,  # 钨钢钉
                    'regenerative_bio_steel': 1.0  # 每秒1点生命回复
                }
            },
            'Impaler': {
                'name': '穿刺者',
                'commander': '德哈卡',
                'weapon_config': 'base',
                'can_move_attack': False,
                'siege_mode': True,  # 需要潜地
                'technologies': {}
            },
            'RaidLiberator_AS15': {
                'name': '掠袭解放者',
                'commander': '诺娃',
                'weapon_config': 'defender_mode',
                'can_move_attack': False,
                'siege_mode': True,  # 需要架设
                'technologies': {}
            }
        }
        
        # 模型参数（来自论文）
        self.alpha = 2.5  # 矿气转换率
        self.rho = 25     # 人口基准价值（论文中为25，不是20）
        self.lambda_mid = 0.593  # 中期游戏人口压力因子
        self.r_ref = 6    # 基准射程
        self.v_ref = 2.95 # 标准移动速度
        
        # 精通配置
        self.masteries = {
            'Dragoon': {},
            'Wrathwalker': {'attack_speed': 0.15},
            'Wrathwalker_SoulArtificer': {'attack_speed': 0.15},
            'SiegeTank_Swann': {'mech_hp': 0.30},
            'Impaler': {'primal_hp': 0.30},
            'RaidLiberator_AS15': {}  # 已包含在单位ID中
        }
    
    def calculate_effective_cost(self, unit_row, unit_config):
        """计算有效成本 C_eff = C_m + α×C_g + λ(t)×S×ρ"""
        mineral_cost = unit_row['mineral_cost']
        gas_cost = unit_row['gas_cost']
        supply_cost = unit_row['supply_cost']
        
        # 资源成本
        resource_cost = mineral_cost + self.alpha * gas_cost
        
        # 人口压力
        commander = unit_config['commander']
        if commander in ['诺娃', '阿拉纳克P1']:
            lambda_max = 2.0  # 100人口指挥官
        else:
            lambda_max = 1.0  # 200人口指挥官
        
        lambda_value = self.lambda_mid * lambda_max
        supply_pressure = supply_cost * self.rho * lambda_value
        
        return resource_cost + supply_pressure
    
    def calculate_effective_hp(self, unit_row, unit_config):
        """计算有效生命值 EHP = HP × (1 + armor/10) + shields"""
        hp = unit_row['hp']
        shields = unit_row['shields']
        armor = unit_row['armor']
        
        # 精通加成
        unit_id = unit_row['english_id']
        if unit_id in self.masteries:
            if 'mech_hp' in self.masteries[unit_id] and '机械' in unit_row['attributes']:
                hp *= (1 + self.masteries[unit_id]['mech_hp'])
            elif 'primal_hp' in self.masteries[unit_id] and '生物' in unit_row['attributes']:
                hp *= (1 + self.masteries[unit_id]['primal_hp'])
        
        # 护甲修正
        armor_factor = 1 + armor / 10
        effective_hp = hp * armor_factor + shields
        
        # 护盾回充（20秒战斗）
        if shields > 0:
            shield_regen = 2 * 20
            effective_hp += shield_regen
        
        # 斯旺再生型生物钢
        if unit_config.get('technologies', {}).get('regenerative_bio_steel'):
            regen_value = unit_config['technologies']['regenerative_bio_steel'] * 20
            effective_hp += regen_value
        
        return effective_hp
    
    def calculate_range_factor(self, weapon_range, collision_radius):
        """计算射程系数 F_range = log2(1 + R/r)"""
        return np.log2(1 + weapon_range / collision_radius)
    
    def calculate_collision_factor(self, collision_radius):
        """计算碰撞体积生存系数 = 1 / (1 + radius × 0.2)"""
        return 1 / (1 + collision_radius * 0.2)
    
    def calculate_operational_factor(self, unit_config):
        """计算操作因子"""
        factor = 1.0
        
        # 架设/潜地惩罚
        if unit_config['siege_mode']:
            factor *= 0.9
        
        # 移动射击加成
        if unit_config['can_move_attack']:
            factor *= 1.1
        
        return factor
    
    def get_weapon_data(self, unit_id, unit_config):
        """获取武器数据"""
        # 根据配置选择武器
        if unit_id == 'Wrathwalker':
            if unit_config['weapon_config'] == 'sacrifice_mastery':
                weapon_id = 'Wrathwalker_Sacrifice_Mastery'
            else:
                weapon_id = 'Wrathwalker'
        elif unit_id == 'Wrathwalker_SoulArtificer':
            if unit_config['weapon_config'] == 'soul_sacrifice_mastery':
                weapon_id = 'Wrathwalker_SoulArtificer_Sacrifice_Mastery'
            else:
                weapon_id = 'Wrathwalker_SoulArtificer'
        elif unit_id == 'SiegeTank_Swann' and unit_config['weapon_config'] == 'siege_mode':
            # 攻城模式使用震荡炮
            weapon_rows = self.weapons_df[
                (self.weapons_df['unit_id'] == unit_id) & 
                (self.weapons_df['weapon_name'] == '震荡炮')
            ]
            if not weapon_rows.empty:
                return weapon_rows.iloc[0]
        else:
            weapon_id = unit_id
        
        # 获取对地武器
        weapon_rows = self.weapons_df[
            (self.weapons_df['unit_id'] == weapon_id) & 
            (self.weapons_df['weapon_type'].isin(['ground', 'both']))
        ]
        
        if not weapon_rows.empty:
            return weapon_rows.iloc[0]
        return None
    
    def calculate_dps(self, weapon_data, vs_attribute=None):
        """计算DPS"""
        if weapon_data is None:
            return 0
        
        base_damage = weapon_data['base_damage'] * weapon_data['attack_count']
        
        # 属性克制
        if vs_attribute and weapon_data['bonus_damage'] != '{}':
            try:
                bonus_dict = json.loads(weapon_data['bonus_damage'])
                if vs_attribute in bonus_dict:
                    base_damage += bonus_dict[vs_attribute] * weapon_data['attack_count']
            except:
                pass
        
        dps = base_damage / weapon_data['attack_interval']
        return dps
    
    def calculate_cev(self, unit_row, unit_config, vs_attribute=None):
        """计算最终CEV"""
        # 有效成本
        effective_cost = self.calculate_effective_cost(unit_row, unit_config)
        
        # 有效生命值
        effective_hp = self.calculate_effective_hp(unit_row, unit_config)
        
        # 获取武器数据
        weapon_data = self.get_weapon_data(unit_row['english_id'], unit_config)
        if weapon_data is None:
            return None
        
        # DPS计算
        dps = self.calculate_dps(weapon_data, vs_attribute)
        
        # 射程系数
        weapon_range = weapon_data['range']
        # 浩劫配合
        if unit_config.get('technologies', {}).get('havoc_synergy'):
            weapon_range += 1
        
        collision_radius = unit_row['collision_radius']
        range_factor = self.calculate_range_factor(weapon_range, collision_radius)
        
        # 碰撞体积系数
        collision_factor = self.calculate_collision_factor(collision_radius)
        
        # 操作因子
        operational_factor = self.calculate_operational_factor(unit_config)
        
        # 协同系数（简化为1.2）
        synergy_factor = 1.2
        
        # 最终CEV计算
        cev = (dps * effective_hp * range_factor * collision_factor * 
               operational_factor * synergy_factor) / effective_cost
        
        return {
            'unit_id': unit_row['english_id'],
            'name': unit_config['name'],
            'commander': unit_config['commander'],
            'effective_cost': effective_cost,
            'effective_hp': effective_hp,
            'dps': dps,
            'range': weapon_range,
            'range_factor': range_factor,
            'collision_factor': collision_factor,
            'operational_factor': operational_factor,
            'cev': cev
        }
    
    def run_evaluation(self):
        """运行完整评估"""
        results = []
        
        print("=== 六大精英单位最终CEV评估 ===\n")
        print("使用论文模型公式，包含所有修正因子\n")
        
        # 评估场景
        scenarios = [
            (None, '通用'),
            ('轻甲', '对轻甲'),
            ('重甲', '对重甲'),
            ('建筑', '对建筑')
        ]
        
        for vs_attribute, scenario_name in scenarios:
            print(f"\n--- {scenario_name}场景 ---")
            scenario_results = []
            
            for unit_id, unit_config in self.elite_units.items():
                unit_row = self.units_df[self.units_df['english_id'] == unit_id].iloc[0]
                cev_data = self.calculate_cev(unit_row, unit_config, vs_attribute)
                
                if cev_data:
                    scenario_results.append(cev_data)
                    print(f"{cev_data['name']}({cev_data['commander']}): CEV = {cev_data['cev']:.1f}")
                    if vs_attribute is None:  # 只在通用场景显示详细信息
                        print(f"  成本: {cev_data['effective_cost']:.0f}")
                        print(f"  有效HP: {cev_data['effective_hp']:.0f}")
                        print(f"  DPS: {cev_data['dps']:.1f}")
                        print(f"  射程: {cev_data['range']}")
                        print(f"  操作因子: {cev_data['operational_factor']}")
            
            # 排序
            scenario_results.sort(key=lambda x: x['cev'], reverse=True)
            
            print("\n排名：")
            for i, result in enumerate(scenario_results):
                print(f"{i+1}. {result['name']}: {result['cev']:.1f}")
                result['rank'] = i + 1
                result['scenario'] = scenario_name
                results.append(result.copy())
        
        return pd.DataFrame(results)
    
    def save_results(self, results_df):
        """保存结果"""
        output_dir = Path(__file__).parent.parent.parent / 'output' / 'final_evaluation'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存详细结果
        results_df.to_csv(output_dir / 'final_six_units_evaluation.csv', 
                         index=False, encoding='utf-8-sig')
        
        # 创建排名总结
        summary = results_df[results_df['scenario'] == '通用'].sort_values('cev', ascending=False)
        
        with open(output_dir / 'evaluation_summary.md', 'w', encoding='utf-8') as f:
            f.write("# 六大精英单位最终CEV评估报告\n\n")
            f.write("## 模型参数\n")
            f.write("- 矿气转换率 α = 2.5\n")
            f.write("- 人口基准价值 ρ = 25\n")
            f.write("- 中期游戏因子 λ(t) = 0.593\n")
            f.write("- 射程系数：F_range = log2(1 + R/r)\n")
            f.write("- 碰撞体积系数：1 / (1 + radius × 0.2)\n")
            f.write("- 架设惩罚：0.9\n")
            f.write("- 移动射击加成：1.1\n\n")
            
            f.write("## 综合CEV排名\n\n")
            for _, row in summary.iterrows():
                f.write(f"### {row['rank']}. {row['name']} ({row['commander']})\n")
                f.write(f"- CEV: {row['cev']:.1f}\n")
                f.write(f"- 有效成本: {row['effective_cost']:.0f}\n")
                f.write(f"- 有效HP: {row['effective_hp']:.0f}\n")
                f.write(f"- DPS: {row['dps']:.1f}\n")
                f.write(f"- 射程: {row['range']}\n")
                f.write(f"- 操作因子: {row['operational_factor']}\n\n")
        
        print(f"\n结果已保存至: {output_dir}")


def main():
    """主函数"""
    evaluator = FinalSixUnitsEvaluation()
    results_df = evaluator.run_evaluation()
    evaluator.save_results(results_df)


if __name__ == "__main__":
    main()