# from dataclasses import asdict, is_dataclass
# import os
# import asyncio
# from typing import Any, Awaitable, Dict, List, Optional, Union
# import sys
# import json
# import socketio
# from .bot_types import *

# # if len(sys.argv) > 1:
# #     arguments = sys.argv[1:]
# #     print("Arguments:", arguments)
# # else:
# #     print("No arguments provided.")

# app_host = os.environ.get("APP_HOST", "localhost:3000")
# token = sys.argv[1]
# data = json.loads(sys.argv[2])
# params = data.get("params")
# sio = socketio.AsyncClient()
# context = {
#     "botId": data["botId"],
#     "botCodeId": data["botCodeId"],
#     "conversationId": data["conversationId"],
#     "conversationThreadId": data["conversationThreadId"],
#     "chargeUserIds": data["chargeUserIds"],
# }


# @sio.event
# async def connect():
#     old_print("[BOT] connection established")


# @sio.event
# async def disconnect():
#     old_print("[BOT] disconnected from server")


# @sio.event
# async def callback(msg):
#     funcName = msg.get("func")
#     funcParams = msg.get("params")
#     func = funcs.get(funcName)
#     if func is not None:
#         return await func(**funcParams)
#     else:
#         return None


# async def main():
#     # print("[BOT] start client socket", app_url)
#     await sio.connect(f"ws://{app_host}/", auth={"token": token}, retry=True)
#     while True:
#         message = sys.stdin.readline()[:-1]
#         if len(message) > 0:
#             # print("[MESSAGE]", message)
#             msg = json.loads(message)
#             func = funcs.get(msg.get("func"))
#             if func is not None:
#                 await func(**msg.get("params"))


# def start():
#     asyncio.run(main())


# async def call(op: str, params: dict) -> Awaitable[dict]:
#     # print("[BOT] client socket send", op, context, params)
#     result = await sio.call(
#         "call",
#         {
#             "op": op,
#             "input": {
#                 "context": context,
#                 "params": params,
#             },
#         },
#     )
#     # print("[BOT] client socket send result", result)
#     return result.get("data")


# async def conversation(id: str) -> Optional[Conversation]:
#     result = await call(
#         "botCodeConversationGet",
#         {
#             "id": id,
#         },
#     )
#     return Conversation(**result) if result is not None else None


# async def user(id: str) -> Optional[User]:
#     result = await call(
#         "botCodeUserGet",
#         {
#             "id": id,
#         },
#     )
#     return User(**result) if result is not None else None


# async def user_private(id: str) -> Optional[UserPrivate]:
#     result = await call(
#         "botCodeUserPrivateGet",
#         {
#             "id": id,
#         },
#     )
#     return UserPrivate(**result) if result is not None else None


# async def live_user(id: str) -> Optional[LiveUser]:
#     result = await call(
#         "botCodeLiveUserGet",
#         {
#             "id": id,
#         },
#     )
#     return LiveUser(**result) if result is not None else None


# async def bot(id: str) -> Optional[Bot]:
#     result = await call(
#         "botCodeBotGet",
#         {
#             "id": id,
#         },
#     )
#     return Bot(**result) if result is not None else None


# async def bot_owners(id: str) -> List[str]:
#     return await call(
#         "botCodeBotOwnersGet",
#         {"id": id},
#     )


# async def message_typing() -> None:
#     await call(
#         "botCodeMessageTyping",
#         {},
#     )


# async def message_send(
#     id: Optional[str] = None,
#     text: Optional[str] = None,
#     images: Optional[List[Union[ImageBase64Result, ImageUriResult, None]]] = None,
#     markdown: Optional[str] = None,
#     mention_user_ids: Optional[List[str]] = None,
#     only_user_ids: Optional[List[str]] = None,
#     lang: Optional[UserLang] = None,
#     visibility: Optional[MessageVisibility] = None,
#     color: Optional[MessageColor] = None,
#     buttons: Optional[List[MessageButton]] = None,
#     mood: Optional[Mood] = None,
#     impersonate_user_id: Optional[str] = None,
#     files: Optional[List[File]] = None,
#     thread: Optional[Thread] = None,
# ) -> Message:
#     return Message(
#         **await call(
#             "botCodeMessageSend",
#             {
#                 "id": id,
#                 "text": text,
#                 "markdown": markdown,
#                 "images": images,
#                 "mentionUserIds": mention_user_ids,
#                 "onlyUserIds": only_user_ids,
#                 "lang": lang,
#                 "visibility": visibility,
#                 "color": color,
#                 "buttons": buttons,
#                 "mood": mood,
#                 "impersonateUserId": impersonate_user_id,
#                 "fileIds": files,
#                 "thread": thread,
#             },
#         )
#     )


