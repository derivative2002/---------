# Makefile for v2.5 paper

# 源文件
TEX_FILE = v25_paper.tex
BIB_FILE = references.bib

# 输出文件
PDF_FILE = v25_paper.pdf

# 命令
LATEX = xelatex
BIBTEX = bibtex

# 默认目标
all: $(PDF_FILE)

# 编译规则
$(PDF_FILE): $(TEX_FILE) $(BIB_FILE)
	$(LATEX) $(TEX_FILE)
	$(BIBTEX) $(basename $(TEX_FILE))
	$(LATEX) $(TEX_FILE)
	$(LATEX) $(TEX_FILE)

# 清理临时文件
clean:
	rm -f *.aux *.log *.out *.toc *.lof *.lot *.bbl *.blg *.synctex.gz

# 完全清理（包括PDF）
cleanall: clean
	rm -f $(PDF_FILE)

# 重新编译
rebuild: cleanall all

.PHONY: all clean cleanall rebuild 