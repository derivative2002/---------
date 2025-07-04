#!/bin/bash
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