# async def message_edit(
#     id: str, text: Optional[str] = None, markdown: Optional[str] = None
# ) -> Message:
#     return Message(
#         **await call(
#             "botCodeMessageEdit",
#             {
#                 "id": id,
#                 "text": text,
#                 "markdown": markdown,
#             },
#         )
#     )


# async def messages_to_text(
#     messages: List[Message], strip_names: Optional[bool] = None
# ) -> str:
#     return await call(
#         "botCodeMessagesToText",
#         {
#             "messages": messages,
#             "stripNames": strip_names,
#         },
#     )


# async def message_history(
#     duration: Optional[int] = None,
#     limit: Optional[int] = None,
#     start: Optional[int] = None,
#     include_hidden: Optional[bool] = None,
#     thread_id: Optional[str] = None,
# ) -> List[Message]:
#     result = await call(
#         "botCodeMessageHistory",
#         {
#             "duration": duration,
#             "limit": limit,
#             "start": start,
#             "include_hidden": include_hidden,
#             "thread_id": thread_id,
#         },
#     )

#     return list(map(lambda m: Message(**m), result))


# async def text_gen(
#     question: Optional[str] = None,
#     instruction: Optional[str] = None,
#     messages: Optional[List[Union[TextGenMessage, Message]]] = None,
#     model: Optional[TextGenModel] = None,
#     temperature: Optional[float] = None,
#     top_k: Optional[int] = None,
#     top_p: Optional[float] = None,
#     max_tokens: Optional[int] = None,
#     frequency_penalty: Optional[float] = None,
#     presence_penalty: Optional[float] = None,
#     repetition_penalty: Optional[float] = None,
#     tools: Optional[List[TextGenTool]] = None,
#     include_files: Optional[bool] = None,
#     json: Optional[Dict[str, Any]] = None,
# ) -> str:
#     return await call(
#         "botCodeTextGen",
#         {
#             "question": question,
#             "instruction": instruction,
#             "messages": (
#                 list(map(lambda x: asdict(x), messages))
#                 if messages is not None
#                 else None
#             ),
#             "model": model,
#             "temperature": temperature,
#             "topK": top_k,
#             "topP": top_p,
#             "maxTokens": max_tokens,
#             "frequencyPenalty": frequency_penalty,
#             "presencePenalty": presence_penalty,
#             "repetitionPenalty": repetition_penalty,
#             "tools": tools,
#             "includeFiles": include_files,
#             "json": json,
#         },
#     )


# async def query_files(
#     query: str,
#     scope: Optional[str] = None,
#     catalog_ids: Optional[List[str]] = None,
#     limit: Optional[int] = None,
# ) -> List[FileChunk]:
#     result = await call(
#         "botCodeQueryFiles",
#         {
#             "query": query,
#             "scope": scope,
#             "catalogIds": catalog_ids,
#             "limit": limit,
#         },
#     )

#     return list(map(lambda m: FileChunk(**m), result))


# async def query_news(
#     query: str, created: Optional[int] = None, limit: Optional[int] = None
# ) -> List[NewsArticle]:
#     result = await call(
#         "botCodeQueryNews",
#         {
#             "query": query,
#             "created": created,
#             "limit": limit,
#         },
#     )

#     return list(map(lambda m: NewsArticle(**m), result))


# async def image_gen(
#     prompt: str,
#     model: Optional[ImageGenModel] = None,
#     negative_prompt: Optional[str] = None,
#     size: Optional[ImageGenSize] = None,
#     guidance_scale: Optional[float] = None,
#     steps: Optional[int] = None,
#     image: Optional[Image] = None,
#     image_strength: Optional[float] = None,
# ) -> Optional[ImageBase64Result]:
#     result = await call(
#         "botCodeImageGen",
#         {
#             "prompt": prompt,
#             "model": model,
#             "negativePrompt": negative_prompt,
#             "size": size,
#             "guidanceScale": guidance_scale,
#             "steps": steps,
#             "image": image,
#             "imageStrength": image_strength,
#         },
#     )
#     return ImageBase64Result(**result) if result is not None else None


# async def google_search(query: str) -> List[SearchArticle]:
#     result = await call(
#         "botCodeGoogleSearch",
#         {
#             "query": query,
#         },
#     )

#     return list(map(lambda m: SearchArticle(**m), result))


# async def email_send(
#     user_id: Optional[str] = None,
#     user_ids: Optional[List[str]] = None,
#     subject: Optional[str] = None,
#     text: Optional[str] = None,
#     markdown: Optional[str] = None,
#     file_id: Optional[str] = None,
# ) -> None:
#     await call(
#         "botCodeEmailSend",
#         {
#             "userId": user_id,
#             "userIds": user_ids,
#             "subject": subject,
#             "text": text,
#             "markdown": markdown,
#             "fileId": file_id,
#         },
#     )


