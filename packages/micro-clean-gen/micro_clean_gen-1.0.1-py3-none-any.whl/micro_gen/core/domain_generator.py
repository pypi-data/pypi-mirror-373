"""
领域层生成器
负责生成聚合根、领域事件、仓储接口等核心领域对象
"""

import os
from pathlib import Path
from typing import Dict, List, Any

class DomainGenerator:
    """领域层生成器"""
    
    def __init__(self, config: Dict[str, Any], base_path: Path):
        self.config = config
        self.project_name = config['project']['name']
        self.base_path = base_path
        
        # 类型映射
        self.go_type_mapping = {
            'string': 'string',
            'int': 'int',
            'float': 'float64',
            'bool': 'bool',
            'time': 'time.Time',
            'uuid': 'string'
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
        
        # 聚合根模板
        aggregate_template = '''package aggregate

import (
    "time"
    "{project}/internal/domain/event"
)

// {Name} 聚合根
type {Name} struct {{
    ID        string    `json:"id"`
    {fields}
    Version   int       `json:"version"`
    CreatedAt time.Time `json:"created_at"`
    UpdatedAt time.Time `json:"updated_at"`
    DeletedAt *time.Time `json:"deleted_at,omitempty"`
}}

// New{Name} 创建新的{name}
func New{Name}(id string, {params}) *{Name} {{
    return &{Name}{{
        ID:        id,
        {field_assigns}
        Version:   0,
        CreatedAt: time.Now(),
        UpdatedAt: time.Now(),
    }}
}}

// ApplyEvent 应用事件
func (a *{Name}) ApplyEvent(event interface{{}}) error {{
    switch e := event.(type) {{
    case *event.{Name}Created:
        return a.apply{Name}Created(e)
    case *event.{Name}Updated:
        return a.apply{Name}Updated(e)
    case *event.{Name}Deleted:
        return a.apply{Name}Deleted(e)
    default:
        return nil
    }}
}}

// apply{Name}Created 应用创建事件
func (a *{Name}) apply{Name}Created(e *event.{Name}Created) error {{
    a.ID = e.ID
    {apply_fields}
    a.Version = 0
    a.CreatedAt = e.Timestamp
    a.UpdatedAt = e.Timestamp
    return nil
}}

// apply{Name}Updated 应用更新事件
func (a *{Name}) apply{Name}Updated(e *event.{Name}Updated) error {{
    {update_fields}
    a.Version++
    a.UpdatedAt = e.Timestamp
    return nil
}}

// apply{Name}Deleted 应用删除事件
func (a *{Name}) apply{Name}Deleted(e *event.{Name}Deleted) error {{
    // 标记为已删除，实际删除由仓储处理
    a.UpdatedAt = e.Timestamp
    return nil
}}
'''
        
        # 为每个聚合生成代码
        for aggregate in self.config['aggregates']:
            name = aggregate['name']
            
            # 生成字段定义
            fields = []
            params = []
            assigns = []
            event_fields = []
            apply_fields = []
            update_fields = []
            
            for field in aggregate['fields']:
                field_name = field['name']
                field_type = self.go_type_mapping.get(field['type'], 'string')
                json_tag = field.get('json', field['name'])
                
                fields.append(f"{field_name} {field_type} `json:\"{json_tag}\"`")
                params.append(f"{field_name} {field_type}")
                assigns.append(f"{field_name}: {field_name},")
                event_fields.append(f"{field_name}: {field_name},")
                apply_fields.append(f"a.{field_name} = e.{field_name}")
                update_fields.append(f"a.{field_name} = e.{field_name}")
            
            # 写入聚合根文件
            aggregate_content = aggregate_template.format(
                Name=name.capitalize(),
                name=name.lower(),
                fields='\n    '.join(fields),
                params=', '.join(params),
                field_assigns='\n        '.join(assigns),
                event_fields='\n        '.join(event_fields),
                apply_fields='\n    '.join(apply_fields),
                update_fields='\n    '.join(update_fields),
                project=self.project_name
            )
            
            aggregate_path = self.base_path / 'internal' / 'domain' / 'aggregate' / f"{name}.go"
            self.write_file(aggregate_path, aggregate_content)
    
    def generate_events(self):
        """生成领域事件"""
        
        # 事件定义模板
        event_template = '''package event

import "time"

// {EventName} 事件定义
type {EventName} struct {{
    ID        string    `json:"id"`
    {fields}
    Timestamp time.Time `json:"timestamp"`
}}

// EventName 返回事件名称
func (e *{EventName}) EventName() string {{
    return "{event_name}"
}}

// AggregateID 返回聚合根ID
func (e *{EventName}) AggregateID() string {{
    return e.ID
}}

// EventTime 返回事件时间
func (e *{EventName}) EventTime() time.Time {{
    return e.Timestamp
}}'''
        
        # 为每个聚合生成事件
        for aggregate in self.config['aggregates']:
            name = aggregate['name']
            
            # 生成默认事件
            events = aggregate.get('events', [])
            if not events:
                # 如果没有定义事件，创建默认的CRUD事件
                events = [
                    {'name': f'{name}Created', 'fields': aggregate['fields']},
                    {'name': f'{name}Updated', 'fields': aggregate['fields']},
                    {'name': f'{name}Deleted', 'fields': [{'name': 'ID', 'type': 'string'}]}
                ]
            
            for event in events:
                event_fields = []
                for field in event.get('fields', []):
                    field_name = field['name']
                    field_type = self.go_type_mapping.get(field['type'], 'string')
                    json_tag = field.get('json', field['name'])
                    event_fields.append(f"{field_name} {field_type} `json:\"{json_tag}\"`")
                
                event_content = event_template.format(
                    EventName=event['name'],
                    event_name=event['name'].lower(),
                    fields='\n    '.join(event_fields)
                )
                
                event_path = self.base_path / 'internal' / 'domain' / 'event' / f"{event['name'].lower()}.go"
                self.write_file(event_path, event_content)
    
    def generate_repositories(self):
        """生成仓储接口"""
        
        # 仓储接口模板
        repository_template = '''package repository

import (
    "context"
    "{project}/internal/domain/aggregate"
)

// {Name}Repository 仓储接口
type {Name}Repository interface {{
    Save(ctx context.Context, {name} *aggregate.{Name}) error
    FindByID(ctx context.Context, id string) (*aggregate.{Name}, error)
    FindAll(ctx context.Context) ([]*aggregate.{Name}, error)
    Delete(ctx context.Context, id string) error
    
    // 事件溯源相关
    LoadEvents(ctx context.Context, aggregateID string) ([]interface{{}}, error)
    SaveEvents(ctx context.Context, aggregateID string, events []interface{{}}, version int) error
    GetVersion(ctx context.Context, aggregateID string) (int, error)
}}'''
        
        # 为每个聚合生成仓储接口
        for aggregate in self.config['aggregates']:
            name = aggregate['name']
            
            repository_content = repository_template.format(
                Name=name.capitalize(),
                name=name.lower(),
                project=self.project_name
            )
            
            repository_path = self.base_path / 'internal' / 'domain' / 'repository' / f"{name}_repository.go"
            self.write_file(repository_path, repository_content)
    
    def generate_projections(self):
        """生成投影接口"""
        
        # 投影接口模板
        projection_template = '''package projection

import (
    "context"
    "time"
    "{project}/internal/domain/event"
)

// {Name}Projection 投影接口
type {Name}Projection interface {{
    Project(ctx context.Context, event interface{{}}) error
    Get(ctx context.Context, id string) (*{Name}ProjectionModel, error)
    GetAll(ctx context.Context) ([]*{Name}ProjectionModel, error)
    Delete(ctx context.Context, id string) error
}}

// {Name}ProjectionModel 投影模型
type {Name}ProjectionModel struct {{
    ID        string    `json:"id"`
    {fields}
    CreatedAt time.Time `json:"created_at"`
    UpdatedAt time.Time `json:"updated_at"`
}}'''
        
        # 为每个聚合生成投影接口
        for aggregate in self.config['aggregates']:
            name = aggregate['name']
            
            fields = []
            for field in aggregate['fields']:
                field_name = field['name']
                field_type = self.go_type_mapping.get(field['type'], 'string')
                json_tag = field.get('json', field['name'])
                fields.append(f"{field_name} {field_type} `json:\"{json_tag}\"`")
            
            projection_content = projection_template.format(
                Name=name.capitalize(),
                fields='\n    '.join(fields),
                project=self.project_name
            )
            
            projection_path = self.base_path / 'internal' / 'domain' / 'projection' / f"{name}_projection.go"
            self.write_file(projection_path, projection_content)
    
    def write_file(self, path: Path, content: str):
        """写入文件"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)