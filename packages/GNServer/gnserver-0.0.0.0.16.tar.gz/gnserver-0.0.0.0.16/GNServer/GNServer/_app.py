


import re
import uuid
import anyio
import decimal
import asyncio
import inspect
import traceback
import datetime
import KeyisBClient
from typing import Any, Awaitable, Callable, Dict, List, Optional, Pattern, Tuple, Union, AsyncGenerator
from dataclasses import dataclass
from aioquic.asyncio.server import serve
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent, StreamDataReceived
from typing import Any, AsyncGenerator, Union, get_origin, get_args
from urllib.parse import parse_qs

from KeyisBClient import gn
import aiofiles
import sys
import os

try:
    if not sys.platform.startswith("win"):
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    print("uvloop не установлен")





import logging

logger = logging.getLogger("GNServer")
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("[GNServer] %(name)s: %(levelname)s: %(message)s"))







def guess_type(filename: str) -> str:
    """
    Возвращает актуальный MIME-тип по расширению файла.
    Только современные и часто используемые типы.
    """
    ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''

    mime_map = {
        # 🔹 Текст и данные
        "txt": "text/plain",
        "html": "text/html",
        "css": "text/css",
        "csv": "text/csv",
        "xml": "application/xml",
        "json": "application/json",
        "js": "application/javascript",

        # 🔹 Изображения (актуальные для веба)
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
        "svg": "image/svg+xml",
        "avif": "image/avif",
        "ico": "image/x-icon",

        # 🔹 Видео (современные форматы)
        "mp4": "video/mp4",
        "webm": "video/webm",

        # 🔹 Аудио (современные форматы)
        "mp3": "audio/mpeg",
        "ogg": "audio/ogg",
        "oga": "audio/ogg",
        "m4a": "audio/mp4",
        "flac": "audio/flac",

        # 🔹 Архивы
        "zip": "application/zip",
        "gz": "application/gzip",
        "tar": "application/x-tar",
        "7z": "application/x-7z-compressed",
        "rar": "application/vnd.rar",

        # 🔹 Документы (актуальные офисные)
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",

        # 🔹 Шрифты
        "woff": "font/woff",
        "woff2": "font/woff2",
        "ttf": "font/ttf",
        "otf": "font/otf",
    }

    return mime_map.get(ext, "application/octet-stream")


import re
from typing import List

# regex для !{var}, поддерживает вложенность через точку
TPL_VAR_RE = re.compile(r'(?<!\\)!\{([A-Za-z_][A-Za-z0-9_\.]*)\}')

# список mime, которые считаем текстовыми
TEXTUAL_MIME_PREFIXES = [
    "text/",                       # text/html, text/css, text/plain
]
TEXTUAL_MIME_EXACT = {
    "application/javascript",
    "application/json",
    "application/xml",
    "application/xhtml+xml"
}
TEXTUAL_MIME_SUFFIXES = (
    "+xml",  # например application/rss+xml
    "+json", # application/ld+json
)

def extract_template_vars(filedata: bytes, mime: str) -> List[str]:
    """
    Ищет все !{var} в тексте, если MIME относится к текстовым.
    """
    mime = (mime or "").lower().strip()

    # определяем, текстовый ли mime
    is_textual = (
        mime.startswith(tuple(TEXTUAL_MIME_PREFIXES))
        or mime in TEXTUAL_MIME_EXACT
        or mime.endswith(TEXTUAL_MIME_SUFFIXES)
        or "javascript" in mime
        or "json" in mime
        or "xml" in mime
    )

    if not is_textual:
        return []

    try:
        text = filedata.decode("utf-8", errors="ignore")
    except Exception:
        return []

    return list(set(m.group(1) for m in TPL_VAR_RE.finditer(text)))


import re
from urllib.parse import urlparse

