import requests

def fetch_line_user_info(code: str):
    # Replace "YOUR_CHANNEL_ID" and "YOUR_CHANNEL_SECRET" with your LINE Channel ID and Channel Secret
    channel_id = "YOUR_CHANNEL_ID"
    channel_secret = "YOUR_CHANNEL_SECRET"
    redirect_uri = "YOUR_REDIRECT_URI"  # The same URI used in the LINE Login authentication request

    # Exchange the authorization code for an access token
    token_endpoint = "https://api.line.me/oauth2/v2.1/token"
    token_payload = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": channel_id,
        "client_secret": channel_secret,
        "redirect_uri": redirect_uri,
    }

    token_response = requests.post(token_endpoint, data=token_payload)
    token_data = token_response.json()

    # Use the access token to get user information
    if "access_token" in token_data:
        user_info_endpoint = "https://api.line.me/v2/profile"
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        user_info_response = requests.get(user_info_endpoint, headers=headers)
        user_info = user_info_response.json()

        return user_info
    else:
        raise HTTPException(status_code=400, detail="Failed to obtain access token")
