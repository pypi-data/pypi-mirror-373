# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RiskLimitTypeItem(models.Model):
    _name = "risk_limit_type.item"
    _description = "Risk Limit Type - Item"

    type_id = fields.Many2one(
        string="Risk Limit Type",
        comodel_name="risk_limit_type",
        required=True,
        ondelete="cascade",
    )
    item_id = fields.Many2one(
        string="Risk Limit Item",
        comodel_name="risk_limit_item",
        required=True,
    )
    restrict_single = fields.Boolean(
        string="Restrict Single Risk",
        default=False,
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        required=True,
    )
    limit_min_amount = fields.Boolean(
        string="Limit Min. Amount",
    )
    min_amount = fields.Monetary(
        string="Min. Amount",
        required=True,
        currency_field="currency_id",
    )
    default_amount = fields.Monetary(
        string="Default Amount",
        required=True,
        currency_field="currency_id",
    )
    limit_max_amount = fields.Boolean(
        string="Limit Max. Amount",
    )
    max_amount = fields.Monetary(
        string="Max. Amount",
        required=True,
        currency_field="currency_id",
    )