def resolve_cors(origin_url: str, rules: list[str]) -> bool:
    """
    Возвращает origin_url если он матчится хотя бы с одним правилом.
    Правила:
      - "*.example.com"    -> wildcard (одна метка)
      - "**.example.com"   -> globstar (0+ меток)
      - "pages.*.core.gn"  -> смешанное
      - "https://*.site.tld" -> с проверкой схемы
      - "!<regex>"         -> полное соответствие по regex к origin_url
    """

    if origin_url == 'gn:proxy:sys':
        return True





    origin = origin_url.rstrip("/")
    pu = urlparse(origin)
    scheme = (pu.scheme or "").lower()
    host = (pu.hostname or "").lower()
    port = pu.port  # может быть None

    if not host:
        return False

    for rule in rules:
        rule = rule.rstrip("/")

        # 1) Регекс-правило
        if rule.startswith("!"):
            pattern = rule[1:]
            if re.fullmatch(pattern, origin):
                return True
            continue

        # 2) Разбор схемы/хоста в правиле
        r_scheme = ""
        r_host = ""
        r_port = None

        if "://" in rule:
            pr = urlparse(rule)
            r_scheme = (pr.scheme or "").lower()
            # pr.netloc может содержать порт
            netloc = pr.netloc.lower()
            # разберём порт, если есть
            if ":" in netloc and not netloc.endswith("]"):  # простая обработка IPv6 не требуется здесь
                name, _, p = netloc.rpartition(":")
                r_host = name
                try:
                    r_port = int(p)
                except ValueError:
                    r_port = None
            else:
                r_host = netloc
        else:
            r_host = rule.lower()

        # схема в правиле задана -> должна совпасть
        if r_scheme and r_scheme != scheme:
            continue
        # порт в правиле задан -> должен совпасть
        if r_port is not None and r_port != port:
            continue

        # 3) Сопоставление хоста по шаблону с * и ** (по меткам)
        if _host_matches_pattern(host, r_host):
            return True

    return False


def _host_matches_pattern(host: str, pattern: str) -> bool:
    """
    Матчит host против pattern по доменным меткам:
      - '*'  -> ровно одна метка
      - '**' -> ноль или больше меток
      Остальные метки — точное совпадение (без внутр. вайлдкардов).
    Примеры:
      host=pages.static.core.gn, pattern=**.core.gn -> True
      host=pages.static.core.gn, pattern=pages.*.core.gn -> True
      host=pages.static.core.gn, pattern=*.gn.gn -> False
      host=abc.def.example.com, pattern=*.example.com -> False (нужно **.example.com)
      host=abc.example.com,     pattern=*.example.com -> True
    """
    host_labels = host.split(".")
    pat_labels = pattern.split(".")

    # быстрый путь: точное совпадение без вайлдкардов
    if "*" not in pattern:
        return host == pattern

    # рекурсивный матч с поддержкой ** (globstar)
    def match(hi: int, pi: int) -> bool:
        # оба дошли до конца
        if pi == len(pat_labels) and hi == len(host_labels):
            return True
        # закончился паттерн — нет
        if pi == len(pat_labels):
            return False

        token = pat_labels[pi]
        if token == "**":
            # два варианта:
            #  - пропустить '**' (ноль меток)
            if match(hi, pi + 1):
                return True
            #  - съесть одну метку (если есть) и остаться на '**'
            if hi < len(host_labels) and match(hi + 1, pi):
                return True
            return False
        elif token == "*":
            # нужно съесть ровно одну метку
            if hi < len(host_labels):
                return match(hi + 1, pi + 1)
            return False
        else:
            # точное совпадение метки
            if hi < len(host_labels) and host_labels[hi] == token:
                return match(hi + 1, pi + 1)
            return False

    return match(0, 0)



@dataclass
class Route:
    method: str
    path_expr: str
    regex: Pattern[str]
    param_types: dict[str, Callable[[str], Any]]
    handler: Callable[..., Any]
    name: str
    cors: Optional[gn.CORSObject]

_PARAM_REGEX: dict[str, str] = {
    "str":   r"[^/]+",
    "path":  r".+",
    "int":   r"\d+",
    "float": r"[+-]?\d+(?:\.\d+)?",
    "bool":  r"(?:true|false|1|0)",
    "uuid":  r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-"
             r"[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
             r"[0-9a-fA-F]{12}",
    "datetime": r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?",
    "date":     r"\d{4}-\d{2}-\d{2}",
    "time":     r"\d{2}:\d{2}:\d{2}(?:\.\d+)?",
    "decimal":  r"[+-]?\d+(?:\.\d+)?",
}

