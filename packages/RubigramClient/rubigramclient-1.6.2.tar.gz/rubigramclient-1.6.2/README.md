# Rubigram
A lightweight Python library to build Rubika bots easily.

## Installation
```bash
pip install RubigramClient
```

## Send Message
```python
from rubigram import Client, filters
from rubigram.models import Update

bot = Client("your_bot_token")

@bot.on_message(filters.command("start") & filters.private)
async def start_handler(client, message: Update):    
    await message.reply("Hi, WELCOME TO RUBIGRAM")

bot.run()
```

## Send Message & Get receiveInlineMessage
```python
from rubigram import Client, filters
from rubigram.models import Update, Button, Keypad, KeypadRow, InlineMessage


bot = Client(token="bot_token", endpoint="endpoint_url")


@bot.on_message(filters.command("start"))
async def start(_, message: Update):
    inline = Keypad(
        rows=[
            KeypadRow(
                buttons=[
                    Button("1", "Button 1"),
                    Button("2", "Button 2")
                ]
            )
        ]
    )
    await bot.send_message(message.chat_id, "Hi", inline_keypad=inline)
    

@bot.on_inline_message(filters.button(["1", "2"]))
async def button(_, message: InlineMessage):
    if message.aux_data.button_id == "1":
        await bot.send_message(message.chat_id, "You Click Button 1")
    elif message.aux_data.button_id == "2":
        await bot.send_message(message.chat_id, "You Click Button 2")
        
bot.run()
```

## Contex Manager
```python
from rubigram import Client
import asyncio

bot = Client("bot_token")

async def main():
    async with bot:
        data = await bot.get_me()
        print(data.bot_id)

asyncio.run(main())
```