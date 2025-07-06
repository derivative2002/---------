#!/usr/bin/env python3
"""
v2.4 精英单位评估主程序
用于评估六大精英单位的CEV值
"""

import logging
from pathlib import Path
import pandas as pd
from typing import Dict, List, Any
import json

from src.data.yaml_loader import YAMLDataLoader
from src.core.cev_calculator_v24 import CEVCalculatorV24, CalculationConfig


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def create_calculation_config() -> CalculationConfig:
    """创建计算配置"""
    return CalculationConfig(
        # 矿气转换率（默认值）
        mineral_gas_ratio=2.5,
        
        # 溅射系数配置
        splash_factors={
            "Liberator_AA": 1.0,    # 对空模式无溅射
            "Liberator_AG": 1.0,    # 对地模式也是单体
            "SiegeTank": 1.4,       # 攻城坦克溅射加成
            "Wrathwalker": 1.0,     # 天罚行者单体
            "Impaler": 1.0,         # 穿刺者单体
            "Dragoon": 1.0,         # 龙骑士单体
            "default": 1.0
        },
        
        # 操作难度系数
        operation_factors={
            "Wrathwalker": 1.3,          # 可移动射击
            "ColossusTaldarim": 1.3,     # 天罚行者（内部ID）
            "Liberator": 0.75,           # 需要架设
            "Liberator_AG": 0.75,        # AG模式需要架设
            "SiegeTank": 0.8,            # 简单架设
            "Impaler": 0.8,              # 简单潜地
            "Dragoon": 1.0,              # 标准操作
            "default": 1.0
        },
        
        # 过量击杀阈值 (伤害阈值, 惩罚系数)
        overkill_thresholds=[
            (200, 0.8),
            (150, 0.85),
            (100, 0.9),
            (0, 1.0)
        ],
        
        # 精通配置
        mastery_config={
            "Nova": {"attack_speed": 0.15},      # 15%攻速
            "Alarak": {"attack_speed": 0.15},    # 15%攻速
            "Swann": {"mech_life": 0.30},        # 30%机械生命值
            "Dehaka": {},
            "Artanis": {}
        }
    )


def evaluate_elite_units(calculator: CEVCalculatorV24) -> List[Dict[str, Any]]:
    """评估六大精英单位"""
    results = []
    
    # 定义要评估的单位和场景
    # (unit_id, weapon_mode, display_name, scenarios_to_run)
    units_to_evaluate = [
        ("Liberator_BlackOps", "AG", "掠袭解放者", ["standard"]),
        ("ColossusTaldarim", "upgraded", "普通天罚行者(快充)", ["standard"]),
        ("ColossusTaldarim", "base", "普通天罚行者(无升级)", ["standard"]),
        ("ColossusTaldarim_SoulArtificer", None, "灵魂巧匠天罚行者", ["standard"]),
        ("ImpalerDehaka", None, "穿刺者", ["standard", "vs_armored"]),
        ("SiegeTank", "siege", "攻城坦克", ["standard", "vs_armored"]),
        # 龙骑士待添加
    ]
    
    for unit_id, weapon_mode, display_name_base, scenarios in units_to_evaluate:
        for scenario in scenarios:
            try:
                # 计算CEV
                result = calculator.calculate_cev(
                    unit_id=unit_id,
                    weapon_mode=weapon_mode,
                    apply_mastery=True,
                    scenario=scenario
                )
                
                # 创建唯一的显示名称
                display_name = display_name_base
                if scenario != "standard":
                    scenario_map = {"vs_armored": "对重甲", "vs_light": "对轻甲"}
                    display_name += f" ({scenario_map.get(scenario, scenario)})"

                result["display_name"] = display_name
                results.append(result)
                
                # 打印结果
                print(f"\n{display_name}:")
                print(f"  CEV: {result['cev']}")
                print(f"  CEV/Pop: {result['cev_per_pop']}")
                print(f"  指挥官: {result['commander']}")
                print(f"  场景: {result['scenario']}")
                # print(f"  详细参数: {result['components']}")
                
            except Exception as e:
                print(f"评估 {display_name_base} (场景: {scenario}) 时出错: {e}")
            
    return results


def create_ranking_table(results: List[Dict[str, Any]]) -> pd.DataFrame:
    """创建排名表"""
    # 按CEV排序
    sorted_results = sorted(results, key=lambda x: x['cev'], reverse=True)
    
    # 创建表格数据
    table_data = []
    for i, result in enumerate(sorted_results, 1):
        table_data.append({
            "排名": i,
            "单位名称": result['display_name'],
            "指挥官": result['commander'],
            "场景": result['scenario'],
            "资源效率(CEV)": result['cev'],
            "人口效率(CEV/Pop)": result['cev_per_pop'],
            "DPS_eff": result['components']['dps_eff'],
            "EHP": result['components']['ehp'],
        })
    
    return pd.DataFrame(table_data)


def save_results(results: List[Dict[str, Any]], output_dir: Path):
    """保存结果"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存JSON格式
    with open(output_dir / "v24_elite_units_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 创建并保存排名表
    df = create_ranking_table(results)
    df.to_csv(output_dir / "v24_elite_units_ranking.csv", index=False, encoding="utf-8")
    
    # 保存Markdown格式
    with open(output_dir / "v24_elite_units_ranking.md", "w", encoding="utf-8") as f:
        f.write("# v2.4 六大精英单位CEV排名\n\n")
        f.write(df.to_markdown(index=False))
        f.write("\n\n## 详细计算结果\n\n")
        
        for result in sorted(results, key=lambda x: x['cev'], reverse=True):
            f.write(f"### {result['display_name']}\n")
            f.write(f"- **CEV**: {result['cev']}\n")
            f.write(f"- **CEV/Pop**: {result['cev_per_pop']}\n")
            f.write(f"- **指挥官**: {result['commander']}\n")
            f.write(f"- **计算参数**:\n")
            for key, value in result['components'].items():
                f.write(f"  - {key}: {value}\n")
            f.write("\n")


def main():
    """主函数"""
    setup_logging()
    
    print("=== v2.4 精英单位CEV评估 ===\n")
    
    # 加载数据
    print("加载数据...")
    loader = YAMLDataLoader()
    loader.load_all()
    
    # 创建计算器
    config = create_calculation_config()
    calculator = CEVCalculatorV24(loader, config)
    
    # 评估单位
    print("\n开始评估...")
    results = evaluate_elite_units(calculator)
    
    # 保存结果
    output_dir = Path("output/v24_evaluation")
    save_results(results, output_dir)
    
    # 显示排名表
    print("\n=== 最终排名 ===")
    df = create_ranking_table(results)
    print(df.to_string(index=False))
    
    print(f"\n结果已保存到: {output_dir}")


if __name__ == "__main__":
    main() 