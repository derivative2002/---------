"""
基准评估系统V2：适配新的数据格式
用于生成官方单位的基准指标榜单和图表，为新单位设计提供对标参考
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path
from datetime import datetime

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class BenchmarkSystemV2:
    """基准评估系统V2，适配新的数据格式"""
    
    def __init__(self, experiment_results_path: str):
        """
        初始化基准系统
        
        Args:
            experiment_results_path: 实验结果CSV文件路径
        """
        self.results_df = pd.read_csv(experiment_results_path)
        self.benchmark_data = {}
        self.charts_dir = Path("benchmarks/charts")
        self.charts_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_all_benchmarks(self) -> Dict[str, pd.DataFrame]:
        """生成所有基准榜单"""
        benchmarks = {
            "overall_cev": self._generate_cev_ranking(),
            "cost_efficiency": self._generate_cost_efficiency_ranking(),
            "dps_ranking": self._generate_dps_ranking(),
            "survivability": self._generate_survivability_ranking(),
            "phase_rankings": self._generate_phase_rankings(),
            "score_ranking": self._generate_score_ranking()
        }
        
        # 保存所有榜单
        self._save_benchmarks(benchmarks)
        return benchmarks
    
    def _generate_cev_ranking(self) -> pd.DataFrame:
        """生成综合CEV排行榜（基于中期数据）"""
        # 使用中期游戏数据作为标准
        df_mid = self.results_df[self.results_df['game_phase'] == 'mid_game'].copy()
        
        ranking = df_mid[['english_id', 'unit_name', 'commander', 'cev', 
                         'effective_cost', 'effective_dps', 'effective_hp']].copy()
        ranking = ranking.sort_values('cev', ascending=False)
        ranking['rank'] = range(1, len(ranking) + 1)
        
        # 添加分位数信息
        ranking['cev_percentile'] = ranking['cev'].rank(pct=True) * 100
        
        return ranking
    
    def _generate_cost_efficiency_ranking(self) -> pd.DataFrame:
        """生成成本效率排行榜"""
        df_mid = self.results_df[self.results_df['game_phase'] == 'mid_game'].copy()
        
        # 使用已有的效率指标
        ranking = df_mid[['english_id', 'unit_name', 'commander', 
                         'resource_efficiency', 'supply_efficiency', 'cev']].copy()
        ranking = ranking.sort_values('resource_efficiency', ascending=False)
        ranking['efficiency_rank'] = range(1, len(ranking) + 1)
        
        return ranking
    
    def _generate_dps_ranking(self) -> pd.DataFrame:
        """生成DPS排行榜"""
        df_mid = self.results_df[self.results_df['game_phase'] == 'mid_game'].copy()
        
        ranking = df_mid[['english_id', 'unit_name', 'commander', 
                         'effective_dps', 'base_dps', 'ability_value', 'cev']].copy()
        ranking = ranking.sort_values('effective_dps', ascending=False)
        ranking['dps_rank'] = range(1, len(ranking) + 1)
        
        # 添加DPS分类
        ranking['dps_tier'] = pd.cut(ranking['effective_dps'], 
                                    bins=[0, 10, 25, 50, 100, float('inf')],
                                    labels=['低', '中低', '中', '高', '极高'])
        
        return ranking
    
    def _generate_survivability_ranking(self) -> pd.DataFrame:
        """生成生存能力排行榜"""
        df_mid = self.results_df[self.results_df['game_phase'] == 'mid_game'].copy()
        
        ranking = df_mid[['english_id', 'unit_name', 'commander', 
                         'effective_hp', 'survivability', 'cev']].copy()
        ranking = ranking.sort_values('effective_hp', ascending=False)
        ranking['survivability_rank'] = range(1, len(ranking) + 1)
        
        # 添加生存能力分类
        ranking['survivability_tier'] = pd.cut(ranking['effective_hp'],
                                              bins=[0, 100, 250, 500, 1000, float('inf')],
                                              labels=['脆弱', '较弱', '中等', '坚韧', '极坚韧'])
        
        return ranking
    
    def _generate_phase_rankings(self) -> Dict[str, pd.DataFrame]:
        """生成不同游戏阶段的排行榜"""
        phase_rankings = {}
        
        for phase in ['early_game', 'mid_game', 'late_game']:
            df_phase = self.results_df[self.results_df['game_phase'] == phase].copy()
            df_phase = df_phase.sort_values('cev', ascending=False)
            phase_rankings[phase] = df_phase[['english_id', 'unit_name', 'commander', 'cev']].head(20)
        
        return phase_rankings
    
    def _generate_score_ranking(self) -> pd.DataFrame:
        """生成综合评分排行榜"""
        df_mid = self.results_df[self.results_df['game_phase'] == 'mid_game'].copy()
        
        ranking = df_mid[['english_id', 'unit_name', 'commander', 'overall_score',
                         'range_score', 'mobility_score', 'versatility_score', 'cev']].copy()
        ranking = ranking.sort_values('overall_score', ascending=False)
        ranking['score_rank'] = range(1, len(ranking) + 1)
        
        return ranking
    
    def generate_benchmark_charts(self):
        """生成基准图表"""
        df_mid = self.results_df[self.results_df['game_phase'] == 'mid_game'].copy()
        
        # 1. CEV分布箱线图
        self._plot_cev_distribution(df_mid)
        
        # 2. DPS vs 生存能力散点图
        self._plot_dps_vs_survivability(df_mid)
        
        # 3. 效率对比图
        self._plot_efficiency_comparison(df_mid)
        
        # 4. 游戏阶段CEV变化图
        self._plot_phase_evolution()
        
        # 5. 综合评分雷达图
        self._plot_score_radar(df_mid)
        
    def _plot_cev_distribution(self, df: pd.DataFrame):
        """绘制CEV分布箱线图"""
        plt.figure(figsize=(12, 8))
        
        # 按指挥官分组的CEV分布
        commanders = df['commander'].unique()
        data_by_commander = [df[df['commander'] == cmd]['cev'].values for cmd in commanders]
        
        plt.boxplot(data_by_commander, labels=commanders)
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('CEV')
        plt.title('各指挥官单位CEV分布（中期游戏）')
        plt.grid(True, alpha=0.3)
        
        # 添加平均线
        plt.axhline(y=df['cev'].mean(), color='r', linestyle='--', 
                   label=f'总体平均: {df["cev"].mean():.2f}')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(self.charts_dir / 'cev_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_dps_vs_survivability(self, df: pd.DataFrame):
        """绘制DPS vs 生存能力散点图"""
        plt.figure(figsize=(12, 10))
        
        # 创建散点图，点的大小表示CEV
        scatter = plt.scatter(df['effective_dps'], df['effective_hp'], 
                            s=df['cev']*10, alpha=0.6, 
                            c=df['cev'], cmap='viridis')
        
        # 添加颜色条
        plt.colorbar(scatter, label='CEV')
        
        # 添加四象限分割线
        plt.axvline(x=df['effective_dps'].median(), color='gray', linestyle='--', alpha=0.5)
        plt.axhline(y=df['effective_hp'].median(), color='gray', linestyle='--', alpha=0.5)
        
        # 标注顶级单位
        top_units = df.nlargest(5, 'cev')
        for _, unit in top_units.iterrows():
            plt.annotate(unit['unit_name'], 
                        (unit['effective_dps'], unit['effective_hp']),
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        plt.xlabel('有效DPS')
        plt.ylabel('有效生命值')
        plt.title('单位战斗特性分布图（圆圈大小表示CEV）')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.charts_dir / 'dps_vs_survivability.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_efficiency_comparison(self, df: pd.DataFrame):
        """绘制效率对比图"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # 资源效率 vs CEV
        ax1.scatter(df['resource_efficiency'], df['cev'], alpha=0.6, s=50)
        ax1.set_xlabel('资源效率')
        ax1.set_ylabel('CEV')
        ax1.set_title('资源效率与CEV关系')
        ax1.grid(True, alpha=0.3)
        
        # 人口效率 vs CEV
        ax2.scatter(df['supply_efficiency'], df['cev'], alpha=0.6, s=50)
        ax2.set_xlabel('人口效率')
        ax2.set_ylabel('CEV')
        ax2.set_title('人口效率与CEV关系')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.charts_dir / 'efficiency_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_phase_evolution(self):
        """绘制游戏阶段CEV变化图"""
        plt.figure(figsize=(14, 8))
        
        # 选择TOP10单位（基于中期CEV）
        df_mid = self.results_df[self.results_df['game_phase'] == 'mid_game']
        top_units = df_mid.nlargest(10, 'cev')['english_id'].unique()
        
        phases = ['early_game', 'mid_game', 'late_game']
        phase_labels = ['早期', '中期', '后期']
        
        for unit_id in top_units:
            unit_data = self.results_df[self.results_df['english_id'] == unit_id]
            unit_name = unit_data.iloc[0]['unit_name']
            
            cev_values = []
            for phase in phases:
                phase_data = unit_data[unit_data['game_phase'] == phase]
                if not phase_data.empty:
                    cev_values.append(phase_data.iloc[0]['cev'])
                else:
                    cev_values.append(0)
            
            plt.plot(phase_labels, cev_values, marker='o', label=unit_name)
        
        plt.xlabel('游戏阶段')
        plt.ylabel('CEV')
        plt.title('TOP10单位CEV阶段变化')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.charts_dir / 'phase_evolution.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_score_radar(self, df: pd.DataFrame):
        """绘制综合评分雷达图"""
        # 选择TOP5单位
        top_units = df.nlargest(5, 'overall_score')
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # 评分维度
        categories = ['射程', '机动性', '多功能性', '生存能力', '资源效率']
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        for _, unit in top_units.iterrows():
            values = [
                unit['range_score'],
                unit['mobility_score'],
                unit['versatility_score'],
                unit['survivability'],
                unit['resource_efficiency'] / df['resource_efficiency'].max()  # 归一化
            ]
            values += values[:1]
            
            ax.plot(angles, values, 'o-', linewidth=2, label=unit['unit_name'])
            ax.fill(angles, values, alpha=0.15)
        
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 1)
        ax.set_title('TOP5单位综合能力雷达图', y=1.08)
        ax.grid(True)
        ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
        
        plt.tight_layout()
        plt.savefig(self.charts_dir / 'score_radar.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _save_benchmarks(self, benchmarks: Dict[str, any]):
        """保存所有基准数据"""
        output_dir = Path("benchmarks/data")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存主要榜单
        for name, data in benchmarks.items():
            if isinstance(data, pd.DataFrame):
                data.to_csv(output_dir / f"{name}_ranking.csv", index=False, encoding='utf-8-sig')
            elif isinstance(data, dict):
                # 处理嵌套的榜单
                for sub_name, sub_data in data.items():
                    sub_data.to_csv(output_dir / f"{name}_{sub_name}.csv", 
                                   index=False, encoding='utf-8-sig')
        
        # 生成汇总报告
        self._generate_summary_report(benchmarks)
    
    def _generate_summary_report(self, benchmarks: Dict[str, any]):
        """生成基准汇总报告"""
        df_mid = self.results_df[self.results_df['game_phase'] == 'mid_game']
        
        report = {
            "generation_time": datetime.now().isoformat(),
            "total_units": len(df_mid['english_id'].unique()),
            "total_commanders": len(df_mid['commander'].unique()),
            "cev_statistics": {
                "mean": float(df_mid['cev'].mean()),
                "std": float(df_mid['cev'].std()),
                "min": float(df_mid['cev'].min()),
                "max": float(df_mid['cev'].max()),
                "quartiles": {
                    "25%": float(df_mid['cev'].quantile(0.25)),
                    "50%": float(df_mid['cev'].quantile(0.50)),
                    "75%": float(df_mid['cev'].quantile(0.75))
                }
            },
            "top_10_units": benchmarks['overall_cev'].head(10)[
                ['english_id', 'unit_name', 'commander', 'cev']
            ].to_dict('records')
        }
        
        with open('benchmarks/benchmark_summary.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    
    def evaluate_new_unit(self, new_unit_stats: Dict) -> Dict[str, any]:
        """
        评估新单位相对于基准的表现
        
        Args:
            new_unit_stats: 新单位的统计数据
            
        Returns:
            评估结果字典
        """
        df_mid = self.results_df[self.results_df['game_phase'] == 'mid_game'].copy()
        
        evaluation = {
            "cev_percentile": float((df_mid['cev'] < new_unit_stats['cev']).mean() * 100),
            "dps_percentile": float((df_mid['effective_dps'] < new_unit_stats['effective_dps']).mean() * 100),
            "survivability_percentile": float((df_mid['effective_hp'] < new_unit_stats['effective_hp']).mean() * 100),
            "similar_units": self._find_similar_units(new_unit_stats, df_mid),
            "balance_assessment": self._assess_balance(new_unit_stats, df_mid)
        }
        
        return evaluation
    
    def _find_similar_units(self, new_unit: Dict, df: pd.DataFrame, top_n: int = 5) -> List[Dict]:
        """找到与新单位最相似的官方单位"""
        # 标准化特征
        features = ['cev', 'effective_dps', 'effective_hp', 'effective_cost']
        
        # 计算欧氏距离
        distances = []
        for _, unit in df.iterrows():
            dist = sum((new_unit.get(f, 0) - unit[f])**2 for f in features) ** 0.5
            distances.append({
                'english_id': unit['english_id'],
                'unit_name': unit['unit_name'],
                'commander': unit['commander'],
                'distance': dist,
                'cev': unit['cev']
            })
        
        # 返回最相似的单位
        return sorted(distances, key=lambda x: x['distance'])[:top_n]
    
    def _assess_balance(self, new_unit: Dict, df: pd.DataFrame) -> Dict[str, str]:
        """评估新单位的平衡性"""
        cev_std = df['cev'].std()
        cev_mean = df['cev'].mean()
        
        # 计算新单位CEV与平均值的偏差
        deviation = (new_unit['cev'] - cev_mean) / cev_std
        
        if abs(deviation) < 1:
            balance_status = "平衡"
            recommendation = "数值设计合理，无需调整"
        elif deviation > 2:
            balance_status = "过强"
            recommendation = "建议降低DPS或生存能力，或增加成本"
        elif deviation > 1:
            balance_status = "略强"
            recommendation = "建议小幅降低战斗属性或小幅增加成本"
        elif deviation < -2:
            balance_status = "过弱"
            recommendation = "建议提升DPS或生存能力，或降低成本"
        else:
            balance_status = "略弱"
            recommendation = "建议小幅提升战斗属性或小幅降低成本"
        
        return {
            "status": balance_status,
            "deviation": f"{deviation:.2f}σ",
            "recommendation": recommendation
        }


def main():
    """生成基准数据的主函数"""
    # 调用新的精英单位基准系统
    from src.analysis.elite_units_benchmark import EliteUnitsBenchmark
    
    print("=== 运行五大精英单位基准评估系统 ===\n")
    elite_benchmark = EliteUnitsBenchmark()
    elite_benchmark.run()
    
    print("\n基准评估完成！")


if __name__ == "__main__":
    main()