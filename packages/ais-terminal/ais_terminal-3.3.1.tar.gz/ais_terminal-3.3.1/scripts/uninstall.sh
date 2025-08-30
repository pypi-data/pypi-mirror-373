#!/bin/bash
# AIS - 上下文感知的错误分析学习助手
# 智能卸载脚本 - 自动检测安装方式并完全清理
# 
# 使用方法: curl -sSL https://raw.githubusercontent.com/kangvcar/ais/main/scripts/uninstall.sh | bash

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印彩色消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}✗  $1${NC}"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检测安装方式
detect_installation_method() {
    local method=""
    
    # 检查pipx用户级安装
    if command_exists pipx && pipx list | grep -q "ais-terminal"; then
        method="pipx-user"
    # 检查pipx系统级安装
    elif [ -d "/opt/pipx" ] && [ -f "/usr/local/bin/ais" ]; then
        method="pipx-system"
    # 检查编译安装的Python 3.10.9环境（修复路径）
    elif [ -x "/usr/local/bin/python3.10" ] && /usr/local/bin/python3.10 -m pip show ais-terminal >/dev/null 2>&1; then
        method="compiled-python310"
    # 检查编译安装的Python 3.9环境
    elif [ -x "/usr/local/bin/python3.9" ] && /usr/local/bin/python3.9 -m pip show ais-terminal >/dev/null 2>&1; then
        method="compiled-python39"
    # 检查python3.9升级安装
    elif command_exists python3.9 && python3.9 -m pip show ais-terminal >/dev/null 2>&1; then
        method="python-upgrade"
    # 检查pip安装
    elif python3 -m pip list 2>/dev/null | grep -q "ais-terminal"; then
        method="pip"
    # 检查系统级安装（旧方式）
    elif [ -f "/usr/local/bin/ais" ] && [ -d "/opt/ais" ]; then
        method="system-old"
    # 检查Docker容器
    elif [ -n "${CONTAINER}" ] || [ -n "${container}" ] || [ -f /.dockerenv ]; then
        method="container"
    else
        method="unknown"
    fi
    
    echo "$method"
}

# pipx用户级卸载
uninstall_pipx_user() {
    print_info "🔄 卸载pipx用户级安装..."
    
    if command_exists pipx; then
        pipx uninstall ais-terminal 2>/dev/null || print_warning "pipx卸载失败，可能已经被移除"
        print_success "pipx用户级卸载完成"
    else
        print_warning "pipx命令不存在，跳过pipx卸载"
    fi
}

# pipx系统级卸载
uninstall_pipx_system() {
    print_info "🔄 卸载pipx系统级安装..."
    
    # 尝试使用pipx卸载
    if command_exists pipx; then
        if [ "$EUID" -eq 0 ]; then
            PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx uninstall ais-terminal 2>/dev/null || true
        else
            sudo PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx uninstall ais-terminal 2>/dev/null || true
        fi
    fi
    
    # 手动清理系统文件
    if [ "$EUID" -eq 0 ]; then
        rm -f /usr/local/bin/ais
        rm -rf /opt/pipx/venvs/ais-terminal 2>/dev/null || true
        rm -f /etc/profile.d/ais.sh  # 清理全局Shell集成
    else
        sudo rm -f /usr/local/bin/ais
        sudo rm -rf /opt/pipx/venvs/ais-terminal 2>/dev/null || true
        sudo rm -f /etc/profile.d/ais.sh  # 清理全局Shell集成
    fi
    
    print_success "pipx系统级卸载完成"
}

# pip卸载
uninstall_pip() {
    print_info "🔄 卸载pip安装..."
    
    # 尝试pip卸载
    python3 -m pip uninstall -y ais-terminal 2>/dev/null || print_warning "pip卸载失败"
    
    print_success "pip卸载完成"
}

