# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ENofa(models.Model):
    _name = "enofa_number"
    _description = "E-NOFA Number"

    enofa_id = fields.Many2one(
        string="# E-NOFA",
        comodel_name="enofa",
    )
    name = fields.Char(
        string="Number",
    )
    faktur_pajak_keluaran_ids = fields.One2many(
        string="Faktur Pajak Keluaran",
        comodel_name="faktur_pajak_keluaran",
        inverse_name="enofa_number_id",
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("unused", "Unused"),
            ("issued", "Issued"),
            ("cancelled", "Cancelled"),
            ("open", "On Process"),
        ],
        required=True,
        default="unused",
        compute="_compute_state",
        store=True,
    )

    @api.depends(
        "faktur_pajak_keluaran_ids",
        "faktur_pajak_keluaran_ids.state",
    )
    def _compute_state(self):
        for record in self:
            result = "unused"
            if record.faktur_pajak_keluaran_ids:
                fpk = record.faktur_pajak_keluaran_ids[-1]
                if fpk.state in ["draft", "confirm", "open"]:
                    result = "open"
                elif fpk.state == "done":
                    result = "issued"
                elif fpk.state == "terminate":
                    result = "cancelled"
            record.state = result
