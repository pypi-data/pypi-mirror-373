# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AdditionalInfo(models.Model):
    _name = "additional_info"
    _inherit = ["mixin.master_data"]
    _description = "Additional Info"

    name = fields.Char(
        string="Additional Info",
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
