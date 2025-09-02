import json
import warnings
from typing import Union

import pandas as pd
from msci.sdk.calc.portfolio.utils.utility import validate_dataframe_date

from ...utils.validations import TypeValidation, StringDateFormat
import re


class ClientPortfolio:
    """
    Wrapper around the portfolio service using the same session as MOS.

    Args:
        portfolio_id (str): (optional) Identifier assigned to cash portfolio. Default value is BaseCashPortfolio.
        as_of_date (str): As of date in the YYYY-MM-DD format.
        initial_cash (float): (optional) Cash component in the portfolio in given currency.
        iso_currency (str): (optional) Currency in ISO format. Default value is USD.

    Returns:
        body (dict): Dictionary representation of ClientPortfolio.
    """

    portfolio_id = TypeValidation('portfolio_id', str)
    as_of_date = StringDateFormat('as_of_date')
    initial_cash = TypeValidation('initial_cash', [int, float])
    iso_currency = TypeValidation('iso_currency', str)

    def __init__(self, portfolio_id="BasePortfolio",
                 as_of_date=None,
                 initial_cash=0,
                 iso_currency="USD"):
        self.portfolio_id = portfolio_id
        self.as_of_date = as_of_date
        self.initial_cash = initial_cash
        self.iso_currency = iso_currency

    @property
    def body(self):
        """
        Generates the request body as dictionary based on the parameter passed.

        Returns:
            dict: Dictionary representation of the node.
        """
        body = {
            "objType": "PortfolioSearchInput",
            "identification": {
                "source": "OMPS",
                "objType": "SimpleIdentification",
                "portfolioId": self.portfolio_id,
            },
        }
        return body

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__dict__}>"


