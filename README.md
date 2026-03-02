<<<<<<< HEAD
# 简易端口扫描器（Python）

面向入门级资产探测学习场景的轻量端口扫描工具，支持多线程 TCP 连接扫描，提供可选 UDP 响应检查、服务识别、批量 IP 扫描与结果导出。

## 功能特性

- 多线程 TCP 端口扫描（可配置线程数、超时）
- 可选 UDP 响应扫描（基于是否收到返回数据进行保守判定）
- 服务识别（getservbyport，无法识别时标记为 Unknown）
- 支持单 IP 与批量 IP（从文件读取）
- 扫描进度提示（每 100 个端口或完成时打印）
- 输出到控制台并写入结果文件（默认 result.txt）

## 环境要求

- Python 3.8 及以上
- 标准库即可，无需额外依赖（socket、argparse、threading 等）

## 快速开始

克隆/下载代码后，进入项目目录，直接运行：

```bash
python port_scanner.py
```

按提示依次输入目标 IP、端口范围、是否启用 UDP 和线程数即可开始扫描。

也可直接使用命令行参数：

```bash
# 单 IP，扫描 1-1000 端口（TCP）
python port_scanner.py --ip 192.168.1.10 --start-port 1 --end-port 1000

# 启用 UDP 联合扫描
python port_scanner.py --ip 192.168.1.10 --start-port 1 --end-port 1000 --udp

# 批量 IP 扫描（ip_list.txt 每行一个 IP）
python port_scanner.py --ip-list ip_list.txt --start-port 1 --end-port 1000

# 调整线程数与超时，指定输出文件
python port_scanner.py --ip 192.168.1.10 --start-port 1 --end-port 2000 --threads 300 --timeout 0.8 --out scan_result.txt
```

## 命令行参数

- `--ip`：目标 IP（与 `--ip-list` 二选一）。
- `--ip-list`：包含多个 IP 的文本文件路径；每行一个 IP。
- `--start-port`：起始端口，默认 1。
- `--end-port`：结束端口，默认 1024。
- `--threads`：工作线程数，默认 200。
- `--timeout`：单端口连接/等待超时（秒），默认 1.0。
- `--udp`：开启后对相同端口做 UDP 响应检查（可选）。
- `--out`：结果输出文件名，默认 `result.txt`。

未提供 `--ip/--ip-list` 时，程序进入交互式模式。

## 输出说明

- 控制台与文件输出格式一致：

```
<ip>\t<port>\t<proto>\t<service>
```

示例：

```
127.0.0.1	80	tcp	http
```

- 当未发现开放端口时，会打印相应提示；若启用 UDP，只有在收到数据响应时才标记为“可能开放”。

## 测试与示例

在本机快速验证：

```bash
python port_scanner.py --ip 127.0.0.1 --start-port 79 --end-port 82
```

若本机有 Web 服务，可能看到：

```
127.0.0.1	80	tcp	http
```

UDP 示例（在有运行的 UDP 服务时更有效）：

```bash
python port_scanner.py --ip 127.0.0.1 --start-port 53 --end-port 53 --udp
```

## 注意事项

- 扫描结果受目标主机与网络环境（防火墙、路由 ACL、IDS/IPS）影响较大，超时与线程数需按环境调优。
- UDP 扫描未收到响应并不表示端口关闭（可能被丢弃或过滤）；本工具对 UDP 采用保守判定，收到响应才标记为可能开放。
- 请在取得授权的前提下进行扫描，遵守当地法律法规与组织合规要求。

## 性能调优建议

- 增大 `--threads` 可提高并发度，但过大可能导致丢包、连接失败或影响稳定性。
- 适当增大 `--timeout` 可减少网络抖动影响，但会降低整体扫描速度。
- 建议先对常见端口（如 22/80/443 等）快速探测，再分段扩大范围。

## 原理概述

- TCP：使用 `connect_ex` 判断是否建立连接（0 表示连接成功即端口开放）。
- UDP：向端口发送空报文并等待响应；若收不到数据不判定开放，以避免误报。
- 服务识别：基于 IANA 注册表的 `getservbyport`（仅对标准端口号有效，异常返回 Unknown）。

## 目录与文件

- `port_scanner.py`：核心扫描脚本。
- `result.txt`：默认输出文件（每次运行覆盖）。
- `ip_list.txt`：可选，批量 IP 输入文件（需自行创建）。

## 许可与声明

本工具仅用于学习与授权测试目的。使用者需自行确保在合法、合规范围内使用由此产生的任何行为与后果。

=======
# 2024.07
简易端口扫描器
>>>>>>> 7edb7ba1c076b97a45bdbc1fb69f5483222ce16e
