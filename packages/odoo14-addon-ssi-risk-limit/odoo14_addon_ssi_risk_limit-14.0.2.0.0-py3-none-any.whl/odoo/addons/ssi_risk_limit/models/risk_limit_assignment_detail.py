# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class RiskLimitAssignment(models.Model):
    _name = "risk_limit_assignment.detail"
    _description = "Risk Limit Assignment"

    assignment_id = fields.Many2one(
        string="# Assignment",
        comodel_name="risk_limit_assignment",
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

            if record.item_id:
                model_name = record.item_id.model
                domain = safe_eval(record.item_id.domain, {})
                domain_result = self.env[model_name].search(domain)
                partner_result = self.env[model_name].search(
                    [
                        (
                            record.item_id.partner_field_id.name,
                            "=",
                            self.assignment_id.partner_id.id,
                        ),
                    ]
                )
                final_result = domain_result & partner_result

                result = self.env[model_name].read_group(
                    domain=[("id", "in", final_result.ids)],
                    fields=[record.item_id.amount_field_id.name],
                    groupby=[],
                )

                if result[0]["__count"] > 0:
                    amount_usage = result[0][record.item_id.amount_field_id.name]

            amount_residual = record.amount - amount_usage
            record.amount_usage = amount_usage
            record.amount_residual = amount_residual

    @api.constrains(
        "amount_residual",
    )
    def constrains_residual(self):
        for record in self.sudo():
            if record.amount_residual < 0.0 and record.restrict_single:
                error_message = """
                Document Type: %s
                Context: Risk limit usage
                Database ID: %s
                Problem: Risk limit %s reached
                Solution: Resolve limit usage or adjust risk limit
                """ % (
                    record.assignment_id._description,
                    record.assignment_id.id,
                    record.item_id.name,
                )
                raise UserError(_(error_message))
