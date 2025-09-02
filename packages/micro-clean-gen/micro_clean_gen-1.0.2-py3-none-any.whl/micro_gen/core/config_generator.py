"""
配置生成器
负责生成Docker Compose配置、应用配置、环境变量、README文档等
"""

import os
from pathlib import Path
from typing import Dict, List, Any

from .templates.template_loader import TemplateLoader

class ConfigGenerator:
    """配置生成器"""
    
    def __init__(self, config: Dict[str, Any], base_path: Path):
        self.config = config
        self.project_name = config['project']['name']
        self.base_path = base_path
        self.template_loader = TemplateLoader(Path(__file__).parent / "templates" / "config")
    
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

        # 复制日志查询脚本
        self.copy_log_query_script()
    
    def generate_docker_compose(self):
        """生成Docker Compose配置 - 超轻量化日志方案"""
        
        compose_content = self.template_loader.render_template("docker-compose.yml.tmpl", {
            'project_name': self.project_name
        })
        
        compose_path = self.base_path / 'docker-compose.yml'
        self.write_file(compose_path, compose_content)
    
    def generate_app_config(self):
        """生成应用配置"""
        
        # Dockerfile模板
        dockerfile_template = '''# 构建阶段
FROM golang:1.21-alpine AS builder

WORKDIR /app

# 安装依赖
RUN apk add --no-cache git ca-certificates tzdata

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
        go_mod_template = '''module {project_name}

go 1.21

require (
    github.com/nats-io/nats.go v1.31.0
    google.golang.org/grpc v1.59.0
    google.golang.org/protobuf v1.31.0
    go.uber.org/zap v1.26.0
    github.com/dgraph-io/badger/v4 v4.2.0
    github.com/redis/go-redis/v9 v9.3.0
)

require (
    github.com/cespare/xxhash/v2 v2.2.0 // indirect
    github.com/dgraph-io/ristretto v0.1.1 // indirect
    github.com/dustin/go-humanize v1.0.1 // indirect
    github.com/golang/glog v1.1.2 // indirect
    github.com/golang/groupcache v0.0.0-20210331224755-41bb18bfe9da // indirect
    github.com/golang/protobuf v1.5.3 // indirect
    github.com/klauspost/compress v1.17.0 // indirect
    github.com/nats-io/nkeys v0.4.6 // indirect
    github.com/nats-io/nuid v1.0.1 // indirect
    go.opencensus.io v0.24.0 // indirect
    go.uber.org/atomic v1.11.0 // indirect
    go.uber.org/multierr v1.11.0 // indirect
    golang.org/x/crypto v0.14.0 // indirect
    golang.org/x/net v0.17.0 // indirect
    golang.org/x/sys v0.13.0 // indirect
    golang.org/x/text v0.13.0 // indirect
    google.golang.org/genproto/googleapis/rpc v0.0.0-20231030173426-d783a09b4405 // indirect
)'''
        
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

# 日志相关命令
logs:
	docker-compose logs -f app

logs-error:
	grep '"level":"ERROR"' /var/log/docker/{project_name}.log | jq .

logs-tail:
	tail -f /var/log/docker/{project_name}.log | jq .

logs-stats:
	@echo "日志统计:"
	@echo "总日志: $$(wc -l < /var/log/docker/{project_name}.log)"
	@echo "ERROR: $$(grep -c '"level":"ERROR"' /var/log/docker/{project_name}.log 2>/dev/null || echo 0)"
	@echo "WARN: $$(grep -c '"level":"WARN"' /var/log/docker/{project_name}.log 2>/dev/null || echo 0)"
	@echo "INFO: $$(grep -c '"level":"INFO"' /var/log/docker/{project_name}.log 2>/dev/null || echo 0)"

# 日志查询脚本
logs-search:
	@if [ -f scripts/log_query.sh ]; then \
		chmod +x scripts/log_query.sh; \
		./scripts/log_query.sh search "$(filter-out $@,$(MAKECMDGOALS))"; \
	else \
		echo "日志查询脚本不存在"; \
	fi

# 全部清理并重新构建
all: clean deps build

.PHONY: build run docker-build docker-run clean deps test fmt lint proto logs logs-error logs-tail logs-stats all'''
        
        # 写入文件
        dockerfile_path = self.base_path / 'Dockerfile'
        dockerfile_content = self.template_loader.render_template("dockerfile.tmpl", {
            'project_name': self.project_name
        })
        self.write_file(dockerfile_path, dockerfile_content)
        
        go_mod_path = self.base_path / 'go.mod'
        go_mod_content = self.template_loader.render_template("go_mod.tmpl", {
            'project_name': self.project_name
        })
        self.write_file(go_mod_path, go_mod_content)
        
        makefile_path = self.base_path / 'Makefile'
        makefile_content = self.template_loader.render_template("makefile.tmpl", {
            'project_name': self.project_name
        })
        self.write_file(makefile_path, makefile_content)
    
    def generate_env_files(self):
        """生成环境变量文件"""
        
        env_content = self.template_loader.render_template("env.tmpl", {
            'project_name': self.project_name
        })
        
        env_example_content = self.template_loader.render_template("env.example.tmpl", {
            'project_name': self.project_name
        })

        # 写入文件
        env_path = self.base_path / '.env'
        self.write_file(env_path, env_content)
        
        env_example_path = self.base_path / '.env.example'
        self.write_file(env_example_path, env_example_content)
    
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

### 超轻量化日志方案

本项目采用超轻量化日志方案，基于Zap + Docker原生日志驱动，零依赖、高性能。

#### 日志配置

环境变量：
- `SERVICE_NAME`: 服务名称（默认：项目名）
- `CONTAINER_ID`: 容器ID（自动生成）
- `LOG_LEVEL`: 日志级别（默认：info）

#### 日志查询

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f app

# 查看JSON格式日志
cat /var/log/docker/{project_name}.log | jq .

# 查询ERROR级别日志
grep '"level":"ERROR"' /var/log/docker/{project_name}.log | jq .

# 按时间查询日志
cat /var/log/docker/{project_name}.log | jq 'select(.time >= "2024-01-01T00:00:00Z")'

# 按关键词查询日志
grep '数据库连接失败' /var/log/docker/{project_name}.log | jq .msg
```

#### 日志轮转

Docker自动处理日志轮转：
- 单个文件最大10MB
- 保留3个历史文件
- 总日志空间不超过30MB

### 生产部署

```bash
# 生产环境部署
docker-compose up -d

# 设置环境变量启动
CONTAINER_ID=$(uuidgen) docker-compose up -d
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
    
    def copy_log_query_script(self):
        """复制日志查询脚本"""
        scripts_dir = self.base_path / 'scripts'
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制日志查询脚本
        import shutil
        import os
        
        source_script = os.path.join(os.path.dirname(__file__), 'templates', 'log_query.sh')
        target_script = scripts_dir / 'log_query.sh'
        
        if os.path.exists(source_script):
            shutil.copy2(source_script, target_script)
            os.chmod(target_script, 0o755)
            print("📝 已生成日志查询脚本: scripts/log_query.sh")
        else:
            print("⚠️  日志查询脚本模板不存在")

    def write_file(self, path: Path, content: str):
        """写入文件"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)