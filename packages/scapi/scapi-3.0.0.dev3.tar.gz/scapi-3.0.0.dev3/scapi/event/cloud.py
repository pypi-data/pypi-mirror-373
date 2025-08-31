from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Any, Iterable, Iterator, Literal
import aiohttp
import json
from .base import _BaseEvent
from ..utils.client import HTTPClient
from ..sites.activity import CloudActivity
from ..utils.types import (
    WSCloudActivityPayload
)
from ..utils.common import __version__

if TYPE_CHECKING:
    from ..sites.session import Session



class _BaseCloud(_BaseEvent):
    """
    クラウドサーバーに接続するためのクラス。

    Attributes:
        url (str): 接続先のURL
        client (HTTPClient): 接続に使用するHTTPClient
        session (Session|None): Scratchのセッション
        header (dict[str,str]): ヘッダーに使用するデータ
        project_id (str|int): 接続先のプロジェクトID
        username (str): 接続に使用するユーザー名
        ws_timeout (aiohttp.ClientWSTimeout): aiohttpライブラリのタイムアウト設定
        send_timeout (float): データを送信する時のタイムアウトまでの時間
    """
    max_length:int|None = None
    rate_limit:float|None = None

    def __init__(
            self,
            url:str,
            client:HTTPClient,
            project_id:int|str,
            username:str,
            ws_timeout:aiohttp.ClientWSTimeout|None=None,
            send_timeout:float|None=None
        ):
        super().__init__()
        self.url = url

        self.client:HTTPClient = client or HTTPClient()
        self.session:"Session|None" = None

        self._ws:aiohttp.ClientWebSocketResponse|None = None
        self._ws_event:asyncio.Event = asyncio.Event()
        self._ws_event.clear()

        self.header:dict[str,str] = {}
        self.project_id = project_id
        self.username = username

        self.last_set_time:float = 0

        self._data:dict[str,str] = {}

        self.ws_timeout = ws_timeout or aiohttp.ClientWSTimeout(ws_receive=None, ws_close=10.0) # pyright: ignore[reportCallIssue]
        self.send_timeout = send_timeout or 10

    @property
    def ws(self) -> aiohttp.ClientWebSocketResponse:
        """
        接続に使用しているWebsocketを返す

        Raises:
            ValueError: 現在接続していない。

        Returns:
            aiohttp.ClientWebSocketResponse
        """
        if self._ws is None:
            raise ValueError("Websocket is None")
        return self._ws
    
    async def _send(self,data:list[dict[str,str]],*,project_id:str|int|None=None):
        add_param = {
            "user":self.username,
            "project_id":str(self.project_id if project_id is None else project_id)
        }
        text = "".join([json.dumps(add_param|i)+"\n" for i in data])
        await self.ws.send_str(text)

    async def _handshake(self):
        await self._send([{"method":"handshake"}])

    def _received_data(self,datas):
        if isinstance(datas,bytes):
            try:
                datas = datas.decode()
            except ValueError:
                return
        for raw_data in datas.split("\n"):
            try:
                data:WSCloudActivityPayload = json.loads(raw_data,parse_constant=str,parse_float=str,parse_int=str)
            except json.JSONDecodeError:
                continue
            if not isinstance(data,dict):
                continue
            method = data.get("method","")
            if method != "set":
                continue
            self._data[data.get("name")] = data.get("value")
            self._call_event(self.on_set,CloudActivity._create_from_ws(data,self))

    async def _event_monitoring(self,event:asyncio.Event):
        wait_count = 0
        while True:
            try:
                async with self.client._session.ws_connect(
                    self.url,
                    headers=self.header,
                    timeout=self.ws_timeout
                ) as ws:
                    self._ws = ws
                    await self._handshake()
                    self._call_event(self.on_connect)
                    self._ws_event.set()
                    wait_count = 0
                    self.last_set_time = max(self.last_set_time,time.time())
                    async for w in ws:
                        if w.type in (
                            aiohttp.WSMsgType.CLOSED,
                            aiohttp.WSMsgType.CLOSING,
                            aiohttp.WSMsgType.CLOSE,
                            aiohttp.WSMsgType.ERROR
                        ):
                            raise Exception
                        if self.is_running:
                            self._received_data(w.data)
            except Exception:
                pass
            self._ws_event.clear()
            self._call_event(self.on_disconnect,wait_count)
            await asyncio.sleep(wait_count)
            wait_count += 2
            await event.wait()

    async def on_connect(self):
        """
        [イベント] サーバーに接続が完了した。
        """
        pass

    async def on_set(self,activity:CloudActivity):
        """
        [イベント] 変数の値が変更された。

        Args:
            activity (CloudActivity): 変更のアクティビティ
        """
        pass

    async def on_disconnect(self,interval:int):
        """
        [イベント] サーバーから切断された。

        Args:
            interval (int): 再接続するまでの時間
        """
        pass


    @staticmethod
    def add_cloud(text:str) -> str:
        """
        先頭に☁がない場合☁を先頭に挿入する。

        Args:
            text (str): 変換したいテキスト

        Returns:
            str: 変換されたテキスト
        """
        if text.startswith("☁ "):
            return "☁ "+text
        return text

    async def send(self,payload:list[dict[str,str]],*,project_id:str|int|None=None):
        """
        サーバーにデータを送信する。

        Args:
            payload (list[dict[str,str]]): 送信したいデータ本体
            project_id (str | int | None, optional): 変更したい場合、送信先のプロジェクトID
        """
        await asyncio.wait_for(self._ws_event.wait(),timeout=self.send_timeout)

        if self.rate_limit:
            now = time.time()
            await asyncio.sleep(self.last_set_time+(self.rate_limit*len(payload)) - now)
            if self.last_set_time < now:
                self.last_set_time = now
        
        await self._send(payload,project_id=project_id)

    async def set_var(self,variable:str,value:Any,*,project_id:str|int|None=None):
        """
        クラウド変数を変更する。

        Args:
            variable (str): 設定したい変数名
            value (Any): 変数の値
            project_id (str | int | None, optional): 変更したい場合、送信先のプロジェクトID
        """
        await self.send([{
            "method":"set",
            "name":self.add_cloud(variable),
            "value":str(value)
        }],project_id=project_id)

    async def set_vars(self,data:dict[str,Any],*,project_id:str|int|None=None):
        """
        クラウド変数を変更する。

        Args:
            data (dict[str,Any]): 変数名と値のペア
            project_id (str | int | None, optional): 変更したい場合、送信先のプロジェクトID
        """
        await self.send([{
            "method":"set",
            "name":self.add_cloud(k),
            "value":str(v)
        } for k,v in data],project_id=project_id)

turbowarp_cloud_url = "wss://clouddata.turbowarp.org"

class TurboWarpCloud(_BaseCloud):
    def __init__(
            self,
            client: HTTPClient,
            project_id:int|str,
            username:str="scapi",
            reason:str="Unknown",
            *,
            url:str=turbowarp_cloud_url,
            timeout:aiohttp.ClientWSTimeout|None=None,
            send_timeout:float|None=None
        ):
        super().__init__(url, client, project_id, username, timeout, send_timeout)

        self.header["User-Agent"] = f"Scapi/{__version__} ({reason})"