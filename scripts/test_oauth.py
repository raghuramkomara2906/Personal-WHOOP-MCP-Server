from urllib.parse import urlparse, parse_qs

from whoop_mcp.oauth import create_authorization_url


url, state = create_authorization_url()

parsed = urlparse(url)
params = parse_qs(parsed.query)


print("\nWHOOP OAuth Diagnostic")
print("----------------------")

print("Authorization endpoint:")
print(f"{parsed.scheme}://{parsed.netloc}{parsed.path}")

print("\nClient ID present:")
print(bool(params.get("client_id")))

print("\nRedirect URI:")
print(params.get("redirect_uri"))

print("\nResponse type:")
print(params.get("response_type"))

print("\nScopes:")
print(params.get("scope"))

print("\nState:")
print(params.get("state"))

print("\nState length:")
print(len(state))

print("\nAuthorization URL:")
print(url)