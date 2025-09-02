#!/usr/bin/env python3
"""
微服务代码生成器命令行接口
"""

import os
import sys
from pathlib import Path
import click
from loguru import logger

from .generator import MicroServiceGenerator


@click.command()
@click.option(
    "--config", "-c",
    type=click.Path(exists=True, path_type=Path),
    default=Path("config.yaml"),
    help="配置文件路径 (默认: config.yaml)"
)
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    default=Path("./output"),
    help="输出目录 (默认: ./output)"
)
@click.option(
    "--force",
    is_flag=True,
    help="强制覆盖现有文件"
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="详细输出"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="干运行模式，不实际生成文件"
)
@click.version_option(version="1.0.0", prog_name="micro-gen")
def main(config: Path, output: Path, force: bool, verbose: bool, dry_run: bool):
    """
    微服务代码生成器 - 基于整洁架构的事件驱动微服务代码生成器
    
    根据配置文件自动生成完整的微服务项目结构，包括：
    - 整洁架构项目结构
    - 事件驱动架构
    - RESTful API和gRPC服务
    - Docker容器化配置
    - 监控和日志配置
    """
    
    # 配置日志
    log_level = "DEBUG" if verbose else "INFO"
    logger.remove()
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"
    )
    
    try:
        logger.info("🚀 启动微服务代码生成器...")
        logger.info(f"配置文件: {config}")
        logger.info(f"输出目录: {output}")
        
        # 检查配置文件
        if not config.exists():
            logger.error(f"配置文件不存在: {config}")
            sys.exit(1)
        
        # 创建生成器
        generator = MicroServiceGenerator(
            config_path=config,
            output_path=output,
            force=force,
            dry_run=dry_run
        )
        
        # 运行生成器
        generator.generate()
        
        logger.success("✅ 代码生成完成！")
        
        if not dry_run:
            logger.info(f"📁 项目已生成到: {output}")
            logger.info("下一步:")
            logger.info(f"  cd {output}")
            logger.info("  make docker-run  # 启动服务")
            
    except Exception as e:
        logger.error(f"❌ 生成失败: {e}")
        if verbose:
            logger.exception("详细错误信息:")
        sys.exit(1)


@click.group()
def cli():
    """微服务代码生成器命令行工具"""
    pass


@cli.command()
@click.argument("project_name")
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    default=Path("./"),
    help="输出目录"
)
def init(project_name: str, output: Path):
    """初始化新的微服务项目配置"""
    
    config_content = f'''# {project_name} 微服务配置
project:
  name: "{project_name}"
  description: "{project_name} 微服务"
  version: "1.0.0"

aggregates:
  - name: "example"
    fields:
      - name: "id"
        type: "string"
        required: true
      - name: "name"
        type: "string"
        required: true
      - name: "description"
        type: "string"
        required: false
      - name: "created_at"
        type: "datetime"
        required: true
'''
    
    config_file = output / "config.yaml"
    config_file.write_text(config_content)
    
    logger.success(f"✅ 已创建配置文件: {config_file}")


@cli.command()
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    default=Path("./examples"),
    help="示例输出目录"
)
def examples(output: Path):
    """生成示例配置文件"""
    
    examples_dir = Path(__file__).parent / "examples"
    
    if not examples_dir.exists():
        logger.error("示例文件目录不存在")
        return
    
    output.mkdir(parents=True, exist_ok=True)
    
    # 复制所有示例文件
    import shutil
    for example_file in examples_dir.glob("*.yaml"):
        target = output / example_file.name
        shutil.copy2(example_file, target)
        logger.info(f"📋 已复制: {target}")
    
    logger.success(f"✅ 示例文件已生成到: {output}")


@cli.command()
def validate():
    """验证配置文件格式"""
    config_file = Path("config.yaml")
    
    if not config_file.exists():
        logger.error("配置文件 config.yaml 不存在")
        return
    
    try:
        from .generator import MicroServiceGenerator
        generator = MicroServiceGenerator(config_path=config_file)
        generator.validate_config()
        logger.success("✅ 配置文件格式正确")
    except Exception as e:
        logger.error(f"❌ 配置文件验证失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()