# 系统级卸载（旧方式）
uninstall_system_old() {
    print_info "🔄 卸载旧的系统级安装..."
    
    if [ "$EUID" -eq 0 ]; then
        rm -f /usr/local/bin/ais
        rm -rf /opt/ais
        rm -rf /etc/ais
        rm -f /etc/profile.d/ais.sh  # 清理全局Shell集成
    else
        sudo rm -f /usr/local/bin/ais
        sudo rm -rf /opt/ais
        sudo rm -rf /etc/ais
        sudo rm -f /etc/profile.d/ais.sh  # 清理全局Shell集成
    fi
    
    print_success "旧系统级安装卸载完成"
}

# 容器卸载
uninstall_container() {
    print_info "🐳 容器环境卸载..."
    
    # pip卸载
    python3 -m pip uninstall -y ais-terminal 2>/dev/null || true
    
    # 清理可能的全局命令
    rm -f /usr/local/bin/ais 2>/dev/null || true
    
    print_success "容器环境卸载完成"
}

# 卸载编译安装的Python 3.10.9环境
uninstall_compiled_python310() {
    print_info "🔄 卸载编译安装的Python 3.10.9环境..."
    
    # 卸载AIS包（修复路径）
    if [ -x "/usr/local/bin/python3.10" ]; then
        /usr/local/bin/python3.10 -m pip uninstall -y ais-terminal 2>/dev/null || print_warning "pip卸载失败"
    fi
    
    # 清理AIS命令和包装脚本
    if [ "$EUID" -eq 0 ]; then
        rm -f /usr/local/bin/ais 2>/dev/null || true
    else
        sudo rm -f /usr/local/bin/ais 2>/dev/null || true
    fi
    
    # 清理临时构建文件
    rm -rf /tmp/python_build 2>/dev/null || true
    rm -f /tmp/ais_install_*.log 2>/dev/null || true
    
    # 询问是否删除编译安装的Python环境
    echo
    print_warning "⚠️  检测到编译安装的Python 3.10.9环境"
    print_info "位置: /usr/local/ (包含bin/python3.10, lib/python3.10等)"
    
    local remove_python=0
    if [ -t 0 ]; then
        read -p "是否同时删除编译安装的Python 3.10.9环境? (y/N): "
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            remove_python=1
        fi
    else
        echo -n "是否同时删除编译安装的Python 3.10.9环境? (y/N): "
        read -r REPLY < /dev/tty
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            remove_python=1
        fi
    fi
    
    if [ $remove_python -eq 1 ]; then
        print_info "正在删除Python 3.10.9环境..."
        if [ "$EUID" -eq 0 ]; then
            # 删除编译安装的Python文件
            rm -f /usr/local/bin/python3.10 2>/dev/null || true
            rm -f /usr/local/bin/pip3.10 2>/dev/null || true
            rm -rf /usr/local/lib/python3.10 2>/dev/null || true
            rm -rf /usr/local/include/python3.10 2>/dev/null || true
            rm -rf /usr/local/share/man/man1/python3.10* 2>/dev/null || true
        else
            sudo rm -f /usr/local/bin/python3.10 2>/dev/null || true
            sudo rm -f /usr/local/bin/pip3.10 2>/dev/null || true
            sudo rm -rf /usr/local/lib/python3.10 2>/dev/null || true
            sudo rm -rf /usr/local/include/python3.10 2>/dev/null || true
            sudo rm -rf /usr/local/share/man/man1/python3.10* 2>/dev/null || true
        fi
        print_success "Python 3.10.9环境已删除"
    else
        print_info "保留Python 3.10.9环境"
    fi
    
    print_success "编译安装的Python 3.10.9环境卸载完成"
}

