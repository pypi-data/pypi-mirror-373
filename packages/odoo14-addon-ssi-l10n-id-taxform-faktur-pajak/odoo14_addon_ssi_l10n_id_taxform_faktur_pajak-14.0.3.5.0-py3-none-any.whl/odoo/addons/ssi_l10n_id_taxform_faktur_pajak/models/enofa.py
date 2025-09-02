# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class ENofa(models.Model):
    _name = "enofa"
    _inherit = [
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_open",
        "mixin.transaction_confirm",
    ]
    _description = "E-NOFA"

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "open"
    _approval_state = "confirm"
    _after_approved_method = "action_open"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True
    _automatically_insert_open_button = False
    _automatically_insert_open_policy_fields = False
    _automatically_insert_done_button = False
    _automatically_insert_done_policy_fields = False

    # Attributes related to add element on form view automatically
    _statusbar_visible_label = "draft,confirm,open,done"
    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "restart_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_confirm",
        "action_approve",
        "action_reject",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_open",
        "dom_done",
        "dom_cancel",
        "dom_reject",
    ]

    # Sequence attribute
    _create_sequence_state = "open"

    date_request = fields.Date(
        string="Date Request",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    request_number = fields.Char(
        string="# Request",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    date_issue = fields.Date(
        string="Date Issue",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    issue_number = fields.Char(
        string="# Issue",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    prefix = fields.Char(
        string="Prefix",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    num_of_nsfp = fields.Integer(
        string="Num. Of NSFP",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    first_num_of_nsfp = fields.Integer(
        string="First Num. Of NSFP",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    tax_year_id = fields.Many2one(
        string="Tax Year",
        comodel_name="l10n_id.tax_year",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    sequence_id = fields.Many2one(
        string="Sequence",
        comodel_name="ir.sequence",
        readonly=True,
    )
    number_ids = fields.One2many(
        string="Numbers",
        comodel_name="enofa_number",
        inverse_name="enofa_id",
        readonly=True,
    )

    @ssi_decorator.post_open_action()
    def _10_create_sequence(self):
        self.ensure_one()
        data = self._prepare_sequence_data()
        Sequence = self.env["ir.sequence"]
        sequence = Sequence.create(data)
        self.write(
            {
                "sequence_id": sequence.id,
            }
        )

    @ssi_decorator.post_open_action()
    def _11_delete_enofa_number(self):
        self.ensure_one()
        self.number_ids.unlink()

    @ssi_decorator.post_open_action()
    def _12_generate_enofa_number(self):
        self.ensure_one()
        EnofaNumber = self.env["enofa_number"]
        for _counter in range(1, self.num_of_nsfp):
            sequence = self.sequence_id.next_by_id()
            EnofaNumber.create(
                {
                    "enofa_id": self.id,
                    "name": sequence,
                }
            )

    def _prepare_sequence_data(self):
        self.ensure_one()
        return {
            "name": self.name,
            "prefix": self.prefix,
            "padding": len(str(self.first_num_of_nsfp)),
            "number_next": self.first_num_of_nsfp,
        }

    @api.model
    def _get_policy_field(self):
        res = super()._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "reject_ok",
            "cancel_ok",
            "restart_ok",
            "reject_ok",
            "manual_number_ok",
            "restart_approval_ok",
        ]
        res += policy_field
        return res

    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch
