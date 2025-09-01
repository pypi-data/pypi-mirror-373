# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = [
        "res.partner",
    ]

    risk_limit_ids = fields.Many2many(
        string="Risk Limits",
        comodel_name="risk_limit_assignment.detail",
        compute="_compute_risk_limit_ids",
        store=False,
        compute_sudo=True,
    )
    risk_limit_assignment_ids = fields.One2many(
        string="Risk Limit Assignments",
        comodel_name="risk_limit_assignment",
        inverse_name="partner_id",
    )
    risk_limit_assignment_id = fields.Many2one(
        string="# Risk Limit Assignments",
        comodel_name="risk_limit_assignment",
        compute="_compute_risk_limit_assignment_id",
        store=True,
        compute_sudo=True,
    )

    @api.depends(
        "risk_limit_assignment_ids",
        "risk_limit_assignment_ids.partner_id",
        "risk_limit_assignment_ids.state",
    )
    def _compute_risk_limit_assignment_id(self):
        for record in self:
            result = False
            if record.risk_limit_assignment_ids:
                result = record.risk_limit_assignment_ids[-1]
            record.risk_limit_assignment_id = result

    @api.depends(
        "risk_limit_assignment_id",
    )
    def _compute_risk_limit_ids(self):
        for record in self:
            result = []
            if record.risk_limit_assignment_id:
                result = record.risk_limit_assignment_id.detail_ids.ids
            record.risk_limit_ids = result
