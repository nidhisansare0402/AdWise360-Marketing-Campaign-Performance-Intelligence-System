import requests
import pandas as pd

def fetch_google_ads_stub(credentials, start_date, end_date):
    """
    Placeholder: implement OAuth2, use google-ads python client or reporting API,
    normalize JSON to DataFrame, and return a metrics DataFrame.
    """
    # pseudo
    # resp = requests.get("https://api.google.com/ads/metrics", params=..., headers=...)
    # df = pd.json_normalize(resp.json()['rows'])
    # return df
    raise NotImplementedError("This is a stub. Replace with actual API client code.")
