#!/bin/bash
# 超轻量化日志查询脚本
# 基于Zap + Docker原生日志驱动

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 使用说明
usage() {
    echo "用法: $0 [命令] [服务名]"
    echo ""
    echo "命令:"
    echo "  tail [服务名]      - 实时查看日志"
    echo "  error [服务名]     - 查看ERROR级别日志"
    echo "  search [关键词]    - 搜索日志内容"
    echo "  json [服务名]      - 查看JSON格式日志"
    echo "  stats [服务名]     - 日志统计"
    echo ""
    echo "示例:"
    echo "  $0 tail app        # 查看app服务日志"
    echo "  $0 error app       # 查看app服务ERROR日志"
    echo "  $0 search '失败'   # 搜索包含'失败'的日志"
    echo "  $0 json app        # 查看app服务JSON格式日志"
}

# 检查依赖
check_deps() {
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}错误: jq未安装，请先安装jq${NC}"
        echo "安装命令: brew install jq (macOS) 或 apt-get install jq (Ubuntu)"
        exit 1
    fi
}

# 获取服务列表
get_services() {
    echo "可用的服务:"
    if [ -d "/var/log/docker" ]; then
        ls -1 /var/log/docker/*.log 2>/dev/null | sed 's/.*\/\([^\/]*\)\.log/  - \1/' || echo "  无日志文件"
    else
        echo "  使用docker-compose服务名"
    fi
}

# 实时查看日志
tail_logs() {
    local service=${1:-app}
    echo -e "${GREEN}实时查看 ${service} 服务日志...${NC}"
    
    if [ -f "/var/log/docker/${service}.log" ]; then
        tail -f "/var/log/docker/${service}.log" | jq -C '.'
    else
        docker-compose logs -f "$service"
    fi
}

# 查看ERROR级别日志
error_logs() {
    local service=${1:-app}
    echo -e "${RED}查看 ${service} 服务ERROR级别日志...${NC}"
    
    if [ -f "/var/log/docker/${service}.log" ]; then
        grep '"level":"ERROR"' "/var/log/docker/${service}.log" | jq -C '.'
    else
        docker-compose logs "$service" | grep -i error
    fi
}

# 搜索日志内容
search_logs() {
    local keyword=$1
    if [ -z "$keyword" ]; then
        echo -e "${RED}错误: 请提供搜索关键词${NC}"
        usage
        exit 1
    fi
    
    echo -e "${YELLOW}搜索包含 '${keyword}' 的日志...${NC}"
    
    if [ -d "/var/log/docker" ]; then
        grep -i "$keyword" /var/log/docker/*.log | jq -C '.'
    else
        docker-compose logs | grep -i "$keyword"
    fi
}

# 查看JSON格式日志
json_logs() {
    local service=${1:-app}
    echo -e "${BLUE}查看 ${service} 服务JSON格式日志...${NC}"
    
    if [ -f "/var/log/docker/${service}.log" ]; then
        cat "/var/log/docker/${service}.log" | jq -C '.'
    else
        echo "JSON格式日志仅在文件模式下可用"
    fi
}

# 日志统计
stats_logs() {
    local service=${1:-app}
    echo -e "${GREEN}${service} 服务日志统计...${NC}"
    
    if [ -f "/var/log/docker/${service}.log" ]; then
        local total=$(wc -l < "/var/log/docker/${service}.log")
        local errors=$(grep -c '"level":"ERROR"' "/var/log/docker/${service}.log" 2>/dev/null || echo 0)
        local warns=$(grep -c '"level":"WARN"' "/var/log/docker/${service}.log" 2>/dev/null || echo 0)
        local infos=$(grep -c '"level":"INFO"' "/var/log/docker/${service}.log" 2>/dev/null || echo 0)
        
        echo "总日志数: $total"
        echo -e "ERROR: ${RED}$errors${NC}"
        echo -e "WARN:  ${YELLOW}$warns${NC}"
        echo -e "INFO:  ${GREEN}$infos${NC}"
    else
        echo "统计信息仅在文件模式下可用"
    fi
}

# 主程序
main() {
    check_deps
    
    if [ $# -eq 0 ]; then
        usage
        get_services
        exit 0
    fi
    
    case "$1" in
        tail)
            tail_logs "$2"
            ;;
        error)
            error_logs "$2"
            ;;
        search)
            search_logs "$2"
            ;;
        json)
            json_logs "$2"
            ;;
        stats)
            stats_logs "$2"
            ;;
        *)
            echo -e "${RED}未知命令: $1${NC}"
            usage
            exit 1
            ;;
    esac
}

# 执行主程序
main "$@"