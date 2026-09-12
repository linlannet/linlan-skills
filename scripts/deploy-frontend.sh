#!/bin/bash

# 麟览技能市场 - 前端部署脚本
# 用法: ./deploy-frontend.sh <项目上下文>
# 示例: ./deploy-frontend.sh linlannet

if [ -z "$1" ]; then
    echo "用法: $0 <项目上下文>"
    echo "可用项目: linlannet, eframe, waytoai"
    exit 1
fi

CONTEXT=$1
DEPLOY_PATH="/data/front/$CONTEXT"
TEMP_DIR="/tmp/deploy-$CONTEXT"

echo "=== 开始部署前端: $CONTEXT ==="

# 读取项目配置
PROJECT_CONFIG=$(cat config/projects.json | grep -A 20 "\"context\": \"$CONTEXT\"" | head -20)

if [ -z "$PROJECT_CONFIG" ]; then
    echo "错误: 未找到项目 $CONTEXT 的配置"
    exit 1
fi

# 获取Git仓库地址
REPO_URL=$(cat config/projects.json | grep -A 5 "\"context\": \"$CONTEXT\"" | grep "repo" | cut -d'"' -f4)

echo "仓库: $REPO_URL"
echo "部署路径: $DEPLOY_PATH"

# 创建临时目录
mkdir -p $TEMP_DIR

# 克隆或更新代码
cd $TEMP_DIR
if [ -d "$CONTEXT" ]; then
    echo "更新代码..."
    cd $CONTEXT
    git pull
else
    echo "克隆仓库..."
    git clone $REPO_URL $CONTEXT
    cd $CONTEXT
fi

# 安装依赖并构建
echo "安装依赖..."
npm install

echo "构建项目..."
npm run build

# 上传到服务器
echo "上传到服务器..."
scp -r dist/* root@47.102.200.108:$DEPLOY_PATH/

echo "清理临时文件..."
cd /
rm -rf $TEMP_DIR

echo "=== 部署完成 ==="
echo "访问地址: https://linlan.net/$CONTEXT/"
