"""
模板加载器
用于从文件系统加载模板文件
"""

import os
from pathlib import Path
from typing import Dict, Any


class TemplateLoader:
    """模板加载器"""
    
    def __init__(self, template_dir: Path):
        """初始化模板加载器
        
        Args:
            template_dir: 模板目录路径
        """
        self.template_dir = template_dir
    
    def load_template(self, template_path: str) -> str:
        """加载模板文件
        
        Args:
            template_path: 相对于模板目录的路径
            
        Returns:
            模板内容
        """
        full_path = self.template_dir / template_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"模板文件不存在: {full_path}")
            
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def render_template(self, template_path: str, context: Dict[str, Any]) -> str:
        """渲染模板
        
        Args:
            template_path: 模板路径
            context: 渲染上下文
            
        Returns:
            渲染后的内容
        """
        template_content = self.load_template(template_path)
        
        # 简单的模板渲染 - 替换占位符
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            template_content = template_content.replace(placeholder, str(value))
        
        return template_content