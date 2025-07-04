"""
实验配置加载器
支持从YAML/JSON文件加载实验配置
"""

import yaml
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Union, Optional
from dataclasses import dataclass, field

from src.experiment.experiment_manager import ExperimentConfig, ExperimentType


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_dir: str = "configs"):
        # 以脚本文件所在目录为基准，定位项目根目录
        project_root = Path(__file__).parent.parent.parent
        self.config_dir = project_root / config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_config(self, config_path: Union[str, Path]) -> ExperimentConfig:
        """
        加载单个实验配置
        
        参数:
            config_path: 配置文件路径（YAML或JSON），可以是相对或绝对路径
            
        返回:
            ExperimentConfig对象
        """
        config_path = Path(config_path)
        
        # 修正路径处理逻辑
        # 如果路径不是绝对路径，则认为它是相对于当前工作目录（项目根目录）的
        if not config_path.is_absolute():
            # 我们假设执行脚本时，当前目录就是项目根目录
            absolute_path = Path.cwd() / config_path
            if not absolute_path.exists():
                # 如果在当前目录找不到，再尝试在默认的configs目录下找
                absolute_path = self.config_dir / config_path

            config_path = absolute_path

        if not config_path.exists():
            raise FileNotFoundError(f"无法在 {config_path} 或默认配置目录中找到该文件")

        # 读取配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.suffix in ['.yaml', '.yml']:
                config_data = yaml.safe_load(f)
            elif config_path.suffix == '.json':
                config_data = json.load(f)
            else:
                raise ValueError(f"不支持的配置文件格式: {config_path.suffix}")
        
        # 转换类型字符串为枚举
        if 'type' in config_data and isinstance(config_data['type'], str):
            config_data['type'] = ExperimentType(config_data['type'])
        
        # 处理特殊值
        if 'commanders' in config_data and config_data['commanders'] == ['all']:
            config_data['commanders'] = self._get_all_commanders()
        
        # 创建配置对象
        return ExperimentConfig(**config_data)
    
    def load_batch_config(self, batch_path: Union[str, Path]) -> List[ExperimentConfig]:
        """
        加载批量实验配置
        
        参数:
            batch_path: 批量配置文件路径
            
        返回:
            ExperimentConfig对象列表
        """
        batch_path = Path(batch_path)
        
        if not batch_path.is_absolute():
            batch_path = self.config_dir / batch_path
        
        with open(batch_path, 'r', encoding='utf-8') as f:
            if batch_path.suffix in ['.yaml', '.yml']:
                batch_data = yaml.safe_load(f)
            else:
                batch_data = json.load(f)
        
        # 提取实验列表
        experiments_data = batch_data.get('experiments', [])
        
        # 批量设置（应用到所有实验）
        batch_settings = batch_data.get('batch_settings', {})
        
        configs = []
        for exp_data in experiments_data:
            # 合并批量设置
            for key, value in batch_settings.items():
                if key not in exp_data:
                    exp_data[key] = value
            
            # 转换类型
            if 'type' in exp_data and isinstance(exp_data['type'], str):
                exp_data['type'] = ExperimentType(exp_data['type'])
            
            # 处理特殊值
            if 'commanders' in exp_data and exp_data['commanders'] == ['all']:
                exp_data['commanders'] = self._get_all_commanders()
            
            configs.append(ExperimentConfig(**exp_data))
        
        return configs
    
    def save_config(self, config: ExperimentConfig, 
                   save_path: Union[str, Path],
                   format: str = 'yaml'):
        """
        保存实验配置到文件
        
        参数:
            config: 实验配置对象
            save_path: 保存路径
            format: 保存格式 ('yaml' 或 'json')
        """
        save_path = Path(save_path)
        
        if not save_path.is_absolute():
            save_path = self.config_dir / save_path
        
        # 确保目录存在
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 转换为字典
        config_data = config.to_dict()
        
        # 保存文件
        with open(save_path, 'w', encoding='utf-8') as f:
            if format == 'yaml':
                yaml.dump(config_data, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False)
            else:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    def list_configs(self, pattern: str = "*.yaml") -> List[Path]:
        """
        列出所有配置文件
        
        参数:
            pattern: 文件匹配模式
            
        返回:
            配置文件路径列表
        """
        configs = []
        
        # 递归查找所有匹配的文件
        for config_file in self.config_dir.rglob(pattern):
            if config_file.is_file():
                configs.append(config_file)
        
        # 同时查找JSON文件
        if pattern == "*.yaml":
            for config_file in self.config_dir.rglob("*.json"):
                if config_file.is_file():
                    configs.append(config_file)
        
        return sorted(configs)
    
    def validate_config(self, config: Union[ExperimentConfig, Dict]) -> List[str]:
        """
        验证配置的有效性
        
        返回:
            错误信息列表（空列表表示配置有效）
        """
        errors = []
        
        if isinstance(config, dict):
            config_dict = config
        else:
            config_dict = config.to_dict()
        
        # 检查必需字段
        required_fields = ['name', 'type']
        for field in required_fields:
            if field not in config_dict or not config_dict[field]:
                errors.append(f"缺少必需字段: {field}")
        
        # 检查类型有效性
        if 'type' in config_dict:
            try:
                if isinstance(config_dict['type'], str):
                    ExperimentType(config_dict['type'])
            except ValueError:
                errors.append(f"无效的实验类型: {config_dict['type']}")
        
        # 检查列表字段
        list_fields = ['commanders', 'units', 'game_phases']
        for field in list_fields:
            if field in config_dict and not isinstance(config_dict[field], list):
                errors.append(f"{field} 必须是列表类型")
        
        # 检查数值字段
        numeric_fields = ['population_cap', 'resource_multiplier', 'num_runs']
        for field in numeric_fields:
            if field in config_dict:
                value = config_dict[field]
                if not isinstance(value, (int, float)) or value <= 0:
                    errors.append(f"{field} 必须是正数")
        
        return errors
    
    def _get_all_commanders(self) -> List[str]:
        """获取所有指挥官列表"""
        return [
            "吉姆·雷诺", "凯瑞甘", "阿塔尼斯", "斯旺",
            "扎加拉", "沃拉尊", "阿巴瑟", "诺娃·泰拉",
            "斯托科夫", "菲尼克斯(塔兰达)", "德哈卡", "汉与霍纳",
            "泰凯斯", "泽拉图", "斯台特曼", "蒙斯克", "阿拉纳克"
        ]
    
    def create_config_from_template(self, 
                                  template_name: str,
                                  output_path: Union[str, Path],
                                  **kwargs):
        """
        从模板创建配置
        
        参数:
            template_name: 模板名称
            output_path: 输出路径
            **kwargs: 覆盖模板的参数
        """
        # 模板定义
        templates = {
            'basic_unit_eval': {
                'name': '基础单位评估',
                'type': 'unit_eval',
                'description': '评估指定单位的效能',
                'commanders': ['吉姆·雷诺'],
                'units': ['陆战队员', '掠夺者', '攻城坦克'],
                'game_phases': ['early_game', 'mid_game', 'late_game'],
                'save_plots': True,
                'generate_report': True
            },
            
            'commander_balance': {
                'name': '指挥官平衡性检查',
                'type': 'cmd_comp',
                'description': '比较多个指挥官的整体表现',
                'commanders': ['吉姆·雷诺', '凯瑞甘', '阿塔尼斯'],
                'save_plots': True,
                'generate_report': True
            },
            
            'quick_cem': {
                'name': 'CEM快速可视化',
                'type': 'cem_viz',
                'description': '生成单位克制关系矩阵',
                'units': ['陆战队员', '跳虫', '狂热者', '掠夺者', '刺蛇', '追猎者'],
                'save_plots': True,
                'generate_report': False
            }
        }
        
        if template_name not in templates:
            raise ValueError(f"未知的模板: {template_name}")
        
        # 获取模板
        template_data = templates[template_name].copy()
        
        # 应用覆盖参数
        template_data.update(kwargs)
        
        # 创建配置
        config = ExperimentConfig(**template_data)
        
        # 保存配置
        self.save_config(config, output_path)
        
        return config


