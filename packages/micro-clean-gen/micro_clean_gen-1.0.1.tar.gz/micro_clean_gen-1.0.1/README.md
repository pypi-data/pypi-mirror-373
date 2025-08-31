# 🐍 Python版整洁架构事件驱动微服务生成器

> **无需Go环境，纯Python一键生成** 整洁架构 + 事件溯源 + CQRS + Projection 完整项目

## 🎯 核心特性

| 特性         | 描述                           |
| ------------ | ------------------------------ |
| **零依赖**   | 只需Python3，无需Go环境        |
| **整洁架构** | 严格遵循Clean Architecture原则 |
| **事件溯源** | 完整的事件存储和重播机制       |
| **CQRS**     | 读写分离，高性能查询           |
| **投影系统** | 毫秒级查询响应                 |
| **一键启动** | 15秒内生成完整项目             |

## 🚀 快速开始

### 1. 生成图片管理系统示例

```bash
python3 micro-gen --config examples/clean-arch-go-config.yaml --output clean-arch-go
```

### 2. 15秒启动完整系统

```bash
cd clean-arch-go
./scripts/start.sh

# 访问服务
API: http://localhost:8080
NATS监控: http://localhost:8222
```

## 📁 生成的项目结构

```
project-name/
├── cmd/                    # 应用入口
│   ├── api/               # HTTP API服务
│   ├── consumer/          # 事件消费者
│   ├── projection/        # 投影构建器
│   └── migration/         # 数据库迁移
├── internal/              # 核心业务逻辑
│   ├── domain/            # 领域层
│   │   ├── aggregate/     # 聚合根
│   │   ├── event/         # 领域事件
│   │   ├── repository/    # 仓储接口
│   │   └── projection/    # 投影接口
│   ├── usecase/           # 用例层
│   │   ├── command/       # 写用例
│   │   ├── query/         # 读用例
│   │   └── event/         # 事件处理
│   ├── adapter/           # 适配器层
│   │   ├── inbound/       # 输入适配器
│   │   └── outbound/      # 输出适配器
│   ├── infrastructure/    # 基础设施层
│   │   ├── config/        # 配置管理
│   │   ├── bootstrap/     # 服务引导程序
│   │   ├── database/      # 数据库连接
│   │   ├── eventstore/    # 事件存储
│   │   └── container/     # 依赖注入容器
├── configs/               # 配置文件
│   ├── app.yaml          # 应用配置
│   └── .env.example      # 环境变量模板
├── migrations/            # 数据库迁移
├── scripts/               # 开发脚本
└── docs/                  # 项目文档
```

## 🏗️ 架构层次

### 领域层 (Domain Layer)
- **聚合根**: 核心业务逻辑和状态
- **领域事件**: 业务状态变化的记录
- **仓储接口**: 数据持久化抽象

### 用例层 (Use Case Layer)
- **命令用例**: 处理写操作
- **查询用例**: 处理读操作
- **事件处理**: 响应领域事件

### 适配器层 (Adapter Layer)
- **输入适配器**: HTTP API, gRPC, CLI
- **输出适配器**: 数据库, 消息队列, 缓存

### 基础设施层 (Infrastructure Layer)
- **事件存储**: PostgreSQL + NATS
- **投影存储**: PostgreSQL + Redis
- **缓存层**: Redis多级缓存

## 🎯 事件溯源实现

### 事件存储
```go
// 事件存储接口
type EventStore interface {
    Save(ctx context.Context, aggregateID string, events []interface{}, version int) error
    Load(ctx context.Context, aggregateID string) ([]interface{}, error)
    Publish(ctx context.Context, event interface{}) error
    
    // 快照支持
    SaveSnapshot(ctx context.Context, aggregateID string, snapshot interface{}, version int) error
    LoadSnapshot(ctx context.Context, aggregateID string) (interface{}, int, error)
    GetSnapshotVersion(ctx context.Context, aggregateID string) (int, error)
}

// 快照接口
type Snapshot interface {
    GetAggregateID() string
    GetVersion() int
    GetSnapshotData() interface{}
}

// 聚合根快照基类
type AggregateSnapshot struct {
    AggregateID string
    Version     int
    Data        interface{}
}

func (s *AggregateSnapshot) GetAggregateID() string {
    return s.AggregateID
}

func (s *AggregateSnapshot) GetVersion() int {
    return s.Version
}

func (s *AggregateSnapshot) GetSnapshotData() interface{} {
    return s.Data
}
```

