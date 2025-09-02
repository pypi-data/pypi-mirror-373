import json
import pandas as pd


class TaxOutput:
    def __init__(self, job, just_summary=False):
        """
        Tax optimisation results like trade suggestions, tax by category, returns , risk.
        """
        if just_summary:
            self.portfolio_df = []
            self.df_trades = []

        else:
            dates = job.close_portfolio_dates(to_dataframe=False)
            my_date = dates[-1]["rebalanceDate"]
            final_portfolio = job.close_portfolio_on(my_date,to_dataframe=False)
            portfolio_df = pd.DataFrame(pd.json_normalize(final_portfolio["positions"]))
            self.portfolio_df = portfolio_df

            job_id = job.job_id
            get_trades_response = job.get(f"jobs/tradeSuggestions/{job_id}/{my_date}")

            df_trades = pd.json_normalize(get_trades_response.json()["suggestions"])
            self.df_trades = df_trades

        metric_type = "OPTIMIZER_RESULT"
        metric_sub_type = "PORTFOLIO_SUMMARY"

        job_id = job.job_id
        get_metrics_response = job.get(
            f"jobs/{job_id}/metrics/{metric_type}?subType={metric_sub_type}"
        )
        opt_summary_json = get_metrics_response.json()['values'][0]

        opt_summary_many = [json.loads(x['PORTFOLIO_SUMMARY']) for x in opt_summary_json['values']]

        rebal_dates = opt_summary_json['dataDates']
        opt_dict = [x['optimalPortfolio'][0] for x in opt_summary_many]
        df_metrics = pd.json_normalize(opt_dict)
        df_metrics.index = rebal_dates

        self.df_metrics = df_metrics

        if 'portfolioTax.taxByGroup' in df_metrics:
            tax_by_category = [x[0]['taxByCategory'] for x in df_metrics['portfolioTax.taxByGroup']]
            tax_by_dict = [{v["taxCategory"]: v for v in x} for x in tax_by_category]
            tax_summary = [{
                "Long-term gain": x["LONG_TERM"]["gain"],
                "Long-term loss": x["LONG_TERM"]["loss"],
                "Long-term net": x["LONG_TERM"]["net"],
                "Short-term gain": x["SHORT_TERM"]["gain"],
                "Short-term loss": x["SHORT_TERM"]["loss"],
                "Short-term net": x["SHORT_TERM"]["net"],
                "Tax free gain": x["TAX_FREE"]["gain"],
                "Tax free loss": x["TAX_FREE"]["loss"],
                "Tax free net": x["TAX_FREE"]["net"],
                "Long-term tax": x["LONG_TERM"]["tax"],
                "Short-term tax": x["SHORT_TERM"]["tax"],
                "Total tax": x["LONG_TERM"]["tax"]
                             + x["SHORT_TERM"]["tax"],
            } for x in tax_by_dict]
        else:
            tax_summary = {}

        if job.profile:
            profile_id = job.profile.profile_id
            portfolio_name = job.profile.strategy.ref_universe.portfolio.portfolio_id
            benchmark_name = job.profile.strategy.ref_universe.benchmark_ref_name
        else:
            profile_id = 'Unknown'
            portfolio_name = 'Unknown'
            benchmark_name = 'Unknown'

        simple_metrics = df_metrics[["return", "totalRisk", "turnover", "beta"]]  # need to add number of assets
        new = pd.DataFrame({'Profile Id': profile_id, 'Portfolio Name': portfolio_name, 'Benchmark Name': benchmark_name}, index=simple_metrics.index)
        simple_metrics = simple_metrics.join(new)

        if tax_summary:
            simple_metrics = simple_metrics.join(pd.DataFrame(tax_summary, index=simple_metrics.index))

        self.port_summary = simple_metrics
        self.opt_detail = df_metrics

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__dict__}>"
