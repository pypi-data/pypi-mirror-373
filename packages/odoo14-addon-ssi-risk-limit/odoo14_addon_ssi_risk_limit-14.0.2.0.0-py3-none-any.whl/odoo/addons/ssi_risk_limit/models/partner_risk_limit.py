# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PartnerRiskLimit(models.Model):
    _name = "partner.risk_limit"
    _description = "Partner - Risk Limit"

    partner_id = fields.Many2one(
        string="# Assignment",
        comodel_name="res.partner",
        required=True,
        ondelete="cascade",
    )
    item_id = fields.Many2one(
        string="Risk Limit Item",
        comodel_name="risk_limit_item",
        required=True,
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        required=True,
    )
    amount = fields.Monetary(
        string="Limit Amount",
        required=True,
        currency_field="currency_id",
    )
    amount_usage = fields.Monetary(
        string="Usage Amount",
        currency_field="currency_id",
        compute="_compute_amount",
        compute_sudo=True,
        store=True,
    )
    amount_residual = fields.Monetary(
        string="Residual Amount",
        currency_field="currency_id",
        compute="_compute_amount",
        compute_sudo=True,
        store=True,
    )

    @api.depends()
    def _compute_amount(self):
        for record in self:
            amount_usage = amount_residual = 0.0
            record.amount_usage = amount_usage
            record.amount_residual = amount_residual
