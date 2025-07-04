"""
数据库查询接口
提供高级查询功能和分析
"""

import sqlite3
from typing import List, Dict, Optional, Tuple
import pandas as pd
from pathlib import Path

from .db_manager import DatabaseManager


class QueryInterface:
    """数据库查询接口"""
    
    def __init__(self, db_path: str = "data/starcraft2.db"):
        self.db = DatabaseManager(db_path)
        
    def find_counter_units(self, target_attribute: str, min_bonus: float = 5) -> pd.DataFrame:
        """查找对特定属性有克制的单位"""
        with self.db.get_connection() as conn:
            query = """
                SELECT DISTINCT 
                    u.chinese_name,
                    c.name as commander,
                    w.weapon_name,
                    wb.bonus_damage,
                    w.base_damage,
                    (w.base_damage * w.attack_count) / w.attack_interval as dps,
                    ((w.base_damage + wb.bonus_damage) * w.attack_count) / w.attack_interval as bonus_dps
                FROM units u
                JOIN commanders c ON u.commander_id = c.id
                JOIN weapons w ON u.id = w.unit_id
                JOIN weapon_bonuses wb ON w.id = wb.weapon_id
                WHERE wb.target_attribute = ? AND wb.bonus_damage >= ?
                ORDER BY wb.bonus_damage DESC
            """
            
            df = pd.read_sql_query(query, conn, params=(target_attribute, min_bonus))
            return df
    
    def analyze_cost_efficiency(self, phase: str = 'mid') -> pd.DataFrame:
        """分析成本效率"""
        # 根据游戏阶段设置λ值
        lambda_values = {'early': 0.2, 'mid': 0.5, 'late': 0.8}
        lambda_val = lambda_values.get(phase, 0.5)
        
        with self.db.get_connection() as conn:
            query = """
                SELECT 
                    u.chinese_name,
                    c.name as commander,
                    u.mineral_cost,
                    u.gas_cost,
                    u.supply_cost,
                    u.mineral_cost + u.gas_cost * 2.5 as base_cost,
                    u.mineral_cost + u.gas_cost * 2.5 + u.supply_cost * 25 * ? as effective_cost,
                    SUM((w.base_damage * w.attack_count) / w.attack_interval) as total_dps,
                    u.hp + u.shields as total_hp,
                    u.hp + u.shields + u.armor * 10 as effective_hp
                FROM units u
                JOIN commanders c ON u.commander_id = c.id
                LEFT JOIN weapons w ON u.id = w.unit_id
                GROUP BY u.id
                HAVING total_dps > 0
            """
            
            df = pd.read_sql_query(query, conn, params=(lambda_val,))
            
            # 计算CEV
            df['cev'] = (df['total_dps'] * df['effective_hp']) / df['effective_cost']
            df['dps_per_cost'] = df['total_dps'] / df['effective_cost']
            df['hp_per_cost'] = df['effective_hp'] / df['effective_cost']
            
            return df.sort_values('cev', ascending=False)
    
    def find_synergistic_units(self, unit_name: str) -> pd.DataFrame:
        """查找与指定单位有协同效应的单位"""
        with self.db.get_connection() as conn:
            # 首先获取单位信息
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.*, GROUP_CONCAT(ua.attribute) as attributes
                FROM units u
                LEFT JOIN unit_attributes ua ON u.id = ua.unit_id
                WHERE u.chinese_name = ?
                GROUP BY u.id
            """, (unit_name,))
            
            target_unit = cursor.fetchone()
            if not target_unit:
                return pd.DataFrame()
            
            # 分析可能的协同
            synergies = []
            
            # 1. 如果是地面单位，找防空单位
            if not target_unit['is_flying']:
                query = """
                    SELECT u.chinese_name, c.name as commander, 'Anti-Air' as synergy_type
                    FROM units u
                    JOIN commanders c ON u.commander_id = c.id
                    JOIN weapons w ON u.id = w.unit_id
                    WHERE w.weapon_type IN ('air', 'both')
                    AND u.commander_id = ?
                """
                df_aa = pd.read_sql_query(query, conn, params=(target_unit['commander_id'],))
                synergies.append(df_aa)
            
            # 2. 如果HP低，找治疗单位
            if target_unit['hp'] < 200:
                query = """
                    SELECT DISTINCT u.chinese_name, c.name as commander, 'Healing' as synergy_type
                    FROM units u
                    JOIN commanders c ON u.commander_id = c.id
                    JOIN abilities a ON u.id = a.unit_id
                    WHERE a.effect LIKE '%"heal":%' AND a.effect NOT LIKE '%"heal":0%'
                """
                df_heal = pd.read_sql_query(query, conn)
                if not df_heal.empty:
                    synergies.append(df_heal)
            
            # 3. 如果是重甲，找能提供增益的单位
            if target_unit['attributes'] and '重甲' in target_unit['attributes']:
                query = """
                    SELECT DISTINCT u.chinese_name, c.name as commander, 'Buff' as synergy_type
                    FROM units u
                    JOIN commanders c ON u.commander_id = c.id
                    JOIN abilities a ON u.id = a.unit_id
                    WHERE a.effect LIKE '%"buff":%' 
                    AND a.target IN ('ally', 'all')
                """
                df_buff = pd.read_sql_query(query, conn)
                if not df_buff.empty:
                    synergies.append(df_buff)
            
            return pd.concat(synergies, ignore_index=True) if synergies else pd.DataFrame()
    
    def get_balance_recommendations(self) -> List[Dict]:
        """获取平衡性建议"""
        recommendations = []
        
        with self.db.get_connection() as conn:
            # 1. 检查极端CEV值
            query = """
                WITH unit_cev AS (
                    SELECT 
                        u.id,
                        u.chinese_name,
                        c.name as commander,
                        u.mineral_cost + u.gas_cost * 2.5 as cost,
                        SUM((w.base_damage * w.attack_count) / w.attack_interval) as dps,
                        u.hp + u.shields as hp,
                        (SUM((w.base_damage * w.attack_count) / w.attack_interval) * (u.hp + u.shields)) 
                        / NULLIF(u.mineral_cost + u.gas_cost * 2.5, 0) as cev
                    FROM units u
                    JOIN commanders c ON u.commander_id = c.id
                    LEFT JOIN weapons w ON u.id = w.unit_id
                    WHERE u.mineral_cost + u.gas_cost > 0
                    GROUP BY u.id
                )
                SELECT * FROM unit_cev
                WHERE cev IS NOT NULL
                ORDER BY cev DESC
            """
            
            df_cev = pd.read_sql_query(query, conn)
            
            # 检查CEV过高的单位
            high_cev_units = df_cev[df_cev['cev'] > df_cev['cev'].quantile(0.95)]
            for _, unit in high_cev_units.iterrows():
                recommendations.append({
                    'type': 'high_cev',
                    'unit': unit['chinese_name'],
                    'commander': unit['commander'],
                    'current_cev': unit['cev'],
                    'suggestion': f"考虑降低DPS或增加成本，当前CEV({unit['cev']:.1f})显著高于平均水平"
                })
            
            # 检查CEV过低的单位
            low_cev_units = df_cev[df_cev['cev'] < df_cev['cev'].quantile(0.05)]
            for _, unit in low_cev_units.iterrows():
                recommendations.append({
                    'type': 'low_cev',
                    'unit': unit['chinese_name'],
                    'commander': unit['commander'],
                    'current_cev': unit['cev'],
                    'suggestion': f"考虑增强战斗力或降低成本，当前CEV({unit['cev']:.1f})过低"
                })
            
            # 2. 检查武器系统平衡
            query = """
                SELECT 
                    u.chinese_name,
                    COUNT(w.id) as weapon_count,
                    MAX(w.range) - MIN(w.range) as range_diff
                FROM units u
                LEFT JOIN weapons w ON u.id = w.unit_id
                GROUP BY u.id
                HAVING weapon_count > 1 AND range_diff > 5
            """
            
            df_weapons = pd.read_sql_query(query, conn)
            for _, unit in df_weapons.iterrows():
                recommendations.append({
                    'type': 'weapon_imbalance',
                    'unit': unit['chinese_name'],
                    'issue': f"武器射程差异过大({unit['range_diff']:.1f})，可能导致使用困难"
                })
        
        return recommendations
    
    def export_analysis_report(self, output_path: str = "analysis_report.xlsx"):
        """导出综合分析报告"""
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 1. 单位总览
            overview_df = self.analyze_cost_efficiency('mid')
            overview_df.to_excel(writer, sheet_name='单位总览', index=False)
            
            # 2. 克制关系
            attributes = ['轻甲', '重甲', '生物', '机械']
            for attr in attributes:
                counter_df = self.find_counter_units(attr)
                if not counter_df.empty:
                    counter_df.to_excel(writer, sheet_name=f'克制{attr}', index=False)
            
            # 3. 指挥官统计
            with self.db.get_connection() as conn:
                query = """
                    SELECT 
                        c.name as commander,
                        COUNT(DISTINCT u.id) as unit_count,
                        AVG(u.mineral_cost + u.gas_cost * 2.5) as avg_cost,
                        AVG(u.supply_cost) as avg_supply,
                        AVG(u.hp + u.shields) as avg_hp,
                        COUNT(DISTINCT w.id) as total_weapons,
                        COUNT(DISTINCT a.id) as total_abilities
                    FROM commanders c
                    LEFT JOIN units u ON c.id = u.commander_id
                    LEFT JOIN weapons w ON u.id = w.unit_id
                    LEFT JOIN abilities a ON u.id = a.unit_id
                    GROUP BY c.id
                """
                commander_df = pd.read_sql_query(query, conn)
                commander_df.to_excel(writer, sheet_name='指挥官统计', index=False)
        
        print(f"分析报告已导出到: {output_path}")


# 使用示例
if __name__ == "__main__":
    qi = QueryInterface()
    
    print("=== 数据库查询接口测试 ===\n")
    
    # 1. 查找克制重甲的单位
    print("1. 克制重甲的单位:")
    df_counter = qi.find_counter_units('重甲', min_bonus=10)
    print(df_counter[['chinese_name', 'commander', 'weapon_name', 'bonus_damage']].head())
    
    # 2. 分析成本效率
    print("\n2. 成本效率Top 5:")
    df_efficiency = qi.analyze_cost_efficiency('mid')
    print(df_efficiency[['chinese_name', 'commander', 'cev', 'dps_per_cost']].head())
    
    # 3. 查找协同单位
    print("\n3. 与陆战队员的协同单位:")
    df_synergy = qi.find_synergistic_units('陆战队员')
    if not df_synergy.empty:
        print(df_synergy)
    
    # 4. 获取平衡建议
    print("\n4. 平衡性建议:")
    recommendations = qi.get_balance_recommendations()
    for rec in recommendations[:3]:
        print(f"  - {rec['type']}: {rec.get('unit', 'N/A')} - {rec.get('suggestion', rec.get('issue', ''))}")
    
    # 5. 导出报告
    qi.export_analysis_report()