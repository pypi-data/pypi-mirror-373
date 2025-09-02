# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = [
        "account.move",
    ]

    faktur_pajak_keluaran_id = fields.Many2one(
        string="# Faktur Pajak keluaran",
        comodel_name="faktur_pajak_keluaran",
        compute="_compute_faktur_pajak_keluaran_id",
        store=True,
    )
    fp_keluaran_state = fields.Selection(
        related="faktur_pajak_keluaran_id.state",
        store=True,
    )
    faktur_pajak_keluaran_ids = fields.Many2many(
        string="Faktur Pajak Keluaran",
        comodel_name="faktur_pajak_keluaran",
        relation="el_faktur_pajak_keluaran_2_journal_entry",
        column1="move_id",
        column2="faktur_pajak_keluaran_id",
        copy=False,
        readonly=True,
    )

    @api.depends(
        "faktur_pajak_keluaran_ids",
        "faktur_pajak_keluaran_ids.state",
    )
    def _compute_faktur_pajak_keluaran_id(self):
        for record in self:
            result = False

            if record.faktur_pajak_keluaran_ids:
                result = record.faktur_pajak_keluaran_ids[-1]
            record.faktur_pajak_keluaran_id = result
