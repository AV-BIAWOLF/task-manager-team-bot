from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import json

# Initialize the bot
# app = Client("task_bot", config_file="config.ini")
app = Client(
    "task_bot",
    api_id=21747498,          # Replace with your actual API ID
    api_hash="041bafbce78896c14c393d21ecd91320",     # Replace with your actual API Hash
    bot_token="7583230231:AAG6KXRB4Ve0y2cSpZDpwsvMaCjIxaMxKgs" # 7583230231:AAG6KXRB4Ve0y2cSpZDpwsvMaCjIxaMxKgs"    # Replace with your bot token
)


# Dictionary to store tasks
tasks = {}

# Helper function to save tasks to a file (optional for persistence)
def save_tasks():
    with open("tasks.json", "w") as file:
        json.dump(tasks, file)

# Load tasks from file on startup (optional for persistence)
def load_tasks():
    global tasks
    try:
        with open("tasks.json", "r") as file:
            tasks = json.load(file)
    except FileNotFoundError:
        tasks = {}

load_tasks()

# Command: Start the bot (bot must be added to a group chat first)
@app.on_message(filters.command("start") & filters.group)
async def start_bot(client, message: Message):
    buttons = [
        [InlineKeyboardButton("New task", callback_data="newtask")],
        [InlineKeyboardButton("Task list", callback_data="listtasks")]
    ]
    await message.reply("Hello! I'm here to help manage your tasks. Use /newtask to create a task or press button "
                        "'New task':", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query()
async def handle_callback_query(client: Client, query: CallbackQuery):
    if query.data == "newtask":
        await query.message.reply("Please use the format: `/newtask Task Name - Task Description`")
    elif query.data == "listtasks":
        # await query.message.reply("Use noramal format")
        await list_tasks(client, query.message)


# Command: Create a new task
@app.on_message(filters.command("newtask") & filters.group)
async def new_task(client, message: Message):
    chat_id = str(message.chat.id)
    task_data = message.text.split(" ", 2)

    if len(task_data) < 3:
        await message.reply("Please use the format: `/newtask Task Name - Task Description`")
        return

    task_name = task_data[1]
    task_description = task_data[2]

    if chat_id not in tasks:
        tasks[chat_id] = []

    task = {
        "name": task_name,
        "description": task_description,
        "status": "waiting",
        "assigned_to": None
    }

    tasks[chat_id].append(task)
    save_tasks()
    await message.reply(f"Task '{task_name}' has been created.")

# Command: Assign a task to a user
@app.on_message(filters.command("assigntask") & filters.group)
async def assign_task(client, message: Message):
    chat_id = str(message.chat.id)
    task_data = message.text.split(" ", 3)

    if len(task_data) < 3: # 4
        await message.reply("Please use the format: `/assigntask TaskName @username`")
        return

    task_name = task_data[1]
    assigned_to = task_data[2]

    for task in tasks.get(chat_id, []):
        if task["name"] == task_name:
            task["assigned_to"] = assigned_to
            save_tasks()
            await message.reply(f"Task '{task_name}' has been assigned to {assigned_to}.")
            return

    await message.reply(f"No task found with the name '{task_name}'.")



# Command: List all tasks
@app.on_message(filters.command("listtasks") & filters.group)
async def list_tasks(client, message: Message):
    chat_id = str(message.chat.id)
    if chat_id not in tasks or not tasks[chat_id]:
        await message.reply("No tasks found.")
        return

    task_list = "Tasks:\n"
    for task in tasks[chat_id]:
        task_list += f"- {task['name']} [{task['status']}]\n"
        task_list += f"  Description: {task['description']}\n"
        if task["assigned_to"]:
            task_list += f"  Assigned to: {task['assigned_to']}\n"

    await message.reply(task_list)

# Command: Change task status
@app.on_message(filters.command("updatestatus") & filters.group)
async def update_status(client, message: Message):
    chat_id = str(message.chat.id)
    task_data = message.text.split(" ", 3)

    if len(task_data) < 3: # 4
        await message.reply("Please use the format: `/updatestatus TaskName new_status`")
        return

    task_name = task_data[1]
    new_status = task_data[2]

    if new_status not in ["waiting", "process", "done"]:
        await message.reply("Status must be one of: waiting, process, done.")
        return

    for task in tasks.get(chat_id, []):
        if task["name"] == task_name:
            task["status"] = new_status
            save_tasks()
            await message.reply(f"Task '{task_name}' status updated to {new_status}.")
            # Remove task if marked as done
            if new_status == "done":
                tasks[chat_id].remove(task)
            return

    await message.reply(f"No task found with the name '{task_name}'.")

# Command: Delete a task
@app.on_message(filters.command("deletetask") & filters.group)
async def delete_task(client, message: Message):
    chat_id = str(message.chat.id)
    task_data = message.text.split(" ", 2)

    if len(task_data) < 2:
        await message.reply("Please use the format: `/deletetask TaskName`")
        return

    task_name = task_data[1]

    for task in tasks.get(chat_id, []):
        if task["name"] == task_name:
            tasks[chat_id].remove(task)
            save_tasks()
            await message.reply(f"Task '{task_name}' has been deleted.")
            return

    await message.reply(f"No task found with the name '{task_name}'.")

# Run the bot
app.run()