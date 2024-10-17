
import re

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

def replace_line_break_with_br(text):
    return text.replace('\n', '<br>')