# 卸载编译安装的Python 3.9环境
uninstall_compiled_python39() {
    print_info "🔄 卸载编译安装的Python 3.9环境..."
    
    # 卸载AIS包
    if [ -x "/usr/local/bin/python3.9" ]; then
        /usr/local/bin/python3.9 -m pip uninstall -y ais-terminal 2>/dev/null || print_warning "pip卸载失败"
    fi
    
    # 清理软链接
    if [ "$EUID" -eq 0 ]; then
        rm -f /usr/local/bin/ais 2>/dev/null || true
    else
        sudo rm -f /usr/local/bin/ais 2>/dev/null || true
    fi
    
    # 询问是否删除编译安装的Python环境
    echo
    print_warning "⚠️  检测到编译安装的Python 3.9环境"
    print_info "位置: /usr/local/ (包含bin/python3.9, lib/python3.9等)"
    
    local remove_python=0
    if [ -t 0 ]; then
        read -p "是否同时删除编译安装的Python 3.9环境? (y/N): "
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            remove_python=1
        fi
    else
        echo -n "是否同时删除编译安装的Python 3.9环境? (y/N): "
        read -r REPLY < /dev/tty
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            remove_python=1
        fi
    fi
    
    if [ $remove_python -eq 1 ]; then
        print_info "正在删除Python 3.9环境..."
        if [ "$EUID" -eq 0 ]; then
            rm -f /usr/local/bin/python3.9 2>/dev/null || true
            rm -f /usr/local/bin/pip3.9 2>/dev/null || true
            rm -rf /usr/local/lib/python3.9 2>/dev/null || true
            rm -rf /usr/local/include/python3.9 2>/dev/null || true
            rm -rf /usr/local/share/man/man1/python3.9* 2>/dev/null || true
        else
            sudo rm -f /usr/local/bin/python3.9 2>/dev/null || true
            sudo rm -f /usr/local/bin/pip3.9 2>/dev/null || true
            sudo rm -rf /usr/local/lib/python3.9 2>/dev/null || true
            sudo rm -rf /usr/local/include/python3.9 2>/dev/null || true
            sudo rm -rf /usr/local/share/man/man1/python3.9* 2>/dev/null || true
        fi
        print_success "Python 3.9环境已删除"
    else
        print_info "保留Python 3.9环境"
    fi
    
    print_success "编译安装的Python 3.9环境卸载完成"
}

# 卸载Python升级安装（python_upgrade策略）
uninstall_python_upgrade() {
    print_info "🔄 卸载Python升级安装..."
    
    # 卸载AIS包
    if command_exists python3.9; then
        python3.9 -m pip uninstall -y ais-terminal 2>/dev/null || print_warning "pip卸载失败"
    fi
    
    # 清理AIS命令
    if [ "$EUID" -eq 0 ]; then
        rm -f /usr/local/bin/ais 2>/dev/null || true
    else
        sudo rm -f /usr/local/bin/ais 2>/dev/null || true
    fi
    
    print_success "Python升级安装卸载完成"
}

# 清理用户配置和数据
cleanup_user_data() {
    print_info "🧹 清理用户配置和数据..."
    
    local cleaned=0
    
    # 清理配置目录
    if [ -d "$HOME/.config/ais" ]; then
        rm -rf "$HOME/.config/ais"
        print_info "  已清理: ~/.config/ais"
        cleaned=1
    fi
    
    # 清理数据目录
    if [ -d "$HOME/.local/share/ais" ]; then
        rm -rf "$HOME/.local/share/ais"
        print_info "  已清理: ~/.local/share/ais"
        cleaned=1
    fi
    
    # 清理缓存目录
    if [ -d "$HOME/.cache/ais" ]; then
        rm -rf "$HOME/.cache/ais"
        print_info "  已清理: ~/.cache/ais"
        cleaned=1
    fi
    
    # 清理pipx本地安装路径（用户级）
    if [ -d "$HOME/.local/share/pipx/venvs/ais-terminal" ]; then
        rm -rf "$HOME/.local/share/pipx/venvs/ais-terminal"
        print_info "  已清理: ~/.local/share/pipx/venvs/ais-terminal"
        cleaned=1
    fi
    
    if [ $cleaned -eq 1 ]; then
        print_success "用户数据清理完成"
    else
        print_info "未找到用户数据，跳过清理"
    fi
}

