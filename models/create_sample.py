# Normal Message
[
    {'email_add_signature': True, 
     'record_name': 'general', 
     'author_id': 3, 'author_guest_id': False, 
     'email_from': '"Mitchell Admin" <admin@yourcompany.example.com>', 
     'model': 'discuss.channel', 
     'res_id': 1, 
     'body': Markup('hey'), 
     'message_type': 'comment', 
     'parent_id': False, 'subject': False, 
     'subtype_id': 1, 'partner_ids': [], 
     'record_alias_domain_id': False, 
     'record_company_id': 1, 
     'reply_to': '"Mitchell Admin" <admin@yourcompany.example.com>', 
     'attachment_ids': []}
]

# Hyperlink Message
[
    {
        'email_add_signature': True,
        'record_name': 'general',
        'author_id': 3,
        'author_guest_id': False,
        'email_from': '"Mitchell Admin" <admin@yourcompany.example.com>',
        'model': 'discuss.channel',
        'res_id': 1,
        'body': Markup(
            '<a target="_blank" rel="noreferrer noopener" '
            'href="https://www.w3schools.com/images/compatible_chrome.png">'
            'https://www.w3schools.com/images/compatible_chrome.png</a>'
        ),
        'message_type': 'comment',
        'parent_id': False,
        'subject': False,
        'subtype_id': 1,
        'partner_ids': [],
        'record_alias_domain_id': False,
        'record_company_id': 1,
        'reply_to': '"Mitchell Admin" <admin@yourcompany.example.com>',
        'attachment_ids': []
    }
]

# With Attachment
[{
    'email_add_signature': True,
    'record_name': 'general',
    'author_id': 3,
    'author_guest_id': False,
    'email_from': '"Mitchell Admin" <admin@yourcompany.example.com>',
    'model': 'discuss.channel',
    'res_id': 1,
    'body': Markup('Heres the file'),
    'message_type': 'comment',
    'parent_id': False,
    'subject': False,
    'subtype_id': 1,
    'partner_ids': [],
    'record_alias_domain_id': False,
    'record_company_id': 1,
    'reply_to': '"Mitchell Admin" <admin@yourcompany.example.com>',
    'attachment_ids': [('<Command.LINK: 4>', 815, 0)]
    }]

#Reply Message
[
    {
        'email_add_signature': True,
        'record_name': 'general',
        'author_id': 3,
        'author_guest_id': False,
        'email_from': '"Mitchell Admin" <admin@yourcompany.example.com>',
        'model': 'discuss.channel',
        'res_id': 1,
        'body': Markup('My reply'),
        'message_type': 'comment',
        'parent_id': 399,
        'subject': False,
        'subtype_id': 1,
        'partner_ids': [],
        'record_alias_domain_id': False,
        'record_company_id': 1,
        'reply_to': '"Mitchell Admin" <admin@yourcompany.example.com>',
        'attachment_ids': []
    }
]
import temp
