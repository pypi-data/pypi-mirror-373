"""
用例层生成器
负责生成命令用例、查询用例、事件处理器等业务用例
"""

import os
from pathlib import Path
from typing import Dict, List, Any

class UseCaseGenerator:
    """用例层生成器"""
    
    def __init__(self, config: Dict[str, Any], base_path: Path):
        self.config = config
        self.project_name = config['project']['name']
        self.base_path = base_path
    
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
        
        # 创建用例模板
        command_template = '''package command

import (
    "context"
    "fmt"
    "time"
    
    "{project}/internal/domain/aggregate"
    "{project}/internal/domain/repository"
    "{project}/internal/domain/event"
    "{project}/internal/infrastructure/eventstore"
)

// Create{Name}Command 创建{name}命令
type Create{Name}Command struct {{
    {fields}
}}

// Create{Name}Handler 创建{name}处理器
type Create{Name}Handler struct {{
    repository repository.{Name}Repository
    eventStore eventstore.EventStore
}}

// NewCreate{Name}Handler 创建处理器实例
func NewCreate{Name}Handler(repo repository.{Name}Repository, store eventstore.EventStore) *Create{Name}Handler {{
    return &Create{Name}Handler{{
        repository: repo,
        eventStore: store,
    }}
}}

// Handle 处理创建{name}命令
func (h *Create{Name}Handler) Handle(ctx context.Context, cmd Create{Name}Command) error {{
    // 业务验证
    if err := h.validate(cmd); err != nil {{
        return fmt.Errorf("validation failed: %w", err)
    }}
    
    // 创建聚合根
    {name} := aggregate.New{Name}(
        {param_assigns}
    )
    
    // 保存聚合状态
    if err := h.repository.Save(ctx, {name}); err != nil {{
        return fmt.Errorf("failed to save {name}: %w", err)
    }}
    
    // 发布领域事件
    events := {name}.GetEvents()
    for _, event := range events {{
        if err := h.eventStore.Publish(ctx, event); err != nil {{
            return fmt.Errorf("failed to publish event: %w", err)
        }}
    }}
    
    // 清除已发布事件
    {name}.ClearEvents()
    
    return nil
}}

// validate 验证命令参数
func (h *Create{Name}Handler) validate(cmd Create{Name}Command) error {{
    // TODO: 实现业务验证逻辑
    return nil
}}
'''
        
        # 更新用例模板
        update_template = '''package command

import (
    "context"
    "fmt"
    
    "{project}/internal/domain/aggregate"
    "{project}/internal/domain/repository"
    "{project}/internal/domain/event"
    "{project}/internal/infrastructure/eventstore"
)

// Update{Name}Command 更新{name}命令
type Update{Name}Command struct {{
    ID string
    {fields}
}}

// Update{Name}Handler 更新{name}处理器
type Update{Name}Handler struct {{
    repository repository.{Name}Repository
    eventStore eventstore.EventStore
}}

// NewUpdate{Name}Handler 创建处理器实例
func NewUpdate{Name}Handler(repo repository.{Name}Repository, store eventstore.EventStore) *Update{Name}Handler {{
    return &Update{Name}Handler{{
        repository: repo,
        eventStore: store,
    }}
}}

// Handle 处理更新{name}命令
func (h *Update{Name}Handler) Handle(ctx context.Context, cmd Update{Name}Command) error {{
    // 查找聚合根
    {name}, err := h.repository.FindByID(ctx, cmd.ID)
    if err != nil {{
        return fmt.Errorf("failed to find {name}: %w", err)
    }}
    
    if {name} == nil {{
        return fmt.Errorf("{name} not found")
    }}
    
    // 业务验证
    if err := h.validate(cmd); err != nil {{
        return fmt.Errorf("validation failed: %w", err)
    }}
    
    // 更新聚合根
    {update_logic}
    
    // 发布更新事件
    {name}.AddEvent(&event.{Name}Updated{{
        ID: cmd.ID,
        {event_fields}
        Timestamp: time.Now(),
    }})
    
    // 保存聚合状态
    if err := h.repository.Save(ctx, {name}); err != nil {{
        return fmt.Errorf("failed to save {name}: %w", err)
    }}
    
    // 发布领域事件
    events := {name}.GetEvents()
    for _, event := range events {{
        if err := h.eventStore.Publish(ctx, event); err != nil {{
            return fmt.Errorf("failed to publish event: %w", err)
        }}
    }}
    
    // 清除已发布事件
    {name}.ClearEvents()
    
    return nil
}}

// validate 验证命令参数
func (h *Update{Name}Handler) validate(cmd Update{Name}Command) error {{
    // TODO: 实现业务验证逻辑
    return nil
}}
'''
        
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
            
            command_content = command_template.format(
                Name=name.capitalize(),
                name=name.lower(),
                fields='\n    '.join(fields),
                param_assigns=',\n        '.join(param_assigns),
                project=self.project_name
            )
            
            command_path = self.base_path / 'internal' / 'usecase' / 'command' / f"create_{name}.go"
            self.write_file(command_path, command_content)
            
            # 生成更新命令
            update_fields = []
            update_logic = []
            event_fields = []
            
            for field in aggregate['fields']:
                update_fields.append(f"{field['name']} {field['type']}")
                update_logic.append(f"{name}.{field['name']} = cmd.{field['name']}")
                event_fields.append(f"{field['name']}: cmd.{field['name']},")
            
            update_content = update_template.format(
                Name=name.capitalize(),
                name=name.lower(),
                fields='\n    '.join(update_fields),
                update_logic='\n    '.join(update_logic),
                event_fields='\n        '.join(event_fields),
                project=self.project_name
            )
            
            update_path = self.base_path / 'internal' / 'usecase' / 'command' / f"update_{name}.go"
            self.write_file(update_path, update_content)
    
    def generate_queries(self):
        """生成查询用例"""
        
        # 查询用例模板
        query_template = '''package query

import (
    "context"
    "fmt"
    
    "{project}/internal/domain/projection"
)

// Get{Name}Query 获取{name}查询
type Get{Name}Query struct {{
    ID string
}}

// Get{Name}Handler 获取{name}处理器
type Get{Name}Handler struct {{
    projection projection.{Name}Projection
}}

// NewGet{Name}Handler 创建处理器实例
func NewGet{Name}Handler(proj projection.{Name}Projection) *Get{Name}Handler {{
    return &Get{Name}Handler{{
        projection: proj,
    }}
}}

// Handle 处理获取{name}查询
func (h *Get{Name}Handler) Handle(ctx context.Context, query Get{Name}Query) (*{Name}Response, error) {{
    // 从投影查询数据
    result, err := h.projection.Get(ctx, query.ID)
    if err != nil {{
        return nil, fmt.Errorf("failed to get {name}: %w", err)
    }}
    
    if result == nil {{
        return nil, fmt.Errorf("{name} not found")
    }}
    
    return &{Name}Response{{
        Data: result,
    }}, nil
}}

// {Name}Response 查询响应
type {Name}Response struct {{
    Data *{Name}ProjectionModel `json:"data"`
}}
'''
        
        # 列表查询用例模板
        list_template = '''package query

import (
    "context"
    "fmt"
    
    "{project}/internal/domain/projection"
)

// List{Name}Query 列表{name}查询
type List{Name}Query struct {{
    Limit  int
    Offset int
}}

// List{Name}Handler 列表{name}处理器
type List{Name}Handler struct {{
    projection projection.{Name}Projection
}}

// NewList{Name}Handler 创建处理器实例
func NewList{Name}Handler(proj projection.{Name}Projection) *List{Name}Handler {{
    return &List{Name}Handler{{
        projection: proj,
    }}
}}

// Handle 处理列表{name}查询
func (h *List{Name}Handler) Handle(ctx context.Context, query List{Name}Query) (*List{Name}Response, error) {{
    // 从投影查询数据
    results, err := h.projection.GetAll(ctx)
    if err != nil {{
        return nil, fmt.Errorf("failed to list {name}: %w", err)
    }}
    
    // 应用分页
    start := query.Offset
    if start >= len(results) {{
        return &List{Name}Response{{Data: []*{Name}ProjectionModel{{}}}}, nil
    }}
    
    end := start + query.Limit
    if end > len(results) {{
        end = len(results)
    }}
    
    return &List{Name}Response{{
        Data: results[start:end],
    }}, nil
}}

// List{Name}Response 列表查询响应
type List{Name}Response struct {{
    Data []*{Name}ProjectionModel `json:"data"`
}}
'''
        
        # 为每个聚合生成查询用例
        for aggregate in self.config['aggregates']:
            name = aggregate['name']
            
            # 生成获取查询
            query_content = query_template.format(
                Name=name.capitalize(),
                name=name.lower(),
                project=self.project_name
            )
            
            query_path = self.base_path / 'internal' / 'usecase' / 'query' / f"get_{name}.go"
            self.write_file(query_path, query_content)
            
            # 生成列表查询
            list_content = list_template.format(
                Name=name.capitalize(),
                name=name.lower(),
                project=self.project_name
            )
            
            list_path = self.base_path / 'internal' / 'usecase' / 'query' / f"list_{name}.go"
            self.write_file(list_path, list_content)
    
    def generate_event_handlers(self):
        """生成事件处理器"""
        
        # 事件处理器模板
        handler_template = '''package event

import (
    "context"
    "fmt"
    
    "{project}/internal/domain/event"
    "{project}/internal/domain/projection"
)

// {EventName}Handler {event_name}事件处理器
type {EventName}Handler struct {{
    projection projection.{Name}Projection
}}

// New{EventName}Handler 创建处理器实例
func New{EventName}Handler(proj projection.{Name}Projection) *{EventName}Handler {{
    return &{EventName}Handler{{
        projection: proj,
    }}
}}

// Handle 处理{event_name}事件
func (h *{EventName}Handler) Handle(ctx context.Context, event *event.{EventName}) error {{
    // 更新投影
    if err := h.projection.Project(ctx, event); err != nil {{
        return fmt.Errorf("failed to project event: %w", err)
    }}
    
    return nil
}}
'''
        
        # 为每个聚合生成事件处理器
        for aggregate in self.config['aggregates']:
            name = aggregate['name']
            
            # 生成创建事件处理器
            handler_content = handler_template.format(
                EventName=f"{name}Created",
                event_name=f"{name.lower()} created",
                Name=name.capitalize(),
                project=self.project_name
            )
            
            handler_path = self.base_path / 'internal' / 'usecase' / 'event' / f"{name}_created_handler.go"
            self.write_file(handler_path, handler_content)
            
            # 生成更新事件处理器
            update_handler_content = handler_template.format(
                EventName=f"{name}Updated",
                event_name=f"{name.lower()} updated",
                Name=name.capitalize(),
                project=self.project_name
            )
            
            update_handler_path = self.base_path / 'internal' / 'usecase' / 'event' / f"{name}_updated_handler.go"
            self.write_file(update_handler_path, update_handler_content)
            
            # 生成删除事件处理器
            delete_handler_content = handler_template.format(
                EventName=f"{name}Deleted",
                event_name=f"{name.lower()} deleted",
                Name=name.capitalize(),
                project=self.project_name
            )
            
            delete_handler_path = self.base_path / 'internal' / 'usecase' / 'event' / f"{name}_deleted_handler.go"
            self.write_file(delete_handler_path, delete_handler_content)
    
    def write_file(self, path: Path, content: str):
        """写入文件"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)