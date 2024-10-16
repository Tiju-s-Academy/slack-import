import json
import os
import traceback
import re

users = {}
with open('users.json') as file:
    users_list = json.load(file)
    for user in users_list:
        users[user['id']] = user
channels = {}
with open('channels.json') as file:
    channels_list = json.load(file)
    for channel in channels_list:
        channels[channel['name_normalized']] = channel

messages_dict = {} #To Store copies of all Messages
messages = []


channel_name = 'teamachievers'
# Store messages from all messages in current channel
for filename in os.listdir(channel_name):
    # filename = os.fsdecode(file)
    with open(f'{channel_name}/{filename}', encoding="utf8") as file:
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

def get_attachments(message):
    return '\n'.join( attachment.get('text') or attachment.get('from_url') for attachment in message['attachments'] )

def get_files(message):
    return '\n'.join( file['url_private_download'] for file in message['files'] )

# Get user name from @ mentions
def get_user_name_from_match(match):
    user_id = match.group(0)
    user_id = user_id[2:len(user_id)-1]
    return '@'+users[user_id]['name']
def replace_user_mention_with_user_name(text):
    pattern = r'<@U[^>]+>'
    text = re.sub(pattern, get_user_name_from_match, text)
    return text

def get_anchor_tag_from_match(match):
    url = match.group(1)
    description = match.group(2)
    return f"<a href='{url}'>{description}</a>"
def replace_link_with_anchor_tag(text):
    pattern = r'<(https?://[^\|>]+)\|([^>]+)>'
    text = re.sub(pattern, get_anchor_tag_from_match, text)
    return text

def get_tel_anchor_tag_from_match(match):
    url = match.group(1)         # Extract the URL part
    description = match.group(2) # Extract the description part
    return f"<a href='{url}'>{description}</a>"

# Function to replace matched links with anchor tags
def replace_tel_link_with_anchor_tag(text):
    pattern = r'<(tel:[^\|>]+)\|([^>]+)>'
    text = re.sub(pattern, get_tel_anchor_tag_from_match, text)
    return text

errored_messages = []
for message in messages:
    try:
        text = f"{users[message['user']]['name']}: "
        if message.get('text'):
            text += message['text']
        if message.get('attachments'):
            text += get_attachments(message)
            # print(message,'\n')

        if message.get('files'):
            text += get_files(message)
        text = replace_user_mention_with_user_name(text)
        text = replace_link_with_anchor_tag(text)
        text = replace_tel_link_with_anchor_tag(text)

        print(text)
        # print(f"{users[message['user']]['name']}: {message['text']}")
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
                reply_text += f"\t {get_attachments(reply_message)}"
            if reply_message.get('files'):
                reply_text += f"\t {get_files(reply_message)}"
            reply_text = replace_user_mention_with_user_name(reply_text)
            reply_text = replace_link_with_anchor_tag(reply_text)
            reply_text = replace_tel_link_with_anchor_tag(reply_text)
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
    # if message.get('attachments'):
    #     print(f"\nAttachments\n{message['attachments'][0].keys()}")
    #     print(f"\nAttachments\n{message['attachments'][0]['text']}")

    # if message.get('files'):
    #     print(f"\nFiles\n{message['files'][0].keys()}")
    # print(f'{message.keys()}\n\n')