# 清理临时文件和日志
cleanup_temp_files() {
    print_info "🗑️ 清理临时文件和日志..."
    
    local cleaned=0
    
    # 清理编译临时目录
    if [ -d "/tmp/python_build" ]; then
        rm -rf /tmp/python_build
        print_info "  已清理: /tmp/python_build"
        cleaned=1
    fi
    
    # 清理安装日志
    rm -f /tmp/ais_install_*.log 2>/dev/null && {
        print_info "  已清理: /tmp/ais_install_*.log"
        cleaned=1
    }
    
    # 清理其他可能的临时文件
    rm -f /tmp/ais_install_error_* 2>/dev/null && {
        print_info "  已清理: /tmp/ais_install_error_*"
        cleaned=1
    }
    
    if [ $cleaned -eq 1 ]; then
        print_success "临时文件清理完成"
    else
        print_info "未找到临时文件，跳过清理"
    fi
}

# 清理Shell集成
cleanup_shell_integration() {
    print_info "🔧 清理Shell集成..."
    
    local cleaned=0
    
    # 清理bashrc
    if [ -f "$HOME/.bashrc" ]; then
        # 清理旧版集成格式
        if grep -q "START AIS INTEGRATION" "$HOME/.bashrc"; then
            sed -i '/# START AIS INTEGRATION/,/# END AIS INTEGRATION/d' "$HOME/.bashrc"
            print_info "  已清理旧版集成: ~/.bashrc"
            cleaned=1
        fi
        # 清理新版集成格式
        if grep -q "AIS INTEGRATION" "$HOME/.bashrc"; then
            sed -i '/# AIS INTEGRATION/,/^$/d' "$HOME/.bashrc"
            print_info "  已清理新版集成: ~/.bashrc"
            cleaned=1
        fi
        # 清理其他可能的AIS相关配置
        if grep -q "ais shell-integration" "$HOME/.bashrc"; then
            sed -i '/command -v ais.*ais shell-integration/d' "$HOME/.bashrc"
            print_info "  已清理shell-integration: ~/.bashrc"
            cleaned=1
        fi
    fi
    
    # 清理zshrc
    if [ -f "$HOME/.zshrc" ]; then
        # 清理旧版集成格式
        if grep -q "START AIS INTEGRATION" "$HOME/.zshrc"; then
            sed -i '/# START AIS INTEGRATION/,/# END AIS INTEGRATION/d' "$HOME/.zshrc"
            print_info "  已清理旧版集成: ~/.zshrc"
            cleaned=1
        fi
        # 清理新版集成格式
        if grep -q "AIS INTEGRATION" "$HOME/.zshrc"; then
            sed -i '/# AIS INTEGRATION/,/^$/d' "$HOME/.zshrc"
            print_info "  已清理新版集成: ~/.zshrc"
            cleaned=1
        fi
        # 清理其他可能的AIS相关配置
        if grep -q "ais shell-integration" "$HOME/.zshrc"; then
            sed -i '/command -v ais.*ais shell-integration/d' "$HOME/.zshrc"
            print_info "  已清理shell-integration: ~/.zshrc"
            cleaned=1
        fi
    fi
    
    # 清理fish配置
    if [ -f "$HOME/.config/fish/config.fish" ]; then
        if grep -q "START AIS INTEGRATION" "$HOME/.config/fish/config.fish"; then
            sed -i '/# START AIS INTEGRATION/,/# END AIS INTEGRATION/d' "$HOME/.config/fish/config.fish"
            print_info "  已清理: ~/.config/fish/config.fish"
            cleaned=1
        fi
        if grep -q "AIS INTEGRATION" "$HOME/.config/fish/config.fish"; then
            sed -i '/# AIS INTEGRATION/,/^$/d' "$HOME/.config/fish/config.fish"
            print_info "  已清理新版集成: ~/.config/fish/config.fish"
            cleaned=1
        fi
    fi
    
    if [ $cleaned -eq 1 ]; then
        print_success "Shell集成清理完成"
    else
        print_info "未找到Shell集成，跳过清理"
    fi
}

# 验证卸载结果
verify_uninstall() {
    print_info "🔍 验证卸载结果..."
    
    local issues=0
    
    # 检查ais命令
    if command_exists ais; then
        print_warning "ais命令仍然存在: $(which ais)"
        issues=$((issues + 1))
    fi
    
    # 检查常见安装位置
    if [ -f "/usr/local/bin/ais" ]; then
        print_warning "全局ais命令仍然存在: /usr/local/bin/ais"
        issues=$((issues + 1))
    fi
    
    # 检查pipx安装
    if command_exists pipx && pipx list | grep -q "ais-terminal"; then
        print_warning "pipx中仍有ais-terminal包"
        issues=$((issues + 1))
    fi
    
    if [ $issues -eq 0 ]; then
        print_success "卸载验证通过，所有组件已清理"
    else
        print_warning "发现 $issues 个残留项目，可能需要手动清理"
    fi
    
    return $issues
}

