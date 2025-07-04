"""
数据库管理器
处理SQLite数据库的创建、连接和基础操作
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from contextlib import contextmanager
import logging
from datetime import datetime

from ..data.models import Unit, Weapon, Ability, UnitMode, CommanderConfig


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = "data/starcraft2.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # 返回字典形式的结果
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            conn.close()
    
    def create_tables(self):
        """创建数据库表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 启用外键约束
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # 创建指挥官表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS commanders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    population_cap INTEGER DEFAULT 200,
                    modifiers TEXT,  -- JSON
                    special_mechanics TEXT,  -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建单位表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS units (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    english_id TEXT NOT NULL,
                    chinese_name TEXT NOT NULL,
                    commander_id INTEGER NOT NULL,
                    mineral_cost INTEGER NOT NULL,
                    gas_cost INTEGER NOT NULL,
                    supply_cost REAL NOT NULL,
                    hp INTEGER NOT NULL,
                    shields INTEGER DEFAULT 0,
                    armor INTEGER DEFAULT 0,
                    collision_radius REAL,
                    movement_speed REAL NOT NULL,
                    is_flying INTEGER DEFAULT 0,
                    production_time REAL,
                    tech_requirements TEXT,  -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (commander_id) REFERENCES commanders(id),
                    UNIQUE(commander_id, english_id)
                )
            """)
            
            # 创建单位属性表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS unit_attributes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unit_id INTEGER NOT NULL,
                    attribute TEXT NOT NULL,
                    FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE,
                    UNIQUE(unit_id, attribute)
                )
            """)
            
            # 创建武器表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weapons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unit_id INTEGER NOT NULL,
                    weapon_name TEXT NOT NULL,
                    weapon_type TEXT CHECK(weapon_type IN ('ground', 'air', 'both')),
                    base_damage REAL NOT NULL,
                    attack_count INTEGER DEFAULT 1,
                    attack_interval REAL NOT NULL,
                    range REAL NOT NULL,
                    splash_type TEXT CHECK(splash_type IN ('none', 'linear', 'circular', 'cone')),
                    splash_params TEXT,  -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE
                )
            """)
            
            # 创建武器加成表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weapon_bonuses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    weapon_id INTEGER NOT NULL,
                    target_attribute TEXT NOT NULL,
                    bonus_damage REAL NOT NULL,
                    FOREIGN KEY (weapon_id) REFERENCES weapons(id) ON DELETE CASCADE,
                    UNIQUE(weapon_id, target_attribute)
                )
            """)
            
            # 创建单位模式表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS unit_modes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unit_id INTEGER NOT NULL,
                    mode_name TEXT NOT NULL,
                    mode_type TEXT CHECK(mode_type IN ('default', 'alternate')),
                    stat_modifiers TEXT,  -- JSON
                    weapon_config TEXT,
                    switch_time REAL DEFAULT 0,
                    FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE,
                    UNIQUE(unit_id, mode_name)
                )
            """)
            
            # 创建能力表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS abilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unit_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT CHECK(type IN ('active', 'passive', 'toggle')),
                    cost_energy REAL DEFAULT 0,
                    cost_hp REAL DEFAULT 0,
                    cooldown REAL DEFAULT 0,
                    effect TEXT,  -- JSON
                    target TEXT DEFAULT 'self',
                    range REAL DEFAULT 0,
                    radius REAL DEFAULT 0,
                    FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE
                )
            """)
            
            # 创建版本管理表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS balance_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT UNIQUE NOT NULL,
                    patch_date DATE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建平衡历史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS unit_balance_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unit_id INTEGER NOT NULL,
                    version_id INTEGER NOT NULL,
                    field_name TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    change_reason TEXT,
                    FOREIGN KEY (unit_id) REFERENCES units(id),
                    FOREIGN KEY (version_id) REFERENCES balance_versions(id)
                )
            """)
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_units_commander ON units(commander_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_units_cost ON units(mineral_cost, gas_cost)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_weapons_unit ON weapons(unit_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_attributes_unit ON unit_attributes(unit_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_attributes_value ON unit_attributes(attribute)")
            
            self.logger.info("数据库表创建成功")
    
    def insert_commander(self, commander: CommanderConfig) -> int:
        """插入指挥官数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO commanders (name, population_cap, modifiers, special_mechanics)
                VALUES (?, ?, ?, ?)
            """, (
                commander.name,
                commander.population_cap,
                json.dumps(commander.modifiers, ensure_ascii=False),
                json.dumps(commander.special_mechanics, ensure_ascii=False)
            ))
            return cursor.lastrowid
    
    def insert_unit(self, unit: Unit, commander_id: int) -> int:
        """插入单位数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 插入单位主数据
            cursor.execute("""
                INSERT INTO units (
                    english_id, chinese_name, commander_id,
                    mineral_cost, gas_cost, supply_cost,
                    hp, shields, armor, collision_radius,
                    movement_speed, is_flying
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                unit.english_id, unit.chinese_name, commander_id,
                unit.mineral_cost, unit.gas_cost, unit.supply_cost,
                unit.hp, unit.shields, unit.armor, unit.collision_radius,
                unit.movement_speed, int(unit.is_flying)
            ))
            unit_id = cursor.lastrowid
            
            # 插入属性
            for attr in unit.attributes:
                cursor.execute("""
                    INSERT INTO unit_attributes (unit_id, attribute)
                    VALUES (?, ?)
                """, (unit_id, attr))
            
            # 插入武器
            for weapon in unit.weapons:
                self._insert_weapon(cursor, unit_id, weapon)
            
            # 插入模式
            for mode in unit.modes:
                self._insert_mode(cursor, unit_id, mode)
            
            # 插入能力
            for ability in unit.abilities:
                self._insert_ability(cursor, unit_id, ability)
            
            return unit_id
    
    def _insert_weapon(self, cursor, unit_id: int, weapon: Weapon):
        """插入武器数据"""
        splash_params = None
        if weapon.splash_params:
            splash_params = json.dumps({
                'radius': weapon.splash_params.radius,
                'damage': weapon.splash_params.damage,
                'angle': weapon.splash_params.angle
            })
        
        cursor.execute("""
            INSERT INTO weapons (
                unit_id, weapon_name, weapon_type,
                base_damage, attack_count, attack_interval,
                range, splash_type, splash_params
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            unit_id, weapon.weapon_name, weapon.weapon_type.value,
            weapon.base_damage, weapon.attack_count, weapon.attack_interval,
            weapon.range, weapon.splash_type.value, splash_params
        ))
        weapon_id = cursor.lastrowid
        
        # 插入伤害加成
        for attr, bonus in weapon.bonus_damage.items():
            cursor.execute("""
                INSERT INTO weapon_bonuses (weapon_id, target_attribute, bonus_damage)
                VALUES (?, ?, ?)
            """, (weapon_id, attr, bonus))
    
    def _insert_mode(self, cursor, unit_id: int, mode: UnitMode):
        """插入模式数据"""
        cursor.execute("""
            INSERT INTO unit_modes (
                unit_id, mode_name, mode_type,
                stat_modifiers, weapon_config, switch_time
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            unit_id, mode.mode_name, mode.mode_type.value,
            json.dumps(mode.stat_modifiers, ensure_ascii=False),
            mode.weapon_config, mode.switch_time
        ))
    
    def _insert_ability(self, cursor, unit_id: int, ability: Ability):
        """插入能力数据"""
        effect = {
            'damage': ability.effect.damage,
            'heal': ability.effect.heal,
            'buff': ability.effect.buff,
            'debuff': ability.effect.debuff
        }
        
        cursor.execute("""
            INSERT INTO abilities (
                unit_id, name, type,
                cost_energy, cost_hp, cooldown,
                effect, target, range, radius
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            unit_id, ability.name, ability.type.value,
            ability.cost.energy, ability.cost.hp, ability.cost.cooldown,
            json.dumps(effect, ensure_ascii=False),
            ability.target, ability.range, ability.radius
        ))
    
    def get_commander_id(self, name: str) -> Optional[int]:
        """获取指挥官ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM commanders WHERE name = ?", (name,))
            row = cursor.fetchone()
            return row['id'] if row else None
    
    def query_units(self, filters: Dict[str, Any] = None) -> List[Dict]:
        """查询单位"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT u.*, c.name as commander_name
                FROM units u
                JOIN commanders c ON u.commander_id = c.id
                WHERE 1=1
            """
            params = []
            
            if filters:
                if 'commander' in filters:
                    query += " AND c.name = ?"
                    params.append(filters['commander'])
                
                if 'min_cost' in filters:
                    query += " AND (u.mineral_cost + u.gas_cost * 2.5) >= ?"
                    params.append(filters['min_cost'])
                
                if 'max_cost' in filters:
                    query += " AND (u.mineral_cost + u.gas_cost * 2.5) <= ?"
                    params.append(filters['max_cost'])
                
                if 'attribute' in filters:
                    query += """
                        AND EXISTS (
                            SELECT 1 FROM unit_attributes ua
                            WHERE ua.unit_id = u.id AND ua.attribute = ?
                        )
                    """
                    params.append(filters['attribute'])
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_unit_details(self, unit_id: int) -> Optional[Dict]:
        """获取单位详细信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 获取单位基础信息
            cursor.execute("""
                SELECT u.*, c.name as commander_name, c.modifiers as commander_modifiers
                FROM units u
                JOIN commanders c ON u.commander_id = c.id
                WHERE u.id = ?
            """, (unit_id,))
            unit = cursor.fetchone()
            if not unit:
                return None
            
            unit_dict = dict(unit)
            
            # 获取属性
            cursor.execute("""
                SELECT attribute FROM unit_attributes WHERE unit_id = ?
            """, (unit_id,))
            unit_dict['attributes'] = [row['attribute'] for row in cursor.fetchall()]
            
            # 获取武器
            cursor.execute("""
                SELECT * FROM weapons WHERE unit_id = ?
            """, (unit_id,))
            weapons = []
            for weapon_row in cursor.fetchall():
                weapon = dict(weapon_row)
                
                # 获取武器加成
                cursor.execute("""
                    SELECT target_attribute, bonus_damage
                    FROM weapon_bonuses WHERE weapon_id = ?
                """, (weapon_row['id'],))
                weapon['bonuses'] = {row['target_attribute']: row['bonus_damage'] 
                                   for row in cursor.fetchall()}
                
                weapons.append(weapon)
            unit_dict['weapons'] = weapons
            
            # 获取模式
            cursor.execute("""
                SELECT * FROM unit_modes WHERE unit_id = ?
            """, (unit_id,))
            unit_dict['modes'] = [dict(row) for row in cursor.fetchall()]
            
            # 获取能力
            cursor.execute("""
                SELECT * FROM abilities WHERE unit_id = ?
            """, (unit_id,))
            unit_dict['abilities'] = [dict(row) for row in cursor.fetchall()]
            
            return unit_dict
    
    def create_backup(self, backup_name: str = None):
        """创建数据库备份"""
        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        backup_path = self.db_path.parent / "backups" / backup_name
        backup_path.parent.mkdir(exist_ok=True)
        
        with self.get_connection() as conn:
            backup_conn = sqlite3.connect(str(backup_path))
            conn.backup(backup_conn)
            backup_conn.close()
        
        self.logger.info(f"数据库备份创建成功: {backup_path}")
        return backup_path


# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 创建数据库管理器
    db = DatabaseManager()
    
    # 创建表
    db.create_tables()
    
    # 测试插入指挥官
    commander = CommanderConfig(
        name="吉姆·雷诺",
        population_cap=200,
        modifiers={'hp': 1.0, 'damage': 1.0},
        special_mechanics=["医疗兵", "钒合金板"]
    )
    commander_id = db.insert_commander(commander)
    print(f"插入指挥官: {commander.name}, ID: {commander_id}")
    
    # 查询测试
    units = db.query_units({'commander': '吉姆·雷诺'})
    print(f"查询到 {len(units)} 个单位")