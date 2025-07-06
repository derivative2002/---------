#!/usr/bin/env python3
"""
合作任务数据导入脚本
将真正的合作任务单位数据导入到数据库中
"""

import csv
import sqlite3
from pathlib import Path


def create_coop_units_table(cursor):
    """创建合作任务单位表"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coop_units (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            english_id TEXT NOT NULL,
            chinese_name TEXT NOT NULL,
            base_unit TEXT,
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
            attributes TEXT,
            special_abilities TEXT,
            mastery_bonuses TEXT,
            commander_level INTEGER DEFAULT 90,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (commander_id) REFERENCES commanders(id),
            UNIQUE(commander_id, english_id)
        );
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_coop_units_commander ON coop_units(commander_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_coop_units_base ON coop_units(base_unit);")


def get_commander_id(cursor, commander_name: str) -> int:
    """获取或创建指挥官ID"""
    cursor.execute("SELECT id FROM commanders WHERE name = ?", (commander_name,))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    
    # 如果指挥官不存在，创建一个
    cursor.execute("""
        INSERT INTO commanders (name, population_cap, special_mechanics)
        VALUES (?, 200, '{}')
    """, (commander_name, ))
    
    return cursor.lastrowid


def import_coop_units(csv_file: str, db_path: str = "data/starcraft2.db"):
    """导入合作任务单位数据"""
    csv_path = Path(csv_file)
    if not csv_path.exists():
        print(f"错误: CSV文件不存在: {csv_file}")
        return False
    
    db_file = Path(db_path)
    if not db_file.exists():
        print(f"错误: 数据库文件不存在: {db_path}")
        return False
    
    print(f"正在导入合作任务数据: {csv_file} -> {db_path}")
    
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    
    try:
        # 创建合作任务单位表
        create_coop_units_table(cursor)
        
        imported_count = 0
        skipped_count = 0
        
        with open(csv_path, 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                try:
                    # 获取指挥官ID
                    commander_id = get_commander_id(cursor, row['commander'])
                    
                    # 检查单位是否已存在
                    cursor.execute("""
                        SELECT id FROM coop_units WHERE english_id = ? AND commander_id = ?
                    """, (row['english_id'], commander_id))
                    
                    if cursor.fetchone():
                        print(f"合作任务单位 '{row['chinese_name']}' 已存在，跳过")
                        skipped_count += 1
                        continue
                    
                    # 插入合作任务单位数据
                    cursor.execute("""
                        INSERT INTO coop_units (
                            english_id, chinese_name, base_unit, commander_id,
                            mineral_cost, gas_cost, supply_cost,
                            hp, shields, armor, collision_radius,
                            movement_speed, is_flying, attributes,
                            special_abilities, mastery_bonuses, commander_level
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        row['english_id'],
                        row['chinese_name'],
                        row.get('base_unit', ''),
                        commander_id,
                        int(row['mineral_cost']),
                        int(row['gas_cost']),
                        float(row['supply_cost']),
                        int(row['hp']),
                        int(row['shields']),
                        int(row['armor']),
                        float(row['collision_radius']),
                        float(row['movement_speed']),
                        1 if row['is_flying'].upper() == 'TRUE' else 0,
                        row.get('attributes', ''),
                        row.get('special_abilities', '[]'),
                        row.get('mastery_bonuses', ''),
                        int(row.get('commander_level', 90))
                    ))
                    
                    unit_id = cursor.lastrowid
                    print(f"✓ 导入合作任务单位: {row['chinese_name']} (ID: {unit_id})")
                    imported_count += 1
                    
                except Exception as e:
                    print(f"处理行时出错: {row.get('chinese_name', 'Unknown')}: {e}")
                    skipped_count += 1
                    continue
        
        # 提交事务
        conn.commit()
        
    except Exception as e:
        print(f"导入过程中出错: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()
    
    print(f"\n合作任务数据导入完成:")
    print(f"成功导入: {imported_count} 个单位")
    print(f"跳过: {skipped_count} 个单位")
    
    return imported_count > 0


def verify_coop_import(db_path: str = "data/starcraft2.db"):
    """验证合作任务数据导入"""
    db_file = Path(db_path)
    if not db_file.exists():
        print(f"数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    
    try:
        # 检查表是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='coop_units';
        """)
        
        if not cursor.fetchone():
            print("合作任务单位表不存在")
            return
        
        # 统计合作任务单位数量
        cursor.execute("SELECT COUNT(*) FROM coop_units")
        total_coop_units = cursor.fetchone()[0]
        
        # 按指挥官统计
        cursor.execute("""
            SELECT c.name, COUNT(cu.id) as unit_count
            FROM commanders c
            LEFT JOIN coop_units cu ON c.id = cu.commander_id
            GROUP BY c.id, c.name
            HAVING unit_count > 0
            ORDER BY unit_count DESC
        """)
        
        commander_stats = cursor.fetchall()
        
        print(f"\n=== 合作任务数据库验证结果 ===")
        print(f"合作任务单位总数: {total_coop_units}")
        print(f"有单位的指挥官数: {len(commander_stats)}")
        
        print("\n各指挥官合作任务单位数:")
        for commander_name, unit_count in commander_stats:
            print(f"  {commander_name}: {unit_count} 个单位")
        
        # 显示特殊单位
        cursor.execute("""
            SELECT cu.chinese_name, c.name as commander, cu.base_unit, cu.mastery_bonuses
            FROM coop_units cu
            JOIN commanders c ON cu.commander_id = c.id
            WHERE cu.base_unit IN ('TychusHero', 'BlazeHero', 'Destroyer', 'Ascendant', 'InfestedMarine', 'PrimalZergling')
            OR cu.chinese_name LIKE '%英雄%' 
            OR cu.chinese_name LIKE '%感染%'
            OR cu.chinese_name LIKE '%原始%'
            ORDER BY c.name
        """)
        
        special_units = cursor.fetchall()
        
        if special_units:
            print("\n特有/英雄单位:")
            for unit_name, commander, base_unit, mastery in special_units:
                print(f"  {unit_name} ({commander}) - 基于: {base_unit}")
        
        # 对比标准单位
        cursor.execute("SELECT COUNT(*) FROM units")
        standard_units = cursor.fetchone()[0]
        
        print(f"\n数据对比:")
        print(f"标准单位: {standard_units} 个")
        print(f"合作任务单位: {total_coop_units} 个")
        
        # 显示增强版单位示例
        cursor.execute("""
            SELECT cu.chinese_name, cu.hp, cu.armor, cu.mastery_bonuses
            FROM coop_units cu
            WHERE cu.chinese_name LIKE '%增强%' OR cu.chinese_name LIKE '%进化%' OR cu.chinese_name LIKE '%老兵%'
            LIMIT 5
        """)
        
        enhanced_units = cursor.fetchall()
        
        if enhanced_units:
            print("\n增强版单位示例:")
            for unit_name, hp, armor, mastery in enhanced_units:
                print(f"  {unit_name} - HP:{hp}, 护甲:{armor}")
                print(f"    精通: {mastery}")
            
    finally:
        conn.close()


def compare_standard_vs_coop(db_path: str = "data/starcraft2.db"):
    """对比标准单位与合作任务单位"""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        print(f"\n=== 标准单位 vs 合作任务单位对比 ===")
        
        # 查找可对比的单位
        cursor.execute("""
            SELECT 
                u.chinese_name as std_name,
                u.hp as std_hp,
                u.armor as std_armor,
                cu.chinese_name as coop_name,
                cu.hp as coop_hp,
                cu.armor as coop_armor,
                cu.mastery_bonuses
            FROM units u
            JOIN coop_units cu ON cu.base_unit = u.english_id
            WHERE u.commander_id = cu.commander_id
            ORDER BY u.chinese_name
        """)
        
        comparisons = cursor.fetchall()
        
        if comparisons:
            print("\n单位属性对比:")
            for std_name, std_hp, std_armor, coop_name, coop_hp, coop_armor, mastery in comparisons:
                hp_diff = coop_hp - std_hp
                armor_diff = coop_armor - std_armor
                
                print(f"\n{std_name} -> {coop_name}")
                print(f"  HP: {std_hp} -> {coop_hp} ({hp_diff:+d})")
                print(f"  护甲: {std_armor} -> {coop_armor} ({armor_diff:+d})")
                if mastery:
                    print(f"  精通: {mastery}")
        else:
            print("未找到可对比的单位")
            
    except Exception as e:
        print(f"对比过程出错: {e}")
    finally:
        conn.close()


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) != 2:
        print("用法: python import_coop_data.py <coop_csv_file>")
        return
    
    csv_file = sys.argv[1]
    
    # 导入合作任务数据
    success = import_coop_units(csv_file)
    
    if success:
        print("\n✅ 合作任务数据导入成功！")
        # 验证导入结果
        verify_coop_import()
        # 对比分析
        compare_standard_vs_coop()
    else:
        print("\n❌ 合作任务数据导入失败！")


if __name__ == "__main__":
    main()