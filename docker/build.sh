#!/bin/bash

# 定义变量
IMAGE_NAME="fastapi_basic"
IMAGE_TAG="latest"
DOCKER_DIR="$(dirname "$0")"
PROJECT_ROOT="$(cd "$DOCKER_DIR/.." && pwd)"

# 输出信息
echo "开始构建Docker镜像..."
echo "项目根目录: $PROJECT_ROOT"
echo "Dockerfile目录: $DOCKER_DIR"
echo "镜像名称: $IMAGE_NAME:$IMAGE_TAG"
echo ""

# 构建镜像
docker build -t "$IMAGE_NAME:$IMAGE_TAG" -f "$DOCKER_DIR/Dockerfile" "$PROJECT_ROOT"

# 检查构建结果
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Docker镜像构建成功!"
    echo "镜像名称: $IMAGE_NAME:$IMAGE_TAG"
    echo ""
    echo "可以使用以下命令运行容器:"
    echo "docker run -d -p 8000:8000 --env-file $PROJECT_ROOT/.env $IMAGE_NAME:$IMAGE_TAG"
else
    echo ""
    echo "❌ Docker镜像构建失败!"
    exit 1
fi