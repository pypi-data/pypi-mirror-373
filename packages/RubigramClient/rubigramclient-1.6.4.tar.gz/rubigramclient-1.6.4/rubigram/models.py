from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Type, Union, TypeVar, Literal, Optional, get_origin, get_args
import rubigram
import json


T = TypeVar("T", bound="Dict")


@dataclass
class Dict:
    def to_dict(self) -> dict[str, Any]:
        data = {}
        for field in fields(self):
            value = getattr(self, field.name)
            if is_dataclass(value):
                data[field.name] = value.to_dict()
            elif isinstance(value, list):
                data[field.name] = [i.to_dict() if is_dataclass(i)else i for i in value]
            else:
                data[field.name] = value
        return data

    @classmethod
    def from_dict(cls: Type[T], data: dict[str, Any]) -> Optional[T]:
        if data is None:
            data = {}
        init_data = {}
        for field in fields(cls):
            value = data.get(field.name)
            field_type = field.type
            origin = get_origin(field_type)
            if isinstance(value, dict) and isinstance(field_type, type) and issubclass(field_type, Dict):
                init_data[field.name] = field_type.from_dict(value)
            elif origin == list:
                inner_type = get_args(field_type)[0]
                if isinstance(inner_type, type) and issubclass(inner_type, Dict):
                    init_data[field.name] = [inner_type.from_dict(
                        v) if isinstance(v, dict) else v for v in (value or [])]
                else:
                    init_data[field.name] = value or []
            elif get_origin(field_type) is Union:
                args = get_args(field_type)
                dict_type = next((a for a in args if isinstance(
                    a, type) and issubclass(a, Dict)), None)
                if dict_type and isinstance(value, dict):
                    init_data[field.name] = dict_type.from_dict(value)
                else:
                    init_data[field.name] = value
            else:
                init_data[field.name] = value
        return cls(**init_data)

    def to_json(self):
        data = self.to_dict().copy()
        data.pop("client", None)
        return json.dumps(data, ensure_ascii=False, indent=4)


@dataclass
class Location(Dict):
    longitude: Optional[str] = None
    latitude: Optional[str] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class OpenChatData(Dict):
    object_guid: Optional[str] = None
    object_type: Optional[Literal["User", "Bot", "Group", "Channel"]] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class JoinChannelData(Dict):
    username: Optional[str] = None
    ask_join: Optional[bool] = False

    def __repr__(self):
        return self.to_json()


@dataclass
class ButtonLink(Dict):
    type: Optional[Literal["joinchannel", "url"]] = None
    link_url: Optional[str] = None
    joinchannel_data: Optional[JoinChannelData] = None
    open_chat_data: Optional[OpenChatData] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class ButtonSelectionItem(Dict):
    text: Optional[str] = None
    image_url: Optional[str] = None
    type: Optional[Literal["TextOnly", "TextImgThu", "TextImgBig"]] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class ButtonTextbox(Dict):
    type_line: Optional[Literal["SingleLine", "MultiLine"]] = None
    type_keypad: Optional[Literal["String", "Number"]] = None
    place_holder: Optional[str] = None
    title: Optional[str] = None
    default_value: Optional[str] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class ButtonLocation(Dict):
    default_pointer_location: Optional[Location] = None
    default_map_location: Optional[Location] = None
    type: Optional[Literal["Picker", "View"]] = None
    title: Optional[str] = None
    location_image_url: Optional[str] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class ButtonStringPicker(Dict):
    items: Optional[list[str]] = None
    default_value: Optional[str] = None
    title: Optional[str] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class ButtonNumberPicker(Dict):
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    default_value: Optional[str] = None
    title: Optional[str] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class ButtonCalendar(Dict):
    default_value: Optional[str] = None
    type: Optional[Literal["DatePersian", "DateGregorian"]] = None
    min_year: Optional[str] = None
    max_year: Optional[str] = None
    title: Optional[str] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class ButtonSelection(Dict):
    selection_id: Optional[str] = None
    search_type: Optional[str] = None
    get_type: Optional[str] = None
    items: Optional[list[ButtonSelectionItem]] = None
    is_multi_selection: Optional[bool] = None
    columns_count: Optional[str] = None
    title: Optional[str] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class Button(Dict):
    id: Optional[str] = None
    button_text: Optional[str] = None
    type: Literal[
        "Simple", "Selection", "Calendar", "NumberPicker", "StringPicker", "Location", "Payment",
        "CameraImage", "CameraVideo", "GalleryImage", "GalleryVideo", "File", "Audio", "RecordAudio",
        "MyPhoneNumber", "MyLocation", "Textbox", "Link", "AskMyPhoneNumber", "AskLocation", "Barcode"
    ] = "Simple"
    button_selection: Optional[ButtonSelection] = None
    button_calendar: Optional[ButtonCalendar] = None
    button_number_picker: Optional[ButtonNumberPicker] = None
    button_string_picker: Optional[ButtonStringPicker] = None
    button_location: Optional[ButtonLocation] = None
    button_textbox: Optional[ButtonTextbox] = None
    button_link: Optional[ButtonLink] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class KeypadRow(Dict):
    buttons: list[Button]

    def __repr__(self):
        return self.to_json()


@dataclass
class Keypad(Dict):
    rows: list[KeypadRow]
    resize_keyboard: bool = True
    on_time_keyboard: bool = False

    def __repr__(self):
        return self.to_json()


