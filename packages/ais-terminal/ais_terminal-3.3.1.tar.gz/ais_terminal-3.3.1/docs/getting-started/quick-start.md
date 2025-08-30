# 快速开始

欢迎使用 AIS！本指南将帮助您在 2 分钟内完成 AIS 的安装和基本配置，快速体验智能错误分析的强大功能。

## 🚀 2 分钟快速上手

### 第 1 步：一键安装
```bash
# 推荐：一键安装脚本（自动检测环境）
curl -sSL https://raw.githubusercontent.com/kangvcar/ais/main/scripts/install.sh | bash

# 国内用户可使用Gitee镜像（更快更稳定）
curl -sSL https://gitee.com/kangvcar/ais/raw/main/scripts/install.sh | bash

# 验证安装
ais --version
```

### 第 2 步：自动配置完成
```bash
# 一键安装脚本已自动配置：
# ✓ Shell 集成（自动错误分析）
# ✓ AI 服务（内置免费服务）
# ✓ 配置文件和数据库

# 验证配置
ais config
```

### 第 3 步：立即使用
```bash
# 测试 AI 问答
ais ask "如何使用 Docker 创建容器？"

# 测试错误分析（故意触发错误）
nonexistent-command
# AIS 会自动分析并提供解决方案

# 测试学习功能
ais learn git
```

### 手动安装（可选）
```bash
# 如果需要手动安装，可以使用：
pipx install ais-terminal

# 然后手动配置Shell集成
ais setup
source ~/.bashrc
```

## 🎯 核心功能快速体验

### 智能错误分析
```bash
# 1. 触发一个常见错误
docker run hello-world
# 如果 Docker 未安装，AIS 会自动分析并提供安装建议

# 2. 触发权限错误
sudo systemctl start nonexistent-service
# AIS 会分析服务不存在的问题并提供解决方案

# 3. 触发网络错误
curl https://nonexistent-domain.com
# AIS 会分析网络问题并提供诊断建议
```

### AI 问答助手
```bash
# 日常技术问题
ais ask "如何查看 Linux 系统的内存使用情况？"

# 编程相关问题
ais ask "Python 中如何处理异常？"

# 工具使用问题
ais ask "Git 如何回退到上一个版本？"

# 复杂问题
ais ask "如何优化 Web 应用的性能？"
```

### 系统化学习
```bash
# 学习 Docker 基础
ais learn docker

# 学习 Git 版本控制
ais learn git

# 学习 Python 编程
ais learn python

# 学习 Linux 系统管理
ais learn linux
```

### 学习报告
```bash
# 生成文本格式学习报告
ais report

# 生成HTML可视化报告
ais report --html

# 生成并打开HTML报告
ais report --html --open
```

## 📚 常用命令速查

### 基本操作
```bash
# 查看帮助
ais --help

# 查看版本
ais --version

# 测试系统集成
ais test-integration

# 开启/关闭自动分析
ais on
ais off
```

### AI 功能
```bash
# AI 问答
ais ask "你的问题"

# 手动错误分析
ais analyze --exit-code 1 --command "failed-command"

# 学习功能
ais learn 主题

# 生成报告
ais report
```

### 配置管理
```bash
# 查看配置
ais config

# 设置配置
ais config --set key=value

# 查看配置帮助
ais config --help-context
```

### 提供商管理
```bash
# 列出提供商
ais provider-list

# 切换提供商
ais provider-use 提供商名称

# 添加提供商
ais provider-add --help-detail
```

## 🔧 个性化配置

### 基本设置
```bash
# 设置上下文收集级别
ais config --set context_level=standard

# 开启/关闭自动分析
ais config --set auto_analysis=true

# 查看所有配置选项
ais config --help-context
```

### 隐私设置
```bash
# 查看当前敏感目录配置
ais config

# 敏感目录已默认配置：
# - ~/.ssh
# - ~/.config/ais
# - ~/.aws
```

