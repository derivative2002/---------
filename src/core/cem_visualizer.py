"""
战斗效能矩阵(CEM)可视化模块
生成单位克制关系热图和交互式可视化
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import pandas as pd
from matplotlib import rcParams
from matplotlib.font_manager import FontProperties

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class CEMVisualizer:
    """战斗效能矩阵可视化器"""
    
    def __init__(self):
        # 单位类型定义
        self.unit_types = {
            "生物": ["陆战队员", "幽灵", "掠夺者", "医疗兵", "雷兽", "跳虫", "刺蛇", "感染者"],
            "机械": ["攻城坦克", "雷神", "战列巡航舰", "解放者", "旋风", "恶火", "响尾蛇"],
            "灵能": ["高阶圣堂武士", "执政官", "黑暗圣堂武士", "升格者", "先知", "哨兵"],
            "重甲": ["雷神", "战列巡航舰", "大和炮", "雷兽", "托拉斯克", "巨像", "不朽者"],
            "轻甲": ["跳虫", "陆战队员", "狂热者", "追猎者", "医疗运输机", "维京战机"],
            "空军": ["解放者", "战列巡航舰", "维京战机", "女妖", "渡鸦", "科学球", "风暴战舰"]
        }
        
        # 克制关系定义 (攻击方对防守方的效率系数)
        self.counter_matrix = self._initialize_counter_matrix()
        
        # 可视化参数
        self.figsize = (12, 10)
        self.cmap = "RdYlBu_r"  # 红黄蓝反转配色
        
    def _initialize_counter_matrix(self) -> Dict[Tuple[str, str], float]:
        """
        初始化单位克制关系矩阵
        返回: {(攻击单位, 防守单位): 效率系数}
        """
        matrix = {}
        
        # 基础克制关系
        counters = [
            # 生物克制
            ("陆战队员", "跳虫", 1.5),
            ("陆战队员", "狂热者", 0.7),
            ("雷兽", "陆战队员", 2.0),
            ("雷兽", "攻城坦克", 1.3),
            
            # 机械克制
            ("攻城坦克", "陆战队员", 2.5),
            ("攻城坦克", "刺蛇", 2.0),
            ("攻城坦克", "雷兽", 0.8),
            ("雷神", "雷兽", 1.8),
            ("雷神", "战列巡航舰", 0.9),
            
            # 空军克制
            ("解放者", "陆战队员", 3.0),
            ("解放者", "刺蛇", 2.5),
            ("维京战机", "解放者", 2.0),
            ("维京战机", "战列巡航舰", 1.8),
            
            # 灵能克制
            ("高阶圣堂武士", "陆战队员", 2.2),
            ("高阶圣堂武士", "跳虫", 2.8),
            ("升格者", "机械单位", 1.6),
            ("黑暗圣堂武士", "攻城坦克", 2.5),
            
            # 特殊克制
            ("幽灵", "雷兽", 3.0),  # 狙击
            ("幽灵", "高阶圣堂武士", 2.5),  # EMP
            ("渡鸦", "黑暗圣堂武士", 2.0),  # 侦测
            ("科学球", "施法单位", 1.8),  # 辐射
        ]
        
        # 构建矩阵
        for attacker, defender, efficiency in counters:
            matrix[(attacker, defender)] = efficiency
            # 默认效率为1.0
            if (defender, attacker) not in matrix:
                matrix[(defender, attacker)] = 1.0 / efficiency if efficiency > 1 else 1.2
                
        return matrix
    
    def create_cem_heatmap(self, 
                          units: List[str], 
                          title: str = "战斗效能矩阵 (CEM)",
                          save_path: Optional[str] = None) -> plt.Figure:
        """
        创建CEM热图
        
        参数:
            units: 要显示的单位列表
            title: 图表标题
            save_path: 保存路径（可选）
        """
        n_units = len(units)
        matrix = np.ones((n_units, n_units))
        
        # 填充矩阵
        for i, attacker in enumerate(units):
            for j, defender in enumerate(units):
                if attacker == defender:
                    matrix[i, j] = 1.0
                else:
                    # 查找克制关系
                    efficiency = self.counter_matrix.get((attacker, defender), 1.0)
                    matrix[i, j] = efficiency
        
        # 创建图表
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # 绘制热图
        sns.heatmap(matrix, 
                   annot=True, 
                   fmt='.2f',
                   cmap=self.cmap,
                   center=1.0,
                   vmin=0.5,
                   vmax=3.0,
                   xticklabels=units,
                   yticklabels=units,
                   cbar_kws={'label': '战斗效率系数'},
                   ax=ax)
        
        # 设置标签
        ax.set_xlabel('防守单位', fontsize=12)
        ax.set_ylabel('攻击单位', fontsize=12)
        ax.set_title(title, fontsize=16, pad=20)
        
        # 旋转x轴标签
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        # 添加网格线
        ax.set_xticks(np.arange(n_units) + 0.5, minor=True)
        ax.set_yticks(np.arange(n_units) + 0.5, minor=True)
        ax.grid(which="minor", color="gray", linestyle='-', linewidth=0.5)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        return fig
    
    def create_unit_matchup_chart(self, 
                                 unit_name: str,
                                 top_n: int = 10) -> plt.Figure:
        """
        创建特定单位的优劣势对战图
        """
        # 收集该单位的所有对战数据
        matchups = []
        
        # 作为攻击方
        for (attacker, defender), efficiency in self.counter_matrix.items():
            if attacker == unit_name:
                matchups.append({
                    'opponent': defender,
                    'efficiency': efficiency,
                    'role': '攻击'
                })
        
        # 作为防守方
        for (attacker, defender), efficiency in self.counter_matrix.items():
            if defender == unit_name:
                matchups.append({
                    'opponent': attacker,
                    'efficiency': 1.0 / efficiency,  # 反转效率
                    'role': '防守'
                })
        
        if not matchups:
            print(f"未找到单位 '{unit_name}' 的对战数据")
            return None
            
        # 转换为DataFrame并排序
        df = pd.DataFrame(matchups)
        df_sorted = df.sort_values('efficiency', ascending=False)
        
        # 选择前N个和后N个
        top_matchups = df_sorted.head(top_n)
        bottom_matchups = df_sorted.tail(top_n)
        plot_data = pd.concat([top_matchups, bottom_matchups])
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 设置颜色
        colors = ['green' if x >= 1.5 else 'red' if x <= 0.7 else 'gray' 
                 for x in plot_data['efficiency']]
        
        # 绘制水平条形图
        bars = ax.barh(plot_data['opponent'], plot_data['efficiency'], color=colors)
        
        # 添加数值标签
        for bar, eff in zip(bars, plot_data['efficiency']):
            width = bar.get_width()
            ax.text(width + 0.05, bar.get_y() + bar.get_height()/2, 
                   f'{eff:.2f}', 
                   ha='left', va='center')
        
        # 添加基准线
        ax.axvline(x=1.0, color='black', linestyle='--', alpha=0.5)
        
        # 设置标签
        ax.set_xlabel('战斗效率系数', fontsize=12)
        ax.set_title(f'{unit_name} 单位对战效率分析', fontsize=16, pad=20)
        ax.set_xlim(0, max(plot_data['efficiency']) * 1.2)
        
        # 添加图例
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='green', label='克制 (≥1.5)'),
            Patch(facecolor='gray', label='均势 (0.7-1.5)'),
            Patch(facecolor='red', label='被克制 (≤0.7)')
        ]
        ax.legend(handles=legend_elements, loc='lower right')
        
        plt.tight_layout()
        return fig
    
    def create_commander_balance_chart(self, 
                                     commander_units: Dict[str, List[str]]) -> plt.Figure:
        """
        创建指挥官平衡性对比图
        
        参数:
            commander_units: {指挥官名称: [单位列表]}
        """
        commander_scores = {}
        
        for commander, units in commander_units.items():
            # 计算该指挥官所有单位的平均克制系数
            all_efficiencies = []
            
            for unit in units:
                for (attacker, defender), efficiency in self.counter_matrix.items():
                    if attacker == unit:
                        all_efficiencies.append(efficiency)
                    elif defender == unit:
                        all_efficiencies.append(1.0 / efficiency)
            
            if all_efficiencies:
                avg_efficiency = np.mean(all_efficiencies)
                std_efficiency = np.std(all_efficiencies)
                commander_scores[commander] = {
                    'average': avg_efficiency,
                    'std': std_efficiency,
                    'versatility': 1.0 / (std_efficiency + 0.1)  # 多样性得分
                }
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 图1: 平均效率
        commanders = list(commander_scores.keys())
        avg_scores = [commander_scores[c]['average'] for c in commanders]
        
        bars1 = ax1.bar(commanders, avg_scores, color='steelblue')
        ax1.axhline(y=1.0, color='red', linestyle='--', alpha=0.5)
        ax1.set_ylabel('平均战斗效率')
        ax1.set_title('指挥官单位平均战斗效率')
        ax1.set_xticklabels(commanders, rotation=45, ha='right')
        
        # 添加数值标签
        for bar, score in zip(bars1, avg_scores):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'{score:.2f}', ha='center', va='bottom')
        
        # 图2: 多样性得分
        versatility_scores = [commander_scores[c]['versatility'] for c in commanders]
        
        bars2 = ax2.bar(commanders, versatility_scores, color='darkgreen')
        ax2.set_ylabel('单位多样性得分')
        ax2.set_title('指挥官单位多样性评分')
        ax2.set_xticklabels(commanders, rotation=45, ha='right')
        
        # 添加数值标签
        for bar, score in zip(bars2, versatility_scores):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'{score:.2f}', ha='center', va='bottom')
        
        plt.tight_layout()
        return fig
    
    def export_cem_data(self, units: List[str], output_path: str):
        """导出CEM数据为CSV格式"""
        n_units = len(units)
        matrix = np.ones((n_units, n_units))
        
        # 填充矩阵
        for i, attacker in enumerate(units):
            for j, defender in enumerate(units):
                if attacker != defender:
                    efficiency = self.counter_matrix.get((attacker, defender), 1.0)
                    matrix[i, j] = efficiency
        
        # 创建DataFrame
        df = pd.DataFrame(matrix, index=units, columns=units)
        df.to_csv(output_path, encoding='utf-8-sig')
        print(f"CEM数据已导出到: {output_path}")


# 使用示例
if __name__ == "__main__":
    visualizer = CEMVisualizer()
    
    # 示例1: 创建主要单位的CEM热图
    main_units = [
        "陆战队员", "掠夺者", "攻城坦克", "雷神",
        "跳虫", "刺蛇", "雷兽",
        "狂热者", "追猎者", "不朽者", "高阶圣堂武士",
        "升格者", "解放者", "维京战机"
    ]
    
    fig1 = visualizer.create_cem_heatmap(
        main_units, 
        title="星际争霸II 主要单位战斗效能矩阵"
    )
    plt.show()
    
    # 示例2: 分析特定单位的优劣势
    fig2 = visualizer.create_unit_matchup_chart("陆战队员")
    if fig2:
        plt.show()
    
    # 示例3: 指挥官平衡性分析
    commander_units_example = {
        "吉姆·雷诺": ["陆战队员", "掠夺者", "攻城坦克", "战列巡航舰"],
        "凯瑞甘": ["跳虫", "刺蛇", "雷兽", "飞龙"],
        "阿塔尼斯": ["狂热者", "龙骑士", "执政官", "风暴战舰"],
        "诺娃·泰拉": ["幽灵", "掠夺者", "攻城坦克", "解放者"]
    }
    
    fig3 = visualizer.create_commander_balance_chart(commander_units_example)
    plt.show()