### 投影系统
```go
// 投影构建器
type Projection interface {
    Project(ctx context.Context, event interface{}) error
    Get(ctx context.Context, id string) (interface{}, error)
}
```

## 📊 性能基准

| 操作类型 | 响应时间      | 并发能力   |
| -------- | ------------- | ---------- |
| 创建聚合 | < 50ms        | 1000+ TPS  |
| 查询投影 | < 5ms         | 10000+ QPS |
| 事件重播 | < 1s/1000事件 | 可并行     |
| 投影更新 | < 100ms       | 实时更新   |

## 🚀 Bootstrap系统

### 服务引导程序
```go
// 使用Bootstrap启动应用
func main() {
    bootstrap.Run()
}
```

### 配置管理
```go
// 使用Viper加载配置
cfg, err := config.LoadConfig()
```

### 依赖注入容器
```go
// 容器管理所有依赖
container := container.NewContainer(cfg)
container.InitInfrastructure(ctx)
container.InitRepositories()
container.InitUseCases()
container.InitHTTPServer()
```

### 配置方式

#### 1. 配置文件 (configs/app.yaml)
```yaml
app:
  name: my-service
  version: 1.0.0
  environment: development
  debug: true

database:
  host: localhost
  port: 5432
  user: user
  password: password
  dbname: mydb
```

#### 2. 环境变量
```bash
# 数据库配置
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=user
export DB_PASSWORD=password

# 启动应用
./scripts/start.sh
```

#### 3. .env文件
```bash
# 复制环境变量模板
cp configs/.env.example configs/.env
# 编辑配置文件
vim configs/.env
```

## 🛠️ 开发工具

### 一键启动
```bash
# 开发环境
./scripts/start.sh

# 生产环境
./scripts/build.sh
docker-compose up -d
```

### 数据库迁移
```bash
# 自动迁移
go run cmd/migration/main.go

# 手动迁移
psql -h localhost -U user -d image_system -f migrations/001_create_events.up.sql
```

### 测试命令
```bash
# 单元测试
go test ./...

# 集成测试
./scripts/test.sh

# 性能测试
./scripts/benchmark.sh
```

## 🎨 DSL配置指南

### 配置文件结构详解

Python生成器使用YAML格式的DSL（领域特定语言）来定义整个微服务的架构。配置文件支持以下顶级配置项：

#### 📋 项目配置 (project)
定义项目的基本信息：

```yaml
project:
  name: my-service                    # 项目名称（必填）- 用于包名、模块名
  description: 我的微服务              # 项目描述（可选）- 用于README文档
  version: 1.0.0                    # 版本号（可选）- 默认为1.0.0
  author: Your Name                 # 作者信息（可选）
  go_version: 1.21                  # Go版本（可选）- 默认为1.21
```

#### 🏗️ 聚合根配置 (aggregates)
定义业务聚合根，每个聚合根对应一个核心业务实体：

```yaml
aggregates:
  - name: User                      # 聚合根名称（必填）- 首字母大写
    description: 用户聚合根           # 描述（可选）
    fields:                         # 聚合根字段定义
      - name: username              # 字段名（必填）
        type: string                # Go类型（必填）- string/int/float64/bool/time.Time
        json: username              # JSON标签（可选）- 默认为字段名小写
        gorm: uniqueIndex           # GORM标签（可选）- 支持所有GORM标签
        validate: required,min=3    # 验证标签（可选）- 支持go-playground/validator
        description: 用户名           # 字段描述（可选）
      
      - name: email
        type: string
        json: email
        validate: required,email
        gorm: uniqueIndex
        
      - name: age
        type: int
        json: age
        validate: min=0,max=150
        
      - name: active
        type: bool
        json: active
        default: true                 # 默认值（可选）
```

#### ⚡ 事件定义 (events)
每个聚合根可以定义多个领域事件：