@dataclass
class PollStatus(Dict):
    state: Optional[Literal["Open", "Closed"]] = None
    selection_index: Optional[int] = None
    percent_vote_options: Optional[list[int]] = None
    total_vote: Optional[int] = None
    show_total_votes: Optional[bool] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class File(Dict):
    file_id: Optional[str] = None
    file_name: Optional[str] = None
    size: Optional[str] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class LiveLocation(Dict):
    start_time: Optional[str] = None
    live_period: Optional[int] = None
    current_location: Optional[Location] = None
    user_id: Optional[str] = None
    status: Optional[Literal["Stopped", "Live"]] = None
    last_update_time: Optional[str] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class Poll(Dict):
    question: Optional[str] = None
    options: Optional[list[str]] = None
    poll_status: Optional[PollStatus] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class ContactMessage(Dict):
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class Sticker(Dict):
    sticker_id: Optional[str] = None
    file: Optional[File] = None
    emoji_character: Optional[str] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class ForwardedFrom(Dict):
    type_from: Optional[Literal["User", "Channel", "Bot"]] = None
    message_id: Optional[str] = None
    from_chat_id: Optional[str] = None
    from_sender_id: Optional[str] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class AuxData(Dict):
    start_id: Optional[str] = None
    button_id: Optional[str] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class PaymentStatus(Dict):
    payment_id: Optional[str] = None
    status: Optional[Literal["Paid", "NotPaid"]] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class Message(Dict):
    message_id: Optional[str] = None
    text: Optional[str] = None
    time: Optional[str] = None
    is_edited: Optional[bool] = None
    sender_type: Optional[Literal["User", "Bot"]] = None
    sender_id: Optional[str] = None
    aux_data: Optional[AuxData] = None
    file: Optional[File] = None
    reply_to_message_id: Optional[str] = None
    forwarded_from: Optional[ForwardedFrom] = None
    forwarded_no_link: Optional[str] = None
    location: Optional[Location] = None
    sticker: Optional[Sticker] = None
    contact_message: Optional[ContactMessage] = None
    poll: Optional[Poll] = None
    live_location: Optional[LiveLocation] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class InlineMessage(Dict):
    client: Optional["rubigram.Client"] = None
    sender_id: Optional[str] = None
    text: Optional[str] = None
    message_id: Optional[str] = None
    chat_id: Optional[str] = None
    file: Optional[File] = None
    location: Optional[Location] = None
    aux_data: Optional[AuxData] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class Bot(Dict):
    bot_id: Optional[str] = None
    bot_title: Optional[str] = None
    avatar: Optional[File] = None
    description: Optional[str] = None
    username: Optional[str] = None
    start_message: Optional[str] = None
    share_url: Optional[str] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class Chat(Dict):
    chat_id: Optional[str] = None
    chat_type: Optional[Literal["User", "Bot", "Group", "Channel"]] = None
    user_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    username: Optional[str] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class MessageId(Dict):
    message_id: Optional[str] = None

    def __repr__(self):
        return self.to_json()


@dataclass
class Update(Dict):
    client: Optional["rubigram.Client"] = None
    type: Optional[Literal["NewMessage", "UpdatedMessage", "RemovedMessage", "StartedBot", "StoppedBot", "UpdatedPayment"]] = None
    chat_id: Optional[str] = None
    removed_message_id: Optional[str] = None
    new_message: Optional[Message] = None
    updated_message: Optional[Message] = None
    updated_payment: Optional[PaymentStatus] = None

    def __str__(self):
        return self.to_json()

    async def send_text(self, text: str,) -> "MessageId":
        return await self.client.send_message(self.chat_id, text)

    async def download(self, name: str):
        return await self.client.download_file(self.new_message.file.file_id, name)

    async def reply(
        self,
        text: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Literal["New", "Remove"] = None,
        disable_notification: bool = None,
    ) -> "MessageId":
        return await self.client.send_message(self.chat_id, text, chat_keypad, inline_keypad, chat_keypad_type, disable_notification, self.new_message.message_id)

    async def reply_file(
        self,
        file: str,
        file_name: str,
        caption: str = None,
        type: Literal["File", "Image", "Voice", "Music", "Gif", "Video"] = "File",
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Literal["New", "Remove"] = None,
        disable_notification: bool = False,
    ) -> "MessageId":
        return await self.client.send_file(self.chat_id, file, file_name, caption, type, chat_keypad, inline_keypad, chat_keypad_type, disable_notification, self.new_message.message_id)

    async def reply_document(self, document: str, name: str, caption: Optional[str] = None, **kwargs) -> "MessageId":
        return await self.reply_file(document, name, caption, "File", **kwargs)

    async def reply_photo(self, photo: str, name: str, caption: Optional[str] = None, **kwargs) -> "MessageId":
        return await self.reply_file(photo, name, caption, "Image", **kwargs)

    async def reply_video(self, video: str, name: str, caption: Optional[str] = None, **kwargs) -> "MessageId":
        return await self.reply_file(video, name, caption, "Video", **kwargs)

    async def reply_gif(self, gif: str, name: str, caption: Optional[str] = None, **kwargs) -> "MessageId":
        return await self.reply_file(gif, name, caption, "Gif", **kwargs)

    async def reply_music(self, music: str, name: str, caption: Optional[str] = None, **kwargs) -> "MessageId":
        return await self.reply_file(music, name, caption, "Music", **kwargs)

    async def reply_voice(self, voice: str, name: str, caption: Optional[str] = None, **kwargs) -> "MessageId":
        return await self.reply_file(voice, name, caption, "Voice", **kwargs)


@dataclass
class Updates(Dict):
    updates: list[Update] = None
    next_offset_id: Optional[str] = None

    def __repr__(self):
        return self.to_json()