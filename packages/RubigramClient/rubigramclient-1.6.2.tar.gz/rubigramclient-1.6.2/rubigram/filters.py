from rubigram.models import Update, InlineMessage
from typing import Union
import re



class Filter:
    def __init__(self, func):
        self.func = func
    
    async def __call__(self, update: Union[Update, InlineMessage]):
        return await self.func(update)
    
    def __and__(self, other: "Filter"):
        async def filter(update):
            return await self(update) and await other(update)
        return Filter(filter)
    
    def __or__(self, other: "Filter"):
        async def filter(update):
            return await self(update) or await other(update)
        return Filter(filter)



async def TEXT(message: Update):
    if isinstance(message, Update):
        return True if message.new_message and message.new_message.text else False
    return False

async def FILE(message: Update):
    if isinstance(message, Update):
        return True if message.new_message and message.new_message.file else False
    return False

async def LIVE(message: Update):
    if isinstance(message, Update):
        return True if message.new_message and message.new_message.live_location else False
    return False

async def POLL(message: Update):
    if isinstance(message, Update):
        return True if message.new_message and message.new_message.poll else False
    return False

async def CONTACT(message: Update):
    if isinstance(message, Update):
        return True if message.new_message and message.new_message.contact_message else False
    return False

async def STICKER(message: Update):
    if isinstance(message, Update):
        return True if message.new_message and message.new_message.sticker else False
    return False

async def LOCATION(message: Update):
    if isinstance(message, Update):
        return True if message.new_message and message.new_message.location else False
    return False

async def FORWARD(message: Update):
    if isinstance(message, Update):
        return True if message.new_message and message.new_message.forwarded_from else False
    return False

async def EDITED(message: Update):
    if isinstance(message, Update):
        return True if message.updated_message else False
    return False

async def PRIVATE(message: Union[Update, InlineMessage]):
    return True if message.chat_id.startswith("b0") else False
    
async def GROUP(message: Union[Update, InlineMessage]):
    return True if message.chat_id.startswith("g0") else False

async def CHANNEL(message: Union[Update, InlineMessage]):
    return True if message.chat_id.startswith("c0") else False

async def FORWARD_BOT(message: Update):
    if isinstance(message, Update) and message.new_message:
        return True if message.new_message.forwarded_from and message.new_message.forwarded_from.type_from == "Bot" else False

async def FORWARD_USER(message: Update):
    if isinstance(message, Update) and message.new_message:
        return True if message.new_message.forwarded_from and message.new_message.forwarded_from.type_from == "User" else False
    
async def FORWARD_CHANNEL(message: Update):
    if isinstance(message, Update) and message.new_message:
        return True if message.new_message.forwarded_from and message.new_message.forwarded_from.type_from == "Channel" else False


text = Filter(TEXT)
file = Filter(FILE)
live = Filter(LIVE)
poll = Filter(POLL)
contact = Filter(CONTACT)
sticker = Filter(STICKER)
location = Filter(LOCATION)
forward = Filter(FORWARD)
edited = Filter(EDITED)
private = Filter(PRIVATE)
group = Filter(GROUP)
channel = Filter(CHANNEL)
forward_bot = Filter(FORWARD_BOT)
forward_user = Filter(FORWARD_USER)
forward_channel = Filter(FORWARD_CHANNEL)


class state(Filter):
    def __init__(self, states: Union[str, list[str]]):
        self.states = states
        super().__init__(self.filter)
        
    async def filter(self, update: Union[Update, InlineMessage]):
        states = self.states if isinstance(self.states, list) else [self.states]
        user = await update.client.state.get_state(update.chat_id)
        return user.lower() in states if user else False
            

class command(Filter):
    def __init__(self, cmd: Union[str, list[str]], prefix: str = "/"):
        self.cmd = cmd
        self.prefix = prefix
        super().__init__(self.filter)

    async def filter(self, update: Update):
        commands = self.cmd if isinstance(self.cmd, list) else [self.cmd]
        text = ""
        if isinstance(update, Update):
            if update.type == "NewMessage":
                text = update.new_message.text
            elif update.type == "UpdatedMessage":
                text = update.updated_message.text
            if text:
                for cmd in commands:
                    if text.lower().startswith(self.prefix + cmd.lower()):
                        return True
                return False


class regex(Filter):
    def __init__(self, pattern: str):
        self.pattern = pattern
        super().__init__(self.filter)

    async def filter(self, update: Union[Update, InlineMessage]):
        text = ""
        if isinstance(update, Update):
            if update.type == "NewMessage":
                text = getattr(update.new_message, "text", "")
            elif update.type == "UpdatedMessage":
                text = getattr(update.updated_message, "text", "")
        elif isinstance(update, InlineMessage):
            text = getattr(update, "text", "")

        if text:
            return bool(re.search(self.pattern, text))
        return False


class chat(Filter):
    def __init__(self, chat_id: Union[str, list[str]]):
        self.chat_id = chat_id
        super().__init__(self.filter)

    async def filter(self, update: Union[Update, InlineMessage]):
        chat_ids = self.chat_id if isinstance(self.chat_id, list) else [self.chat_id]
        return update.chat_id in chat_ids


class button(Filter):
    def __init__(self, button_id: Union[str, list[str]], prefix: str = ""):
        self.button_id = button_id
        self.prefix = prefix
        super().__init__(self.filter)

    async def filter(self, update: InlineMessage):
        if isinstance(update, InlineMessage):
            button_ids = self.button_id if isinstance(self.button_id, list) else [self.button_id]
            for btn_id in button_ids:
                if update.aux_data.button_id.startswith(self.prefix + btn_id):
                    return True
            return False