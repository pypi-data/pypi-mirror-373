from GNServer import App as _App, GNRequest, GNResponse, AsyncClient
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
import subprocess
import sys
from KeyisBClient import Url
import asyncio


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

        self._default_venv_path = None

        self._client = AsyncClient()

        self.__add_routes()



    def setAccessKey(self, key: str):
        self._access_key = key

    def setVenvPath(self, venv_path: str):
        self._default_venv_path = venv_path

    def addServerStartFile(self, name: str, file_path: str, port: Optional[int] = None, start_when_run: bool = False, venv_path: Optional[str] = None):
        self._servers_start_files[name] = {"name": name, "path": file_path, "port": port, "start_when_run": start_when_run, "venv_path": venv_path if venv_path is not None else self._default_venv_path}

    async def startLikeRun(self):
        for server in self._servers_start_files:
            if self._servers_start_files[server]["start_when_run"]:
                asyncio.create_task(self.startServer(server))

    async def startServer(self, name: str, timeout: float = 10.0) -> bool:
        if name in self._servers_start_files:
            server = self._servers_start_files[name]
            path = server["path"]
            venv_path = server["venv_path"]
            if not os.path.isfile(path):
                raise ValueError(f"Server start file not found: {path}")
            
            if path.endswith('.py'):
                if venv_path is not None:
                    if not os.path.isdir(venv_path):
                        raise ValueError(f"Virtual environment path not found: {venv_path}")
                    python_executable = os.path.join(venv_path, 'bin', 'python')
                    if not os.path.isfile(python_executable):
                        raise ValueError(f"Python executable not found in virtual environment: {python_executable}")
                else:
                    python_executable = sys.executable
                
                subprocess.Popen([python_executable, path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            else:
                subprocess.Popen([path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            return await self.checkServerHealth(name, timeout=timeout)
        else:
            raise ValueError(f"No server start file found with name: {name}")
    


    async def _send_message_to_server(self, name: str, path: str, payload: Optional[dict] = None, timeout: float = 1.0) -> Optional[GNResponse]:
        port = self._servers_start_files[name].get("port")
        if port is None:
            raise ValueError(f"No port specified for server: {name}")

        if path.startswith('/'):
            path = path[1:]

        c = self._client.request(GNRequest('POST', Url(f'gn://127.0.0.1:{port}/!gn-vm-host/{path}'), payload=payload))

        try:
            result = await asyncio.wait_for(c, timeout=timeout)
        except asyncio.TimeoutError:
            result = None
        
        return result

    async def checkServerHealth(self, name: str, timeout: float = 3.0, interval=0.5):
        end = asyncio.get_event_loop().time() + timeout
        while asyncio.get_event_loop().time() < end:
            result = await self._send_message_to_server(name, '/ping', timeout=timeout)
            if result is not None:
                return True
            else:
                await asyncio.sleep(interval)
        return False
        


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

    async def reloadServer(self, name: str, timeout: float = 1):
        if name in self._servers_start_files:
            self.stopServer(name)
            await asyncio.sleep(timeout)
            return await self.startServer(name)
        else:
            raise ValueError(f"No server start file found with name: {name}")

    def run(self,
            host,
            port,
            cert_path: str,
            key_path: str,
            *,
            idle_timeout: float = 20.0,
            wait: bool = True
            ):
        

        asyncio.create_task(self.startLikeRun())

        self._app.run(
            host=host,
            port=port,
            cert_path=cert_path,
            key_path=key_path,
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
        async def ping_handler(request: GNRequest, name: Optional[str] = None, timeout: float = 3.0):
            if not self.__resolve_access_key(request):
                return None
            
            if not name:
                return GNResponse('ok', {'time': datetime.datetime.now(datetime.timezone.utc).isoformat()})
            else:
                try:
                    result = await self.checkServerHealth(name, timeout=timeout)
                    if result:
                        return GNResponse('ok', {'message': f'Server {name} is alive.'})
                    else:
                        return GNResponse('error', {'error': f'Server {name} is not responding.'})
                except ValueError as e:
                    return GNResponse('error', {'error': str(e)})
                
        @self._app.route('GET', '/servers')
        async def list_servers_handler(request: GNRequest):
            if not self.__resolve_access_key(request):
                return None
            
            servers_info = []
            for server in self._servers_start_files.values():
                servers_info.append({
                    'name': server['name'],
                    'port': server['port'],
                    'start_when_run': server['start_when_run']
                })
            return GNResponse('ok', {'servers': servers_info})



            

        @self._app.route('POST', '/start-server')
        async def start_server_handler(request: GNRequest, name: str = ''):
            if not self.__resolve_access_key(request):
                return None
            
            if not name:
                return GNResponse('error', {'error': 'Server name is required.'})
            try:
                result = await self.startServer(name)
                if result:
                    return GNResponse('ok', {'message': f'Server {name} started.'})
                else:
                    return GNResponse('error', {'error': f'Server {name} failed to start within the timeout period.'})
            except ValueError as e:
                return GNResponse('error', {'error': str(e)})
            
            

        @self._app.route('POST', '/reload-server')
        async def reload_server_handler(request: GNRequest, name: str = '', timeout: float = 0.5):
            if not self.__resolve_access_key(request):
                return None

            if not name:
                return GNResponse('error', {'error': 'Server name is required.'})

            try:
                result = await self.reloadServer(name, timeout)
                if result:
                    return GNResponse('ok', {'message': f'Server {name} reloaded.'})
                else:
                    return GNResponse('error', {'error': f'Server {name} failed to reload within the timeout period.'})
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
                    result = await self.startServer(server)
                    if not result:
                        return GNResponse('error', {'error': f'Server {server} failed to start within the timeout period.'})
                except ValueError as e:
                    return GNResponse('error', {'error': str(e)})
        
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
                    result = await self.reloadServer(server, timeout)
                    if not result:
                        return GNResponse('error', {'error': f'Server {server} failed to reload within the timeout period.'})
                except ValueError as e:
                    return GNResponse('error', {'error': str(e)})
