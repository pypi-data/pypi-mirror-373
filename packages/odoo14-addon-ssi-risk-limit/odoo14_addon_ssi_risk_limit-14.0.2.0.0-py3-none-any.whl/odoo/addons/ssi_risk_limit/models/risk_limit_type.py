# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RiskLimitType(models.Model):
    _name = "risk_limit_type"
    _description = "Risk Limit Type"
    _inherit = [
        "mixin.master_data",
        "mixin.res_partner_m2o_configurator",
    ]

    _res_partner_m2o_configurator_insert_form_element_ok = True
    _res_partner_m2o_configurator_form_xpath = "//page[@name='partner']"

    item_ids = fields.One2many(
        string="Items",
        comodel_name="risk_limit_type.item",
        inverse_name="type_id",
    )
    composite_item_ids = fields.One2many(
        string="Composite Items",
        comodel_name="risk_limit_type.composite_item",
        inverse_name="type_id",
    )
