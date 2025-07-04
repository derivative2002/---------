#!/usr/bin/env python3
"""增强版单位对比可视化

提供更多维度的单位对比图表，包括：
- 多维度条形图对比
- 雷达图能力展示
- 热力图矩阵对比
- 时间序列动态展示
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from pathlib import Path
import json
from typing import Dict, List, Tuple, Any

# 配置中文字体
# 尝试多种中文字体
chinese_fonts = ['PingFang SC', 'Heiti SC', 'STHeiti', 'Arial Unicode MS', 'SimHei']
font_found = False

for font_name in chinese_fonts:
    if any(font_name in font.name for font in fm.fontManager.ttflist):
        plt.rcParams['font.sans-serif'] = [font_name]
        font_found = True
        print(f"使用字体: {font_name}")
        break

# 如果没找到中文字体，尝试查找所有可用字体
if not font_found:
    for font in fm.fontManager.ttflist:
        if any(char in font.name for char in ['Chinese', 'CN', 'SC', 'TC', 'Hei', 'Song', 'Kai']):
            plt.rcParams['font.sans-serif'] = [font.name]
            print(f"使用字体: {font.name}")
            break

plt.rcParams['axes.unicode_minus'] = False


class EnhancedUnitVisualizer:
    """增强版单位可视化器"""
    
    def __init__(self, data_path: Path):
        """初始化可视化器
        
        Args:
            data_path: 数据文件路径
        """
        self.data_path = data_path
        self.df = pd.read_csv(data_path)
        self.colors = {
            '阿塔尼斯': '#1E88E5',
            '阿拉纳克': '#D32F2F', 
            '诺娃': '#FF6F00',
            '德哈卡': '#388E3C',
            '斯旺': '#7B1FA2'
        }
        
    def create_multi_bar_comparison(self, save_path: Path = None):
        """创建多维度条形图对比
        
        展示CEV、DPS、生存能力、机动性等多个维度
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('五大精英单位多维度对比', fontsize=20, fontweight='bold')
        
        # 准备数据
        units = self.df[self.df['game_phase'] == 'mid_game'].copy()
        units['display_name'] = units['unit_name'] + '\n(' + units['commander'] + ')'
        
        # 1. CEV对比
        ax = axes[0, 0]
        bars = ax.bar(units['display_name'], units['cev'], 
                      color=[self.colors[cmd] for cmd in units['commander']])
        ax.set_title('战斗效能值(CEV)对比', fontsize=14)
        ax.set_ylabel('CEV值')
        ax.grid(axis='y', alpha=0.3)
        for bar, val in zip(bars, units['cev']):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                   f'{val:.1f}', ha='center', va='bottom')
        
        # 2. DPS对比
        ax = axes[0, 1]
        x = np.arange(len(units))
        width = 0.35
        ax.bar(x - width/2, units['base_dps'], width, label='基础DPS',
               color='lightblue', edgecolor='black')
        ax.bar(x + width/2, units['effective_dps'], width, label='有效DPS',
               color='orange', edgecolor='black')
        ax.set_title('伤害输出对比', fontsize=14)
        ax.set_ylabel('DPS')
        ax.set_xticks(x)
        ax.set_xticklabels(units['display_name'], rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # 3. 生存能力对比
        ax = axes[1, 0]
        metrics = ['survivability', 'mobility_score', 'range_score']
        labels = ['生存能力', '机动性', '射程评分']
        x = np.arange(len(units))
        width = 0.25
        
        for i, (metric, label) in enumerate(zip(metrics, labels)):
            ax.bar(x + i*width, units[metric], width, label=label)
        
        ax.set_title('能力指标对比', fontsize=14)
        ax.set_ylabel('评分')
        ax.set_xticks(x + width)
        ax.set_xticklabels(units['display_name'], rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # 4. 成本效益对比
        ax = axes[1, 1]
        ax.scatter(units['effective_cost'], units['overall_score'], 
                  s=units['cev']*5, 
                  c=[self.colors[cmd] for cmd in units['commander']],
                  alpha=0.7, edgecolors='black')
        
        for _, unit in units.iterrows():
            ax.annotate(unit['unit_name'], 
                       (unit['effective_cost'], unit['overall_score']),
                       xytext=(5, 5), textcoords='offset points', fontsize=10)
        
        ax.set_title('成本效益散点图', fontsize=14)
        ax.set_xlabel('有效成本')
        ax.set_ylabel('综合评分')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
    def create_radar_chart(self, save_path: Path = None):
        """创建雷达图展示单位能力"""
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # 选择中期游戏数据
        units = self.df[self.df['game_phase'] == 'mid_game'].copy()
        
        # 定义维度
        categories = ['CEV', 'DPS效率', '生存能力', '机动性', '射程', '多功能性']
        
        # 标准化数据到0-1范围
        def normalize(series):
            return (series - series.min()) / (series.max() - series.min())
        
        # 准备雷达图数据
        for _, unit in units.iterrows():
            values = [
                normalize(units['cev'])[unit.name],
                normalize(units['effective_dps'])[unit.name],
                normalize(units['survivability'])[unit.name],
                normalize(units['mobility_score'])[unit.name],
                normalize(units['range_score'])[unit.name],
                normalize(units['versatility_score'])[unit.name]
            ]
            values += values[:1]  # 闭合图形
            
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            angles += angles[:1]
            
            ax.plot(angles, values, 'o-', linewidth=2, 
                   label=f"{unit['unit_name']}({unit['commander']})",
                   color=self.colors[unit['commander']])
            ax.fill(angles, values, alpha=0.15, color=self.colors[unit['commander']])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, size=12)
        ax.set_ylim(0, 1)
        ax.grid(True)
        ax.set_title('精英单位能力雷达图', size=16, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
    def create_heatmap_comparison(self, save_path: Path = None):
        """创建热力图矩阵对比"""
        # 选择关键指标
        metrics = ['cev', 'effective_dps', 'survivability', 'mobility_score', 
                  'range_score', 'resource_efficiency', 'overall_score']
        labels = ['CEV', '有效DPS', '生存能力', '机动性', 
                 '射程', '资源效率', '综合评分']
        
        # 准备数据矩阵
        phases = ['early_game', 'mid_game', 'late_game']
        data_matrix = []
        unit_labels = []
        
        for phase in phases:
            phase_data = self.df[self.df['game_phase'] == phase]
            for _, unit in phase_data.iterrows():
                row = []
                for metric in metrics:
                    # 标准化到0-1范围
                    col_data = self.df[metric]
                    normalized = (unit[metric] - col_data.min()) / (col_data.max() - col_data.min())
                    row.append(normalized)
                data_matrix.append(row)
                unit_labels.append(f"{unit['unit_name']}\n{phase.replace('_', ' ').title()}")
        
        # 创建热力图
        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(data_matrix, 
                   xticklabels=labels,
                   yticklabels=unit_labels,
                   cmap='YlOrRd',
                   cbar_kws={'label': '标准化评分'},
                   annot=True,
                   fmt='.2f',
                   linewidths=0.5)
        
        ax.set_title('单位能力热力图对比', fontsize=16, fontweight='bold')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
    def create_phase_evolution_chart(self, save_path: Path = None):
        """创建游戏阶段演化图"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle('单位性能随游戏阶段变化', fontsize=18, fontweight='bold')
        
        phases = ['early_game', 'mid_game', 'late_game']
        phase_labels = ['前期', '中期', '后期']
        
        # 左图：CEV变化
        for commander in self.colors.keys():
            unit_data = self.df[self.df['commander'] == commander]
            if not unit_data.empty:
                unit_name = unit_data.iloc[0]['unit_name']
                cev_values = [unit_data[unit_data['game_phase'] == phase]['cev'].values[0] 
                             for phase in phases]
                ax1.plot(phase_labels, cev_values, 'o-', 
                        label=f"{unit_name}({commander})",
                        color=self.colors[commander],
                        linewidth=2, markersize=8)
        
        ax1.set_xlabel('游戏阶段', fontsize=12)
        ax1.set_ylabel('战斗效能值(CEV)', fontsize=12)
        ax1.set_title('CEV随游戏阶段变化', fontsize=14)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 右图：综合评分变化
        for commander in self.colors.keys():
            unit_data = self.df[self.df['commander'] == commander]
            if not unit_data.empty:
                unit_name = unit_data.iloc[0]['unit_name']
                score_values = [unit_data[unit_data['game_phase'] == phase]['overall_score'].values[0] 
                               for phase in phases]
                ax2.plot(phase_labels, score_values, 'o-', 
                        label=f"{unit_name}({commander})",
                        color=self.colors[commander],
                        linewidth=2, markersize=8)
        
        ax2.set_xlabel('游戏阶段', fontsize=12)
        ax2.set_ylabel('综合评分', fontsize=12)
        ax2.set_title('综合评分随游戏阶段变化', fontsize=14)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
    def create_unit_ranking_chart(self, save_path: Path = None):
        """创建单位排名图表"""
        fig, axes = plt.subplots(3, 1, figsize=(12, 16))
        fig.suptitle('精英单位综合排名', fontsize=20, fontweight='bold')
        
        phases = ['early_game', 'mid_game', 'late_game']
        phase_labels = ['游戏前期', '游戏中期', '游戏后期']
        
        for idx, (phase, phase_label) in enumerate(zip(phases, phase_labels)):
            ax = axes[idx]
            phase_data = self.df[self.df['game_phase'] == phase].sort_values('overall_score', ascending=True)
            
            # 创建横向条形图
            y_pos = np.arange(len(phase_data))
            bars = ax.barh(y_pos, phase_data['overall_score'], 
                           color=[self.colors[cmd] for cmd in phase_data['commander']])
            
            # 添加单位名称
            ax.set_yticks(y_pos)
            ax.set_yticklabels([f"{row['unit_name']}({row['commander']})" 
                               for _, row in phase_data.iterrows()])
            
            # 添加数值标签
            for i, (_, row) in enumerate(phase_data.iterrows()):
                ax.text(row['overall_score'] + 0.1, i, 
                       f"{row['overall_score']:.2f}", 
                       va='center', fontsize=10)
            
            ax.set_xlabel('综合评分', fontsize=12)
            ax.set_title(f'{phase_label}单位排名', fontsize=14)
            ax.grid(axis='x', alpha=0.3)
            
            # 添加排名标注
            for i in range(len(phase_data)):
                ax.text(-0.5, i, f'#{len(phase_data)-i}', 
                       ha='right', va='center', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()


def main():
    """主函数"""
    # 数据路径
    data_path = Path('/Users/bytedance/项目/星际争霸二数学模型/experiments/results/unit_eval/2025-07-02/21-38-04_五大精英单位对比排名_483fb4cf/data/processed/unit_evaluation_results.csv')
    output_dir = data_path.parent.parent / 'plots'
    output_dir.mkdir(exist_ok=True)
    
    # 创建可视化器
    visualizer = EnhancedUnitVisualizer(data_path)
    
    # 生成各种图表
    print("生成多维度条形图对比...")
    visualizer.create_multi_bar_comparison(output_dir / 'multi_dimension_comparison.png')
    
    print("生成能力雷达图...")
    visualizer.create_radar_chart(output_dir / 'ability_radar_chart.png')
    
    print("生成热力图矩阵...")
    visualizer.create_heatmap_comparison(output_dir / 'heatmap_comparison.png')
    
    print("生成阶段演化图...")
    visualizer.create_phase_evolution_chart(output_dir / 'phase_evolution.png')
    
    print("生成单位排名图...")
    visualizer.create_unit_ranking_chart(output_dir / 'unit_rankings.png')
    
    print(f"\n所有图表已保存到: {output_dir}")


if __name__ == '__main__':
    main()