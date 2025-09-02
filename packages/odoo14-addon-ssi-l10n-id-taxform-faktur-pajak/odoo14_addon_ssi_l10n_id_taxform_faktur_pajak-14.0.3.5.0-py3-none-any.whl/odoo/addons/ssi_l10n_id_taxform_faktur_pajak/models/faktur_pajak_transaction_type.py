# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FakturPajakTransactionType(models.Model):
    _name = "faktur_pajak_transaction_type"
    _inherit = [
        "mixin.master_data",
    ]
    _description = "Type of Faktur Pajak Transaction"

    efaktur_mode = fields.Selection(
        string="E-Faktur Mode",
        selection=[
            ("header", "Header"),
            ("detail", "Detail"),
        ],
        required=True,
        default="header",
    )
    fpk_journal_selection_method = fields.Selection(
        default="domain",
        selection=[("manual", "Manual"), ("domain", "Domain"), ("code", "Python Code")],
        string="FP Keluaran Journal Selection Method",
        required=True,
    )
    fpk_journal_ids = fields.Many2many(
        comodel_name="account.journal",
        string="FP Keluaran Journals",
        relation="fp_keluaran_type_2_journal",
        column1="type_id",
        column2="journal_id",
    )
    fpk_journal_domain = fields.Text(default="[]", string="FP Keluaran Journal Domain")
    fpk_journal_python_code = fields.Text(
        default="result = []", string="FP Keluaran Journal Python Code"
    )

    fpk_account_selection_method = fields.Selection(
        default="domain",
        selection=[("manual", "Manual"), ("domain", "Domain"), ("code", "Python Code")],
        string="FP Keluaran Account Selection Method",
        required=True,
    )
    fpk_account_ids = fields.Many2many(
        comodel_name="account.account",
        string="FP Keluaran Accounts",
        relation="fp_keluaran_type_2_account",
        column1="type_id",
        column2="account_id",
    )
    fpk_account_domain = fields.Text(default="[]", string="FP Keluaran Account Domain")
    fpk_account_python_code = fields.Text(
        default="result = []", string="FP Keluaran Account Python Code"
    )

    fpk_tax_selection_method = fields.Selection(
        default="domain",
        selection=[("manual", "Manual"), ("domain", "Domain"), ("code", "Python Code")],
        string="FP Keluaran Tax Selection Method",
        required=True,
    )
    fpk_tax_ids = fields.Many2many(
        comodel_name="account.tax",
        string="FP Keluaran Taxes",
        relation="fp_keluaran_type_2_tax",
        column1="type_id",
        column2="tax_id",
    )
    fpk_tax_domain = fields.Text(default="[]", string="FP Keluaran Tax Domain")
    fpk_tax_python_code = fields.Text(
        default="result = []", string="FP Keluaran Tax Python Code"
    )

    tax_id = fields.Many2one(
        string="Tax",
        comodel_name="account.tax",
    )
    need_add_info = fields.Boolean(
        string="Need Additional Info",
        default=False,
    )
    need_facility_stamp = fields.Boolean(
        string="Need Facility Stamp",
        default=False,
    )
