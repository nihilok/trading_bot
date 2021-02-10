import re

import pytz
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Defaults
from telegram.bot import Bot
import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


class BaseBot:

    def __init__(self, token="1692177307:AAFljJEI2CZ06qLzyw4TS4Ty18A7R5N1btg", message_handler=None, channel=None):
        # Instantiate the bot with defaults
        defaults = Defaults(parse_mode=ParseMode.HTML, allow_sending_without_reply=True,
                            tzinfo=pytz.timezone('UTC'))
        self.bot = Bot(token)
        self.updater = Updater(token, use_context=True, defaults=defaults)

        # Get the dispatcher to register handlers
        self.dp = self.updater.dispatcher

        # on non command text message - echo the message on Telegram
        if message_handler:
            self.dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
        else:
            self.dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.echo))
        self.dp.add_handler(CommandHandler('start', self.start))
        self.channel_id = channel

    @staticmethod
    def start(update, context):
        print(update.effective_chat.id)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Bot started!")

    @staticmethod
    def echo(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=update.effective_chat.id)

    def add_command(self, command, func):
        self.dp.add_handler(CommandHandler(command, func))

    def run(self):
        self.updater.start_polling()
        self.updater.idle()

    def broadcast(self, message):
        self.bot.send_message(chat_id=self.channel_id, text=message)

    @staticmethod
    def send_message(update, context, text):
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)


if __name__ == '__main__':
    BaseBot().run()

context_dir = ['__annotations__', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_commands', '_id_attrs', '_message', '_post', '_request', '_validate_token', 'addStickerToSet', 'add_sticker_to_set', 'answerCallbackQuery', 'answerInlineQuery', 'answerPreCheckoutQuery', 'answerShippingQuery', 'answer_callback_query', 'answer_inline_query', 'answer_pre_checkout_query', 'answer_shipping_query', 'base_file_url', 'base_url', 'bot', 'can_join_groups', 'can_read_all_group_messages', 'close', 'commands', 'copyMessage', 'copy_message', 'createNewStickerSet', 'create_new_sticker_set', 'de_json', 'de_list', 'defaults', 'deleteChatPhoto', 'deleteChatStickerSet', 'deleteMessage', 'deleteStickerFromSet', 'deleteWebhook', 'delete_chat_photo', 'delete_chat_sticker_set', 'delete_message', 'delete_sticker_from_set', 'delete_webhook', 'editMessageCaption', 'editMessageLiveLocation', 'editMessageMedia', 'editMessageReplyMarkup', 'editMessageText', 'edit_message_caption', 'edit_message_live_location', 'edit_message_media', 'edit_message_reply_markup', 'edit_message_text', 'exportChatInviteLink', 'export_chat_invite_link', 'first_name', 'forwardMessage', 'forward_message', 'getChat', 'getChatAdministrators', 'getChatMember', 'getChatMembersCount', 'getFile', 'getGameHighScores', 'getMe', 'getMyCommands', 'getStickerSet', 'getUpdates', 'getUserProfilePhotos', 'getWebhookInfo', 'get_chat', 'get_chat_administrators', 'get_chat_member', 'get_chat_members_count', 'get_file', 'get_game_high_scores', 'get_me', 'get_my_commands', 'get_sticker_set', 'get_updates', 'get_user_profile_photos', 'get_webhook_info', 'id', 'kickChatMember', 'kick_chat_member', 'last_name', 'leaveChat', 'leave_chat', 'link', 'logOut', 'log_out', 'logger', 'name', 'parse_data', 'pinChatMessage', 'pin_chat_message', 'promoteChatMember', 'promote_chat_member', 'request', 'restrictChatMember', 'restrict_chat_member', 'sendAnimation', 'sendAudio', 'sendChatAction', 'sendContact', 'sendDice', 'sendDocument', 'sendGame', 'sendInvoice', 'sendLocation', 'sendMediaGroup', 'sendMessage', 'sendPhoto', 'sendPoll', 'sendSticker', 'sendVenue', 'sendVideo', 'sendVideoNote', 'sendVoice', 'send_animation', 'send_audio', 'send_chat_action', 'send_contact', 'send_dice', 'send_document', 'send_game', 'send_invoice', 'send_location', 'send_media_group', 'send_message', 'send_photo', 'send_poll', 'send_sticker', 'send_venue', 'send_video', 'send_video_note', 'send_voice', 'setChatAdministratorCustomTitle', 'setChatDescription', 'setChatPermissions', 'setChatPhoto', 'setChatStickerSet', 'setChatTitle', 'setGameScore', 'setMyCommands', 'setPassportDataErrors', 'setStickerPositionInSet', 'setStickerSetThumb', 'setWebhook', 'set_chat_administrator_custom_title', 'set_chat_description', 'set_chat_permissions', 'set_chat_photo', 'set_chat_sticker_set', 'set_chat_title', 'set_game_score', 'set_my_commands', 'set_passport_data_errors', 'set_sticker_position_in_set', 'set_sticker_set_thumb', 'set_webhook', 'stopMessageLiveLocation', 'stopPoll', 'stop_message_live_location', 'stop_poll', 'supports_inline_queries', 'to_dict', 'to_json', 'token', 'unbanChatMember', 'unban_chat_member', 'unpinAllChatMessages', 'unpinChatMessage', 'unpin_all_chat_messages', 'unpin_chat_message', 'uploadStickerFile', 'upload_sticker_file', 'username']
