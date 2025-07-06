"""
标准化埃蒙部队（SAC）数据加载器
用于v2.3模型的PvE评估基准
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class SACUnit:
    """SAC中的单个单位"""
    name: str
    english_id: str
    weight: float
    hp: int
    shield: int
    armor: int
    attributes: List[str]
    supply: int
    
    def get_ehp(self) -> float:
        """计算该单位的有效生命值"""
        # 护甲减伤
        if self.armor > 0:
            armor_reduction = self.armor / (self.armor + 10)
            effective_hp = self.hp / (1 - armor_reduction)
        else:
            effective_hp = self.hp
        
        # 护盾（简化处理）
        return effective_hp + self.shield


@dataclass
class SACComposition:
    """标准化埃蒙部队组合"""
    name: str
    description: str
    core_units: List[SACUnit]
    attribute_distribution: Dict[str, float]
    ehp_per_supply: float
    threat_profile: Dict[str, Any]
    tactical_notes: List[str]
    
    def get_weighted_ehp(self) -> float:
        """计算加权平均EHP"""
        total_ehp = 0
        total_weight = 0
        
        for unit in self.core_units:
            unit_ehp = unit.get_ehp()
            total_ehp += unit_ehp * unit.weight
            total_weight += unit.weight
        
        return total_ehp / total_weight if total_weight > 0 else 0
    
    def get_attribute_coverage(self, attribute: str) -> float:
        """获取特定属性的覆盖率"""
        return self.attribute_distribution.get(attribute, 0.0)
    
    def is_vulnerable_to(self, damage_type: str) -> bool:
        """判断是否对某种伤害类型脆弱"""
        if damage_type == "对空" and "空中威胁" in self.threat_profile.get('primary', ''):
            return True
        if damage_type == "AOE" and any("密集" in note for note in self.tactical_notes):
            return True
        return False


class SACLoader:
    """SAC数据加载器"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        初始化SAC加载器
        
        Args:
            config_path: SAC配置文件路径，默认使用项目内置路径
        """
        if config_path is None:
            config_path = Path(__file__).parent / "standard_amon_compositions.yaml"
        
        self.config_path = config_path
        self._compositions: Dict[str, SACComposition] = {}
        self._evaluation_settings: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """加载SAC配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 解析SAC组合
            compositions_data = config.get('compositions', {})
            for sac_id, sac_data in compositions_data.items():
                self._compositions[sac_id] = self._parse_composition(sac_data)
            
            # 解析评估设置
            self._evaluation_settings = config.get('evaluation_settings', {})
            
        except FileNotFoundError:
            raise FileNotFoundError(f"SAC配置文件未找到: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"SAC配置文件格式错误: {e}")
    
    def _parse_composition(self, sac_data: Dict[str, Any]) -> SACComposition:
        """解析单个SAC组合数据"""
        # 解析核心单位
        core_units = []
        for unit_data in sac_data.get('core_units', []):
            unit = SACUnit(
                name=unit_data['name'],
                english_id=unit_data['english_id'],
                weight=unit_data['weight'],
                hp=unit_data['hp'],
                shield=unit_data['shield'],
                armor=unit_data['armor'],
                attributes=unit_data['attributes'],
                supply=unit_data['supply']
            )
            core_units.append(unit)
        
        return SACComposition(
            name=sac_data['name'],
            description=sac_data['description'],
            core_units=core_units,
            attribute_distribution=sac_data['attribute_distribution'],
            ehp_per_supply=sac_data['ehp_per_supply'],
            threat_profile=sac_data['threat_profile'],
            tactical_notes=sac_data['tactical_notes']
        )
    
    def get_composition(self, sac_id: str) -> SACComposition:
        """获取指定的SAC组合"""
        if sac_id not in self._compositions:
            raise ValueError(f"未知的SAC ID: {sac_id}")
        return self._compositions[sac_id]
    
    def list_compositions(self) -> List[str]:
        """列出所有可用的SAC组合ID"""
        return list(self._compositions.keys())
    
    def get_all_compositions(self) -> Dict[str, SACComposition]:
        """获取所有SAC组合"""
        return self._compositions.copy()
    
    def get_evaluation_settings(self) -> Dict[str, Any]:
        """获取评估设置"""
        return self._evaluation_settings.copy()
    
    def calculate_mixed_damage_multiplier(self, sac_id: str, bonus_damage: Dict[str, float]) -> float:
        """
        计算对SAC的混合伤害乘数
        
        Args:
            sac_id: SAC组合ID
            bonus_damage: 属性加成伤害字典，如 {"重甲": 10, "生物": 5}
        
        Returns:
            混合伤害乘数
        """
        sac = self.get_composition(sac_id)
        total_multiplier = 1.0
        
        for attribute, bonus in bonus_damage.items():
            coverage = sac.get_attribute_coverage(attribute)
            if coverage > 0:
                # 加成伤害按覆盖率加权
                total_multiplier += (bonus / 100) * coverage
        
        return total_multiplier
    
    def get_counter_recommendations(self, sac_id: str) -> Dict[str, List[str]]:
        """获取对抗特定SAC的推荐策略"""
        sac = self.get_composition(sac_id)
        
        return {
            'countered_by': sac.threat_profile.get('countered_by', []),
            'tactical_notes': sac.tactical_notes,
            'vulnerable_attributes': [
                attr for attr, coverage in sac.attribute_distribution.items()
                if coverage > 0.5  # 超过50%覆盖率的属性
            ]
        }
    
    def validate_config(self) -> List[str]:
        """验证配置文件的完整性"""
        errors = []
        
        for sac_id, sac in self._compositions.items():
            # 检查权重总和
            total_weight = sum(unit.weight for unit in sac.core_units)
            if abs(total_weight - 1.0) > 0.01:
                errors.append(f"{sac_id}: 单位权重总和不等于1.0 ({total_weight})")
            
            # 检查属性分布
            for attr, coverage in sac.attribute_distribution.items():
                if not 0 <= coverage <= 1:
                    errors.append(f"{sac_id}: 属性'{attr}'覆盖率超出范围 ({coverage})")
            
            # 检查EHP合理性
            calculated_ehp = sac.get_weighted_ehp() / (
                sum(unit.supply * unit.weight for unit in sac.core_units)
            )
            if abs(calculated_ehp - sac.ehp_per_supply) > 10:
                errors.append(f"{sac_id}: 计算EHP与配置EHP差异过大")
        
        return errors
    
    def export_summary(self) -> Dict[str, Any]:
        """导出SAC数据摘要"""
        summary = {
            'total_compositions': len(self._compositions),
            'compositions': {}
        }
        
        for sac_id, sac in self._compositions.items():
            summary['compositions'][sac_id] = {
                'name': sac.name,
                'description': sac.description,
                'unit_count': len(sac.core_units),
                'ehp_per_supply': sac.ehp_per_supply,
                'primary_threat': sac.threat_profile.get('primary'),
                'main_attributes': [
                    attr for attr, coverage in sac.attribute_distribution.items()
                    if coverage > 0.5
                ]
            }
        
        return summary


# 全局SAC加载器实例
_sac_loader = None

def get_sac_loader() -> SACLoader:
    """获取全局SAC加载器实例（单例模式）"""
    global _sac_loader
    if _sac_loader is None:
        _sac_loader = SACLoader()
    return _sac_loader


def load_sac_composition(sac_id: str) -> SACComposition:
    """快速加载SAC组合的便捷函数"""
    return get_sac_loader().get_composition(sac_id)


def list_available_sacs() -> List[str]:
    """列出所有可用SAC的便捷函数"""
    return get_sac_loader().list_compositions()


if __name__ == "__main__":
    # 测试SAC加载器
    print("=== SAC数据加载器测试 ===\n")
    
    loader = SACLoader()
    
    # 验证配置
    errors = loader.validate_config()
    if errors:
        print("配置验证错误:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ 配置验证通过")
    
    print(f"\n可用的SAC组合: {loader.list_compositions()}")
    
    # 显示每个SAC的详细信息
    for sac_id in loader.list_compositions():
        sac = loader.get_composition(sac_id)
        print(f"\n--- {sac_id}: {sac.name} ---")
        print(f"描述: {sac.description}")
        print(f"每人口EHP: {sac.ehp_per_supply}")
        print(f"核心单位: {[unit.name for unit in sac.core_units]}")
        print(f"主要威胁: {sac.threat_profile.get('primary')}")
        
        # 测试混合伤害计算
        test_bonus = {"重甲": 50, "生物": 25}
        multiplier = loader.calculate_mixed_damage_multiplier(sac_id, test_bonus)
        print(f"测试伤害乘数(+50%重甲,+25%生物): {multiplier:.2f}")
    
    print("\n=== 测试完成 ===") 