class TaxLotPortfolio(ClientPortfolio):
    """
    Upload tax lots portfolio. Inherits class ClientPortfolio.

    Args:
        portfolio_id (str): (optional) Identifier assigned to cash portfolio. Default value is BaseCashPortfolio.
        as_of_date (str): As of date in the YYYY-MM-DD format.
        asset_id (str) : Asset Id for portfolio upload like ISIN, CUSIP, TICKER.
        initial_cash (float): (optional) Cash component in the portfolio in given currency.
        iso_currency (str): (optional) Currency in ISO format. Default value is USD.
        quantity_type (str): (optional) Quantity type. Default value is NumShares.
        snapshot_type (str): (optional) Snapshot type. Default value is CLOSE.
        taxlot_file_path (str): Taxlot data in JSON format from file.
        taxlot_df (dataFrame): Taxlot data in pandas dataframe format with mandatory columns

            - asset_id: A Unique identifier from ISIN, CUSIP, TICKER.

            - 'quantity': Quantity of each asset in the portfolio.

            - 'openTradeDate': Date of the open trade.

            - 'openCostBasis': Cost basis of the open trade.

            - 'tradingRule': (Optional) Trading rule for taxlot. Default value is default.

            - 'status': (Optional) Status of the taxlot. Default value is Open.

            -'closedLotPrice': (Optional) Closing lot price of that particular asset id on the given closedTradeDate.

            -'closedTradeDate': (Optional) Date on which the trade was closed for that particular asset id.

            Example is pd.DataFrame([{"openTradeDate": "2016-12-30", "ISIN": "US02079K3059", "quantity": 1000, "openCostBasis": 792.45, "Asset Name": "ALPHABET INC", "tradingRule": "keepLot", "status": "Open","closedTradeDate": None ,"closedLotPrice": None},
            {"openTradeDate": "2016-12-30", "ISIN": "US0231351067", "quantity": 450, "openCostBasis": 749.87, "Asset Name": "AMAZON.COM INC", "tradingRule": "sellLot", "status": "Open","closedTradeDate": None ,"closedLotPrice": None},
            {"openTradeDate": "2016-12-30", "ISIN": "US30303M1027", "quantity": 900, "openCostBasis": 115.05, "Asset Name": "FACEBOOK INC", "status": "Open","closedTradeDate": None ,"closedLotPrice": None},
            "openTradeDate": "2016-12-30", "ISIN": "US64110L1061", "quantity": 300, "openCostBasis": 315.05, "Asset Name": "NETFLIX INC", "status": "Closed","closedTradeDate": "2017-01-01" ,"closedLotPrice": 300.0}])


    Returns:
        body (dict): Dictionary representation of TaxLotPortfolio.
    """

    as_of_date = StringDateFormat('as_of_date', mandatory=True)
    asset_id = TypeValidation('asset_id', str, mandatory=True)
    portfolio_id = TypeValidation('portfolio_id', str)

    def __init__(self, as_of_date,
                 asset_id,
                 portfolio_id="BasePortfolio",
                 snapshot_type="CLOSE",
                 quantity_type="NumShares",
                 initial_cash: Union[int, float] = None,
                 iso_currency="USD",
                 taxlot_file_path=None,
                 taxlot_df=None
                 ):
        super().__init__(portfolio_id, as_of_date=as_of_date, initial_cash=initial_cash, iso_currency=iso_currency)
        self.asset_id = asset_id
        self.snapshot_type = snapshot_type
        self.initial_cash = initial_cash
        self.iso_currency = iso_currency
        self.quantity_type = quantity_type
        self.taxlot_file_path = taxlot_file_path
        self.taxlot_df = taxlot_df

    def taxlots_to_shares_obj(self):
        """
        Method to create JSON objects from positions data.
        """

        asset_id = self.asset_id
        open_positions = self.positions[self.positions['status'] == 'Open']
        initial_shares = open_positions.groupby(self.asset_id).sum(numeric_only=True)
        initial_shares.reset_index(inplace=True)
        initial_shares["quantityType"] = self.quantity_type
        initial_shares["instrument"] = [
            {"primaryId": {"id": iid, "idType": asset_id}}
            for iid in initial_shares[asset_id]
        ]

        if 'closedLotPrice' in initial_shares.columns:
            initial_shares_obj = initial_shares.drop(columns=[asset_id, "openCostBasis", 'closedLotPrice']).to_dict(orient="records")
        else:
            initial_shares_obj = initial_shares.drop(
            columns=[asset_id, "openCostBasis"]
        ).to_dict(orient="records")

        # Adding initial cash component
        if self.initial_cash is not None:
            taxlot_init_cash_rec = {
                'quantity': self.initial_cash,
                'quantityType': self.quantity_type,
                'instrument': {'primaryId': {'id': self.iso_currency, 'idType': "MDSUID"}},
            }

            initial_shares_obj.append(taxlot_init_cash_rec)

        return initial_shares_obj

    def portfolio_body(self):
        """
        Method to create portfolio body for uploading to MSCI Portfolio Storage in JSON format.
        """
        initial_shares_obj = self.taxlots_to_shares_obj()
        taxlot_initial_portfolio = {
            "id": self.portfolio_id,
            "asOfDate": self.as_of_date,
            "snapshotType": self.snapshot_type,
            "baseCurrency": self.iso_currency,
            "positions": initial_shares_obj,
        }
        return taxlot_initial_portfolio

    def taxlot_body(self):
        """
        Method to create taxlot body for uploading to MSCI Portfolio Storage in JSON format.
        """
        asset_id = self.asset_id
        initial_taxlots = self.positions
        pattern = r'[^a-zA-Z0-9.]'
        initial_taxlots[asset_id] = initial_taxlots[asset_id].apply(lambda x: re.sub(pattern, '', x))
        initial_taxlots["id"] = initial_taxlots.apply(
            lambda x: [x[asset_id] + "_qty_" + x["openTradeDate"]][0], axis=1
        )

        # add a sequence number to discriminate lots opened on the same date
        initial_taxlots['lotSeq'] = initial_taxlots.groupby('id').cumcount()
        initial_taxlots['id'] = initial_taxlots['id'] + \
                                '_' + initial_taxlots['lotSeq'].apply(str)

        # Replace dots with underscores in 'id' column if they exist
        initial_taxlots['id'] = initial_taxlots['id'].apply(lambda x: x.replace('.', '_') if '.' in x else x)

        initial_taxlots["instrument"] = [
            {"primaryId": {"id": isin, "idType": asset_id}}
            for isin in initial_taxlots[asset_id]
        ]

        if any(
                (row['status'] == 'Closed' and
                 (pd.isna(row.get('closedTradeDate')) or pd.isna(row.get('closedLotPrice'))))
                for _, row in initial_taxlots.iterrows()
        ):
            raise ValueError("For 'Closed' status, 'closedTradeDate' and 'closedLotPrice' must be provided.")

        close_status_columns = ['closedTradeDate', 'closedLotPrice']
        if 'closedTradeDate' in initial_taxlots.columns:
            validate_dataframe_date(initial_taxlots, 'closedTradeDate')

        for col in close_status_columns:
            if col not in initial_taxlots.columns:
                initial_taxlots[col] = None
        initial_taxlots = initial_taxlots.where(pd.notnull(initial_taxlots), None)
        initial_taxlots['closedLotPrice'] = pd.to_numeric(initial_taxlots['closedLotPrice'], errors='coerce')

        initial_taxlots['closedLotPrice'] = initial_taxlots['closedLotPrice'].apply(
            lambda x: f"{initial_taxlots['iso_currency'].iloc[0]} {x:.2f}" if pd.notnull(x) else None
        )

        obj_columns = [
            "openTradeDate",
            "quantity",
            "quantityType",
            "status",
            "portfolioID",
            "openCostBasisPrice",
            "id",
            "instrument",
            "attributes",
            "closedTradeDate",
            "closedLotPrice",
        ]
        initial_taxlots_obj = initial_taxlots[[f for f in obj_columns]].to_dict(
            orient="records"
        )

        return initial_taxlots_obj

    def modify_portfolio(self, portfolio_id, positions):
        """
        Method to update position data provided by user by addition additional properties.
        """
        if 'status' not in positions.columns:
            positions['status'] = 'Open'
        if positions is not None:
            if not positions['status'].isin(['Open', 'Closed']).all():
                raise ValueError("All values in the 'status' column must be either 'Open' or 'Closed'.")
        positions['status'] = positions['status'].fillna('Open')
        positions['iso_currency'] = self.iso_currency
        open_positions = positions[positions['status'] == 'Open'].copy()
        closed_positions = positions[positions['status'] == 'Closed'].copy()
        # Modifying the positions df and adding columns to dataframe
        open_positions['quantityType'] = self.quantity_type
        #positions['status'] = 'Open'
        open_positions['portfolioID'] = portfolio_id
        closed_positions['portfolioID'] = portfolio_id
        open_positions['openCostBasisPrice'] = open_positions.apply(lambda x: [str(self.iso_currency) + ' ' + str(x['openCostBasis'])][0], axis=1)
        closed_positions['openCostBasisPrice'] = closed_positions.apply(lambda x: [str(self.iso_currency) + ' ' + str(x['openCostBasis'])][0], axis=1)

        if 'tradingRule' in open_positions.columns:
            open_positions['tradingRule'] = open_positions['tradingRule'].fillna('default')
            open_positions['attributes'] = open_positions.apply(
                lambda row: {'tradingRule': row['tradingRule']}, axis=1
            )
        else:
            open_positions['attributes'] = open_positions.apply(lambda row: {}, axis=1)

        positions = pd.concat([open_positions, closed_positions], ignore_index=True)
        self.positions = positions
        return positions


