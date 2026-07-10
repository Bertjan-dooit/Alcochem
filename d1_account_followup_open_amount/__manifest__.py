# Copyright 2026 DooIT B.V.
# License LGPL-3 (https://www.gnu.org/licenses/lgpl-3.0.html)
{
    "name": "Follow-Up Report Open Amount",
    "summary": "Show the original amount and the open amount per invoice "
    "on the Follow-Up Report for partially paid invoices",
    # NOTE: description carries the functional changelog (DooIT convention).
    "description": """
Follow-Up Report Open Amount 18.0.1.1.0
========================================
The modern Follow-Up Report (account_reports, based on the Partner Ledger
report engine) is confusing for partially paid invoices: the "Amount" column
shows the ORIGINAL invoice amount (account_move_line.balance) and the "Balance"
column shows a RUNNING/cumulative total - so a customer never sees the open
amount per invoice.

Odoo reworked this in version 19. This module adjusts the 18.0 report so that:
  * "Amount"  = the original invoice amount (per line);
  * "Balance" = the open amount (amount_residual) of THAT invoice (no running
    total);
  * the total row shows the sum of the original amounts and the sum of the open
    amounts, computed over the open lines only;
  * fully reconciled lines (open amount = 0, e.g. bank payment counterparts and
    fully paid invoices) are hidden.

Only the modern account.report "Follow-Up Report" is affected. The classic
account_followup e-mail body already used the residual amount and is untouched.

Remove this module after upgrading to Odoo 19 (the fix is standard there).

Changelog:
----------
* 18.0.1.1.0: "Amount" shows the original amount, "Balance" shows the open
  amount per invoice (no running total), totals sum each column separately.
* 18.0.1.0.0: Initial version. Amount column showed amount_residual; fully
  reconciled (residual = 0) lines are hidden.
""",
    "version": "18.0.1.1.0",
    "category": "Accounting",
    "author": "DooIT B.V.",
    "license": "LGPL-3",
    # account_reports defines the report record and the report handler model
    # (account.followup.report.handler) that we extend.
    "depends": ["account_reports"],
    "installable": True,
}
