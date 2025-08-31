"""
配置生成器
负责生成Docker Compose配置、应用配置、环境变量、README文档等
"""

import os
from pathlib import Path
from typing import Dict, List, Any

class ConfigGenerator:
    """配置生成器"""
    
    def __init__(self, config: Dict[str, Any], base_path: Path):
        self.config = config
        self.project_name = config['project']['name']
        self.base_path = base_path
    
    def generate(self):
        """生成配置"""
        print("🏗️  生成配置文件...")
        
        # 生成Docker Compose配置
        self.generate_docker_compose()
        
        # 生成应用配置
        self.generate_app_config()
        
        # 生成环境变量
        self.generate_env_files()
        
        # 生成README文档
        self.generate_readme()
    
    def generate_docker_compose(self):
        """生成Docker Compose配置"""
        
        # Docker Compose模板
        compose_template = '''version: '3.8'

services:
  # 应用服务
  app:
    build: .
    ports:
      - "8080:8080"
      - "50051:50051"
    environment:
      - NATS_URL=nats://nats:4222
      - NATS_STREAM=events
      - NATS_SNAPSHOT_STREAM=snapshots
    depends_on:
      - nats
    networks:
      - microservice-net

  # NATS消息代理
  nats:
    image: nats:latest
    ports:
      - "4222:4222"
      - "8222:8222"
    command: ["--js"]
    networks:
      - microservice-net

  # 监控
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - microservice-net

  # 日志聚合
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    networks:
      - microservice-net

networks:
  microservice-net:
    driver: bridge
'''
        
        compose_path = self.base_path / 'docker-compose.yml'
        self.write_file(compose_path, compose_template)
    
    def generate_app_config(self):
        """生成应用配置"""
        
        # Dockerfile模板
        dockerfile_template = '''# 构建阶段
FROM golang:1.21-alpine AS builder

WORKDIR /app

# 安装依赖
RUN apk add --no-cache git

# 复制go mod文件
COPY go.mod go.sum ./
RUN go mod download

# 复制源代码
COPY . .

# 构建应用
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main cmd/server/main.go

# 运行阶段
FROM alpine:latest

RUN apk --no-cache add ca-certificates
WORKDIR /root/

# 从构建阶段复制二进制文件
COPY --from=builder /app/main .

# 暴露端口
EXPOSE 8080 50051

# 运行应用
CMD ["./main"]
'''
        
        # Go模块模板
        go_mod_template = '''module {project}

go 1.21

require (
    github.com/nats-io/nats.go v1.31.0
    google.golang.org/grpc v1.59.0
    google.golang.org/protobuf v1.31.0
)

require (
    github.com/golang/protobuf v1.5.3 // indirect
    github.com/klauspost/compress v1.17.0 // indirect
    github.com/nats-io/nkeys v0.4.6 // indirect
    github.com/nats-io/nuid v1.0.1 // indirect
    golang.org/x/crypto v0.14.0 // indirect
    golang.org/x/net v0.17.0 // indirect
    golang.org/x/sys v0.13.0 // indirect
    golang.org/x/text v0.13.0 // indirect
    google.golang.org/genproto/googleapis/rpc v0.0.0-20231030173426-d783a09b4405 // indirect
)
'''
        
        # Makefile模板
        makefile_template = '''# Go 参数
GOCMD=go
GOBUILD=$(GOCMD) build
GOCLEAN=$(GOCMD) clean
GOTEST=$(GOCMD) test
GOGET=$(GOCMD) get
GOMOD=$(GOCMD) mod
BINARY_NAME=main
DOCKER_IMAGE={project_name}

# 构建应用
build:
	$(GOBUILD) -o $(BINARY_NAME) -v cmd/server/main.go

# 运行应用
run:
	$(GOCMD) run cmd/server/main.go

# 构建Docker镜像
docker-build:
	docker build -t $(DOCKER_IMAGE) .

# 运行Docker容器
docker-run:
	docker-compose up --build

# 清理
clean:
	$(GOCLEAN)
	rm -f $(BINARY_NAME)

# 依赖管理
deps:
	$(GOMOD) download
	$(GOMOD) tidy

# 测试
test:
	$(GOTEST) -v ./...

# 代码格式化
fmt:
	$(GOCMD) fmt ./...

# 代码检查
lint:
	golangci-lint run

# 生成proto文件
proto:
	protoc --go_out=. --go-grpc_out=. pkg/proto/*.proto

# 全部清理并重新构建
all: clean deps build

.PHONY: build run docker-build docker-run clean deps test fmt lint proto all
'''
        
        # 写入文件
        dockerfile_path = self.base_path / 'Dockerfile'
        self.write_file(dockerfile_path, dockerfile_template)
        
        go_mod_path = self.base_path / 'go.mod'
        self.write_file(go_mod_path, go_mod_template.format(project=self.project_name))
        
        makefile_path = self.base_path / 'Makefile'
        self.write_file(makefile_path, makefile_template.format(project_name=self.project_name))
    
    def generate_env_files(self):
        """生成环境变量文件"""
        
        # 环境变量模板
        env_template = '''# NATS配置
NATS_URL=nats://localhost:4222
NATS_STREAM=events
NATS_SNAPSHOT_STREAM=snapshots

# 应用配置
APP_PORT=8080
GRPC_PORT=50051

# 日志配置
LOG_LEVEL=info
LOG_FORMAT=json

# 监控配置
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000

# 数据库配置（如果使用）
DB_HOST=localhost
DB_PORT=5432
DB_NAME={project_name}
DB_USER=postgres
DB_PASSWORD=password

# Redis配置（如果使用）
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
'''
        
        # 环境变量示例模板
        env_example_template = '''# 复制此文件为 .env 并修改相应配置

# NATS配置
NATS_URL=nats://localhost:4222
NATS_STREAM=events
NATS_SNAPSHOT_STREAM=snapshots

# 应用配置
APP_PORT=8080
GRPC_PORT=50051

# 日志配置
LOG_LEVEL=info
LOG_FORMAT=json

# 监控配置
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000

# 数据库配置（可选）
DB_HOST=localhost
DB_PORT=5432
DB_NAME={project_name}
DB_USER=postgres
DB_PASSWORD=password

# Redis配置（可选）
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
'''
        
        # 写入文件
        env_path = self.base_path / '.env'
        self.write_file(env_path, env_template.format(project_name=self.project_name))
        
        env_example_path = self.base_path / '.env.example'
        self.write_file(env_example_path, env_example_template.format(project_name=self.project_name))
    
    def generate_readme(self):
        """生成README文档"""
        
        # README模板
        readme_template = '''# {project_name}

一个基于事件驱动的微服务，使用整洁架构模式构建。

## 特性

- 🚀 基于整洁架构设计
- 📡 事件驱动架构
- 🔍 事件溯源模式
- 🏗️ 聚合根模式
- 📊 投影模式
- 🌐 RESTful API
- 🎯 gRPC服务
- 📡 NATS消息代理
- 🐳 Docker容器化
- 📈 Prometheus监控
- 📊 Grafana可视化

## 快速开始

### 前置要求

- Go 1.21+
- Docker & Docker Compose
- NATS消息代理

### 安装依赖

```bash
go mod download
```

### 本地运行

1. 复制环境变量文件：
```bash
cp .env.example .env
```

2. 启动基础设施服务：
```bash
docker-compose up -d nats
```

3. 运行应用：
```bash
make run
```

### Docker运行

```bash
make docker-run
```

## API文档

### RESTful API

#### 创建{name}
```bash
curl -X POST http://localhost:8080/api/v1/{name_lower} \\
  -H "Content-Type: application/json" \\
  -d '{json_example}'
```

#### 获取{name}
```bash
curl http://localhost:8080/api/v1/{name_lower}?id=123
```

#### 更新{name}
```bash
curl -X PUT http://localhost:8080/api/v1/{name_lower} \\
  -H "Content-Type: application/json" \\
  -d '{json_example}'
```

#### 列表{name}
```bash
curl http://localhost:8080/api/v1/{name_lower}/list?limit=10&offset=0
```

### gRPC API

#### 生成proto文件
```bash
make proto
```

#### 调用gRPC服务
```bash
grpcurl -plaintext localhost:50051 list
```

## 架构

### 清洁架构

```
cmd/
├── server/
│   └── main.go
internal/
├── domain/
│   ├── aggregate/      # 聚合根
│   ├── event/        # 领域事件
│   ├── repository/   # 仓储接口
│   └── projection/   # 投影接口
├── usecase/
│   ├── command/      # 命令用例
│   ├── query/        # 查询用例
│   └── event/        # 事件处理器
├── adapter/
│   ├── http/         # HTTP处理器
│   ├── grpc/         # gRPC服务
│   └── message/      # 消息处理器
└── infrastructure/
    ├── eventstore/   # 事件存储
    ├── projection/   # 投影实现
    └── container/    # 依赖注入容器
```

### 事件流

1. **命令处理**：HTTP/gRPC请求 -> 命令处理器 -> 领域验证 -> 事件生成
2. **事件存储**：事件持久化 -> 事件发布 -> 事件溯源
3. **投影更新**：事件订阅 -> 投影更新 -> 查询优化

## 监控

### Prometheus指标

- HTTP请求指标
- gRPC调用指标
- 事件处理指标
- 系统性能指标

### Grafana仪表板

访问 http://localhost:3000 (admin/admin)

## 开发

### 代码规范

```bash
make fmt    # 格式化代码
make lint   # 代码检查
make test   # 运行测试
```

### 添加新聚合

1. 在配置文件中定义聚合
2. 运行代码生成器
3. 实现业务逻辑

## 部署

### 环境变量

- `NATS_URL`: NATS服务器地址
- `NATS_STREAM`: 事件流名称
- `APP_PORT`: HTTP端口
- `GRPC_PORT`: gRPC端口

### 生产部署

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 贡献

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 许可证

MIT License

## 支持

如有问题，请提交Issue或联系维护者。
'''
        
        # 为每个聚合生成JSON示例
        aggregates_info = []
        for aggregate in self.config['aggregates']:
            name = aggregate['name']
            name_lower = name.lower()
            
            # 生成JSON示例
            json_example = "{"
            for field in aggregate['fields']:
                field_name = field["name"]
                field_example = self.get_field_example(field["type"])
                json_example += f'"{field_name}": "{field_example}", '
            json_example = json_example.rstrip(', ') + "}"
            
            aggregates_info.append({
                'name': name,
                'name_lower': name_lower,
                'json_example': json_example
            })
        
        # 使用第一个聚合的信息
        if aggregates_info:
            info = aggregates_info[0]
            readme_content = readme_template.format(
                project_name=self.project_name,
                name=info['name'],
                name_lower=info['name_lower'],
                json_example=info['json_example']
            )
        else:
            readme_content = readme_template.format(
                project_name=self.project_name,
                name="Entity",
                name_lower="entity",
                json_example='{"name": "example", "description": "test entity"}'
            )
        
        readme_path = self.base_path / 'README.md'
        self.write_file(readme_path, readme_content)
    
    def get_field_example(self, field_type: str) -> str:
        """根据字段类型返回示例值"""
        type_mapping = {
            'string': 'example',
            'int': '123',
            'int64': '123',
            'float64': '123.45',
            'bool': 'true',
            'time.Time': '2024-01-01T00:00:00Z'
        }
        return type_mapping.get(field_type, 'example')
    
    def write_file(self, path: Path, content: str):
        """写入文件"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)