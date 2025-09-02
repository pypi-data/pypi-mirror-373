"""
微服务代码生成器主类
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List
from loguru import logger

from .core.generator import CleanArchitectureGenerator


class MicroServiceGenerator:
    """微服务代码生成器主类"""
    
    def __init__(self, config_path: Path, output_path: Path = None, force: bool = False, dry_run: bool = False):
        self.config_path = Path(config_path)
        self.output_path = Path(output_path) if output_path else Path("./output")
        self.force = force
        self.dry_run = dry_run
        self.config = None
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self.config_path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                elif self.config_path.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    raise ValueError(f"不支持的配置文件格式: {self.config_path.suffix}")
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise
    
    def validate_config(self) -> List[str]:
        """验证配置文件"""
        from .core.utils import validate_config
        
        if not self.config:
            self.config = self.load_config()
        
        errors = validate_config(self.config)
        
        if errors:
            logger.error("配置验证失败:")
            for error in errors:
                logger.error(f"  - {error}")
        else:
            logger.success("配置验证通过")
        
        return errors
    
    def generate(self) -> None:
        """生成微服务代码"""
        # 加载配置
        self.config = self.load_config()
        
        # 验证配置
        errors = self.validate_config()
        if errors:
            raise ValueError("配置文件验证失败")
        
        # 创建输出目录
        if not self.dry_run:
            self.output_path.mkdir(parents=True, exist_ok=True)
        
        # 创建生成器
        generator = CleanArchitectureGenerator(self.config, self.output_path)
        
        # 设置生成选项
        generator.force = self.force
        generator.dry_run = self.dry_run
        
        # 执行生成
        generator.generate()
        
        logger.success("🎉 微服务代码生成完成！")