### AI 提供商配置
```bash
# 添加OpenAI提供商
ais provider-add openai \
  --url https://api.openai.com/v1/chat/completions \
  --model gpt-4o-mini \
  --key YOUR_API_KEY

# 添加本地Ollama提供商
ais provider-add ollama \
  --url http://localhost:11434/v1/chat/completions \
  --model llama3

# 切换提供商
ais provider-use ollama
```

## 🎨 界面美化

### Rich 输出（内置）
```bash
# AIS 默认启用了 Rich 美化输出：
# ✓ 彩色输出和语法高亮
# ✓ 进度条和流式输出
# ✓ 表格格式和面板显示
# ✓ 交互式菜单

# 查看美化效果
ais ask "什么是Docker？"
ais history
```

### 流式输出（内置）
```bash
# AIS 默认启用了流式输出：
# ✓ 实时显示AI分析进度
# ✓ 渐进式内容显示
# ✓ 动态进度指示器

# 体验流式输出
ais learn git
```

## 💡 使用技巧

### 提高效率
1. **使用别名**：为常用命令创建别名
   ```bash
   alias aa='ais ask'
   alias al='ais learn'
   alias ar='ais report'
   alias ah='ais history'
   ```

2. **配置多个提供商**：为不同用途配置不同的 AI 提供商
   ```bash
   # 添加多个提供商
   ais provider-add openai --url ... --model gpt-4o-mini --key YOUR_KEY
   ais provider-add ollama --url http://localhost:11434/v1/chat/completions --model llama3
   
   # 根据需要切换
   ais provider-use openai    # 使用OpenAI
   ais provider-use ollama    # 使用本地Ollama
   ```

3. **查看详细帮助**：使用内置的详细帮助
   ```bash
   ais ask --help-detail
   ais learn --help-detail
   ais provider-add --help-detail
   ```

### 学习建议
1. **从错误中学习**：遇到错误时，先让 AIS 分析，再学习相关主题
2. **定期查看报告**：了解自己的学习进度和技能提升
3. **主动提问**：多使用 `ais ask` 来获取技术知识

### 隐私保护
1. **使用本地 AI**：Ollama 提供完全本地化的 AI 服务
2. **配置敏感信息过滤**：自动过滤密码和密钥
3. **定期清理数据**：删除不需要的历史记录

## 🔍 故障排除

### 常见问题
```bash
# 如果命令未找到
export PATH="$PATH:$HOME/.local/bin"

# 如果 Shell 集成不工作
ais setup
source ~/.bashrc

# 如果 AI 服务连接失败
ais provider-list
ais test-integration
```

### 获取帮助
```bash
# 查看详细帮助
ais --help
ais ask --help-detail

# 测试系统集成
ais test-integration

# 查看历史记录
ais history
```

## 🎉 成功！

恭喜您完成了 AIS 的快速配置！现在您可以：

✓ 自动分析命令执行错误
✓ 使用 AI 问答解决技术问题
✓ 系统化学习各种技术主题
✓ 跟踪学习进度和技能提升

## 📚 下一步

根据您的需求，建议继续阅读：

- [基本使用](./basic-usage) - 详细的使用指南
- [错误分析](../features/error-analysis) - 深入了解错误分析功能
- [AI 问答](../features/ai-chat) - 掌握 AI 问答技巧
- [学习系统](../features/learning-system) - 系统化学习指南
- [配置指南](../configuration/) - 个性化配置选项

---

::: tip 提示
AIS 会随着使用变得更加智能。建议在日常工作中持续使用，让 AIS 更好地了解您的需求。
:::

::: info 本地 AI
如果您担心隐私问题，强烈推荐使用 Ollama 本地 AI 模型，既免费又保护隐私。
:::

::: warning 注意
AIS 内置了免费的AI服务，安装后即可使用。如需更好的AI体验，可配置OpenAI或使用本地Ollama。
:::