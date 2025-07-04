"""
实验运行器
执行不同类型的实验并管理输出
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import json
import yaml
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import traceback

from src.experiment.experiment_manager import (
    ExperimentManager, ExperimentConfig, ExperimentType
)
from src.analysis.comprehensive_evaluator import ComprehensiveEvaluator
from src.core.cev_calculator import CEVCalculator, UnitParameters
from src.core.cem_visualizer import CEMVisualizer
from src.data.data_processor import DataProcessor
from src.data.advanced_data_loader import AdvancedDataLoader


class ExperimentRunner:
    """实验运行器"""
    
    def __init__(self, exp_manager: Optional[ExperimentManager] = None):
        self.exp_manager = exp_manager if exp_manager else ExperimentManager()
        self.current_exp_dir = None
        
        # 使用新的数据加载器
        self.loader = AdvancedDataLoader()
        self.evaluator = ComprehensiveEvaluator(data_dir="data/units")
        
        # 保留旧的，以防万一
        self.data_processor = DataProcessor()
        self.cev_calculator = CEVCalculator()
        self.cem_visualizer = CEMVisualizer()
        
        # 注册实验类型处理器
        self.experiment_handlers = {
            ExperimentType.UNIT_EVALUATION: self._run_unit_evaluation,
            ExperimentType.COMMANDER_COMPARISON: self._run_commander_comparison,
            ExperimentType.BALANCE_ANALYSIS: self._run_balance_analysis,
            ExperimentType.CEM_VISUALIZATION: self._run_cem_visualization,
            ExperimentType.PARAMETER_SWEEP: self._run_parameter_sweep,
            ExperimentType.SYNERGY_ANALYSIS: self._run_synergy_analysis,
            ExperimentType.META_ANALYSIS: self._run_meta_analysis
        }
        
        # 设置matplotlib
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
        plt.rcParams['axes.unicode_minus'] = False
    
    def run_experiment(self, config: ExperimentConfig, 
                      exp_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        运行实验
        
        参数:
            config: 实验配置
            exp_dir: 实验目录（如果为None则自动创建）
            
        返回:
            实验结果字典
        """
        # 创建或使用实验目录
        if exp_dir is None:
            exp_dir = self.exp_manager.create_experiment_dir(config)
        
        self.current_exp_dir = exp_dir
        
        # 更新状态为运行中
        self.exp_manager.update_experiment_status(exp_dir, 'running')
        
        try:
            # 记录开始时间
            start_time = datetime.now()
            
            # 运行对应类型的实验
            handler = self.experiment_handlers.get(config.type)
            if handler is None:
                raise ValueError(f"未知的实验类型: {config.type}")
            
            # 执行实验
            results = handler(config, exp_dir)
            
            # 记录结束时间和耗时
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            results['meta'] = {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'success': True
            }
            
            # 保存结果
            self.exp_manager.save_experiment_results(exp_dir, results)
            
            # 生成报告
            if config.generate_report:
                self.exp_manager.create_experiment_report(exp_dir)
            
            self.exp_manager.logger.info(
                f"实验完成: {config.name} (耗时: {duration:.2f}秒)"
            )
            
        except Exception as e:
            # 记录错误
            error_info = {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            }
            
            error_path = exp_dir / '.experiment' / 'error.json'
            with open(error_path, 'w', encoding='utf-8') as f:
                json.dump(error_info, f, indent=2, ensure_ascii=False)
            
            # 更新状态为失败
            self.exp_manager.update_experiment_status(exp_dir, 'failed')
            
            self.exp_manager.logger.error(
                f"实验失败: {config.name}\n{traceback.format_exc()}"
            )
            
            results = {
                'meta': {
                    'success': False,
                    'error': str(e)
                }
            }
        
        return results
    
    def _save_plot(self, fig: plt.Figure, name: str, subdir: str = "") -> Path:
        """保存图表到实验目录"""
        plot_dir = self.current_exp_dir / 'plots'
        if subdir:
            plot_dir = plot_dir / subdir
            plot_dir.mkdir(exist_ok=True)
        
        plot_path = plot_dir / f"{name}.png"
        fig.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        return plot_path
    
    def _save_data(self, data: Any, name: str, subdir: str = "processed") -> Path:
        """保存数据到实验目录"""
        data_dir = self.current_exp_dir / 'data' / subdir
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # 根据数据类型选择保存方式
        if isinstance(data, pd.DataFrame):
            data_path = data_dir / f"{name}.csv"
            data.to_csv(data_path, index=False, encoding='utf-8-sig')
        elif isinstance(data, dict):
            data_path = data_dir / f"{name}.json"
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            data_path = data_dir / f"{name}.txt"
            with open(data_path, 'w', encoding='utf-8') as f:
                f.write(str(data))
        
        return data_path
    
    def _run_unit_evaluation(self, config: ExperimentConfig, 
                           exp_dir: Path) -> Dict[str, Any]:
        """运行单位评估实验"""
        results = {
            'units_evaluated': [],
            'phase_rankings': {},
            'best_units': {}
        }
        
        # 加载单位数据
        database = self.loader.load_all_data()
        all_units_data = list(database.units.values())
        
        # 过滤指定的单位和指挥官
        if config.units:
            units_data = [u for u in all_units_data if u.english_id in config.units]
        else:
            units_data = all_units_data
            
        if config.commanders:
            units_data = [u for u in units_data if u.commander in config.commanders]
        
        # 评估每个单位在不同阶段的表现
        evaluation_results = []
        
        for unit_data in units_data:
            for phase in config.game_phases:
                eval_content = self.evaluator.evaluate_single_unit(
                    unit_data, 
                    game_phase=phase,
                    context={
                        'n_support': 2,
                        'n_ally': 15,
                        'army_composition': []
                    }
                )
                
                # 创建一个新的字典，确保game_phase存在
                full_result = {
                    'game_phase': phase,
                    **eval_content
                }
                evaluation_results.append(full_result)
        
        # 转换为DataFrame
        df_results = pd.DataFrame(evaluation_results)
        
        # 保存原始评估数据
        self._save_data(df_results, "unit_evaluation_results")
        
        # 分析结果
        for phase in config.game_phases:
            phase_data = df_results[df_results['game_phase'] == phase]
            
            # 排名
            phase_ranking = phase_data.nlargest(10, 'overall_score')[
                ['unit_name', 'commander', 'overall_score', 'cev', 'resource_efficiency']
            ].to_dict('records')
            
            results['phase_rankings'][phase] = phase_ranking
            
            # 最佳单位
            if not phase_data.empty:
                best_unit = phase_data.loc[phase_data['overall_score'].idxmax()]
                results['best_units'][phase] = {
                    'name': best_unit['unit_name'],
                    'commander': best_unit['commander'],
                    'score': best_unit['overall_score']
                }
        
        # 生成可视化
        if config.save_plots:
            # 1. 各阶段得分对比
            fig, ax = plt.subplots(figsize=(12, 8))
            
            for phase in config.game_phases:
                phase_data = df_results[df_results['game_phase'] == phase]
                top_units = phase_data.nlargest(10, 'overall_score')
                
                ax.scatter(top_units.index, top_units['overall_score'], 
                         label=phase, s=100, alpha=0.7)
            
            ax.set_xlabel('单位索引')
            ax.set_ylabel('综合得分')
            ax.set_title('单位在不同游戏阶段的表现')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            self._save_plot(fig, "phase_comparison")
            
            # 2. CEV vs 成本分析
            fig2, ax2 = plt.subplots(figsize=(10, 8))
            
            mid_game_data = df_results[df_results['game_phase'] == 'mid_game']
            
            scatter = ax2.scatter(
                mid_game_data['effective_cost'],
                mid_game_data['cev'],
                c=mid_game_data['overall_score'],
                cmap='viridis',
                s=100,
                alpha=0.7
            )
            
            # 添加单位标签
            for idx, row in mid_game_data.iterrows():
                if row['overall_score'] > mid_game_data['overall_score'].quantile(0.8):
                    ax2.annotate(
                        row['unit_name'][:10],
                        (row['effective_cost'], row['cev']),
                        xytext=(5, 5),
                        textcoords='offset points',
                        fontsize=8
                    )
            
            ax2.set_xlabel('有效成本')
            ax2.set_ylabel('战斗效能值 (CEV)')
            ax2.set_title('中期游戏: 成本-效能分析')
            plt.colorbar(scatter, label='综合得分')
            ax2.grid(True, alpha=0.3)
            
            self._save_plot(fig2, "cost_effectiveness_analysis")
        
        results['units_evaluated'] = list(df_results['unit_name'].unique())
        results['total_evaluations'] = len(evaluation_results)
        
        return results
    
    def _run_commander_comparison(self, config: ExperimentConfig, 
                                exp_dir: Path) -> Dict[str, Any]:
        """运行指挥官对比实验"""
        results = {
            'commanders_compared': config.commanders,
            'comparison_metrics': {},
            'rankings': {}
        }
        
        # 使用综合评估器比较指挥官
        comparison_df = self.evaluator.compare_commanders(config.commanders)
        
        # 保存比较数据
        self._save_data(comparison_df, "commander_comparison")
        
        # 分析结果
        results['comparison_metrics'] = comparison_df.to_dict('records')
        
        # 各阶段排名
        for phase in ['early', 'mid', 'late']:
            score_col = f'{phase}_avg_score'
            if score_col in comparison_df.columns:
                rankings = comparison_df.nlargest(len(config.commanders), score_col)[
                    ['commander', score_col]
                ].to_dict('records')
                results['rankings'][f'{phase}_game'] = rankings
        
        # 生成可视化
        if config.save_plots:
            # 指挥官得分雷达图
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
            
            # 准备数据
            categories = ['早期', '中期', '后期', '单位数量', '平均射程']
            
            for idx, commander in enumerate(config.commanders[:5]):  # 最多5个
                if commander in comparison_df['commander'].values:
                    cmd_data = comparison_df[comparison_df['commander'] == commander].iloc[0]
                    
                    values = [
                        cmd_data.get('early_avg_score', 0) / 100,
                        cmd_data.get('mid_avg_score', 0) / 100,
                        cmd_data.get('late_avg_score', 0) / 100,
                        cmd_data.get('unit_count', 0) / 20,
                        cmd_data.get('avg_range', 0) / 10
                    ]
                    
                    # 闭合图形
                    values += values[:1]
                    angles = [n / len(categories) * 2 * 3.14159 for n in range(len(categories))]
                    angles += angles[:1]
                    
                    ax.plot(angles, values, 'o-', linewidth=2, label=commander)
                    ax.fill(angles, values, alpha=0.15)
            
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)
            ax.set_ylim(0, 1)
            ax.set_title('指挥官能力对比雷达图', y=1.08)
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
            ax.grid(True)
            
            self._save_plot(fig, "commander_radar_chart")
        
        return results
    
    def _run_balance_analysis(self, config: ExperimentConfig, 
                            exp_dir: Path) -> Dict[str, Any]:
        """运行平衡性分析实验"""
        results = {
            'balance_report': {},
            'issues_found': [],
            'recommendations': []
        }
        
        # 生成平衡性报告
        balance_report = self.evaluator.generate_balance_report()
        
        # 保存报告
        self._save_data(balance_report, "balance_report")
        
        results['balance_report'] = balance_report
        results['issues_found'] = balance_report.get('balance_issues', [])
        results['recommendations'] = balance_report.get('recommendations', [])
        
        return results
    
    def _run_cem_visualization(self, config: ExperimentConfig, 
                             exp_dir: Path) -> Dict[str, Any]:
        """运行CEM可视化实验"""
        results = {
            'units_visualized': config.units,
            'matrices_generated': []
        }
        
        if config.save_plots:
            # 生成主CEM热图
            fig = self.cem_visualizer.create_cem_heatmap(
                config.units,
                title="战斗效能矩阵 (CEM)"
            )
            
            plot_path = self._save_plot(fig, "cem_heatmap")
            results['matrices_generated'].append(str(plot_path))
            
            # 为每个单位生成对战分析
            for unit in config.units[:5]:  # 最多5个
                fig = self.cem_visualizer.create_unit_matchup_chart(unit)
                if fig:
                    plot_path = self._save_plot(fig, f"matchup_{unit}", "matchups")
                    results['matrices_generated'].append(str(plot_path))
        
        # 导出CEM数据
        data_path = self.current_exp_dir / 'data' / 'processed' / 'cem_matrix.csv'
        self.cem_visualizer.export_cem_data(config.units, str(data_path))
        
        return results
    
    def _run_parameter_sweep(self, config: ExperimentConfig, 
                           exp_dir: Path) -> Dict[str, Any]:
        """运行参数扫描实验"""
        results = {
            'parameters_swept': [],
            'optimal_parameters': {},
            'sweep_results': []
        }
        
        # 参数扫描示例：人口压力因子的影响
        sweep_params = config.extra_params.get('sweep_params', {
            'lambda_k': [0.01, 0.05, 0.1],
            'lambda_t0': [180, 300, 600]
        })
        
        sweep_results = []
        
        # 保存原始参数
        original_k = self.cev_calculator.lambda_k
        original_t0 = self.cev_calculator.lambda_t0
        
        try:
            for k in sweep_params.get('lambda_k', [0.05]):
                for t0 in sweep_params.get('lambda_t0', [300]):
                    # 设置参数
                    self.cev_calculator.lambda_k = k
                    self.cev_calculator.lambda_t0 = t0
                    
                    # 评估示例单位
                    test_unit = UnitParameters(
                        name="测试单位",
                        commander="测试",
                        mineral_cost=100,
                        gas_cost=50,
                        supply_cost=2,
                        base_dps=20,
                        hp=150
                    )
                    
                    # 在不同时间点评估
                    for time in [180, 600, 1200]:
                        cev_result = self.cev_calculator.calculate_cev(
                            test_unit,
                            time_seconds=time
                        )
                        
                        sweep_results.append({
                            'lambda_k': k,
                            'lambda_t0': t0,
                            'time': time,
                            'lambda_value': cev_result['lambda_t'],
                            'cev': cev_result['cev'],
                            'effective_cost': cev_result['effective_cost']
                        })
        
        finally:
            # 恢复原始参数
            self.cev_calculator.lambda_k = original_k
            self.cev_calculator.lambda_t0 = original_t0
        
        # 保存扫描结果
        df_sweep = pd.DataFrame(sweep_results)
        self._save_data(df_sweep, "parameter_sweep_results")
        
        results['sweep_results'] = sweep_results
        results['parameters_swept'] = list(sweep_params.keys())
        
        # 找出最优参数（CEV变化最平滑的）
        # 这里简化为CEV标准差最小的参数组合
        param_groups = df_sweep.groupby(['lambda_k', 'lambda_t0'])
        optimal = param_groups['cev'].std().idxmin()
        
        results['optimal_parameters'] = {
            'lambda_k': optimal[0],
            'lambda_t0': optimal[1]
        }
        
        return results
    
    def _run_synergy_analysis(self, config: ExperimentConfig, 
                            exp_dir: Path) -> Dict[str, Any]:
        """运行协同效应分析实验"""
        results = {
            'synergies_analyzed': [],
            'synergy_scores': {}
        }
        
        # 分析指定的单位组合
        synergy_combinations = config.extra_params.get('synergy_combinations', [
            {
                'commander': '吉姆·雷诺',
                'units': ['陆战队员', '医疗兵', '攻城坦克'],
                'name': '经典人族组合'
            },
            {
                'commander': '阿拉纳克',
                'units': ['升格者', '虚空光晕', '末日降临者'],
                'name': '死亡舰队'
            }
        ])
        
        for combo in synergy_combinations:
            # 创建单位参数（简化）
            units = []
            for unit_name in combo['units']:
                units.append(UnitParameters(
                    name=unit_name,
                    commander=combo['commander'],
                    mineral_cost=200,
                    gas_cost=100,
                    supply_cost=3,
                    base_dps=25,
                    hp=200
                ))
            
            # 计算单独CEV和组合CEV
            individual_cevs = []
            for unit in units:
                cev_result = self.cev_calculator.calculate_cev(
                    unit,
                    time_seconds=600,
                    army_composition=[]
                )
                individual_cevs.append(cev_result['cev'])
            
            # 计算组合CEV（带协同效应）
            combined_cevs = []
            for unit in units:
                cev_result = self.cev_calculator.calculate_cev(
                    unit,
                    time_seconds=600,
                    n_support=len(units) - 1,
                    army_composition=combo['units']
                )
                combined_cevs.append(cev_result['cev'])
            
            # 计算协同系数
            synergy_score = sum(combined_cevs) / sum(individual_cevs)
            
            results['synergies_analyzed'].append(combo['name'])
            results['synergy_scores'][combo['name']] = {
                'units': combo['units'],
                'commander': combo['commander'],
                'individual_total': sum(individual_cevs),
                'combined_total': sum(combined_cevs),
                'synergy_multiplier': synergy_score
            }
        
        # 保存分析结果
        self._save_data(results['synergy_scores'], "synergy_analysis")
        
        return results
    
    def _run_meta_analysis(self, config: ExperimentConfig, 
                         exp_dir: Path) -> Dict[str, Any]:
        """运行元分析实验（分析其他实验的结果）"""
        results = {
            'experiments_analyzed': [],
            'meta_insights': []
        }
        
        # 获取要分析的实验
        target_exp_type = config.extra_params.get(
            'target_type', 
            ExperimentType.UNIT_EVALUATION
        )
        
        experiments = self.exp_manager.list_experiments(
            exp_type=target_exp_type,
            status='completed'
        )[:10]  # 最多分析10个
        
        # 比较实验结果
        if experiments:
            exp_dirs = [Path(exp['path']) for exp in experiments]
            comparison_df = self.exp_manager.compare_experiments(exp_dirs)
            
            # 保存比较结果
            self._save_data(comparison_df, "experiment_comparison")
            
            results['experiments_analyzed'] = [
                exp['name'] for exp in experiments
            ]
            
            # 生成洞察
            insights = []
            
            # 趋势分析
            if 'timestamp' in comparison_df.columns:
                insights.append(
                    f"分析了 {len(experiments)} 个{target_exp_type.value}实验"
                )
            
            results['meta_insights'] = insights
        
        return results


