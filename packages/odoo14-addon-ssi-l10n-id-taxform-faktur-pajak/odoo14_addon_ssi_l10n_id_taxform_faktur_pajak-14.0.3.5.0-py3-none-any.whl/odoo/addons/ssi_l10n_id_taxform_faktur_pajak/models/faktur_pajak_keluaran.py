# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.ssi_decorator import ssi_decorator


class FakturPajakKeluaran(models.Model):
    _name = "faktur_pajak_keluaran"
    _inherit = [
        "mixin.transaction_terminate",
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_open",
        "mixin.transaction_confirm",
        "mixin.transaction_partner",
        "mixin.transaction_tax_address",
        "mixin.transaction_untaxed_with_field",
        "mixin.transaction_total_with_field",
        "mixin.transaction_tax_with_field",
        "mixin.company_currency",
        "mixin.account_move",
        "mixin.many2one_configurator",
    ]
    _description = "Faktur Pajak Keluaran"

    # mixin.multiple_approval attributes
    _approval_from_state = "draft"
    _approval_to_state = "open"
    _approval_state = "confirm"
    _after_approved_method = "action_open"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True
    _automatically_insert_open_button = False
    _automatically_insert_open_policy_fields = False

    # Attributes related to add element on form view automatically
    _statusbar_visible_label = "draft,confirm,open,done"
    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "done_ok",
        "cancel_ok",
        "terminate_ok",
        "restart_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_confirm",
        "action_approve",
        "action_reject",
        "action_done",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "%(ssi_transaction_cancel_mixin.base_select_terminate_reason_action)d",
        "action_restart",
        "action_recompute_all_fields",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_open",
        "dom_done",
        "dom_cancel",
        "dom_terminate",
        "dom_reject",
    ]

    # Sequence attribute
    # do not create document number since e-faktur number will be given by coretax
    # _create_sequence_state = "open"

    # mixin.transaction_untaxed attributes
    _detail_object_name = "detail_ids"
    _detail_amount_field_name = "price_subtotal"
    _amount_untaxed_field_name = "amount_untaxed"

    # mixin.transaction_tax attributes
    _tax_detail_object_name = "tax_ids"
    _tax_detail_amount_field_name = "tax_amount"
    _amount_tax_field_name = "amount_tax"

    # mixin.transaction_total attributes
    _amount_untaxed_field_name = "amount_untaxed"
    _amount_tax_field_name = "amount_tax"
    _amount_total_field_name = "amount_total"

    # mixin.transaction_tax attributes
    _tax_lines_field_name = "tax_ids"
    _tax_on_self = False
    _tax_source_recordset_field_name = "detail_ids"
    _price_unit_field_name = "price_unit"
    _quantity_field_name = "uom_quantity"

    name = fields.Char(
        required=True,
        readonly=True,
        states={
            "open": [
                ("readonly", False),
            ],
        },
    )
    date = fields.Date(
        string="Date",
        copy=False,
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    currency_id = fields.Many2one(
        related="company_currency_id",
    )
    taxform_period_id = fields.Many2one(
        string="Masa Pajak",
        comodel_name="l10n_id.tax_period",
        compute="_compute_taxform_period",
        store=True,
        copy=False,
    )
    taxform_year_id = fields.Many2one(
        string="Tahun Pajak",
        comodel_name="l10n_id.tax_year",
        compute="_compute_taxform_year",
        store=True,
        copy=False,
    )
    allowed_fpk_journal_ids = fields.Many2many(
        string="Allowed FP Keluaran Journal",
        comodel_name="account.journal",
        compute="_compute_allowed_fpk_journal_ids",
        compute_sudo=True,
        store=False,
    )
    allowed_fpk_account_ids = fields.Many2many(
        string="Allowed FP Keluaran Accounts",
        comodel_name="account.account",
        compute="_compute_allowed_fpk_account_ids",
        compute_sudo=True,
        store=False,
    )
    allowed_fpk_tax_ids = fields.Many2many(
        string="Allowed FP Keluaran Taxes",
        comodel_name="account.tax",
        compute="_compute_allowed_fpk_tax_ids",
        compute_sudo=True,
        store=False,
    )

    type_id = fields.Many2one(
        string="Transaction Type",
        comodel_name="faktur_pajak_transaction_type",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    enofa_number_id = fields.Many2one(
        string="# E-NOFA",
        comodel_name="enofa_number",
        required=False,
        readonly=True,
    )
    tax_id = fields.Many2one(
        string="Tax",
        comodel_name="account.tax",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )

    @api.depends(
        "type_id",
    )
    def _compute_allowed_add_info_ids(self):
        for record in self:
            result = False
            AddInfo = self.env["additional_info"]
            if record.type_id:
                criteria = [
                    ("type_id", "=", record.type_id.id),
                ]
                result = AddInfo.search(criteria).ids
            record.allowed_add_info_ids = result

    allowed_add_info_ids = fields.Many2many(
        string="Allowed Additional Info",
        comodel_name="additional_info",
        compute="_compute_allowed_add_info_ids",
        store=False,
        compute_sudo=True,
    )

    add_info_id = fields.Many2one(
        string="Additional Info",
        comodel_name="additional_info",
        required=False,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )

    @api.depends(
        "type_id",
    )
    def _compute_allowed_facility_stamp_ids(self):
        for record in self:
            result = False
            FacilityStamp = self.env["facility_stamp"]
            if record.type_id:
                criteria = [
                    ("type_id", "=", record.type_id.id),
                ]
                result = FacilityStamp.search(criteria).ids
            record.allowed_facility_stamp_ids = result

    allowed_facility_stamp_ids = fields.Many2many(
        string="Allowed Facility Stamp",
        comodel_name="facility_stamp",
        compute="_compute_allowed_facility_stamp_ids",
        store=False,
        compute_sudo=True,
    )

    facility_stamp_id = fields.Many2one(
        string="Facility Stamp",
        comodel_name="facility_stamp",
        required=False,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )

    @api.model
    def _default_buyer_document_id(self):
        try:
            result = self.env.ref(
                "ssi_l10n_id_taxform_faktur_pajak.fp_buyer_document_tin"
            ).id
        except Exception:
            result = False
        return result

    buyer_document_id = fields.Many2one(
        string="Buyer Document",
        comodel_name="buyer_document",
        required=True,
        readonly=True,
        default=lambda self: self._default_buyer_document_id(),
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )

    allowed_enofa_number_ids = fields.Many2many(
        string="Allowed E-NOFA Numbers",
        comodel_name="enofa_number",
        compute="_compute_allowed_enofa_number_ids",
        store=False,
        compute_sudo=True,
    )
    allowed_move_ids = fields.Many2many(
        string="Allowed Journal Entries",
        comodel_name="account.move",
        compute="_compute_allowed_move_ids",
        store=False,
        compute_sudo=True,
    )
    move_ids = fields.Many2many(
        string="Journal Entries",
        comodel_name="account.move",
        relation="el_faktur_pajak_keluaran_2_journal_entry",
        column1="faktur_pajak_keluaran_id",
        column2="move_id",
    )
    allowed_move_line_ids = fields.Many2many(
        string="Allowed Journal Items",
        comodel_name="account.move.line",
        compute="_compute_allowed_move_line_ids",
        store=False,
        compute_sudo=True,
    )
    detail_ids = fields.One2many(
        string="Details",
        comodel_name="faktur_pajak_keluaran_detail",
        inverse_name="faktur_pajak_keluaran_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    tax_ids = fields.One2many(
        string="Taxes",
        comodel_name="faktur_pajak_keluaran_tax",
        inverse_name="faktur_pajak_keluaran_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    efaktur_mode = fields.Selection(
        string="E-Faktur Mode",
        selection=[
            ("header", "Header"),
            ("detail", "Detail"),
        ],
        required=True,
        default="detail",
    )
    efaktur_kd_jenis_transaksi = fields.Char(
        string="KD_JENIS_TRANSAKSI",
        compute="_compute_efaktur_kd_jenis_transaksi",
        store=True,
        compute_sudo=True,
    )
    efaktur_fg_pengganti = fields.Char(
        string="FG_PENGGANTI",
        compute="_compute_efaktur_fg_pengganti",
        store=True,
        compute_sudo=True,
    )
    efaktur_nomor_faktur = fields.Char(
        string="NOMOR_FAKTUR",
        compute="_compute_efaktur_nomor_faktur",
        store=True,
        compute_sudo=True,
    )

    @api.depends(
        "enofa_number_id",
    )
    def _compute_efaktur_nomor_faktur(self):
        for record in self:
            result = "-"
            if record.enofa_number_id:
                result = record.enofa_number_id.name.replace(".", "")
            record.efaktur_nomor_faktur = result

    efaktur_masa_pajak = fields.Char(
        string="MASA_PAJAK",
        compute="_compute_efaktur_masa_pajak",
        store=True,
        compute_sudo=True,
    )

    @api.depends("taxform_period_id")
    def _compute_efaktur_masa_pajak(self):
        for record in self:
            result = "-"
            if record.taxform_period_id:
                result = str(record.taxform_period_id.date_start.month).zfill(2)
            record.efaktur_masa_pajak = result

    efaktur_tahun_pajak = fields.Char(
        string="TAHUN_FAKTUR",
        compute="_compute_efaktur_tahun_pajak",
        store=True,
        compute_sudo=True,
    )

    @api.depends("taxform_year_id")
    def _compute_efaktur_tahun_pajak(self):
        for record in self:
            result = "-"
            if record.taxform_year_id:
                result = str(record.taxform_period_id.date_start.year)
            record.efaktur_tahun_pajak = result

    efaktur_tanggal_faktur = fields.Char(
        string="TANGGAL_FAKTUR",
        compute="_compute_efaktur_tanggal_faktur",
        store=True,
        compute_sudo=True,
    )

    @api.depends(
        "date",
    )
    def _compute_efaktur_tanggal_faktur(self):
        for record in self:
            result = "-"
            if record.date:
                result = record.date.strftime("%d/%m/%Y")
            record.efaktur_tanggal_faktur = result

    @api.depends(
        "partner_id",
    )
    def _compute_efaktur_npwp(self):
        for record in self:
            result = "000000000000000"
            if record.partner_id and record.partner_id.vat:
                npwp = record.partner_id.vat
                result = ""
                for s in re.findall(r"\d+", npwp):
                    result += s
            record.efaktur_npwp = result

    efaktur_npwp = fields.Char(
        string="NPWP",
        compute="_compute_efaktur_npwp",
        store=True,
        compute_sudo=True,
    )

    @api.depends(
        "company_id",
        "company_id.partner_id",
        "company_id.partner_id.vat",
    )
    def _compute_efaktur_company_npwp(self):
        for record in self:
            result = "000000000000000"
            if record.company_id and record.company_id.partner_id.vat:
                npwp = record.company_id.partner_id.vat
                result = ""
                for s in re.findall(r"\d+", npwp):
                    result += s
            record.efaktur_company_npwp = result

    efaktur_company_npwp = fields.Char(
        string="Company NPWP",
        compute="_compute_efaktur_company_npwp",
        store=True,
        compute_sudo=True,
    )

    @api.depends(
        "company_id",
        "company_id.partner_id",
        "company_id.partner_id.nitku",
    )
    def _compute_efaktur_seller_id_tku(self):
        for record in self:
            result = "0000000000000000"
            if (
                record.company_id
                and record.company_id.partner_id
                and record.company_id.partner_id.nitku
            ):
                result = record.company_id.partner_id.nitku
            record.efaktur_seller_id_tku = result

    efaktur_seller_id_tku = fields.Char(
        string="SELLER_ID_TKU",
        compute="_compute_efaktur_seller_id_tku",
        store=True,
        compute_sudo=True,
    )

    efaktur_nama = fields.Char(
        string="NAMA",
        compute="_compute_efaktur_nama",
        store=True,
        compute_sudo=True,
    )

    @api.depends("partner_id")
    def _compute_efaktur_nama(self):
        for record in self:
            result = "-"
            if record.partner_id:
                result = record.partner_id.name
            record.efaktur_nama = result

    efaktur_alamat_lengkap = fields.Char(
        string="ALAMAT_LENGKAP",
        compute="_compute_efaktur_alamat_lengkap",
        store=True,
        compute_sudo=True,
    )

    @api.depends(
        "partner_id",
        "contact_partner_id",
    )
    def _compute_efaktur_alamat_lengkap(self):
        for record in self:
            result = "-"
            if record.partner_id:
                result = ""
                if record.tax_address_id:
                    partner = record.tax_address_id
                else:
                    partner = record.partner_id

                if partner.street:
                    result += partner.street + ". "

                if partner.street2:
                    result += partner.street2 + ". "

                if partner.city:
                    result += partner.city + ". "

                if partner.state_id:
                    result += partner.state_id.name + ". "

                if partner.zip:
                    result += partner.zip + ". "

            record.efaktur_alamat_lengkap = result

    efaktur_jumlah_ppn = fields.Char(
        string="JUMLAH_PPN",
        compute="_compute_efaktur_jumlah_ppn",
        store=True,
        compute_sudo=True,
    )

    @api.depends("amount_tax")
    def _compute_efaktur_jumlah_ppn(self):
        for record in self:
            record.efaktur_jumlah_ppn = str(int(record.amount_tax))

    efaktur_jumlah_dpp = fields.Char(
        string="JUMLAH_DPP",
        compute="_compute_efaktur_jumlah_dpp",
        store=True,
        compute_sudo=True,
    )

    @api.depends("amount_untaxed")
    def _compute_efaktur_jumlah_dpp(self):
        for record in self:
            record.efaktur_jumlah_dpp = str(int(record.amount_untaxed))

    efaktur_referensi = fields.Char(
        string="REFERENSI",
        compute="_compute_efaktur_referensi",
        store=True,
        compute_sudo=True,
    )

    @api.depends("add_info_id")
    def _compute_efaktur_of_add_info(self):
        for record in self:
            result = "-"
            if record.add_info_id:
                result = record.add_info_id.code
            record.efaktur_of_add_info = result

    efaktur_of_add_info = fields.Char(
        string="ADD_INFO",
        compute="_compute_efaktur_of_add_info",
        store=True,
        compute_sudo=True,
    )

    @api.depends("facility_stamp_id")
    def _compute_efaktur_of_facility_stamp(self):
        for record in self:
            result = "-"
            if record.facility_stamp_id:
                result = record.facility_stamp_id.code
            record.efaktur_of_facility_stamp = result

    efaktur_of_facility_stamp = fields.Char(
        string="FACILITY_STAMP",
        compute="_compute_efaktur_of_facility_stamp",
        store=True,
        compute_sudo=True,
    )

    need_add_info = fields.Boolean(
        related="type_id.need_add_info",
    )
    need_facility_stamp = fields.Boolean(
        related="type_id.need_facility_stamp",
    )

    @api.depends("buyer_document_id")
    def _compute_efaktur_of_buyer_document(self):
        for record in self:
            result = "-"
            if record.buyer_document_id:
                result = record.buyer_document_id.code
            record.efaktur_of_buyer_document = result

    efaktur_of_buyer_document = fields.Char(
        string="BUYER DOCUMENT",
        compute="_compute_efaktur_of_buyer_document",
        store=True,
        compute_sudo=True,
    )

    @api.depends(
        "partner_id",
        "partner_id.country_id",
    )
    def _compute_efaktur_country(self):
        for record in self:
            result = "-"
            if record.partner_id:
                if record.partner_id.country_id:
                    result = record.partner_id.country_id.efaktur_code

            record.efaktur_country = result

    efaktur_country = fields.Char(
        string="BUYER COUNTRY",
        compute="_compute_efaktur_country",
        store=True,
        compute_sudo=True,
    )

    @api.depends(
        "partner_id",
        "partner_id.email",
    )
    def _compute_efaktur_email(self):
        for record in self:
            result = "-"
            if record.partner_id:
                if record.partner_id.email:
                    result = record.partner_id.email

            record.efaktur_email = result

    efaktur_email = fields.Char(
        string="BUYER EMAIL",
        compute="_compute_efaktur_email",
        store=True,
        compute_sudo=True,
    )

    @api.depends(
        "partner_id",
        "partner_id.nitku",
    )
    def _compute_efaktur_buyer_id_tku(self):
        for record in self:
            result = "0000000000000000"
            if record.partner_id and record.partner_id.nitku:
                result = record.partner_id.nitku
            record.efaktur_buyer_id_tku = result

    efaktur_buyer_id_tku = fields.Char(
        string="BUYER_ID_TKU",
        compute="_compute_efaktur_buyer_id_tku",
        store=True,
        compute_sudo=True,
    )

    @api.depends(
        "move_ids",
    )
    def _compute_efaktur_referensi(self):
        for record in self:
            result = "-"
            if record.move_ids:
                result = ", ".join(str(e) for e in record.move_ids.mapped("name"))
            record.efaktur_referensi = result

    efaktur_of_opt = fields.Selection(
        string="OF_OPT",
        selection=[("A", "Barang"), ("B", "Jasa")],
        required=True,
        readonly=True,
        default="A",
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )

    @api.depends(
        "move_ids",
    )
    def _compute_efaktur_of_name(self):
        for record in self:
            result = "-"
            if record.move_ids:
                result = ", ".join(str(e) for e in record.move_ids.mapped("name"))
            record.efaktur_of_name = result

    efaktur_of_name = fields.Char(
        string="OF_NAMA",
        compute="_compute_efaktur_of_name",
        store=True,
        compute_sudo=True,
    )

    @api.depends("amount_untaxed")
    def _compute_efaktur_of_harga_satuan(self):
        for record in self:
            record.efaktur_of_harga_satuan = str(int(record.amount_untaxed))

    efaktur_of_harga_satuan = fields.Char(
        string="OF_HARGA_SATUAN",
        compute="_compute_efaktur_of_harga_satuan",
        store=True,
        compute_sudo=True,
    )

    @api.depends("amount_untaxed")
    def _compute_efaktur_of_jumlah_barang(self):
        for record in self:
            record.efaktur_of_jumlah_barang = 1

    efaktur_of_jumlah_barang = fields.Char(
        string="OF_JUMLAH_BARANG",
        compute="_compute_efaktur_of_jumlah_barang",
        store=True,
        compute_sudo=True,
    )

    @api.depends("amount_untaxed")
    def _compute_efaktur_of_harga_total(self):
        for record in self:
            record.efaktur_of_harga_total = str(int(record.amount_untaxed))

    efaktur_of_harga_total = fields.Char(
        string="OF_HARGA_TOTAL",
        compute="_compute_efaktur_of_harga_total",
        store=True,
        compute_sudo=True,
    )

    @api.depends("amount_untaxed")
    def _compute_efaktur_of_diskon(self):
        for record in self:
            record.efaktur_of_diskon = 0

    efaktur_of_diskon = fields.Char(
        string="OF_DISKON",
        compute="_compute_efaktur_of_diskon",
        store=True,
        compute_sudo=True,
    )

    @api.depends("amount_untaxed")
    def _compute_efaktur_of_dpp(self):
        for record in self:
            record.efaktur_of_dpp = str(int(record.amount_untaxed))

    efaktur_of_dpp = fields.Char(
        string="OF_DPP",
        compute="_compute_efaktur_of_dpp",
        store=True,
        compute_sudo=True,
    )

    @api.depends("amount_tax")
    def _compute_efaktur_of_ppn(self):
        for record in self:
            record.efaktur_of_ppn = str(int(record.amount_tax))

    efaktur_of_ppn = fields.Char(
        string="OF_PPN",
        compute="_compute_efaktur_of_ppn",
        store=True,
        compute_sudo=True,
    )

    @api.depends(
        "type_id",
    )
    def _compute_efaktur_kd_jenis_transaksi(self):
        for record in self:
            result = ""
            if record.type_id:
                result = record.type_id.code
            record.efaktur_kd_jenis_transaksi = result

    @api.depends(
        "type_id",
        "enofa_number_id",
        "enofa_number_id.faktur_pajak_keluaran_ids",
        "enofa_number_id.faktur_pajak_keluaran_ids.state",
    )
    def _compute_efaktur_fg_pengganti(self):
        for record in self:
            result = "0"
            if record.enofa_number_id:
                criteria = [
                    ("enofa_number_id", "=", record.enofa_number_id.id),
                ]
                FPKs = self.env["faktur_pajak_keluaran"].search(criteria)
                if len(FPKs) > 1:
                    if record.id == FPKs[-1].id:
                        result = "1"
            record.efaktur_fg_pengganti = result

    @api.depends("type_id")
    def _compute_allowed_fpk_journal_ids(self):
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="account.journal",
                    method_selection=record.type_id.fpk_journal_selection_method,
                    manual_recordset=record.type_id.fpk_journal_ids,
                    domain=record.type_id.fpk_journal_domain,
                    python_code=record.type_id.fpk_journal_python_code,
                )
            record.allowed_fpk_journal_ids = result

    @api.depends("type_id")
    def _compute_allowed_fpk_account_ids(self):
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="account.account",
                    method_selection=record.type_id.fpk_account_selection_method,
                    manual_recordset=record.type_id.fpk_account_ids,
                    domain=record.type_id.fpk_account_domain,
                    python_code=record.type_id.fpk_account_python_code,
                )
            record.allowed_fpk_account_ids = result

    @api.depends("type_id")
    def _compute_allowed_fpk_tax_ids(self):
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="account.tax",
                    method_selection=record.type_id.fpk_tax_selection_method,
                    manual_recordset=record.type_id.fpk_tax_ids,
                    domain=record.type_id.fpk_tax_domain,
                    python_code=record.type_id.fpk_tax_python_code,
                )
            record.allowed_fpk_tax_ids = result

    @api.depends(
        "type_id",
        "partner_id",
    )
    def _compute_allowed_move_ids(self):
        AM = self.env["account.move"]
        for record in self:
            result = False
            if record.type_id and record.partner_id:
                criteria1 = [
                    ("faktur_pajak_keluaran_id", "=", False),
                    ("state", "=", "posted"),
                    ("journal_id", "in", record.allowed_fpk_journal_ids.ids),
                    ("partner_id.commercial_partner_id.id", "=", record.partner_id.id),
                ]
                result = AM.search(criteria1)
                criteria2 = [
                    ("faktur_pajak_keluaran_id", "!=", False),
                    ("fp_keluaran_state", "in", ["draft", "cancelled"]),
                    ("state", "=", "posted"),
                    ("journal_id", "in", record.allowed_fpk_journal_ids.ids),
                    ("partner_id.commercial_partner_id.id", "=", record.partner_id.id),
                ]
                result += AM.search(criteria2)
            record.allowed_move_ids = result

    @api.depends(
        "company_id",
        "taxform_year_id",
    )
    def _compute_allowed_enofa_number_ids(self):
        for record in self:
            result = False
            ENofaNumber = self.env["enofa_number"]
            if record.company_id and record.taxform_year_id:
                criteria = [
                    ("enofa_id.company_id", "=", self.company_id.id),
                    ("enofa_id.tax_year_id", "=", self.taxform_year_id.id),
                    ("state", "=", "unused"),
                ]
                result = ENofaNumber.search(criteria).ids
            record.allowed_enofa_number_ids = result

    @api.depends(
        "move_ids",
    )
    def _compute_allowed_move_line_ids(self):
        for record in self:
            result = False
            AML = self.env["account.move.line"]
            if record.move_ids:
                criteria = [
                    ("move_id", "in", record.move_ids.ids),
                    ("credit", ">", 0.0),
                    ("tax_ids", "!=", False),
                    ("account_id", "in", record.allowed_fpk_account_ids.ids),
                    ("tax_ids", "in", self.allowed_fpk_tax_ids.ids),
                ]
                result = AML.search(criteria).ids
            record.allowed_move_line_ids = result

    @api.depends(
        "date",
    )
    def _compute_taxform_period(self):
        for fp in self:
            fp.taxform_period_id = False
            if fp.date:
                fp.taxform_period_id = (
                    self.env["l10n_id.tax_period"]._find_period(fp.date).id
                )

    @api.depends(
        "taxform_period_id",
    )
    def _compute_taxform_year(self):
        for fp in self:
            fp.taxform_year_id = False
            if fp.taxform_period_id:
                fp.taxform_year_id = fp.taxform_period_id.year_id.id

    @api.onchange(
        "type_id",
    )
    def onchange_efaktur_mode(self):
        self.efaktur_mode = False
        if self.type_id:
            self.efaktur_mode = self.type_id.efaktur_mode

    @api.onchange(
        "type_id",
    )
    def onchange_tax_id(self):
        self.tax_id = False
        if self.type_id:
            self.tax_id = self.type_id.tax_id

    def action_reload_detail(self):
        Detail = self.env["faktur_pajak_keluaran_detail"]
        self.detail_ids.unlink()
        for record in self.sudo():
            if record.allowed_move_line_ids:
                for aml in record.allowed_move_line_ids:
                    data = {
                        "faktur_pajak_keluaran_id": self.id,
                        "name": (aml.product_id and aml.product_id.name)
                        or aml.name
                        or "-",
                        "account_id": aml.account_id.id,
                        "product_id": aml.product_id and aml.product_id.id,
                        "uom_quantity": aml.quantity or 1.0,
                        "uom_id": aml.product_uom_id and aml.product_uom_id.id,
                        "price_unit": aml.credit / (aml.quantity or 1.0),
                        "tax_ids": [(6, 0, [self.tax_id.id])],
                    }
                    Detail.create(data)
        self._recompute_standard_tax()

    def action_recompute_efaktur_fields(self):
        for record in self:
            record.invalidate_cache()

            record._compute_efaktur_kd_jenis_transaksi()
            record._compute_efaktur_fg_pengganti()
            record._compute_efaktur_nomor_faktur()
            record._compute_efaktur_masa_pajak()
            record._compute_efaktur_tahun_pajak()
            record._compute_efaktur_tanggal_faktur()
            record._compute_efaktur_npwp()
            record._compute_efaktur_company_npwp()
            record._compute_efaktur_seller_id_tku()
            record._compute_efaktur_nama()
            record._compute_efaktur_alamat_lengkap()
            record._compute_efaktur_jumlah_ppn()
            record._compute_efaktur_jumlah_dpp()
            record._compute_efaktur_referensi()
            record._compute_efaktur_of_add_info()
            record._compute_efaktur_of_facility_stamp()
            record._compute_efaktur_of_buyer_document()
            record._compute_efaktur_country()
            record._compute_efaktur_email()
            record._compute_efaktur_buyer_id_tku()
            record._compute_efaktur_of_name()
            record._compute_efaktur_of_harga_satuan()
            record._compute_efaktur_of_jumlah_barang()
            record._compute_efaktur_of_harga_total()
            record._compute_efaktur_of_diskon()
            record._compute_efaktur_of_dpp()
            record._compute_efaktur_of_ppn()

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Success"),
                "message": _("All E-Faktur fields have been recomputed successfully."),
                "type": "success",
                "sticky": False,
            },
        }

    @api.model
    def _get_policy_field(self):
        res = super()._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "reject_ok",
            "done_ok",
            "cancel_ok",
            "terminate_ok",
            "restart_ok",
            "reject_ok",
            "manual_number_ok",
            "restart_approval_ok",
        ]
        res += policy_field
        return res

    @ssi_decorator.pre_done_check()
    def _check_document_number(self):
        self.ensure_one()
        if self.name == "/":
            error_message = """
            Document Type: %s
            Context: Finish document
            Database ID: %s
            Problem: Missing FPK number from coretax
            Solution: Fill document number with coretax's FPK number
            """ % (
                self._description.lower(),
                self.id,
            )
            raise UserError(_(error_message))

    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch
