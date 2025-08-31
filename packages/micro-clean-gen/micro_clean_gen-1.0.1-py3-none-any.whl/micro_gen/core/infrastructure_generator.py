"""
基础设施层生成器
负责生成事件存储、投影存储、依赖注入容器、引导程序等基础设施代码
"""

import os
from pathlib import Path
from typing import Dict, List, Any

class InfrastructureGenerator:
    """基础设施层生成器"""
    
    def __init__(self, config: Dict[str, Any], base_path: Path):
        self.config = config
        self.project_name = config['project']['name']
        self.base_path = base_path
    
    def generate(self):
        """生成基础设施层代码"""
        print("🏗️  生成基础设施层代码...")
        
        # 生成事件存储
        self.generate_event_store()
        
        # 生成投影存储
        self.generate_projection_store()
        
        # 生成依赖注入容器
        self.generate_container()
        
        # 生成引导程序
        self.generate_bootstrap()
    
    def generate_event_store(self):
        """生成事件存储"""
        
        # Nats事件存储模板
        event_store_template = '''package eventstore

import (
    "context"
    "encoding/json"
    "fmt"
    "log"
    "time"

    "github.com/nats-io/nats.go"
    "{project}/internal/domain/event"
)

// NatsEventStore NATS事件存储
type NatsEventStore struct {{
    conn   *nats.Conn
    js     nats.JetStreamContext
    stream string
}}

// NewNatsEventStore 创建NATS事件存储
func NewNatsEventStore(url string, stream string) (*NatsEventStore, error) {{
    // 连接到NATS
    conn, err := nats.Connect(url)
    if err != nil {{
        return nil, fmt.Errorf("failed to connect to NATS: %w", err)
    }}
    
    // 获取JetStream上下文
    js, err := conn.JetStream()
    if err != nil {{
        return nil, fmt.Errorf("failed to get JetStream: %w", err)
    }}
    
    // 创建流
    streamConfig := &nats.StreamConfig{{
        Name:      stream,
        Subjects:  []string{{"events.*"}},
        Storage:   nats.FileStorage,
        Retention: nats.LimitsPolicy,
        MaxAge:    24 * 365 * time.Hour, // 1年
    }}
    
    _, err = js.AddStream(streamConfig)
    if err != nil && err != nats.ErrStreamNameAlreadyInUse {{
        return nil, fmt.Errorf("failed to create stream: %w", err)
    }}
    
    return &NatsEventStore{{
        conn:   conn,
        js:     js,
        stream: stream,
    }}, nil
}}

// Publish 发布事件
func (s *NatsEventStore) Publish(ctx context.Context, event event.Event) error {{
    data, err := json.Marshal(event)
    if err != nil {{
        return fmt.Errorf("failed to marshal event: %w", err)
    }}
    
    subject := fmt.Sprintf("events.%s", event.GetType())
    
    _, err = s.js.Publish(subject, data)
    if err != nil {{
        return fmt.Errorf("failed to publish event: %w", err)
    }}
    
    log.Printf("Published event: %s", event.GetType())
    return nil
}}

// Subscribe 订阅事件
func (s *NatsEventStore) Subscribe(ctx context.Context, eventType string, handler func(event.Event) error) error {{
    subject := fmt.Sprintf("events.%s", eventType)
    
    _, err := s.js.Subscribe(subject, func(msg *nats.Msg) {{
        var eventData map[string]interface{{}}
        if err := json.Unmarshal(msg.Data, &eventData); err != nil {{
            log.Printf("Failed to unmarshal event: %v", err)
            return
        }}
        
        // 创建具体的事件实例
        var event event.Event
        switch eventType {{
        case "{name}.created":
            event = &event.{Name}Created{{}}
        case "{name}.updated":
            event = &event.{Name}Updated{{}}
        case "{name}.deleted":
            event = &event.{Name}Deleted{{}}
        default:
            log.Printf("Unknown event type: %s", eventType)
            return
        }}
        
        if err := json.Unmarshal(msg.Data, event); err != nil {{
            log.Printf("Failed to unmarshal event: %v", err)
            return
        }}
        
        if err := handler(event); err != nil {{
            log.Printf("Failed to handle event: %v", err)
            return
        }}
        
        msg.Ack()
    }}, nats.Durable(eventType))
    
    if err != nil {{
        return fmt.Errorf("failed to subscribe to events: %w", err)
    }}
    
    return nil
}}

// Close 关闭连接
func (s *NatsEventStore) Close() error {{
    if s.conn != nil {{
        s.conn.Close()
    }}
    return nil
}}'''
        
        # 快照存储模板
        snapshot_template = '''package eventstore

import (
    "context"
    "encoding/json"
    "fmt"
    "time"

    "github.com/nats-io/nats.go"
    "{project}/internal/domain/aggregate"
)

// SnapshotStore 快照存储
type SnapshotStore struct {{
    conn   *nats.Conn
    js     nats.JetStreamContext
    stream string
}}

// NewSnapshotStore 创建快照存储
func NewSnapshotStore(url string, stream string) (*SnapshotStore, error) {{
    conn, err := nats.Connect(url)
    if err != nil {{
        return nil, fmt.Errorf("failed to connect to NATS: %w", err)
    }}
    
    js, err := conn.JetStream()
    if err != nil {{
        return nil, fmt.Errorf("failed to get JetStream: %w", err)
    }}
    
    streamConfig := &nats.StreamConfig{{
        Name:      stream,
        Subjects:  []string{{"snapshots.*"}},
        Storage:   nats.FileStorage,
        Retention: nats.LimitsPolicy,
        MaxAge:    7 * 24 * time.Hour, // 7天
    }}
    
    _, err = js.AddStream(streamConfig)
    if err != nil && err != nats.ErrStreamNameAlreadyInUse {{
        return nil, fmt.Errorf("failed to create stream: %w", err)
    }}
    
    return &SnapshotStore{{
        conn:   conn,
        js:     js,
        stream: stream,
    }}, nil
}}

// SaveSnapshot 保存快照
func (s *SnapshotStore) SaveSnapshot(ctx context.Context, aggregateID string, aggregate *aggregate.{Name}, version int) error {{
    snapshot := Snapshot{{
        AggregateID: aggregateID,
        Version:     version,
        Data:        aggregate,
        Timestamp:   time.Now(),
    }}
    
    data, err := json.Marshal(snapshot)
    if err != nil {{
        return fmt.Errorf("failed to marshal snapshot: %w", err)
    }}
    
    subject := fmt.Sprintf("snapshots.%s", aggregateID)
    
    _, err = s.js.Publish(subject, data)
    if err != nil {{
        return fmt.Errorf("failed to publish snapshot: %w", err)
    }}
    
    return nil
}}

// LoadSnapshot 加载快照
func (s *SnapshotStore) LoadSnapshot(ctx context.Context, aggregateID string) (*aggregate.{Name}, int, error) {{
    subject := fmt.Sprintf("snapshots.%s", aggregateID)
    
    sub, err := s.js.SubscribeSync(subject)
    if err != nil {{
        return nil, 0, fmt.Errorf("failed to subscribe to snapshots: %w", err)
    }}
    defer sub.Unsubscribe()
    
    msg, err := sub.NextMsg(1 * time.Second)
    if err != nil {{
        if err == nats.ErrTimeout {{
            return nil, 0, nil // 没有快照
        }}
        return nil, 0, fmt.Errorf("failed to get snapshot: %w", err)
    }}
    
    var snapshot Snapshot
    if err := json.Unmarshal(msg.Data, &snapshot); err != nil {{
        return nil, 0, fmt.Errorf("failed to unmarshal snapshot: %w", err)
    }}
    
    return snapshot.Data, snapshot.Version, nil
}}

// Snapshot 快照数据结构
type Snapshot struct {{
    AggregateID string      `json:"aggregate_id"`
    Version     int         `json:"version"`
    Data        interface{{}} `json:"data"`
    Timestamp   time.Time   `json:"timestamp"`
}}'''
        
        # 为每个聚合生成事件存储
        for aggregate in self.config['aggregates']:
            name = aggregate['name']
            
            # 生成NATS事件存储
            event_store_content = event_store_template.format(
                Name=name.capitalize(),
                name=name.lower(),
                project=self.project_name
            )
            
            event_store_path = self.base_path / 'internal' / 'infrastructure' / 'eventstore' / 'nats_event_store.go'
            self.write_file(event_store_path, event_store_content)
            
            # 生成快照存储
            snapshot_content = snapshot_template.format(
                Name=name.capitalize(),
                name=name.lower(),
                project=self.project_name
            )
            
            snapshot_path = self.base_path / 'internal' / 'infrastructure' / 'eventstore' / 'snapshot_store.go'
            self.write_file(snapshot_path, snapshot_content)
            
            break  # 只需要生成一次
    
    def generate_projection_store(self):
        """生成投影存储"""
        
        # 内存投影存储模板
        memory_projection_template = '''package projection

import (
    "context"
    "fmt"
    "sync"
    "time"
    
    "{project}/internal/domain/projection"
    "{project}/internal/domain/event"
)

// Memory{Name}Projection 内存{name}投影
type Memory{Name}Projection struct {{
    mu    sync.RWMutex
    data  map[string]*projection.{Name}ProjectionModel
    index map[string]int
    items []*projection.{Name}ProjectionModel
}}

// NewMemory{Name}Projection 创建内存投影实例
func NewMemory{Name}Projection() *Memory{Name}Projection {{
    return &Memory{Name}Projection{{
        data:  make(map[string]*projection.{Name}ProjectionModel),
        index: make(map[string]int),
        items: make([]*projection.{Name}ProjectionModel, 0),
    }}
}}

// Get 获取{name}
func (p *Memory{Name}Projection) Get(ctx context.Context, id string) (*projection.{Name}ProjectionModel, error) {{
    p.mu.RLock()
    defer p.mu.RUnlock()
    
    item, exists := p.data[id]
    if !exists {{
        return nil, fmt.Errorf("{name} not found")
    }}
    
    return item, nil
}}

// GetAll 获取所有{name}
func (p *Memory{Name}Projection) GetAll(ctx context.Context) ([]*projection.{Name}ProjectionModel, error) {{
    p.mu.RLock()
    defer p.mu.RUnlock()
    
    return p.items, nil
}}

// Project 处理事件投影
func (p *Memory{Name}Projection) Project(ctx context.Context, event event.Event) error {{
    p.mu.Lock()
    defer p.mu.Unlock()
    
    switch e := event.(type) {{
    case *event.{Name}Created:
        return p.handle{Name}Created(e)
    case *event.{Name}Updated:
        return p.handle{Name}Updated(e)
    case *event.{Name}Deleted:
        return p.handle{Name}Deleted(e)
    default:
        return fmt.Errorf("unknown event type: %T", event)
    }}
}}

func (p *Memory{Name}Projection) handle{Name}Created(e *event.{Name}Created) error {{
    model := &projection.{Name}ProjectionModel{{
        ID:        e.ID,
        {field_assigns}
        CreatedAt: e.Timestamp,
        UpdatedAt: e.Timestamp,
    }}
    
    p.data[e.ID] = model
    p.index[e.ID] = len(p.items)
    p.items = append(p.items, model)
    
    return nil
}}

func (p *Memory{Name}Projection) handle{Name}Updated(e *event.{Name}Updated) error {{
    model, exists := p.data[e.ID]
    if !exists {{
        return fmt.Errorf("{name} not found")
    }}
    
    {field_updates}
    model.UpdatedAt = e.Timestamp
    
    return nil
}}

func (p *Memory{Name}Projection) handle{Name}Deleted(e *event.{Name}Deleted) error {{
    model, exists := p.data[e.ID]
    if !exists {{
        return nil
    }}
    
    delete(p.data, e.ID)
    
    index, exists := p.index[e.ID]
    if exists {{
        p.items = append(p.items[:index], p.items[index+1:]...)
        delete(p.index, e.ID)
    }}
    
    return nil
}}'''
        
        # 为每个聚合生成投影存储
        for aggregate in self.config['aggregates']:
            name = aggregate['name']
            
            # 生成字段赋值和更新
            field_assigns = []
            field_updates = []
            
            for field in aggregate['fields']:
                field_assigns.append(f"{field['name']}: e.{field['name']},")
                field_updates.append(f"model.{field['name']} = e.{field['name']}")
            
            projection_content = memory_projection_template.format(
                Name=name.capitalize(),
                name=name.lower(),
                field_assigns='\n        '.join(field_assigns),
                field_updates='\n    '.join(field_updates),
                project=self.project_name
            )
            
            projection_path = self.base_path / 'internal' / 'infrastructure' / 'projection' / f"memory_{name}_projection.go"
            self.write_file(projection_path, projection_content)
    
    def generate_container(self):
        """生成依赖注入容器"""
        
        # 容器模板
        container_template = '''package container

import (
    "{project}/internal/adapter/grpc"
    "{project}/internal/adapter/http"
    "{project}/internal/adapter/message"
    "{project}/internal/domain/repository"
    "{project}/internal/domain/projection"
    "{project}/internal/infrastructure/eventstore"
    "{project}/internal/infrastructure/projection"
    "{project}/internal/usecase/command"
    "{project}/internal/usecase/event"
    "{project}/internal/usecase/query"
)

// Container 依赖注入容器
type Container struct {{
    // 基础设施
    EventStore   *eventstore.NatsEventStore
    SnapshotStore *eventstore.SnapshotStore
    
    // 投影
    {projections}
    
    // 仓储
    {repositories}
    
    // 用例
    {commands}
    {queries}
    {handlers}
    
    // 适配器
    {http_handlers}
    {grpc_services}
    {message_handlers}
}}

// NewContainer 创建容器实例
func NewContainer(config *Config) (*Container, error) {{
    // 创建基础设施
    eventStore, err := eventstore.NewNatsEventStore(config.NATS.URL, config.NATS.Stream)
    if err != nil {{
        return nil, err
    }}
    
    snapshotStore, err := eventstore.NewSnapshotStore(config.NATS.URL, config.NATS.SnapshotStream)
    if err != nil {{
        return nil, err
    }}
    
    // 创建投影
    {projection_instances}
    
    // 创建仓储
    {repository_instances}
    
    // 创建用例
    {command_instances}
    
    // 创建查询
    {query_instances}
    
    // 创建事件处理器
    {handler_instances}
    
    return &Container{{
        EventStore:    eventStore,
        SnapshotStore: snapshotStore,
        {projection_fields}
        {repository_fields}
        {command_fields}
        {query_fields}
        {handler_fields}
        {http_fields}
        {grpc_fields}
        {message_fields}
    }}, nil
}}'''
        
        # 配置模板
        config_template = '''package config

import (
    "os"
    "strconv"
    "time"
)

// Config 应用配置
type Config struct {{
    Server ServerConfig
    NATS   NATSConfig
    Log    LogConfig
}}

// ServerConfig 服务器配置
type ServerConfig struct {{
    Host         string
    Port         int
    ReadTimeout  time.Duration
    WriteTimeout time.Duration
    IdleTimeout  time.Duration
}}

// NATSConfig NATS配置
type NATSConfig struct {{
    URL            string
    Stream         string
    SnapshotStream string
}}

// LogConfig 日志配置
type LogConfig struct {{
    Level  string
    Format string
}}

// LoadConfig 加载配置
func LoadConfig() *Config {{
    return &Config{{
        Server: ServerConfig{{
            Host:         getEnv("SERVER_HOST", "0.0.0.0"),
            Port:         getEnvInt("SERVER_PORT", 8080),
            ReadTimeout:  getEnvDuration("SERVER_READ_TIMEOUT", 30*time.Second),
            WriteTimeout: getEnvDuration("SERVER_WRITE_TIMEOUT", 30*time.Second),
            IdleTimeout:  getEnvDuration("SERVER_IDLE_TIMEOUT", 120*time.Second),
        }},
        NATS: NATSConfig{{
            URL:            getEnv("NATS_URL", "nats://localhost:4222"),
            Stream:         getEnv("NATS_STREAM", "{project}"),
            SnapshotStream: getEnv("NATS_SNAPSHOT_STREAM", "{project}-snapshots"),
        }},
        Log: LogConfig{{
            Level:  getEnv("LOG_LEVEL", "info"),
            Format: getEnv("LOG_FORMAT", "json"),
        }},
    }}
}}

func getEnv(key, defaultValue string) string {{
    if value := os.Getenv(key); value != "" {{
        return value
    }}
    return defaultValue
}}

func getEnvInt(key string, defaultValue int) int {{
    if value := os.Getenv(key); value != "" {{
        if intValue, err := strconv.Atoi(value); err == nil {{
            return intValue
        }}
    }}
    return defaultValue
}}

func getEnvDuration(key string, defaultValue time.Duration) time.Duration {{
    if value := os.Getenv(key); value != "" {{
        if duration, err := time.ParseDuration(value); err == nil {{
            return duration
        }}
    }}
    return defaultValue
}}'''

    def generate_bootstrap(self):
        """生成引导程序"""
        
        # 引导程序模板
        bootstrap_template = '''package main

import (
    "context"
    "log"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "{project}/internal/adapter/container"
    "{project}/internal/adapter/http"
)

func main() {{
    // 加载配置
    config := container.LoadConfig()
    
    // 创建容器
    c, err := container.NewContainer(config)
    if err != nil {{
        log.Fatal("Failed to create container:", err)
    }}
    
    // 创建HTTP服务器
    srv := &http.Server{{
        Addr:         config.Server.Host + ":" + string(rune(config.Server.Port)),
        Handler:      http.NewRouter(c),
        ReadTimeout:  config.Server.ReadTimeout,
        WriteTimeout: config.Server.WriteTimeout,
        IdleTimeout:  config.Server.IdleTimeout,
    }}
    
    // 启动服务器
    go func() {{
        log.Printf("Starting server on %s", srv.Addr)
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {{
            log.Fatal("Server failed to start:", err)
        }}
    }}()
    
    // 等待中断信号
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit
    
    log.Println("Shutting down server...")
    
    // 优雅关闭
    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()
    
    if err := srv.Shutdown(ctx); err != nil {{
        log.Fatal("Server forced to shutdown:", err)
    }}
    
    log.Println("Server exited")
}}'''
        
        # 生成引导程序
        bootstrap_content = bootstrap_template.format(
            project=self.project_name
        )
        
        bootstrap_path = self.base_path / 'cmd' / 'server' / 'main.go'
        self.write_file(bootstrap_path, bootstrap_content)
        
        main_template = '''package main

import (
    "log"
    "os"
    
    "{project}/internal/infrastructure/container"
    "{project}/internal/infrastructure/bootstrap"
)

func main() {
    config := &container.Config{
        NATS: container.NATSConfig{
            URL:            getEnv("NATS_URL", "nats://localhost:4222"),
            Stream:         getEnv("NATS_STREAM", "events"),
            SnapshotStream: getEnv("NATS_SNAPSHOT_STREAM", "snapshots"),
        },
    }
    
    app, err := bootstrap.NewApp(config)
    if err != nil {
        log.Fatalf("Failed to create app: %v", err)
    }
    
    if err := app.Start(); err != nil {
        log.Fatalf("Failed to start app: %v", err)
    }
}

func getEnv(key, defaultValue string) string {
    if value := os.Getenv(key); value != "" {
        return value
    }
    return defaultValue
}
'''
        
        # 生成引导程序和主程序
        bootstrap_path = self.base_path / 'internal' / 'infrastructure' / 'bootstrap' / 'bootstrap.go'
        self.write_file(bootstrap_path, bootstrap_template)
        
        main_path = self.base_path / 'cmd' / 'server' / 'main.go'
        self.write_file(main_path, main_template)
    
    def write_file(self, path: Path, content: str):
        """写入文件"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)