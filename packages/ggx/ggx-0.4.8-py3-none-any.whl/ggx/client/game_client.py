import asyncio
import json
import random
import re
import inspect
from typing import Any, Callable, Dict, List, Optional, Union, Awaitable
import aiohttp
from loguru import logger
from websockets.asyncio.client import connect, ClientConnection
from websockets.exceptions import ConnectionClosed

from ._cfg import *


class GameClient:
    
    HandlerType = Callable[[Any], Union[Any, Awaitable[Any]]]
    
    def __init__(
        self,
        url: str,
        server_header: str,
        username: str,
        password: str
    ) -> None:
        
        self.url = url
        self.server_header = server_header
        self.username = username
        self.password = password
        
        self.ws: Optional[ClientConnection] = None
        self.connected = asyncio.Event()
        self._stop_event = asyncio.Event()
        self._tasks: List[asyncio.Task] = []
        
        self._msg_queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        self._pending_futures: Dict[str, List[asyncio.Future]] = {}
        self.user_agent = random.choice(DEFAULT_UA_LIST)
        
    async def connect(self) -> None:
        """
        Main client loop to manage connection and reconnection.
        """
        while not self._stop_event.is_set():
            try:
                await self._run_connection_session()
            except (ConnectionClosed, asyncio.CancelledError):
                logger.warning("Connection closed gracefully.")
                self.connected.clear()
                if self._stop_event.is_set():
                    break
                logger.info("Attempting to reconnect in 5 seconds...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Error during connection session: {e}")
                self.connected.clear()
                if self._stop_event.is_set():
                    break
                logger.info("Attempting to reconnect in 5 seconds...")
                await asyncio.sleep(5)
        logger.info("Client shutdown complete.")

    async def _run_connection_session(self) -> None:
        """
        Handles a single connection session.
        """
        async with connect(
            self.url,
            origin=CLIENT_ORIGIN,
            user_agent_header=self.user_agent,
            additional_headers=AD_HEADERS
        ) as ws:
            self.ws = ws
            self.connected.set()
            logger.info(f"GGClient connected! {VERSION}")
            
            listener = asyncio.create_task(self._listener())
            keep_alive = asyncio.create_task(self.keep_alive())
            nch_task = asyncio.create_task(self._nch())
            
            if not await self._init():
                await self.disconnect()
                return
            
            runner = asyncio.create_task(self.run_jobs())
            self._tasks = [listener, keep_alive, nch_task, runner]
            
            done, pending = await asyncio.wait(
                self._tasks,
                return_when=asyncio.FIRST_EXCEPTION
            )
            
            for t in pending:
                t.cancel()
            
            await asyncio.gather(*pending, return_exceptions=True)
            
            for t in done:
                exc = t.exception()
                if exc and not isinstance(exc, asyncio.CancelledError):
                    raise exc
                
    async def _init(self) -> bool:
        await self._init_socket()
        return await self.login(self.username, self.password)            
                
    async def run_jobs(self) -> None:
        pass

    async def disconnect(self) -> None:
        self.connected.clear()
        if self.ws:
            try:
                await self.ws.close()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")

        logger.info("Disconnected!.")
        
    async def shutdown(self) -> None:
        self._stop_event.set()
        await self.disconnect()
        
        current_task = asyncio.current_task()
        tasks_to_cancel = [t for t in self._tasks if t is not current_task]

        for task in tasks_to_cancel:
            task.cancel()
            
        await asyncio.gather(*tasks_to_cancel, return_exceptions=True)
        
    async def send(self, message: str) -> None:
        if not self.ws: raise RuntimeError("GGClient not connected!")
        await self.ws.send(message)
            
    async def send_message(self, parts: List[str]) -> None:
        msg = "%".join(["", *parts, ""])
        await self.send(msg)
        
    async def send_raw_message(self, command: str, data: List[Any]) -> None:
        json_parts = [json.dumps(item) if isinstance(item, (dict, list)) else item for item in data]
        await self.send_message(["xt", self.server_header, command, "1", *json_parts])

    async def send_json_message(self, command: str, data: Dict[str, Any]) -> None:
        await self.send_message(["xt", self.server_header, command, "1", json.dumps(data)])

    async def send_xml_message(self, t: str, action: str, r: str, data: str) -> None:
        await self.send(f"<msg t='{t}'><body action='{action}' r='{r}'>{data}</body></msg>")
        
    async def receive(self) -> Dict[str, Any]:
        return await self._msg_queue.get()
    
    def _parse_message(self, message: str) -> Dict[str, Any]:
        if message.startswith("<"):
            m = re.search(r"<msg t='(.*?)'><body action='(.*?)' r='(.*?)'>(.*?)</body></msg>", message)
            t_val, action, r_val, data = m.groups()
            return {"type": "xml", "payload": {"t": t_val, "action": action, "r": int(r_val), "data": data}}
        
        parts = message.strip("%").split("%")
        cmd = parts[1]; status = int(parts[3])
        raw = "%".join(parts[4:])
        
        try:
            data = json.loads(raw)
        except:
            data = raw
        
        parsed_data = {"type": "json", "payload": {"command": cmd, "status": status, "data": data}}      
        return parsed_data
    
    async def _listener(self) -> None:
        try:
            async for raw in self.ws:
                text = raw.decode('utf-8') if isinstance(raw, bytes) else raw
                msg = self._parse_message(text)
                await self._msg_queue.put(msg)
                payload = msg.get("payload", {})
                cmd = payload.get("command") or payload.get("action")
                futures = self._pending_futures.get(cmd)
                if futures:
                    for fut in futures:
                        if not fut.done():
                            fut.set_result(payload.get("data"))
                    continue

                method = f"on_{cmd}"
                if hasattr(self, method):
                    handler = getattr(self, method)
                    data = payload.get("data")
                    if inspect.iscoroutinefunction(handler):
                        asyncio.create_task(handler(data))
                    else:
                        handler(data)
        except ConnectionClosed:
            logger.warning("Connection closed, stopping listener...")
        except asyncio.CancelledError:
            logger.warning("Listener task cancelled.")
            
    async def wait_for_response(self, command: str, timeout: float = 5.0) -> Any:
        deadline = asyncio.get_event_loop().time() + timeout
        buffer: List[Dict[str, Any]] = []
        try:
            while True:
                remaining = deadline - asyncio.get_event_loop().time()
                if remaining <= 0:
                    raise asyncio.TimeoutError(f"Timeout waiting for {command}")
                msg = await asyncio.wait_for(self._msg_queue.get(), timeout=remaining)
                payload = msg.get("payload", {})
                cmd = payload.get("command") or payload.get("action")
                msg_status = payload.get("status")
                if cmd == command and msg_status != 1:
                    return payload.get("data")
                buffer.append(msg)
        finally:
            for m in buffer:
                await self._msg_queue.put(m)
            
    async def send_rpc(self, command: str, data: Dict[str, Any], timeout: float = 5.0) -> Any:
        await self.send_json_message(command, data)
        return await self.wait_for_response(command, timeout)
    
    async def send_hrpc(self, command: str, data: Dict[str, Any], handler: HandlerType, timeout: float = 5.0) -> Any:
        await self.send_json_message(command, data)
        resp_data = await self.wait_for_response(command, timeout)
        to_handle = handler(resp_data)
        if inspect.isawaitable(to_handle):
            await to_handle
            
    async def keep_alive(self, interval: int = 60) -> None:
        try:
            await self.connected.wait()
            while self.connected.is_set() and not self._stop_event.is_set():
                await asyncio.sleep(interval)
                await self.send_raw_message("pin", ["<RoundHouseKick>"])
        except asyncio.CancelledError:
            logger.warning("Keep-alive task cancelled.")
            
    async def _nch(self, interval: int = 360) -> None:
        try:
            await self.connected.wait()
            while self.connected.is_set():
                await asyncio.sleep(interval)
                await self.send(f'%xt%{self.server_header}%nch%1%')
        except asyncio.CancelledError:
            logger.warning("NCH task cancelled.")
        
    async def _init_socket(self):
        await self.send_xml_message("sys", "verChk", "0", "<ver v='166' />")
        await self.send_xml_message("sys", "login", "0", 
                                        f"<login z='{self.server_header}'><nick><![CDATA[]]></nick><pword><![CDATA[1123010%fr%0]]></pword></login>")
        await self.send_xml_message("sys", "autoJoin", "-1", "")
        await self.send_xml_message("sys", "roundTrip", "1", "")
            
    async def fetch_game_db(self) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(GAME_VERSION_URL) as resp:
                resp.raise_for_status()
                text = await resp.text()
                _, version = text.strip().split("=", 1)
                version = version.strip()
            
            db_url = f"https://empire-html5.goodgamestudios.com/default/items/items_v{version}.json"
            async with session.get(db_url) as db_resp:
                db_resp.raise_for_status()
                data = await db_resp.json()
                return data
            
    async def login(
        self,
        username: str,
        password: str
        ) -> bool:
        
        if not self.connected.is_set():
            logger.error("Not connected yet!")
            return False
            
        while True:
            try:
                await self.send_json_message(
                    "lli",
                    {
                        "CONM": 175,
                        "RTM": 24,
                        "ID": 0,
                        "PL": 1,
                        "NOM": username,
                        "PW": password,
                        "LT": None,
                        "LANG": "fr",
                        "DID": "0",
                        "AID": "1674256959939529708",
                        "KID": "",
                        "REF": "https://empire.goodgamestudios.com",
                        "GCI": "",
                        "SID": 9,
                        "PLFID": 1
                    }
                    )
                
                response = await self.wait_for_response("lli")
                
                if not isinstance(response, dict):
                    return True
                
                if isinstance(response, dict) and not response:
                    logger.warning("Wrong username or password!")
                    return False
                
                if isinstance(response, dict) and "CD" in response:
                    cooldown_value = response["CD"]
                    logger.debug(f'Connection locked by the server! Reconnect in {cooldown_value} sec!')
                    await asyncio.sleep(cooldown_value)
                    
                else:
                    return True
                 
            except Exception as e:
                logger.error(f"Error during login: {e}")
                return False