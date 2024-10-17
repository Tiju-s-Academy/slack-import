
import re
import json
import requests

users = {}

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

def get_pipe_anchor_tag_from_match(match):
    url = match.group(1)
    description = match.group(2)
    return f"<a target='_blank' rel='noreferrer noopener' href='{url}'>{description}</a>"

#  url|description
def replace_pipe_link_with_anchor_tag(text):
    pattern = r'<(https?://[^\s|>]+)\|([^>]+)>'   
    text = re.sub(pattern, get_pipe_anchor_tag_from_match, text)
    return text

def get_url_anchor_tag_from_match(match):
    url = match.group(1)
    return f"<a target='_blank' rel='noreferrer noopener' href='{url}'>{url}</a>"
def replace_url_with_anchor_tag(text):
    pattern = r'(https?://[^\s]+)'
    text = re.sub(pattern, get_url_anchor_tag_from_match, text)
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

def replace_line_break_with_br(text):
    return text.replace('\n', '<br>')

# Function to replace matched emoji text with its Unicode character
def get_unicode_from_emoji(match):
    # Extract the matched emoji name (without the colons)
    emoji_name = match.group(1)
    # Return the corresponding Unicode character, or leave it as is if not found
    unicode = emoji_unicode_data.get(emoji_name)
    if unicode:
        unicode = f'&#{unicode};'
        return unicode
    return match.group(0)

def replace_emoji_with_unicode(text, emoji_data):
    global emoji_unicode_data
    emoji_unicode_data = emoji_data
    pattern = r':([a-zA-Z0-9_]+):'
    text = re.sub(pattern, get_unicode_from_emoji, text)
    return text

def get_all_channels(filename):
    channels = {}
    with open(filename) as file:
        channels_list = json.load(file)
        for channel in channels_list:
            channels[channel['name_normalized']] = channel
    return channels

def get_all_users(filename):
    users = {}
    with open(filename) as file:
        users_list = json.load(file)
        for user in users_list:
            users[user['id']] = user
    return users

def get_emoji_data():
    emoji_data_url = 'https://raw.githubusercontent.com/iamcal/emoji-data/master/emoji.json'
    res = requests.get(emoji_data_url)
    emoji_data = json.loads(res.content)
    emoji_unicode_data = {}
    for emoji in emoji_data:
        emoji_unicode_data[emoji['short_name']] = emoji['unified']
    return emoji_unicode_data
