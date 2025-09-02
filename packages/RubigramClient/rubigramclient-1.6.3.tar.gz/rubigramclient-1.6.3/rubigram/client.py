from typing import Optional, Callable, Literal, Union
from rubigram.models import Update, InlineMessage
from rubigram.method import Method
from rubigram.filters import Filter
from rubigram.state import StateManager
from datetime import datetime
from aiohttp import web
import asyncio



class Client(Method):
    def __init__(
        self,
        token: str,
        endpoint: Optional[str] = None,
        host: str = "0.0.0.0",
        port: int = 8000
    ):
        self.token = token
        self.endpoint = endpoint
        self.host = host
        self.port = port
        self.offset_id = None
        self.ROUTES = []
        self.MESSAGE_HANDLER = []
        self.INLINE_HANDLER = []
        # self.state = StateManager()
        super().__init__(token)     
            

    def create_handler(self, type: Literal["message", "inline"], filters: Optional[Filter] = None):
        def decorator(func: Callable) -> Callable:
            async def wrapper(client: Client, update: Update):
                if filters is None or await filters(update):
                    await func(client, update)
                    return True
                return False
            self.MESSAGE_HANDLER.append(wrapper) if type == "message" else self.INLINE_HANDLER.append(wrapper)
            return func
        return decorator
    
    def on_message(self, filters: Optional[Filter] = None):
        return self.create_handler("message", filters)

    def on_inline_message(self, filters: Optional[Filter] = None):
        return self.create_handler("inline", filters)
        
    async def dispatch(self, update: Union[Update, InlineMessage], type: Literal["message", "inline"]):
        handlers = self.MESSAGE_HANDLER if type == "message" else self.INLINE_HANDLER
        for handler in handlers:
            matched = await handler(self, update)
            if matched:
                return

    async def updater(self, data: dict):
        if "inline_message" in data:
            event = InlineMessage.from_dict(data["inline_message"])
            type = "inline"
        elif "update" in data:
            event = Update.from_dict(data["update"])
            type = "message"
        else: return
        event.client = self
        await self.dispatch(event, type)
    
    async def set_endpoints(self):
        endpoint_type = ["ReceiveUpdate", "ReceiveInlineMessage"]
        for i in endpoint_type: await self.update_bot_endpoint(f"{self.endpoint}/{i}", i)
    
    async def on_startup(self, app):
        await self.set_endpoints()
        # await self.state.start()
        await self.start()

    async def on_cleanup(self, app):
        # await self.state.stop()
        await self.stop()
        
    def create_request_handler(self):
        async def wrapper(request: web.Request):
            data = await request.json()
            await self.updater(data)
            return web.json_response({"status": "OK"})
        return wrapper
    
    async def runner(self):
        try:
            # await self.state.start()
            while True:
                get_updates = await self.get_update(100, self.offset_id)
                if get_updates.updates:
                    updates = get_updates.updates
                    for update in updates:
                        time = int(update.new_message.time) if update.type == "NewMessage" else int(update.updated_message.time) if update.type == "UpdatedMessage" else None
                        now = int(datetime.now().timestamp())
                        if time and time >= now or time + 2 >= now:
                            update.client = self
                            await self.dispatch(update, "message")
                    self.offset_id = get_updates.next_offset_id
        except Exception as error:
            print(f"ERROR : {error}")
        finally:
            # await self.state.stop()
            await self.stop()
    
    def create_app(self, path: str, method: str = "Get"):
        def decorator(func):
            self.ROUTES.append((path, func, method))
            return func
        return decorator
            
    def run(self):
        if self.endpoint:
            app = web.Application()
            app.on_startup(self.on_startup)
            app.on_cleanup(self.on_cleanup)
            for path, func, method in self.ROUTES:
                if method.upper() == "GET":
                    app.router.add_get(path, func)
                elif method.upper() == "POST":
                    app.router.add_post(path, func)
            app.router.add_post("/ReceiveUpdate", self.create_request_handler())
            app.router.add_post("/ReceiveInlineMessage", self.create_request_handler())
            web.run_app(app, host=self.host, port=self.port)
        else:
            try:
                asyncio.run(self.runner())
            except Exception as error:
                print(f"ERROR : {error}")