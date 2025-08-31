from aiohttp import ClientSession, FormData
from typing import Any, Optional
import aiofiles, re, os


class Network:
    def __init__(self, token: str) -> None:
        self.token: str = token
        self.session: Optional[ClientSession] = None
        self.api: str = f"https://botapi.rubika.ir/v3/{token}/"

    async def start(self):
        if not self.session:
            self.session = ClientSession()

    async def stop(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def request(self, method: str, json: dict[str, Any]):
        await self.start()
        async with self.session.post(self.api + method, json=json) as response:
            response.raise_for_status()
            data: dict = await response.json()
            return data.get("data")

    async def ContentFile(self, url: str) -> bytes:
        await self.start()
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.read()

    async def RequestUploadFile(self, upload_url: str, file: str, name: str):
        if isinstance(file, str):
            if re.match(r"^https://", file):
                file = await self.ContentFile(file)
            elif os.path.isfile(file):
                async with aiofiles.open(file, "rb") as f:
                    file = await f.read()
            else:
                raise Exception("file not found : {}".format(file))

            form = FormData()
            form.add_field("file", file, filename=name, content_type="application/octet-stream")
            await self.start()
            async with self.session.post(upload_url, data=form) as response:
                response.raise_for_status()
                data: dict = await response.json()
                return data.get("data", {}).get("file_id")

        raise Exception("Format Of file is invalid")

    async def RequestDownloadFile(self, url: str, name: str):
        file = await self.ContentFile(url)
        async with aiofiles.open(name, "wb") as f:
            await f.write(file)
        return name