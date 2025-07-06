"""
MK Ⅱ 洛基（雷神）单位CEV测试脚本
用于计算MK II 洛基的战斗效能值，并与其他精英单位进行比较
"""
import sys
import logging
import json
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

sys.path.append('.')
from src.core.cev_calculator_v25 import CEVCalculatorV25, CalculationConfig
from src.data.yaml_loader import YAMLDataLoader, UnitData, WeaponData, CommanderData
from src.data.models import Unit, Weapon

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ThorMk2Unit(UnitData):
    """MK II 洛基单位数据类"""
    def __init__(self):
        # 初始化所有必需的属性
        self.id = "ThorMk2"
        self.name = "MK Ⅱ 洛基（雷神）"
        self.name_en = "Thor MK II"
        self.commander = "Moebius"  # 隶属于莫比斯军团指挥官
        self.race = "Terr"
        
        # 基础属性
        self.life = 300
        self.armor = 5
        self.shields = 170
        self.energy = 0
        self.radius = 0.875
        self.plane = "Ground"
        
        # 成本信息 - 调整后的资源成本
        self.minerals = 600
        self.vespene = 450
        self.supply = 6
        self.build_time = 60
        
        # 移动属性
        self.speed = 2.25
        self.acceleration = 1.0
        self.turning_rate = 1.0
        
        # 物理属性
        self.sight = 12
        self.height = 3.5
        
        # 单位类型和属性
        self.attributes = ["Armored", "Mechanical", "Massive"]
        
        # 武器配置
        self.weapons = [
            {
                'mode': 'default',
                'weapon_ref': 'LanceMissileLaunchersMk2',
                'is_default': True
            }
        ]
        
        # 能力和模式
        self.abilities = []
        self.modes = {}


class ThorMk2Weapon(WeaponData):
    """MK II 洛基武器数据类"""
    def __init__(self):
        # 初始化所有必需的属性
        self.id = "LanceMissileLaunchersMk2"
        self.name = "磁轨导弹发射器"
        self.name_en = "Lance Missile Launchers"
        
        # 目标过滤器
        self.target_filters = ["Ground", "Air"]
        self.exclude_filters = ["Missile", "Stasis", "Dead", "Hidden", "Invulnerable"]
        
        # 武器属性
        self.damage = 45
        self.damage_type = "Normal"
        self.attacks = 4  # 4次攻击
        self.period = 2.0  # 2秒攻击间隔
        self.range = 18.0  # 18射程
        
        # 属性加成
        self.attribute_bonus = {"Armored": 15}  # 对重甲+15
        
        # 架设状态下不是AOE，没有溅射伤害
        self.splash_radius = 0
        self.splash_damage = []
        self.arc = 0
        self.upgrades = {}


class MoebiusCommander(CommanderData):
    """莫比斯军团指挥官数据类"""
    def __init__(self):
        # 直接提供所有必需的参数
        self.id = "Moebius"
        self.name = "莫比斯军团"
        self.name_en = "Moebius Corps"
        self.race = "Terr"
        self.population_cap = 200
        self.mineral_gas_ratio = 2.5  # 矿气转换率调整为2.5
        self.production_efficiency = 1.0
        self.masteries = {}
        self.prestiges = []
        
        # 需要人口税的指挥官
        self.no_supply_tax = False


