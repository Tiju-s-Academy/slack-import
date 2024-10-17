from odoo import models,fields,api

class MailMessage(models.Model):
    _inherit = "mail.message"

    is_slack_message = fields.Boolean()

    def create(self, vals):
        print('Create vals: ', vals)
        return super().create(vals)
    
class DiscussChannel(models.Model):
    _inherit = "discuss.channel"

    is_slack_channel = fields.Boolean()

class ResUser(models.Model):
    _inherit = "res.users"

    is_slack_user = fields.Boolean()
    slack_user_id = fields.Char(string="Slack User ID")
    slack_username = fields.Char(string="Slack Username")

class ResCompany(models.Model):
    _inherit = "res.company"

    def action_slack_import(self):
        return {
            'name': ('Slack Data Import'),
            'res_model': 'slack.import.wizard',
            'view_mode': 'form',
            'context': {
                # 'active_model': 'sale.order',
                # 'active_ids': self.sale_order_ids.ids,
                # 'default_rental_id': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }