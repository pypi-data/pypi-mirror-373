from GNServer.GNServer import App as _App, GNRequest, GNResponse
from typing import Optional
import datetime
import os
import re
import signal
import subprocess
import sys
import time
from typing import Iterable, Set, Tuple
import os
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms

def _kill_process_by_port(port: int):

    def _run(cmd: list[str]) -> Tuple[int, str, str]:
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, check=False)
            return p.returncode, p.stdout.strip(), p.stderr.strip()
        except FileNotFoundError:
            return 127, "", f"{cmd[0]} not found"

    def pids_from_fuser(port: int, proto: str) -> Set[int]:
        # fuser понимает 59367/udp и 59367/tcp (оба стека)
        rc, out, _ = _run(["fuser", f"{port}/{proto}"])
        if rc != 0:
            return set()
        return {int(x) for x in re.findall(r"\b(\d+)\b", out)}

    def pids_from_lsof(port: int, proto: str) -> Set[int]:
        # lsof -ti UDP:59367  /  lsof -ti TCP:59367
        rc, out, _ = _run(["lsof", "-ti", f"{proto.upper()}:{port}"])
        if rc != 0 or not out:
            return set()
        return {int(x) for x in out.splitlines() if x.isdigit()}

    def pids_from_ss(port: int, proto: str) -> Set[int]:
        # ss -H -uapn 'sport = :59367'  (UDP)  /  ss -H -tapn ... (TCP)
        flag = "-uapn" if proto == "udp" else "-tapn"
        rc, out, _ = _run(["ss", "-H", flag, f"sport = :{port}"])
        if rc != 0 or not out:
            return set()
        pids = set()
        for line in out.splitlines():
            # ... users:(("python3",pid=1234,fd=55))
            for m in re.finditer(r"pid=(\d+)", line):
                pids.add(int(m.group(1)))
        return pids

    def find_pids(port: int, proto: str | None) -> Set[int]:
        protos: Iterable[str] = [proto] if proto in ("udp","tcp") else ("udp","tcp")
        found: Set[int] = set()
        for pr in protos:
            # Порядок: fuser -> ss -> lsof (достаточно любого)
            found |= pids_from_fuser(port, pr)
            found |= pids_from_ss(port, pr)
            found |= pids_from_lsof(port, pr)
        # не убивать себя
        found.discard(os.getpid())
        return found

    def kill_pids(pids: Set[int]) -> None:
        if not pids:
            return
        me = os.getpid()
        for sig in (signal.SIGTERM, signal.SIGKILL):
            still = set()
            for pid in pids:
                if pid == me:
                    continue
                try:
                    os.kill(pid, sig)
                except ProcessLookupError:
                    continue
                except PermissionError:
                    print(f"[WARN] No permission to signal {pid}")
                    still.add(pid)
                    continue
                still.add(pid)
            if not still:
                return
            # подождём чуть-чуть
            for _ in range(10):
                live = set()
                for pid in still:
                    try:
                        os.kill(pid, 0)
                        live.add(pid)
                    except ProcessLookupError:
                        pass
                still = live
                if not still:
                    return
                time.sleep(0.1)

    def wait_port_free(port: int, proto: str | None, timeout: float = 3.0) -> bool:
        t0 = time.time()
        while time.time() - t0 < timeout:
            if not find_pids(port, proto):
                return True
            time.sleep(0.1)
        return not find_pids(port, proto)

    for proto in ("udp", "tcp"):
        pids = find_pids(port, proto)
    

        print(f"Гашу процессы на порту {port}: {sorted(pids)}")
        kill_pids(pids)

        if wait_port_free(port, proto):
            print(f"Порт {port} освобождён.")
        else:
            print(f"[ERROR] Не удалось освободить порт {port}. Возможно, другой netns/служба перезапускает процесс.")


def _sign(k:bytes)->bytes:nonce=os.urandom(16);m=b"keyisb-vm-host-"+os.urandom(32);return nonce+Cipher(algorithms.ChaCha20(k[:32],nonce),None).encryptor().update(m)
def _verify(k:bytes,s:bytes)->bool:nonce,ct=s[:16],s[16:];return Cipher(algorithms.ChaCha20(k[:32],nonce),None).decryptor().update(ct).startswith(b"keyisb-vm-host-")

