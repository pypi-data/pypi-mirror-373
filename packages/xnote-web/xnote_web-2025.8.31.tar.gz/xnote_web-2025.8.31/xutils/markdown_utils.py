

def has_latex(content: str):
    """检测文本中是否含有latex公式"""
    if "```latex" in content:
        return True
    if "\\(" in content and "\\)" in content:
        return True
    if "\\[" in content and "\\]" in content:
        return True
    return False