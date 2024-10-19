
import re
import json
import requests
import emoji

users = {}

def get_attachments(message):
    return '\n'.join( attachment.get('text') or attachment.get('from_url') for attachment in message['attachments'] )

def get_files(message):
    return '\n'.join( file['url_private_download'] for file in message['files'] )

# Get user name from @ mentions
def get_user_name_from_match(match):
    user_id = match.group(0)
    user_id = user_id[2:len(user_id)-1]
    user = users.get(user_id) or users['FALLBACK_USER']
    return '@'+user['name']
def replace_user_mention_with_user_name(text):
    pattern = r'<@U[^>]+>'
    text = re.sub(pattern, get_user_name_from_match, text)
    return text


def get_pipe_anchor_tag_from_match(match):
    """Generates an anchor tag from a Slack-style URL with a description (e.g., <url|description>)."""
    url = match.group(1)
    description = match.group(2)
    return f"<a target='_blank' rel='noreferrer noopener' href='{url}'>{description}</a>"

def replace_pipe_link_with_anchor_tag(text):
    """
    Replaces Slack-style links with pipe notation (e.g., <https://example.com|Example>)
    with proper HTML anchor tags.
    """
    pattern = r'<(https?://[^\s|>]+)\|([^>]+)>'
    text = re.sub(pattern, get_pipe_anchor_tag_from_match, text)
    return text

def get_url_anchor_tag_from_match(match):
    """Generates an anchor tag from a plain URL enclosed in angle brackets."""
    url = match.group(1).strip('<>')
    return f"<a target='_blank' rel='noreferrer noopener' href='{url}'>{url}</a>"

def replace_url_with_anchor_tag(text):
    """
    Replaces URLs enclosed in angle brackets (e.g., <https://example.com>)
    with proper HTML anchor tags, avoiding double-wrapping.
    """
    # Match URLs enclosed in angle brackets without a description, avoiding already-wrapped links.
    pattern = r'<(https?://[^\s|>]+)>'
    
    # Function to avoid processing URLs already wrapped in <a> tags
    def avoid_double_wrapping(match):
        url = match.group(1)
        # Check if this URL is already wrapped in an anchor tag.
        if re.search(r'<a [^>]*href=[\'"]' + re.escape(url) + r'[\'"]', text):
            return match.group(0)  # Keep the original if it's already wrapped.
        return get_url_anchor_tag_from_match(match)
    
    text = re.sub(pattern, avoid_double_wrapping, text)
    return text

def get_tel_anchor_tag_from_match(match):
    """Generates an anchor tag for 'tel' links (e.g., <tel:+123456789|Call Us>)."""
    url = match.group(1)
    description = match.group(2)
    return f"<a href='{url}'>{description}</a>"

def replace_tel_link_with_anchor_tag(text):
    """
    Replaces Slack-style telephone links (e.g., <tel:+123456789|Call Us>)
    with proper HTML anchor tags.
    """
    pattern = r'<(tel:[^\|>]+)\|([^>]+)>'
    text = re.sub(pattern, get_tel_anchor_tag_from_match, text)
    return text

def replace_line_break_with_br(text):
    return text.replace('\n', '<br>')


def get_emoji_from_short_code(match):
    emoji_name = match.group(0)
    return emoji.emojize(emoji_name)

def replace_short_name_with_emoji(text):
    pattern = r':([a-zA-Z0-9_]+):'
    text = re.sub(pattern, get_emoji_from_short_code, text)
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