# 主卸载函数
main() {
    echo "================================================"
    echo "        AIS - 上下文感知的错误分析学习助手 卸载器"
    echo "================================================"
    echo "自动检测安装方式并完全清理"
    echo
    
    # 检测安装方式
    METHOD=$(detect_installation_method)
    print_info "🔍 检测到安装方式: $METHOD"
    
    # 确认卸载
    echo
    print_warning "⚠️  即将卸载AIS及其所有配置和数据"
    if [ -t 0 ]; then
        # 标准输入是终端，可以正常读取用户输入
        read -p "继续卸载吗? (y/N): " -r
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "已取消卸载"
            exit 0
        fi
    else
        # 从管道执行，使用/dev/tty读取用户输入
        echo -n "继续卸载吗? (y/N): "
        read -r REPLY < /dev/tty
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "已取消卸载"
            exit 0
        fi
    fi
    
    echo
    print_info "🚀 开始卸载AIS..."
    
    # 根据检测到的方式执行卸载
    case "$METHOD" in
        "pipx-user")
            uninstall_pipx_user
            ;;
        "pipx-system")
            uninstall_pipx_system
            ;;
        "compiled-python310")
            uninstall_compiled_python310
            ;;
        "compiled-python39")
            uninstall_compiled_python39
            ;;
        "python-upgrade")
            uninstall_python_upgrade
            ;;
        "pip")
            uninstall_pip
            ;;
        "system-old")
            uninstall_system_old
            ;;
        "container")
            uninstall_container
            ;;
        "unknown")
            print_warning "未检测到AIS安装，尝试清理可能的残留文件..."
            # 尝试所有卸载方式
            uninstall_pipx_user 2>/dev/null || true
            uninstall_pipx_system 2>/dev/null || true
            uninstall_compiled_python310 2>/dev/null || true
            uninstall_compiled_python39 2>/dev/null || true
            uninstall_python_upgrade 2>/dev/null || true
            uninstall_pip 2>/dev/null || true
            uninstall_system_old 2>/dev/null || true
            ;;
    esac
    
    # 清理用户数据和配置
    cleanup_user_data
    cleanup_shell_integration
    cleanup_temp_files
    
    echo
    # 验证卸载结果
    verify_uninstall
    
    echo
    print_success "🎉 AIS卸载完成！"
    print_info "💡 如需重新安装，请运行:"
    print_info "   curl -sSL https://raw.githubusercontent.com/kangvcar/ais/main/scripts/install.sh | bash"
    
    echo
    print_warning "🔄 建议重新加载Shell配置或重新打开终端"
}

# 处理命令行参数
case "${1:-}" in
    --help|-h)
        echo "AIS 智能卸载脚本"
        echo
        echo "用法: $0"
        echo
        echo "功能:"
        echo "  自动检测AIS安装方式"
        echo "  完全清理所有相关文件和配置"
        echo "  清理Shell集成"
        echo "  验证卸载结果"
        echo
        echo "支持的安装方式:"
        echo "  - pipx用户级安装 (pipx-user)"
        echo "  - pipx系统级安装 (pipx-system)"
        echo "  - 编译安装的Python 3.10.9环境 (compiled-python310)"
        echo "  - 编译安装的Python 3.9环境 (compiled-python39)"
        echo "  - Python升级安装 (python-upgrade)"
        echo "  - pip直接安装 (pip)"
        echo "  - 系统级安装（旧方式）(system-old)"
        echo "  - 容器安装 (container)"
        exit 0
        ;;
    --force)
        print_info "强制卸载模式"
        # 在强制模式下跳过确认
        REPLY="y"
        ;;
esac

# 运行主函数
main