# 便捷函数
def load_and_run_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """加载并运行单个配置"""
    from src.experiment.experiment_runner import ExperimentRunner
    
    loader = ConfigLoader()
    config = loader.load_config(config_path)
    
    # 验证配置
    errors = loader.validate_config(config)
    if errors:
        raise ValueError(f"配置验证失败:\n" + "\n".join(errors))
    
    # 运行实验
    runner = ExperimentRunner()
    return runner.run_experiment(config)


def load_and_run_batch(batch_path: Union[str, Path]) -> pd.DataFrame:
    """加载并运行批量配置"""
    from src.experiment.experiment_runner import run_batch_experiments
    
    loader = ConfigLoader()
    configs = loader.load_batch_config(batch_path)
    
    # 验证所有配置
    for i, config in enumerate(configs):
        errors = loader.validate_config(config)
        if errors:
            raise ValueError(f"配置 {i+1} 验证失败:\n" + "\n".join(errors))
    
    # 运行批量实验
    return run_batch_experiments(configs)


# 使用示例
if __name__ == "__main__":
    loader = ConfigLoader()
    
    # 列出所有配置
    print("可用的配置文件:")
    configs = loader.list_configs()
    for config_path in configs:
        print(f"  - {config_path.relative_to(loader.config_dir)}")
    
    # 加载示例配置
    if configs:
        example_config = loader.load_config(configs[0])
        print(f"\n加载的配置: {example_config.name}")
        print(f"类型: {example_config.type.value}")
        print(f"指挥官: {', '.join(example_config.commanders[:3])}...")
    
    # 从模板创建新配置
    new_config = loader.create_config_from_template(
        'basic_unit_eval',
        'my_experiment.yaml',
        name='我的单位评估实验',
        commanders=['阿拉纳克', '诺娃·泰拉']
    )
    print(f"\n创建新配置: {new_config.name}")