_CONVERTER_FUNC: dict[str, Callable[[str], Any]] = {
    "int":     int,
    "float":   float,
    "bool":    lambda s: s.lower() in {"1","true","yes","on"},
    "uuid":    uuid.UUID,
    "decimal": decimal.Decimal,
    "datetime": datetime.datetime.fromisoformat,
    "date":     datetime.date.fromisoformat,
    "time":     datetime.time.fromisoformat,
}

def _compile_path(path: str) -> tuple[Pattern[str], dict[str, Callable[[str], Any]]]:
    param_types: dict[str, Callable[[str], Any]] = {}
    rx_parts: list[str] = ["^"]
    i = 0
    while i < len(path):
        if path[i] != "{":
            rx_parts.append(re.escape(path[i]))
            i += 1
            continue
        j = path.index("}", i)
        spec = path[i+1:j]
        i = j + 1

        if ":" in spec:
            name, conv = spec.split(":", 1)
        else:
            name, conv = spec, "str"

        if conv.startswith("^"):
            rx = f"(?P<{name}>{conv})"
            typ = str
        else:
            rx = f"(?P<{name}>{_PARAM_REGEX.get(conv, _PARAM_REGEX['str'])})"
            typ = _CONVERTER_FUNC.get(conv, str)

        rx_parts.append(rx)
        param_types[name] = typ

    rx_parts.append("$")
    return re.compile("".join(rx_parts)), param_types

def _convert_value(raw: str | list[str], ann: Any, fallback: Callable[[str], Any]) -> Any:
    origin = get_origin(ann)
    args   = get_args(ann)

    if isinstance(raw, list) or origin is list:
        subtype = args[0] if (origin is list and args) else str
        if not isinstance(raw, list):
            raw = [raw]
        return [_convert_value(r, subtype, fallback) for r in raw]

    conv = _CONVERTER_FUNC.get(ann, ann) if ann is not inspect._empty else fallback
    return conv(raw) if callable(conv) else raw

def _ensure_async(fn: Callable[..., Any]) -> Callable[..., Any]:
    if inspect.iscoroutinefunction(fn) or inspect.isasyncgenfunction(fn):
        return fn
    async def wrapper(*args, **kw):
        return fn(*args, **kw)
    return wrapper

