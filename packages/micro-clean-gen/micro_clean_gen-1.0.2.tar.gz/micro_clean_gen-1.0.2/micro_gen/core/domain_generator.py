"""
领域层生成器
负责生成聚合根、领域事件、仓储接口等核心领域对象
"""

import os
from pathlib import Path
from typing import Dict, List, Any
from .templates.template_loader import TemplateLoader


class DomainGenerator:
    """领域层生成器"""

    def __init__(self, config: Dict[str, Any], base_path: Path):
        self.config = config
        self.project_name = config["project"]["name"]
        self.base_path = base_path
        self.template_loader = TemplateLoader(Path(__file__).parent / "templates" / "domain")

        # 类型映射
        self.go_type_mapping = {
            "string": "string",
            "int": "int",
            "float": "float64",
            "bool": "bool",
            "time": "time.Time",
            "uuid": "string",
        }

    def generate(self):
        """生成领域层代码"""
        print("🏗️  生成领域层代码...")

        # 生成聚合根
        self.generate_aggregates()

        # 生成领域事件
        self.generate_events()

        # 生成仓储接口
        self.generate_repositories()

        # 生成投影接口
        self.generate_projections()

    def generate_aggregates(self):
        """生成聚合根"""

        # 为每个聚合生成代码
        for aggregate in self.config["aggregates"]:
            name = aggregate["name"]

            # 生成字段定义
            fields = []
            params = []
            assigns = []
            event_fields = []
            apply_fields = []
            update_fields = []

            for field in aggregate["fields"]:
                field_name = field["name"]
                field_type = self.go_type_mapping.get(field["type"], "string")
                json_tag = field.get("json", field["name"])

                fields.append(f'{field_name} {field_type} `json:"{json_tag}"`')
                params.append(f"{field_name} {field_type}")
                assigns.append(f"{field_name}: {field_name},")
                event_fields.append(f"{field_name}: {field_name},")
                apply_fields.append(f"a.{field_name} = e.{field_name}")
                update_fields.append(f"a.{field_name} = e.{field_name}")

            # 使用模板生成聚合根
            aggregate_content = self.template_loader.render_template(
                "aggregate.go.tmpl",
                {
                    "Name": name.capitalize(),
                    "name": name.lower(),
                    "fields": "\n    ".join(fields),
                    "params": ", ".join(params),
                    "field_assigns": "\n        ".join(assigns),
                    "event_fields": "\n        ".join(event_fields),
                    "apply_fields": "\n    ".join(apply_fields),
                    "update_fields": "\n    ".join(update_fields),
                    "project": self.project_name,
                },
            )

            aggregate_path = (
                self.base_path
                / "internal"
                / "domain"
                / "aggregate"
                / f"{name.lower()}.go"
            )
            self.write_file(aggregate_path, aggregate_content)

    def generate_events(self):
        """生成领域事件"""

        # 为每个聚合生成事件
        for aggregate in self.config["aggregates"]:
            name = aggregate["name"]

            # 生成默认事件
            events = aggregate.get("events", [])
            if not events:
                # 如果没有定义事件，创建默认的CRUD事件
                events = [
                    {"name": f"{name}CreatedEvent", "fields": aggregate["fields"]},
                    {"name": f"{name}UpdatedEvent", "fields": aggregate["fields"]},
                    {
                        "name": f"{name}DeletedEvent",
                        "fields": [{"name": "ID", "type": "string"}],
                    },
                ]

            for event in events:
                event_fields = []
                for field in event.get("fields", []):
                    field_name = field["name"]
                    field_type = self.go_type_mapping.get(field["type"], "string")
                    json_tag = field.get("json", field["name"])
                    event_fields.append(
                        f'{field_name} {field_type} `json:"{json_tag}"`'
                    )

                event_content = self.template_loader.render_template(
                    "event.go.tmpl",
                    {
                        "EventName": event["name"],
                        "event_name": event["name"].lower(),
                        "fields": "\n    ".join(event_fields),
                    },
                )

                event_path = (
                    self.base_path
                    / "internal"
                    / "domain"
                    / "event"
                    / f"{event['name'].lower()}.go"
                )
                self.write_file(event_path, event_content)

    def generate_repositories(self):
        """生成仓储接口"""

        # 为每个聚合生成仓储接口
        for aggregate in self.config["aggregates"]:
            name = aggregate["name"]

            repository_content = self.template_loader.render_template(
                "repository.go.tmpl",
                {
                    "Name": name.capitalize(),
                    "name": name.lower(),
                    "project": self.project_name,
                },
            )

            repository_path = (
                self.base_path
                / "internal"
                / "domain"
                / "repository"
                / f"{name.lower()}_repository.go"
            )
            self.write_file(repository_path, repository_content)

    def generate_projections(self):
        """生成投影接口"""

        # 为每个聚合生成投影接口
        for aggregate in self.config["aggregates"]:
            name = aggregate["name"]

            fields = []
            for field in aggregate["fields"]:
                field_name = field["name"]
                field_type = self.go_type_mapping.get(field["type"], "string")
                json_tag = field.get("json", field["name"])
                fields.append(f'{field_name} {field_type} `json:"{json_tag}"`')

            projection_content = self.template_loader.render_template(
                "projection.go.tmpl",
                {
                    "Name": name.capitalize(),
                    "fields": "\n    ".join(fields),
                    "project": self.project_name,
                },
            )

            projection_path = (
                self.base_path
                / "internal"
                / "domain"
                / "projection"
                / f"{name.lower()}_projection.go"
            )
            self.write_file(projection_path, projection_content)

    def write_file(self, path: Path, content: str):
        """写入文件"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
