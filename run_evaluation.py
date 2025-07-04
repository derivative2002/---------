#!/usr/bin/env python3
"""
星际争霸II单位评估系统主程序
运行完整的评估流程
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.analysis.comprehensive_evaluator import ComprehensiveEvaluator
from src.core.cev_calculator import CEVCalculator, UnitParameters
from src.core.cem_visualizer import CEMVisualizer
from src.data.data_processor import DataProcessor
import matplotlib.pyplot as plt
import pandas as pd


def main():
    print("=== 星际争霸II单位评估系统 v2.1 ===\n")
    
    # 初始化评估器
    evaluator = ComprehensiveEvaluator()
    data_processor = DataProcessor()
    cem_visualizer = CEMVisualizer()
    
    # 1. 处理Excel数据
    print("1. 正在加载和处理单位数据...")
    units_data = data_processor.process_all_units()
    print(f"   成功加载 {len(units_data)} 个单位数据\n")
    
    # 2. 生成数据摘要
    print("2. 数据统计摘要:")
    summary = data_processor.get_unit_summary_stats(units_data)
    print(f"   - 平均矿物成本: {summary['cost_stats']['avg_mineral']:.1f}")
    print(f"   - 平均瓦斯成本: {summary['cost_stats']['avg_gas']:.1f}")
    print(f"   - 平均DPS: {summary['combat_stats']['avg_dps']:.1f}")
    print(f"   - 最高性价比单位: {summary['efficiency_stats']['best_dps_per_cost']}\n")
    
    # 3. 导出处理后的数据
    output_dir = Path("data/processed")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    print("3. 导出标准化数据...")
    data_processor.export_to_csv(units_data, str(output_dir / "units_standardized.csv"))
    data_processor.export_to_json(units_data, str(output_dir / "units_standardized.json"))
    
    # 4. 创建示例CEV计算
    print("\n4. 示例CEV计算:")
    example_units = [
        UnitParameters(
            name="陆战队员",
            commander="吉姆·雷诺",
            mineral_cost=45,
            gas_cost=0,
            supply_cost=1,
            base_dps=9.8,
            hp=55,
            armor=0,
            range=5,
            upgrades={"步兵武器": 3, "步兵装甲": 3}
        ),
        UnitParameters(
            name="升格者",
            commander="阿拉纳克",
            mineral_cost=250,
            gas_cost=150,
            supply_cost=4,
            base_dps=25,
            hp=200,
            shields=100,
            range=7,
            abilities=["心灵风暴", "牺牲"]
        ),
        UnitParameters(
            name="攻城坦克",
            commander="吉姆·雷诺",
            mineral_cost=150,
            gas_cost=125,
            supply_cost=3,
            base_dps=35,
            hp=200,
            armor=1,
            range=13,
            abilities=["攻城模式"]
        )
    ]
    
    cev_calculator = CEVCalculator()
    
    # 不同游戏阶段的CEV比较
    for phase, time_sec in [("早期", 180), ("中期", 600), ("后期", 1200)]:
        print(f"\n   {phase}游戏 ({time_sec//60}分钟):")
        results = cev_calculator.compare_units(example_units, time_seconds=time_sec)
        for i, result in enumerate(results[:3]):
            print(f"   {i+1}. {result['unit_name']}: CEV={result['cev']:.2f}, "
                  f"成本={result['effective_cost']:.1f}")
    
    # 5. 创建CEM可视化
    print("\n5. 生成战斗效能矩阵 (CEM)...")
    
    # 选择要显示的单位
    display_units = [
        "陆战队员", "掠夺者", "攻城坦克",
        "跳虫", "刺蛇", "雷兽",
        "狂热者", "追猎者", "不朽者"
    ]
    
    # 创建并保存CEM热图
    output_dir = Path("data/results")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    fig_cem = cem_visualizer.create_cem_heatmap(
        display_units,
        title="星际争霸II 单位战斗效能矩阵",
        save_path=str(output_dir / "cem_heatmap.png")
    )
    print("   CEM热图已保存到: data/results/cem_heatmap.png")
    
    # 6. 单位对战分析
    print("\n6. 生成单位对战分析...")
    fig_matchup = cem_visualizer.create_unit_matchup_chart("陆战队员", top_n=8)
    if fig_matchup:
        fig_matchup.savefig(str(output_dir / "marine_matchup.png"), dpi=300, bbox_inches='tight')
        print("   陆战队员对战分析已保存到: data/results/marine_matchup.png")
    
    # 7. 生成评估报告示例
    print("\n7. 生成单位评估仪表板...")
    
    # 创建测试单位数据
    test_unit_data = {
        "name": "攻城坦克",
        "commander": "吉姆·雷诺", 
        "mineral_cost": 150,
        "gas_cost": 125,
        "supply_cost": 3,
        "base_dps": 35,
        "hp": 200,
        "armor": 1,
        "range": 13,
        "speed": 2.25,
        "abilities": ["攻城模式", "区域伤害"],
        "upgrades": {"车辆武器": 3, "车辆装甲": 3}
    }
    
    evaluator.create_evaluation_dashboard(
        "攻城坦克", 
        "吉姆·雷诺",
        save_path=str(output_dir / "siege_tank_dashboard.png")
    )
    print("   攻城坦克评估仪表板已保存到: data/results/siege_tank_dashboard.png")
    
    # 8. 生成平衡性报告
    print("\n8. 生成游戏平衡性报告...")
    balance_report = evaluator.generate_balance_report(
        save_path=str(output_dir / "balance_report.json")
    )
    print("   平衡性报告已保存到: data/results/balance_report.json")
    
    print("\n=== 评估完成！===")
    print(f"所有结果已保存到 data/ 目录下")
    print("- processed/: 标准化的单位数据")
    print("- results/: 分析结果和可视化图表")
    
    # 显示所有图表
    plt.show()


if __name__ == "__main__":
    main()