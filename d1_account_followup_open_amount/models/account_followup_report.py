# Copyright 2026 DooIT B.V.
# License LGPL-3 (https://www.gnu.org/licenses/lgpl-3.0.html)
#
# The modern "Follow-Up Report" (account_reports) is built on the Partner Ledger
# report engine. Out of the box it shows two amount columns:
#   * "Amount"  (expression 'amount')  -> account_move_line.balance (original)
#   * "Balance" (expression 'balance') -> a RUNNING/cumulative balance
# For a partially paid invoice this is confusing: "Amount" shows the original
# amount and "Balance" shows a running total, not the open amount per invoice.
#
# We want, per invoice line:
#   * "Amount" (Bedrag) -> the ORIGINAL invoice amount (unchanged: balance)
#   * "Balance" (Saldo) -> the OPEN amount of THAT invoice (amount_residual),
#                          NOT a running total.
# And on the total row:
#   * "Amount" total -> sum of the original amounts of the open invoices
#   * "Balance" total -> sum of the open amounts of the open invoices
#
# We override the follow-up report handler (account.followup.report.handler, an
# in-place prototype of account.partner.ledger.report.handler, so these overrides
# ONLY affect the follow-up report and not the partner ledger).
#
# Odoo reworked this in version 19; drop this module after upgrading to v19.
from odoo import models
from odoo.tools import SQL


class D1FollowupReportHandler(models.AbstractModel):
    _inherit = "account.followup.report.handler"

    # #D1 Follow-up: Bedrag = origineel, Saldo = open saldo per factuur (V19 backport)
    def _get_aml_value_extra_select(self):
        # Fetch the residual amount alongside the aml values so we can show it in
        # the "Balance" column and filter fully reconciled lines out.
        res = list(super()._get_aml_value_extra_select())
        res.append(
            SQL(", account_move_line.amount_residual AS d1_amount_residual")
        )
        return res

    def _get_report_line_move_line(
        self, options, aml_query_result, partner_line_id, init_bal_by_col_group,
        level_shift=0,
    ):
        # Keep the "Amount" column as the original amount (balance) and replace
        # the "Balance" column with the open amount (amount_residual) of this
        # single invoice line - i.e. no running/cumulative total.
        line = super()._get_report_line_move_line(
            options, aml_query_result, partner_line_id, init_bal_by_col_group,
            level_shift=level_shift,
        )
        if "d1_amount_residual" in aml_query_result:
            report = self.env["account.report"].browse(options["report_id"])
            residual = aml_query_result["d1_amount_residual"]
            for idx, column in enumerate(options["columns"]):
                if (
                    column["expression_label"] == "balance"
                    and column["column_group_key"]
                    == aml_query_result["column_group_key"]
                ):
                    line["columns"][idx] = report._build_column_dict(
                        residual, column, options=options
                    )
        return line

    def _filter_overdue_amls_from_results(self, aml_results):
        # Drop fully reconciled lines (open amount = 0), e.g. payment counterparts
        # and fully paid invoices - a follow-up should only dun open amounts.
        results = super()._filter_overdue_amls_from_results(aml_results)
        return [aml for aml in results if aml.get("d1_amount_residual")]

    def _filter_due_amls_from_results(self, aml_results):
        # Drop fully reconciled lines (open amount = 0), e.g. payment counterparts
        # and fully paid invoices - a follow-up should only dun open amounts.
        results = super()._filter_due_amls_from_results(aml_results)
        return [aml for aml in results if aml.get("d1_amount_residual")]

    def _get_query_sums(self, report, options) -> SQL:
        # Total row, computed only over still-open lines (amount_residual != 0) so
        # it matches the displayed lines:
        #   * amount  (Bedrag) = SUM(balance)          -> original invoice amounts
        #   * balance (Saldo)  = SUM(amount_residual)  -> open amounts
        #
        # This is a copy of account.partner.ledger.report.handler._get_query_sums
        # with the "balance" aggregate switched to amount_residual and a filter on
        # open lines added. Only the follow-up report is affected (prototype
        # inheritance). Kept in sync with 18.0; drop this module on the v19 move.
        queries = []
        for column_group_key, column_group_options in report._split_options_per_column_group(options).items():
            query = report._get_report_query(column_group_options, "from_beginning")
            date_from = options["date"]["date_from"]
            queries.append(SQL(
                """
                (WITH partner_sums AS (
                    SELECT
                        account_move_line.partner_id            AS groupby,
                        %(column_group_key)s                    AS column_group_key,
                        SUM(%(debit_select)s)                   AS debit,
                        SUM(%(credit_select)s)                  AS credit,
                        SUM(%(balance_select)s)                 AS amount,
                        SUM(%(residual_select)s)                AS balance,
                        BOOL_AND(account_move_line.reconciled)  AS all_reconciled,
                        MAX(account_move_line.date)             AS latest_date
                    FROM %(table_references)s
                    %(currency_table_join)s
                    WHERE %(search_condition)s
                    AND account_move_line.amount_residual != 0
                    GROUP BY account_move_line.partner_id
                )
                SELECT *
                FROM partner_sums
                WHERE partner_sums.balance != 0
                OR partner_sums.all_reconciled = FALSE
                OR partner_sums.latest_date >= %(date_from)s
                )""",
                column_group_key=column_group_key,
                debit_select=report._currency_table_apply_rate(SQL("account_move_line.debit")),
                credit_select=report._currency_table_apply_rate(SQL("account_move_line.credit")),
                # #D1 Bedrag-totaal = origineel, Saldo-totaal = open saldo
                balance_select=report._currency_table_apply_rate(SQL("account_move_line.balance")),
                residual_select=report._currency_table_apply_rate(SQL("account_move_line.amount_residual")),
                # #D1 einde
                table_references=query.from_clause,
                currency_table_join=report._currency_table_aml_join(column_group_options),
                search_condition=query.where_clause,
                date_from=date_from,
            ))

        return SQL(" UNION ALL ").join(queries)
    # #D1 einde