```yaml
    events:
      - name: UserCreated            # 事件名称（必填）- 必须以聚合根名开头
        description: 用户创建事件      # 事件描述（可选）
        fields:                      # 事件字段（可选）
          - name: UserID
            type: string
            json: user_id
            description: 用户ID
            
          - name: Username
            type: string
            json: username
            
      - name: UserUpdated
        description: 用户更新事件
        fields:
          - name: UserID
            type: string
            json: user_id
            
          - name: UpdatedFields
            type: map[string]interface{}  # 支持复杂类型
            json: updated_fields
            
      - name: UserDeleted
        description: 用户删除事件
        fields:
          - name: UserID
            type: string
            json: user_id
            
          - name: DeletedAt
            type: time.Time
            json: deleted_at
```

#### 📊 投影配置 (projections)
定义事件投影模型（可选配置）：

```yaml
projections:
  - name: UserProjection            # 投影名称（必填）
    aggregate: User                 # 关联的聚合根（必填）
    description: 用户查询投影        # 描述（可选）
    fields:                         # 投影字段定义
      - name: ID
        type: string
        gorm: primaryKey
        
      - name: Username
        type: string
        gorm: index
        
      - name: Email
        type: string
        gorm: uniqueIndex
        
      - name: Active
        type: bool
        gorm: index
```

#### 🔧 基础设施配置 (infrastructure)
定义基础设施依赖：

```yaml
infrastructure:
  database:                       # 数据库配置
    type: postgresql              # 支持postgresql/mysql/sqlite
    host: localhost
    port: 5432
    database: myservice
    username: user
    password: password
    
  cache:                         # 缓存配置
    type: redis                  # 支持redis/memcached
    host: localhost
    port: 6379
    
  message_queue:               # 消息队列
    type: nats                 # 支持nats/rabbitmq/kafka
    host: localhost
    port: 4222
    
  monitoring:                  # 监控配置
    metrics: true              # 启用Prometheus指标
    tracing: true              # 启用分布式追踪
    logging: zap               # 日志库选择
```

#### 🌐 API配置 (api)
定义API接口：

```yaml
api:
  http:                        # HTTP配置
    enabled: true
    port: 8080
    prefix: /api/v1
    
  grpc:                       # gRPC配置
    enabled: true
    port: 50051
    reflection: true          # 启用服务反射
    
  cors:                      # CORS配置
    enabled: true
    origins: ["*"]
    methods: ["GET", "POST", "PUT", "DELETE"]
    headers: ["Content-Type", "Authorization"]
```

#### 🔗 会话管理 (session)
分布式会话管理配置，用于长时任务和Saga事务：

```yaml
session:
  enabled: true              # 启用会话管理
  
  saga:                      # Saga配置
    enabled: true
    timeout: 30m             # Saga超时时间
    compensation: true       # 启用补偿机制
    
  context:                   # 会话上下文
    storage: redis          # 存储后端: redis/postgresql
    ttl: 24h                # 会话TTL
    compression: true       # 启用压缩
    
  orchestration:            # 编排配置
    pattern: choreography   # 编排模式: choreography/orchestration
    coordinator: enabled    # 启用协调器（仅orchestration模式）
    
  checkpoint:              # 检查点机制
    enabled: true
    interval: 30s           # 自动检查点间隔
    storage: postgresql     # 检查点存储
    
  recovery:                # 故障恢复
    enabled: true
    strategy: retry         # 恢复策略: retry/rollback/compensate
    max_retries: 3        # 最大重试次数
    backoff: exponential  # 退避策略
```

#### 🔄 长时任务 (long_running)
长时任务和批处理配置：

```yaml
long_running:
  enabled: true
  
  tasks:
    - name: ImageProcessingTask
      type: batch             # 任务类型: batch/streaming
      timeout: 2h
      parallelism: 5         # 并行度
      
      stages:               # 处理阶段
        - name: Download
          timeout: 10m
          retry_policy: 3
          
        - name: Process
          timeout: 1h
          checkpoint: true   # 启用检查点
          
        - name: Upload
          timeout: 30m
          retry_policy: 5
          
      context:              # 会话上下文
        required_fields:
          - user_id
          - image_urls
          - processing_config
        
        distributed_lock: true    # 分布式锁
        state_machine: true      # 状态机
        
      compensation:         # 补偿机制
        enabled: true
        rollback_steps:
          - DeleteTempFiles
          - RevertDatabase
          - SendNotification
```

### 完整配置示例

