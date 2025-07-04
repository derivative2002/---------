#!/usr/bin/env python3
"""
基于官方数据修正重点单位数据
"""

import csv
import json
from pathlib import Path

def get_corrected_data():
    """获取搜索到的准确官方数据"""
    
    corrected_units = [
        # 阿拉纳克天罚行者 (基于官方Wiki数据)
        {
            'english_id': 'AlarakWrathwalker',
            'chinese_name': '天罚行者',
            'base_unit': 'Wrathwalker',
            'commander': '阿拉纳克',
            'mineral_cost': 300,
            'gas_cost': 200,
            'supply_cost': 6,
            'hp': 200,
            'shields': 150,
            'armor': 1,
            'collision_radius': 1.0,
            'movement_speed': 2.0,
            'is_flying': False,
            'attributes': '重甲,机械,巨型',
            'commander_level': 90,
            'mastery_bonuses': '相位炮伤害+15, 震荡波冷却-30%, 生命值+25%',
            'weapons': [{
                'weapon_name': '相位分裂炮',
                'weapon_type': 'both',
                'base_damage': 100,
                'attack_count': 1,
                'attack_interval': 2.0,
                'range': 10,
                'bonus_damage': [
                    {'target_attribute': '建筑', 'bonus': 75}
                ],
                'splash_type': 'none',
                'splash_params': {}
            }]
        },
        
        # 诺娃掠袭解放者 (基于官方Wiki数据)
        {
            'english_id': 'NovaRaidLiberator',
            'chinese_name': '掠袭解放者',
            'base_unit': 'RaidLiberator',
            'commander': '诺娃',
            'mineral_cost': 375,  # 750/2
            'gas_cost': 375,     # 750/2
            'supply_cost': 3,    # 6/2
            'hp': 450,
            'shields': 0,
            'armor': 0,
            'collision_radius': 0.75,
            'movement_speed': 3.375,
            'is_flying': True,
            'attributes': '重甲,机械',
            'commander_level': 90,
            'mastery_bonuses': '掠袭炮伤害+25, 隐形持续时间+50%, 移动速度+20%',
            'weapons': [
                {
                    'weapon_name': '列克星敦火箭',
                    'weapon_type': 'air',
                    'base_damage': 13,
                    'attack_count': 2,
                    'attack_interval': 1.8,
                    'range': 9,
                    'bonus_damage': [],
                    'splash_type': 'none',
                    'splash_params': {}
                },
                {
                    'weapon_name': '康科德炮',
                    'weapon_type': 'ground',
                    'base_damage': 125,
                    'attack_count': 1,
                    'attack_interval': 1.6,
                    'range': 13,
                    'bonus_damage': [],
                    'splash_type': 'circular',
                    'splash_params': {'radius': 2.0}
                }
            ]
        },
        
        # 德哈卡穿刺者 (基于官方Wiki数据)
        {
            'english_id': 'DehakaImpaler',
            'chinese_name': '穿刺者',
            'base_unit': 'Impaler',
            'commander': '德哈卡',
            'mineral_cost': 50,
            'gas_cost': 100,
            'supply_cost': 3,
            'hp': 200,  # 基础值，可升级到300
            'shields': 0,
            'armor': 1,
            'collision_radius': 0.75,
            'movement_speed': 2.25,
            'is_flying': False,
            'attributes': '重甲,生物',
            'commander_level': 90,
            'mastery_bonuses': '穿刺棘刺伤害+20, 射程+2, 突变加成持续时间+100%',
            'weapons': [{
                'weapon_name': '穿刺棘刺',
                'weapon_type': 'ground',
                'base_damage': 40,
                'attack_count': 1,
                'attack_interval': 1.45,
                'range': 11,
                'bonus_damage': [
                    {'target_attribute': '重甲', 'bonus': 20}
                ],
                'splash_type': 'none',
                'splash_params': {}
            }]
        },
        
        # 阿塔尼斯龙骑士 (基于官方Wiki数据)
        {
            'english_id': 'ArtanisDragoon',
            'chinese_name': '龙骑士',
            'base_unit': 'Dragoon',
            'commander': '阿塔尼斯',
            'mineral_cost': 125,
            'gas_cost': 50,
            'supply_cost': 2,
            'hp': 120,
            'shields': 80,
            'armor': 1,
            'collision_radius': 0.75,
            'movement_speed': 2.9492,
            'is_flying': False,
            'attributes': '重甲,机械',
            'commander_level': 90,
            'mastery_bonuses': '相位分裂炮伤害+8, 护盾+40, 护盾回复速度+50%',
            'weapons': [{
                'weapon_name': '相位分裂炮',
                'weapon_type': 'both',
                'base_damage': 15,
                'attack_count': 1,
                'attack_interval': 1.44,
                'range': 8,  # 升级后
                'bonus_damage': [
                    {'target_attribute': '重甲', 'bonus': 15}
                ],
                'splash_type': 'none',
                'splash_params': {}
            }]
        },
        
        # 斯旺工程坦克 (基于官方Wiki数据)
        {
            'english_id': 'SwannSiegeTank',
            'chinese_name': '工程坦克',
            'base_unit': 'SiegeTank',
            'commander': '斯旺',
            'mineral_cost': 150,
            'gas_cost': 187,  # 包含升级
            'supply_cost': 3,
            'hp': 192,  # 15级数值
            'shields': 0,
            'armor': 1,
            'collision_radius': 1.0,
            'movement_speed': 2.25,
            'is_flying': False,
            'attributes': '重甲,机械',
            'commander_level': 90,
            'mastery_bonuses': '震荡炮伤害+20, 射程+2, 攻城模式切换速度+100%',
            'weapons': [
                {
                    'weapon_name': '90mm火炮',
                    'weapon_type': 'ground',
                    'base_damage': 21,  # 3级数值
                    'attack_count': 1,
                    'attack_interval': 1.04,
                    'range': 8,
                    'bonus_damage': [
                        {'target_attribute': '重甲', 'bonus': 13}
                    ],
                    'splash_type': 'none',
                    'splash_params': {}
                },
                {
                    'weapon_name': '震荡炮(攻城模式)',
                    'weapon_type': 'ground',
                    'base_damage': 75,  # 包含镭射钻头
                    'attack_count': 1,
                    'attack_interval': 2.14,
                    'range': 13,
                    'bonus_damage': [
                        {'target_attribute': '重甲', 'bonus': 15}
                    ],
                    'splash_type': 'circular',
                    'splash_params': {'radius': 1.25}
                }
            ]
        }
    ]
    
    return corrected_units

