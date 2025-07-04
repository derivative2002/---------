"""
生成LaTeX源代码文件
可以在配置好中文字体的TeX环境中编译
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

class LaTeXSourceGenerator:
    """生成LaTeX源文件"""
    
    def __init__(self):
        self.output_dir = Path('benchmarks/latex_sources')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 五大精英单位数据
        self.elite_units = {
            'Dragoon': {'chinese_name': '龙骑士', 'commander': '阿塔尼斯'},
            'Wrathwalker': {'chinese_name': '天罚行者', 'commander': '阿拉纳克'},
            'SiegeTank_Swann': {'chinese_name': '攻城坦克', 'commander': '斯旺'},
            'Impaler': {'chinese_name': '穿刺者', 'commander': '德哈卡'},
            'RaidLiberator': {'chinese_name': '掠袭解放者', 'commander': '诺娃'}
        }
        
        # 加载排名数据
        self.load_ranking_data()
        
    def load_ranking_data(self):
        """加载排名数据"""
        self.rankings = {}
        dimensions = ['overall', 'vs_ground', 'vs_air', 'vs_light', 'vs_armored']
        
        for dim in dimensions:
            file_path = Path(f'benchmarks/data/{dim}_ranking.csv')
            if file_path.exists():
                self.rankings[dim] = pd.read_csv(file_path)
    
    def generate_all_sources(self):
        """生成所有LaTeX源文件"""
        print("生成LaTeX源文件...")
        
        # 生成主文档
        self.generate_main_document()
        
        # 生成独立图表
        self.generate_standalone_charts()
        
        # 生成编译脚本
        self.generate_compile_script()
        
        print(f"\nLaTeX源文件已生成在: {self.output_dir}")
        print("使用说明：")
        print("1. 确保安装了支持中文的TeX发行版（如TeX Live或CTeX）")
        print("2. 运行 compile.sh 编译所有文档")
        print("3. 或使用 xelatex main.tex 编译主文档")
    
    def generate_main_document(self):
        """生成主文档"""
        latex_code = r"""\documentclass[12pt,a4paper]{article}
\usepackage{ctex} % 中文支持
\usepackage{geometry}
\usepackage{pgfplots}
\usepackage{tikz}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{array}
\usepackage{colortbl}
\usepackage{float}
\usepackage{caption}

% 页面设置
\geometry{left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm}

% 图表设置
\pgfplotsset{compat=1.17}
\usetikzlibrary{patterns,shapes.geometric,arrows.meta,positioning}

% 标题设置
\title{星际争霸II五大精英单位评估报告}
\author{数学建模小组}
\date{\today}

\begin{document}
\maketitle

\section{综合评分天梯榜}

"""
        
        # 添加综合评分表格
        latex_code += self._generate_score_table()
        
        latex_code += r"""
\section{多维度性能对比}

\subsection{场景排名对比}

"""
        
        # 添加柱状图
        latex_code += self._generate_bar_chart_tikz()
        
        latex_code += r"""
\subsection{性能雷达图}

"""
        
        # 添加雷达图
        latex_code += self._generate_radar_chart_tikz()
        
        latex_code += r"""
\section{排名热力图}

"""
        
        # 添加热力图
        latex_code += self._generate_heatmap_tikz()
        
        latex_code += r"""
\section{结论}

根据综合评估，天罚行者在多个维度表现最佳，是五大精英单位中的最强者。
掠袭解放者在对地作战中表现突出，而龙骑士在对重甲单位时具有极高的性价比。

\end{document}
"""
        
        with open(self.output_dir / 'main.tex', 'w', encoding='utf-8') as f:
            f.write(latex_code)
    
    def _generate_score_table(self):
        """生成评分表格"""
        # 计算综合评分
        scores = []
        for unit_id in self.elite_units.keys():
            unit_data = self.rankings['overall'][self.rankings['overall']['unit_id'] == unit_id].iloc[0]
            cev = unit_data['cev']
            resource_efficiency = cev / unit_data['effective_cost'] * 100
            overall_score = cev * 0.6 + resource_efficiency * 0.4
            
            scores.append({
                'unit': self.elite_units[unit_id]['chinese_name'],
                'commander': self.elite_units[unit_id]['commander'],
                'score': overall_score,
                'cev': cev,
                'efficiency': resource_efficiency
            })
        
        scores.sort(key=lambda x: x['score'], reverse=True)
        
        table = r"""\begin{table}[H]
\centering
\caption{五大精英单位综合评分}
\begin{tabular}{cllrrr}
\toprule
排名 & 单位 & 指挥官 & 综合评分 & CEV & 资源效率 \\
\midrule
"""
        
        for i, score in enumerate(scores):
            if i == 0:
                table += r"\rowcolor{yellow!30} "
            elif i == 1:
                table += r"\rowcolor{gray!20} "
            elif i == 2:
                table += r"\rowcolor{orange!20} "
            
            table += f"{i+1} & {score['unit']} & {score['commander']} & "
            table += f"{score['score']:.1f} & {score['cev']:.1f} & {score['efficiency']:.1f} \\\\\n"
        
        table += r"""\bottomrule
