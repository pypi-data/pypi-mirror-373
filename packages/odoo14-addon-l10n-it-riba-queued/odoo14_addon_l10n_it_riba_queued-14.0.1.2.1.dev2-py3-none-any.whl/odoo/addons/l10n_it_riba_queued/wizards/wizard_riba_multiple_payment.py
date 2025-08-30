# Copyright 2025 Simone Rubino - PyTech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class RibaPaymentMultiple(models.TransientModel):
    _inherit = "riba.payment.multiple"

    def pay_async(self):
        return self.with_context(
            l10n_it_riba_async_single_process=True,
        ).pay()
