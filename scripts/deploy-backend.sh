#!/bin/bash

# 麟览技能市场 - 后端部署脚本
# 用法: ./deploy-backend.sh <项目上下文>
# 示例: ./deploy-backend.sh xiaolan_backend

if [ -z "$1" ]; then
    echo "用法: $0 <项目上下文>"
    echo "可用项目: xiaolan_backend, eframe_backend, wayto_backend"
    exit 1
fi

CONTEXT=$1
DEPLOY_PATH="/data/api/$CONTEXT"
TEMP_DIR="/tmp/deploy-$CONTEXT"

echo "=== 开始部署后端: $CONTEXT ==="

# 读取项目配置
PROJECT_CONFIG=$(cat config/projects.json | grep -A 20 "\"context\": \"$CONTEXT\"" | head -20)

if [ -z "$PROJECT_CONFIG" ]; then
    echo "错误: 未找到项目 $CONTEXT 的配置"
    exit 1
fi

# 获取Git仓库地址
REPO_URL=$(cat config/projects.json | grep -A 5 "\"context\": \"$CONTEXT\"" | grep "repo" | cut -d'"' -f4)
START_SCRIPT=$(cat config/projects.json | grep -A 10 "\"context\": \"$CONTEXT\"" | grep "startScript" | cut -d'"' -f4)

echo "仓库: $REPO_URL"
echo "部署路径: $DEPLOY_PATH"
echo "启动脚本: $START_SCRIPT"

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

# 上传到服务器
echo "上传到服务器..."
scp -r . root@47.102.200.108:$DEPLOY_PATH/

# 停止旧服务
echo "停止旧服务..."
ssh root@47.102.200.108 "pkill -f $CONTEXT"

# 修复启动脚本中的java路径
echo "修复java路径..."
ssh root@47.102.200.108 "sed -i 's|nohup java |nohup /data/jdk-17/bin/java |g' $DEPLOY_PATH/*.sh"

# 启动新服务
echo "启动新服务..."
ssh root@47.102.200.108 "cd $DEPLOY_PATH && ./$START_SCRIPT"

echo "清理临时文件..."
cd /
rm -rf $TEMP_DIR

echo "=== 部署完成 ==="
