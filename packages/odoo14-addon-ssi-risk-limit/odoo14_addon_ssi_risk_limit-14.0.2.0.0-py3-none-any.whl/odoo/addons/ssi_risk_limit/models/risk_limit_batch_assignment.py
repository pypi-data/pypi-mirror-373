# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class RiskLimitBatchAssignment(models.Model):
    _name = "risk_limit_batch_assignment"
    _description = "Risk Limit Batch Assignment"
    _inherit = [
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_open",
        "mixin.transaction_confirm",
        "mixin.many2one_configurator",
    ]

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "open"
    _approval_state = "confirm"
    _after_approved_method = "action_open"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True
    _automatically_insert_open_policy_fields = False
    _automatically_insert_open_button = False

    _statusbar_visible_label = "draft,confirm,open"
    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "open_ok",
        "restart_approval_ok",
        "cancel_ok",
        "restart_ok",
        "done_ok",
        "manual_number_ok",
    ]

    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "action_done",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_open",
        "dom_reject",
        "dom_done",
        "dom_cancel",
    ]

    # Sequence attribute
    _create_sequence_state = "open"

    date = fields.Date(
        string="Date",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="risk_limit_type",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    allowed_partner_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Allowed Partners",
        compute="_compute_allowed_partner_ids",
        store=False,
        compute_sudo=True,
    )
    partner_ids = fields.Many2many(
        string="Partners",
        comodel_name="res.partner",
        relation="rel_risk_limit_batch_assignment_2_partner",
        column1="batch_assignment_id",
        columne2="partner_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    risk_limit_assignment_ids = fields.One2many(
        string="Risk Limit Assignments",
        comodel_name="risk_limit_assignment",
        inverse_name="batch_id",
        readonly=True,
    )

    @api.depends("type_id")
    def _compute_allowed_partner_ids(self):
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="res.partner",
                    method_selection=record.type_id.partner_selection_method,
                    manual_recordset=record.type_id.partner_ids,
                    domain=record.type_id.partner_domain,
                    python_code=record.type_id.partner_python_code,
                )
            record.allowed_partner_ids = result

    def action_load_partner(self):
        for record in self.sudo():
            record._load_partner()

    def _load_partner(self):
        self.ensure_one()
        self.write({"partner_ids": [(6, 0, self.allowed_partner_ids.ids)]})

    @api.model
    def _get_policy_field(self):
        res = super()._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "done_ok",
            "open_ok",
            "cancel_ok",
            "reject_ok",
            "restart_ok",
            "restart_approval_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    @ssi_decorator.post_approve_action()
    def _01_create_assignment(self):
        self.ensure_one()
        RiskLimit = self.env["risk_limit_assignment"]
        for partner in self.partner_ids:
            RiskLimit.create(
                {
                    "type_id": self.type_id.id,
                    "date": self.date,
                    "partner_id": partner.id,
                    "batch_id": self.id,
                }
            )

    @ssi_decorator.post_done_action()
    def _01_process_assignment(self):
        self.ensure_one()
        for assignment in self.risk_limit_assignment_ids:
            assignment.action_compute_item()
            assignment.with_context(bypass_policy_check=True).action_confirm()
            assignment.with_context(bypass_policy_check=True).action_open()

    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch
