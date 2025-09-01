# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class RiskLimitItem(models.Model):
    _name = "risk_limit_item"
    _description = "Risk Limit Item"
    _inherit = ["mixin.master_data"]

    model_id = fields.Many2one(
        string="Referenced Model",
        comodel_name="ir.model",
        index=True,
        copy=True,
    )
    model = fields.Char(
        related="model_id.model",
        store=False,
    )
    partner_field_id = fields.Many2one(
        string="Partner Field",
        comodel_name="ir.model.fields",
        index=True,
        copy=True,
    )
    amount_field_id = fields.Many2one(
        string="Amount Field",
        comodel_name="ir.model.fields",
        index=True,
        copy=True,
    )
    domain = fields.Char(
        string="Domain",
    )

    @api.onchange(
        "model_id",
    )
    def onchange_partner_field_id(self):
        self.partner_field_id = False

    @api.onchange(
        "model_id",
    )
    def onchange_amount_field_id(self):
        self.amount_field_id = False