```yaml
# 完整项目配置示例
project:
  name: ecommerce-order-service
  description: 电商订单服务 - 支持订单创建、支付、发货等完整生命周期
  version: 2.1.0
  author: 架构团队
  go_version: 1.21

aggregates:
  - name: Order
    description: 订单聚合根
    fields:
      - name: OrderNumber
        type: string
        json: order_number
        validate: required
        gorm: uniqueIndex
        description: 订单号
        
      - name: CustomerID
        type: string
        json: customer_id
        validate: required,uuid
        gorm: index
        description: 客户ID
        
      - name: TotalAmount
        type: float64
        json: total_amount
        validate: required,min=0
        description: 订单总金额
        
      - name: Status
        type: string
        json: status
        validate: required,oneof=pending paid shipped delivered cancelled
        gorm: index
        default: pending
        description: 订单状态
        
      - name: ShippingAddress
        type: string
        json: shipping_address
        validate: required
        description: 收货地址
        
    events:
      - name: OrderCreated
        description: 订单创建事件
        fields:
          - name: OrderID
            type: string
            json: order_id
            validate: required,uuid
            
          - name: Items
            type: "[]OrderItem"  # 支持自定义类型
            json: items
            
      - name: OrderPaid
        description: 订单支付事件
        fields:
          - name: OrderID
            type: string
            json: order_id
            
          - name: PaymentID
            type: string
            json: payment_id
            
          - name: PaidAt
            type: time.Time
            json: paid_at
            
      - name: OrderShipped
        description: 订单发货事件
        fields:
          - name: OrderID
            type: string
            json: order_id
            
          - name: TrackingNumber
            type: string
            json: tracking_number
            
      - name: OrderDelivered
        description: 订单送达事件
        fields:
          - name: OrderID
            type: string
            json: order_id
            
          - name: DeliveredAt
            type: time.Time
            json: delivered_at

projections:
  - name: OrderSummaryProjection
    aggregate: Order
    description: 订单摘要投影 - 用于查询订单列表
    fields:
      - name: ID
        type: string
        gorm: primaryKey
        
      - name: OrderNumber
        type: string
        gorm: uniqueIndex
        
      - name: CustomerID
        type: string
        gorm: index
        
      - name: TotalAmount
        type: float64
        
      - name: Status
        type: string
        gorm: index
        
      - name: CreatedAt
        type: time.Time
        gorm: index

infrastructure:
  database:
    type: postgresql
    host: localhost
    port: 5432
    database: ecommerce
    username: ecommerce_user
    password: secure_password
    
  cache:
    type: redis
    host: localhost
    port: 6379
    
  message_queue:
    type: nats
    host: localhost
    port: 4222
    
  monitoring:
    metrics: true
    tracing: true
    logging: zap

api:
  http:
    enabled: true
    port: 8080
    prefix: /api/v2
    
  grpc:
    enabled: true
    port: 50051
    reflection: true
    
  cors:
    enabled: true
    origins: ["https://frontend.com", "https://admin.com"]
    methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    headers: ["Content-Type", "Authorization", "X-Requested-With"]

session:
  enabled: true
  
  saga:
    enabled: true
    timeout: 30m
    compensation: true
    
  context:
    storage: redis
    ttl: 24h
    compression: true
    
  orchestration:
    pattern: choreography
    coordinator: enabled
    
  checkpoint:
    enabled: true
    interval: 30s
    storage: postgresql
    
  recovery:
    enabled: true
    strategy: retry
    max_retries: 3
    backoff: exponential

long_running:
  enabled: true
  
  tasks:
    - name: OrderFulfillmentTask
      type: batch
      timeout: 4h
      parallelism: 3
      
      stages:
        - name: InventoryCheck
          timeout: 5m
          retry_policy: 3
          
        - name: PaymentProcessing
          timeout: 15m
          checkpoint: true
          
        - name: ShippingArrangement
          timeout: 1h
          retry_policy: 2
          
        - name: Notification
          timeout: 5m
          
      context:
        required_fields:
          - order_id
          - customer_id
          - payment_method
          - shipping_address
        
        distributed_lock: true
        state_machine: true
        
      compensation:
        enabled: true
        rollback_steps:
          - ReleaseInventory
          - RefundPayment
          - CancelShipping
          - SendCancellationNotification
```

### 生成项目

使用配置文件生成项目：

```bash
# 基础用法
python3 clean-arch-generator.py --config my-service.yaml

# 指定输出目录
python3 clean-arch-generator.py --config my-service.yaml --output ./projects/

# 使用自定义项目名
python3 clean-arch-generator.py --config my-service.yaml --project custom-name
```

### 支持的Go类型映射

| DSL类型                | Go类型                 | 数据库类型   | 描述       |
| ---------------------- | ---------------------- | ------------ | ---------- |
| string                 | string                 | VARCHAR(255) | 字符串     |
| int                    | int                    | INTEGER      | 整数       |
| int64                  | int64                  | BIGINT       | 大整数     |
| float64                | float64                | DECIMAL      | 浮点数     |
| bool                   | bool                   | BOOLEAN      | 布尔值     |
| time.Time              | time.Time              | TIMESTAMP    | 时间戳     |
| uuid.UUID              | uuid.UUID              | UUID         | UUID       |
| json.RawMessage        | json.RawMessage        | JSONB        | JSON数据   |
| []string               | []string               | TEXT[]       | 字符串数组 |
| map[string]interface{} | map[string]interface{} | JSONB        | JSON对象   |

## 🔧 技术栈

### 核心依赖
- **Go**: 1.21+
- **PostgreSQL**: 15+ (事件存储)
- **Redis**: 7+ (缓存和投影)
- **NATS**: 2+ (消息队列)

### 开发工具
- **Docker**: 容器化部署
- **Docker Compose**: 本地开发
- **Make**: 构建工具
- **Air**: 热重载

## 🎯 会话管理架构

### 分布式会话设计

```
┌─────────────────────────────────────────────────────────────┐
│                    Session Management Layer                 │
├─────────────────┬─────────────────┬───────────────────────────┤
│   Saga Manager  │ Context Manager │  Checkpoint Manager       │
│                 │                 │                           │
│ ┌─────────────┐ │ ┌─────────────┐ │ ┌───────────────────────┐ │
│ │ Coordinator │ │ │  Session    │ │ │   State Machine     │ │
│ │   / Choreo  │ │ │  Context    │ │ │   Recovery Engine   │ │
│ └─────────────┘ │ └─────────────┘ │ └───────────────────────┘ │
└─────────────────┴─────────────────┴───────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Storage Layer                           │
├─────────────────┬─────────────────┬───────────────────────────┤
│     Redis       │   PostgreSQL    │     Event Store          │
│  (Session TTL)  │ (Checkpoint)    │   (Event Log)            │
└─────────────────┴─────────────────┴───────────────────────────┘
```

### 会话上下文结构

```go
type SessionContext struct {
    SessionID    string                 `json:"session_id"`
    SagaID       string                 `json:"saga_id"`
    WorkflowID   string                 `json:"workflow_id"`
    
    // 执行状态
    CurrentStage string                 `json:"current_stage"`
    StageIndex   int                    `json:"stage_index"`
    Status       SessionStatus          `json:"status"`
    
    // 业务上下文
    Payload      map[string]interface{} `json:"payload"`
    Metadata     map[string]string      `json:"metadata"`
    
    // 时间控制
    CreatedAt    time.Time              `json:"created_at"`
    UpdatedAt    time.Time              `json:"updated_at"`
    ExpiresAt    time.Time              `json:"expires_at"`
    
    // 故障恢复
    RetryCount   int                    `json:"retry_count"`
    LastError    string                 `json:"last_error"`
    
    // 分布式锁
    LockToken    string                 `json:"lock_token"`
    LockedBy     string                 `json:"locked_by"`
    LockExpiry   time.Time              `json:"lock_expiry"`
}
```

### 会话生命周期管理

```go
type SessionManager interface {
    // 会话创建
    CreateSession(ctx context.Context, workflowID string, payload map[string]interface{}) (*SessionContext, error)
    
    // 状态更新
    UpdateStage(ctx context.Context, sessionID string, stage string, data map[string]interface{}) error
    
    // 检查点
    SaveCheckpoint(ctx context.Context, sessionID string, stageIndex int) error
    
    // 故障恢复
    RecoverSession(ctx context.Context, sessionID string) (*SessionContext, error)
    
    // 分布式锁
    AcquireLock(ctx context.Context, sessionID string, instanceID string) (bool, error)
    ReleaseLock(ctx context.Context, sessionID string, lockToken string) error
    
    // 补偿机制
    Compensate(ctx context.Context, sessionID string, steps []string) error
}
```