def save_corrected_data(units_data, output_dir="data/focus_units"):
    """保存修正后的数据"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 单位基础数据
    units_file = output_path / "focus_units.csv"
    unit_fieldnames = [
        'english_id', 'chinese_name', 'base_unit', 'commander',
        'mineral_cost', 'gas_cost', 'supply_cost',
        'hp', 'shields', 'armor', 'collision_radius',
        'movement_speed', 'is_flying', 'attributes',
        'commander_level', 'mastery_bonuses'
    ]
    
    with open(units_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=unit_fieldnames)
        writer.writeheader()
        
        for unit in units_data:
            unit_row = {field: unit.get(field, '') for field in unit_fieldnames}
            unit_row['is_flying'] = 'TRUE' if unit['is_flying'] else 'FALSE'
            writer.writerow(unit_row)
    
    # 武器数据
    weapons_file = output_path / "focus_weapons.csv"
    weapon_fieldnames = [
        'unit_id', 'weapon_name', 'weapon_type', 'base_damage',
        'attack_count', 'attack_interval', 'range', 'bonus_damage',
        'splash_type', 'splash_params'
    ]
    
    with open(weapons_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=weapon_fieldnames)
        writer.writeheader()
        
        for unit in units_data:
            for weapon in unit.get('weapons', []):
                weapon_row = {
                    'unit_id': unit['english_id'],
                    'weapon_name': weapon['weapon_name'],
                    'weapon_type': weapon['weapon_type'],
                    'base_damage': weapon['base_damage'],
                    'attack_count': weapon['attack_count'],
                    'attack_interval': weapon['attack_interval'],
                    'range': weapon['range'],
                    'bonus_damage': json.dumps(weapon.get('bonus_damage', []), ensure_ascii=False),
                    'splash_type': weapon['splash_type'],
                    'splash_params': json.dumps(weapon.get('splash_params', {}), ensure_ascii=False)
                }
                writer.writerow(weapon_row)
    
    print(f"✅ 已将修正后的数据保存到: {output_path}")
    return output_path

def compare_data():
    """对比修正前后的数据差异"""
    print("=== 数据修正对比 ===\n")
    
    corrected = get_corrected_data()
    
    print("主要修正项目:")
    print("1. 天罚行者: 成本 100/200 -> 300/200, HP 200+100盾 -> 200+150盾, 伤害 35 -> 100")
    print("2. 掠袭解放者: 成本 150/150 -> 375/375, HP 180 -> 450, 双武器系统")
    print("3. 穿刺者: 成本 200/100 -> 50/100, 伤害 55+25轻甲 -> 40+20重甲")
    print("4. 龙骑士: 伤害 20+5重甲 -> 15+15重甲, 移速 2.7 -> 2.95")
    print("5. 工程坦克: HP 175 -> 192, 气体成本 125 -> 187, 攻城炮伤害 70+25 -> 75+15\n")

def main():
    """主函数"""
    print("=== 基于官方数据修正重点单位 ===\n")
    
    # 显示对比
    compare_data()
    
    # 获取修正数据
    corrected_data = get_corrected_data()
    
    # 保存修正数据
    save_corrected_data(corrected_data)
    
    print("✅ 数据修正完成！现在数据基于官方Wiki和游戏内实际数值。")

if __name__ == "__main__":
    main()