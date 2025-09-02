# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCountry(models.Model):
    _inherit = "res.country"

    efaktur_code = fields.Char(
        string="E-Faktur Code",
    )
