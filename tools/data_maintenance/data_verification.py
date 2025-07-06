#!/usr/bin/env python3
"""
重点单位数据校对脚本
用于验证和修正星际争霸二合作任务单位的基础数据
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple

class DataVerifier:
    """数据校对器"""
    
    def __init__(self, data_dir: str = "data/focus_units"):
        self.data_dir = Path(data_dir)
        self.corrections = {}
        self.load_official_data()
    
    def load_official_data(self):
        """加载官方准确数据作为参考"""
        # 基于官方资料的准确数据
        self.official_data = {
            'AlarakWrathwalker': {
                'chinese_name': '天罚行者',
                'hp': 200,
                'shields': 100,
                'armor': 1,
                'mineral_cost': 100,
                'gas_cost': 200,
                'supply_cost': 4,
                'movement_speed': 2.25,
                'is_flying': False,
                'attributes': ['重甲', '机械'],
                'weapon_damage': 35,
                'weapon_range': 7,
                'attack_interval': 2.5,
                'bonus_vs_light': 15,
                'bonus_vs_armored': 10
            },
            'NovaRaidLiberator': {
                'chinese_name': '掠袭解放者',
                'hp': 180,
                'shields': 0,
                'armor': 1,
                'mineral_cost': 150,
                'gas_cost': 150,
                'supply_cost': 3,
                'movement_speed': 4.13,
                'is_flying': True,
                'attributes': ['重甲', '机械'],
                'weapon_damage': 85,
                'weapon_range': 9,
                'attack_interval': 2.14,
                'bonus_vs_light': 45,
                'bonus_vs_armored': 0
            },
            'DehakaImpaler': {
                'chinese_name': '穿刺者',
                'hp': 200,
                'shields': 0,
                'armor': 2,
                'mineral_cost': 200,
                'gas_cost': 100,
                'supply_cost': 4,
                'movement_speed': 2.25,
                'is_flying': False,
                'attributes': ['重甲', '生物'],
                'weapon_damage': 55,
                'weapon_range': 11,
                'attack_interval': 3.0,
                'bonus_vs_light': 25,
                'bonus_vs_armored': 0
            },
            'ArtanisDragoon': {
                'chinese_name': '龙骑士',
                'hp': 100,
                'shields': 120,  # 升级后数值
                'armor': 1,
                'mineral_cost': 125,
                'gas_cost': 50,
                'supply_cost': 2,
                'movement_speed': 2.7,  # 升级后速度
                'is_flying': False,
                'attributes': ['重甲', '机械'],
                'weapon_damage': 20,
                'weapon_range': 8,  # 升级后射程
                'attack_interval': 1.44,
                'bonus_vs_light': 0,
                'bonus_vs_armored': 5
            },
            'SwannSiegeTank': {
                'chinese_name': '工程坦克',
                'hp': 175,
                'shields': 0,
                'armor': 1,
                'mineral_cost': 150,
                'gas_cost': 125,
                'supply_cost': 3,
                'movement_speed': 2.25,
                'is_flying': False,
                'attributes': ['重甲', '机械'],
                # 坦克模式
                'weapon_damage_tank': 15,
                'weapon_range_tank': 7,
                'attack_interval_tank': 1.04,
                'bonus_vs_armored_tank': 10,
                # 攻城模式
                'weapon_damage_siege': 70,
                'weapon_range_siege': 15,
                'attack_interval_siege': 2.14,
                'bonus_vs_armored_siege': 25
            }
        }
    
    def verify_basic_stats(self) -> Dict:
        """验证基础属性数据"""
        print("=== 校对基础属性数据 ===\n")
        
        units_file = self.data_dir / "focus_units.csv"
        if not units_file.exists():
            print(f"文件不存在: {units_file}")
            return {}
        
        issues = {}
        corrections = {}
        
        with open(units_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                unit_id = row['english_id']
                if unit_id not in self.official_data:
                    continue
                
                official = self.official_data[unit_id]
                current_issues = []
                current_corrections = {}
                
                # 检查各项数据
                checks = [
                    ('hp', int, 'HP'),
                    ('shields', int, '护盾'),
                    ('armor', int, '护甲'),
                    ('mineral_cost', int, '矿物成本'),
                    ('gas_cost', int, '瓦斯成本'),
                    ('supply_cost', float, '人口成本'),
                    ('movement_speed', float, '移动速度')
                ]
                
                for field, data_type, display_name in checks:
                    if field in official:
                        current_val = data_type(row[field])
                        expected_val = official[field]
                        
                        if current_val != expected_val:
                            current_issues.append(f"{display_name}: {current_val} -> {expected_val}")
                            current_corrections[field] = expected_val
                
                # 检查飞行状态
                current_flying = row['is_flying'] == 'TRUE'
                expected_flying = official['is_flying']
                if current_flying != expected_flying:
                    current_issues.append(f"飞行状态: {current_flying} -> {expected_flying}")
                    current_corrections['is_flying'] = 'TRUE' if expected_flying else 'FALSE'
                
                # 检查属性标签
                current_attrs = set(row['attributes'].split(',')) if row['attributes'] else set()
                expected_attrs = set(official['attributes'])
                if current_attrs != expected_attrs:
                    current_issues.append(f"属性: {current_attrs} -> {expected_attrs}")
                    current_corrections['attributes'] = ','.join(expected_attrs)
                
                if current_issues:
                    issues[unit_id] = current_issues
                    corrections[unit_id] = current_corrections
                    print(f"【{official['chinese_name']}】需要修正:")
                    for issue in current_issues:
                        print(f"  - {issue}")
                    print()
        
        self.corrections.update(corrections)
        return issues
    
    def verify_weapon_data(self) -> Dict:
        """验证武器数据"""
        print("=== 校对武器数据 ===\n")
        
        weapons_file = self.data_dir / "focus_weapons.csv"
        if not weapons_file.exists():
            print(f"文件不存在: {weapons_file}")
            return {}
        
        issues = {}
        weapon_corrections = []
        
        with open(weapons_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            weapons_data = list(reader)
        
        for row in weapons_data:
            unit_id = row['unit_id']
            weapon_name = row['weapon_name']
            
            if unit_id not in self.official_data:
                continue
            
            official = self.official_data[unit_id]
            current_issues = []
            weapon_fix = row.copy()
            
            # 检查不同武器类型
            if unit_id == 'SwannSiegeTank':
                if '90mm' in weapon_name:
                    # 坦克模式武器
                    expected_damage = official['weapon_damage_tank']
                    expected_range = official['weapon_range_tank']
                    expected_interval = official['attack_interval_tank']
                elif '震荡炮' in weapon_name:
                    # 攻城模式武器
                    expected_damage = official['weapon_damage_siege']
                    expected_range = official['weapon_range_siege']
                    expected_interval = official['attack_interval_siege']
            else:
                # 单武器单位
                expected_damage = official['weapon_damage']
                expected_range = official['weapon_range']
                expected_interval = official['attack_interval']
            
            # 检查基础伤害
            current_damage = float(row['base_damage'])
            if current_damage != expected_damage:
                current_issues.append(f"基础伤害: {current_damage} -> {expected_damage}")
                weapon_fix['base_damage'] = str(expected_damage)
            
            # 检查射程
            current_range = float(row['range'])
            if current_range != expected_range:
                current_issues.append(f"射程: {current_range} -> {expected_range}")
                weapon_fix['range'] = str(expected_range)
            
            # 检查攻击间隔
            current_interval = float(row['attack_interval'])
            if abs(current_interval - expected_interval) > 0.01:
                current_issues.append(f"攻击间隔: {current_interval} -> {expected_interval}")
                weapon_fix['attack_interval'] = str(expected_interval)
            
            # 检查克制伤害
            bonus_data = json.loads(row['bonus_damage']) if row['bonus_damage'] else []
            expected_bonuses = []
            
            if unit_id in ['AlarakWrathwalker', 'NovaRaidLiberator', 'DehakaImpaler']:
                if official.get('bonus_vs_light', 0) > 0:
                    expected_bonuses.append({'target_attribute': '轻甲', 'bonus': official['bonus_vs_light']})
            
            if unit_id in ['AlarakWrathwalker', 'ArtanisDragoon'] or 'SwannSiegeTank' in unit_id:
                if official.get('bonus_vs_armored', 0) > 0 or official.get('bonus_vs_armored_tank', 0) > 0:
                    if unit_id == 'SwannSiegeTank':
                        if '90mm' in weapon_name:
                            bonus_val = official['bonus_vs_armored_tank']
                        else:
                            bonus_val = official['bonus_vs_armored_siege']
                    else:
                        bonus_val = official['bonus_vs_armored']
                    
                    if bonus_val > 0:
                        expected_bonuses.append({'target_attribute': '重甲', 'bonus': bonus_val})
            
            # 比较克制伤害
            if len(bonus_data) != len(expected_bonuses):
                current_issues.append(f"克制伤害数量不匹配")
                weapon_fix['bonus_damage'] = json.dumps(expected_bonuses, ensure_ascii=False)
            else:
                for current_bonus, expected_bonus in zip(bonus_data, expected_bonuses):
                    if (current_bonus.get('target_attribute') != expected_bonus['target_attribute'] or 
                        current_bonus.get('bonus') != expected_bonus['bonus']):
                        current_issues.append(f"克制伤害值不正确")
                        weapon_fix['bonus_damage'] = json.dumps(expected_bonuses, ensure_ascii=False)
                        break
            
            if current_issues:
                key = f"{unit_id}_{weapon_name}"
                issues[key] = current_issues
                weapon_corrections.append(weapon_fix)
                print(f"【{weapon_name}】需要修正:")
                for issue in current_issues:
                    print(f"  - {issue}")
                print()
        
        self.weapon_corrections = weapon_corrections
        return issues
    
    def apply_corrections(self):
        """应用数据修正"""
        print("=== 应用数据修正 ===\n")
        
        # 修正基础单位数据
        if hasattr(self, 'corrections') and self.corrections:
            units_file = self.data_dir / "focus_units.csv"
            self._apply_unit_corrections(units_file)
        
        # 修正武器数据
        if hasattr(self, 'weapon_corrections') and self.weapon_corrections:
            weapons_file = self.data_dir / "focus_weapons.csv"
            self._apply_weapon_corrections(weapons_file)
    
    def _apply_unit_corrections(self, units_file: Path):
        """应用单位数据修正"""
        with open(units_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
        
        # 应用修正
        for row in rows:
            unit_id = row['english_id']
            if unit_id in self.corrections:
                for field, new_value in self.corrections[unit_id].items():
                    row[field] = str(new_value)
                print(f"已修正 {row['chinese_name']} 的数据")
        
        # 写回文件
        with open(units_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"单位数据修正完成: {units_file}")
    
    def _apply_weapon_corrections(self, weapons_file: Path):
        """应用武器数据修正"""
        with open(weapons_file, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ['unit_id', 'weapon_name', 'weapon_type', 'base_damage', 
                         'attack_count', 'attack_interval', 'range', 'bonus_damage', 
                         'splash_type', 'splash_params']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.weapon_corrections)
        
        print(f"武器数据修正完成: {weapons_file}")
    
    def generate_verification_report(self):
        """生成完整校对报告"""
        print("=== 重点单位数据校对报告 ===\n")
        
        basic_issues = self.verify_basic_stats()
        weapon_issues = self.verify_weapon_data()
        
        total_issues = len(basic_issues) + len(weapon_issues)
        
        if total_issues == 0:
            print("✅ 所有数据校对通过，未发现问题！")
        else:
            print(f"⚠️ 发现 {total_issues} 项需要修正的数据")
            
            if input("\n是否应用这些修正？(y/n): ").lower() == 'y':
                self.apply_corrections()
                print("\n✅ 数据修正完成！")
            else:
                print("\n❌ 已跳过数据修正")
        
        return basic_issues, weapon_issues


def main():
    """主函数"""
    verifier = DataVerifier()
    verifier.generate_verification_report()


if __name__ == "__main__":
    main()