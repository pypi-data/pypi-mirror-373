# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BuyerDocument(models.Model):
    _name = "buyer_document"
    _inherit = ["mixin.master_data"]
    _description = "Buyer Document"

    name = fields.Char(
        string="Buyer Document",
    )
    code = fields.Char(
        default="/",
    )
