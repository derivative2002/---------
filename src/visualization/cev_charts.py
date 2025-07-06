#!/usr/bin/env python3
"""
CEV结果可视化图表生成工具
用于生成论文v2.4版本的图表
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import seaborn as sns
from pathlib import Path

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class CEVVisualizer:
    """CEV结果可视化类"""
    
    def __init__(self):
        self.colors = {
            '掠袭解放者': '#FF6B6B',
            '灵魂巧匠天罚行者': '#4ECDC4', 
            '攻城坦克': '#45B7D1',
            '普通天罚行者': '#96CEB4',
            '穿刺者': '#FFEAA7',
            '龙骑士': '#DDA0DD'
        }
        
        self.commander_colors = {
            '诺娃': '#FF6B6B',
            '阿拉纳克P1': '#4ECDC4',
            '斯旺': '#45B7D1', 
            '阿拉纳克': '#96CEB4',
            '德哈卡': '#FFEAA7',
            '阿塔尼斯': '#DDA0DD'
        }
        
    def create_cev_ranking_chart(self, cev_data: Dict, save_path: str = None):
        """创建CEV排名柱状图"""
        # 准备数据
        units = list(cev_data.keys())
        values = [cev_data[unit]['avg_cev'] for unit in units]
        commanders = [cev_data[unit]['commander'] for unit in units]
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 创建柱状图
        bars = ax.bar(range(len(units)), values, 
                     color=[self.colors[unit] for unit in units],
                     alpha=0.8, edgecolor='black', linewidth=1)
        
        # 设置标签
        ax.set_xlabel('精英单位', fontsize=14, fontweight='bold')
        ax.set_ylabel('CEV值', fontsize=14, fontweight='bold')
        ax.set_title('六大精英单位CEV排名 (v2.4模型)', fontsize=16, fontweight='bold')
        
        # 设置x轴标签
        ax.set_xticks(range(len(units)))
        ax.set_xticklabels([f"{unit}\n({commanders[i]})" for i, unit in enumerate(units)], 
                          rotation=45, ha='right')
        
        # 添加数值标签
        for i, (bar, value) in enumerate(zip(bars, values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                   f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # 添加排名标签
        for i, bar in enumerate(bars):
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height()/2,
                   f'#{i+1}', ha='center', va='center', 
                   fontsize=12, fontweight='bold', color='white')
        
        # 美化图表
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim(0, max(values) * 1.1)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def create_cev_comparison_chart(self, cev_data: Dict, save_path: str = None):
        """创建CEV对比雷达图"""
        # 准备数据
        units = list(cev_data.keys())
        categories = ['DPS', 'EHP', '射程', '成本效率', '综合CEV']
        
        # 标准化数据到0-100范围
        normalized_data = {}
        for unit in units:
            data = cev_data[unit]
            normalized_data[unit] = {
                'DPS': min(data['dps_eff'] / 200 * 100, 100),
                'EHP': min(data['ehp'] / 500 * 100, 100), 
                '射程': min(data['f_range'] / 6 * 100, 100),
                '成本效率': min(1000 / data['c_eff'] * 100, 100),
                '综合CEV': min(data['avg_cev'] / 250 * 100, 100)
            }
        
        # 创建雷达图
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # 设置角度
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))
        
        # 绘制每个单位
        for i, unit in enumerate(units):
            values = [normalized_data[unit][cat] for cat in categories]
            values += [values[0]]  # 闭合图形
            
            ax.plot(angles, values, 'o-', linewidth=2, 
                   label=f"{unit} ({cev_data[unit]['commander']})",
                   color=self.colors[unit])
            ax.fill(angles, values, alpha=0.25, color=self.colors[unit])
        
        # 设置标签
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=12)
        ax.set_ylim(0, 100)
        ax.set_title('六大精英单位能力雷达图 (v2.4模型)', fontsize=16, fontweight='bold', pad=20)
        
        # 添加图例
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def create_cev_evolution_chart(self, evolution_data: Dict, save_path: str = None):
        """创建CEV演化图表"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        versions = list(evolution_data.keys())
        units = list(evolution_data[versions[0]].keys())
        
        # 为每个单位绘制演化曲线
        for unit in units:
            values = [evolution_data[version][unit] for version in versions]
            ax.plot(versions, values, 'o-', linewidth=2, markersize=8,
                   label=unit, color=self.colors[unit])
        
        # 设置标签
        ax.set_xlabel('模型版本', fontsize=14, fontweight='bold')
        ax.set_ylabel('CEV值', fontsize=14, fontweight='bold')
        ax.set_title('CEV模型演化过程 (v2.3 → v2.4)', fontsize=16, fontweight='bold')
        
        # 美化图表
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 添加版本说明
        version_notes = {
            'v2.3初版': '基础模型',
            'v2.3+溅射': '添加溅射系数',
            'v2.4最终': '优化操作难度'
        }
        
        for i, version in enumerate(versions):
            if version in version_notes:
                ax.annotate(version_notes[version], 
                           xy=(i, max([evolution_data[version][unit] for unit in units])),
                           xytext=(i, max([evolution_data[version][unit] for unit in units]) + 20),
                           ha='center', fontsize=10,
                           bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def create_cost_efficiency_chart(self, cev_data: Dict, save_path: str = None):
        """创建成本效率散点图"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 准备数据
        costs = [cev_data[unit]['c_eff'] for unit in cev_data.keys()]
        cevs = [cev_data[unit]['avg_cev'] for unit in cev_data.keys()]
        units = list(cev_data.keys())
        
        # 创建散点图
        for i, unit in enumerate(units):
            ax.scatter(costs[i], cevs[i], s=200, alpha=0.7, 
                      color=self.colors[unit], edgecolor='black', linewidth=2)
            ax.annotate(f"{unit}\n({cev_data[unit]['commander']})", 
                       xy=(costs[i], cevs[i]), xytext=(10, 10),
                       textcoords='offset points', ha='left',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
        
        # 添加效率线
        x_range = np.linspace(min(costs), max(costs), 100)
        efficiency_lines = [0.2, 0.4, 0.6]
        for eff in efficiency_lines:
            y_line = x_range * eff
            ax.plot(x_range, y_line, '--', alpha=0.5, color='gray')
            ax.text(max(costs) * 0.9, max(costs) * 0.9 * eff, 
                   f'效率={eff:.1f}', fontsize=10, alpha=0.7)
        
        # 设置标签
        ax.set_xlabel('有效成本', fontsize=14, fontweight='bold')
        ax.set_ylabel('CEV值', fontsize=14, fontweight='bold')
        ax.set_title('成本效率分析 (v2.4模型)', fontsize=16, fontweight='bold')
        
        # 美化图表
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def generate_all_charts(self, cev_data: Dict, output_dir: str = "output/v24_charts"):
        """生成所有图表"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 生成排名图
        self.create_cev_ranking_chart(cev_data, 
                                     str(output_path / "cev_ranking.png"))
        
        # 生成雷达图
        self.create_cev_comparison_chart(cev_data,
                                        str(output_path / "cev_radar.png"))
        
        # 生成成本效率图
        self.create_cost_efficiency_chart(cev_data,
                                         str(output_path / "cost_efficiency.png"))
        
        # 生成演化图（如果有演化数据）
        evolution_data = {
            'v2.3初版': {
                '掠袭解放者': 94.5,
                '灵魂巧匠天罚行者': 84.2,
                '攻城坦克': 59.5,
                '普通天罚行者': 45.3,
                '穿刺者': 83.8,
                '龙骑士': 59.7
            },
            'v2.3+溅射': {
                '掠袭解放者': 196.7,
                '灵魂巧匠天罚行者': 179.2,
                '攻城坦克': 112.6,
                '普通天罚行者': 97.6,
                '穿刺者': 67.4,
                '龙骑士': 43.4
            },
            'v2.4最终': {
                '掠袭解放者': 210.7,
                '灵魂巧匠天罚行者': 190.9,
                '攻城坦克': 112.6,
                '普通天罚行者': 104.0,
                '穿刺者': 82.4,
                '龙骑士': 65.4
            }
        }
        
        self.create_cev_evolution_chart(evolution_data,
                                       str(output_path / "cev_evolution.png"))
        
        print(f"所有图表已生成到: {output_path}")
        return output_path


def main():
    """主函数 - 生成v2.4版本的所有图表"""
    # 最终CEV数据
    cev_data = {
        '掠袭解放者': {
            'commander': '诺娃',
            'avg_cev': 210.72,
            'dps_eff': 89.3,
            'ehp': 450.0,
            'f_range': 5.0,
            'c_eff': 462.5
        },
        '灵魂巧匠天罚行者': {
            'commander': '阿拉纳克P1',
            'avg_cev': 190.87,
            'dps_eff': 183.5,
            'ehp': 375.0,
            'f_range': 5.1,
            'c_eff': 1500.0
        },
        '攻城坦克': {
            'commander': '斯旺',
            'avg_cev': 112.62,
            'dps_eff': 75.0,
            'ehp': 250.3,
            'f_range': 3.9,
            'c_eff': 462.5
        },
        '普通天罚行者': {
            'commander': '阿拉纳克',
            'avg_cev': 104.01,
            'dps_eff': 45.9,
            'ehp': 375.0,
            'f_range': 5.1,
            'c_eff': 750.0
        },
        '穿刺者': {
            'commander': '德哈卡',
            'avg_cev': 82.38,
            'dps_eff': 90.9,
            'ehp': 300.0,
            'f_range': 3.3,
            'c_eff': 475.0
        },
        '龙骑士': {
            'commander': '阿塔尼斯',
            'avg_cev': 65.44,
            'dps_eff': 27.8,
            'ehp': 280.0,
            'f_range': 4.0,
            'c_eff': 275.0
        }
    }
    
    # 创建可视化器并生成图表
    visualizer = CEVVisualizer()
    visualizer.generate_all_charts(cev_data)


if __name__ == "__main__":
    main() 