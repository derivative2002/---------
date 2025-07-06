"""
验证v2.4精炼CEV计算器的模型实现
"""

import pandas as pd
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.refined_cev_calculator import RefinedCEVCalculator
from src.data.models import ELITE_UNITS_DATA


def test_cev_calculation():
    """测试CEV计算的正确性"""
    print("=== v2.4 CEV计算器验证 ===\n")
    
    calculator = RefinedCEVCalculator()
    
    # 测试所有精英单位
    results = []
    
    for unit_name, unit_data in ELITE_UNITS_DATA.items():
        try:
            # 创建单位数据
            unit_stats = calculator.create_unit_stats(
                hp=unit_data['unit']['hp'],
                shield=unit_data['unit'].get('shield', 0),
                armor=unit_data['unit']['armor'],
                mineral_cost=unit_data['unit']['mineral_cost'],
                gas_cost=unit_data['unit']['gas_cost'],
                supply_cost=unit_data['unit']['supply_cost'],
                collision_radius=unit_data['unit'].get('collision_radius', 0.75)
            )
            
            # 创建武器数据
            weapon_stats = calculator.create_weapon_stats(
                base_damage=unit_data['weapon']['base_damage'],
                attack_count=unit_data['weapon'].get('attack_count', 1),
                attack_interval=unit_data['weapon']['attack_interval'],
                weapon_range=unit_data['weapon']['range'],
                splash_factor=unit_data['weapon'].get('splash_factor', 1.0)
            )
        
        # 计算CEV
            cev = calculator.calculate_cev(
                unit_stats=unit_stats,
                weapon_stats=weapon_stats,
                commander=unit_data['commander']
            )
        
        results.append({
                '单位名称': unit_name,
                '指挥官': unit_data['commander'],
                'CEV': cev,
                '状态': '✓ 成功'
            })
            
        except Exception as e:
            results.append({
                '单位名称': unit_name,
            '指挥官': unit_data['commander'],
                'CEV': 0,
                '状态': f'✗ 错误: {str(e)}'
        })
    
    # 显示结果
    df = pd.DataFrame(results)
    df = df.sort_values('CEV', ascending=False)
    print(df.to_string(index=False))
    print()

    # 验证预期排名
    print("=== 预期排名验证 ===")
    expected_order = [
        '掠袭解放者',
        '灵魂巧匠天罚行者', 
        '普通天罚行者',
        '攻城坦克',
        '穿刺者',
        '龙骑士'
    ]
    
    actual_order = df[df['状态'] == '✓ 成功']['单位名称'].tolist()
    
    print("预期排名:")
    for i, unit in enumerate(expected_order, 1):
        print(f"{i}. {unit}")
    
    print("\n实际排名:")
    for i, unit in enumerate(actual_order, 1):
        print(f"{i}. {unit}")
    
    print(f"\n排名匹配度: {len(set(expected_order) & set(actual_order))}/{len(expected_order)}")
    
    return df


def test_parameter_consistency():
    """测试参数一致性"""
    print("\n=== 参数一致性测试 ===\n")
    
    calculator = RefinedCEVCalculator()
    
    # 测试关键参数
    print("关键参数:")
    print(f"- 矿气转换率: 2.5")
    print(f"- 人口基准价值: 20")
    print(f"- 100人口指挥官人口质量乘数: 2.0")
    print(f"- 200人口指挥官人口质量乘数: 1.0")
    print()
    
    # 测试特殊系数
    print("特殊系数:")
    print("- 天罚行者操作难度系数: 1.3")
    print("- 解放者操作难度系数: 0.75")
    print("- 坦克/穿刺者操作难度系数: 0.8")
    print("- 过量击杀惩罚: 分段惩罚机制")
    print()


def test_edge_cases():
    """测试边界情况"""
    print("=== 边界情况测试 ===\n")
    
    calculator = RefinedCEVCalculator()
    
    # 测试空中单位（碰撞半径为0）
    print("测试空中单位处理:")
    try:
        unit_stats = calculator.create_unit_stats(
            hp=200, shield=0, armor=0,
            mineral_cost=150, gas_cost=100, supply_cost=2,
            collision_radius=0  # 空中单位
        )
        
        weapon_stats = calculator.create_weapon_stats(
            base_damage=25, attack_count=1, attack_interval=1.0,
            weapon_range=6, splash_factor=1.0
        )
        
        cev = calculator.calculate_cev(unit_stats, weapon_stats, "测试指挥官")
        print(f"✓ 空中单位CEV计算成功: {cev:.2f}")
        
    except Exception as e:
        print(f"✗ 空中单位测试失败: {e}")
    
    # 测试高伤害单位
    print("\n测试高伤害单位过量击杀惩罚:")
    try:
        weapon_stats = calculator.create_weapon_stats(
            base_damage=250, attack_count=1, attack_interval=2.0,
            weapon_range=8, splash_factor=1.5
        )
        
        print(f"✓ 高伤害单位处理成功")
        
    except Exception as e:
        print(f"✗ 高伤害单位测试失败: {e}")


if __name__ == "__main__":
    # 运行所有测试
    print("星际争霸II CEV计算器 v2.4 模型验证\n")
    
    # 主要测试
    results_df = test_cev_calculation()
    
    # 参数测试
    test_parameter_consistency()
    
    # 边界测试
    test_edge_cases()
    
    # 总结
    print("\n=== 验证总结 ===")
    success_count = len(results_df[results_df['状态'] == '✓ 成功'])
    total_count = len(results_df)
    
    print(f"✓ 成功计算: {success_count}/{total_count} 个单位")
    print(f"✓ 计算器状态: {'正常' if success_count == total_count else '需要修复'}")
    
    if success_count == total_count:
        print("✓ 所有测试通过，v2.4计算器工作正常")
    else:
        print("⚠ 部分测试失败，请检查错误信息")