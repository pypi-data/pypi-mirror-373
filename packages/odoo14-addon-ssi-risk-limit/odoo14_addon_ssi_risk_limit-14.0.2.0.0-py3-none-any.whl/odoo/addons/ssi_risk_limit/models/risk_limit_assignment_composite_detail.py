# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class RiskLimitAssignmentCompositeDetail(models.Model):
    _name = "risk_limit_assignment.composite_detail"
    _description = "Risk Limit Assignment - Composite Detail"

    assignment_id = fields.Many2one(
        string="# Assignment",
        comodel_name="risk_limit_assignment",
        required=True,
        ondelete="cascade",
    )
    detail_ids = fields.Many2many(
        string="Risk Limit Assignment - Detail",
        comodel_name="risk_limit_assignment.detail",
        relation="rel_risk_assignment_detail_composite_2_detail",
        column1="composite_detail_id",
        column2="detail_id",
        compute="_compute_detail_ids",
        store=True,
        compute_sudo=True,
    )
    item_ids = fields.Many2many(
        string="Risk Limit Items",
        comodel_name="risk_limit_item",
        relation="rel_risk_assignment_detail_composite_2_item",
        column1="detail_id",
        column2="item_id",
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

    @api.depends(
        "item_ids",
    )
    def _compute_detail_ids(self):
        Detail = self.env["risk_limit_assignment.detail"]
        for record in self:
            result = []
            if record.item_ids:
                criteria = [
                    ("assignment_id", "=", record.assignment_id.id),
                    ("item_id", "in", record.item_ids.ids),
                ]
                result = Detail.search(criteria).ids
            record.detail_ids = result

    @api.depends(
        "detail_ids",
        "detail_ids.amount_usage",
    )
    def _compute_amount(self):
        for record in self:
            amount_usage = amount_residual = 0.0

            for detail in record.detail_ids:
                amount_usage += detail.amount_usage

            amount_residual = record.amount - amount_usage

            record.amount_residual = amount_residual
            record.amount_usage = amount_usage

    @api.constrains(
        "amount_residual",
    )
    def constrains_residual(self):
        for record in self.sudo():
            if record.amount_residual < 0.0:
                error_message = """
                Document Type: %s
                Context: Risk limit composite usage
                Database ID: %s
                Problem: Compososite Risk limit reached
                Solution: Resolve limit usage or adjust risk limit
                """ % (
                    record.assignment_id._description,
                    record.assignment_id.id,
                )
                raise UserError(_(error_message))
