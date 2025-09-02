QA_TOKEN_URL = "https://accounts-qa1.msci.com/oauth/token"
OMPS_AUDIENCE = "https://portfoliostore/api"
OMPS_FILE_PREFIX = "omps"
MOS_DEFAULT_VERSION = "1.4"
MOS_VERSIONS_SUPPORTED = ["1.4"]
ALLOWED_ASSET_TYPES = ['ISIN', 'CUSIP', 'MDSUID', 'TICKER', 'SEDOL']

SDK_DIR = "msci_sdk"
TOKEN_FILE_NAME = "token.txt"

# QA environment details
PCS_QA = {
    # internal
    # "pcs_host": "qa-mos-otw.msciapps.com",
    # external
    "pcs_base_url": "https://test-api2.msci.com/analytics/optimization",
    "pcs_audience": "pcs-qa",
    "pcs_token_url": QA_TOKEN_URL
}

# UAT environment details
PCS_UAT = {
    "pcs_base_url": "https://uat-api2.msci.com/analytics/optimization",
    "pcs_audience": "https://pcs-uat",
    "pcs_token_url": "https://accounts-uat1.msci.com/oauth/token"
}

# DEV environment details
PCS_DEV = {
    "pcs_base_url": "https://dev-mos-otw.msciapps.com/analytics/optimization",
    "pcs_audience": "pcs-qa",
    "pcs_token_url": QA_TOKEN_URL
}

# PROD environment details
PCS_PROD = {
    "pcs_base_url": "https://api2.msci.com/analytics/optimization",
    "pcs_audience": "https://pcs",
    "pcs_token_url": "https://accounts.msci.com/oauth/token"
}

# OMPS service
OMPS_QA = {
    # internal
    # "omps_base_url": "https://omps.portfolio-store-qa.k8s.msciapps.com/portfolio-service/api/v3.0",
    # external
    "omps_base_url": "https://test-api2.msci.com/analytics/portfolio-service/v3.0",
    "omps_token_url": QA_TOKEN_URL,
    "omps_audience": OMPS_AUDIENCE}

OMPS_UAT = {
    "omps_base_url": "https://uat-api2.msci.com/analytics/portfolio-service/v3.0",
    "omps_token_url": "https://accounts-uat1.msci.com/oauth/token",
    "omps_audience": OMPS_AUDIENCE}

OMPS_DEV = {
    "omps_base_url": "https://test-api2.msci.com/analytics/portfolio-service/v3.0",
    "omps_token_url": QA_TOKEN_URL,
    "omps_audience": OMPS_AUDIENCE}

OMPS_PROD = {
    "omps_base_url": "https://api2.msci.com/analytics/portfolio-service/v3.0",
    "omps_token_url": "https://accounts.msci.com/oauth/token",
    "omps_audience": OMPS_AUDIENCE}

# Messages
NO_PREVIOUS_JOB_MESSAGE = 'No previous job available'
NO_TAX_OUTPUT_MESSAGE = 'No Tax Output to display'

# Error
PORTFOLIO_ID_AS_OF_DATE_ERROR = 'portfolio_id and as_of_date must be provided!'
ASSET_DETAILS_MULTI_ACCOUNT_ERROR = 'Metric subtype ASSET_DETAILS not supported for Multi-account optimization'
