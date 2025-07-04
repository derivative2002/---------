"""
实验管理系统
类似Hydra的实验组织和日志管理，专门为数学建模实验设计
"""

import os
import json
import yaml
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
import hashlib
import pandas as pd
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging


class ExperimentType(Enum):
    """实验类型枚举"""
    UNIT_EVALUATION = "unit_eval"              # 单位评估
    COMMANDER_COMPARISON = "cmd_comp"          # 指挥官对比
    BALANCE_ANALYSIS = "balance"               # 平衡性分析
    CEM_VISUALIZATION = "cem_viz"              # CEM可视化
    PARAMETER_SWEEP = "param_sweep"            # 参数扫描
    SYNERGY_ANALYSIS = "synergy"               # 协同效应分析
    META_ANALYSIS = "meta"                     # 元分析（多实验对比）


@dataclass
class ExperimentConfig:
    """实验配置数据类"""
    # 基础信息
    name: str
    type: ExperimentType
    description: str = ""
    
    # 模型配置
    model_version: str = "v2.1"
    cev_version: str = "dynamic"
    cem_enabled: bool = True
    
    # 评估参数
    commanders: List[str] = field(default_factory=list)
    units: List[str] = field(default_factory=list)
    game_phases: List[str] = field(default_factory=lambda: ["early_game", "mid_game", "late_game"])
    
    # 环境参数
    population_cap: int = 200
    resource_multiplier: float = 1.0
    
    # 运行参数
    num_runs: int = 1
    random_seed: Optional[int] = None
    
    # 输出设置
    save_plots: bool = True
    save_raw_data: bool = True
    generate_report: bool = True
    
    # 额外参数
    extra_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        data = asdict(self)
        data['type'] = self.type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ExperimentConfig':
        """从字典创建"""
        data = data.copy()
        if 'type' in data:
            data['type'] = ExperimentType(data['type'])
        return cls(**data)
    
    def get_experiment_id(self) -> str:
        """生成实验ID"""
        # 基于关键参数生成唯一ID
        key_params = {
            'type': self.type.value,
            'commanders': sorted(self.commanders),
            'units': sorted(self.units),
            'game_phases': sorted(self.game_phases),
            'model_version': self.model_version
        }
        
        # 创建稳定的哈希
        param_str = json.dumps(key_params, sort_keys=True)
        return hashlib.md5(param_str.encode()).hexdigest()[:8]