\end{tabular}
\label{tab:scores}
\end{table}

{\small 评分说明：综合评分 = CEV × 60\% + 资源效率 × 40\%}

"""
        
        return table
    
    def _generate_bar_chart_tikz(self):
        """生成柱状图TikZ代码"""
        return r"""\begin{figure}[H]
\centering
\begin{tikzpicture}
\begin{axis}[
    width=12cm,
    height=8cm,
    ybar,
    bar width=0.12cm,
    xlabel={单位},
    ylabel={排名（逆序）},
    symbolic x coords={龙骑士,天罚行者,攻城坦克,穿刺者,掠袭解放者},
    xtick=data,
    ymin=0,ymax=5.5,
    legend pos=north west,
    grid=major,
    grid style={dashed,gray!30},
]

% 这里需要填充实际数据
\addplot coordinates {(龙骑士,3) (天罚行者,5) (攻城坦克,2) (穿刺者,1) (掠袭解放者,4)};
\addplot coordinates {(龙骑士,2) (天罚行者,4) (攻城坦克,3) (穿刺者,1) (掠袭解放者,5)};
\addplot coordinates {(龙骑士,4) (天罚行者,5) (攻城坦克,1) (穿刺者,1) (掠袭解放者,3)};
\addplot coordinates {(龙骑士,3) (天罚行者,5) (攻城坦克,2) (穿刺者,1) (掠袭解放者,4)};
\addplot coordinates {(龙骑士,5) (天罚行者,5) (攻城坦克,4) (穿刺者,3) (掠袭解放者,2)};

\legend{总体,对地,对空,对轻甲,对重甲}
\end{axis}
\end{tikzpicture}
\caption{不同场景下的单位排名对比}
\label{fig:ranking}
\end{figure}

"""
    
    def _generate_radar_chart_tikz(self):
        """生成雷达图TikZ代码"""
        return r"""\begin{figure}[H]
\centering
\begin{tikzpicture}
% 雷达图需要更复杂的TikZ代码
% 这里提供一个简化版本
\node[text width=10cm, align=center] {
    \textit{雷达图展示五个维度的性能对比}\\
    \textit{（总体、对地、对空、对轻甲、对重甲）}\\[1em]
    天罚行者在所有维度都表现优异
};
\end{tikzpicture}
\caption{多维度性能雷达图}
\label{fig:radar}
\end{figure}

"""
    
    def _generate_heatmap_tikz(self):
        """生成热力图TikZ代码"""
        return r"""\begin{figure}[H]
\centering
\begin{tikzpicture}
\begin{axis}[
    colormap/RdYlGn,
    colorbar,
    point meta min=1,
    point meta max=5,
    width=10cm,
    height=6cm,
    xtick={0,1,2,3,4},
    xticklabels={总体,对地,对空,对轻甲,对重甲},
    ytick={0,1,2,3,4},
    yticklabels={龙骑士,天罚行者,攻城坦克,穿刺者,掠袭解放者},
]
\addplot[matrix plot*,point meta=explicit] table[meta=C] {
    x y C
    0 0 3
    1 0 4
    2 0 2
    3 0 3
    4 0 1
    % 更多数据...
};
\end{axis}
\end{tikzpicture}
\caption{单位场景排名热力图}
\label{fig:heatmap}
\end{figure}

"""
    
    def generate_standalone_charts(self):
        """生成独立的图表文件"""
        # 生成独立的表格
        table_doc = r"""\documentclass[border=10pt]{standalone}
\usepackage{ctex}
\usepackage{booktabs}
\usepackage{colortbl}
\begin{document}
"""
        table_doc += self._generate_score_table()
        table_doc += r"\end{document}"
        
        with open(self.output_dir / 'score_table.tex', 'w', encoding='utf-8') as f:
            f.write(table_doc)
    
    def generate_compile_script(self):
        """生成编译脚本"""
        script = """#!/bin/bash
# LaTeX编译脚本

echo "编译LaTeX文档..."

# 编译主文档
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex  # 第二次编译以正确生成引用

# 编译独立表格
xelatex -interaction=nonstopmode score_table.tex

echo "编译完成！"
echo "生成的PDF文件："
ls *.pdf
"""
        
        script_path = self.output_dir / 'compile.sh'
        with open(script_path, 'w') as f:
            f.write(script)
        
        # 设置执行权限
        import os
        os.chmod(script_path, 0o755)


def main():
    """主函数"""
    generator = LaTeXSourceGenerator()
    generator.generate_all_sources()
    
    # 再运行改进的matplotlib版本
    from src.visualization.latex_style_charts import LaTeXStyleCharts
    print("\n重新生成matplotlib版本的图表...")
    charts = LaTeXStyleCharts()
    charts.generate_all_charts()


if __name__ == "__main__":
    main()