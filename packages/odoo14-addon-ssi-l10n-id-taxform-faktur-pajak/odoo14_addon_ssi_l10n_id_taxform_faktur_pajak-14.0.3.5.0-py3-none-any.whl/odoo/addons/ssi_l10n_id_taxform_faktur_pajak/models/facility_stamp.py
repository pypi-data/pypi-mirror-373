# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FacilityStamp(models.Model):
    _name = "facility_stamp"
    _inherit = ["mixin.master_data"]
    _description = "Facility Stamp"

    name = fields.Char(
        string="Facility Stamp",
    )
    code = fields.Char(
        default="/",
    )
    type_id = fields.Many2one(
        string="Transaction Type",
        comodel_name="faktur_pajak_transaction_type",
        required=True,
    )

    @api.constrains("code")
    def _check_duplicate_code(self):
        return True
