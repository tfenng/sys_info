# 系统信息工具

这是一个基于 `psutil` 的轻量级 Python 命令行工具，用于快速查看当前机器的基础系统信息。现在入口分为两种模式：

- 交互模式：`python main.py`
- 子命令模式：`python main.py <sub-command>`

功能逻辑已拆分到多个扁平子模块，`main.py` 只负责总入口和分发。

## 功能概览

- CPU 核心数、线程数、频率与时间统计
- 内存使用情况
- 磁盘分区与根目录容量
- 网络 I/O 统计
- 当前在线用户
- 当前连接用户详情
- 系统启动时间与运行时长
- 磁盘 I/O 统计
- 网卡地址、状态与各网卡流量
- 网络连接状态汇总
- 进程 CPU / 内存 Top 10

## 环境要求

- Python 3.11 及以上
- 推荐使用 `uv` 管理依赖

## 安装依赖

```bash
uv sync
```

如果只想快速安装运行依赖，也可以使用：

```bash
uv pip install psutil
```

## 运行方式

运行主程序：

```bash
uv run python main.py
```

启动后默认进入系统概览页，可继续选择：

- `1`：用户详情
- `2`：负载详情
- `3`：磁盘详情
- `4`：网络详情
- `5`：网络接口（UP）
- `r`：刷新当前页面
- `q`：退出

直接通过子命令运行单项功能：

```bash
uv run python main.py overview
uv run python main.py users
uv run python main.py load
uv run python main.py disk
uv run python main.py network
uv run python main.py interfaces
uv run python main.py processes
```

也可以分别运行单个模块：

```bash
uv run python disk.py
uv run python load.py
uv run python net.py
uv run python processes.py
uv run python up_interfaces.py
uv run python users.py
```

## 项目结构

- `main.py`：统一入口，支持交互菜单与子命令分发
- `common.py`：公共格式化与输出辅助函数
- `load.py`：负载详情与 CPU / 内存 Top 10
- `disk.py`：磁盘容量与磁盘 I/O 统计
- `net.py`：查看网络收发统计和连接信息
- `up_interfaces.py`：查看当前处于 UP 状态的网络接口
- `processes.py`：列出当前运行中的进程
- `users.py`：查看当前在线用户详情

## 说明

本项目采用扁平目录结构，适合学习 `psutil` 的基础用法，也便于后续拆分为包结构或增加测试。
