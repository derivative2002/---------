#!/bin/bash
# 编译v2.2版本论文的脚本

echo "开始编译论文v2.2版本..."

# 使用xelatex编译（支持中文）
xelatex report.tex

# 如果有参考文献，运行bibtex
if [ -f report.bib ]; then
    bibtex report
    xelatex report.tex
fi

# 再次编译以确保交叉引用正确
xelatex report.tex

# 清理临时文件
rm -f *.aux *.log *.toc *.out *.nav *.snm *.vrb *.bbl *.blg

echo "编译完成！生成的PDF文件：report.pdf"

# 复制到上级目录
cp report.pdf ../report_v2.2.pdf
echo "已复制到 ../report_v2.2.pdf"