# async def conversation_users(
#     type: Optional[str] = None, role: Optional[str] = None
# ) -> List[User]:
#     result = await call(
#         "botCodeConversationUsers",
#         {"type": type, "role": role},
#     )

#     return list(map(lambda m: User(**m), result))


# async def conversation_bots(tag: Optional[BotTag] = None) -> List[Bot]:
#     result = await call(
#         "botCodeConversationBots",
#         {
#             "tag": tag,
#         },
#     )

#     return list(map(lambda m: Bot(**m), result))


# async def conversation_show_content(content: ConversationContent) -> None:
#     await call(
#         "botCodeConversationShowContent",
#         content,
#     )


# async def conversation_show_buttons(
#     user_id: Optional[str] = None, buttons: Optional[List[MessageButton]] = None
# ) -> None:
#     await call(
#         "botCodeConversationShowButtons",
#         {
#             "userId": user_id,
#             "buttons": buttons,
#         },
#     )


# async def conversation_participants(type: Optional[str] = None) -> List[User]:
#     result = await call(
#         "botCodeConversationParticipants",
#         {
#             "type": type,
#         },
#     )

#     return list(map(lambda m: User(**m), result))


# async def file_create(
#     type: FileType,
#     title: str,
#     markdown: Optional[str] = None,
#     uri: Optional[str] = None,
#     thumbnail: Optional[Union[ImageBase64Result, ImageUriResult]] = None,
#     lang: Optional[UserLang] = None,
#     indexable: Optional[bool] = None,
#     message_send: Optional[bool] = None,
#     add_to_conversation: Optional[bool] = None,
#     add_to_feed: Optional[bool] = None,
#     send_notification: Optional[bool] = None,
# ) -> File:
#     return File(
#         **await call(
#             "botCodeFileCreate",
#             {
#                 "type": type,
#                 "title": title,
#                 "markdown": markdown,
#                 "uri": uri,
#                 "thumbnail": thumbnail,
#                 "lang": lang,
#                 "indexable": indexable,
#                 "messageSend": message_send,
#                 "addToConversation": add_to_conversation,
#                 "addToFeed": add_to_feed,
#                 "sendNotification": send_notification,
#             },
#         )
#     )


# async def file_update(
#     id: str,
#     markdown: Optional[str] = None,
#     title: Optional[str] = None,
#     thumbnail: Optional[Image] = None,
# ) -> None:
#     await call(
#         "botCodeFileUpdate",
#         {
#             "id": id,
#             "title": title,
#             "markdown": markdown,
#             "thumbnail": thumbnail,
#         },
#     )


# async def file_to_text_gen_message(
#     file: File,
#     role: Optional[TextGenRole] = None,
#     include_name: Optional[bool] = None,
#     text: Optional[str] = None,
# ) -> TextGenMessage:
#     return TextGenMessage(
#         **await call(
#             "botCodeFileToTextGenMessage",
#             {
#                 "file": file,
#                 "role": role,
#                 "includeName": include_name,
#                 "text": text,
#             },
#         )
#     )


# async def markdown_create_image(
#     file_id: str, image: Union[ImageBase64Result, ImageUriResult]
# ) -> str:
#     return await call(
#         "botCodeMarkdownCreateImage",
#         {
#             "file_id": file_id,
#             "image": image,
#         },
#     )


# async def data_set(**kwargs) -> dict:
#     return await call(
#         "botCodeDataSet",
#         kwargs,
#     )


# async def data() -> dict:
#     return await call(
#         "botCodeDataGet",
#         {},
#     )


# async def bot_search(query: str, limit: Optional[int] = None) -> List[Bot]:
#     result = await call(
#         "botCodeBotSearch",
#         {"query": query, "limit": limit},
#     )

#     return list(map(lambda m: Bot(**m), result))


# old_print = print


# def log(
#     *args: list[Any],
# ) -> List[Bot]:
#     old_print(args)
#     asyncio.create_task(
#         call(
#             "botCodeLog",
#             {
#                 "type": "log",
#                 "args": list(map(lambda x: asdict(x) if is_dataclass(x) else x, args)),
#             },
#         )
#     )


# print = log


# def error(
#     *args: list[Any],
# ) -> List[Bot]:
#     asyncio.create_task(
#         call(
#             "botCodeLog",
#             {
#                 "type": "error",
#                 "args": list(map(lambda x: asdict(x) if is_dataclass(x) else x, args)),
#             },
#         )
#     )
