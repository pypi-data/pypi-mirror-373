import pandas as pd


def portfolios_to_df(portfolio):
    asset_data = []
    for position in portfolio["positions"]:
        asset_data.append(
            [position["asset"]["id"], position["quantity"], position["weight"], position["asset"]["cusip"],
             position["asset"]["isin"], position["asset"]["ticker"], position["asset"]["sedol"]])
    df = pd.DataFrame(asset_data, columns=['assetId', 'Quantity', 'Weight', 'cusip', 'isin', 'ticker', 'sedol'])
    return df


def format_portfolio_output(resp, to_dataframe):
    if to_dataframe:
        return portfolios_to_df(resp.json())
    else:
        return resp.json()


def format_dates_output(resp, to_dataframe):
    if to_dataframe:
        return pd.json_normalize(resp.json())
    else:
        return resp.json()
