# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    if not version:
        return
    logger = logging.getLogger(__name__)
    logger.info("Updating faktur_pajak_keluaran...")

    env = api.Environment(cr, SUPERUSER_ID, dict())

    cr.execute(
        "UPDATE faktur_pajak_keluaran SET buyer_document_id = %s;",
        (env.ref("ssi_l10n_id_taxform_faktur_pajak.fp_buyer_document_tin").id,),
    )
    logger.info("Successfully updated faktur_pajak_keluaran tables")
