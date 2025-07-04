"""
精通和科技配置
定义各指挥官的精通加成和关键科技
"""

class MasteryConfig:
    """精通配置类"""
    
    # 各指挥官的精通配置
    COMMANDER_MASTERIES = {
        '诺娃': {
            'attack_speed': 0.15,  # 15%攻速
            'description': '解放者和渡鸦攻击速度+15%'
        },
        '阿拉纳克': {
            'attack_speed': 0.15,  # 15%攻速
            'description': '阿拉纳克单位攻击速度+15%'
        },
        '斯旺': {
            'mech_hp': 0.30,  # 30%机械生命值
            'description': '机械单位生命值+30%'
        },
        '德哈卡': {
            'primal_hp': 0.30,  # 30%原始虫族生命值
            'description': '原始虫族生命值+30%'
        },
        '阿塔尼斯': {
            'production_speed': 0.30,  # 30%生产速度
            'shield_regen': 0.15,     # 15%护盾回充
            'description': '生产速度+30%，护盾回充+15%'
        }
    }
    
    # 关键科技配置
    KEY_TECHNOLOGIES = {
        '天罚行者': {
            '献祭': {
                'attack_speed': 1.0,  # +100%攻速（速度翻倍）
                'description': '攻击速度+100%'
            }
        },
        '掠袭解放者': {
            '高级弹道': {
                'range': 4,  # +4射程
                'description': 'AG模式射程+4'
            }
        },
        '攻城坦克': {
            '钨钢钉': {
                'damage': 30,  # +30伤害（对主目标）
                'description': '攻城模式+30伤害'
            }
        }
    }
    
    @staticmethod
    def apply_mastery(base_stats, commander, unit_type=None):
        """
        应用精通加成
        
        Args:
            base_stats: 基础属性字典
            commander: 指挥官名称
            unit_type: 单位类型（用于特定判断）
            
        Returns:
            修正后的属性字典
        """
        stats = base_stats.copy()
        
        if commander not in MasteryConfig.COMMANDER_MASTERIES:
            return stats
        
        mastery = MasteryConfig.COMMANDER_MASTERIES[commander]
        
        # 应用攻速加成
        if 'attack_speed' in mastery and 'attack_interval' in stats:
            stats['attack_interval'] = stats['attack_interval'] / (1 + mastery['attack_speed'])
        
        # 应用生命值加成
        if commander == '斯旺' and 'mech_hp' in mastery:
            if unit_type and '机械' in unit_type:
                stats['hp'] = stats['hp'] * (1 + mastery['mech_hp'])
        
        if commander == '德哈卡' and 'primal_hp' in mastery:
            if unit_type and '原始' in unit_type:
                stats['hp'] = stats['hp'] * (1 + mastery['primal_hp'])
        
        return stats
    
    @staticmethod
    def apply_technology(base_stats, unit_name, tech_name):
        """
        应用科技加成
        
        Args:
            base_stats: 基础属性字典
            unit_name: 单位名称
            tech_name: 科技名称
            
        Returns:
            修正后的属性字典
        """
        stats = base_stats.copy()
        
        if unit_name not in MasteryConfig.KEY_TECHNOLOGIES:
            return stats
        
        if tech_name not in MasteryConfig.KEY_TECHNOLOGIES[unit_name]:
            return stats
        
        tech = MasteryConfig.KEY_TECHNOLOGIES[unit_name][tech_name]
        
        # 应用攻速加成
        if 'attack_speed' in tech and 'attack_interval' in stats:
            stats['attack_interval'] = stats['attack_interval'] / (1 + tech['attack_speed'])
        
        # 应用伤害加成
        if 'damage' in tech and 'base_damage' in stats:
            stats['base_damage'] = stats['base_damage'] + tech['damage']
        
        # 应用射程加成
        if 'range' in tech and 'range' in stats:
            stats['range'] = stats['range'] + tech['range']
        
        return stats


class StandardBuilds:
    """标准构建配置（常见的精通+科技组合）"""
    
    ELITE_BUILDS = {
        '掠袭解放者': {
            'name': '满级精通解放者',
            'masteries': ['attack_speed'],
            'technologies': ['高级弹道'],
            'upgrades': 3  # +3攻防
        },
        '天罚行者': {
            'name': '献祭天罚',
            'masteries': ['attack_speed'],
            'technologies': ['献祭'],
            'upgrades': 3
        },
        '攻城坦克': {
            'name': '钨钢钉坦克',
            'masteries': ['mech_hp'],
            'technologies': ['钨钢钉'],
            'upgrades': 3
        },
        '穿刺者': {
            'name': '进化穿刺者',
            'masteries': ['primal_hp'],
            'technologies': [],
            'upgrades': 3
        },
        '龙骑士': {
            'name': '快速龙骑',
            'masteries': ['production_speed', 'shield_regen'],
            'technologies': [],
            'upgrades': 3
        }
    }