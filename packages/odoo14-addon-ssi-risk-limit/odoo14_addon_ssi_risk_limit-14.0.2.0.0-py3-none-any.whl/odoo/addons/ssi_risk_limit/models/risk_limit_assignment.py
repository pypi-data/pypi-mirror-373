# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.ssi_decorator import ssi_decorator


class RiskLimitAssignment(models.Model):
    _name = "risk_limit_assignment"
    _description = "Risk Limit Assignment"
    _inherit = [
        "mixin.transaction_terminate",
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_open",
        "mixin.transaction_confirm",
        "mixin.transaction_partner",
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
        "terminate_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "%(ssi_transaction_terminate_mixin.base_select_terminate_reason_action)d",
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
        "dom_terminate",
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
    batch_id = fields.Many2one(
        string="# Batch Assignment",
        comodel_name="risk_limit_batch_assignment",
        readonly=True,
    )
    allowed_partner_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Allowed Partners",
        compute="_compute_allowed_partner_ids",
        store=False,
        compute_sudo=True,
    )
    detail_ids = fields.One2many(
        string="Details",
        comodel_name="risk_limit_assignment.detail",
        inverse_name="assignment_id",
        readonly=True,
    )
    composite_detail_ids = fields.One2many(
        string="Composite Details",
        comodel_name="risk_limit_assignment.composite_detail",
        inverse_name="assignment_id",
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

    @api.onchange(
        "type_id",
    )
    def onchange_partner_id(self):
        self.partner_id = False

    @api.constrains(
        "state",
    )
    def constrain_only_one(self):
        RiskLimit = self.env["risk_limit_assignment"]
        for record in self.sudo():
            criteria = [
                ("partner_id", "=", record.partner_id.id),
                ("state", "=", "open"),
                ("id", "!=", record.id),
            ]
            result_count = RiskLimit.search_count(criteria)
            if result_count > 0 and record.state == "open":
                error_message = """
                Document Type: %s
                Context: Risk limit assignment activation
                Database ID: %s
                Problem: Multiple assignment detected
                Solution: Finish other assignment
                """ % (
                    record._description,
                    record.id,
                )
                raise UserError(_(error_message))

    def action_compute_item(self):
        for record in self.sudo():
            record._compute_item()

    def action_compute_amount(self):
        for record in self.sudo():
            record._compute_amount()

    def _compute_item(self):
        self.ensure_one()
        self.detail_ids.unlink()
        Detail = self.env["risk_limit_assignment.detail"]
        CompositeDetail = self.env["risk_limit_assignment.composite_detail"]
        for item in self.type_id.item_ids:
            Detail.create(
                {
                    "assignment_id": self.id,
                    "item_id": item.item_id.id,
                    "currency_id": item.currency_id.id,
                    "amount": item.default_amount,
                    "restrict_single": item.restrict_single,
                }
            )

        self.composite_detail_ids.unlink()
        for item in self.type_id.composite_item_ids:
            CompositeDetail.create(
                {
                    "assignment_id": self.id,
                    "item_ids": [(6, 0, item.item_ids.ids)],
                    "currency_id": item.currency_id.id,
                    "amount": item.default_amount,
                }
            )

    def _compute_amount(self):
        self.ensure_one()
        for detail in self.detail_ids:
            detail._compute_amount()

    @api.model
    def _get_policy_field(self):
        res = super()._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "done_ok",
            "open_ok",
            "cancel_ok",
            "terminate_ok",
            "reject_ok",
            "restart_ok",
            "restart_approval_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    @ssi_decorator.post_confirm_action()
    @ssi_decorator.post_approve_action()
    def _01_compute_amount(self):
        self.ensure_one()
        self._compute_amount()

    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch
