import re
import glob

def check_markdown_rules():
    files = glob.glob("chapters/*.md")
    for f in files:
        with open(f, "r", encoding="utf-8") as file:
            content = file.read()
            # 1. 检查是否存在裸写的图片绝对路径
            if re.search(r'!\[.*?\]\([C-Z]:[/\\]', content):
                print(f"[警告] {f} 中包含绝对路径图片引用！")
            # 2. 检查是否有未闭合的数学公式 $$
            if content.count("$$") % 2 != 0:
                print(f"[错误] {f} 中存在未闭合的块级公式 $$！")
            # 3. 检查是否有中文全角符号夹杂在公式环境内
            if re.search(r'\$[^\$]*[，。！？][^\$]*\$', content):
                print(f"[提示] {f} 的 LaTeX 行内公式中疑似包含中文标点！")

if __name__ == "__main__":
    check_markdown_rules()