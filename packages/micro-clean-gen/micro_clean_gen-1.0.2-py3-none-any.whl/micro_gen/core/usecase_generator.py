"""
用例层生成器
负责生成命令用例、查询用例、事件处理器等业务用例
"""

import os
from pathlib import Path
from typing import Dict, List, Any
from .templates.template_loader import TemplateLoader

class UseCaseGenerator:
    """用例层生成器"""
    
    def __init__(self, config: Dict[str, Any], base_path: Path):
        self.config = config
        self.project_name = config['project']['name']
        self.base_path = base_path
        self.template_loader = TemplateLoader(Path(__file__).parent / "templates" / "usecase")
    
    def generate(self):
        """生成用例层代码"""
        print("🏗️  生成用例层代码...")
        
        # 生成命令用例
        self.generate_commands()
        
        # 生成查询用例
        self.generate_queries()
        
        # 生成事件处理器
        self.generate_event_handlers()
    
    def generate_commands(self):
        """生成命令用例"""
        
        # 为每个聚合生成命令用例
        for aggregate in self.config['aggregates']:
            name = aggregate['name']
            
            # 生成创建命令
            fields = []
            params = []
            param_assigns = []
            
            for field in aggregate['fields']:
                fields.append(f"{field['name']} {field['type']}")
                params.append(f"{field['name']}")
                param_assigns.append(f"cmd.{field['name']}")
            
            command_content = self.template_loader.render_template("create_command.go.tmpl", {
                'Name': name.capitalize(),
                'name': name.lower(),
                'fields': '\n    '.join(fields),
                'param_assigns': ',\n        '.join(param_assigns),
                'project': self.project_name
            })
            
            command_path = self.base_path / 'internal' / 'usecase' / 'command' / f"create_{name.lower()}.go"
            self.write_file(command_path, command_content)
            
            # 生成更新命令
            update_fields = []
            update_logic = []
            event_fields = []
            
            for field in aggregate['fields']:
                update_fields.append(f"{field['name']} {field['type']}")
                update_logic.append(f"{name}.{field['name']} = cmd.{field['name']}")
                event_fields.append(f"{field['name']}: cmd.{field['name']},")
            
            update_content = self.template_loader.render_template("update_command.go.tmpl", {
                'Name': name.capitalize(),
                'name': name.lower(),
                'fields': '\n    '.join(update_fields),
                'update_logic': '\n    '.join(update_logic),
                'event_fields': '\n        '.join(event_fields),
                'project': self.project_name
            })
            
            update_path = self.base_path / 'internal' / 'usecase' / 'command' / f"update_{name.lower()}.go"
            self.write_file(update_path, update_content)
    
    def generate_queries(self):
        """生成查询用例"""
        
        # 为每个聚合生成查询用例
        for aggregate in self.config['aggregates']:
            name = aggregate['name']
            
            # 生成获取查询
            query_content = self.template_loader.render_template("get_query.go.tmpl", {
                'Name': name.capitalize(),
                'name': name.lower(),
                'project': self.project_name
            })
            
            query_path = self.base_path / 'internal' / 'usecase' / 'query' / f"get_{name.lower()}.go"
            self.write_file(query_path, query_content)
            
            # 生成列表查询
            list_content = self.template_loader.render_template("list_query.go.tmpl", {
                'Name': name.capitalize(),
                'name': name.lower(),
                'project': self.project_name
            })
            
            list_path = self.base_path / 'internal' / 'usecase' / 'query' / f"list_{name.lower()}.go"
            self.write_file(list_path, list_content)
    
    def generate_event_handlers(self):
        """生成事件处理器"""
        
        # 为每个聚合生成事件处理器
        for aggregate in self.config['aggregates']:
            name = aggregate['name']
            
            # 生成创建事件处理器
            handler_content = self.template_loader.render_template("event_handler.go.tmpl", {
                'EventName': f"{name}Created",
                'event_name': f"{name.lower()} created",
                'Name': name.capitalize(),
                'project': self.project_name
            })
            
            handler_path = self.base_path / 'internal' / 'usecase' / 'event' / f"{name.lower()}_created_handler.go"
            self.write_file(handler_path, handler_content)
            
            # 生成更新事件处理器
            update_handler_content = self.template_loader.render_template("event_handler.go.tmpl", {
                'EventName': f"{name}Updated",
                'event_name': f"{name.lower()} updated",
                'Name': name.capitalize(),
                'project': self.project_name
            })
            
            update_handler_path = self.base_path / 'internal' / 'usecase' / 'event' / f"{name.lower()}_updated_handler.go"
            self.write_file(update_handler_path, update_handler_content)
            
            # 生成删除事件处理器
            delete_handler_content = self.template_loader.render_template("event_handler.go.tmpl", {
                'EventName': f"{name}Deleted",
                'event_name': f"{name.lower()} deleted",
                'Name': name.capitalize(),
                'project': self.project_name
            })
            
            delete_handler_path = self.base_path / 'internal' / 'usecase' / 'event' / f"{name.lower()}_deleted_handler.go"
            self.write_file(delete_handler_path, delete_handler_content)
    
    def write_file(self, path: Path, content: str):
        """写入文件"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)