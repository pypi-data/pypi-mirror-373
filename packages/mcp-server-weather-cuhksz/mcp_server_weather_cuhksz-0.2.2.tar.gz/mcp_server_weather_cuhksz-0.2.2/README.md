# MCP Weather 服务器 (`mcp_server_weather_cuhksz`)

该目录包含了基于和风天气 (QWeather) API、为 MCP 提供天气相关工具的 FastMCP 服务器实现。

一个基于和风天气 (QWeather) API、为语言模型提供天气相关工具的 FastMCP 服务器。

## 📋 目录

- [✨ 项目描述](#-项目描述)
- [🎯 核心功能](#-核心功能)
- [🛠️ 可用工具](#️-可用工具)
- [⚙️ 操作模式](#️-操作模式)
- [🚀 安装与部署](#-安装与部署)
- [🏗️ 项目架构](#️-项目架构)
- [🧪 测试说明](#-测试说明)
- [🔧 故障排除](#-故障排除)
- [📄 许可证](#-许可证)

## ✨ 项目描述

本项目基于 FastMCP 框架，将多个和风天气 API 端点封装为标准的 MCP 工具，使语言模型能够轻松地查询实时天气、天气预报、灾害预警和生活指数等信息。

## 🎯 核心功能

- **丰富工具集**: 提供从城市搜索到未来15天天气预报、逐小时预报、灾害预警等多种实用工具。
- **双重操作模式**: 支持直连和风天气 API 或通过 `unified-api` 代理服务运行，灵活适应不同部署需求。
- **动态配置**: 通过环境变量在运行时动态决定连接目标，无需修改代码即可切换模式。
- **容器化设计**: 提供完整的 Docker 和 Docker Compose 配置，实现一键部署和隔离环境。
- **内置缓存**: 对 API 请求结果进行缓存，提高响应速度并减少不必要的 API 调用。

## 🛠️ 可用工具

---

### 1. `get_location_id`
调用和风天气城市搜索，返回含 Location ID 的详细地点列表。**注意⚠️: 在调用其他需要地理位置的工具前，必须先调用此工具获取 Location ID。**

- **参数说明**:
  - `location` (`string`): **必须**。查询关键字，可以是城市名称、`经度,纬度`、LocationID 或 Adcode（中国行政区划代码）。例如 `"北京"` 或 `"116.41,39.92"`。
  - `adm` (`string`): *可选*。上级行政区过滤，如 `"beijing"` 或 `"江西省"`。
  - `search_range` (`string`): *可选*。搜索范围，ISO 3166 国家/地区代码，如 `"cn"`。
  - `number` (`int`): *可选*。返回数量，取值范围 1-20，默认为 `1`。
  - `lang` (`string`): *可选*。语言设置，支持 `'zh'` (默认) 或 `'en'`。

---

### 2. `get_daily_weather`
获取指定地点未来多天的逐日天气预报。

- **参数说明**:
  - `days` (`string`): **必须**。预报天数，可选值为 `'3d'`, `'7d'`, `'10d'`, `'15d'`, `'30d'`。
  - `location` (`string`): **必须**。地理位置参数，必须是 `get_location_id` 返回的 LocationID 或 `经度,纬度` 格式。例如 `"101010100"`。
  - `lang` (`string`): *可选*。语言设置，支持 `'zh'` (默认) 或 `'en'`。
  - `unit` (`string`): *可选*。单位制，支持 `'m'` (公制，默认) 或 `'i'` (英制)。

---

### 3. `get_hourly_weather`
获取指定地点未来多小时的逐小时天气预报。

- **参数说明**:
  - `hours` (`string`): **必须**。预报小时数，可选值为 `'24h'`, `'72h'`, `'168h'`。
  - `location` (`string`): **必须**。地理位置参数，同上。
  - `lang` (`string`): *可选*。语言设置，支持 `'zh'` (默认) 或 `'en'`。
  - `unit` (`string`): *可选*。单位制，支持 `'m'` (公制，默认) 或 `'i'` (英制)。

---

### 4. `get_weather_warning_now`
查询指定地点的实时气象灾害预警信息。

- **参数说明**:
  - `location` (`string`): **必须**。地理位置参数，同上。
  - `lang` (`string`): *可选*。语言设置，支持 `'zh'` (默认) 或 `'en'`。

---

### 5. `get_weather_indices`
查询指定地点的天气生活指数。

- **参数说明**:
  - `days` (`string`): **必须**。预报天数，可选值为 `'1d'` 或 `'3d'`。
  - `location` (`string`): **必须**。地理位置参数，同上。
  - `lang` (`string`): *可选*。语言设置，支持 `'zh'` (默认) 或 `'en'`。

## ⚙️ 操作模式

服务器可在以下两种模式之一运行，由 `IS_UNIFIED_API` 环境变量控制。

### 1. 统一 API 代理模式 (Unified API Proxy Mode) - 推荐

- **描述**: 在此模式下，服务器作为 `unified-api` 代理服务的客户端。它将所有天气 API 请求转发到该代理，由代理负责账户选择、负载均衡和认证。这是**生产环境或多账户部署场景下的推荐模式**。
- **配置 (`IS_UNIFIED_API=true`)**:
  - `IS_UNIFIED_API`: 必须设置为 `true`。
  - `UNIFIED_API_HOST`: `unified-api` 服务的 URL (例如 `http://unified-api:6380` 或 `http://host.docker.internal:6380`)。

### 2. 直连 API 模式 (Direct API Mode)

- **描述**: 在此模式下，服务器直接连接到和风天气 API，并使用本地配置的凭证生成 JWT 进行认证。此模式适用于本地开发和独立测试。
- **配置 (`IS_UNIFIED_API=false`)**:
  - `IS_UNIFIED_API`: 必须设置为 `false`。
  - `WEATHER_API_HOST`: 和风天气 API 的 URL (例如, `https://api.qweather.com`)。
  - `QWEATHER_KEY_ID`, `QWEATHER_PROJECT_ID`, `QWEATHER_PRIVATE_KEY`: 您的和风天气凭证。

## 🚀 安装与部署

本项目设计为在 Docker 环境中运行。

### 1. 集成部署 (统一 API 代理模式) - 推荐

此方法会同时启动 `mcp-server`、`unified-api` 和 `redis` 服务，是完整的生产和测试部署方案。

**a. 环境准备**

- 安装 [Docker](https://www.docker.com/get-started/) 和 [Docker Compose](https://docs.docker.com/compose/install/)。
- 确保项目根目录下的 `.env` 文件和 `unified_api/` 目录下的配置文件已准备就绪。

**b. 启动服务**

在**项目根目录**下执行：
```bash
# 构建并以守护进程模式启动所有服务
docker-compose up --build -d

# 查看 mcp-server 的实时日志
docker-compose logs -f mcp-server

# 停止所有服务
docker-compose down
```
服务启动后，将在 `http://localhost:3003` 上提供 MCP 接口。根 `docker-compose.yml` 会自动设置 `IS_UNIFIED_API=true`。

### 2. 独立部署 (直连 API 模式)

此方法仅用于单独运行和测试 `mcp-server`。

**a. 配置凭证**

在 `src/mcp_server_weather_cuhksz/` 目录下创建一个 `.env` 文件，并填入“直连 API 模式”所需的 `QWEATHER_*` 变量。

**b. 启动服务**

从 `src/mcp_server_weather_cuhksz/` 目录**内部**执行：
```bash
docker-compose up --build -d
```

## 🏗️ 项目架构

### 模块关系

本项目由两个核心服务组成：
- **`mcp-server-weather` (本项目)**: 作为 MCP 层，将业务逻辑（天气查询）封装为语言模型可调用的工具。
- **`unified-api`**: 作为代理和认证层，管理多个和风天气账户，实现负载均衡和统一的 API 访问入口。

### 关键设计：运行时动态配置

为了确保配置的灵活性和可靠性，本项目采用以下策略：
1.  **集中化配置入口**: 所有配置逻辑都集中在主入口 `__main__.py` 中，由它根据环境变量决定最终的操作模式和 API Host。
2.  **运行时动态解析**: 核心逻辑模块 `mcp_weather.py` 中的工具函数在被调用时，才通过 `os.getenv(...)` 动态获取配置。这确保了工具总是使用最新的、由容器编排工具注入的正确配置，避免了因 Python 模块导入时序问题导致的配置固化。

这种设计确保了由 Docker Compose 注入的配置始终拥有最高优先级，使得服务行为在不同部署环境中一致且可靠。

## 🧪 测试说明

项目提供了一个自动化测试脚本 `test/test.py`，用于验证所有 MCP 工具的基本功能。

### 运行测试

1.  **启动服务**: 确保服务已通过 `docker-compose up -d` (在项目根目录) 成功启动。
2.  **执行脚本**: 在您的本地 Python 环境中（需要安装 `fastmcp` 客户端库），运行测试：
    ```bash
    # 建议在项目的虚拟环境中运行
    python test/test.py
    ```
脚本会自动连接 `http://localhost:3003` 的服务，发现并调用所有可用工具，然后打印出结果或错误信息。

## 🔧 故障排除

### 常见问题

#### 1. 工具调用时出现 `Name or service not known` 错误
- **症状**: `test/test.py` 或其他客户端调用工具时，返回类似 `[Errno -2] Name or service not known` 的网络错误。
- **原因**: `mcp-server` 容器无法通过其配置的 `UNIFIED_API_HOST` 地址连接到 `unified-api` 服务。
- **解决方案**:
  - 检查根 `docker-compose.yml` 文件中 `mcp-server` 服务的 `UNIFIED_API_HOST` 环境变量。
  - 对于 Docker for Mac/Windows，推荐使用 `http://host.docker.internal:6380`，它会指向宿主机的网络。
  - 如果在 Linux 上，您可能需要配置 `extra_hosts` 或确保两个服务在同一个自定义的 bridge network 中，并使用服务名 `http://unified-api:6380` 进行通信。

#### 2. `unified-api` 服务健康检查失败
- **症状**: `docker-compose up` 过程中 `mcp-server` 等待 `unified-api` 超时。
- **原因**: `unified-api` 容器未能正常启动。可能是 `accounts.yaml` 配置错误、私钥文件缺失或路径不正确。
- **解决方案**: 使用 `docker-compose logs unified-api` 查看其详细日志，定位并修复问题。

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。
