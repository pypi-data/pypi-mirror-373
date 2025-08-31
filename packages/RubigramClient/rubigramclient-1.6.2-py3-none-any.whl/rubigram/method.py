from .network import Network
from typing import Literal, Optional
from rubigram.models import Bot, Chat, Keypad, MessageId, Updates


class Method(Network):
    def __init__(self, token: str):
        super().__init__(token)

    async def get_me(self) -> "Bot":
        response = await self.request("getMe", {})
        return Bot.from_dict(response["bot"])

    async def get_chat(self, chat_id: str) -> "Chat":
        response = await self.request("getChat", {"chat_id": chat_id})
        return Chat.from_dict(response["chat"])

    async def get_update(self, limit: int = 1, offset_id: Optional[int] = None) -> "Updates":
        response = await self.request("getUpdates", {"limit": limit, "offset_id": offset_id})
        return Updates.from_dict(response)

    async def get_file(self, file_id: str) -> str:
        response = await self.request("getFile", {"file_id": file_id})
        return response["download_url"]

    async def set_command(self, command: list):
        response = await self.request("setCommands", {"bot_commands": command})
        return response

    async def update_bot_endpoint(self, url: str, type: Literal["ReceiveUpdate", "ReceiveInlineMessage", "ReceiveQuery", "GetSelectionItem", "SearchSelectionItems"]):
        response = await self.request("updateBotEndpoints", {"url": url, "type": type})
        return response

    async def delete_message(self, chat_id: str, message_id: str):
        await self.request("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

    async def remove_chat_keypad(self, chat_id: str):
        await self.request("editChatKeypad", {"chat_id": chat_id, "chat_keypad_type": "Remove"})

    async def edit_chat_keypad(self, chat_id: str, chat_keypad: Keypad):
        await self.request("editChatKeypad", {"chat_id": chat_id, "chat_keypad_type": "New", "chat_keypad": chat_keypad.to_dict()})

    async def edit_message_keypad(self, chat_id: str, message_id: str, inline_keypad: Keypad):
        await self.request("editMessageKeypad", {"chat_id": chat_id, "message_id": message_id, "inline_keypad": inline_keypad.to_dict()})

    async def edit_message_text(self, chat_id: str, message_id: str, text: str):
        await self.request("editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": text})

    async def forward_message(self, from_chat_id: str, message_id: str, to_chat_id: str, disable_notification: bool = False) -> "MessageId":
        data = {"from_chat_id": from_chat_id, "message_id": message_id, "to_chat_id": to_chat_id, "disable_notification": disable_notification}
        response = await self.request("forwardMessage", data)
        return MessageId.from_dict(response)

    async def send_message(
        self,
        chat_id: str,
        text: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Literal["New", "Remove"] = None,
        disable_notification: bool = None,
        reply_to_message_id=None
    ) -> "MessageId":
        data = {
            "chat_id": chat_id,
            "text": text,
            "chat_keypad": chat_keypad.to_dict() if chat_keypad else None,
            "inline_keypad": inline_keypad.to_dict() if inline_keypad else None,
            "chat_keypad_type": chat_keypad_type,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id
        }
        data = {key: value for key, value in data.items() if value is not None}
        response = await self.request("sendMessage", data)
        return MessageId.from_dict(response)

    async def send_poll(
        self,
        chat_id: str,
        question: str,
        options: list[str],
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        disable_notification: bool = False,
        reply_to_message_id: str = None,
        chat_keypad_type: Literal["New", "Remove"] = None
    ) -> "MessageId":
        data = {
            "chat_id": chat_id,
            "question": question,
            "options": options,
            "chat_keypad": chat_keypad.to_dict() if chat_keypad else None,
            "inline_keypad": inline_keypad.to_dict() if inline_keypad else None,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "chat_keypad_type": chat_keypad_type
        }
        data = {key: value for key, value in data.items() if value is not None}
        response = await self.request("sendPoll", data)
        return MessageId.from_dict(response)

    async def send_location(
        self,
        chat_id: str,
        latitude: str,
        longitude: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        disable_notification: bool = False,
        reply_to_message_id: str = None,
        chat_keypad_type: Literal["New", "Remove"] = None
    ) -> "MessageId":
        data = {
            "chat_id": chat_id,
            "latitude": latitude,
            "longitude": longitude,
            "chat_keypad": chat_keypad.to_dict() if chat_keypad else None,
            "inline_keypad": inline_keypad.to_dict() if inline_keypad else None,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "chat_keypad_type": chat_keypad_type
        }
        data = {key: value for key, value in data.items() if value is not None}
        response = await self.request("sendLocation", data)
        return MessageId.from_dict(response)

    async def send_contact(
        self,
        chat_id: str,
        first_name: str,
        last_name: str,
        phone_number: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        disable_notification: bool = False,
        reply_to_message_id: str = None,
        chat_keypad_type: Literal["New", "Remove"] = None
    ) -> "MessageId":
        data = {
            "chat_id": chat_id,
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number,
            "chat_keypad": chat_keypad.to_dict() if chat_keypad else None,
            "inline_keypad": inline_keypad.to_dict() if inline_keypad else None,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "chat_keypad_type": chat_keypad_type
        }
        data = {key: value for key, value in data.items() if value is not None}
        response = await self.request("sendContact", data)
        return MessageId.from_dict(response)

    async def send_sticker(
        self,
        chat_id: str,
        sticker_id: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        disable_notification: bool = False,
        reply_to_message_id: str = None,
        chat_keypad_type: Literal["New", "Remove"] = None,
    ) -> "MessageId":
        data = {
            "chat_id": chat_id,
            "sticker_id": sticker_id,
            "chat_keypad": chat_keypad.to_dict() if chat_keypad else None,
            "inline_keypad": inline_keypad.to_dict() if inline_keypad else None,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "chat_keypad_type": chat_keypad_type
        }
        data = {key: value for key, value in data.items() if value is not None}
        response = await self.request("sendSticker", data)
        return MessageId.from_dict(response)

    async def request_send_file(self, type: str):
        response = await self.request("requestSendFile", {"type": type})
        return response["upload_url"]

    async def upload_file(self, file: str, name: str, type: str):
        upload_url = await self.request_send_file(type)
        response = await self.RequestUploadFile(upload_url, file, name)
        return response

    async def download_file(self, file_id: str, file_name: str):
        download_url = await self.get_file(file_id)
        response = await self.RequestDownloadFile(download_url, file_name)
        return response

    async def send_file(
        self,
        chat_id: str,
        file: str,
        file_name: str,
        caption: str = None,
        type: Literal["File", "Image", "Voice", "Music", "Gif", "Video"] = "File",
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Literal["New", "Remove"] = None,
        disable_notification: bool = False,
        reply_to_message_id: str = None,
    ) -> "MessageId":
        file_id = await self.upload_file(file, file_name, type)
        data = {
            "chat_id": chat_id,
            "file_id": file_id,
            "text": caption,
            "chat_keypad": chat_keypad.to_dict() if chat_keypad else None,
            "inline_keypad": inline_keypad.to_dict() if inline_keypad else None,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "chat_keypad_type": chat_keypad_type,
        }
        data = {key: value for key, value in data.items() if value is not None}
        response = await self.request("sendFile", data)
        return MessageId.from_dict(response)

    async def send_document(self, chat_id: str, document: str, name: str, caption: str = None, **kwargs):
        return await self.send_file(chat_id, document, name, caption, "File", **kwargs)

    async def send_photo(self, chat_id: str, photo: str, name: str, caption: str = None, **kwargs):
        return await self.send_file(chat_id, photo, name, caption, "Image", **kwargs)

    async def send_video(self, chat_id: str, video: str, name: str, caption: str = None, **kwargs):
        return await self.send_file(chat_id, video, name, caption, "Video", **kwargs)

    async def send_gif(self, chat_id: str, gif: str, name: str, caption: str = None, **kwargs):
        return await self.send_file(chat_id, gif, name, caption, "Gif", **kwargs)

    async def send_music(self, chat_id: str, music: str, name: str, caption: str = None, **kwargs):
        return await self.send_file(chat_id, music, name, caption, "Music", **kwargs)

    async def send_voice(self, chat_id: str, voice: str, name: str, caption: str = None, **kwargs):
        return await self.send_file(chat_id, voice, name, caption, "Voice", **kwargs)