class App:
    def __init__(self):
        self._routes: List[Route] = []
        self._cors: Optional[gn.CORSObject] = None

    def route(self, method: str, path: str, cors: Optional[gn.CORSObject] = None):
        if path == '/':
            path = ''
        def decorator(fn: Callable[..., Any]):
            regex, param_types = _compile_path(path)
            self._routes.append(
                Route(
                    method.upper(),
                    path,
                    regex,
                    param_types,
                    _ensure_async(fn),
                    fn.__name__,
                    cors
                )
            )
            return fn
        return decorator

    def get(self, path: str, *, cors: Optional[gn.CORSObject] = None):
        return self.route("GET", path, cors)

    def post(self, path: str, *, cors: Optional[gn.CORSObject] = None):
        return self.route("POST", path, cors)

    def put(self, path: str, *, cors: Optional[gn.CORSObject] = None):
        return self.route("PUT", path, cors)

    def delete(self, path: str, *, cors: Optional[gn.CORSObject] = None):
        return self.route("DELETE", path, cors)

    
    def setRouteCors(self, cors: Optional[gn.CORSObject] = None):
        self._cors = cors



    async def dispatch(
        self, request: gn.GNRequest
    ) -> Union[gn.GNResponse, AsyncGenerator[gn.GNResponse, None]]:
        path    = request.url.path
        method  = request.method.upper()
        cand    = {path, path.rstrip("/") or "/", f"{path}/"}
        allowed = set()

        for r in self._routes:
            m = next((r.regex.fullmatch(p) for p in cand if r.regex.fullmatch(p)), None)
            if not m:
                continue

            allowed.add(r.method)
            if r.method != method:
                continue

            if r.cors is not None:
                if request._origin is None:
                    return gn.GNResponse("gn:backend:801", {'error': 'Cors error. Route has cors but request has no origin url.'})
                if not resolve_cors(request._origin, r.cors._allow_origins):
                    return gn.GNResponse("gn:backend:802", {'error': 'Cors error: origin'})
                if request.method not in r.cors._allow_methods and '*' not in r.cors._allow_methods:
                    return gn.GNResponse("gn:backend:803", {'error': 'Cors error: method'})

            sig = inspect.signature(r.handler)
            def _ann(name: str):
                param = sig.parameters.get(name)
                return param.annotation if param else inspect._empty

            kw: dict[str, Any] = {
                name: _convert_value(val, _ann(name), r.param_types.get(name, str))
                for name, val in m.groupdict().items()
            }

            for qn, qvals in parse_qs(request.url.query, keep_blank_values=True).items():
                if qn in kw:
                    continue
                raw = qvals if len(qvals) > 1 else qvals[0]
                kw[qn] = _convert_value(raw, _ann(qn), str)

            if "request" in sig.parameters:
                kw["request"] = request

            if inspect.isasyncgenfunction(r.handler):
                return r.handler(**kw)

            result = await r.handler(**kw)
            if isinstance(result, gn.GNResponse):
                if result._cors is None:
                    result._cors = self._cors
                if result._cors is not None and result._cors != r.cors:
                    if request._origin is None:
                        return gn.GNResponse("gn:backend:801", {'error': 'Cors error. Route has cors but request has no origin url.'})
                    if not resolve_cors(request._origin, result._cors._allow_origins):
                        return gn.GNResponse("gn:backend:802", {'error': 'Cors error: origin'})
                    if request.method not in result._cors._allow_methods and '*' not in result._cors._allow_methods:
                        return gn.GNResponse("gn:backend:803", {'error': 'Cors error: method'})
                return result
            else:
                raise TypeError(
                    f"{r.handler.__name__} returned {type(result)}; GNResponse expected"
                )

        if allowed:
            return gn.GNResponse("gn:backend:405", {'error': 'Method Not Allowed'})
        return gn.GNResponse("gn:backend:404", {'error': 'Not Found'})


    def fastFile(self, path: str, file_path: str, cors: Optional[gn.CORSObject] = None, template: Optional[gn.TemplateObject] = None, payload: Optional[dict] = None):
        @self.get(path)
        async def r_static():
            nonlocal file_path
            if file_path.endswith('/'):
                file_path = file_path[:-1]
                
            if not os.path.isfile(file_path):
                return gn.GNResponse('gn:backend:404', cors=cors)

            fileObject = gn.FileObject(file_path, template)
            return gn.GNResponse('ok', payload=payload, files=fileObject, cors=cors)


    def static(self, path: str, dir_path: str, cors: Optional[gn.CORSObject] = None, template: Optional[gn.TemplateObject] = None, payload: Optional[dict] = None):
        @self.get(f"{path}/{{_path:path}}")
        async def r_static(_path: str):
            file_path = os.path.join(dir_path, _path)
            
            if file_path.endswith('/'):
                file_path = file_path[:-1]
                
            if not os.path.isfile(file_path):
                return gn.GNResponse('gn:backend:404', cors=cors)
            
            fileObject = gn.FileObject(file_path, template)
            return gn.GNResponse('ok', payload=payload, files=fileObject, cors=cors)




    def _init_sys_routes(self):
        @self.get('/!gn-vm-host/ping')
        async def r_ping(request: gn.GNRequest):
            if request
            return gn.GNResponse('ok', {'status': 'pong'})



    class _ServerProto(QuicConnectionProtocol):
        def __init__(self, *a, api: "App", **kw):
            super().__init__(*a, **kw)
            self._api = api
            self._buffer: Dict[int, bytearray] = {}
            self._streams: Dict[int, Tuple[asyncio.Queue[Optional[gn.GNRequest]], bool]] = {}

        def quic_event_received(self, event: QuicEvent):
            if isinstance(event, StreamDataReceived):
                buf = self._buffer.setdefault(event.stream_id, bytearray())
                buf.extend(event.data)

                # пока не знаем, это стрим или нет

                if len(buf) < 8: # не дошел даже frame пакета
                    logger.debug(f'Пакет отклонен: {buf} < 8. Не доставлен фрейм')
                    return
                
                    
                # получаем длинну пакета
                mode, stream, lenght = gn.GNRequest.type(buf)

                if mode not in (1, 2): # не наш пакет
                    logger.debug(f'Пакет отклонен: mode пакета {mode}. Разрешен 1, 2')
                    return
                
                if not stream: # если не стрим, то ждем конец quic стрима и запускаем обработку ответа
                    if event.end_stream:
                        request = gn.GNRequest.deserialize(buf, mode)
                        # request.stream_id = event.stream_id
                        # loop = asyncio.get_event_loop()
                        # request.fut = loop.create_future()


                        request.stream_id = event.stream_id
                        asyncio.create_task(self._handle_request(request, mode))
                        logger.debug(f'Отправлена задача разрешения пакета {request} route -> {request.route}')

                        self._buffer.pop(event.stream_id, None)
                    return
                
                # если стрим, то смотрим сколько пришло данных
                if len(buf) < lenght: # если пакет не весь пришел, пропускаем
                    return

                # первый в буфере пакет пришел полностью
        
                # берем пакет
                data = buf[:lenght]

                # удаляем его из буфера
                del buf[:lenght]

                # формируем запрос
                request = gn.GNRequest.deserialize(data, mode)

                logger.debug(request, f'event.stream_id -> {event.stream_id}')

                request.stream_id = event.stream_id

                queue, inapi = self._streams.setdefault(event.stream_id, (asyncio.Queue(), False))

                if request.method == 'gn:end-stream':
                    if event.stream_id in self._streams:
                        _ = self._streams.get(event.stream_id)
                        if _ is not None:
                            queue, inapi = _
                            if inapi:
                                queue.put_nowait(None)
                                self._buffer.pop(event.stream_id)
                                self._streams.pop(event.stream_id)
                                logger.debug(f'Закрываем стрим [{event.stream_id}]')
                                return




                queue.put_nowait(request)

                # отдаем очередь в интерфейс
                if not inapi:
                    self._streams[event.stream_id] = (queue, True)

                    async def w():
                        while True:
                            chunk = await queue.get()
                            if chunk is None:
                                break
                            yield chunk

                    request._stream = w
                    asyncio.create_task(self._handle_request(request, mode))

        async def _handle_request(self, request: gn.GNRequest, mode: int):
            
            request._client_ip = self._quic._network_paths[0].addr[0]

            try:
                
                response = await self._api.dispatch(request)

                if inspect.isasyncgen(response):
                    async for chunk in response:  # type: ignore[misc]
                        chunk._stream = True
                        chunk = await self.resolve_response(chunk)
                        self._quic.send_stream_data(request.stream_id, chunk.serialize(mode), end_stream=False)
                        self.transmit()
                        
                    l = gn.GNResponse('gn:end-stream')
                    l._stream = True
                    l = self.resolve_response(l)
                    self._quic.send_stream_data(request.stream_id, l.serialize(mode), end_stream=True)
                    self.transmit()
                    return


                response = await self.resolve_response(response)
                self._quic.send_stream_data(request.stream_id, response.serialize(mode), end_stream=True)
                logger.debug(f'Отправлен на сервер ответ -> {response.command} {response.payload if response.payload and len((response.payload)) < 200 else ''}')
                self.transmit()
            except Exception as e:
                logger.error('GNServer: error\n'  + traceback.format_exc())

                response = gn.GNResponse('gn:backend:500')
                self._quic.send_stream_data(request.stream_id, response.serialize(mode), end_stream=True)
                self.transmit()
        
        async def resolve_response(self, response: gn.GNResponse) -> gn.GNResponse:
            await response.assembly()

            return response

        
 



    def run(
        self,
        host: str,
        port: int,
        cert_path: str,
        key_path: str,
        *,
        idle_timeout: float = 20.0,
        wait: bool = True
    ):

        self._init_sys_routes()

        cfg = QuicConfiguration(
            alpn_protocols=["gn:backend"], is_client=False, idle_timeout=idle_timeout
        )
        cfg.load_cert_chain(cert_path, key_path)

        async def _main():
            await serve(
                host,
                port,
                configuration=cfg,
                create_protocol=lambda *a, **kw: App._ServerProto(*a, api=self, **kw),
                retry=False,
            )
            if wait:
                await asyncio.Event().wait()

        asyncio.run(_main())
