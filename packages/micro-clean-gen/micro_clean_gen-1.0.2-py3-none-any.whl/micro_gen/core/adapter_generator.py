"""
适配器层生成器
负责生成HTTP处理器、gRPC服务、消息处理器等适配器代码
"""

import os
from pathlib import Path
from typing import Dict, List, Any
from .templates.template_loader import TemplateLoader

class AdapterGenerator:
    """适配器层生成器"""
    
    def __init__(self, config: Dict[str, Any], base_path: Path):
        self.config = config
        self.project_name = config['project']['name']
        self.base_path = base_path
        self.template_loader = TemplateLoader(Path(__file__).parent / "templates" / "adapter")
    
    def generate(self):
        """生成适配器层代码"""
        print("🏗️  生成适配器层代码...")
        
        # 生成HTTP处理器
        self.generate_http_handlers()
        
        # 生成gRPC服务
        self.generate_grpc_services()
        
        # 生成消息处理器
        self.generate_message_handlers()
    
    def generate_http_handlers(self):
        """生成HTTP处理器"""

        # 为每个聚合生成HTTP处理器
        for aggregate in self.config['aggregates']:
            name = aggregate['name']

            # 生成字段赋值
            field_assigns = []
            request_fields = []

            for field in aggregate['fields']:
                field_assigns.append(f"{field['name']}: req.{field['name']},")
                request_fields.append(f"{field['name']} {field['type']} `json:\"{field['name']}\"`")

            handler_content = self.template_loader.render_template("http_handler.go.tmpl", {
                'Name': name.capitalize(),
                'name': name.lower(),
                'field_assigns': '\n        '.join(field_assigns),
                'request_fields': '\n    '.join(request_fields),
                'project': self.project_name
            })

            handler_path = self.base_path / 'internal' / 'adapter' / 'http' / f"{name.lower()}_handler.go"
            self.write_file(handler_path, handler_content)
    
    def generate_grpc_services(self):
        """生成gRPC服务"""
        
        # 为每个聚合生成gRPC服务
        for aggregate in self.config['aggregates']:
            name = aggregate['name']
            
            # 生成字段赋值
            field_assigns = []
            field_mappings = []
            
            for field in aggregate['fields']:
                field_assigns.append(f"{field['name']}: req.{field['name']},")
                field_mappings.append(f"{field['name']}: model.{field['name']},")
            
            service_content = self.template_loader.render_template("grpc_service.go.tmpl", {
                'Name': name.capitalize(),
                'name': name.lower(),
                'field_assigns': '\n        '.join(field_assigns),
                'project': self.project_name,
                'proto_mappings': '\n        '.join(field_mappings)
            })
            
            service_path = self.base_path / 'internal' / 'adapter' / 'grpc' / f"{name.lower()}_service.go"
            self.write_file(service_path, service_content)
            
            # 生成映射函数
            mapper_content = self.template_loader.render_template("grpc_mapper.go.tmpl", {
                'Name': name.capitalize(),
                'name': name.lower(),
                'field_mappings': '\n        '.join(field_mappings),
                'project': self.project_name
            })
            
            mapper_path = self.base_path / 'internal' / 'adapter' / 'grpc' / f"{name.lower()}_mapper.go"
            self.write_file(mapper_path, mapper_content)
    
    def generate_message_handlers(self):
        """生成消息处理器"""
        
        # 为每个聚合生成消息处理器
        for aggregate in self.config['aggregates']:
            name = aggregate['name']
            
            handler_content = self.template_loader.render_template("message_handler.go.tmpl", {
                'Name': name.capitalize(),
                'name': name.lower(),
                'project': self.project_name
            })
            
            handler_path = self.base_path / 'internal' / 'adapter' / 'message' / f"{name.lower()}_handler.go"
            self.write_file(handler_path, handler_content)
    
    def write_file(self, path: Path, content: str):
        """写入文件"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)