"""
适配器层生成器
负责生成HTTP处理器、gRPC服务、消息处理器等适配器代码
"""

import os
from pathlib import Path
from typing import Dict, List, Any

class AdapterGenerator:
    """适配器层生成器"""
    
    def __init__(self, config: Dict[str, Any], base_path: Path):
        self.config = config
        self.project_name = config['project']['name']
        self.base_path = base_path
    
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
        
        # HTTP处理器模板
        handler_template = '''package http

import (
    "encoding/json"
    "net/http"
    "strconv"
    
    "{project}/internal/usecase/command"
    "{project}/internal/usecase/query"
)

// {Name}Handler {name} HTTP处理器
type {Name}Handler struct {{
    createHandler *command.Create{Name}Handler
    updateHandler *command.Update{Name}Handler
    getHandler    *query.Get{Name}Handler
    listHandler   *query.List{Name}Handler
}}

// New{Name}Handler 创建处理器实例
func New{Name}Handler(
    create *command.Create{Name}Handler,
    update *command.Update{Name}Handler,
    get *query.Get{Name}Handler,
    list *query.List{Name}Handler,
) *{Name}Handler {{
    return &{Name}Handler{{
        createHandler: create,
        updateHandler: update,
        getHandler:    get,
        listHandler:   list,
    }}
}}

// Create 创建{name}
func (h *{Name}Handler) Create(w http.ResponseWriter, r *http.Request) {{
    var req Create{Name}Request
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {{
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }}
    
    cmd := command.Create{Name}Command{{
        {field_assigns}
    }}
    
    if err := h.createHandler.Handle(r.Context(), cmd); err != nil {{
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }}
    
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusCreated)
    json.NewEncoder(w).Encode(map[string]string{{
        "message": "{name} created successfully",
    }})
}}

// Update 更新{name}
func (h *{Name}Handler) Update(w http.ResponseWriter, r *http.Request) {{
    id := r.URL.Query().Get("id")
    if id == "" {{
        http.Error(w, "ID is required", http.StatusBadRequest)
        return
    }}
    
    var req Update{Name}Request
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {{
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }}
    
    cmd := command.Update{Name}Command{{
        ID: id,
        {field_assigns}
    }}
    
    if err := h.updateHandler.Handle(r.Context(), cmd); err != nil {{
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }}
    
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]string{{
        "message": "{name} updated successfully",
    }})
}}

// Get 获取{name}
func (h *{Name}Handler) Get(w http.ResponseWriter, r *http.Request) {{
    id := r.URL.Query().Get("id")
    if id == "" {{
        http.Error(w, "ID is required", http.StatusBadRequest)
        return
    }}
    
    q := query.Get{Name}Query{{ID: id}}
    result, err := h.getHandler.Handle(r.Context(), q)
    if err != nil {{
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }}
    
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(result)
}}

// List 列表{name}
func (h *{Name}Handler) List(w http.ResponseWriter, r *http.Request) {{
    limitStr := r.URL.Query().Get("limit")
    offsetStr := r.URL.Query().Get("offset")
    
    limit, _ := strconv.Atoi(limitStr)
    if limit <= 0 {{
        limit = 10
    }}
    
    offset, _ := strconv.Atoi(offsetStr)
    if offset < 0 {{
        offset = 0
    }}
    
    q := query.List{Name}Query{{
        Limit:  limit,
        Offset: offset,
    }}
    
    result, err := h.listHandler.Handle(r.Context(), q)
    if err != nil {{
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }}
    
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(result)
}}

// Create{Name}Request 创建{name}请求
type Create{Name}Request struct {{
    {request_fields}
}}

// Update{Name}Request 更新{name}请求
type Update{Name}Request struct {{
    {request_fields}
}}
'''
        
        # 为每个聚合生成HTTP处理器
        for aggregate in self.config['aggregates']:
            name = aggregate['name']
            
            # 生成字段赋值
            field_assigns = []
            request_fields = []
            
            for field in aggregate['fields']:
                field_assigns.append(f"{field['name']}: req.{field['name']},")
                request_fields.append(f"{field['name']} {field['type']} `json:\"{field['name']}\"`")
            
            handler_content = handler_template.format(
                Name=name.capitalize(),
                name=name.lower(),
                field_assigns='\n        '.join(field_assigns),
                request_fields='\n    '.join(request_fields),
                project=self.project_name
            )
            
            handler_path = self.base_path / 'internal' / 'adapter' / 'http' / f"{name}_handler.go"
            self.write_file(handler_path, handler_content)
    
    def generate_grpc_services(self):
        """生成gRPC服务"""
        
        # gRPC服务模板
        service_template = '''package grpc

import (
    "context"
    
    "google.golang.org/grpc"
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/status"
    
    "{project}/internal/usecase/command"
    "{project}/internal/usecase/query"
    pb "{project}/api/proto"
)

// {Name}Service {name} gRPC服务
type {Name}Service struct {{
    pb.Unimplemented{Name}ServiceServer
    createHandler *command.Create{Name}Handler
    updateHandler *command.Update{Name}Handler
    getHandler    *query.Get{Name}Handler
    listHandler   *query.List{Name}Handler
}}

// New{Name}Service 创建服务实例
func New{Name}Service(
    create *command.Create{Name}Handler,
    update *command.Update{Name}Handler,
    get *query.Get{Name}Handler,
    list *query.List{Name}Handler,
) *{Name}Service {{
    return &{Name}Service{{
        createHandler: create,
        updateHandler: update,
        getHandler:    get,
        listHandler:   list,
    }}
}}

// Create{Name} 创建{name}
func (s *{Name}Service) Create{Name}(ctx context.Context, req *pb.Create{Name}Request) (*pb.Create{Name}Response, error) {{
    cmd := command.Create{Name}Command{{
        {field_assigns}
    }}
    
    if err := s.createHandler.Handle(ctx, cmd); err != nil {{
        return nil, status.Errorf(codes.Internal, "failed to create {name}: %v", err)
    }}
    
    return &pb.Create{Name}Response{{
        Message: "{name} created successfully",
    }}, nil
}}

// Update{name} 更新{name}
func (s *{Name}Service) Update{name}(ctx context.Context, req *pb.Update{name}Request) (*pb.Update{name}Response, error) {{
    cmd := command.Update{name}Command{{
        ID: req.GetId(),
        {field_assigns}
    }}
    
    if err := s.updateHandler.Handle(ctx, cmd); err != nil {{
        return nil, status.Errorf(codes.Internal, "failed to update {name}: %v", err)
    }}
    
    return &pb.Update{name}Response{{
        Message: "{name} updated successfully",
    }}, nil
}}

// Get{name} 获取{name}
func (s *{Name}Service) Get{name}(ctx context.Context, req *pb.Get{name}Request) (*pb.Get{name}Response, error) {{
    q := query.Get{name}Query{{ID: req.GetId()}}
    result, err := s.getHandler.Handle(ctx, q)
    if err != nil {{
        return nil, status.Errorf(codes.Internal, "failed to get {name}: %v", err)
    }}
    
    return &pb.Get{name}Response{{
        {name}: Map{name}ToProto(result),
    }}, nil
}}

// List{name} 列表{name}
func (s *{Name}Service) List{name}(ctx context.Context, req *pb.List{name}Request) (*pb.List{name}Response, error) {{
    q := query.List{name}Query{{
        Limit:  int(req.GetLimit()),
        Offset: int(req.GetOffset()),
    }}
    
    result, err := s.listHandler.Handle(ctx, q)
    if err != nil {{
        return nil, status.Errorf(codes.Internal, "failed to list {name}: %v", err)
    }}
    
    items := make([]*pb.{name}, len(result.Items))
    for i, item := range result.Items {{
        items[i] = Map{name}ToProto(item)
    }}
    
    return &pb.List{name}Response{{
        Items: items,
        Total: int32(result.Total),
    }}, nil
}}

// Map{name}ToProto 将领域模型转换为proto模型
func Map{name}ToProto(m *model.{name}) *pb.{name} {{
    return &pb.{name}{{
        {proto_mappings}
    }}
}}
'''
        
        # 映射器模板
        mapper_template = '''package repository

import (
    "{project}/internal/domain/model"
    "{project}/internal/infrastructure/persistence/entity"
)

// {Name}Mapper {name}实体映射器
type {Name}Mapper struct {{}}

// New{Name}Mapper 创建映射器实例
func New{Name}Mapper() *{Name}Mapper {{
    return &{Name}Mapper{{}}
}}

// ToEntity 将领域模型转换为实体
func (m *{Name}Mapper) ToEntity(domain *model.{Name}) *entity.{Name}Entity {{
    if domain == nil {{
        return nil
    }}
    
    return &entity.{Name}Entity{{
        {entity_mappings}
    }}
}}

// ToDomain 将实体转换为领域模型
func (m *{Name}Mapper) ToDomain(entity *entity.{Name}Entity) *model.{Name} {{
    if entity == nil {{
        return nil
    }}
    
    return &model.{Name}{{
        {domain_mappings}
    }}
}}

// ToDomainList 将实体列表转换为领域模型列表
func (m *{Name}Mapper) ToDomainList(entities []*entity.{Name}Entity) []*model.{Name} {{
    if len(entities) == 0 {{
        return []*model.{Name}{{}}
    }}
    
    domains := make([]*model.{Name}, len(entities))
    for i, entity := range entities {{
        domains[i] = m.ToDomain(entity)
    }}
    
    return domains
}}
'''
        
        # 映射函数模板
        mapper_template = '''package grpc

import (
    pb "{project}/pkg/proto"
    "{project}/internal/domain/projection"
)

// Map{Name}ToProto 映射{name}投影到proto
func Map{Name}ToProto(model *projection.{Name}ProjectionModel) *pb.{Name} {{
    if model == nil {{
        return nil
    }}
    
    return &pb.{Name}{{
        {field_mappings}
    }}
}}

// Map{Name}FromProto 映射proto到{name}投影
func Map{Name}FromProto(proto *pb.{Name}) *projection.{Name}ProjectionModel {{
    if proto == nil {{
        return nil
    }}
    
    return &projection.{Name}ProjectionModel{{
        {field_mappings}
    }}
}}'''
        
        # 为每个聚合生成gRPC服务
        for aggregate in self.config['aggregates']:
            name = aggregate['name']
            
            # 生成字段赋值
            field_assigns = []
            field_mappings = []
            
            for field in aggregate['fields']:
                field_assigns.append(f"{field['name']}: req.{field['name']},")
                field_mappings.append(f"{field['name']}: model.{field['name']},")
            
            service_content = service_template.format(
                Name=name.capitalize(),
                name=name.lower(),
                field_assigns='\n        '.join(field_assigns),
                project=self.project_name,
                proto_mappings=''  # 添加空的proto_mappings
            )
            
            service_path = self.base_path / 'internal' / 'adapter' / 'grpc' / f"{name}_service.go"
            self.write_file(service_path, service_content)
            
            # 生成映射函数
            mapper_content = mapper_template.format(
                Name=name.capitalize(),
                name=name.lower(),
                field_mappings='\n        '.join(field_mappings),
                project=self.project_name
            )
            
            mapper_path = self.base_path / 'internal' / 'adapter' / 'grpc' / f"{name}_mapper.go"
            self.write_file(mapper_path, mapper_content)
    
    def generate_message_handlers(self):
        """生成消息处理器"""
        
        # 消息处理器模板
        handler_template = '''package message

import (
    "context"
    "encoding/json"
    "fmt"
    
    "{project}/internal/usecase/event"
    "{project}/internal/domain/event"
)

// EventHandler 事件消息处理器
type EventHandler struct {{
    {name}CreatedHandler *event.{Name}CreatedHandler
    {name}UpdatedHandler *event.{Name}UpdatedHandler
    {name}DeletedHandler *event.{Name}DeletedHandler
}}

// NewEventHandler 创建处理器实例
func NewEventHandler(
    created *event.{Name}CreatedHandler,
    updated *event.{Name}UpdatedHandler,
    deleted *event.{Name}DeletedHandler,
) *EventHandler {{
    return &EventHandler{{
        {name}CreatedHandler: created,
        {name}UpdatedHandler: updated,
        {name}DeletedHandler: deleted,
    }}
}}

// HandleMessage 处理消息
func (h *EventHandler) HandleMessage(ctx context.Context, topic string, message []byte) error {{
    switch topic {{
    case "{name}.created":
        return h.handle{Name}Created(ctx, message)
    case "{name}.updated":
        return h.handle{Name}Updated(ctx, message)
    case "{name}.deleted":
        return h.handle{Name}Deleted(ctx, message)
    default:
        return fmt.Errorf("unknown topic: %s", topic)
    }}
}}

func (h *EventHandler) handle{Name}Created(ctx context.Context, message []byte) error {{
    var evt event.{Name}Created
    if err := json.Unmarshal(message, &evt); err != nil {{
        return fmt.Errorf("failed to unmarshal event: %w", err)
    }}
    
    return h.{name}CreatedHandler.Handle(ctx, &evt)
}}

func (h *EventHandler) handle{Name}Updated(ctx context.Context, message []byte) error {{
    var evt event.{Name}Updated
    if err := json.Unmarshal(message, &evt); err != nil {{
        return fmt.Errorf("failed to unmarshal event: %w", err)
    }}
    
    return h.{name}UpdatedHandler.Handle(ctx, &evt)
}}

func (h *EventHandler) handle{Name}Deleted(ctx context.Context, message []byte) error {{
    var evt event.{Name}Deleted
    if err := json.Unmarshal(message, &evt); err != nil {{
        return fmt.Errorf("failed to unmarshal event: %w", err)
    }}
    
    return h.{name}DeletedHandler.Handle(ctx, &evt)
}}
'''
        
        # 为每个聚合生成消息处理器
        for aggregate in self.config['aggregates']:
            name = aggregate['name']
            
            handler_content = handler_template.format(
                Name=name.capitalize(),
                name=name.lower(),
                project=self.project_name
            )
            
            handler_path = self.base_path / 'internal' / 'adapter' / 'message' / f"{name}_handler.go"
            self.write_file(handler_path, handler_content)
    
    def write_file(self, path: Path, content: str):
        """写入文件"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)