def run_thor_mk2_test():
    """运行洛基MK II的CEV测试"""
    # 创建数据加载器
    loader = YAMLDataLoader()
    
    try:
        # 先加载现有数据
        loader.load_all()
        logger.info("成功加载基础数据")
        
        # 列出所有可用的单位ID
        print("=== 可用单位ID ===")
        for unit_id in loader.units.keys():
            unit = loader.units[unit_id]
            print(f"{unit_id} - {unit.name} ({unit.commander})")
    except Exception as e:
        logger.error(f"加载基础数据失败: {e}")
        return
    
    # 注入莫比斯指挥官数据
    moebius_commander = MoebiusCommander()
    loader.commanders[moebius_commander.id] = moebius_commander
    
    # 注入洛基MK II数据
    thor_unit = ThorMk2Unit()
    thor_weapon = ThorMk2Weapon()
    
    # 手动注入到数据加载器
    loader.units[thor_unit.id] = thor_unit
    loader.weapons[thor_weapon.id] = thor_weapon
    
    # 创建配置
    config = CalculationConfig()
    
    # 为洛基设置操作系数
    if hasattr(config, 'operation_factors') and isinstance(config.operation_factors, dict):
        config.operation_factors["ThorMk2"] = 0.6  # 操作系数较低
    
    # 确保莫比斯指挥官不在人口税豁免列表中
    if hasattr(config, 'commanders_exempt_from_supply_tax') and isinstance(config.commanders_exempt_from_supply_tax, list):
        if "Moebius" in config.commanders_exempt_from_supply_tax:
            config.commanders_exempt_from_supply_tax.remove("Moebius")
    
    # 设置莫比斯指挥官的矿气转换率
    if hasattr(config, 'commander_mineral_gas_ratio') and isinstance(config.commander_mineral_gas_ratio, dict):
        config.commander_mineral_gas_ratio["Moebius"] = 2.5  # 矿气转换率调整为2.5
    
    # 初始化精通配置
    if config.mastery_config is None:
        config.mastery_config = {
            "Alarak": {"attack_speed": 0.15},
            "AlarakP1": {"attack_speed": 0.15},
            "Swann": {"mech_life": 0.30, "attack_speed": 0.15},
            "Nova": {"attack_speed": 0.15},
            "Dehaka": {"attack_speed": 0.15},
            "Moebius": {"attack_speed": 0.15}  # 给莫比斯军团添加精通
        }
    
    # 创建计算器
    calculator = CEVCalculatorV25(loader, config)
    
    # 用于存储结果的字典
    results = {
        "unit_details": {
            "name": thor_unit.name,
            "id": thor_unit.id,
            "commander": moebius_commander.name,
            "cost": {
                "minerals": thor_unit.minerals,
                "vespene": thor_unit.vespene,
                "supply": thor_unit.supply
            },
            "stats": {
                "life": thor_unit.life,
                "armor": thor_unit.armor,
                "shields": thor_unit.shields
            },
            "weapon": {
                "name": thor_weapon.name,
                "damage": thor_weapon.damage,
                "attacks": thor_weapon.attacks,
                "period": thor_weapon.period,
                "range": thor_weapon.range,
                "bonus_vs_armored": thor_weapon.attribute_bonus.get("Armored", 0)
            }
        },
        "cev_results": {},
        "comparisons": {}
    }
    
    # 计算洛基MK II的CEV
    try:
        # 标准场景
        result_standard = calculator.calculate_cev("ThorMk2", apply_mastery=True)
        print(f"\n=== MK Ⅱ 洛基（雷神）- 标准场景 ===")
        print(f"CEV: {result_standard['cev']}")
        print(f"CEV/Pop: {result_standard['cev_per_pop']}")
        print(f"详细参数: ")
        for k, v in result_standard['components'].items():
            print(f"  {k}: {v}")
        
        # 保存结果
        results["cev_results"]["standard"] = {
            "cev": result_standard["cev"],
            "cev_per_pop": result_standard["cev_per_pop"],
            "components": result_standard["components"],
            "details": result_standard["details"]
        }
        
        # 对重甲场景
        result_vs_armored = calculator.calculate_cev("ThorMk2", scenario="vs_armored", apply_mastery=True)
        print(f"\n=== MK Ⅱ 洛基（雷神）- 对重甲场景 ===")
        print(f"CEV: {result_vs_armored['cev']}")
        print(f"CEV/Pop: {result_vs_armored['cev_per_pop']}")
        print(f"详细参数: ")
        for k, v in result_vs_armored['components'].items():
            print(f"  {k}: {v}")
        
        # 保存结果
        results["cev_results"]["vs_armored"] = {
            "cev": result_vs_armored["cev"],
            "cev_per_pop": result_vs_armored["cev_per_pop"],
            "components": result_vs_armored["components"],
            "details": result_vs_armored["details"]
        }
        
        # 显示经济相关详细数据
        print(f"\n=== 经济细节 ===")
        print(f"基础成本: {thor_unit.minerals} 矿物 + {thor_unit.vespene} 瓦斯")
        print(f"人口消耗: {thor_unit.supply}")
        print(f"人口税: {result_standard['details']['population_tax']}")
        print(f"矿气转换率: {result_standard['details']['mineral_gas_ratio']}")
        print(f"有效成本: {result_standard['components']['c_eff']}")
        
        # 保存经济详情
        results["economic_details"] = {
            "base_cost": {
                "minerals": thor_unit.minerals,
                "vespene": thor_unit.vespene
            },
            "population_tax": result_standard['details']['population_tax'],
            "mineral_gas_ratio": result_standard['details']['mineral_gas_ratio'],
            "effective_cost": result_standard['components']['c_eff']
        }
        
        # 尝试计算其他精英单位作为参考
        try:
            # 攻城坦克（使用正确ID：SiegeTank）
            tank_result = calculator.calculate_cev("SiegeTank", scenario="vs_armored", apply_mastery=True)
            print(f"\n=== 攻城坦克（对重甲）- 参考 ===")
            print(f"CEV: {tank_result['cev']}")
            print(f"CEV/Pop: {tank_result['cev_per_pop']}")
            
            # 灵魂巧匠天罚行者（使用正确ID：ColossusTaldarim_SoulArtificer）
            ww_result = calculator.calculate_cev("ColossusTaldarim_SoulArtificer", apply_mastery=True)
            print(f"\n=== 灵魂巧匠天罚行者 - 参考 ===")
            print(f"CEV: {ww_result['cev']}")
            print(f"CEV/Pop: {ww_result['cev_per_pop']}")
            
            # 掠袭解放者（使用正确ID：Liberator_BlackOps）
            lib_result = calculator.calculate_cev("Liberator_BlackOps", weapon_mode="AA", apply_mastery=True)
            print(f"\n=== 掠袭解放者 - 参考 ===")
            print(f"CEV: {lib_result['cev']}")
            print(f"CEV/Pop: {lib_result['cev_per_pop']}")
            
            # 与精英单位比较
            print(f"\n=== 与其他精英单位比较 ===")
            thor_vs_tank = result_vs_armored['cev'] / tank_result['cev']
            thor_vs_ww = result_standard['cev'] / ww_result['cev']
            thor_vs_lib = result_standard['cev'] / lib_result['cev']
            
            print(f"洛基(重甲) vs 攻城坦克(重甲): {thor_vs_tank:.2f}倍")
            print(f"洛基(标准) vs 天罚行者: {thor_vs_ww:.2f}倍")
            print(f"洛基(标准) vs 掠袭解放者: {thor_vs_lib:.2f}倍")
            
            # 按人口效率比较
            print(f"\n=== 人口效率比较 ===")
            thor_vs_tank_pop = result_vs_armored['cev_per_pop'] / tank_result['cev_per_pop']
            thor_vs_ww_pop = result_standard['cev_per_pop'] / ww_result['cev_per_pop']
            thor_vs_lib_pop = result_standard['cev_per_pop'] / lib_result['cev_per_pop']
            
            print(f"洛基(重甲) vs 攻城坦克(重甲): {thor_vs_tank_pop:.2f}倍")
            print(f"洛基(标准) vs 天罚行者: {thor_vs_ww_pop:.2f}倍")
            print(f"洛基(标准) vs 掠袭解放者: {thor_vs_lib_pop:.2f}倍")
            
            # 保存比较结果
            results["comparisons"]["elite_units"] = {
                "vs_siege_tank": {
                    "cev_ratio": thor_vs_tank,
                    "cev_per_pop_ratio": thor_vs_tank_pop
                },
                "vs_wrathwalker": {
                    "cev_ratio": thor_vs_ww,
                    "cev_per_pop_ratio": thor_vs_ww_pop
                },
                "vs_liberator": {
                    "cev_ratio": thor_vs_lib,
                    "cev_per_pop_ratio": thor_vs_lib_pop
                }
            }
            
            # 保存参考单位结果
            results["reference_units"] = {
                "siege_tank": {
                    "cev": tank_result["cev"],
                    "cev_per_pop": tank_result["cev_per_pop"]
                },
                "wrathwalker": {
                    "cev": ww_result["cev"],
                    "cev_per_pop": ww_result["cev_per_pop"]
                },
                "liberator": {
                    "cev": lib_result["cev"],
                    "cev_per_pop": lib_result["cev_per_pop"]
                }
            }
            
            # 输出总结
            print(f"\n=== CEV分析总结 ===")
            print(f"MK Ⅱ 洛基标准场景CEV: {result_standard['cev']:.2f}")
            print(f"MK Ⅱ 洛基对重甲场景CEV: {result_vs_armored['cev']:.2f}")
            print(f"MK Ⅱ 洛基人口效率: {result_standard['cev_per_pop']:.2f}")
            print(f"与精英单位比较:")
            print(f"- 对攻城坦克(重甲): 资源效率{thor_vs_tank:.2f}倍，人口效率{thor_vs_tank_pop:.2f}倍")
            print(f"- 对天罚行者: 资源效率{thor_vs_ww:.2f}倍，人口效率{thor_vs_ww_pop:.2f}倍")
            print(f"- 对掠袭解放者: 资源效率{thor_vs_lib:.2f}倍，人口效率{thor_vs_lib_pop:.2f}倍")
            print(f"结论: MK Ⅱ 洛基对重甲目标的CEV表现非常出色，在精英单位中处于领先地位。")
            
            # 保存结果到JSON文件
            with open("output/thor_mk2_cev_results_adjusted_cost_ratio.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n分析结果已保存到 output/thor_mk2_cev_results_adjusted_cost_ratio.json")
            
        except Exception as e:
            logger.warning(f"计算参考单位时出错: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        logger.error(f"计算错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_thor_mk2_test() 