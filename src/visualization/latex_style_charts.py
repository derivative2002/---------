"""
使用matplotlib生成LaTeX风格的图表
包括柱状图、天梯榜、雷达图和热力图
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import cm
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime

# 设置LaTeX风格
plt.style.use('seaborn-v0_8-paper')

# 设置字体 - 优先使用系统中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# LaTeX风格设置
mpl.rcParams['axes.linewidth'] = 0.8
mpl.rcParams['grid.linewidth'] = 0.5
mpl.rcParams['xtick.major.width'] = 0.8
mpl.rcParams['ytick.major.width'] = 0.8
mpl.rcParams['xtick.minor.width'] = 0.5
mpl.rcParams['ytick.minor.width'] = 0.5
mpl.rcParams['xtick.major.size'] = 4
mpl.rcParams['ytick.major.size'] = 4
mpl.rcParams['xtick.minor.size'] = 2
mpl.rcParams['ytick.minor.size'] = 2

# 使用Computer Modern字体（LaTeX默认字体）for math
mpl.rcParams['mathtext.fontset'] = 'cm'

class LaTeXStyleCharts:
    """LaTeX风格图表生成器"""
    
    def __init__(self):
        self.output_dir = Path('benchmarks/latex_charts')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 五大精英单位数据
        self.elite_units = {
            'Dragoon': {'chinese_name': '龙骑士', 'commander': '阿塔尼斯'},
            'Wrathwalker': {'chinese_name': '天罚行者', 'commander': '阿拉纳克'},
            'SiegeTank_Swann': {'chinese_name': '攻城坦克', 'commander': '斯旺'},
            'Impaler': {'chinese_name': '穿刺者', 'commander': '德哈卡'},
            'RaidLiberator': {'chinese_name': '掠袭解放者', 'commander': '诺娃'}
        }
        
        # 加载排名数据
        self.load_ranking_data()
        
        # 定义配色方案（学术风格）
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'tertiary': '#2ca02c',
            'quaternary': '#d62728',
            'quinary': '#9467bd',
            'bar_colors': ['#4C72B0', '#DD8452', '#55A868', '#C44E52', '#8172B3'],
            'heatmap': 'RdYlGn_r'
        }
        
    def load_ranking_data(self):
        """加载排名数据"""
        self.rankings = {}
        dimensions = ['overall', 'vs_ground', 'vs_air', 'vs_light', 'vs_armored']
        
        for dim in dimensions:
            file_path = Path(f'benchmarks/data/{dim}_ranking.csv')
            if file_path.exists():
                self.rankings[dim] = pd.read_csv(file_path)
    
    def generate_all_charts(self):
        """生成所有图表"""
        print("生成LaTeX风格图表...")
        
        # 1. 柱状图 - 不同场景下的排名
        self.generate_ranking_bar_chart()
        
        # 2. 综合评分天梯榜
        self.generate_score_ladder()
        
        # 3. 雷达图
        self.generate_radar_chart()
        
        # 4. 热力图
        self.generate_heatmap()
        
        print(f"\n所有图表已生成在: {self.output_dir}")
    
    def generate_ranking_bar_chart(self):
        """生成排名柱状图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 准备数据
        scenarios = {
            'overall': '总体',
            'vs_ground': '对地',
            'vs_air': '对空',
            'vs_light': '对轻甲',
            'vs_armored': '对重甲'
        }
        
        # 单位名称
        unit_names = [self.elite_units[uid]['chinese_name'] for uid in self.elite_units.keys()]
        x = np.arange(len(unit_names))
        width = 0.15
        
        # 为每个场景绘制柱状图
        for i, (key, name) in enumerate(scenarios.items()):
            ranks = []
            for unit_id in self.elite_units.keys():
                rank = self.rankings[key][self.rankings[key]['unit_id'] == unit_id]['rank'].values[0]
                ranks.append(6 - rank)  # 转换为逆序（越高越好）
            
            offset = (i - 2) * width
            bars = ax.bar(x + offset, ranks, width, 
                          label=name, color=self.colors['bar_colors'][i], 
                          edgecolor='black', linewidth=0.5)
            
            # 添加数值标签
            for bar, rank in zip(bars, ranks):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{6-rank}', ha='center', va='bottom', fontsize=8)
        
        # 设置图表样式
        ax.set_xlabel('单位', fontsize=12, fontweight='bold')
        ax.set_ylabel('排名（逆序）', fontsize=12, fontweight='bold')
        ax.set_title('五大精英单位场景排名对比', fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(unit_names, rotation=15, ha='right')
        ax.set_ylim(0, 5.5)
        ax.set_yticks(range(6))
        ax.set_yticklabels(['', '5', '4', '3', '2', '1'])
        
        # 添加网格
        ax.grid(True, axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # 图例
        ax.legend(frameon=True, fancybox=False, shadow=False, 
                 edgecolor='black', loc='upper left')
        
        # 添加边框
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(0.5)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'ranking_bar_chart.png', dpi=300, bbox_inches='tight')
        plt.savefig(self.output_dir / 'ranking_bar_chart.pdf', bbox_inches='tight')
        plt.close()
        
        print("✓ 生成排名柱状图")
    
    def generate_score_ladder(self):
        """生成综合评分天梯榜"""
        # 计算综合评分
        scores = []
        for unit_id in self.elite_units.keys():
            unit_data = self.rankings['overall'][self.rankings['overall']['unit_id'] == unit_id].iloc[0]
            
            # 综合评分计算
            cev = unit_data['cev']
            resource_efficiency = cev / unit_data['effective_cost'] * 100
            overall_score = cev * 0.6 + resource_efficiency * 0.4
            
            scores.append({
                'rank': 0,  # 待填充
                'unit': self.elite_units[unit_id]['chinese_name'],
                'commander': self.elite_units[unit_id]['commander'],
                'score': overall_score,
                'cev': cev,
                'efficiency': resource_efficiency
            })
        
        # 排序并设置排名
        scores.sort(key=lambda x: x['score'], reverse=True)
        for i, score in enumerate(scores):
            score['rank'] = i + 1
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 隐藏坐标轴
        ax.axis('off')
        
        # 标题
        ax.text(0.5, 0.95, '综合评分天梯榜', 
                ha='center', va='top', fontsize=16, fontweight='bold',
                transform=ax.transAxes)
        
        # 创建表格数据
        cell_text = []
        colors = []
        
        for score in scores:
            row = [
                f"{score['rank']}",
                score['unit'],
                score['commander'],
                f"{score['score']:.1f}",
                f"{score['cev']:.1f}",
                f"{score['efficiency']:.1f}"
            ]
            cell_text.append(row)
            
            # 设置排名颜色
            if score['rank'] == 1:
                colors.append(['#FFD700'] * 6)  # 金色
            elif score['rank'] == 2:
                colors.append(['#C0C0C0'] * 6)  # 银色
            elif score['rank'] == 3:
                colors.append(['#CD7F32'] * 6)  # 铜色
            else:
                colors.append(['white'] * 6)
        
        # 创建表格
        table = ax.table(cellText=cell_text,
                        cellColours=colors,
                        colLabels=['排名', '单位', '指挥官', '综合评分', 'CEV', '资源效率'],
                        cellLoc='center',
                        loc='center',
                        bbox=[0.1, 0.3, 0.8, 0.6])
        
        # 设置表格样式
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # 设置表头样式
        for i in range(6):
            cell = table[(0, i)]
            cell.set_facecolor('#4C72B0')
            cell.set_text_props(weight='bold', color='white')
        
        # 添加边框
        for key, cell in table.get_celld().items():
            cell.set_linewidth(0.5)
            cell.set_edgecolor('black')
        
        # 添加说明
        ax.text(0.5, 0.15, '评分说明：综合评分 = CEV × 60% + 资源效率 × 40%',
                ha='center', va='top', fontsize=10,
                transform=ax.transAxes)
        
        ax.text(0.5, 0.10, '其中CEV为战斗效能值，资源效率为单位CEV与成本的比值',
                ha='center', va='top', fontsize=9, style='italic',
                transform=ax.transAxes)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'score_ladder.png', dpi=300, bbox_inches='tight')
        plt.savefig(self.output_dir / 'score_ladder.pdf', bbox_inches='tight')
        plt.close()
        
        print("✓ 生成综合评分天梯榜")
    
    def generate_radar_chart(self):
        """生成雷达图"""
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # 准备数据
        dimensions = ['overall', 'vs_ground', 'vs_air', 'vs_light', 'vs_armored']
        dimension_names = ['总体', '对地', '对空', '对轻甲', '对重甲']
        
        # 角度
        angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False)
        angles = np.concatenate([angles, [angles[0]]])
        
        # 为每个单位绘制雷达图
        for i, unit_id in enumerate(self.elite_units.keys()):
            values = []
            for dim in dimensions:
                df = self.rankings[dim]
                cev = df[df['unit_id'] == unit_id]['cev'].values[0]
                # 标准化到0-1
                normalized = cev / df['cev'].max()
                values.append(normalized)
            
            values.append(values[0])  # 闭合多边形
            
            unit_name = self.elite_units[unit_id]['chinese_name']
            ax.plot(angles, values, 'o-', linewidth=2, 
                   label=unit_name, color=self.colors['bar_colors'][i])
            ax.fill(angles, values, alpha=0.15, color=self.colors['bar_colors'][i])
        
        # 设置雷达图样式
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dimension_names, fontsize=12)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=10)
        
        # 添加网格
        ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
        
        # 标题和图例
        ax.set_title('五大精英单位多维度性能对比\n（标准化值）', 
                    fontsize=14, fontweight='bold', pad=30)
        ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1), 
                 frameon=True, fancybox=False, shadow=False,
                 edgecolor='black')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'radar_chart.png', dpi=300, bbox_inches='tight')
        plt.savefig(self.output_dir / 'radar_chart.pdf', bbox_inches='tight')
        plt.close()
        
        print("✓ 生成雷达图")
    
    def generate_heatmap(self):
        """生成热力图"""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # 准备数据矩阵
        units = [self.elite_units[uid]['chinese_name'] for uid in self.elite_units.keys()]
        scenarios = ['总体', '对地', '对空', '对轻甲', '对重甲']
        ranking_matrix = np.zeros((len(units), len(scenarios)))
        
        # 填充排名数据
        dimensions = ['overall', 'vs_ground', 'vs_air', 'vs_light', 'vs_armored']
        for i, unit_id in enumerate(self.elite_units.keys()):
            for j, dim in enumerate(dimensions):
                rank = self.rankings[dim][self.rankings[dim]['unit_id'] == unit_id]['rank'].values[0]
                ranking_matrix[i, j] = rank
        
        # 创建热力图
        im = ax.imshow(ranking_matrix, cmap='RdYlGn_r', aspect='auto', 
                      vmin=1, vmax=5, interpolation='nearest')
        
        # 设置刻度
        ax.set_xticks(np.arange(len(scenarios)))
        ax.set_yticks(np.arange(len(units)))
        ax.set_xticklabels(scenarios, fontsize=11)
        ax.set_yticklabels(units, fontsize=11)
        
        # 旋转顶部标签
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right", rotation_mode="anchor")
        
        # 添加数值标签
        for i in range(len(units)):
            for j in range(len(scenarios)):
                text = ax.text(j, i, f'{int(ranking_matrix[i, j])}',
                             ha="center", va="center", color="black", fontsize=12)
        
        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('排名', rotation=270, labelpad=15, fontsize=11)
        cbar.set_ticks([1, 2, 3, 4, 5])
        
        # 设置标题
        ax.set_title('五大精英单位场景排名热力图', fontsize=14, fontweight='bold', pad=20)
        
        # 添加边框
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(0.5)
            spine.set_color('black')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'heatmap.png', dpi=300, bbox_inches='tight')
        plt.savefig(self.output_dir / 'heatmap.pdf', bbox_inches='tight')
        plt.close()
        
        print("✓ 生成热力图")


def main():
    """主函数"""
    generator = LaTeXStyleCharts()
    generator.generate_all_charts()
    
    # 生成LaTeX源文件说明
    readme_content = """# LaTeX风格图表

本目录包含使用matplotlib生成的LaTeX风格图表。

## 图表列表

1. **ranking_bar_chart** - 不同场景下的单位排名对比
2. **score_ladder** - 综合评分天梯榜
3. **radar_chart** - 多维度性能雷达图
4. **heatmap** - 场景排名热力图

## 文件格式

每个图表都提供两种格式：
- `.png` - 高分辨率位图（300 DPI）
- `.pdf` - 矢量图格式

## 使用说明

这些图表采用学术论文风格设计，可直接用于：
- 学术论文
- 技术报告
- 演示文稿

图表使用了Times New Roman（英文）和系统中文字体。
"""
    
    with open(Path('benchmarks/latex_charts/README.md'), 'w', encoding='utf-8') as f:
        f.write(readme_content)


if __name__ == "__main__":
    main()