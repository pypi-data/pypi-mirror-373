# MCP自动化工具集合

本项目包含两个独立的MCP工具包：
- **office-assistant-mcp**: 客群管理和短信营销自动化
- **commission-setting-mcp**: 佣金设置自动化

## 项目架构

```
office_assistant_mcp/
├── src/
│   ├── office_assistant_mcp/          # 客群短信业务
│   ├── commission_setting_mcp/        # 佣金设置业务  
│   └── shared/                        # 共享基础组件
├── pyproject.toml                     # office-assistant-mcp配置
├── pyproject_commission.toml          # commission-setting-mcp配置
├── build_and_upload_pypi.sh          # office包构建脚本
└── build_and_upload_commission.sh    # 佣金包构建脚本
```

## 包管理
使用uv

## 安装依赖
clone项目后，使用uv安装依赖：
```bash
uv sync
```

执行代码前激活虚拟环境：
```bash
source .venv/bin/activate
```

安装三方包:
```bash
uv add playwright==1.51.0
```

## Tools调试

### 客群短信业务调试
启动office-assistant-mcp调试工具：
```bash
uv run mcp dev src/office_assistant_mcp/mcp_server.py
```

### 佣金设置业务调试
启动commission-setting-mcp调试工具：
```bash
uv run mcp dev src/commission_setting_mcp/mcp_server.py
```

调试界面自动打开
页面配置：STDIO
uv
run --with mcp mcp run src/office_assistant_mcp/mcp_server.py

## 开发

为了能执行examples/下的文件，需要在根目录下安装office_assistant_mcp包：
```bash
uv pip install -e .
```

## 构建和发布

### Office Assistant MCP包

**手动构建：**
```bash
uv build
```

**自动构建和发布：**
```bash
./build_and_upload_pypi.sh
```
- 自动递增版本号
- 构建包文件
- 可选择上传到PyPI

### Commission Setting MCP包

**自动构建和发布：**
```bash
./build_and_upload_commission.sh
```
- 自动递增版本号
- 切换配置文件进行构建
- 恢复原配置文件
- 可选择上传到PyPI

### 包文件位置
构建的包文件存放在 `dist/` 目录下：
- office-assistant-mcp-x.x.x.tar.gz
- office-assistant-mcp-x.x.x-py3-none-any.whl
- commission-setting-mcp-x.x.x.tar.gz  
- commission-setting-mcp-x.x.x-py3-none-any.whl

## 功能模块

### Office Assistant MCP
- 客群创建和管理
- 用户行为标签设置
- 短信营销计划创建
- 飞书SSO登录

### Commission Setting MCP
- 佣金设置管理
- 更多功能开发中...




