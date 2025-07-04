#!/usr/bin/env python3
"""
v2.3模型的CEV计算脚本
用于计算六大精英单位的准确CEV值
"""

import numpy as np

class V23CEVCalculator:
    """基于v2.3模型的CEV计算器"""
    
    def __init__(self):
        # 定义六大精英单位的基础参数
        self.units = {
            '灵魂巧匠天罚行者': {
                'cost_m': 300 + 750,  # 包含10个死徒的成本
                'cost_g': 200,
                'supply': 6,
                'hp': 200,
                'shield': 150,
                'dps_base': 306.67,  # 灵魂巧匠的4倍DPS
                'range': 12,
                'radius': 0.75,
                'commander': '阿拉纳克P1',
                'mu': 1.0,  # 阿拉纳克是200人口
                'omega': 1.1,  # 可移动射击
                'psi': 0.85,  # 中等过量击杀
                'vs_armored': 0,  # 无额外加成
                'vs_light': 0
            },
            '掠袭解放者': {
                'cost_m': 375,
                'cost_g': 375,
                'supply': 3,
                'hp': 180,
                'shield': 0,
                'dps_base': 78.1,  # 防御者模式DPS
                'range': 13,
                'radius': 1.0,
                'commander': '诺娃',
                'mu': 2.0,  # 诺娃100人口
                'omega': 0.7,  # 需要精确架设
                'psi': 0.85,
                'vs_armored': 0,
                'vs_light': 0
            },
            '普通天罚行者': {
                'cost_m': 300,
                'cost_g': 200,
                'supply': 6,
                'hp': 200,
                'shield': 150,
                'dps_base': 76.69,  # 献祭+精通
                'range': 12,
                'radius': 0.75,
                'commander': '阿拉纳克',
                'mu': 1.0,
                'omega': 1.1,
                'psi': 0.9,
                'vs_armored': 0,
                'vs_light': 0
            },
            '穿刺者': {
                'cost_m': 200,
                'cost_g': 100,
                'supply': 2,
                'hp': 200,  # 满级突变
                'shield': 0,
                'dps_base': 40,  # 潜地后的DPS
                'range': 9,
                'radius': 0.75,
                'commander': '德哈卡',
                'mu': 1.0,
                'omega': 0.9,
                'psi': 0.9,
                'vs_armored': 1.0,  # +100%对重甲
                'vs_light': 0
            },
            '攻城坦克': {
                'cost_m': 150,
                'cost_g': 125,
                'supply': 3,
                'hp': 227.5,  # 含+30%生命值精通
                'shield': 0,
                'dps_base': 35,  # 基础DPS
                'range': 13,
                'radius': 1.5,
                'commander': '斯旺',
                'mu': 1.0,
                'omega': 0.9,
                'psi': 0.9,
                'vs_armored': 0.5,  # 钨钢钉对重甲+50%
                'vs_light': 0,
                'aoe': 1.4  # AOE效果
            },
            '龙骑士': {
                'cost_m': 125,
                'cost_g': 50,
                'supply': 2,
                'hp': 80,
                'shield': 80,
                'dps_base': 20,  # 基础DPS较低
                'range': 6,
                'radius': 0.75,
                'commander': '阿塔尼斯',
                'mu': 1.0,
                'omega': 1.0,
                'psi': 1.0,
                'vs_armored': 1.0,  # 对重甲翻倍
                'vs_light': 0
            }
        }
        
        # 基础单位参数（用于对比）
        self.basic_units = {
            '陆战队员': {'hp': 45, 'shield': 0, 'armor': 0, 'tags': ['轻甲', '生物']},
            '跳虫': {'hp': 35, 'shield': 0, 'armor': 0, 'tags': ['轻甲', '生物']},
            '狂热者': {'hp': 100, 'shield': 50, 'armor': 1, 'tags': ['轻甲', '生物']}
        }
        
        # SAC参数
        self.sac_params = {
            'SAC-T': {
                'ehp_per_supply': 95,
                'armored_ratio': 0.8,
                'light_ratio': 0.2
            },
            'SAC-Z': {
                'ehp_per_supply': 75,
                'armored_ratio': 0.7,
                'light_ratio': 0.3
            }
        }
    
    def calculate_ehp(self, unit):
        """计算有效生命值"""
        hp = unit['hp']
        shield = unit['shield']
        # 简化的EHP计算，护盾有2秒/点的回复率
        return shield * 1.2 + hp
    
    def calculate_range_factor(self, unit):
        """计算射程系数（平方根版本）"""
        return np.sqrt(unit['range'] / unit['radius'])
    
    def calculate_cost_eff(self, unit):
        """计算有效成本"""
        # 根据指挥官调整矿气转换率
        if unit['commander'] == '诺娃':
            alpha = 1.0  # 诺娃矿气1:1
        else:
            alpha = 2.5  # 标准2.5:1
        
        return unit['cost_m'] + alpha * unit['cost_g']
    
    def calculate_dps_vs_sac(self, unit, sac_name):
        """计算对SAC的有效DPS"""
        sac = self.sac_params[sac_name]
        base_dps = unit['dps_base']
        
        # 计算混合伤害
        armored_dps = base_dps * (1 + unit['vs_armored'])
        light_dps = base_dps * (1 + unit['vs_light'])
        
        # 加权平均
        avg_dps = (armored_dps * sac['armored_ratio'] + 
                   light_dps * sac['light_ratio'])
        
        # 应用AOE系数（如果有）
        if 'aoe' in unit:
            avg_dps *= unit['aoe']
        
        return avg_dps
    
    def calculate_cev(self, unit, vs_target='general'):
        """计算CEV值"""
        ehp = self.calculate_ehp(unit)
        range_factor = self.calculate_range_factor(unit)
        cost_eff = self.calculate_cost_eff(unit)
        
        if vs_target in ['SAC-T', 'SAC-Z']:
            # 对SAC的CEV
            dps_eff = self.calculate_dps_vs_sac(unit, vs_target)
            target_ehp = self.sac_params[vs_target]['ehp_per_supply']
        else:
            # 通用CEV
            dps_eff = unit['dps_base']
            target_ehp = 1  # 归一化
        
        # 应用v2.3公式
        cev = (dps_eff * unit['psi'] * ehp * unit['omega'] * range_factor) / cost_eff * unit['mu']
        
        # 如果是对SAC，需要除以目标EHP
        if vs_target in ['SAC-T', 'SAC-Z']:
            cev = cev / target_ehp
        
        return cev
    
    def calculate_all_cevs(self):
        """计算所有单位的CEV值"""
        results = {}
        
        for unit_name, unit_data in self.units.items():
            results[unit_name] = {
                'general': round(self.calculate_cev(unit_data, 'general'), 1),
                'vs_SAC-T': round(self.calculate_cev(unit_data, 'SAC-T'), 2),
                'vs_SAC-Z': round(self.calculate_cev(unit_data, 'SAC-Z'), 2),
            }
        
        return results
    
    def print_latex_tables(self):
        """生成LaTeX表格内容"""
        results = self.calculate_all_cevs()
        
        # 表4.1: 对SAC的战斗效能
        print("% 表4.1内容")
        for unit_name in self.units.keys():
            commander = self.units[unit_name]['commander']
            sac_t = results[unit_name]['vs_SAC-T']
            sac_z = results[unit_name]['vs_SAC-Z']
            print(f"{unit_name} & {commander} & {sac_t} & {sac_z} \\\\")
        
        print("\n% 表4.3内容（排名）")
        # 按平均CEV排序
        sorted_units = sorted(results.items(), 
                            key=lambda x: (x[1]['vs_SAC-T'] + x[1]['vs_SAC-Z'])/2, 
                            reverse=True)
        
        for rank, (unit_name, values) in enumerate(sorted_units, 1):
            avg_cev = round((values['vs_SAC-T'] + values['vs_SAC-Z'])/2, 1)
            print(f"{rank} & {unit_name} & ... & {avg_cev} & ... \\\\")

if __name__ == "__main__":
    calculator = V23CEVCalculator()
    print("=== v2.3模型CEV计算结果 ===\n")
    
    results = calculator.calculate_all_cevs()
    
    print("通用CEV值：")
    for unit, values in results.items():
        print(f"{unit}: {values['general']}")
    
    print("\n对SAC的CEV值：")
    for unit, values in results.items():
        print(f"{unit}: SAC-T={values['vs_SAC-T']}, SAC-Z={values['vs_SAC-Z']}")
    
    print("\n" + "="*50 + "\n")
    calculator.print_latex_tables()