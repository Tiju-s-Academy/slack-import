from odoo import models,fields,api
import base64
import tempfile
import logging
from pathlib import Path
import shutil
import zipfile
import os
import json
from . import helpers
import traceback
from markupsafe import Markup

emoji_unicode_data = {}
_logger = logging.getLogger("Slack Import Debug")

class SlackChannelNames(models.Model):
    _name = 'slack.channel.name'
    name = fields.Char()

class SlackImportWizard(models.TransientModel):
    _name = "slack.import.wizard"

    slack_workspace_file = fields.Binary(string="Slack Workspace File (Zip)")
    slack_filename = fields.Char(string="Slack Filename")    

    channels_to_import = fields.Many2many('slack.channel.name')


    def action_import_data(self):
        """
        Writes the uploaded binary file to a temporary file.
        """
        if self.slack_workspace_file:

            zip_file_path =  '/tmp/odoo_slack_data_temp.zip'
            extract_path = '/tmp/odoo_slack_data_temp'
            if Path(extract_path).is_dir():
                shutil.rmtree(extract_path)
            # Decode the binary data
            file_data = base64.b64decode(self.slack_workspace_file)
            
            # Create a temporary file
            with open(zip_file_path, 'wb') as temp_file:
                temp_file.write(file_data)
                temp_file_path = temp_file.name

            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            # _logger.error(os.listdir('/tmp/odoo_slack_data_temp'))
            global emoji_unicode_data
            emoji_unicode_data = helpers.get_emoji_data()

            users_file_path = f'{extract_path}/users.json'
            users = {}
            if Path(users_file_path).exists():
                users = helpers.get_all_users(users_file_path)
                # Set value for users dict in helpers module too
                helpers.users = users

            channels_file_path = f'{extract_path}/channels.json'
            if Path(channels_file_path).exists():
                channels = helpers.get_all_channels(channels_file_path)
                messages_dict = {}
                for channel_name, channel_data in channels.items():
                    _logger.error(channel_name)
                    messages = []
                    # Store all messages in current channel
                    for filename in os.listdir(f'{extract_path}/{channel_name}'):
                        with open(f'{extract_path}/{channel_name}/{filename}', encoding="utf8") as file:
                            messages = messages + json.load(file)

                    # Store messages in a dictionary for getting reply messages later
                    for message in messages:
                        messages_dict[message['ts']] = message.copy()

                    # Remove all messages which are inside a thread, as those will be retrieved from the message dict later
                    for i in range(len(messages)-1, -1, -1):
                        thread_ts = messages[i].get('thread_ts', False)
                        if thread_ts:
                            if thread_ts != messages[i]['ts']:
                                messages.pop(i)

                    # Sort the messages dict by the timestamp it is send 
                    def msg_send_time(msg):
                        return msg['ts']
                    messages = sorted(messages, key=msg_send_time)

                    errored_messages = []
                    for message in messages:
                        try:
                            text = f"{users[message['user']]['name']}: "
                            if message.get('text'):
                                text += message['text']
                            if message.get('attachments'):
                                text += helpers.get_attachments(message)
                                # print(message,'\n')

                            if message.get('files'):
                                text += helpers.get_files(message)

                            # Process the text to include tags, convert to unicode etc.. 
                            text = self.process_text(text)

                            print(text)
                        except:
                            exc = traceback.format_exc()
                            errored_messages.append((message, exc))
                            
                        # Replies to message
                        if message.get('thread_ts'):
                            # print(message)
                            for reply in message['replies']:
                                reply_message = messages_dict[reply['ts']]
                                reply_text = f"\t {users[reply_message['user']]['name']}: "

                                if reply_message.get('text'):
                                    reply_text += f"\t {reply_message['text']}"
                                if reply_message.get('attachments'):
                                    reply_text += f"\t {helpers.get_attachments(reply_message)}"
                                if reply_message.get('files'):
                                    reply_text += f"\t {helpers.get_files(reply_message)}"

                                # Process the text to include tags, convert to unicode etc.. 
                                reply_text = self.process_text(reply_text)

                                try:
                                    print(reply_text)
                                    pass
                                    # print(f"\t {users[reply['user']]['name']}: {messages_dict[reply['ts']]['text']}")
                                except:
                                    exc = traceback.format_exc()
                                    errored_messages.append((messages_dict[reply['ts']], exc))
                        print('\n')
                    # from datetime import datetime
                    # timestamp = 1728899885.867629
                    # dt_object = datetime.fromtimestamp(timestamp)

                    print('errored_messages', len(errored_messages))
                    for message, exc in errored_messages:
                        print(message, exc)

            # You can print or log the path for debugging purposes
            _logger.info(f"Temporary file created at: {temp_file_path}")

            # Perform any additional logic here with the temp file

    def process_text(self, text):
        text = helpers.replace_user_mention_with_user_name(text)
        text = helpers.replace_pipe_link_with_anchor_tag(text)
        text = helpers.replace_url_with_anchor_tag(text)
        text = helpers.replace_tel_link_with_anchor_tag(text)
        text = helpers.replace_line_break_with_br(text)
        text = helpers.replace_emoji_with_unicode(text, emoji_unicode_data)

        text = f"<p>{text}</p>"
        return text