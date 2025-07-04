#!/usr/bin/env python3
"""
论文v2.3修改辅助工具
帮助快速定位和标记需要修改的内容
"""

import re
import os
from typing import List, Tuple, Dict

class PaperModificationHelper:
    """论文修改辅助工具"""
    
    def __init__(self, tex_file_path: str):
        self.tex_file_path = tex_file_path
        self.content = self._read_file()
        self.lines = self.content.split('\n')
        
    def _read_file(self) -> str:
        """读取LaTeX文件"""
        with open(self.tex_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def find_text_locations(self, search_patterns: List[str]) -> Dict[str, List[Tuple[int, str]]]:
        """查找文本位置"""
        results = {}
        for pattern in search_patterns:
            matches = []
            for i, line in enumerate(self.lines, 1):
                if pattern in line:
                    matches.append((i, line.strip()))
            results[pattern] = matches
        return results
    
    def generate_modification_report(self):
        """生成修改报告"""
        print("=== 论文v2.3修改位置报告 ===\n")
        
        # 1. 事实性错误位置
        print("## 1. 事实性错误位置\n")
        
        fact_errors = [
            ("凯瑞甘、诺娃·泰拉", "需修改为正确的100人口指挥官列表"),
            ("轨道轰炸", "修改为'狮鹫号空袭'"),
            ("α = 2.5", "添加采集效率说明"),
            ("陆战队员.*泰凯斯", "修改为攻城坦克在不同指挥官"),
            ("强化我", "修改为'供奉我'"),
            ("诺娃·泰拉", "统一简称为'诺娃'"),
        ]
        
        for pattern, description in fact_errors:
            print(f"### 查找: {pattern}")
            print(f"说明: {description}")
            locations = self.find_text_locations([pattern])
            for pat, locs in locations.items():
                if locs:
                    for line_num, line_text in locs:
                        print(f"  行 {line_num}: {line_text[:80]}...")
                else:
                    print("  未找到匹配")
            print()
        
        # 2. 需要删除的章节
        print("\n## 2. 需要删除的章节\n")
        
        sections_to_delete = [
            ("section{新单位设计框架}", "整章删除"),
            ("subsection{设计原则总结}", "删除小节"),
            ("subsection{迭代优化流程}", "删除小节"),
            ("完整的单位设计工作流程", "从摘要中删除"),
            ("与设计框架", "从标题中删除"),
        ]
        
        for pattern, action in sections_to_delete:
            print(f"### {pattern} - {action}")
            locations = self.find_text_locations([pattern])
            for pat, locs in locations.items():
                if locs:
                    for line_num, line_text in locs:
                        print(f"  行 {line_num}: {line_text}")
                else:
                    print("  未找到")
            print()
    
    def create_backup(self):
        """创建备份"""
        backup_path = self.tex_file_path.replace('.tex', '_backup_v2.2.tex')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(self.content)
        print(f"备份已创建: {backup_path}")
    
    def apply_simple_replacements(self, output_path: str):
        """应用简单的文本替换"""
        modified_content = self.content
        
        # 定义替换规则
        replacements = [
            # 人口上限修正
            ("100人口（如凯瑞甘、诺娃·泰拉）", "100人口（如诺娃、泽拉图、扎加拉、泰凯斯）"),
            ("凯瑞甘、诺娃·泰拉）vs 200人口", "诺娃、泽拉图、扎加拉、泰凯斯）vs 200人口（如凯瑞甘"),
            
            # 技能名称修正
            ("轨道轰炸", "狮鹫号空袭（Griffin Airstrike）"),
            
            # 阿拉纳克技能名称
            ("强化我", "供奉我"),
            ("Empover Me", "Empower Me"),
            
            # 统一命名
            ("诺娃·泰拉", "诺娃"),
            
            # 标题修正
            ("单位客观评估与设计框架", "单位客观评估"),
        ]
        
        for old_text, new_text in replacements:
            count = modified_content.count(old_text)
            if count > 0:
                modified_content = modified_content.replace(old_text, new_text)
                print(f"替换 '{old_text}' -> '{new_text}' ({count}处)")
        
        # 保存修改后的文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        print(f"\n修改后的文件已保存至: {output_path}")

def main():
    """主函数"""
    # 设置路径
    base_path = "/Users/bytedance/项目/星际争霸二数学模型/docs/paper/versions"
    input_file = os.path.join(base_path, "v2.2/report.tex")
    output_file = os.path.join(base_path, "v2.3/report_draft.tex")
    
    # 创建v2.3目录
    os.makedirs(os.path.join(base_path, "v2.3"), exist_ok=True)
    
    # 初始化辅助工具
    helper = PaperModificationHelper(input_file)
    
    # 创建备份
    helper.create_backup()
    
    # 生成修改报告
    helper.generate_modification_report()
    
    # 应用简单替换
    print("\n=== 应用自动替换 ===\n")
    helper.apply_simple_replacements(output_file)
    
    print("\n=== 后续手动修改提示 ===")
    print("1. 检查并修正矿气转换率说明（第124行附近）")
    print("2. 修改陆战队员例子为攻城坦克例子")
    print("3. 删除第7章（新单位设计框架）")
    print("4. 更新六大精英单位数据表")
    print("5. 简化对抗模型为6×3矩阵")
    print("6. 更新附录B的指挥官人口上限表")

if __name__ == "__main__":
    main()