# Copyright 2026 DooIT B.V.
# License LGPL-3 (https://www.gnu.org/licenses/lgpl-3.0.html)
{
    "name": "Follow-Up Report Open Amount",
    "summary": "Show the open (residual) amount instead of the original amount "
    "on the Follow-Up Report for partially paid invoices",
    # NOTE: description carries the functional changelog (DooIT convention).
    "description": """
Follow-Up Report Open Amount 18.0.1.0.0
========================================
The modern Follow-Up Report (account_reports, based on the Partner Ledger
report engine) shows the ORIGINAL invoice amount (account_move_line.balance)
in the "Amount" column, even when an invoice is only partially paid. Customers
therefore receive follow-up letters/e-mails quoting the full invoice amount
instead of the remaining open balance, which is confusing.

Odoo fixed this behaviour in version 19. This module backports the fix to 18.0
by displaying the OPEN amount (amount_residual) instead of the original amount,
and by hiding fully reconciled counterpart lines (e.g. the bank payment lines
with a zero open balance).

Only the modern account.report "Follow-Up Report" is affected. The classic
account_followup e-mail body already used the residual amount and is untouched.

Remove this module after upgrading to Odoo 19 (the fix is standard there).

Changelog:
----------
* 18.0.1.0.0: Initial version. Amount column shows amount_residual; fully
  reconciled (residual = 0) lines are hidden.
""",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "author": "DooIT B.V.",
    "license": "LGPL-3",
    # account_reports defines the report record and the report handler model
    # (account.followup.report.handler) that we extend.
    "depends": ["account_reports"],
    "installable": True,
}