class App():
    def __init__(self):
        self._app = _App()

        self._servers_start_files = {}

        self._access_key: Optional[str] = None

        self.__add_routes()



    def setAccessKey(self, key: str):
        self._access_key = key


    def addServerStartFile(self, name: str, file_path: str, port: Optional[int] = None, start_when_run: bool = False):
        self._servers_start_files[name] = {"name": name, "path": file_path, "port": port, "start_when_run": start_when_run}

    def startLikeRun(self):
        for server in self._servers_start_files:
            if self._servers_start_files[server]["start_when_run"]:
                self.startServer(server)
        
    def startServer(self, name: str):
        if name in self._servers_start_files:
            server = self._servers_start_files[name]

            path = server["path"]

            if path.endswith('.py'):
                import subprocess
                import sys
                subprocess.Popen([sys.executable, path], shell=True)
            elif path.endswith('.bat') or path.endswith('.cmd'):
                import subprocess
                subprocess.Popen([path], shell=True)
            else:
                raise ValueError("Unsupported file type. Only .py, .bat, and .cmd are supported.")
        else:
            raise ValueError(f"No server start file found with name: {name}")


    def stopServer(self, name: str):
        if name in self._servers_start_files:
            server = self._servers_start_files[name]
            port = server["port"]
            if port is not None:
                _kill_process_by_port(port)
            else:
                raise ValueError(f"No port specified for server: {name}")
        else:
            raise ValueError(f"No server start file found with name: {name}")

    def reloadServer(self, name: str, timeout: float = 0.5):
        if name in self._servers_start_files:
            self.stopServer(name)
            time.sleep(timeout)
            self.startServer(name)
        else:
            raise ValueError(f"No server start file found with name: {name}")

    def run(self,
            cert_path: str,
            key_path: str,
            *,
            idle_timeout: float = 20.0,
            wait: bool = True
            ):
        

        self.startLikeRun()

        self._app.run(
            '0.0.0.0',
            60000,
            cert_path,
            key_path,
            idle_timeout=idle_timeout,
            wait=wait
        )


    def __resolve_access_key(self, request: GNRequest) -> bool:
        if self._access_key is None:
            raise ValueError("Access key is not set.")
        
        sign = request.cookies.get('vm-host-sign')

        if sign is None:
            return False

        return _verify(self._access_key.encode(), sign)

    def __add_routes(self):
        @self._app.route('POST', '/ping')
        async def ping_handler(request: GNRequest):
            if not self.__resolve_access_key(request):
                return None
            

            return GNResponse('ok', {'time': datetime.datetime.now(datetime.timezone.utc).isoformat()})
            

        @self._app.route('POST', '/start-server')
        async def start_server_handler(request: GNRequest, name: str = ''):
            if not self.__resolve_access_key(request):
                return None
            
            if not name:
                return GNResponse('error', {'error': 'Server name is required.'})
            
            try:
                self.startServer(name)
                return GNResponse('ok', {'message': f'Server {name} started.'})
            except ValueError as e:
                return GNResponse('error', {'error': str(e)})

        @self._app.route('POST', '/reload-server')
        async def reload_server_handler(request: GNRequest, name: str = '', timeout: float = 0.5):
            if not self.__resolve_access_key(request):
                return None

            if not name:
                return GNResponse('error', {'error': 'Server name is required.'})

            try:
                self.reloadServer(name, timeout)
                return GNResponse('ok', {'message': f'Server {name} reloaded.'})
            except ValueError as e:
                return GNResponse('error', {'error': str(e)})
        
        @self._app.route('POST', '/stop-server')
        async def stop_server_handler(request: GNRequest, name: str = ''):
            if not self.__resolve_access_key(request):
                return None

            if not name:
                return GNResponse('error', {'error': 'Server name is required.'})

            try:
                self.stopServer(name)
                return GNResponse('ok', {'message': f'Server {name} stopped.'})
            except ValueError as e:
                return GNResponse('error', {'error': str(e)})
        
        @self._app.route('POST', '/start-all-servers')
        async def start_all_servers_handler(request: GNRequest):
            if not self.__resolve_access_key(request):
                return None

            for server in self._servers_start_files:
                try:
                    self.startServer(server)
                except ValueError as e:
                    return GNResponse('error', {'error': str(e)})

            return GNResponse('ok', {'message': 'All servers started.'})
        
        @self._app.route('POST', '/stop-all-servers')
        async def stop_all_servers_handler(request: GNRequest):
            if not self.__resolve_access_key(request):
                return None

            for server in self._servers_start_files:
                try:
                    self.stopServer(server)
                except ValueError as e:
                    return GNResponse('error', {'error': str(e)})

            return GNResponse('ok', {'message': 'All servers stopped.'})
        
        @self._app.route('POST', '/reload-all-servers')
        async def reload_all_servers_handler(request: GNRequest, timeout: float = 0.5):
            if not self.__resolve_access_key(request):
                return None

            for server in self._servers_start_files:
                try:
                    self.reloadServer(server, timeout)
                except ValueError as e:
                    return GNResponse('error', {'error': str(e)})

            return GNResponse('ok', {'message': 'All servers reloaded.'})