class ExperimentManager:
    """实验管理器"""
    
    def __init__(self, base_dir: str = "experiments"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # 创建基础目录结构
        self.configs_dir = self.base_dir / "configs"
        self.results_dir = self.base_dir / "results"
        self.reports_dir = self.base_dir / "reports"
        self.archive_dir = self.base_dir / "archive"
        
        for dir_path in [self.configs_dir, self.results_dir, 
                        self.reports_dir, self.archive_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # 设置日志
        self.setup_logging()
    
    def setup_logging(self):
        """设置日志系统"""
        log_dir = self.base_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # 创建日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 文件处理器
        log_file = log_dir / f"experiments_{datetime.now():%Y%m%d}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # 配置根日志器
        logger = logging.getLogger('experiment')
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        self.logger = logger
    
    def create_experiment_dir(self, config: ExperimentConfig) -> Path:
        """
        创建实验目录
        
        目录结构:
        experiments/
        └── results/
            └── {type}/{date}/{time}_{name}_{id}/
                ├── .experiment/
                │   ├── config.yaml
                │   ├── metadata.json
                │   └── command.txt
                ├── data/
                │   ├── raw/
                │   └── processed/
                ├── plots/
                ├── models/
                └── report/
        """
        # 生成目录名
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y-%m-%d")
        time_str = timestamp.strftime("%H-%M-%S")
        exp_id = config.get_experiment_id()
        
        # 清理实验名称（移除特殊字符）
        safe_name = "".join(c for c in config.name if c.isalnum() or c in "._- ")
        safe_name = safe_name.replace(" ", "_")
        
        # 构建完整路径
        dir_name = f"{time_str}_{safe_name}_{exp_id}"
        exp_dir = self.results_dir / config.type.value / date_str / dir_name
        
        # 创建目录结构
        exp_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        subdirs = {
            'meta': exp_dir / '.experiment',
            'data_raw': exp_dir / 'data' / 'raw',
            'data_processed': exp_dir / 'data' / 'processed',
            'plots': exp_dir / 'plots',
            'models': exp_dir / 'models',
            'report': exp_dir / 'report'
        }
        
        for subdir in subdirs.values():
            subdir.mkdir(parents=True, exist_ok=True)
        
        # 保存配置
        self._save_experiment_metadata(exp_dir, config, timestamp)
        
        self.logger.info(f"创建实验目录: {exp_dir}")
        
        return exp_dir
    
    def _save_experiment_metadata(self, exp_dir: Path, config: ExperimentConfig, 
                                timestamp: datetime):
        """保存实验元数据"""
        meta_dir = exp_dir / '.experiment'
        
        # 保存配置
        config_path = meta_dir / 'config.yaml'
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config.to_dict(), f, default_flow_style=False, 
                     allow_unicode=True, sort_keys=False)
        
        # 保存元数据
        metadata = {
            'experiment_id': config.get_experiment_id(),
            'name': config.name,
            'type': config.type.value,
            'timestamp': timestamp.isoformat(),
            'model_version': config.model_version,
            'status': 'created',
            'platform': os.name,
            'python_version': os.sys.version,
            'working_dir': str(Path.cwd()),
            'exp_dir': str(exp_dir)
        }
        
        metadata_path = meta_dir / 'metadata.json'
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # 保存命令信息
        import sys
        command_path = meta_dir / 'command.txt'
        with open(command_path, 'w', encoding='utf-8') as f:
            f.write(' '.join(sys.argv))
    
    def load_experiment_config(self, exp_dir: Union[str, Path]) -> ExperimentConfig:
        """加载实验配置"""
        exp_dir = Path(exp_dir)
        config_path = exp_dir / '.experiment' / 'config.yaml'
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        return ExperimentConfig.from_dict(config_data)
    
    def list_experiments(self, 
                        exp_type: Optional[ExperimentType] = None,
                        date_from: Optional[datetime] = None,
                        date_to: Optional[datetime] = None,
                        status: Optional[str] = None) -> List[Dict]:
        """列出实验"""
        experiments = []
        
        # 遍历结果目录
        for type_dir in self.results_dir.iterdir():
            if not type_dir.is_dir():
                continue
                
            # 过滤实验类型
            if exp_type and type_dir.name != exp_type.value:
                continue
            
            # 遍历日期目录
            for date_dir in type_dir.iterdir():
                if not date_dir.is_dir():
                    continue
                
                # 解析日期
                try:
                    dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
                except ValueError:
                    continue
                
                # 日期过滤
                if date_from and dir_date < date_from:
                    continue
                if date_to and dir_date > date_to:
                    continue
                
                # 遍历实验目录
                for exp_dir in date_dir.iterdir():
                    if not exp_dir.is_dir():
                        continue
                    
                    # 读取元数据
                    metadata_path = exp_dir / '.experiment' / 'metadata.json'
                    if metadata_path.exists():
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        # 状态过滤
                        if status and metadata.get('status') != status:
                            continue
                        
                        experiments.append({
                            'path': str(exp_dir),
                            'relative_path': str(exp_dir.relative_to(self.base_dir)),
                            **metadata
                        })
        
        # 按时间排序
        experiments.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return experiments
    
    def get_latest_experiment(self, exp_type: Optional[ExperimentType] = None) -> Optional[Path]:
        """获取最新的实验路径"""
        experiments = self.list_experiments(exp_type=exp_type)
        
        if experiments:
            return Path(experiments[0]['path'])
        
        return None
    
    def update_experiment_status(self, exp_dir: Union[str, Path], status: str):
        """更新实验状态"""
        exp_dir = Path(exp_dir)
        metadata_path = exp_dir / '.experiment' / 'metadata.json'
        
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            metadata['status'] = status
            metadata['last_updated'] = datetime.now().isoformat()
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def save_experiment_results(self, exp_dir: Union[str, Path], 
                              results: Dict[str, Any]):
        """保存实验结果"""
        exp_dir = Path(exp_dir)
        
        # 保存结果摘要
        results_path = exp_dir / '.experiment' / 'results_summary.json'
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # 更新状态
        self.update_experiment_status(exp_dir, 'completed')
        
        self.logger.info(f"保存实验结果: {exp_dir}")
    
    def create_experiment_report(self, exp_dir: Union[str, Path]) -> Path:
        """创建实验报告"""
        exp_dir = Path(exp_dir)
        
        # 加载配置和结果
        config = self.load_experiment_config(exp_dir)
        
        metadata_path = exp_dir / '.experiment' / 'metadata.json'
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        results_path = exp_dir / '.experiment' / 'results_summary.json'
        if results_path.exists():
            with open(results_path, 'r', encoding='utf-8') as f:
                results = json.load(f)
        else:
            results = {}
        
        # 创建Markdown报告
        report_path = exp_dir / 'report' / 'experiment_report.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# 实验报告: {config.name}\n\n")
            f.write(f"**实验ID**: {metadata['experiment_id']}\n")
            f.write(f"**类型**: {config.type.value}\n")
            f.write(f"**时间**: {metadata['timestamp']}\n")
            f.write(f"**状态**: {metadata.get('status', 'unknown')}\n\n")
            
            f.write("## 实验配置\n\n")
            f.write(f"- **模型版本**: {config.model_version}\n")
            f.write(f"- **CEV版本**: {config.cev_version}\n")
            f.write(f"- **指挥官**: {', '.join(config.commanders)}\n")
            f.write(f"- **单位**: {', '.join(config.units[:5])}...")
            if len(config.units) > 5:
                f.write(f" (共{len(config.units)}个)\n")
            else:
                f.write("\n")
            f.write(f"- **游戏阶段**: {', '.join(config.game_phases)}\n\n")
            
            if results:
                f.write("## 实验结果\n\n")
                f.write("```json\n")
                f.write(json.dumps(results, indent=2, ensure_ascii=False))
                f.write("\n```\n\n")
            
            f.write("## 输出文件\n\n")
            
            # 列出生成的文件
            for category, path in [
                ("数据文件", exp_dir / 'data'),
                ("图表文件", exp_dir / 'plots'),
                ("模型文件", exp_dir / 'models')
            ]:
                files = list(path.rglob('*'))
                files = [f for f in files if f.is_file()]
                
                if files:
                    f.write(f"### {category}\n\n")
                    for file in files[:10]:  # 最多显示10个
                        f.write(f"- {file.relative_to(exp_dir)}\n")
                    if len(files) > 10:
                        f.write(f"- ... (共{len(files)}个文件)\n")
                    f.write("\n")
        
        self.logger.info(f"生成实验报告: {report_path}")
        
        return report_path
    
    def archive_experiment(self, exp_dir: Union[str, Path]):
        """归档实验"""
        exp_dir = Path(exp_dir)
        
        # 获取实验信息
        metadata_path = exp_dir / '.experiment' / 'metadata.json'
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # 创建归档名称
        archive_name = f"{metadata['experiment_id']}_{metadata['name']}.zip"
        archive_path = self.archive_dir / archive_name
        
        # 创建ZIP归档
        import zipfile
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in exp_dir.rglob('*'):
                if file_path.is_file():
                    zf.write(file_path, file_path.relative_to(exp_dir.parent))
        
        # 删除原目录（可选）
        # shutil.rmtree(exp_dir)
        
        self.logger.info(f"归档实验: {archive_path}")
    
    def compare_experiments(self, exp_dirs: List[Union[str, Path]]) -> pd.DataFrame:
        """比较多个实验"""
        comparison_data = []
        
        for exp_dir in exp_dirs:
            exp_dir = Path(exp_dir)
            
            # 加载配置和结果
            config = self.load_experiment_config(exp_dir)
            
            metadata_path = exp_dir / '.experiment' / 'metadata.json'
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            results_path = exp_dir / '.experiment' / 'results_summary.json'
            if results_path.exists():
                with open(results_path, 'r', encoding='utf-8') as f:
                    results = json.load(f)
            else:
                results = {}
            
            # 组合数据
            row_data = {
                'experiment_id': metadata['experiment_id'],
                'name': config.name,
                'type': config.type.value,
                'timestamp': metadata['timestamp'],
                'model_version': config.model_version,
                'num_commanders': len(config.commanders),
                'num_units': len(config.units),
                **{f"result_{k}": v for k, v in results.items()}
            }
            
            comparison_data.append(row_data)
        
        # 创建DataFrame
        df = pd.DataFrame(comparison_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp', ascending=False)
        
        return df


# 便捷函数
def create_experiment(name: str, 
                     exp_type: ExperimentType,
                     **kwargs) -> Tuple[ExperimentManager, Path, ExperimentConfig]:
    """创建新实验的便捷函数"""
    manager = ExperimentManager()
    
    config = ExperimentConfig(
        name=name,
        type=exp_type,
        **kwargs
    )
    
    exp_dir = manager.create_experiment_dir(config)
    
    return manager, exp_dir, config


# 使用示例
if __name__ == "__main__":
    # 创建实验
    manager, exp_dir, config = create_experiment(
        name="升格者vs陆战队员对比",
        exp_type=ExperimentType.UNIT_EVALUATION,
        commanders=["阿拉纳克", "吉姆·雷诺"],
        units=["升格者", "陆战队员"],
        description="对比不同指挥官的核心单位效能"
    )
    
    print(f"实验目录: {exp_dir}")
    
    # 模拟保存结果
    results = {
        "best_unit": "升格者",
        "max_cev": 156.8,
        "optimal_phase": "late_game"
    }
    
    manager.save_experiment_results(exp_dir, results)
    
    # 生成报告
    report_path = manager.create_experiment_report(exp_dir)
    print(f"报告路径: {report_path}")
    
    # 列出所有实验
    all_experiments = manager.list_experiments()
    print(f"\n共有 {len(all_experiments)} 个实验")
    
    for exp in all_experiments[:3]:
        print(f"- {exp['name']} ({exp['type']}) - {exp['timestamp']}")