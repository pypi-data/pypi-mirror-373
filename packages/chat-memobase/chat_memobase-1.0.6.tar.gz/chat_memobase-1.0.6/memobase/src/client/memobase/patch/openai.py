import threading
import asyncio
import json
from typing import AsyncGenerator, Union
from openai import AzureOpenAI, AsyncAzureOpenAI
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from openai._streaming import Stream, AsyncStream
from ..core.entry import MemoBaseClient, User, ChatBlob
from ..core.user import UserProfile
from ..utils import string_to_uuid, LOG
from ..error import ServerError

PROMPT = """

--# ADDITIONAL INFO #--
{user_context}
{additional_memory_prompt}
--# DONE #--"""


def openai_memory(
    openai_client: AzureOpenAI,
    mb_client: MemoBaseClient,
    additional_memory_prompt: str = "Make sure the user's query needs the memory, otherwise just return the answer directly.",
    max_context_size: int = 1000,
) -> AzureOpenAI:
    if hasattr(openai_client, "_memobase_patched"):
        return openai_client

    openai_client._memobase_patched = True
    openai_client.get_profile = _get_profile(mb_client)
    openai_client.get_memory_prompt = _get_memory_prompt(
        mb_client, max_context_size, additional_memory_prompt
    )
    openai_client.flush = _flush(mb_client)
    if isinstance(openai_client, AzureOpenAI):
        openai_client.chat.completions.create = _sync_chat(
            openai_client, mb_client, additional_memory_prompt, max_context_size
        )
    # elif isinstance(openai_client, AsyncOpenAI):
    #     raise ValueError(f"AsyncOpenAI is not supported yet")
    else:
        raise ValueError(f"Invalid openai_client type: {type(openai_client)}")
    return openai_client


def _get_profile(mb_client: MemoBaseClient):
    def get_profile(u_string) -> list[UserProfile]:
        uid = string_to_uuid(u_string)
        return mb_client.get_user(uid, no_get=True).profile()

    return get_profile


def _get_memory_prompt(
    mb_client: MemoBaseClient,
    max_context_size: int = 1000,
    additional_memory_prompt: str = "",
):
    def get_memory(u_string) -> list[UserProfile]:
        uid = string_to_uuid(u_string)
        u = mb_client.get_user(uid, no_get=True)
        context = u.context(max_token_size=max_context_size)
        sys_prompt = PROMPT.format(
            user_context=context, additional_memory_prompt=additional_memory_prompt
        )
        return sys_prompt

    return get_memory


def _flush(mb_client: MemoBaseClient):
    def flush(u_string) -> list[UserProfile]:
        uid = string_to_uuid(u_string)
        return mb_client.get_user(uid, no_get=True).flush()

    return flush


def add_message_to_user(messages: ChatBlob, user: User):
    try:
        r = user.insert(messages)
        LOG.debug(f"Insert {messages}")
    except ServerError as e:
        LOG.error(f"Failed to insert message: {e}")


def user_context_insert(
    messages, u: User, additional_memory_prompt: str, max_context_size: int
):
    context = u.context(max_token_size=max_context_size)
    if not len(context):
        return messages
    sys_prompt = PROMPT.format(
        user_context=context, additional_memory_prompt=additional_memory_prompt
    )
    if messages[0]["role"] == "system":
        messages[0]["content"] += sys_prompt
    else:
        messages.insert(0, {"role": "system", "content": sys_prompt.strip()})
    return messages


def _sync_chat(
    client: AzureOpenAI,
    mb_client: MemoBaseClient,
    additional_memory_prompt: str,
    max_context_size: int = 1000,
):
    _create_chat = client.chat.completions.create

    def sync_chat(*args, **kwargs) -> ChatCompletion | Stream[ChatCompletionChunk]:
        is_streaming = kwargs.get("stream", False)
        if kwargs.get("user_id", None) is None:
            kwargs.pop("user_id")
            if not is_streaming:
                return _create_chat(*args, **kwargs)
            else:
                return (r for r in _create_chat(*args, **kwargs))

        user_id = string_to_uuid(kwargs.pop("user_id"))
        user_query = kwargs["messages"][-1]
        if user_query["role"] != "user":
            LOG.warning(f"Last query is not user query: {user_query}")
            if not is_streaming:
                return _create_chat(*args, **kwargs)
            else:
                return (r for r in _create_chat(*args, **kwargs))

        u = mb_client.get_or_create_user(user_id)
        kwargs["messages"] = user_context_insert(
            kwargs["messages"], u, additional_memory_prompt, max_context_size
        )
        response = _create_chat(*args, **kwargs)

        # --- 为同步函数也添加了健壮性修复 ---
        user_content = user_query["content"]
        if isinstance(user_content, list):
            user_content_for_db = json.dumps(user_content, ensure_ascii=False)
        else:
            user_content_for_db = user_content
        # --- 修复结束 ---

        if is_streaming:
            def yield_response_and_log():
                total_response = ""
                r_role = None
                for r in response:
                    yield r
                    try:
                        r_string = r.choices[0].delta.content
                        r_role = r_role or r.choices[0].delta.role
                        total_response += r_string or ""
                    except Exception:
                        continue
                if not len(total_response):
                    return
                if r_role != "assistant":
                    LOG.warning(f"Last response is not assistant response: {r_role}")
                    return response

                messages = ChatBlob(messages=[
                    {"role": "user", "content": user_content_for_db},
                    {"role": "assistant", "content": total_response},
                ])
                threading.Thread(target=add_message_to_user, args=(messages, u)).start()

            return yield_response_and_log()
        else:
            r_role = response.choices[0].message.role
            if r_role != "assistant":
                LOG.warning(f"Last response is not assistant response: {r_role}")
                return response
            r_string = response.choices[0].message.content or ""
            messages = ChatBlob(messages=[
                {"role": "user", "content": user_content_for_db},
                {"role": "assistant", "content": r_string},
            ])
            threading.Thread(target=add_message_to_user, args=(messages, u)).start()
            return response

    return sync_chat


# --- 修改后的异步函数 _async_chat ---
def _async_chat(
        client: AsyncAzureOpenAI,
        mb_client: MemoBaseClient,
        additional_memory_prompt: str,
        max_context_size: int = 1000,
):
    _create_chat = client.chat.completions.create

    async def async_chat(*args, **kwargs) -> Union[ChatCompletion, AsyncStream[ChatCompletionChunk]]:
        is_streaming = kwargs.get("stream", False)
        if kwargs.get("user_id", None) is None:
            kwargs.pop("user_id", None)
            return await _create_chat(*args, **kwargs)

        user_id = string_to_uuid(kwargs.pop("user_id"))
        user_query = kwargs["messages"][-1]
        if user_query["role"] != "user":
            LOG.warning(f"Last query is not user query: {user_query}")
            return await _create_chat(*args, **kwargs)

        u = mb_client.get_or_create_user(user_id)
        kwargs["messages"] = user_context_insert(
            kwargs["messages"], u, additional_memory_prompt, max_context_size
        )
        response = await _create_chat(*args, **kwargs)

        # <-- 2. 在创建 ChatBlob 之前，统一处理用户的 content -->
        user_content = user_query["content"]
        if isinstance(user_content, list):
            user_content_for_db = json.dumps(user_content, ensure_ascii=False)
        else:
            user_content_for_db = user_content
        # <-- 处理结束 -->

        if is_streaming:
            async def yield_response_and_log() -> AsyncGenerator[ChatCompletionChunk, None]:
                total_response = ""
                r_role = None
                async for r in response:
                    yield r
                    try:
                        r_string = r.choices[0].delta.content
                        r_role = r_role or r.choices[0].delta.role
                        total_response += r_string or ""
                    except Exception:
                        continue
                if not len(total_response): return
                if r_role != "assistant":
                    LOG.warning(f"Last response is not assistant response: {r_role}")
                    return

                # <-- 3. 使用处理后的 user_content_for_db -->
                messages = ChatBlob(messages=[
                    {"role": "user", "content": user_content_for_db},
                    {"role": "assistant", "content": total_response},
                ])
                asyncio.create_task(asyncio.to_thread(add_message_to_user, messages, u))

            return yield_response_and_log()
        else:
            r_role = response.choices[0].message.role
            if r_role != "assistant":
                LOG.warning(f"Last response is not assistant response: {r_role}")
                return response
            r_string = response.choices[0].message.content