class CashPortfolio(ClientPortfolio):
    """
    Creates a cash portfolio for optimization. Inherits class ClientPortfolio.

    Args:
        portfolio_id (str): (optional) Identifier assigned to cash portfolio. Default value is BaseCashPortfolio.
        initial_cash (float, int): (optional) Cash value in USD. Default value is 10 million USD.

    Returns:
        body (dict): Dictionary representation of CashPortfolio.

    """

    portfolio_id = TypeValidation('portfolio_id', str)
    initial_cash = TypeValidation('initial_cash', [float, int])

    def __init__(self, portfolio_id="BaseCashPortfolio", initial_cash=10000000, iso_currency="USD"):
        super().__init__(portfolio_id)
        self.initial_cash = initial_cash
        self.iso_currency = iso_currency

    @property
    def body(self):
        """
        Generates the request body as dictionary based on the parameter passed.

        Returns:
            dict: Dictionary representation of the node.
        """
        return {
            "objType": "InlineCashPortfolio",
            "initialAmount": self.initial_cash,
            "currency": self.iso_currency,
        }


class SimplePortfolio(ClientPortfolio):
    """
    Upload simple portfolio (no taxlots). Inherits class ClientPortfolio.

    Args:
        portfolio_id (str): (optional) Identifier assigned to cash portfolio. Default value is BaseCashPortfolio.
        as_of_date (str): As of date in the YYYY-MM-DD format.
        asset_id (str) : Asset Id for portfolio upload like ISIN, CUSIP, TICKER.
        initial_cash (float): (optional) Cash component in the portfolio in given currency.
        initial_curency (str): (optional) Currency in ISO format. Default value is USD.
        assets (list): asset identifiers in the asset_id provided.
        quantities (list): asset quantities in the quantity_type provided.

            .. deprecated:: 1.8.0
                ``assets`` and ``quantities`` is deprecated. Use ``portfolio_df`` instead.

        quantity_type (str): (optional) Quantity type. Default value is NumShares.
        snapshot_type (str): (optional) Snapshot type. Default value is CLOSE.
        portfolio_file_path (str): Portfolio data in JSON format from file.
        portfolio_df (pd.DataFrame): Portfolio data in pandas dataframe format with mandatory columns

            - asset_id: A Unique identifier from ISIN, CUSIP, TICKER.

            - 'quantity': Quantity of each asset in the portfolio.

            Example is pd.DataFrame({'ISIN': ['US0231351067', 'US02079K3059'],'quantity': [100, 150]}).

    Returns:
        body (dict): Dictionary representation of SimplePortfolio.
    """
    as_of_date = StringDateFormat('as_of_date', mandatory=True)
    asset_id = TypeValidation('asset_id', str, mandatory=True)
    portfolio_id = TypeValidation('portfolio_id', str)

    def __init__(self, as_of_date,
                 asset_id,
                 portfolio_id="BasePortfolio",
                 snapshot_type="CLOSE",
                 quantity_type="NumShares",
                 initial_cash: Union[int, float] = None,
                 iso_currency: str ="USD",
                 assets: list = None,
                 quantities: list = None,
                 portfolio_file_path=None,
                 portfolio_df=None
                 ):

        super().__init__(portfolio_id, as_of_date=as_of_date, initial_cash=initial_cash, iso_currency=iso_currency)
        self.asset_id = asset_id
        self.snapshot_type = snapshot_type
        self.initial_cash = initial_cash
        self.iso_currency = iso_currency
        self.quantity_type = quantity_type

        if assets and quantities:
            warnings.warn(
                "assets and quantities is deprecated and will be removed in the next version. Kindly use portfolio_df instead.",
                DeprecationWarning)
        self.quantities = quantities
        self.assets = assets
        self.portfolio_file_path = portfolio_file_path
        self.portfolio_df = portfolio_df

    def shares_obj(self):
        """
        Method to create positions data.
        """

        positions_list = list()
        for index, row in self.portfolio_df.iterrows():
            tmp = {
                'quantity': row['quantity'],
                'quantityType': self.quantity_type,
                'instrument': {"primaryId": {"id": row[self.asset_id], "idType": self.asset_id}}
            }
            positions_list.append(tmp)

        # Adding initial cash component
        if self.initial_cash is not None:
            initial_cash_rec = {
                'quantity': self.initial_cash,
                'quantityType': self.quantity_type,
                'instrument': {'primaryId': {'id': self.iso_currency, 'idType': "MDSUID"}},
            }

            positions_list.append(initial_cash_rec)

        return positions_list

    def portfolio_body(self):
        """
        Method to create portfolio body for uploading to MSCI Portfolio Storage in JSON format.
        """
        positions_list = self.shares_obj()
        initial_portfolio = {
            "id": self.portfolio_id,
            "asOfDate": self.as_of_date,
            "snapshotType": self.snapshot_type,
            "baseCurrency": self.iso_currency,
            "positions": positions_list,
        }
        return initial_portfolio
