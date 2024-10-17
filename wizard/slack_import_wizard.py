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

            self.clear_all_slack_data_from_db() #For debug and test only

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

            users_file_path = f'{extract_path}/users.json'
            users = {}
            if Path(users_file_path).exists():
                users = helpers.get_all_users(users_file_path)
                # Set value for users dict in helpers module too
                helpers.users = users
                # Create users
                for user_slack_id, user_data in users.items():
                    user_data['odoo_user'] = self.env['res.users'].create({
                        'name': user_data['name'],
                        'login': user_data['profile'].get('email') or user_data['name'],
                        'slack_user_id': user_slack_id,
                        'is_slack_user': True,
                    })

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
                            text = f"<p>"
                            if message.get('text'):
                                text += self.process_text(message['text'])

                            if message.get('attachments') and not message.get('text'):
                                text += self.process_text(helpers.get_attachments(message))
                                # print(message,'\n')

                            if message.get('files'):
                                text += self.process_text(helpers.get_files(message))

                            # Process the text to include tags, convert to unicode etc.. 
                            # text = self.process_text(text)
                            text = text+ '</p>'
                            create_vals = self.get_values_for_record_creation(message_data=text, channel_name=channel_name, send_user=users[message['user']]['odoo_user'], )
                            self.env['mail.message'].create(create_vals)
                            print(text)
                        except:
                            exc = traceback.format_exc()
                            errored_messages.append((message, exc))
                            
                        # Replies to message
                        if message.get('thread_ts'):
                            # print(message)
                            for reply in message['replies']:
                                reply_message = messages_dict[reply['ts']]
                                reply_text = f"<p>"

                                if reply_message.get('text'):
                                    reply_text += self.process_text(reply_message['text'])
                                if reply_message.get('attachments') and not reply_message.get('text'):
                                    reply_text += self.process_text(helpers.get_attachments(reply_message))
                                if reply_message.get('files'):
                                    reply_text += self.process_text(helpers.get_files(reply_message))

                                # Process the text to include tags, convert to unicode etc.. 
                                reply_text = reply_text+'</p>'
                                create_vals = self.get_values_for_record_creation(message_data=reply_text, channel_name=channel_name, send_user= users[reply_message['user']]['odoo_user'], )
                                self.env['mail.message'].create(create_vals)
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

                    # break

            # You can print or log the path for debugging purposes
            _logger.info(f"Temporary file created at: {temp_file_path}")

            # Perform any additional logic here with the temp file

    def process_text(self, text):
        print("TEXTBEFORE: ", text)
        text = helpers.replace_user_mention_with_user_name(text)
        text = helpers.replace_pipe_link_with_anchor_tag(text)
        text = helpers.replace_url_with_anchor_tag(text)  # Then handle plain URLs
        text = helpers.replace_tel_link_with_anchor_tag(text)
        text = helpers.replace_line_break_with_br(text)
        text = helpers.replace_short_name_with_emoji(text)

        # text = f"<p>{text}</p>"
        return text
    
    # For debug purpose only
    def clear_all_slack_data_from_db(self):
        self.env['res.users'].sudo().search([('is_slack_user','=',True)]).unlink()
        self.env['mail.message'].sudo().search([('is_slack_message','=',True)]).unlink()
        self.env['discuss.channel'].sudo().search([('is_slack_channel','=',True)]).unlink()



    def get_values_for_record_creation(self, message_data: str, channel_name, send_user, parent_msg_id=False, all_users_data = {} ):
        channel = self.env['discuss.channel'].sudo().search([('name','=',channel_name)])
        if channel:
            channel = channel[0]
        else:
            channel = self.env['discuss.channel'].sudo().create({'name': channel_name, 'channel_type': 'channel', 'is_slack_channel': True})
        values = {
            'email_add_signature': True, 
            'record_name': channel.name, 
            'author_id': send_user.partner_id.id,
            'model': 'discuss.channel',
            'res_id': channel.id,
            'body': Markup(message_data),
            # 'body': message_data,
            'message_type': 'comment',
            'parent_id': parent_msg_id,
            'subtype_id': 1,
            'record_company_id': 1, 
            'is_slack_message': True,
            'create_uid': send_user.id
        }
        return values