"""
高级数据加载器
支持新的数据格式规范v2.0
"""

import pandas as pd
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging

from .models import (
    Unit, Weapon, Ability, UnitMode, SplashParams,
    WeaponType, SplashType, AbilityType, ModeType,
    CommanderConfig, UnitDatabase
)


class AdvancedDataLoader:
    """高级数据加载器"""
    
    def __init__(self, data_dir: str = "data/units"):
        self.data_dir = Path(data_dir)
        self.logger = logging.getLogger(__name__)
        self.database = UnitDatabase()
        
    def load_all_data(self) -> UnitDatabase:
        """加载所有数据"""
        # 1. 加载主单位数据
        self._load_units_master()
        
        # 2. 加载武器数据
        self._load_weapons()
        
        # 3. 加载模式数据
        self._load_unit_modes()
        
        # 4. 加载能力数据（如果有）
        self._load_abilities()
        
        # 5. 加载指挥官配置
        self._load_commander_configs()
        
        # 6. 验证数据
        errors = self.database.validate_data()
        if errors:
            self.logger.warning(f"数据验证发现{len(errors)}个问题")
            for error in errors[:10]:  # 只显示前10个
                self.logger.warning(error)
                
        return self.database
    
    def _load_units_master(self):
        """加载主单位数据"""
        file_path = self.data_dir / "units_master.csv"
        
        if not file_path.exists():
            self.logger.error(f"找不到主数据文件: {file_path}")
            return
            
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            
            for _, row in df.iterrows():
                # 解析属性标签
                attributes = []
                if pd.notna(row.get('attributes')):
                    attributes = [attr.strip() for attr in str(row['attributes']).split(',')]
                
                # 解析特殊能力
                abilities = []
                if pd.notna(row.get('special_abilities')):
                    try:
                        abilities_data = json.loads(row['special_abilities'])
                        abilities = [Ability.from_dict(data) for data in abilities_data]
                    except json.JSONDecodeError:
                        self.logger.warning(f"解析能力失败: {row['english_id']}")
                
                # 创建单位对象
                unit = Unit(
                    english_id=row['english_id'],
                    chinese_name=row['chinese_name'],
                    commander=row['commander'],
                    mineral_cost=int(row['mineral_cost']),
                    gas_cost=int(row['gas_cost']),
                    supply_cost=float(row['supply_cost']),
                    hp=int(row['hp']),
                    shields=int(row.get('shields', 0)),
                    armor=int(row.get('armor', 0)),
                    collision_radius=float(row['collision_radius']) if pd.notna(row.get('collision_radius')) else None,
                    movement_speed=float(row['movement_speed']),
                    is_flying=str(row.get('is_flying', 'false')).lower() == 'true',
                    attributes=attributes,
                    abilities=abilities
                )
                
                self.database.add_unit(unit)
                
        except Exception as e:
            self.logger.error(f"加载主数据失败: {e}")
    
    def _load_weapons(self):
        """加载武器数据"""
        file_path = self.data_dir / "weapons.csv"
        
        if not file_path.exists():
            self.logger.warning(f"找不到武器数据文件: {file_path}")
            return
            
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            
            for _, row in df.iterrows():
                # 解析伤害加成
                bonus_damage = {}
                if pd.notna(row.get('bonus_damage')) and row['bonus_damage'] != '{}':
                    try:
                        bonus_damage = json.loads(row['bonus_damage'])
                    except json.JSONDecodeError:
                        self.logger.warning(f"解析伤害加成失败: {row['unit_id']} - {row['weapon_name']}")
                
                # 解析溅射参数
                splash_params = None
                if pd.notna(row.get('splash_params')) and row['splash_params'] != '{}':
                    try:
                        splash_params = SplashParams.from_json(row['splash_params'])
                    except Exception as e:
                        self.logger.warning(f"解析溅射参数失败: {row['unit_id']} - {row['weapon_name']}: {e}")
                
                # 创建武器对象
                weapon = Weapon(
                    unit_id=row['unit_id'],
                    weapon_name=row['weapon_name'],
                    weapon_type=WeaponType(row['weapon_type']),
                    base_damage=float(row['base_damage']),
                    attack_count=int(row.get('attack_count', 1)),
                    attack_interval=float(row['attack_interval']),
                    range=float(row['range']),
                    bonus_damage=bonus_damage,
                    splash_type=SplashType(row.get('splash_type', 'none')),
                    splash_params=splash_params
                )
                
                # 添加到对应单位
                for unit in self.database.units.values():
                    if unit.english_id == weapon.unit_id:
                        unit.weapons.append(weapon)
                        
        except Exception as e:
            self.logger.error(f"加载武器数据失败: {e}")
    
    def _load_unit_modes(self):
        """加载单位模式数据"""
        file_path = self.data_dir / "unit_modes.csv"
        
        if not file_path.exists():
            self.logger.info(f"没有模式数据文件: {file_path}")
            return
            
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            
            for _, row in df.iterrows():
                # 解析属性修正
                stat_modifiers = {}
                if pd.notna(row.get('stat_modifiers')) and row['stat_modifiers'] != '{}':
                    try:
                        stat_modifiers = json.loads(row['stat_modifiers'])
                    except json.JSONDecodeError:
                        self.logger.warning(f"解析属性修正失败: {row['unit_id']} - {row['mode_name']}")
                
                # 创建模式对象
                mode = UnitMode(
                    unit_id=row['unit_id'],
                    mode_name=row['mode_name'],
                    mode_type=ModeType(row['mode_type']),
                    stat_modifiers=stat_modifiers,
                    weapon_config=row['weapon_config'],
                    switch_time=float(row.get('switch_time', 0))
                )
                
                # 添加到对应单位
                for unit in self.database.units.values():
                    if unit.english_id == mode.unit_id:
                        unit.modes.append(mode)
                        
        except Exception as e:
            self.logger.error(f"加载模式数据失败: {e}")
    
    def _load_abilities(self):
        """加载能力详细数据"""
        file_path = self.data_dir / "abilities.csv"
        
        if not file_path.exists():
            self.logger.info(f"没有能力数据文件: {file_path}")
            return
            
        # TODO: 实现能力数据的详细加载
        pass
    
    def _load_commander_configs(self):
        """加载指挥官配置"""
        file_path = self.data_dir.parent / "commanders" / "commander_config.json"
        
        if not file_path.exists():
            self.logger.info(f"没有指挥官配置文件: {file_path}")
            self._create_default_commander_configs()
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                configs = json.load(f)
                
            for name, config in configs.items():
                commander = CommanderConfig(
                    name=name,
                    population_cap=config.get('population_cap', 200),
                    modifiers=config.get('modifiers', {}),
                    special_mechanics=config.get('special_mechanics', [])
                )
                self.database.commanders[name] = commander
                
        except Exception as e:
            self.logger.error(f"加载指挥官配置失败: {e}")
            self._create_default_commander_configs()
    
    def _create_default_commander_configs(self):
        """创建默认指挥官配置"""
        default_configs = {
            "吉姆·雷诺": CommanderConfig(
                name="吉姆·雷诺",
                population_cap=200,
                modifiers={'hp': 1.0, 'damage': 1.0},
                special_mechanics=["医疗兵", "钒合金板"]
            ),
            "凯瑞甘": CommanderConfig(
                name="凯瑞甘",
                population_cap=200,
                modifiers={'hp': 1.1, 'damage': 1.1},
                special_mechanics=["恶性爬虫", "omega蠕虫"]
            ),
            "阿塔尼斯": CommanderConfig(
                name="阿塔尼斯",
                population_cap=200,
                modifiers={'shields': 1.2, 'damage': 1.0},
                special_mechanics=["守护者之壳", "太阳能轰炸"]
            ),
            "诺娃·泰拉": CommanderConfig(
                name="诺娃·泰拉",
                population_cap=100,
                modifiers={'hp': 1.5, 'damage': 2.0},
                special_mechanics=["精英部队", "战术空运"]
            ),
            "泰凯斯": CommanderConfig(
                name="泰凯斯",
                population_cap=100,
                modifiers={'hp': 2.0, 'damage': 1.5},
                special_mechanics=["无法无天", "英雄单位"]
            ),
            "阿拉纳克": CommanderConfig(
                name="阿拉纳克",
                population_cap=200,
                modifiers={'damage': 1.2, 'hp': 1.1},
                special_mechanics=["死亡舰队", "强化我"]
            )
        }
        
        for name, config in default_configs.items():
            self.database.commanders[name] = config
    
    def export_to_legacy_format(self) -> List[Dict[str, Any]]:
        """导出为旧格式，兼容现有系统"""
        legacy_data = []
        
        for unit in self.database.units.values():
            # 计算基础DPS（使用主武器）
            base_dps = 0
            if unit.weapons:
                primary_weapon = unit.weapons[0]
                base_dps = primary_weapon.dps
            
            # 获取主要攻击射程
            range_value = 5
            if unit.weapons:
                range_value = unit.weapons[0].range
            
            legacy_entry = {
                'name': unit.chinese_name,
                'commander': unit.commander,
                'mineral_cost': unit.mineral_cost,
                'gas_cost': unit.gas_cost,
                'supply_cost': unit.supply_cost,
                'hp': unit.hp,
                'shields': unit.shields,
                'armor': unit.armor,
                'base_dps': base_dps,
                'range': range_value,
                'speed': unit.movement_speed,
                'abilities': [ability.name for ability in unit.abilities],
                'equivalent_cost': unit.equivalent_cost,
                'unit_type': '/'.join(unit.attributes)
            }
            
            legacy_data.append(legacy_entry)
            
        return legacy_data


# 使用示例
if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    # 加载数据
    loader = AdvancedDataLoader()
    database = loader.load_all_data()
    
    # 测试查询
    print(f"加载了 {len(database.units)} 个单位")
    
    # 获取吉姆·雷诺的陆战队员
    marine = database.get_unit("吉姆·雷诺", "Marine")
    if marine:
        print(f"\n{marine.chinese_name}:")
        print(f"  HP: {marine.hp}")
        print(f"  武器数: {len(marine.weapons)}")
        if marine.weapons:
            print(f"  主武器DPS: {marine.weapons[0].dps:.2f}")
    
    # 获取所有轻甲单位
    light_units = database.get_units_by_attribute("轻甲")
    print(f"\n轻甲单位数量: {len(light_units)}")