def run_batch_experiments(configs: List[ExperimentConfig]) -> pd.DataFrame:
    """批量运行实验"""
    runner = ExperimentRunner()
    results_summary = []
    
    for config in configs:
        print(f"\n运行实验: {config.name}")
        results = runner.run_experiment(config)
        
        results_summary.append({
            'name': config.name,
            'type': config.type.value,
            'success': results['meta'].get('success', False),
            'duration': results['meta'].get('duration_seconds', 0),
            'exp_dir': str(runner.current_exp_dir)
        })
    
    return pd.DataFrame(results_summary)


# 预定义实验模板
class ExperimentTemplates:
    """实验模板"""
    
    @staticmethod
    def unit_tier_list(commanders: List[str]) -> ExperimentConfig:
        """单位排行榜实验"""
        return ExperimentConfig(
            name=f"单位综合排行榜 - {','.join(commanders[:2])}等",
            type=ExperimentType.UNIT_EVALUATION,
            description="评估指定指挥官的所有单位并生成排行榜",
            commanders=commanders,
            units=[],  # 空列表表示评估所有单位
            game_phases=["early_game", "mid_game", "late_game"],
            save_plots=True,
            generate_report=True
        )
    
    @staticmethod
    def commander_balance_check(commanders: List[str]) -> ExperimentConfig:
        """指挥官平衡性检查"""
        return ExperimentConfig(
            name="指挥官平衡性分析",
            type=ExperimentType.COMMANDER_COMPARISON,
            description="比较多个指挥官的整体实力和特色",
            commanders=commanders,
            units=[],
            save_plots=True,
            generate_report=True
        )
    
    @staticmethod
    def unit_matchup_matrix(units: List[str]) -> ExperimentConfig:
        """单位对战矩阵"""
        return ExperimentConfig(
            name="单位克制关系矩阵",
            type=ExperimentType.CEM_VISUALIZATION,
            description="可视化单位间的克制关系",
            commanders=[],
            units=units,
            save_plots=True,
            generate_report=True
        )


# 使用示例
if __name__ == "__main__":
    # 创建实验配置
    config = ExperimentTemplates.unit_tier_list(
        commanders=["吉姆·雷诺", "阿拉纳克", "诺娃·泰拉"]
    )
    
    # 运行实验
    runner = ExperimentRunner()
    results = runner.run_experiment(config)
    
    print(f"\n实验完成!")
    print(f"成功: {results['meta']['success']}")
    print(f"耗时: {results['meta'].get('duration_seconds', 0):.2f}秒")