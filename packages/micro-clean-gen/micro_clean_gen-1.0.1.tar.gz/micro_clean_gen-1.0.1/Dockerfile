# 微服务代码生成器 Docker镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
COPY VERSION .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY micro_gen/ ./micro_gen/
COPY setup.py .
COPY README.md .
COPY LICENSE .
COPY MANIFEST.in .

# 安装包
RUN pip install -e .

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app
USER app

# 设置工作目录
WORKDIR /workspace

# 设置默认命令
ENTRYPOINT ["micro-gen"]
CMD ["--help"]