from OTCFinUtils.security import get_dataverse_token

# TODO - write basic tests

url = "https://org873d3f04.crm.dynamics.com/"
token = get_dataverse_token(url)
print(token)