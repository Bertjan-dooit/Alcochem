# Copyright 2026 DooIT B.V.
# License LGPL-3 (https://www.gnu.org/licenses/lgpl-3.0.html)
#
# The modern "Follow-Up Report" (account_reports) is built on the Partner Ledger
# report engine. Its "Amount" column maps to account_move_line.balance, i.e. the
# ORIGINAL amount of the move line. A partial payment only lowers amount_residual,
# not balance, so a partially paid invoice keeps showing its full original amount.
#
# We override the follow-up report handler (account.followup.report.handler, an
# in-place prototype of account.partner.ledger.report.handler, so these overrides
# ONLY affect the follow-up report and not the partner ledger) to:
#   1. fetch amount_residual/amount_residual_currency alongside the aml values;
#   2. display those residual values in the Amount / Amount Currency / Balance
#      columns instead of the original balance;
#   3. hide fully reconciled lines (residual = 0), e.g. the bank counterpart line
#      of a partial payment, which would otherwise clutter the report.
#
# The report totals are produced by a separate query (_query_partners) that sums
# the balances; that sum already equals the residual of the open invoices
# (invoice balance + payment counterpart balance = invoice residual), so the
# totals stay correct and consistent with the (now residual-based) lines.
from odoo import models
from odoo.tools import SQL


class D1FollowupReportHandler(models.AbstractModel):
    _inherit = "account.followup.report.handler"

    # #D1 Follow-up: open saldo i.p.v. oorspronkelijk bedrag (V19 backport)
    def _get_aml_value_extra_select(self):
        # Add the residual amounts to the aml value query so we can display them
        # in _get_report_line_move_line and filter on them below.
        res = list(super()._get_aml_value_extra_select())
        res.append(
            SQL(", account_move_line.amount_residual AS d1_amount_residual")
        )
        res.append(
            SQL(
                ", account_move_line.amount_residual_currency"
                " AS d1_amount_residual_currency"
            )
        )
        return res

    def _get_report_line_move_line(
        self, options, aml_query_result, partner_line_id, init_bal_by_col_group,
        level_shift=0,
    ):
        # Substitute the original amount (balance) with the open amount (residual)
        # for every amount-like column of the follow-up report.
        if "d1_amount_residual" in aml_query_result:
            aml_query_result = dict(aml_query_result)
            residual = aml_query_result["d1_amount_residual"]
            aml_query_result["amount"] = residual
            aml_query_result["balance"] = residual
            aml_query_result["amount_currency"] = aml_query_result.get(
                "d1_amount_residual_currency"
            )
        return super()._get_report_line_move_line(
            options, aml_query_result, partner_line_id, init_bal_by_col_group,
            level_shift=level_shift,
        )

    def _filter_overdue_amls_from_results(self, aml_results):
        # Drop fully reconciled lines (open amount = 0), e.g. payment counterparts.
        results = super()._filter_overdue_amls_from_results(aml_results)
        return [aml for aml in results if aml.get("d1_amount_residual")]

    def _filter_due_amls_from_results(self, aml_results):
        # Drop fully reconciled lines (open amount = 0), e.g. payment counterparts.
        results = super()._filter_due_amls_from_results(aml_results)
        return [aml for aml in results if aml.get("d1_amount_residual")]

    def _get_query_sums(self, report, options) -> SQL:
        # The report totals are a SUM(balance) over every move line up to the
        # "as of" date. In a partial-payment workflow the payment can fall
        # outside that scope (different date/account), so the total keeps
        # showing the original amount while the lines already show the residual.
        # We sum amount_residual instead: it is a point-in-time snapshot of the
        # open amount, so the total is date independent and always equals the
        # sum of the (residual-based) open lines shown above it.
        #
        # This is a copy of account.partner.ledger.report.handler._get_query_sums
        # with the "amount"/"balance" aggregates switched from balance to
        # amount_residual. Only the follow-up report is affected (prototype
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
                        SUM(%(residual_select)s)                AS amount,
                        SUM(%(residual_select)s)                AS balance,
                        BOOL_AND(account_move_line.reconciled)  AS all_reconciled,
                        MAX(account_move_line.date)             AS latest_date
                    FROM %(table_references)s
                    %(currency_table_join)s
                    WHERE %(search_condition)s
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
                # #D1 open saldo: sommeer amount_residual i.p.v. balance
                residual_select=report._currency_table_apply_rate(SQL("account_move_line.amount_residual")),
                # #D1 einde
                table_references=query.from_clause,
                currency_table_join=report._currency_table_aml_join(column_group_options),
                search_condition=query.where_clause,
                date_from=date_from,
            ))

        return SQL(" UNION ALL ").join(queries)
    # #D1 einde
