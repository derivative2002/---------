"""
六大精英单位基准测试
包含普通天罚行者和灵魂巧匠天罚行者
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
import seaborn as sns
from pathlib import Path
import json

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class SixEliteUnitsBenchmark:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / 'data' / 'units'
        self.units_df = pd.read_csv(self.data_dir / 'units_master.csv')
        self.weapons_df = pd.read_csv(self.data_dir / 'weapons.csv')
        
        # 六大精英单位
        self.elite_units = [
            'Dragoon',              # 龙骑士
            'Wrathwalker',         # 普通天罚行者
            'Wrathwalker_SoulArtificer',  # 灵魂巧匠天罚行者
            'SiegeTank_Swann',     # 攻城坦克（斯旺）
            'Impaler',             # 穿刺者
            'RaidLiberator_AS15'   # 掠袭解放者（+15%攻速）
        ]
        
        # 游戏参数
        self.lambda_t = 0.593  # 中期游戏
        self.alpha = 2.5       # 矿气转换率
        self.rho = 20          # 人口基准价值
        self.synergy = 1.265   # 协同系数
        
        # 精通配置
        self.masteries = {
            'Dragoon': {},  # 阿塔尼斯无攻速精通
            'Wrathwalker': {'attack_speed': 0.15},  # 阿拉纳克15%攻速
            'Wrathwalker_SoulArtificer': {'attack_speed': 0.15},  # 阿拉纳克15%攻速
            'SiegeTank_Swann': {'mech_hp': 0.30},  # 斯旺机械生命值+30%
            'Impaler': {'primal_hp': 0.30},  # 德哈卡原始虫族生命值
            'RaidLiberator_AS15': {}  # 已包含15%攻速在单位ID中
        }
        
        # 特殊科技
        self.technologies = {
            'Wrathwalker': {
                'sacrifice': True,  # 献祭科技
                'havoc_synergy': True  # 浩劫配合+1射程
            },
            'Wrathwalker_SoulArtificer': {
                'sacrifice': True,
                'havoc_synergy': True
            }
        }
    
    def calculate_cev(self, unit_row, target_type=None, vs_attribute=None):
        """计算单位的CEV"""
        unit_id = unit_row['english_id']
        
        # 计算有效成本
        mineral_cost = unit_row['mineral_cost']
        gas_cost = unit_row['gas_cost'] 
        supply_cost = unit_row['supply_cost']
        
        resource_cost = mineral_cost + gas_cost * self.alpha
        supply_pressure = supply_cost * self.rho * self.lambda_t
        effective_cost = resource_cost + supply_pressure
        
        # 计算有效HP
        hp = unit_row['hp']
        shields = unit_row['shields']
        armor = unit_row['armor']
        
        # 精通加成
        if unit_id in self.masteries and 'mech_hp' in self.masteries[unit_id]:
            if '机械' in unit_row['attributes']:
                hp *= (1 + self.masteries[unit_id]['mech_hp'])
        elif unit_id in self.masteries and 'primal_hp' in self.masteries[unit_id]:
            if '生物' in unit_row['attributes']:
                hp *= (1 + self.masteries[unit_id]['primal_hp'])
        
        damage_reduction = armor / (armor + 10)
        hp_armor_factor = 1 / (1 - damage_reduction)
        effective_hp = hp * hp_armor_factor + shields
        
        # 考虑护盾回充（20秒战斗）
        if shields > 0:
            shield_regen = 2 * 20  # 每秒2点，20秒战斗
            effective_hp += shield_regen
        
        # 获取武器数据
        weapon_id = unit_id
        
        # 特殊处理：选择合适的武器配置
        if unit_id == 'Wrathwalker' and self.technologies.get(unit_id, {}).get('sacrifice'):
            if unit_id in self.masteries and self.masteries[unit_id].get('attack_speed'):
                weapon_id = 'Wrathwalker_Sacrifice_Mastery'
            else:
                weapon_id = 'Wrathwalker_Sacrifice'
        elif unit_id == 'Wrathwalker_SoulArtificer':
            if self.technologies.get(unit_id, {}).get('sacrifice'):
                if unit_id in self.masteries and self.masteries[unit_id].get('attack_speed'):
                    weapon_id = 'Wrathwalker_SoulArtificer_Sacrifice_Mastery'
                else:
                    weapon_id = 'Wrathwalker_SoulArtificer_Sacrifice'
        
        # 筛选武器
        if target_type == 'ground':
            weapon_rows = self.weapons_df[(self.weapons_df['unit_id'] == weapon_id) & 
                                        (self.weapons_df['weapon_type'].isin(['ground', 'both']))]
        elif target_type == 'air':
            weapon_rows = self.weapons_df[(self.weapons_df['unit_id'] == weapon_id) & 
                                        (self.weapons_df['weapon_type'].isin(['air', 'both']))]
        else:
            weapon_rows = self.weapons_df[self.weapons_df['unit_id'] == weapon_id]
        
        if weapon_rows.empty:
            return None
        
        # 计算DPS
        total_dps = 0
        for _, weapon in weapon_rows.iterrows():
            base_damage = weapon['base_damage'] * weapon['attack_count']
            
            # 属性克制加成
            if vs_attribute and weapon['bonus_damage'] != '{}':
                try:
                    bonus_dict = json.loads(weapon['bonus_damage'])
                    if vs_attribute in bonus_dict:
                        base_damage += bonus_dict[vs_attribute] * weapon['attack_count']
                except:
                    pass
            
            attack_interval = weapon['attack_interval']
            dps = base_damage / attack_interval
            total_dps += dps
        
        # 特殊能力价值（简化处理）
        ability_value = 0
        if unit_id == 'Dragoon':
            ability_value = 5  # 守护护盾、奇异电荷等
        elif unit_id in ['Wrathwalker', 'Wrathwalker_SoulArtificer']:
            ability_value = 15  # 相位模式、攀崖等
        elif unit_id == 'SiegeTank_Swann':
            ability_value = 20  # 攻城模式溅射
        elif unit_id == 'Impaler':
            ability_value = 10  # 潜地、嫩化等
        elif unit_id == 'RaidLiberator_AS15':
            ability_value = 10  # 防御者模式等
        
        total_dps += ability_value
        
        # 计算CEV
        cev = (total_dps * effective_hp * self.synergy) / effective_cost
        
        return {
            'unit_id': unit_id,
            'chinese_name': unit_row['chinese_name'],
            'effective_cost': effective_cost,
            'effective_hp': effective_hp,
            'dps': total_dps,
            'cev': cev
        }
    
    def run_comprehensive_benchmark(self):
        """运行综合基准测试"""
        results = []
        
        # 定义测试场景
        scenarios = [
            ('overall', None, None, '综合评分'),
            ('vs_ground', 'ground', None, '对地能力'),
            ('vs_air', 'air', None, '对空能力'),
            ('vs_light', 'ground', '轻甲', '对轻甲'),
            ('vs_armored', 'ground', '重甲', '对重甲'),
            ('vs_structure', 'ground', '建筑', '对建筑')
        ]
        
        for scenario_id, target_type, vs_attribute, scenario_name in scenarios:
            print(f"\n=== {scenario_name} ===")
            scenario_results = []
            
            for unit_id in self.elite_units:
                unit_row = self.units_df[self.units_df['english_id'] == unit_id].iloc[0]
                cev_data = self.calculate_cev(unit_row, target_type, vs_attribute)
                
                if cev_data:
                    scenario_results.append(cev_data)
                    print(f"{cev_data['chinese_name']}: CEV = {cev_data['cev']:.1f}")
            
            # 排序并添加排名
            scenario_results.sort(key=lambda x: x['cev'], reverse=True)
            for i, result in enumerate(scenario_results):
                result['rank'] = i + 1
                result['scenario'] = scenario_name
                results.append(result)
        
        return pd.DataFrame(results)
    
    def create_visualizations(self, results_df):
        """创建可视化图表"""
        output_dir = Path(__file__).parent.parent.parent / 'output' / 'six_units'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. 综合排名柱状图
        plt.figure(figsize=(12, 8))
        overall_df = results_df[results_df['scenario'] == '综合评分'].sort_values('cev', ascending=True)
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        bars = plt.barh(overall_df['chinese_name'], overall_df['cev'], color=colors)
        
        # 添加数值标签
        for bar, value in zip(bars, overall_df['cev']):
            plt.text(value + 1, bar.get_y() + bar.get_height()/2, 
                    f'{value:.1f}', va='center')
        
        plt.xlabel('战斗效能值 (CEV)', fontsize=14)
        plt.title('六大精英单位综合CEV排名', fontsize=16, pad=20)
        plt.tight_layout()
        plt.savefig(output_dir / 'overall_ranking.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. 多维度雷达图
        fig, axes = plt.subplots(2, 3, figsize=(18, 12), subplot_kw=dict(projection='polar'))
        axes = axes.flatten()
        
        categories = ['综合评分', '对地能力', '对空能力', '对轻甲', '对重甲', '对建筑']
        
        for idx, unit_id in enumerate(self.elite_units):
            ax = axes[idx]
            unit_name = results_df[results_df['unit_id'] == unit_id].iloc[0]['chinese_name']
            
            # 获取各维度数据
            values = []
            for cat in categories:
                cat_data = results_df[(results_df['unit_id'] == unit_id) & 
                                    (results_df['scenario'] == cat)]
                if not cat_data.empty:
                    values.append(cat_data.iloc[0]['cev'])
                else:
                    values.append(0)
            
            # 闭合雷达图
            values += values[:1]
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            angles += angles[:1]
            
            # 绘制雷达图
            ax.plot(angles, values, 'o-', linewidth=2, color=colors[idx])
            ax.fill(angles, values, alpha=0.25, color=colors[idx])
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, size=10)
            ax.set_title(unit_name, size=14, pad=20)
            ax.set_ylim(0, max(results_df['cev']) * 1.1)
            
            # 添加网格
            ax.grid(True, alpha=0.3)
        
        plt.suptitle('六大精英单位多维度能力对比', fontsize=18, y=0.98)
        plt.tight_layout()
        plt.savefig(output_dir / 'radar_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. 热力图
        pivot_df = results_df.pivot(index='chinese_name', columns='scenario', values='cev')
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(pivot_df, annot=True, fmt='.1f', cmap='YlOrRd', 
                   cbar_kws={'label': 'CEV值'})
        plt.title('六大精英单位CEV热力图', fontsize=16, pad=20)
        plt.xlabel('评估场景', fontsize=12)
        plt.ylabel('单位名称', fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_dir / 'heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"\n图表已保存至: {output_dir}")
    
    def save_results(self, results_df):
        """保存结果到CSV"""
        output_dir = Path(__file__).parent.parent.parent / 'output' / 'six_units'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results_df.to_csv(output_dir / 'six_elite_units_benchmark.csv', 
                         index=False, encoding='utf-8-sig')
        
        # 创建排名汇总
        summary = []
        for scenario in results_df['scenario'].unique():
            scenario_df = results_df[results_df['scenario'] == scenario].sort_values('cev', ascending=False)
            for idx, row in scenario_df.iterrows():
                summary.append({
                    '场景': scenario,
                    '排名': row['rank'],
                    '单位': row['chinese_name'],
                    'CEV': f"{row['cev']:.1f}"
                })
        
        summary_df = pd.DataFrame(summary)
        summary_df.to_csv(output_dir / 'ranking_summary.csv', 
                         index=False, encoding='utf-8-sig')
        
        print(f"结果已保存至: {output_dir}")


def main():
    """主函数"""
    print("=== 六大精英单位基准测试 ===")
    print("包含：龙骑士、普通天罚行者、灵魂巧匠天罚行者、攻城坦克、穿刺者、掠袭解放者")
    
    benchmark = SixEliteUnitsBenchmark()
    results_df = benchmark.run_comprehensive_benchmark()
    
    # 创建可视化
    print("\n生成可视化图表...")
    benchmark.create_visualizations(results_df)
    
    # 保存结果
    benchmark.save_results(results_df)
    
    # 打印总结
    print("\n=== 总结 ===")
    overall_df = results_df[results_df['scenario'] == '综合评分'].sort_values('cev', ascending=False)
    print("\n综合CEV排名：")
    for idx, row in overall_df.iterrows():
        print(f"{row['rank']}. {row['chinese_name']}: {row['cev']:.1f}")


if __name__ == "__main__":
    main()