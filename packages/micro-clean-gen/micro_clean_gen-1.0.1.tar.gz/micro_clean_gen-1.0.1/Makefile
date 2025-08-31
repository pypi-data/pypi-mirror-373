# 微服务代码生成器 Makefile

.PHONY: help install dev-install test lint format clean build upload upload-test

# 默认目标
help:
	@echo "微服务代码生成器"
	@echo ""
	@echo "可用命令:"
	@echo "  install       - 安装包"
	@echo "  dev-install   - 开发模式安装"
	@echo "  test          - 运行测试"
	@echo "  lint          - 代码检查"
	@echo "  format        - 格式化代码"
	@echo "  clean         - 清理构建文件"
	@echo "  build         - 构建包"
	@echo "  upload        - 发布到 PyPI"
	@echo "  upload-test   - 发布到测试 PyPI"
	@echo ""
	@echo "使用示例:"
	@echo "  make install"
	@echo "  make test"
	@echo "  make build"

# 安装
install:
	pip install .

dev-install:
	pip install -e .

# 测试
test:
	python -m pytest tests/ -v

test-coverage:
	python -m pytest tests/ -v --cov=micro_gen --cov-report=html --cov-report=term

# 代码检查
lint:
	python -m flake8 micro_gen/
	python -m mypy micro_gen/
	python -m bandit -r micro_gen/

# 格式化
format:
	python -m black micro_gen/
	python -m isort micro_gen/

# 清理
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# 构建
build: clean
	python -m build

# 上传测试
upload-test: build
	python -m twine upload --repository testpypi dist/*

# 上传正式
upload: build
	python -m twine upload dist/*

# 开发工具安装
dev-deps:
	pip install -e ".[dev]"

# 运行示例
example-basic:
	python -m micro_gen.cli init user-service --output ./examples/user-service
	python -m micro_gen.cli -c ./examples/user-service/config.yaml -o ./examples/user-service/output

example-complex:
	python -m micro_gen.cli -c ./micro_gen/examples/complex.yaml -o ./examples/complex-output

# 验证配置
validate:
	python -m micro_gen.cli validate

# Docker相关
docker-build:
	docker build -t micro-gen:latest .

docker-run:
	docker run -it --rm -v $(PWD):/workspace micro-gen:latest

# 文档
docs:
	python -m mkdocs serve

docs-build:
	python -m mkdocs build

# 发布准备
prepare-release:
	@echo "准备发布..."
	make clean
	make test
	make lint
	make build
	@echo "发布准备完成！"