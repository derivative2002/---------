"""
验证模型实现是否符合论文设计
"""

import pandas as pd
from src.core.model_corrections import ModelCorrections, CORRECTED_ELITE_UNITS

def verify_cev_formula():
    """验证CEV公式实现"""
    print("=== CEV公式验证 ===\n")
    
    # 以龙骑士为例
    unit = CORRECTED_ELITE_UNITS['Dragoon']
    
    # 中期游戏参数
    lambda_t = 0.593  # 中期游戏λ值
    lambda_max = 1.0  # 阿塔尼斯是200人口指挥官
    lambda_value = lambda_t * lambda_max
    
    # 1. 有效成本计算
    effective_cost = ModelCorrections.calculate_effective_cost(unit, lambda_value)
    print(f"有效成本计算:")
    print(f"  矿物成本: {unit['mineral_cost']}")
    print(f"  瓦斯成本: {unit['gas_cost']} × 2.5 = {unit['gas_cost'] * 2.5}")
    print(f"  人口压力: {unit['supply_cost']} × 20 × {lambda_value:.3f} = {unit['supply_cost'] * 20 * lambda_value:.1f}")
    print(f"  有效成本: {effective_cost:.1f}\n")
    
    # 2. CEV计算（对重甲）
    dps_vs_armored = unit['vs_armored_dps']
    effective_hp = unit['effective_hp']
    synergy = unit['synergy']
    
    cev_vs_armored = (dps_vs_armored * effective_hp * synergy) / effective_cost
    print(f"CEV计算（对重甲）:")
    print(f"  DPS: {dps_vs_armored}")
    print(f"  有效HP: {effective_hp}")
    print(f"  协同系数: {synergy}")
    print(f"  CEV = ({dps_vs_armored} × {effective_hp} × {synergy}) / {effective_cost:.1f}")
    print(f"  CEV = {cev_vs_armored:.1f}\n")
    
    # 3. 对比普通目标
    dps_normal = unit['base_dps']
    cev_normal = (dps_normal * effective_hp * synergy) / effective_cost
    print(f"CEV计算（普通目标）:")
    print(f"  DPS: {dps_normal}")
    print(f"  CEV = {cev_normal:.1f}")
    print(f"  对重甲提升: {cev_vs_armored / cev_normal:.1f}倍\n")


def verify_all_elite_units():
    """验证所有精英单位的CEV计算"""
    print("=== 五大精英单位CEV验证 ===\n")
    
    results = []
    lambda_value = 0.593  # 中期游戏
    
    for unit_id, unit_data in CORRECTED_ELITE_UNITS.items():
        # 确定λ_max
        if unit_data['commander'] in ['诺娃']:
            lambda_max = 2.0  # 100人口指挥官
        else:
            lambda_max = 1.0  # 200人口指挥官
        
        final_lambda = lambda_value * lambda_max
        
        # 计算有效成本
        effective_cost = ModelCorrections.calculate_effective_cost(unit_data, final_lambda)
        
        # 计算CEV（使用最高DPS场景）
        if unit_id == 'Dragoon':
            dps = unit_data['vs_armored_dps']
            scenario = '对重甲'
        elif unit_id == 'SiegeTank_Swann':
            dps = unit_data['vs_armored_siege']
            scenario = '攻城模式对重甲'
        elif unit_id == 'Impaler':
            dps = unit_data['vs_armored_dps']
            scenario = '对重甲'
        elif unit_id == 'RaidLiberator':
            dps = unit_data['ag_mode_dps']
            scenario = 'AG模式'
        else:
            dps = unit_data['base_dps']
            scenario = '基础'
        
        # 加上能力价值
        total_dps = dps + unit_data['ability_value']
        
        # 计算CEV
        cev = (total_dps * unit_data['effective_hp'] * unit_data['synergy']) / effective_cost
        
        results.append({
            '单位': unit_data['chinese_name'],
            '指挥官': unit_data['commander'],
            '场景': scenario,
            'DPS': total_dps,
            '有效HP': unit_data['effective_hp'],
            '有效成本': effective_cost,
            'CEV': cev
        })
    
    # 显示结果
    df = pd.DataFrame(results)
    df = df.sort_values('CEV', ascending=False)
    print(df.to_string(index=False))
    print()


def check_model_parameters():
    """检查关键模型参数"""
    print("=== 模型参数检查 ===\n")
    
    params = ModelCorrections.STANDARD_PARAMS
    
    print("1. 有效成本参数:")
    print(f"   - 矿气转换率(α): {params['mineral_gas_ratio']}")
    print(f"   - 人口基准价值(ρ): {params['supply_base_value']}")
    print()
    
    print("2. 人口压力因子:")
    print(f"   - 200人口λ_max: {params['lambda_max_200']}")
    print(f"   - 100人口基础λ_max: {params['lambda_max_100_base']}")
    print()
    
    print("3. 特殊组合效应:")
    for combo, value in params['synergy_params'].items():
        print(f"   - {combo}: {value}")
    print()


def compare_with_experiment_results():
    """对比实验结果"""
    print("=== 与实验结果对比 ===\n")
    
    # 读取实验结果
    try:
        df = pd.read_csv('benchmarks/data/overall_ranking.csv')
        print("实验结果中的CEV值:")
        for _, row in df.iterrows():
            print(f"  {row['unit_name']}: {row['cev']:.1f}")
        print()
        
        print("注意: 实验结果可能使用了不同的参数值")
        print("建议重新运行实验以使用修正后的参数")
    except:
        print("未找到实验结果文件")


if __name__ == "__main__":
    # 运行所有验证
    verify_cev_formula()
    verify_all_elite_units()
    check_model_parameters()
    compare_with_experiment_results()
    
    print("\n=== 建议 ===")
    print("1. 修正enhanced_cev_calculator.py中的人口基准价值为20")
    print("2. 实现100人口指挥官的ρ_free扣减")
    print("3. 添加特殊组合效应的具体实现")
    print("4. 重新运行实验以获得准确的CEV值")