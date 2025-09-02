# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).
# pylint: disable=W0622

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CreateFakturPajakKeluaran(models.TransientModel):
    _name = "create_faktur_pajak_keluaran"
    _inherit = [
        "mixin.many2one_configurator",
    ]
    _description = "Create Faktur Pajak Keluaran"

    move_ids = fields.Many2many(
        string="Journal Entries",
        comodel_name="account.move",
        default=lambda self: self._default_move_ids(),
    )
    partner_ids = fields.Many2many(
        string="Partners",
        comodel_name="res.partner",
        compute="_compute_partner_ids",
        store=False,
    )
    group_by_partner = fields.Boolean(
        string="Group By Partner",
        default=True,
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="faktur_pajak_transaction_type",
        required=True,
    )
    efaktur_mode = fields.Selection(
        string="E-Faktur Mode",
        selection=[
            ("header", "Header"),
            ("detail", "Detail"),
        ],
        required=True,
    )
    efaktur_opt = fields.Selection(
        string="OPT",
        selection=[
            ("A", "Barang"),
            ("B", "Jasa"),
        ],
        required=False,
    )
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
    )
    facility_stamp_id = fields.Many2one(
        string="Facility Stamp",
        comodel_name="facility_stamp",
        required=False,
    )
    allowed_facility_stamp_ids = fields.Many2many(
        string="Allowed Facility Stamp",
        comodel_name="facility_stamp",
        compute="_compute_allowed_facility_stamp_ids",
        store=False,
        compute_sudo=True,
    )
    buyer_document_id = fields.Many2one(
        string="Buyer Document",
        comodel_name="buyer_document",
        required=True,
    )
    allowed_fpk_journal_ids = fields.Many2many(
        string="Allowed FP Keluaran Journal",
        comodel_name="account.journal",
        compute="_compute_allowed_fpk_journal_ids",
        compute_sudo=True,
        store=False,
    )
    allowed_move_ids = fields.Many2many(
        string="Allowed Journal Entries",
        comodel_name="account.move",
        compute="_compute_allowed_move_ids",
        store=False,
        compute_sudo=True,
    )

    @api.model
    def _default_move_ids(self):
        return self.env.context.get("active_ids", [])

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

    @api.depends(
        "type_id",
        "move_ids",
    )
    def _compute_allowed_move_ids(self):
        AM = self.env["account.move"]
        for record in self:
            result = False
            if record.type_id and record.move_ids:
                criteria1 = [
                    ("faktur_pajak_keluaran_id", "=", False),
                    ("state", "=", "posted"),
                    ("journal_id", "in", record.allowed_fpk_journal_ids.ids),
                    ("id", "in", record.move_ids.ids),
                ]
                result = AM.search(criteria1)
                criteria2 = [
                    ("faktur_pajak_keluaran_id", "!=", False),
                    ("fp_keluaran_state", "in", ["cancel"]),
                    ("state", "=", "posted"),
                    ("journal_id", "in", record.allowed_fpk_journal_ids.ids),
                    ("id", "in", record.move_ids.ids),
                ]
                result += AM.search(criteria2)
            record.allowed_move_ids = result

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

    @api.depends("allowed_move_ids")
    def _compute_partner_ids(self):
        for record in self:
            result = []
            if record.move_ids:
                result = record.allowed_move_ids.mapped(
                    "partner_id.commercial_partner_id"
                )
            record.partner_ids = result

    @api.onchange(
        "type_id",
    )
    def onchange_facility_stamp_id(self):
        self.facility_stamp_id = False

    @api.onchange(
        "type_id",
    )
    def onchange_efaktur_mode(self):
        self.efaktur_mode = False
        if self.type_id.efaktur_mode:
            self.efaktur_mode = self.type_id.efaktur_mode

    def action_confirm(self):
        for record in self.sudo():
            record._confirm()

    def _confirm(self):
        self.ensure_one()
        if self.group_by_partner:
            self._create_fpk_by_partner()
        else:
            self._create_fpk()

    def _create_fpk(self):
        self.ensure_one()
        FPK = self.env["faktur_pajak_keluaran"]
        for am in self.allowed_move_ids:
            data = {
                "partner_id": am.partner_id.commercial_partner_id.id,
                "type_id": self.type_id.id,
                "date": am.invoice_date,
                "tax_id": self.type_id.tax_id.id,
                "move_ids": [(6, 0, [am.id])],
                "efaktur_mode": self.efaktur_mode,
            }
            if self.efaktur_mode == "header":
                data["efaktur_of_opt"] = self.efaktur_opt
            fpk = FPK.create(data)
            fpk.action_reload_detail()

    def _create_fpk_by_partner(self):
        self.ensure_one()
        FPK = self.env["faktur_pajak_keluaran"]
        for partner in self.partner_ids:
            ams = self.allowed_move_ids.filtered(
                lambda r: r.partner_id.commercial_partner_id.id == partner.id
            )
            data = {
                "partner_id": partner.id,
                "type_id": self.type_id.id,
                "date": ams[0].invoice_date,
                "tax_id": self.type_id.tax_id.id,
                "move_ids": [(6, 0, ams.ids)],
                "efaktur_mode": self.efaktur_mode,
            }
            if self.efaktur_mode == "header":
                data["efaktur_of_opt"] = self.efaktur_opt
            fpk = FPK.create(data)
            fpk.action_reload_detail()

    def _get_enofa_number(self):
        self.ensure_one()
        ENofa = self.env["enofa"]
        ENofaNumber = self.env["enofa_number"]
        criteria = [("state", "=", "open")]
        enofas = ENofa.search(criteria)
        number = False

        if len(enofas) == 0:
            str_error = _("No E-NOFA found")
            raise UserError(str_error)

        enofa = enofas[0]

        for enofa in enofas:

            criteria = [
                ("enofa_id", "=", enofa.id),
                ("state", "=", "unused"),
            ]
            numbers = ENofaNumber.search(criteria)

            if len(numbers) > 0:
                number = numbers[0]
                break

        if not number:
            str_error = _("No E-NOFA number found")
            raise UserError(str_error)

        return number
