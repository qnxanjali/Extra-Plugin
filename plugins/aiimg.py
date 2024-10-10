import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from io import BytesIO
from VIPMUSIC import app

# Function to generate buttons for model selection (2x3 format)
def generate_buttons(prompt):
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("ᴀɴɪᴍᴇ", callback_data=f"anime:{prompt}"),
                InlineKeyboardButton("𝟹ᴅ ʀᴇɴᴅᴇʀ", callback_data=f"3d:{prompt}")
            ],
            [
                InlineKeyboardButton("ʀᴇᴀʟᴄᴀʀᴛᴏᴏɴ𝟹ᴅ", callback_data=f"realcartoon:{prompt}"),
                InlineKeyboardButton("Dɪsɴᴇʏ", callback_data=f"disney:{prompt}")
            ],
            [
                InlineKeyboardButton("ʀᴇᴀʟɪsᴛɪᴄ", callback_data=f"realistic:{prompt}")  # New button
            ]
        ]
    )
    return buttons

# Function to get images from the API
def get_images(api_url, count=1):
    images = []
    for _ in range(count):
        response = requests.get(api_url)
        response.raise_for_status()
        image_url = response.json().get('image')
        if image_url:
            img_response = requests.get(image_url)
            img = BytesIO(img_response.content)
            images.append(img)
    return images

# Function to create "💥 Rᴇɢᴇɴᴇʀᴀᴛᴇ 💥" and "❌ Cʟᴏsᴇ ❌" buttons in 2x2 format
def regenerate_button(model, prompt):
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("💥 ʀᴇɢᴇɴᴇʀᴀᴛᴇ 💥", callback_data=f"regenerate:{model}:{prompt}"),
                InlineKeyboardButton("❌ ᴄʟᴏsᴇ ❌", callback_data="close")
            ]
        ]
    )
    return buttons

# Function to get images from the API
def get_images(api_url, count=4):
    images = []
    for _ in range(count):
        response = requests.get(api_url)
        response.raise_for_status()
        image_url = response.json().get('image')
        if image_url:
            img_response = requests.get(image_url)
            img = BytesIO(img_response.content)
            images.append(img)
    return images

# Function to create buttons for regeneration and closing
def regeneration_buttons(model, prompt):
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎉 ʀᴇɢᴇɴᴇʀᴀᴛᴇ 🎉", callback_data=f"regenerate:{model}:{prompt}"),
             InlineKeyboardButton("❌ ᴄʟᴏsᴇ ❌", callback_data=f"close:{model}:{prompt}")]
        ]
    )
    return buttons

# Command handler for image generation
@app.on_message(filters.command(["make", "ake"], prefixes=["/", "!", ".", "M", "m"]))
async def handle_image_generation(client, message):
    prompt = ' '.join(message.command[1:])
    if not prompt:
        await message.reply_text('ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴘʀᴏᴍᴘᴛ.')
        return
    buttons = generate_buttons(prompt)
    await message.reply_text("Please select an image style:", reply_markup=buttons)

# Callback handler for button presses
@app.on_callback_query()
async def callback_query_handler(client, callback_query):
    data = callback_query.data
    parts = data.split(":")

    if len(parts) == 2:  # For the first image generation buttons
        filter_type, prompt = parts
    elif len(parts) == 3:  # For the regenerate button
        _, filter_type, prompt = parts

    # Display a waiting message with an hourglass emoji
    wait_message = await callback_query.message.edit_text("⏳")

    # Determine the API URL based on the model selected
    if filter_type == "anime":
        api_url = f"https://anime-img.codesearch.workers.dev/prompt={prompt}"
        model_name = "ᴀɴɪᴍᴇ"
    elif filter_type == "3d":
        api_url = f"https://3d-image.codesearch.workers.dev/prompt={prompt}"
        model_name = "𝟹ᴅ ʀᴇɴᴅᴇʀ"
    elif filter_type == "realcartoon":
        api_url = f"https://text2img.codesearch.workers.dev/prompt={prompt}"
        model_name = "ʀᴇᴀʟᴄᴀʀᴛᴏᴏɴ𝟹ᴅ"
    elif filter_type == "disney":
        api_url = f"https://disney-img.codesearch.workers.dev/prompt={prompt}"
        model_name = "ᴅɪsɴᴇʏ"
    elif filter_type == "realistic":
        api_url = f"https://realism-img.codesearch.workers.dev/prompt={prompt}"
        model_name = "ʀᴇᴀʟɪsᴛɪᴄ"
    else:
        await callback_query.message.reply_text("Invalid option selected.")
        return

    try:
        # Get 4 distinct images from the API
        images = get_images(api_url, count=4)

        # Remove the 'Generating' message
        await client.delete_messages(chat_id=callback_query.message.chat.id, message_ids=wait_message.id)

        if images:
            media_group = []

            # Prepare the images for sending in one message
            for img in images:
                media_group.append(InputMediaPhoto(img))

            # Send all images in one message
            await client.send_media_group(chat_id=callback_query.message.chat.id, media=media_group)

            # Add regenerate and close buttons
            regenerate_markup = regeneration_buttons(filter_type, prompt)

            # Send details and regenerate button in the same message
            model_text = f"ᴍᴏᴅᴇʟ: {model_name}\n"
            prompt_text = f"ᴘʀᴏᴍᴘᴛ: `{prompt}`\n"
            user_text = f"ʀᴇǫᴜɪʀᴇᴅ ʙʏ: {callback_query.from_user.mention}\n"

            caption = f"{model_text}\n{prompt_text}\n{user_text}"

            await callback_query.message.reply_text(caption, reply_markup=regenerate_markup)
        else:
            await callback_query.message.reply_text("No image found.")
    except Exception as e:
        await callback_query.message.reply_text(f"An error occurred: {e}")