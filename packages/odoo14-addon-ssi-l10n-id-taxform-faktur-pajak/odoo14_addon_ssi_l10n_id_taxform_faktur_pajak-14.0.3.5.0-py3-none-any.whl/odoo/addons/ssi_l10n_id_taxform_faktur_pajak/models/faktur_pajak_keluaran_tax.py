# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FakturPajakKeluaranTax(models.Model):
    _name = "faktur_pajak_keluaran_tax"
    _description = "Detail Faktur Pajak Tax"
    _inherit = ["mixin.tax_line"]

    faktur_pajak_keluaran_id = fields.Many2one(
        comodel_name="faktur_pajak_keluaran",
        string="# Faktur Pajak Keluaran",
        required=True,
        ondelete="cascade",
    )
