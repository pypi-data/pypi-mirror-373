"""
The MIT License (MIT)

Copyright (c) 2023 pkjmesra

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import asyncio
import json
import logging
import os
import tempfile
import zipfile
from typing import Optional, Tuple

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, Updater, CallbackContext


class PKTickBot:
    """Telegram bot that sends zipped ticks.json file on command"""

    # Telegram file size limits (50MB for documents)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

    def __init__(
        self, bot_token: str, ticks_file_path: str, chat_id: Optional[str] = None
    ):
        self.bot_token = bot_token
        self.ticks_file_path = ticks_file_path
        self.chat_id = chat_id
        self.updater = None
        self.logger = logging.getLogger(__name__)

    def start(self, update: Update, context: CallbackContext) -> None:
        """Send welcome message"""
        update.message.reply_text(
            "📊 PKTickBot is running!\n"
            "Use /ticks to get the latest market data JSON file (zipped)\n"
            "Use /status to check bot status\n"
            "Use /help for more information"
        )

    def help_command(self, update: Update, context: CallbackContext) -> None:
        """Send help message"""
        update.message.reply_text(
            "🤖 PKTickBot Commands:\n"
            "/start - Start the bot\n"
            "/ticks - Get zipped market data file\n"
            "/status - Check bot and data status\n"
            "/help - Show this help message\n\n"
            "📦 Files are automatically compressed to reduce size. "
            "If the file is too large, it will be split into multiple parts."
        )

    def create_zip_file(self, json_path: str) -> Tuple[str, int]:
        """Create a zip file from JSON and return (zip_path, file_size)"""
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_zip:
            zip_path = tmp_zip.name

        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(json_path, os.path.basename(json_path))

            file_size = os.path.getsize(zip_path)
            return zip_path, file_size

        except Exception as e:
            self.logger.error(f"Error creating zip file: {e}")
            # Clean up on error
            if os.path.exists(zip_path):
                os.unlink(zip_path)
            raise

    def split_large_file(self, file_path: str, max_size: int) -> list:
        """Split large file into multiple parts and return list of part paths"""
        part_paths = []
        part_num = 1

        try:
            with open(file_path, "rb") as src_file:
                while True:
                    part_filename = f"{file_path}.part{part_num}"
                    with open(part_filename, "wb") as part_file:
                        data = src_file.read(max_size)
                        if not data:
                            break
                        part_file.write(data)

                    part_paths.append(part_filename)
                    part_num += 1

            return part_paths

        except BaseException:
            # Clean up any created parts on error
            for part_path in part_paths:
                if os.path.exists(part_path):
                    os.unlink(part_path)
            raise

    def send_zipped_ticks(self, update: Update, context: CallbackContext) -> None:
        """Send zipped ticks.json file to user with size handling"""
        try:
            if not os.path.exists(self.ticks_file_path):
                update.message.reply_text(
                    "❌ ticks.json file not found yet. Please wait for data to be collected."
                )
                return

            file_size = os.path.getsize(self.ticks_file_path)
            if file_size == 0:
                update.message.reply_text(
                    "⏳ ticks.json file is empty. Data collection might be in progress."
                )
                return

            # Create zip file
            zip_path, zip_size = self.create_zip_file(self.ticks_file_path)

            try:
                if zip_size <= self.MAX_FILE_SIZE:
                    # Send single file
                    with open(zip_path, "rb") as f:
                        update.message.reply_document(
                            document=f,
                            filename="market_ticks.zip",
                            caption=f"📈 Latest market data (compressed)\nOriginal: {file_size:,} bytes → Zipped: {zip_size:,} bytes",
                        )
                    self.logger.info("Sent zipped ticks file to user")

                else:
                    # File too large, need to split
                    update.message.reply_text(
                        f"📦 File is too large ({zip_size:,} bytes). Splitting into parts..."
                    )

                    part_paths = self.split_large_file(zip_path, self.MAX_FILE_SIZE)

                    for i, part_path in enumerate(part_paths, 1):
                        with open(part_path, "rb") as f:
                            update.message.reply_document(
                                document=f,
                                filename=f"market_ticks.part{i}.zip",
                                caption=f"Part {i} of {len(part_paths)}",
                            )
                        self.logger.info(f"Sent part {i} of {len(part_paths)}")

                    update.message.reply_text(
                        "✅ All parts sent! To reconstruct:\n"
                        + "1. Download all parts\n"
                        + "2. Run: `cat market_ticks.part*.zip > market_ticks.zip`\n"
                        + "3. Unzip: `unzip market_ticks.zip`"
                    )

            finally:
                # Clean up temporary files
                if os.path.exists(zip_path):
                    os.unlink(zip_path)
                # Clean up any part files if they exist
                for part_path in self.find_part_files(zip_path):
                    if os.path.exists(part_path):
                        os.unlink(part_path)

        except Exception as e:
            self.logger.error(f"Error sending zipped ticks file: {e}")
            update.message.reply_text(
                "❌ Error preparing or sending file. Please try again later."
            )

    def find_part_files(self, base_path: str) -> list:
        """Find any existing part files for a given base path"""
        import glob
        return glob.glob(f"{base_path}.part*")

    def status(self, update: Update, context: CallbackContext) -> None:
        """Check bot and data status"""
        try:
            status_msg = "✅ PKTickBot is online\n"

            if os.path.exists(self.ticks_file_path):
                file_size = os.path.getsize(self.ticks_file_path)
                status_msg += f"📁 ticks.json: {file_size:,} bytes\n"

                # Check zip size
                try:
                    zip_path, zip_size = self.create_zip_file(self.ticks_file_path)
                    status_msg += f"📦 Compressed: {zip_size:,} bytes\n"
                    os.unlink(zip_path)  # Clean up temp zip

                    if zip_size > self.MAX_FILE_SIZE:
                        parts_needed = (zip_size + self.MAX_FILE_SIZE - 1) // self.MAX_FILE_SIZE
                        status_msg += f"⚠️  Will be split into {parts_needed} parts\n"

                except Exception as e:
                    status_msg += f"📦 Compression: Error ({e})\n"

                if file_size > 0:
                    try:
                        with open(self.ticks_file_path, "r") as f:
                            data = json.load(f)
                        status_msg += f"📊 Instruments: {len(data):,}\n"
                    except BaseException:
                        status_msg += "📊 Instruments: File format error\n"
                else:
                    status_msg += "📊 Instruments: File empty\n"
            else:
                status_msg += "❌ ticks.json: Not found\n"

            update.message.reply_text(status_msg)

        except Exception as e:
            self.logger.error(f"Error in status command: {e}")
            update.message.reply_text("❌ Error checking status")

    def run_bot(self):
        """Run the telegram bot - synchronous version for v13.4"""
        try:
            self.updater = Updater(self.bot_token, use_context=True)
            dispatcher = self.updater.dispatcher

            # Add handlers
            dispatcher.add_handler(CommandHandler("start", self.start))
            dispatcher.add_handler(CommandHandler("ticks", self.send_zipped_ticks))
            dispatcher.add_handler(CommandHandler("status", self.status))
            dispatcher.add_handler(CommandHandler("help", self.help_command))

            self.logger.info("Starting PKTickBot...")

            if self.chat_id:
                # Send startup message to specific chat
                try:
                    self.updater.bot.send_message(
                        chat_id=self.chat_id, text="🚀 PKTickBot started successfully!"
                    )
                except Exception as e:
                    self.logger.warn(f"Could not send startup message: {e}")

            # Start polling
            self.updater.start_polling()
            
            # Run the bot until interrupted
            self.updater.idle()

        except Exception as e:
            self.logger.error(f"Bot error: {e}")
            raise
        finally:
            if self.updater:
                self.updater.stop()

    def run(self):
        """Run the bot - no asyncio needed for v13.4"""
        self.run_bot()

