import argparse
import socket
import threading
from queue import Queue
from typing import List, Tuple


def get_service(port: int, proto: str) -> str:
    try:
        return socket.getservbyport(port, proto)
    except OSError:
        return "Unknown"


def scan_tcp_port(ip: str, port: int, timeout: float) -> Tuple[int, str, bool]:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        result = s.connect_ex((ip, port))
        if result == 0:
            return port, get_service(port, "tcp"), True
        return port, "", False
    except OSError:
        return port, "", False
    finally:
        try:
            s.close()
        except Exception:
            pass


def scan_udp_port(ip: str, port: int, timeout: float) -> Tuple[int, str, bool]:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    try:
        s.sendto(b"", (ip, port))
        try:
            data, _ = s.recvfrom(1024)
            if data is not None:
                return port, get_service(port, "udp"), True
        except socket.timeout:
            return port, "", False
        except OSError:
            return port, "", False
        return port, "", False
    except OSError:
        return port, "", False
    finally:
        try:
            s.close()
        except Exception:
            pass


class PortScanner:
    def __init__(self, ip: str, start_port: int, end_port: int, threads: int, timeout: float, udp: bool):
        self.ip = ip
        self.start_port = start_port
        self.end_port = end_port
        self.threads = max(1, threads)
        self.timeout = timeout
        self.udp = udp
        self.results_tcp: List[Tuple[int, str]] = []
        self.results_udp: List[Tuple[int, str]] = []
        self._lock = threading.Lock()
        self._scanned = 0
        self._total = end_port - start_port + 1

    def _worker(self, q: Queue):
        while True:
            try:
                port = q.get_nowait()
            except Exception:
                break
            try:
                p, s, ok = scan_tcp_port(self.ip, port, self.timeout)
                if ok:
                    with self._lock:
                        self.results_tcp.append((p, s))
                if self.udp:
                    p2, s2, ok2 = scan_udp_port(self.ip, port, self.timeout)
                    if ok2:
                        with self._lock:
                            self.results_udp.append((p2, s2))
            finally:
                with self._lock:
                    self._scanned += 1
                    if self._scanned % 100 == 0 or self._scanned == self._total:
                        print(f"进度 {self.ip}: {self._scanned}/{self._total}")
                q.task_done()

    def run(self):
        q: Queue = Queue()
        for p in range(self.start_port, self.end_port + 1):
            q.put(p)
        workers = []
        for _ in range(self.threads):
            t = threading.Thread(target=self._worker, args=(q,), daemon=True)
            t.start()
            workers.append(t)
        q.join()
        for t in workers:
            t.join(timeout=0.1)
        self.results_tcp.sort(key=lambda x: x[0])
        self.results_udp.sort(key=lambda x: x[0])


def parse_ips(single_ip: str = "", ip_list_path: str = "") -> List[str]:
    ips: List[str] = []
    if ip_list_path:
        try:
            with open(ip_list_path, "r", encoding="utf-8") as f:
                for line in f:
                    v = line.strip()
                    if v:
                        ips.append(v)
        except FileNotFoundError:
            pass
    if single_ip:
        ips.append(single_ip)
    dedup = []
    seen = set()
    for i in ips:
        if i not in seen:
            seen.add(i)
            dedup.append(i)
    return dedup


def main():
    parser = argparse.ArgumentParser(prog="port_scanner")
    parser.add_argument("--ip", type=str, default="")
    parser.add_argument("--ip-list", type=str, default="")
    parser.add_argument("--start-port", type=int, default=1)
    parser.add_argument("--end-port", type=int, default=1024)
    parser.add_argument("--threads", type=int, default=200)
    parser.add_argument("--timeout", type=float, default=1.0)
    parser.add_argument("--udp", action="store_true")
    parser.add_argument("--out", type=str, default="result.txt")
    args = parser.parse_args()

    ips = parse_ips(args.ip, args.ip_list)
    if not ips:
        target_ip = input("请输入目标IP：").strip()
        start_port = int(input("请输入起始端口：").strip())
        end_port = int(input("请输入结束端口：").strip())
        udp_choice = input("是否启用UDP扫描？(y/N)：").strip().lower() == "y"
        threads = input("线程数(默认200)：").strip()
        threads = int(threads) if threads else 200
        ips = [target_ip]
        args.start_port = start_port
        args.end_port = end_port
        args.udp = udp_choice
        args.threads = threads

    all_lines: List[str] = []
    for ip in ips:
        print(f"开始扫描 {ip} 的端口 {args.start_port}-{args.end_port}，协议 TCP{' + UDP' if args.udp else ''}")
        scanner = PortScanner(ip, args.start_port, args.end_port, args.threads, args.timeout, args.udp)
        scanner.run()
        if scanner.results_tcp:
            print(f"{ip} TCP 开放端口：")
            for p, s in scanner.results_tcp:
                line = f"{ip}\t{p}\ttcp\t{s}"
                print(line)
                all_lines.append(line)
        else:
            print(f"{ip} 未发现 TCP 开放端口")
        if args.udp:
            if scanner.results_udp:
                print(f"{ip} UDP 可能开放端口（基于响应）：")
                for p, s in scanner.results_udp:
                    line = f"{ip}\t{p}\tudp\t{s}"
                    print(line)
                    all_lines.append(line)
            else:
                print(f"{ip} 未发现有响应的 UDP 端口")

    if all_lines:
        try:
            with open(args.out, "w", encoding="utf-8") as f:
                for ln in all_lines:
                    f.write(ln + "\n")
            print(f"结果已写入 {args.out}")
        except Exception as e:
            print(f"写入结果失败: {e}")


if __name__ == "__main__":
    main()

