# 开发者指南

欢迎参与 AIS 项目的开发！本指南将帮助您了解项目架构、开发流程和贡献方式。

## 🚀 快速开始

### 开发环境准备
```bash
# 克隆项目
git clone https://github.com/kangvcar/ais.git
cd ais

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/ -v
```

### 项目结构
```
ais/
├── src/ais/                  # 主要源代码
│   ├── commands/            # 命令行命令实现
│   ├── core/               # 核心功能模块
│   ├── ai/                 # AI 集成相关
│   ├── shell/              # Shell 集成
│   └── utils/              # 工具函数
├── tests/                   # 测试代码
├── docs/                   # 文档
├── scripts/                # 辅助脚本
└── pyproject.toml          # 项目配置
```

## 🏗️ 技术架构

### 核心组件
- **Click**: 命令行界面框架
- **Rich**: 终端美化和交互
- **SQLite**: 本地数据存储
- **Asyncio**: 异步处理
- **Pydantic**: 数据验证和序列化

### 模块说明
| 模块 | 描述 | 链接 |
|------|------|------|
| [架构设计](./architecture) | 详细的架构设计文档 | 🏗️ |
| [贡献指南](./contributing) | 参与项目贡献的指南 | 🤝 |
| [测试指南](./testing) | 测试框架和最佳实践 | 🧪 |

## 💻 开发流程

### 功能开发
1. 创建功能分支
2. 实现功能代码
3. 编写测试用例
4. 运行质量检查
5. 提交拉取请求

### 代码质量
```bash
# 代码格式化
black src/ tests/
autopep8 --in-place --aggressive --aggressive --max-line-length=100 src/ tests/ -r

# 代码检查
flake8 src/ tests/ --max-line-length=100

# 运行测试
pytest tests/ -v --cov=src/ais
```

## 🧪 测试

### 测试类型
- **单元测试**: 测试单个函数和类
- **集成测试**: 测试组件间的交互
- **端到端测试**: 测试完整的用户场景

### 运行测试
```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_commands.py

# 运行覆盖率测试
pytest tests/ --cov=src/ais --cov-report=html
```

## 📝 文档

### 文档类型
- **用户文档**: 使用指南和教程
- **API 文档**: 代码接口文档
- **开发文档**: 开发者指南

### 文档构建
```bash
# 安装文档依赖
pip install -e ".[docs]"

# 构建文档
cd docs
npm install
npm run build

# 本地预览
npm run dev
```

## 🔧 工具和脚本

### 开发脚本
```bash
# 设置开发环境
./scripts/setup-dev.sh

# 运行代码检查
./scripts/check-code.sh

# 发布新版本
./scripts/release.sh
```

### 调试工具
```bash
# 测试 AIS 集成
ais test-integration

# 性能分析
python -m cProfile -o profile.stats src/ais/main.py
```

## 🚢 部署

### 本地部署
```bash
# 构建分发包
python -m build

# 本地安装
pip install dist/ais-*.whl
```

### Docker 部署
```bash
# 构建 Docker 镜像
docker build -t ais:latest .

# 运行容器
docker run -it ais:latest
```

## 🤝 贡献方式

### 贡献类型
- **代码贡献**: 新功能、bug 修复
- **文档贡献**: 文档改进、翻译
- **测试贡献**: 测试用例、测试覆盖率
- **设计贡献**: UI/UX 改进

### 贡献流程
1. Fork 项目
2. 创建功能分支
3. 进行开发
4. 运行测试
5. 提交 PR

## 📊 项目统计

### 开发活跃度
- **提交频率**: 每周 10+ 提交
- **问题响应**: 24 小时内响应
- **PR 审查**: 48 小时内审查

### 代码质量
- **测试覆盖率**: 目标 80%+
- **代码质量**: 通过 flake8 检查
- **文档完整性**: 覆盖所有公共 API

## 🎯 开发路线图

### 近期目标
- [ ] 完善 AI 提供商支持
- [ ] 优化 Shell 集成稳定性
- [ ] 增强学习系统功能
- [ ] 改进错误分析准确性

### 长期目标
- [ ] 图形化用户界面
- [ ] 多语言支持
- [ ] 插件系统
- [ ] 云端同步

## 📚 学习资源

### 技术文档
- [Click 文档](https://click.palletsprojects.com/)
- [Rich 文档](https://rich.readthedocs.io/)
- [SQLite 文档](https://sqlite.org/docs.html)
- [Asyncio 文档](https://docs.python.org/3/library/asyncio.html)

### 开发最佳实践
- [Python 最佳实践](https://docs.python-guide.org/)
- [测试最佳实践](https://docs.pytest.org/en/stable/)
- [Git 工作流](https://www.atlassian.com/git/tutorials/comparing-workflows)

---

## 下一步

- [架构设计](./architecture) - 了解项目架构
- [贡献指南](./contributing) - 参与项目贡献
- [测试指南](./testing) - 了解测试流程

---

::: tip 提示
建议新贡献者先从简单的问题开始，熟悉项目结构和开发流程。
:::

::: info 交流
加入我们的开发者社区，与其他贡献者交流讨论。
:::

::: warning 注意
提交 PR 前，请确保通过所有测试和代码质量检查。
:::