### 实际使用示例

#### 1. 启动长时任务会话
```go
// 创建订单履约会话
session, err := sessionManager.CreateSession(ctx, "order-fulfillment", map[string]interface{}{
    "order_id":      order.ID,
    "customer_id":   order.CustomerID,
    "payment_method": order.PaymentMethod,
    "shipping_address": order.ShippingAddress,
})
```

#### 2. 阶段执行与检查点
```go
// 执行库存检查阶段
func (s *OrderFulfillmentService) executeInventoryCheck(ctx context.Context, sessionID string) error {
    // 获取会话上下文
    session, err := s.sessionManager.GetSession(ctx, sessionID)
    if err != nil {
        return fmt.Errorf("failed to get session: %w", err)
    }
    
    // 执行业务逻辑
    if err := s.inventoryService.CheckAvailability(ctx, session.Payload["order_id"]); err != nil {
        // 保存失败状态
        s.sessionManager.UpdateStage(ctx, sessionID, "inventory_check_failed", map[string]interface{}{
            "error": err.Error(),
        })
        return err
    }
    
    // 保存检查点
    return s.sessionManager.SaveCheckpoint(ctx, sessionID, 1)
}
```

#### 3. 故障恢复
```go
// 服务重启后恢复会话
func (s *OrderFulfillmentService) recoverSessions(ctx context.Context) error {
    // 获取所有未完成的会话
    sessions, err := s.sessionManager.GetActiveSessions(ctx)
    if err != nil {
        return err
    }
    
    for _, session := range sessions {
        // 检查分布式锁
        locked, err := s.sessionManager.AcquireLock(ctx, session.SessionID, s.instanceID)
        if err != nil || !locked {
            continue // 其他实例正在处理
        }
        
        // 恢复执行
        go s.resumeWorkflow(ctx, session)
    }
    
    return nil
}
```

### 会话存储策略

#### Redis存储（高性能）
```yaml
session:
  context:
    storage: redis
    ttl: 24h
    compression: true
    key_prefix: "session:"
    cluster_mode: true
```

#### PostgreSQL存储（持久化）
```yaml
session:
  context:
    storage: postgresql
    ttl: 7d
    table_name: "session_contexts"
    cleanup_interval: 1h
```

### 故障恢复策略

#### 1. 重试策略（Retry）
```go
// 指数退避重试
backoff := &ExponentialBackoff{
    InitialInterval: time.Second,
    MaxInterval:     time.Minute,
    Multiplier:      2.0,
    MaxRetries:      3,
}

for i := 0; i < backoff.MaxRetries; i++ {
    err := executeStage(ctx, sessionID)
    if err == nil {
        break
    }
    
    if i < backoff.MaxRetries-1 {
        time.Sleep(backoff.NextInterval(i))
    }
}
```

#### 2. 补偿策略（Compensate）
```go
// Saga补偿机制
func (s *OrderFulfillmentService) compensate(ctx context.Context, sessionID string) error {
    session, _ := s.sessionManager.GetSession(ctx, sessionID)
    
    // 逆序执行补偿步骤
    for i := len(session.CompletedStages) - 1; i >= 0; i-- {
        stage := session.CompletedStages[i]
        
        switch stage.Name {
        case "inventory_reserved":
            s.inventoryService.ReleaseReservation(ctx, session.Payload["order_id"])
        case "payment_processed":
            s.paymentService.Refund(ctx, session.Payload["payment_id"])
        case "shipping_arranged":
            s.shippingService.CancelShipment(ctx, session.Payload["shipment_id"])
        }
    }
    
    return s.sessionManager.Compensate(ctx, sessionID, []string{"all"})
}
```

## 📈 扩展能力

## 🎓 学习资源

### 文档
- [整洁架构指南](docs/architecture.md)
- [API文档](docs/api.md)
- [部署指南](docs/deployment.md)

### 示例项目
- [图片管理系统](examples/clean-arch-go-config.yaml)
- [订单系统](examples/order-system.yaml)
- [用户管理系统](examples/user-system.yaml)

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交Pull Request
4. 通过代码审查

## 📄 许可证

MIT License - 自由使用，欢迎贡献！