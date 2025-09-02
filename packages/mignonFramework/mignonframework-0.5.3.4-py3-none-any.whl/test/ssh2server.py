import sys
import signal
import threading
import time
from typing import List, Optional, Tuple

import sshtunnel
from mignonFramework import JsonConfigManager, injectJson, Logger


RECONNECT_DELAY_SECONDS = 3


log = Logger(True)


manager = JsonConfigManager('./config.json')

class SSHConnectionConfig:
    ssh_server_host: str
    ssh_server_port: int
    ssh_username: str
    ssh_password: str

class ForwardRule:
    ssh_connection: SSHConnectionConfig
    local_host: str
    local_port: int
    remote_host: str
    remote_port: int
    comment: Optional[str] = None

@injectJson(manager)
class AppConfig:
    forwards: List[ForwardRule]



@log
def start_tunnel(rule: ForwardRule) -> Optional[sshtunnel.SSHTunnelForwarder]:
    """
    根据给定的规则，配置并准备一个 SSHTunnelForwarder 实例。
    这个函数现在也被重连逻辑复用。
    """
    try:
        conn_info = rule.ssh_connection
        server = sshtunnel.SSHTunnelForwarder(
            ssh_address_or_host=(conn_info.ssh_server_host, conn_info.ssh_server_port),
            ssh_username=conn_info.ssh_username,
            ssh_password=conn_info.ssh_password,
            local_bind_address=(rule.local_host, rule.local_port),
            remote_bind_address=(rule.remote_host, rule.remote_port),
            set_keepalive=30.0
        )

        return server
    except Exception as e:
        print(f"[!] 配置隧道 {rule.local_host}:{rule.local_port} 失败: {e}", file=sys.stderr)
        return None


@log
def main():
    print("[*] 正在启动多路独立 SSH 隧道服务...")
    try:
        app_config: AppConfig = AppConfig()
        if not hasattr(app_config, 'forwards') or not app_config.forwards:
            print("[!] 配置文件 `config.json` 的 forwards 列表为空或不存在。", file=sys.stderr)
            return
    except Exception as e:
        print(f"[!] 加载配置失败: {e}", file=sys.stderr)
        return

    managed_tunnels: List[Tuple[ForwardRule, sshtunnel.SSHTunnelForwarder]] = []
    last_reconnect_attempt = {}
    for rule in app_config.forwards:
        print(f"\n--- 正在初始化隧道: {rule.comment or f'本地端口 {rule.local_port}'} ---")
        tunnel_server = start_tunnel(rule)

        if tunnel_server:
            conn_info = rule.ssh_connection
            YELLOW = '\033[93m'
            LIGHT_BLUE = '\033[94m'
            BRIGHT_MAGENTA = '\033[95m'
            RESET = '\033[0m'
            print(f"[*] < {YELLOW}{rule.comment}{RESET} > [本地] {LIGHT_BLUE}{rule.local_host}:{rule.local_port}{RESET} -> [SSH] {conn_info.ssh_server_host} -> [远程] {BRIGHT_MAGENTA}{rule.remote_host}:{rule.remote_port}{RESET}")

            thread = threading.Thread(target=tunnel_server.start, daemon=True)
            thread.start()
            managed_tunnels.append((rule, tunnel_server))

    time.sleep(1.5)
    print(f"\n[*] 所有隧道任务已派发完毕！存活隧道数: {len(managed_tunnels)}。")
    print(f"[*] 隧道断开后将每隔 {RECONNECT_DELAY_SECONDS} 秒尝试自动重连。")
    print("[*] 按 Ctrl+C 退出。")

    try:
        while True:
            time.sleep(5)
            next_managed_tunnels = []
            for rule, tunnel in managed_tunnels:
                if tunnel.is_active:
                    next_managed_tunnels.append((rule, tunnel))
                    continue
                local_addr = f"{rule.local_host}:{rule.local_port}"
                current_time = time.time()
                last_attempt_time = last_reconnect_attempt.get(rule.local_port, 0)
                if current_time - last_attempt_time > RECONNECT_DELAY_SECONDS:
                    print(f"[!] 警告: {rule.comment} 隧道 {local_addr} 已断开，将在后台尝试重连...")
                    last_reconnect_attempt[rule.local_port] = current_time
                    try:
                        tunnel.stop()
                    except Exception:
                        pass
                    new_tunnel = start_tunnel(rule)
                    if new_tunnel:
                        thread = threading.Thread(target=new_tunnel.start, daemon=True)
                        thread.start()
                        next_managed_tunnels.append((rule, new_tunnel))
                    else:
                        next_managed_tunnels.append((rule, tunnel))
                    print(f"{rule.comment}  [本地] {rule.local_host}:{rule.local_port}  重连成功")
                else:
                    next_managed_tunnels.append((rule, tunnel))
            managed_tunnels = next_managed_tunnels

    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        print("\n[*] 正在关闭所有隧道...")
        for rule, tunnel in managed_tunnels:
            try:
                if tunnel.is_active:
                    tunnel.stop()
            except Exception as e:
                local_addr = f"{rule.local_host}:{rule.local_port}"
                print(f"[!] 关闭隧道 {local_addr} 时出错: {e}", file=sys.stderr)
        print("[*] 程序退出。")

if __name__ == '__main__':
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    main()