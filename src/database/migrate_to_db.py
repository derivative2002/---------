"""
数据迁移脚本
将CSV数据迁移到SQLite数据库
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import logging
from typing import Dict
import json

from src.database.db_manager import DatabaseManager
from src.data.advanced_data_loader import AdvancedDataLoader
from src.data.models import CommanderConfig


class DataMigrator:
    """数据迁移器"""
    
    def __init__(self, db_path: str = "data/starcraft2.db", data_dir: str = "data/units"):
        self.db = DatabaseManager(db_path)
        self.loader = AdvancedDataLoader(data_dir)
        self.logger = logging.getLogger(__name__)
        self.commander_id_map: Dict[str, int] = {}
        
    def migrate_all(self):
        """执行完整的数据迁移"""
        self.logger.info("开始数据迁移...")
        
        # 1. 创建数据库表
        self.db.create_tables()
        
        # 2. 加载CSV数据
        database = self.loader.load_all_data()
        
        # 3. 迁移指挥官数据
        self._migrate_commanders(database.commanders)
        
        # 4. 迁移单位数据
        self._migrate_units(database.units)
        
        # 5. 创建备份
        backup_path = self.db.create_backup("initial_migration.db")
        
        self.logger.info(f"数据迁移完成！备份保存在: {backup_path}")
        
    def _migrate_commanders(self, commanders: Dict[str, CommanderConfig]):
        """迁移指挥官数据"""
        self.logger.info("迁移指挥官数据...")
        
        for name, config in commanders.items():
            commander_id = self.db.insert_commander(config)
            self.commander_id_map[name] = commander_id
            self.logger.info(f"  - {name}: ID={commander_id}")
            
    def _migrate_units(self, units: Dict[str, 'Unit']):
        """迁移单位数据"""
        self.logger.info(f"迁移 {len(units)} 个单位...")
        
        success_count = 0
        error_count = 0
        
        for unit_key, unit in units.items():
            try:
                # 获取指挥官ID
                commander_id = self.commander_id_map.get(unit.commander)
                if not commander_id:
                    self.logger.warning(f"未找到指挥官ID: {unit.commander}")
                    continue
                
                # 插入单位
                unit_id = self.db.insert_unit(unit, commander_id)
                success_count += 1
                
                self.logger.debug(f"  - {unit.chinese_name} ({unit.english_id}): ID={unit_id}")
                
            except Exception as e:
                error_count += 1
                self.logger.error(f"迁移单位失败 {unit.chinese_name}: {e}")
        
        self.logger.info(f"单位迁移完成: 成功={success_count}, 失败={error_count}")
    
    def verify_migration(self):
        """验证迁移结果"""
        self.logger.info("\n验证迁移结果...")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 统计各表数据
            tables = ['commanders', 'units', 'weapons', 'unit_attributes', 
                     'unit_modes', 'abilities']
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()['count']
                self.logger.info(f"  {table}: {count} 条记录")
            
            # 检查一些具体数据
            self.logger.info("\n数据抽样检查:")
            
            # 检查武器系统
            cursor.execute("""
                SELECT u.chinese_name, COUNT(w.id) as weapon_count
                FROM units u
                LEFT JOIN weapons w ON u.id = w.unit_id
                GROUP BY u.id
                HAVING weapon_count > 1
            """)
            
            multi_weapon_units = cursor.fetchall()
            if multi_weapon_units:
                self.logger.info("  多武器单位:")
                for row in multi_weapon_units:
                    self.logger.info(f"    - {row['chinese_name']}: {row['weapon_count']}个武器")
            
            # 检查模式切换单位
            cursor.execute("""
                SELECT u.chinese_name, COUNT(m.id) as mode_count
                FROM units u
                LEFT JOIN unit_modes m ON u.id = m.unit_id
                GROUP BY u.id
                HAVING mode_count > 0
            """)
            
            mode_units = cursor.fetchall()
            if mode_units:
                self.logger.info("  模式切换单位:")
                for row in mode_units:
                    self.logger.info(f"    - {row['chinese_name']}: {row['mode_count']}个模式")
    
    def test_queries(self):
        """测试一些查询"""
        self.logger.info("\n测试查询功能...")
        
        # 测试1: 查询重甲单位
        units = self.db.query_units({'attribute': '重甲'})
        self.logger.info(f"\n重甲单位: {len(units)}个")
        for unit in units[:3]:
            self.logger.info(f"  - {unit['chinese_name']} ({unit['commander_name']})")
        
        # 测试2: 查询高成本单位
        units = self.db.query_units({'min_cost': 500})
        self.logger.info(f"\n高成本单位(>500): {len(units)}个")
        for unit in units:
            cost = unit['mineral_cost'] + unit['gas_cost'] * 2.5
            self.logger.info(f"  - {unit['chinese_name']}: {cost:.0f}")
        
        # 测试3: 获取单位详情
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM units WHERE english_id = 'SiegeTank' LIMIT 1")
            row = cursor.fetchone()
            
            if row:
                unit_details = self.db.get_unit_details(row['id'])
                if unit_details:
                    self.logger.info(f"\n攻城坦克详细信息:")
                    self.logger.info(f"  - 武器数: {len(unit_details['weapons'])}")
                    self.logger.info(f"  - 模式数: {len(unit_details['modes'])}")
                    self.logger.info(f"  - 属性: {unit_details['attributes']}")


def main():
    """主函数"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    migrator = DataMigrator()
    
    # 执行迁移
    migrator.migrate_all()
    
    # 验证结果
    migrator.verify_migration()
    
    # 测试查询
    migrator.test_queries()


if __name__ == "__main__":
    main()