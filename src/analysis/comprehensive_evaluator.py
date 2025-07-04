"""
综合评估系统
整合CEV计算、CEM可视化和数据处理的完整评估流程
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
import matplotlib.pyplot as plt
from datetime import datetime

from src.core.cev_calculator import CEVCalculator, UnitParameters
from src.core.cem_visualizer import CEMVisualizer
from src.data.data_processor import DataProcessor
from src.data.csv_data_loader import CSVDataLoader
from src.core.enhanced_cev_calculator import EnhancedCEVCalculator
from ..data.models import Unit


class ComprehensiveEvaluator:
    """综合评估系统"""
    
    def __init__(self, data_dir: str):
        self.calculator = EnhancedCEVCalculator(data_dir=data_dir)
        self.database = self.calculator.database
        self.cev_calculator = CEVCalculator()
        self.cem_visualizer = CEMVisualizer()
        self.data_processor = DataProcessor()
        self.csv_loader = CSVDataLoader()
        
        # 评估权重配置
        self.evaluation_weights = {
            "early_game": {
                "resource_efficiency": 0.6,
                "combat_power": 0.3,
                "versatility": 0.1
            },
            "mid_game": {
                "resource_efficiency": 0.4,
                "combat_power": 0.4,
                "versatility": 0.2
            },
            "late_game": {
                "resource_efficiency": 0.2,
                "combat_power": 0.5,
                "versatility": 0.3
            }
        }
        
        # 场景时间定义（秒）
        self.game_phases = {
            "early_game": 180,   # 3分钟
            "mid_game": 600,     # 10分钟
            "late_game": 1200    # 20分钟
        }
    
    def convert_to_unit_parameters(self, unit_data: Any) -> Dict:
        """将任意单位数据格式转换为标准评估字典"""
        if isinstance(unit_data, Unit):
            # 从Unit对象转换
            return {
                'name': unit_data.chinese_name,
                'commander': unit_data.commander,
                'unit_obj': unit_data
            }
        elif isinstance(unit_data, dict):
            # 从旧的字典格式转换
            # (保留以兼容旧代码)
            return {
                'name': unit_data.get('name') or unit_data.get('chinese_name'),
                'commander': unit_data.get('commander'),
                'raw_data': unit_data
            }
        else:
            raise TypeError(f"不支持的单位数据类型: {type(unit_data)}")
    
    def evaluate_single_unit(self, 
                           unit_data: Any,
                           game_phase: str = 'mid_game',
                           context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        评估单个单位的综合表现
        """
        params = self.convert_to_unit_parameters(unit_data)
        
        # 从数据库获取完整的Unit对象
        unit_obj = params.get('unit_obj')
        if not unit_obj:
            # 如果传入的是旧格式，需要从数据库查找
            unit_id = f"{params['commander']}_{params['name']}" # 这是一个猜测，可能需要调整
            found_unit = next((u for u in self.database.units.values() 
                               if u.chinese_name == params['name'] and u.commander == params['commander']), None)
            if not found_unit:
                return {'error': f"找不到单位: {params['name']}"}
            unit_obj = found_unit

        time_map = {
            'early_game': 180,
            'mid_game': 600,
            'late_game': 1200
        }
        time_seconds = time_map.get(game_phase, 600)

        # CEV 计算
        cev_result = self.calculator.calculate_cev(
            unit=unit_obj,
            time_seconds=time_seconds,
            **context
        )

        # 综合评分
        score_result = self._calculate_overall_score(
            unit=unit_obj,
            cev_result=cev_result,
            game_phase=game_phase
        )

        return {
            'unit_name': unit_obj.chinese_name,
            'english_id': unit_obj.english_id,
            'commander': unit_obj.commander,
            **cev_result,
            **score_result
        }
    
    def _calculate_overall_score(self, unit: Unit, cev_result: Dict, game_phase: str) -> Dict:
        """计算单位的综合评分"""
        
        weights = {
            'early_game': {'cev': 0.4, 'resource_efficiency': 0.5, 'versatility': 0.1},
            'mid_game':   {'cev': 0.5, 'resource_efficiency': 0.3, 'versatility': 0.2},
            'late_game':  {'cev': 0.6, 'resource_efficiency': 0.2, 'versatility': 0.2}
        }
        
        phase_weights = weights.get(game_phase, weights['mid_game'])
        
        # 资源效率
        resource_efficiency = cev_result.get('resource_efficiency', 0)
        
        # 多功能性 (直接调用计算器中的私有方法)
        range_score = self.calculator._calculate_range_score(unit) if hasattr(self.calculator, '_calculate_range_score') else 0
        mobility_score = self.calculator._calculate_mobility_score(unit) if hasattr(self.calculator, '_calculate_mobility_score') else 0
        versatility = (range_score + mobility_score) / 2
        
        # 计算综合分
        overall_score = (
            phase_weights['cev'] * cev_result.get('cev', 0) * 0.1 +  # 缩放CEV
            phase_weights['resource_efficiency'] * resource_efficiency * 100 +
            phase_weights['versatility'] * versatility * 100
        )
        
        return {
            'overall_score': overall_score,
            'resource_efficiency': resource_efficiency,
            'versatility_score': versatility
        }
    
    def evaluate_commander_roster(self, 
                                commander: str,
                                units_list: List[Dict] = None) -> pd.DataFrame:
        """评估指挥官的所有单位"""
        if units_list is None:
            # 从数据处理器获取该指挥官的所有单位
            all_units = self.data_processor.process_all_units(commander)
            units_list = [u for u in all_units if u['commander'] == commander]
        
        evaluations = []
        
        # 对每个游戏阶段进行评估
        for phase in ["early_game", "mid_game", "late_game"]:
            for unit in units_list:
                eval_result = self.evaluate_single_unit(unit, phase)
                evaluations.append(eval_result)
        
        # 转换为DataFrame
        df = pd.DataFrame(evaluations)
        
        # 添加排名
        for phase in ["early_game", "mid_game", "late_game"]:
            phase_mask = df['game_phase'] == phase
            df.loc[phase_mask, 'phase_rank'] = df.loc[phase_mask, 'overall_score'].rank(
                ascending=False, method='min'
            )
        
        return df
    
    def generate_unit_report(self, unit_name: str, commander: str) -> Dict:
        """生成单位详细报告"""
        # 获取单位数据
        all_units = self.data_processor.process_all_units(commander)
        unit_data = next((u for u in all_units if u['name'] == unit_name), None)
        
        if not unit_data:
            return {"error": f"未找到单位: {unit_name}"}
        
        report = {
            "unit_info": unit_data,
            "phase_evaluations": {},
            "matchup_analysis": {},
            "recommendations": []
        }
        
        # 各阶段评估
        for phase in ["early_game", "mid_game", "late_game"]:
            eval_result = self.evaluate_single_unit(unit_data, phase)
            report["phase_evaluations"][phase] = eval_result
        
        # 对战分析
        # 这里可以集成CEM可视化的结果
        
        # 生成建议
        evaluations = report["phase_evaluations"]
        
        # 分析强势期
        best_phase = max(evaluations.items(), 
                        key=lambda x: x[1]["overall_score"])[0]
        report["recommendations"].append(
            f"该单位在{best_phase}表现最佳，建议优先在该时期使用"
        )
        
        # 分析弱点
        if evaluations["late_game"]["supply_efficiency"] < 10:
            report["recommendations"].append(
                "后期人口效率较低，建议配合高价值单位使用"
            )
        
        if unit_data["range"] < 5:
            report["recommendations"].append(
                "射程较短，需要良好的微操或掩护单位"
            )
        
        return report
    
    def compare_commanders(self, commanders: List[str]) -> pd.DataFrame:
        """比较多个指挥官的整体实力"""
        commander_stats = []
        
        for commander in commanders:
            # 获取该指挥官的所有单位
            units = self.data_processor.process_all_units(commander)
            commander_units = [u for u in units if u['commander'] == commander]
            
            if not commander_units:
                continue
            
            # 评估所有单位
            df_eval = self.evaluate_commander_roster(commander, commander_units)
            
            # 计算统计指标
            stats = {
                "commander": commander,
                "unit_count": len(commander_units),
                
                # 各阶段平均得分
                "early_avg_score": df_eval[df_eval['game_phase'] == 'early_game']['overall_score'].mean(),
                "mid_avg_score": df_eval[df_eval['game_phase'] == 'mid_game']['overall_score'].mean(),
                "late_avg_score": df_eval[df_eval['game_phase'] == 'late_game']['overall_score'].mean(),
                
                # 最强单位
                "best_early_unit": df_eval[df_eval['game_phase'] == 'early_game'].nlargest(1, 'overall_score')['unit_name'].values[0],
                "best_late_unit": df_eval[df_eval['game_phase'] == 'late_game'].nlargest(1, 'overall_score')['unit_name'].values[0],
                
                # 多样性指标
                "avg_range": np.mean([u['range'] for u in commander_units]),
                "has_air": any('飞行' in u.get('abilities', []) for u in commander_units),
                "has_stealth": any('隐形' in u.get('abilities', []) for u in commander_units),
                
                # 经济效率
                "avg_cost": np.mean([u['equivalent_cost'] for u in commander_units]),
                "avg_supply": np.mean([u['supply_cost'] for u in commander_units])
            }
            
            commander_stats.append(stats)
        
        return pd.DataFrame(commander_stats)
    
    def generate_balance_report(self, 
                              save_path: Optional[str] = None) -> Dict:
        """生成游戏平衡性报告"""
        report = {
            "generation_time": datetime.now().isoformat(),
            "summary": {},
            "commander_analysis": {},
            "unit_rankings": {},
            "balance_issues": [],
            "recommendations": []
        }
        
        # 获取所有指挥官
        commanders = list(self.cev_calculator.commander_modifiers.keys())
        commanders.remove("默认")
        
        # 比较指挥官
        commander_comparison = self.compare_commanders(commanders[:5])  # 示例：前5个
        report["commander_analysis"] = commander_comparison.to_dict()
        
        # 识别平衡性问题
        if len(commander_comparison) > 0:
            # 检查指挥官间的差异
            score_std = commander_comparison[['early_avg_score', 'mid_avg_score', 'late_avg_score']].std()
            
            for phase, std in score_std.items():
                if std > 20:  # 阈值
                    report["balance_issues"].append(
                        f"{phase}阶段指挥官实力差异过大 (标准差: {std:.1f})"
                    )
        
        # 生成建议
        report["recommendations"] = [
            "考虑加强表现较差的指挥官的独特机制",
            "平衡高人口效率单位的其他属性",
            "确保每个指挥官在至少一个游戏阶段有竞争力"
        ]
        
        # 保存报告
        if save_path:
            import json
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report
    
    def create_evaluation_dashboard(self, 
                                  unit_name: str,
                                  commander: str,
                                  save_path: Optional[str] = None):
        """创建单位评估仪表板"""
        # 获取单位报告
        report = self.generate_unit_report(unit_name, commander)
        
        if "error" in report:
            print(report["error"])
            return
        
        # 创建图表
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'{unit_name} ({commander}) 综合评估报告', fontsize=16)
        
        # 1. 各阶段得分
        ax1 = axes[0, 0]
        phases = list(report["phase_evaluations"].keys())
        scores = [report["phase_evaluations"][p]["overall_score"] for p in phases]
        
        ax1.bar(phases, scores, color=['green', 'blue', 'red'])
        ax1.set_title('各游戏阶段综合得分')
        ax1.set_ylabel('综合得分')
        
        # 2. 效率指标雷达图
        ax2 = axes[0, 1]
        categories = ['资源效率', '人口效率', '生存能力', '射程优势', '机动性']
        
        mid_eval = report["phase_evaluations"]["mid_game"]
        values = [
            mid_eval["resource_efficiency"] * 10,
            mid_eval["supply_efficiency"],
            mid_eval["survivability"] * 10,
            mid_eval["range_advantage"] * 10,
            mid_eval["mobility"] * 10
        ]
        
        # 雷达图
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]
        
        ax2.plot(angles, values, 'o-', linewidth=2)
        ax2.fill(angles, values, alpha=0.25)
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(categories)
        ax2.set_title('中期游戏效率指标')
        
        # 3. 成本效益分析
        ax3 = axes[1, 0]
        phases_data = report["phase_evaluations"]
        
        x = [phases_data[p]["effective_cost"] for p in phases]
        y = [phases_data[p]["cev"] for p in phases]
        
        ax3.scatter(x, y, s=100)
        for i, phase in enumerate(phases):
            ax3.annotate(phase, (x[i], y[i]), xytext=(5, 5), 
                        textcoords='offset points')
        
        ax3.set_xlabel('有效成本')
        ax3.set_ylabel('战斗效能值 (CEV)')
        ax3.set_title('成本-效能分析')
        ax3.grid(True, alpha=0.3)
        
        # 4. 建议文本
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        recommendations_text = "使用建议:\n\n"
        for i, rec in enumerate(report["recommendations"], 1):
            recommendations_text += f"{i}. {rec}\n\n"
        
        ax4.text(0.1, 0.9, recommendations_text, transform=ax4.transAxes,
                fontsize=11, verticalalignment='top', wrap=True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()


# 使用示例
if __name__ == "__main__":
    evaluator = ComprehensiveEvaluator(data_dir="path_to_data_directory")
    
    # 示例1: 评估单个单位
    print("=== 单位评估示例 ===")
    test_unit = {
        "name": "升格者",
        "commander": "阿拉纳克",
        "mineral_cost": 250,
        "gas_cost": 150,
        "supply_cost": 4,
        "base_dps": 25,
        "hp": 200,
        "shields": 100,
        "armor": 1,
        "range": 7,
        "speed": 2.25,
        "abilities": ["心灵风暴", "牺牲"],
        "upgrades": {"灵能攻击": 3}
    }
    
    eval_result = evaluator.evaluate_single_unit(test_unit, "late_game")
    print(f"{test_unit['name']} 后期评分: {eval_result['overall_score']:.2f}")
    print(f"  - CEV: {eval_result['cev']:.2f}")
    print(f"  - 资源效率: {eval_result['resource_efficiency']:.3f}")
    
    # 示例2: 生成单位报告
    print("\n=== 生成单位详细报告 ===")
    # 这里需要实际的单位数据，示例中使用测试数据
    
    # 示例3: 创建评估仪表板
    print("\n=== 创建评估仪表板 ===")
    # evaluator.create_evaluation_dashboard("升格者", "阿拉纳克")