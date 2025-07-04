#!/usr/bin/env python3
"""
新单位快速评估工具
用于将新设计的单位与官方单位基准进行对标
"""

import sys
import json
from src.analysis.benchmark_system_v2 import BenchmarkSystemV2
from src.core.enhanced_cev_calculator import EnhancedCEVCalculator

def main():
    """交互式新单位评估"""
    print("=== 星际争霸II新单位评估工具 ===\n")
    
    # 加载基准系统
    benchmark = BenchmarkSystemV2(
        "experiments/results/unit_eval/2025-07-02/21-38-04_五大精英单位对比排名_483fb4cf/data/processed/unit_evaluation_results.csv"
    )
    
    # 加载基准统计数据
    with open('benchmarks/benchmark_summary.json', 'r', encoding='utf-8') as f:
        summary = json.load(f)
    
    print("官方单位CEV基准数据：")
    print(f"- 平均值: {summary['cev_statistics']['mean']:.2f}")
    print(f"- 标准差: {summary['cev_statistics']['std']:.2f}")
    print(f"- 范围: {summary['cev_statistics']['min']:.2f} - {summary['cev_statistics']['max']:.2f}")
    print(f"- 中位数: {summary['cev_statistics']['quartiles']['50%']:.2f}\n")
    
    # 获取新单位数据
    print("请输入新单位的数据：")
    
    try:
        unit_name = input("单位名称: ")
        hp = float(input("生命值 (HP): "))
        shield = float(input("护盾值 (Shield，没有则输入0): "))
        armor = float(input("护甲值 (Armor): "))
        dps = float(input("每秒伤害 (DPS): "))
        mineral_cost = float(input("矿物成本: "))
        gas_cost = float(input("瓦斯成本: "))
        supply_cost = float(input("人口成本: "))
        
        # 计算衍生指标
        calculator = EnhancedCEVCalculator()
        
        # 计算有效生命值
        effective_hp = calculator._calculate_effective_hp(hp, shield, armor)
        
        # 计算有效成本（中期游戏，t=300）
        lambda_300 = calculator._calculate_time_factor(300)
        effective_cost = calculator._calculate_effective_cost(
            mineral_cost, gas_cost, supply_cost, lambda_300
        )
        
        # 计算CEV
        cev = (dps * effective_hp) / effective_cost
        
        print(f"\n=== {unit_name} 评估结果 ===")
        print(f"有效生命值: {effective_hp:.2f}")
        print(f"有效成本: {effective_cost:.2f}")
        print(f"CEV值: {cev:.2f}")
        
        # 使用基准系统评估
        new_unit_stats = {
            "cev": cev,
            "effective_dps": dps,
            "effective_hp": effective_hp,
            "effective_cost": effective_cost
        }
        
        evaluation = benchmark.evaluate_new_unit(new_unit_stats)
        
        print(f"\n百分位排名:")
        print(f"- CEV百分位: {evaluation['cev_percentile']:.1f}% (超过了{evaluation['cev_percentile']:.1f}%的官方单位)")
        print(f"- DPS百分位: {evaluation['dps_percentile']:.1f}%")
        print(f"- 生存百分位: {evaluation['survivability_percentile']:.1f}%")
        
        print(f"\n平衡性评估:")
        print(f"- 状态: {evaluation['balance_assessment']['status']}")
        print(f"- 偏差: {evaluation['balance_assessment']['deviation']}")
        print(f"- 建议: {evaluation['balance_assessment']['recommendation']}")
        
        print(f"\n最相似的官方单位:")
        for i, similar in enumerate(evaluation['similar_units'][:3], 1):
            print(f"{i}. {similar['unit_name']} ({similar['commander']}) - CEV: {similar['cev']:.2f}")
        
        # 保存评估结果
        save_option = input("\n是否保存评估结果？(y/n): ")
        if save_option.lower() == 'y':
            result = {
                "unit_name": unit_name,
                "stats": {
                    "hp": hp,
                    "shield": shield,
                    "armor": armor,
                    "dps": dps,
                    "mineral_cost": mineral_cost,
                    "gas_cost": gas_cost,
                    "supply_cost": supply_cost
                },
                "calculated": {
                    "effective_hp": effective_hp,
                    "effective_cost": effective_cost,
                    "cev": cev
                },
                "evaluation": evaluation
            }
            
            filename = f"benchmarks/new_unit_evaluations/{unit_name.replace(' ', '_')}_evaluation.json"
            import os
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"评估结果已保存到: {filename}")
            
    except ValueError as e:
        print(f"输入错误: {e}")
        return
    except KeyboardInterrupt:
        print("\n评估已取消")
        return


if __name__ == "__main__":
    main()