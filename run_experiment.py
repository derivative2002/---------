#!/usr/bin/env python3
"""
实验运行命令行接口
提供类似Hydra的实验管理体验
"""

import argparse
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import logging
from datetime import datetime
from typing import Optional, List

from src.experiment.experiment_manager import ExperimentManager, ExperimentType
from src.experiment.experiment_runner import ExperimentRunner
from src.experiment.config_loader import ConfigLoader, load_and_run_config, load_and_run_batch


def setup_logging(verbose: bool = False):
    """设置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )


def cmd_run(args):
    """运行单个实验"""
    loader = ConfigLoader()
    
    # 加载配置
    try:
        config = loader.load_config(args.config)
    except FileNotFoundError:
        print(f"错误: 找不到配置文件 '{args.config}'")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 加载配置失败 - {e}")
        sys.exit(1)
    
    # 验证配置
    errors = loader.validate_config(config)
    if errors:
        print("配置验证失败:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    # 覆盖参数
    if args.name:
        config.name = args.name
    if args.commanders:
        config.commanders = args.commanders.split(',')
    if args.units:
        config.units = args.units.split(',')
    if args.no_plots:
        config.save_plots = False
    if args.no_report:
        config.generate_report = False
    
    # 运行实验
    print(f"\n{'='*60}")
    print(f"运行实验: {config.name}")
    print(f"类型: {config.type.value}")
    print(f"{'='*60}\n")
    
    runner = ExperimentRunner()
    results = runner.run_experiment(config)
    
    # 显示结果摘要
    if results['meta']['success']:
        print(f"\n✓ 实验成功完成!")
        print(f"  耗时: {results['meta']['duration_seconds']:.2f}秒")
        print(f"  输出目录: {runner.current_exp_dir}")
        
        # 显示关键结果
        if 'units_evaluated' in results:
            print(f"  评估单位数: {len(results['units_evaluated'])}")
        if 'best_units' in results:
            print("\n  最佳单位:")
            for phase, unit_info in results['best_units'].items():
                print(f"    {phase}: {unit_info['name']} (得分: {unit_info['score']:.2f})")
    else:
        print(f"\n✗ 实验失败: {results['meta'].get('error', '未知错误')}")
        sys.exit(1)


def cmd_batch(args):
    """运行批量实验"""
    print(f"\n运行批量实验: {args.batch}")
    
    try:
        summary_df = load_and_run_batch(args.batch)
    except FileNotFoundError:
        print(f"错误: 找不到批量配置文件 '{args.batch}'")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)
    
    # 显示汇总
    print("\n批量实验汇总:")
    print(summary_df.to_string(index=False))
    
    # 统计
    success_count = summary_df['success'].sum()
    total_count = len(summary_df)
    total_time = summary_df['duration'].sum()
    
    print(f"\n完成: {success_count}/{total_count} 个实验成功")
    print(f"总耗时: {total_time:.2f}秒")


def cmd_list(args):
    """列出实验"""
    manager = ExperimentManager()
    
    # 解析筛选条件
    exp_type = None
    if args.type:
        try:
            exp_type = ExperimentType(args.type)
        except ValueError:
            print(f"错误: 无效的实验类型 '{args.type}'")
            print(f"有效类型: {', '.join([t.value for t in ExperimentType])}")
            sys.exit(1)
    
    # 获取实验列表
    experiments = manager.list_experiments(
        exp_type=exp_type,
        status=args.status
    )
    
    if not experiments:
        print("没有找到符合条件的实验")
        return
    
    # 显示实验列表
    print(f"\n找到 {len(experiments)} 个实验:\n")
    
    # 按类型分组
    by_type = {}
    for exp in experiments:
        exp_type = exp['type']
        if exp_type not in by_type:
            by_type[exp_type] = []
        by_type[exp_type].append(exp)
    
    for exp_type, type_experiments in by_type.items():
        print(f"{exp_type}:")
        for exp in type_experiments[:args.limit]:
            timestamp = datetime.fromisoformat(exp['timestamp'])
            print(f"  [{timestamp:%Y-%m-%d %H:%M}] {exp['name']}")
            print(f"    ID: {exp['experiment_id']}")
            print(f"    状态: {exp.get('status', 'unknown')}")
            print(f"    路径: {exp['relative_path']}")
            print()
        
        if len(type_experiments) > args.limit:
            print(f"  ... 还有 {len(type_experiments) - args.limit} 个实验\n")


def cmd_configs(args):
    """列出配置文件"""
    loader = ConfigLoader()
    
    configs = loader.list_configs()
    
    if not configs:
        print("没有找到配置文件")
        return
    
    print(f"\n找到 {len(configs)} 个配置文件:\n")
    
    # 按目录分组
    by_dir = {}
    for config_path in configs:
        dir_path = config_path.parent.relative_to(loader.config_dir)
        if dir_path not in by_dir:
            by_dir[dir_path] = []
        by_dir[dir_path].append(config_path)
    
    for dir_path, dir_configs in sorted(by_dir.items()):
        print(f"{dir_path}/:")
        for config_path in sorted(dir_configs):
            print(f"  - {config_path.name}")
        print()
    
    # 显示示例命令
    if configs:
        example_config = configs[0].relative_to(loader.config_dir)
        print("运行示例:")
        print(f"  python run_experiment.py run {example_config}")


def cmd_create(args):
    """创建新配置"""
    loader = ConfigLoader()
    
    # 列出可用模板
    templates = ['basic_unit_eval', 'commander_balance', 'quick_cem']
    
    if args.list_templates:
        print("可用的配置模板:")
        for template in templates:
            print(f"  - {template}")
        return
    
    # 检查模板
    if args.template not in templates:
        print(f"错误: 未知的模板 '{args.template}'")
        print(f"可用模板: {', '.join(templates)}")
        sys.exit(1)
    
    # 创建配置
    try:
        config = loader.create_config_from_template(
            args.template,
            args.output,
            name=args.name or f"新实验_{datetime.now():%Y%m%d_%H%M%S}"
        )
        
        print(f"✓ 创建配置文件: {args.output}")
        print(f"  名称: {config.name}")
        print(f"  类型: {config.type.value}")
        
        if args.edit:
            import subprocess
            subprocess.run(['open', args.output])
            
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


def cmd_report(args):
    """查看实验报告"""
    manager = ExperimentManager()
    
    # 获取实验路径
    if args.exp_dir:
        exp_dir = Path(args.exp_dir)
    else:
        # 获取最新实验
        exp_dir = manager.get_latest_experiment()
        if not exp_dir:
            print("错误: 没有找到实验")
            sys.exit(1)
    
    # 生成或更新报告
    if args.regenerate or not (exp_dir / 'report' / 'experiment_report.md').exists():
        print("生成实验报告...")
        report_path = manager.create_experiment_report(exp_dir)
    else:
        report_path = exp_dir / 'report' / 'experiment_report.md'
    
    # 显示报告
    if args.open:
        import subprocess
        subprocess.run(['open', report_path])
    else:
        with open(report_path, 'r', encoding='utf-8') as f:
            print(f.read())


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="星际争霸II单位评估实验管理系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 运行单个实验
  python run_experiment.py run configs/examples/unit_evaluation.yaml
  
  # 运行批量实验
  python run_experiment.py batch configs/batch/full_analysis.yaml
  
  # 列出最近的实验
  python run_experiment.py list --limit 5
  
  # 创建新配置
  python run_experiment.py create -t basic_unit_eval -o my_config.yaml
        """
    )
    
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='显示详细输出')
    
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # run - 运行单个实验
    parser_run = subparsers.add_parser('run', help='运行单个实验')
    parser_run.add_argument('config', help='配置文件路径')
    parser_run.add_argument('-n', '--name', help='覆盖实验名称')
    parser_run.add_argument('-c', '--commanders', help='覆盖指挥官列表(逗号分隔)')
    parser_run.add_argument('-u', '--units', help='覆盖单位列表(逗号分隔)')
    parser_run.add_argument('--no-plots', action='store_true', help='不生成图表')
    parser_run.add_argument('--no-report', action='store_true', help='不生成报告')
    
    # batch - 运行批量实验
    parser_batch = subparsers.add_parser('batch', help='运行批量实验')
    parser_batch.add_argument('batch', help='批量配置文件路径')
    
    # list - 列出实验
    parser_list = subparsers.add_parser('list', help='列出已运行的实验')
    parser_list.add_argument('-t', '--type', help='筛选实验类型')
    parser_list.add_argument('-s', '--status', help='筛选状态')
    parser_list.add_argument('-l', '--limit', type=int, default=10,
                            help='显示数量限制(默认10)')
    
    # configs - 列出配置
    parser_configs = subparsers.add_parser('configs', help='列出可用的配置文件')
    
    # create - 创建配置
    parser_create = subparsers.add_parser('create', help='从模板创建新配置')
    parser_create.add_argument('-t', '--template', default='basic_unit_eval',
                              help='模板名称')
    parser_create.add_argument('-o', '--output', required=True,
                              help='输出文件路径')
    parser_create.add_argument('-n', '--name', help='实验名称')
    parser_create.add_argument('--list-templates', action='store_true',
                              help='列出可用模板')
    parser_create.add_argument('--edit', action='store_true',
                              help='创建后打开编辑')
    
    # report - 查看报告
    parser_report = subparsers.add_parser('report', help='查看实验报告')
    parser_report.add_argument('exp_dir', nargs='?', help='实验目录(默认最新)')
    parser_report.add_argument('--regenerate', action='store_true',
                              help='重新生成报告')
    parser_report.add_argument('--open', action='store_true',
                              help='在默认程序中打开')
    
    # 解析参数
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.verbose)
    
    # 执行命令
    if args.command == 'run':
        cmd_run(args)
    elif args.command == 'batch':
        cmd_batch(args)
    elif args.command == 'list':
        cmd_list(args)
    elif args.command == 'configs':
        cmd_configs(args)
    elif args.command == 'create':
        cmd_create(args)
    elif args.command == 'report':
        cmd_report(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()