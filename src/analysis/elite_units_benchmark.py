"""
五大精英单位基准评估系统
包含多维度排名和可视化功能
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import json
from pathlib import Path
from datetime import datetime

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class EliteUnitsBenchmark:
    """五大精英单位基准评估系统"""
    
    def __init__(self):
        # 加载数据
        self.units_df = pd.read_csv('data/units/units_master.csv')
        self.weapons_df = pd.read_csv('data/units/weapons.csv')
        
        # 五个精英单位
        self.elite_units = ['Dragoon', 'Wrathwalker', 'SiegeTank_Swann', 'Impaler', 'RaidLiberator']
        
        # 时间因子（中期游戏）
        self.lambda_t = 0.593
        
        # 固定数据（从实验结果获取）
        self.unit_data = {
            'Dragoon': {
                'chinese_name': '龙骑士',
                'commander': '阿塔尼斯',
                'effective_hp': 210,
                'ability_value': 0,
                'synergy': 1.265
            },
            'Wrathwalker': {
                'chinese_name': '天罚行者',
                'commander': '阿拉纳克',
                'effective_hp': 429,
                'ability_value': 12,
                'synergy': 1.265
            },
            'SiegeTank_Swann': {
                'chinese_name': '攻城坦克',
                'commander': '斯旺',
                'effective_hp': 211.2,
                'ability_value': 10,
                'synergy': 1.265
            },
            'Impaler': {
                'chinese_name': '穿刺者',
                'commander': '德哈卡',
                'effective_hp': 220,
                'ability_value': 10,
                'synergy': 1.265
            },
            'RaidLiberator': {
                'chinese_name': '掠袭解放者',
                'commander': '诺娃',
                'effective_hp': 450,
                'ability_value': 10,
                'synergy': 1.265
            }
        }
        
        # 创建输出目录
        self.output_dir = Path('benchmarks')
        self.charts_dir = self.output_dir / 'charts'
        self.data_dir = self.output_dir / 'data'
        
        self.charts_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def calculate_effective_cost(self, unit_row):
        """计算有效成本"""
        resource_cost = unit_row['mineral_cost'] + unit_row['gas_cost'] * 2.5
        supply_pressure = unit_row['supply_cost'] * 25 * self.lambda_t
        return resource_cost + supply_pressure
    
    def calculate_weapon_dps(self, unit_id, target_type=None, vs_attribute=None):
        """计算武器DPS"""
        weapons = self.weapons_df[self.weapons_df['unit_id'] == unit_id].copy()
        
        # 根据目标类型筛选武器
        if target_type == 'ground':
            weapons = weapons[weapons['weapon_type'].isin(['ground', 'both'])]
        elif target_type == 'air':
            weapons = weapons[weapons['weapon_type'].isin(['air', 'both'])]
        
        total_dps = 0
        for _, weapon in weapons.iterrows():
            base_damage = weapon['base_damage']
            
            # 应用克制加成
            if vs_attribute and pd.notna(weapon.get('bonus_damage', '{}')):
                try:
                    bonus_data = json.loads(weapon['bonus_damage'])
                    if vs_attribute in bonus_data:
                        base_damage += bonus_data[vs_attribute]
                except:
                    pass
            
            dps = base_damage * weapon['attack_count'] / weapon['attack_interval']
            total_dps += dps
        
        return total_dps
    
    def calculate_cev(self, unit_row, target_type=None, vs_attribute=None):
        """计算CEV"""
        unit_id = unit_row['english_id']
        
        # 获取预设数据
        unit_info = self.unit_data[unit_id]
        effective_hp = unit_info['effective_hp']
        
        # 计算有效成本
        effective_cost = self.calculate_effective_cost(unit_row)
        
        # 计算DPS
        base_dps = self.calculate_weapon_dps(unit_id, target_type, vs_attribute)
        effective_dps = base_dps * unit_info['synergy']
        total_dps = effective_dps + unit_info['ability_value']
        
        # 计算CEV
        cev = (total_dps * effective_hp) / effective_cost
        
        return {
            'unit_id': unit_id,
            'unit_name': unit_info['chinese_name'],
            'commander': unit_info['commander'],
            'cev': cev,
            'total_dps': total_dps,
            'effective_hp': effective_hp,
            'effective_cost': effective_cost
        }
    
    def generate_all_rankings(self):
        """生成所有排名榜单"""
        selected_units = self.units_df[self.units_df['english_id'].isin(self.elite_units)]
        
        rankings = {}
        
        # 定义评估维度
        dimensions = {
            'overall': (None, None, '总体均衡'),
            'vs_ground': ('ground', None, '对地'),
            'vs_air': ('air', None, '对空'),
            'vs_light': (None, '轻甲', '对轻甲'),
            'vs_armored': (None, '重甲', '对重甲')
        }
        
        for key, (target_type, vs_attribute, name) in dimensions.items():
            results = []
            for _, unit in selected_units.iterrows():
                result = self.calculate_cev(unit, target_type, vs_attribute)
                results.append(result)
            
            df = pd.DataFrame(results).sort_values('cev', ascending=False)
            df['rank'] = range(1, len(df) + 1)
            rankings[key] = df
        
        return rankings
    
    def create_visualizations(self, rankings):
        """创建可视化图表"""
        
        # 1. 多维度CEV雷达图
        self._plot_radar_chart(rankings)
        
        # 2. 不同场景下的CEV对比柱状图
        self._plot_cev_comparison(rankings)
        
        # 3. DPS vs HP散点图
        self._plot_dps_vs_hp(rankings['overall'])
        
        # 4. 克制效果展示图
        self._plot_counter_effects(rankings)
        
        # 5. 排名变化热力图
        self._plot_ranking_heatmap(rankings)
    
    def _plot_radar_chart(self, rankings):
        """绘制雷达图"""
        fig, axes = plt.subplots(1, 2, figsize=(16, 8), subplot_kw=dict(projection='polar'))
        
        # 准备数据
        dimensions = ['总体', '对地', '对空', '对轻甲', '对重甲']
        num_vars = len(dimensions)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]
        
        # 左图：CEV值雷达图
        ax = axes[0]
        for unit_id in self.elite_units:
            values = []
            for key in ['overall', 'vs_ground', 'vs_air', 'vs_light', 'vs_armored']:
                cev = rankings[key][rankings[key]['unit_id'] == unit_id]['cev'].values[0]
                values.append(cev)
            
            values += values[:1]
            unit_name = self.unit_data[unit_id]['chinese_name']
            ax.plot(angles, values, 'o-', linewidth=2, label=unit_name)
            ax.fill(angles, values, alpha=0.15)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dimensions, size=12)
        ax.set_title('五大精英单位CEV多维度对比', size=16, y=1.08)
        ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1.1))
        ax.grid(True)
        
        # 右图：标准化雷达图（0-1范围）
        ax = axes[1]
        for unit_id in self.elite_units:
            values = []
            for key in ['overall', 'vs_ground', 'vs_air', 'vs_light', 'vs_armored']:
                df = rankings[key]
                cev = df[df['unit_id'] == unit_id]['cev'].values[0]
                # 标准化到0-1
                normalized = cev / df['cev'].max()
                values.append(normalized)
            
            values += values[:1]
            unit_name = self.unit_data[unit_id]['chinese_name']
            ax.plot(angles, values, 'o-', linewidth=2, label=unit_name)
            ax.fill(angles, values, alpha=0.15)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dimensions, size=12)
        ax.set_ylim(0, 1)
        ax.set_title('标准化性能对比（相对值）', size=16, y=1.08)
        ax.grid(True)
        
        plt.tight_layout()
        plt.savefig(self.charts_dir / 'radar_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_cev_comparison(self, rankings):
        """绘制CEV对比柱状图"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # 准备数据
        scenarios = ['总体', '对地', '对空', '对轻甲', '对重甲']
        x = np.arange(len(scenarios))
        width = 0.15
        
        # 绘制每个单位的柱状图
        for i, unit_id in enumerate(self.elite_units):
            values = []
            for key in ['overall', 'vs_ground', 'vs_air', 'vs_light', 'vs_armored']:
                cev = rankings[key][rankings[key]['unit_id'] == unit_id]['cev'].values[0]
                values.append(cev)
            
            unit_name = self.unit_data[unit_id]['chinese_name']
            offset = (i - 2) * width
            bars = ax.bar(x + offset, values, width, label=unit_name)
            
            # 添加数值标签
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}', ha='center', va='bottom', fontsize=8)
        
        ax.set_xlabel('战斗场景', fontsize=12)
        ax.set_ylabel('CEV值', fontsize=12)
        ax.set_title('五大精英单位在不同场景下的CEV对比', fontsize=16)
        ax.set_xticks(x)
        ax.set_xticklabels(scenarios)
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(self.charts_dir / 'cev_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_dps_vs_hp(self, overall_df):
        """绘制DPS vs HP散点图"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 准备数据
        for _, unit in overall_df.iterrows():
            ax.scatter(unit['total_dps'], unit['effective_hp'], 
                      s=unit['cev']*10, alpha=0.7, 
                      label=unit['unit_name'])
            
            # 添加标签
            ax.annotate(unit['unit_name'], 
                       (unit['total_dps'], unit['effective_hp']),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=10)
        
        ax.set_xlabel('总DPS', fontsize=12)
        ax.set_ylabel('有效生命值', fontsize=12)
        ax.set_title('DPS vs 有效生命值（圆圈大小表示CEV）', fontsize=16)
        ax.grid(True, alpha=0.3)
        
        # 添加参考线
        ax.axvline(overall_df['total_dps'].median(), color='gray', linestyle='--', alpha=0.5)
        ax.axhline(overall_df['effective_hp'].median(), color='gray', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(self.charts_dir / 'dps_vs_hp.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_counter_effects(self, rankings):
        """绘制克制效果图"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # 左图：对重甲克制效果
        units = []
        normal_cev = []
        vs_armored_cev = []
        
        for unit_id in self.elite_units:
            units.append(self.unit_data[unit_id]['chinese_name'])
            normal = rankings['overall'][rankings['overall']['unit_id'] == unit_id]['cev'].values[0]
            armored = rankings['vs_armored'][rankings['vs_armored']['unit_id'] == unit_id]['cev'].values[0]
            normal_cev.append(normal)
            vs_armored_cev.append(armored)
        
        x = np.arange(len(units))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, normal_cev, width, label='常规', alpha=0.8)
        bars2 = ax1.bar(x + width/2, vs_armored_cev, width, label='对重甲', alpha=0.8)
        
        # 标注提升百分比
        for i in range(len(units)):
            if normal_cev[i] > 0:
                improvement = (vs_armored_cev[i] - normal_cev[i]) / normal_cev[i] * 100
                if improvement > 5:  # 只标注明显提升的
                    ax1.text(i, max(normal_cev[i], vs_armored_cev[i]) + 2,
                            f'+{improvement:.0f}%', ha='center', fontsize=10)
        
        ax1.set_ylabel('CEV值')
        ax1.set_title('重甲克制效果')
        ax1.set_xticks(x)
        ax1.set_xticklabels(units, rotation=15)
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 右图：空地能力对比
        ground_dps = []
        air_dps = []
        
        for unit_id in self.elite_units:
            g_dps = rankings['vs_ground'][rankings['vs_ground']['unit_id'] == unit_id]['total_dps'].values[0]
            a_dps = rankings['vs_air'][rankings['vs_air']['unit_id'] == unit_id]['total_dps'].values[0]
            ground_dps.append(g_dps)
            air_dps.append(a_dps)
        
        bars1 = ax2.bar(x - width/2, ground_dps, width, label='对地DPS', alpha=0.8)
        bars2 = ax2.bar(x + width/2, air_dps, width, label='对空DPS', alpha=0.8)
        
        ax2.set_ylabel('DPS')
        ax2.set_title('空地作战能力对比')
        ax2.set_xticks(x)
        ax2.set_xticklabels(units, rotation=15)
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(self.charts_dir / 'counter_effects.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_ranking_heatmap(self, rankings):
        """绘制排名热力图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 准备数据矩阵
        units = [self.unit_data[uid]['chinese_name'] for uid in self.elite_units]
        scenarios = ['总体', '对地', '对空', '对轻甲', '对重甲']
        ranking_matrix = np.zeros((len(units), len(scenarios)))
        
        for i, unit_id in enumerate(self.elite_units):
            for j, key in enumerate(['overall', 'vs_ground', 'vs_air', 'vs_light', 'vs_armored']):
                rank = rankings[key][rankings[key]['unit_id'] == unit_id]['rank'].values[0]
                ranking_matrix[i, j] = rank
        
        # 绘制热力图
        sns.heatmap(ranking_matrix, annot=True, fmt='.0f', cmap='RdYlGn_r',
                   xticklabels=scenarios, yticklabels=units,
                   cbar_kws={'label': '排名'}, vmin=1, vmax=5)
        
        ax.set_title('五大精英单位各场景排名热力图', fontsize=16)
        
        plt.tight_layout()
        plt.savefig(self.charts_dir / 'ranking_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def save_rankings(self, rankings):
        """保存排名数据"""
        # 保存各个榜单
        for key, df in rankings.items():
            df.to_csv(self.data_dir / f'{key}_ranking.csv', index=False, encoding='utf-8-sig')
        
        # 生成汇总报告
        summary = {
            'generation_time': datetime.now().isoformat(),
            'elite_units': self.elite_units,
            'rankings': {}
        }
        
        for key, df in rankings.items():
            summary['rankings'][key] = df[['unit_name', 'commander', 'cev', 'rank']].round(2).to_dict('records')
        
        with open(self.output_dir / 'elite_units_summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
    
    def generate_markdown_report(self, rankings):
        """生成Markdown报告"""
        report = []
        report.append("# 五大精英单位基准评估报告\n")
        report.append(f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
        
        # 快速概览
        report.append("## 快速概览\n")
        report.append("| 单位 | 指挥官 | 总体CEV | 最强场景 | 最弱场景 |")
        report.append("|------|--------|---------|----------|----------|")
        
        for unit_id in self.elite_units:
            unit_name = self.unit_data[unit_id]['chinese_name']
            commander = self.unit_data[unit_id]['commander']
            overall_cev = rankings['overall'][rankings['overall']['unit_id'] == unit_id]['cev'].values[0]
            
            # 找出最强和最弱场景
            scenarios = {
                '总体': rankings['overall'][rankings['overall']['unit_id'] == unit_id]['cev'].values[0],
                '对地': rankings['vs_ground'][rankings['vs_ground']['unit_id'] == unit_id]['cev'].values[0],
                '对空': rankings['vs_air'][rankings['vs_air']['unit_id'] == unit_id]['cev'].values[0],
                '对轻甲': rankings['vs_light'][rankings['vs_light']['unit_id'] == unit_id]['cev'].values[0],
                '对重甲': rankings['vs_armored'][rankings['vs_armored']['unit_id'] == unit_id]['cev'].values[0]
            }
            
            best = max(scenarios.items(), key=lambda x: x[1])
            worst = min(scenarios.items(), key=lambda x: x[1])
            
            report.append(f"| {unit_name} | {commander} | {overall_cev:.1f} | {best[0]}({best[1]:.1f}) | {worst[0]}({worst[1]:.1f}) |")
        
        # 各榜单冠军
        report.append("\n## 各榜单冠军\n")
        titles = {
            'overall': '总体最强',
            'vs_ground': '对地之王',
            'vs_air': '制空霸主',
            'vs_light': '轻甲克星',
            'vs_armored': '重甲杀手'
        }
        
        for key, title in titles.items():
            champion = rankings[key].iloc[0]
            report.append(f"- **{title}**: {champion['unit_name']}（CEV: {champion['cev']:.1f}）")
        
        # 保存报告
        with open(self.output_dir / 'elite_units_report.md', 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
    
    def run(self):
        """运行完整的基准评估流程"""
        print("=== 五大精英单位基准评估系统 ===\n")
        
        # 生成排名
        print("生成多维度排名榜单...")
        rankings = self.generate_all_rankings()
        
        # 创建可视化
        print("创建可视化图表...")
        self.create_visualizations(rankings)
        
        # 保存数据
        print("保存榜单数据...")
        self.save_rankings(rankings)
        
        # 生成报告
        print("生成评估报告...")
        self.generate_markdown_report(rankings)
        
        print(f"\n评估完成！结果保存在: {self.output_dir}")
        print("- 数据文件: benchmarks/data/")
        print("- 可视化图表: benchmarks/charts/")
        print("- 汇总报告: benchmarks/elite_units_summary.json")
        print("- Markdown报告: benchmarks/elite_units_report.md")
        
        return rankings


def main():
    """主函数"""
    benchmark = EliteUnitsBenchmark()
    benchmark.run()


if __name__ == "__main__":
    main()