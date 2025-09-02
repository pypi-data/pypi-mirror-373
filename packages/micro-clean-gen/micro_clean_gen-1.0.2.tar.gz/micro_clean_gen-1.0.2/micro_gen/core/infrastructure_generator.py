"""
基础设施层生成器 - 重构版本
使用模板文件而不是硬编码字符串
"""

import os
from pathlib import Path
from typing import Dict, List, Any

from .templates.template_loader import TemplateLoader


class InfrastructureGenerator:
    """基础设施层生成器 - 使用模板文件"""

    def __init__(self, config: Dict[str, Any], base_path: Path):
        self.config = config
        self.project_name = config["project"]["name"]
        self.base_path = base_path
        
        # 初始化模板加载器
        template_dir = Path(__file__).parent / "templates"
        self.template_loader = TemplateLoader(template_dir)

    def generate(self):
        """生成基础设施层代码"""
        print("🏗️  生成基础设施层代码...")

        # 生成事件存储
        self.generate_event_store()

        # 生成投影存储
        self.generate_projection_store()

        # 生成缓存存储
        self.generate_cache_store()

        # 生成依赖注入容器
        self.generate_container()

        # 生成引导程序
        self.generate_bootstrap()

    def generate_event_store(self):
        """生成事件存储"""
        
        # 为每个聚合生成事件存储
        for aggregate in self.config["aggregates"]:
            name = aggregate["name"]
            name_upper = name.capitalize()
            name_lower = name.lower()

            # 生成NATS事件存储
            context = {
                "ProjectName": self.project_name,
                "NameUpper": name_upper,
                "NameLower": name_lower,
            }
            
            event_store_content = self.template_loader.render_template(
                "infrastructure/nats_event_store.go.tmpl", context
            )

            event_store_path = (
                self.base_path
                / "internal"
                / "infrastructure"
                / "eventstore"
                / "nats_event_store.go"
            )
            self.write_file(event_store_path, event_store_content)

            # 生成快照存储
            snapshot_content = self.template_loader.render_template(
                "infrastructure/snapshot_store.go.tmpl", context
            )

            snapshot_path = (
                self.base_path
                / "internal"
                / "infrastructure"
                / "eventstore"
                / "snapshot_store.go"
            )
            self.write_file(snapshot_path, snapshot_content)

            break  # 只需要生成一次

    def generate_cache_store(self):
        """生成缓存存储"""
        
        cache_content = self.template_loader.render_template(
            "infrastructure/cache_store.go.tmpl", {"ProjectName": self.project_name}
        )

        cache_path = (
            self.base_path
            / "internal"
            / "infrastructure"
            / "cache"
            / "cache_store.go"
        )
        self.write_file(cache_path, cache_content)

    def generate_projection_store(self):
        """生成投影存储"""
        
        # 为每个聚合生成投影存储
        for aggregate in self.config["aggregates"]:
            name = aggregate["name"]
            name_upper = name.capitalize()
            name_lower = name.lower()

            # 生成字段赋值和更新
            field_assigns = []
            field_updates = []

            for field in aggregate["fields"]:
                field_assigns.append(f"{field['name']}: e.{field['name']},")
                field_updates.append(f"model.{field['name']} = e.{field['name']}")

            context = {
                "ProjectName": self.project_name,
                "NameUpper": name_upper,
                "NameLower": name_lower,
                "FieldAssignments": "\n        ".join(field_assigns),
                "FieldUpdates": "\n    ".join(field_updates),
            }

            # 使用模板文件
            projection_content = self.template_loader.render_template(
                "infrastructure/memory_projection.go.tmpl", context
            )

            projection_path = (
                self.base_path
                / "internal"
                / "infrastructure"
                / "projection"
                / f"memory_{name_lower}_projection.go"
            )
            self.write_file(projection_path, projection_content)

    def generate_container(self):
        """生成依赖注入容器"""
        
        # 生成容器和配置
        container_content = self.generate_container_content()
        config_content = self.generate_config_content()

        container_path = (
            self.base_path
            / "internal"
            / "infrastructure"
            / "container"
            / "container.go"
        )
        self.write_file(container_path, container_content)

        config_path = (
            self.base_path
            / "internal"
            / "infrastructure"
            / "container"
            / "config.go"
        )
        self.write_file(config_path, config_content)

    def generate_bootstrap(self):
        """生成引导程序"""
        
        # 生成引导程序和主程序
        bootstrap_content = self.generate_bootstrap_content()
        main_content = self.generate_main_content()

        bootstrap_path = (
            self.base_path
            / "internal"
            / "infrastructure"
            / "bootstrap"
            / "bootstrap.go"
        )
        self.write_file(bootstrap_path, bootstrap_content)

        main_path = self.base_path / "cmd" / "server" / "main.go"
        self.write_file(main_path, main_content)

    def generate_container_content(self) -> str:
        """生成容器内容"""
        context = {"ProjectName": self.project_name}
        return self.template_loader.render_template("infrastructure/container.go.tmpl", context)

    def generate_config_content(self) -> str:
        """生成配置内容"""
        context = {"ProjectName": self.project_name}
        return self.template_loader.render_template("infrastructure/config.go.tmpl", context)

    def generate_bootstrap_content(self) -> str:
        """生成引导程序内容"""
        context = {"ProjectName": self.project_name}
        return self.template_loader.render_template("infrastructure/bootstrap.go.tmpl", context)

    def generate_main_content(self) -> str:
        """生成主程序内容"""
        context = {"ProjectName": self.project_name}
        return self.template_loader.render_template("infrastructure/main.go.tmpl", context)

    def write_file(self, path: Path, content: str):
        """Write content to file"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
