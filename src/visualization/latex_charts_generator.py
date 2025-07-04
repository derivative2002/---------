"""
LaTeX图表生成器
生成专业的LaTeX风格图表，包括柱状图、天梯榜、雷达图和热力图
"""

import pandas as pd
import numpy as np
from pathlib import Path
import subprocess
import json
from typing import Dict, List, Tuple
import tempfile
import shutil

class LaTeXChartsGenerator:
    """LaTeX图表生成器"""
    
    def __init__(self):
        self.output_dir = Path('benchmarks/latex_charts')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载五大精英单位数据
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
    
    def generate_all_charts(self):
        """生成所有图表"""
        print("生成LaTeX图表...")
        
        # 1. 柱状图 - 不同场景下的排名
        self.generate_ranking_bar_chart()
        
        # 2. 综合评分天梯榜
        self.generate_score_ladder()
        
        # 3. 雷达图
        self.generate_radar_chart()
        
        # 4. 热力图
        self.generate_heatmap()
        
        print(f"所有LaTeX图表已生成在: {self.output_dir}")
    
    def generate_ranking_bar_chart(self):
        """生成排名柱状图"""
        latex_code = r"""\documentclass[border=10pt]{standalone}
\usepackage{pgfplots}
\usepackage{xeCJK}
\setCJKmainfont{SimSun}  % 宋体
\setmainfont{Times New Roman}
\pgfplotsset{compat=1.17}

\begin{document}
\begin{tikzpicture}
\begin{axis}[
    width=14cm,
    height=10cm,
    title={\Large 五大精英单位场景排名对比},
    xlabel={单位},
    ylabel={排名（逆序，越高越好）},
    ymin=0,
    ymax=5.5,
    xtick=data,
    xticklabels={龙骑士,天罚行者,攻城坦克,穿刺者,掠袭解放者},
    xticklabel style={rotate=20,anchor=east},
    ytick={1,2,3,4,5},
    yticklabels={5,4,3,2,1},
    legend pos=north west,
    grid=major,
    grid style={dashed,gray!30},
    bar width=0.15cm,
    enlarge x limits=0.15,
]

"""
        
        # 准备数据
        scenarios = {
            'overall': '总体',
            'vs_ground': '对地',
            'vs_air': '对空',
            'vs_light': '对轻甲',
            'vs_armored': '对重甲'
        }
        
        colors = ['blue!70', 'red!70', 'green!70', 'orange!70', 'purple!70']
        
        # 为每个场景添加数据
        for i, (key, name) in enumerate(scenarios.items()):
            ranks = []
            for unit_id in self.elite_units.keys():
                rank = self.rankings[key][self.rankings[key]['unit_id'] == unit_id]['rank'].values[0]
                ranks.append(6 - rank)  # 转换为逆序
            
            coords = " ".join([f"({j},{ranks[j]})" for j in range(5)])
            latex_code += f"\\addplot[ybar,fill={colors[i]}] coordinates {{{coords}}};\n"
        
        latex_code += r"""
\legend{总体,对地,对空,对轻甲,对重甲}
\end{axis}
\end{tikzpicture}
\end{document}
"""
        
        self._compile_latex(latex_code, "ranking_bar_chart")
    
    def generate_score_ladder(self):
        """生成综合评分天梯榜"""
        # 计算综合评分
        scores = []
        for unit_id in self.elite_units.keys():
            unit_data = self.rankings['overall'][self.rankings['overall']['unit_id'] == unit_id].iloc[0]
            
            # 模拟综合评分计算（基于CEV、资源效率等）
            cev = unit_data['cev']
            resource_efficiency = cev / unit_data['effective_cost'] * 100
            
            # 简化的综合评分
            overall_score = cev * 0.6 + resource_efficiency * 0.4
            
            scores.append({
                'unit': self.elite_units[unit_id]['chinese_name'],
                'commander': self.elite_units[unit_id]['commander'],
                'score': overall_score,
                'cev': cev
            })
        
        # 排序
        scores.sort(key=lambda x: x['score'], reverse=True)
        
        latex_code = r"""\documentclass[border=10pt]{standalone}
\usepackage{pgfplots}
\usepackage{xeCJK}
\usepackage{array}
\usepackage{colortbl}
\setCJKmainfont{SimSun}
\setmainfont{Times New Roman}
\pgfplotsset{compat=1.17}

\begin{document}
\begin{tikzpicture}
\node[anchor=north west] {
\Large\textbf{综合评分天梯榜}\\[0.5cm]
\begin{tabular}{|c|l|l|r|r|}
\hline
\rowcolor{gray!20}
\textbf{排名} & \textbf{单位} & \textbf{指挥官} & \textbf{综合评分} & \textbf{CEV} \\
\hline
"""
        
        # 添加排名数据
        for i, unit in enumerate(scores):
            rank_color = ""
            if i == 0:
                rank_color = r"\cellcolor{yellow!30}"
            elif i == 1:
                rank_color = r"\cellcolor{gray!20}"
            elif i == 2:
                rank_color = r"\cellcolor{orange!20}"
            
            latex_code += f"{rank_color}{i+1} & {unit['unit']} & {unit['commander']} & "
            latex_code += f"{unit['score']:.1f} & {unit['cev']:.1f} \\\\\n"
            latex_code += r"\hline" + "\n"
        
        latex_code += r"""
\end{tabular}
};

% 添加评分说明
\node[anchor=north west, text width=10cm] at (0,-5) {
\small
\textbf{评分说明:}\\
综合评分 = CEV × 60\% + 资源效率 × 40\%\\
其中CEV为战斗效能值，资源效率为单位CEV与成本的比值
};
\end{tikzpicture}
\end{document}
"""
        
        self._compile_latex(latex_code, "score_ladder")
    
    def generate_radar_chart(self):
        """生成雷达图"""
        latex_code = r"""\documentclass[border=10pt]{standalone}
\usepackage{pgfplots}
\usepackage{xeCJK}
\setCJKmainfont{SimSun}
\setmainfont{Times New Roman}
\usetikzlibrary{pgfplots.polar}
\pgfplotsset{compat=1.17}

\begin{document}
\begin{tikzpicture}
\begin{polaraxis}[
    title={\Large 五大精英单位多维度性能对比},
    width=12cm,
    height=12cm,
    xtick={0,72,144,216,288},
    xticklabels={总体,对地,对空,对轻甲,对重甲},
    ymin=0,
    ymax=1,
    ytick={0,0.2,0.4,0.6,0.8,1},
    yticklabels={0,0.2,0.4,0.6,0.8,1},
    grid=both,
    grid style={dashed,gray!30},
    legend style={at={(1.3,1)},anchor=north west},
]

"""
        
        # 准备标准化数据
        units_data = {}
        dimensions = ['overall', 'vs_ground', 'vs_air', 'vs_light', 'vs_armored']
        
        for unit_id in self.elite_units.keys():
            values = []
            for dim in dimensions:
                df = self.rankings[dim]
                cev = df[df['unit_id'] == unit_id]['cev'].values[0]
                # 标准化到0-1
                normalized = cev / df['cev'].max()
                values.append(normalized)
            
            # 闭合多边形
            values.append(values[0])
            units_data[unit_id] = values
        
        # 绘制每个单位
        colors = ['blue', 'red', 'green', 'orange', 'purple']
        for i, (unit_id, values) in enumerate(units_data.items()):
            coords = " ".join([f"({j*72},{values[j]})" for j in range(6)])
            unit_name = self.elite_units[unit_id]['chinese_name']
            latex_code += f"\\addplot[thick,color={colors[i]},mark=*,fill={colors[i]},fill opacity=0.1] "
            latex_code += f"coordinates {{{coords}}};\n"
            latex_code += f"\\addlegendentry{{{unit_name}}}\n"
        
        latex_code += r"""
\end{polaraxis}
\end{tikzpicture}
\end{document}
"""
        
        self._compile_latex(latex_code, "radar_chart")
    
    def generate_heatmap(self):
        """生成热力图"""
        latex_code = r"""\documentclass[border=10pt]{standalone}
\usepackage{pgfplots}
\usepackage{xeCJK}
\setCJKmainfont{SimSun}
\setmainfont{Times New Roman}
\pgfplotsset{compat=1.17}
\usepgfplotslibrary{colorbrewer}

\begin{document}
\begin{tikzpicture}
\begin{axis}[
    title={\Large 五大精英单位场景排名热力图},
    width=12cm,
    height=8cm,
    colormap/RdYlGn-5,
    colorbar,
    colorbar style={
        title={排名},
        ytick={1,2,3,4,5},
        yticklabels={1,2,3,4,5},
    },
    point meta min=1,
    point meta max=5,
    xtick=data,
    ytick=data,
    xticklabels={总体,对地,对空,对轻甲,对重甲},
    yticklabels={龙骑士,天罚行者,攻城坦克,穿刺者,掠袭解放者},
    xticklabel style={rotate=30,anchor=east},
    nodes near coords={\pgfmathprintnumber\pgfplotspointmeta},
    nodes near coords style={font=\small},
    enlarge x limits=0.5,
    enlarge y limits=0.5,
]

\addplot[
    matrix plot,
    point meta=explicit,
] table[meta=C] {
    x y C
"""
        
        # 准备热力图数据
        dimensions = ['overall', 'vs_ground', 'vs_air', 'vs_light', 'vs_armored']
        for i, unit_id in enumerate(self.elite_units.keys()):
            for j, dim in enumerate(dimensions):
                rank = self.rankings[dim][self.rankings[dim]['unit_id'] == unit_id]['rank'].values[0]
                latex_code += f"    {j} {4-i} {rank}\n"
        
        latex_code += r"""};
\end{axis}
\end{tikzpicture}
\end{document}
"""
        
        self._compile_latex(latex_code, "heatmap")
    
    def _compile_latex(self, latex_code: str, filename: str):
        """编译LaTeX代码为PDF和PNG"""
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            tex_file = temp_path / f"{filename}.tex"
            
            # 写入LaTeX代码
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_code)
            
            # 编译为PDF
            try:
                # 使用xelatex支持中文
                result = subprocess.run(
                    ['xelatex', '-interaction=nonstopmode', str(tex_file)],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    # 复制PDF文件
                    pdf_file = temp_path / f"{filename}.pdf"
                    if pdf_file.exists():
                        shutil.copy(pdf_file, self.output_dir / f"{filename}.pdf")
                        print(f"✓ 生成 {filename}.pdf")
                    
                    # 转换为PNG（如果有pdftoppm）
                    try:
                        subprocess.run(
                            ['pdftoppm', '-png', '-r', '300', str(pdf_file), str(temp_path / filename)],
                            check=True
                        )
                        png_file = temp_path / f"{filename}-1.png"
                        if png_file.exists():
                            shutil.copy(png_file, self.output_dir / f"{filename}.png")
                            print(f"✓ 生成 {filename}.png")
                    except:
                        print(f"⚠ 无法转换 {filename}.pdf 为 PNG（需要安装 poppler-utils）")
                else:
                    print(f"✗ 编译 {filename}.tex 失败")
                    print(result.stderr)
                    
                    # 保存tex文件以便调试
                    shutil.copy(tex_file, self.output_dir / f"{filename}.tex")
                    print(f"  LaTeX源文件保存在: {self.output_dir / filename}.tex")
                    
            except FileNotFoundError:
                print("✗ 未找到 xelatex 命令，需要安装 TeX 发行版（如 TeX Live 或 MiKTeX）")
                # 保存LaTeX源文件
                shutil.copy(tex_file, self.output_dir / f"{filename}.tex")
                print(f"  LaTeX源文件保存在: {self.output_dir / filename}.tex")


def main():
    """主函数"""
    generator = LaTeXChartsGenerator()
    generator.generate_all_charts()


if __name__ == "__main__":
    main()