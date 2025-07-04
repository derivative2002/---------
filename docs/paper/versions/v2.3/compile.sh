#!/bin/bash

# 编译v2.3版本论文

echo "=== 编译v2.3版本论文 ==="

# 确保在正确的目录
cd "$(dirname "$0")"

# 清理临时文件
echo "清理临时文件..."
rm -f report_draft.aux report_draft.log report_draft.out report_draft.toc

# 第一次编译（生成aux文件）
echo "第一次编译..."
xelatex report_draft.tex

# 第二次编译（生成目录）
echo "第二次编译（生成目录）..."
xelatex report_draft.tex

# 第三次编译（确保引用正确）
echo "第三次编译（最终版本）..."
xelatex report_draft.tex

# 重命名为正式版本
if [ -f report_draft.pdf ]; then
    mv report_draft.pdf report.pdf
    echo "✅ 编译成功！生成文件：report.pdf"
else
    echo "❌ 编译失败！"
    exit 1
fi

# 清理临时文件
echo "清理编译临时文件..."
rm -f report_draft.aux report_draft.log report_draft.out report_draft.toc

echo "=== 编译完成 ===
"