# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FakturPajakKeluaranDetail(models.Model):
    _name = "faktur_pajak_keluaran_detail"
    _description = "Detail Faktur Pajak Keluaran"
    _inherit = ["mixin.product_line_account"]

    faktur_pajak_keluaran_id = fields.Many2one(
        comodel_name="faktur_pajak_keluaran",
        string="# Faktur Pajak Keluaran",
        required=True,
        ondelete="cascade",
    )

    @api.depends(
        "name",
    )
    def _compute_efaktur_of_name(self):
        for record in self:
            result = "-"
            if record.name:
                result = record.name
            record.efaktur_of_name = result

    efaktur_of_name = fields.Char(
        string="OF_NAMA",
        compute="_compute_efaktur_of_name",
        store=True,
        compute_sudo=True,
    )

    @api.depends(
        "product_id",
        "product_id.code",
    )
    def _compute_efaktur_of_code(self):
        for record in self:
            result = "-"
            if record.product_id and record.product_id.code:
                result = record.product_id.code
            record.efaktur_of_code = result

    efaktur_of_code = fields.Char(
        string="OF_KODE",
        compute="_compute_efaktur_of_code",
        store=True,
        compute_sudo=True,
    )

    @api.depends("price_unit")
    def _compute_efaktur_of_harga_satuan(self):
        for record in self:
            record.efaktur_of_harga_satuan = str(record.price_unit)

    efaktur_of_harga_satuan = fields.Char(
        string="OF_HARGA_SATUAN",
        compute="_compute_efaktur_of_harga_satuan",
        store=True,
        compute_sudo=True,
    )

    @api.depends("uom_quantity")
    def _compute_efaktur_of_jumlah_barang(self):
        for record in self:
            record.efaktur_of_jumlah_barang = str(record.uom_quantity)

    efaktur_of_jumlah_barang = fields.Char(
        string="OF_JUMLAH_BARANG",
        compute="_compute_efaktur_of_jumlah_barang",
        store=True,
        compute_sudo=True,
    )

    @api.depends("price_subtotal")
    def _compute_efaktur_of_harga_total(self):
        for record in self:
            record.efaktur_of_harga_total = str(record.price_subtotal)

    efaktur_of_harga_total = fields.Char(
        string="OF_HARGA_TOTAL",
        compute="_compute_efaktur_of_harga_total",
        store=True,
        compute_sudo=True,
    )

    @api.depends("price_subtotal")
    def _compute_efaktur_of_diskon(self):
        for record in self:
            record.efaktur_of_diskon = 0

    efaktur_of_diskon = fields.Char(
        string="OF_DISKON",
        compute="_compute_efaktur_of_diskon",
        store=True,
        compute_sudo=True,
    )

    @api.depends("price_subtotal")
    def _compute_efaktur_of_dpp(self):
        for record in self:
            record.efaktur_of_dpp = str(record.price_subtotal)

    efaktur_of_dpp = fields.Char(
        string="OF_DPP",
        compute="_compute_efaktur_of_dpp",
        store=True,
        compute_sudo=True,
    )

    @api.depends("price_tax")
    def _compute_efaktur_of_ppn(self):
        for record in self:
            record.efaktur_of_ppn = str(int(record.price_tax))

    efaktur_of_ppn = fields.Char(
        string="OF_PPN",
        compute="_compute_efaktur_of_ppn",
        store=True,
        compute_sudo=True,
    )

    @api.depends(
        "product_id",
        "product_id.type",
    )
    def _compute_efaktur_of_opt(self):
        for record in self:
            result = "-"
            if record.product_id:
                if record.product_id.type == "service":
                    result = "B"
                else:
                    result = "A"
            record.efaktur_of_opt = result

    efaktur_of_opt = fields.Char(
        string="OF_OPT",
        compute="_compute_efaktur_of_opt",
        store=True,
        compute_sudo=True,
    )

    @api.depends(
        "uom_id",
    )
    def _compute_efaktur_of_unit(self):
        for record in self:
            result = "-"
            if record.uom_id:
                result = record.uom_id.efaktur_code
            record.efaktur_of_unit = result

    efaktur_of_unit = fields.Char(
        string="OF_OPT",
        compute="_compute_efaktur_of_unit",
        store=True,
        compute_sudo=True,
    )
