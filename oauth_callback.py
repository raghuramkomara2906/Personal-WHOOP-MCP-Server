from html import escape

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from whoop_mcp.oauth import (
    create_authorization_url,
    exchange_code_for_tokens,
    validate_state,
)


# --------------------------------------------------
# OAuth / Web Router
# --------------------------------------------------

router = APIRouter()


# --------------------------------------------------
# Home Page
# --------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def home():
    """
    Landing page for the Personal WHOOP MCP application.
    """

    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Personal WHOOP MCP</title>

            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 700px;
                    margin: 80px auto;
                    padding: 20px;
                    line-height: 1.6;
                }

                h1 {
                    margin-bottom: 10px;
                }

                .button {
                    display: inline-block;
                    padding: 12px 20px;
                    margin-top: 20px;
                    background: #000000;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                }

                .secondary {
                    margin-top: 20px;
                }
            </style>
        </head>

        <body>
            <h1>Personal WHOOP MCP</h1>

            <p>
                Connect your WHOOP account to securely enable
                health and fitness data access through MCP.
            </p>

            <a class="button" href="/connect">
                Connect WHOOP
            </a>

            <div class="secondary">
                <a href="/privacy">
                    Privacy Policy
                </a>
            </div>
        </body>
    </html>
    """


# --------------------------------------------------
# Start WHOOP OAuth
# --------------------------------------------------

@router.get("/connect")
async def connect_whoop():
    """
    Start the WHOOP OAuth authorization flow.

    Generates the WHOOP authorization URL and redirects
    the user to WHOOP for authentication and consent.
    """

    authorization_url, _ = create_authorization_url()

    return RedirectResponse(
        url=authorization_url,
        status_code=302,
    )


# --------------------------------------------------
# WHOOP OAuth Callback
# --------------------------------------------------

@router.get(
    "/callback",
    response_class=HTMLResponse,
)
async def oauth_callback(
    request: Request,
):
    """
    Handle the OAuth callback from WHOOP.

    WHOOP redirects the user here after authorization.

    The callback contains:
    - authorization code
    - OAuth state
    - optional OAuth error information

    The authorization code is exchanged for WHOOP
    access and refresh tokens.
    """

    code = request.query_params.get("code")
    state = request.query_params.get("state")

    error = request.query_params.get("error")

    error_description = request.query_params.get(
        "error_description"
    )

    # --------------------------------------------------
    # WHOOP returned an OAuth error
    # --------------------------------------------------

    if error:
        safe_error = escape(
            error
        )

        safe_description = escape(
            error_description
            or "No additional details provided."
        )

        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>
                        WHOOP Connection Failed
                    </title>
                </head>

                <body style="
                    font-family: Arial, sans-serif;
                    max-width: 700px;
                    margin: 80px auto;
                    padding: 20px;
                    line-height: 1.6;
                ">

                    <h1>
                        WHOOP Connection Failed
                    </h1>

                    <p>
                        WHOOP authorization was denied
                        or failed.
                    </p>

                    <p>
                        <strong>Error:</strong>
                        {safe_error}
                    </p>

                    <p>
                        <strong>Details:</strong>
                        {safe_description}
                    </p>

                    <p>
                        <a href="/connect">
                            Try Again
                        </a>
                    </p>

                </body>
            </html>
            """,
            status_code=400,
        )

    # --------------------------------------------------
    # Authorization code missing
    # --------------------------------------------------

    if not code:
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>
                        Authorization Code Missing
                    </title>
                </head>

                <body style="
                    font-family: Arial, sans-serif;
                    max-width: 700px;
                    margin: 80px auto;
                    padding: 20px;
                    line-height: 1.6;
                ">

                    <h1>
                        Authorization Code Missing
                    </h1>

                    <p>
                        WHOOP did not return an
                        authorization code.
                    </p>

                    <p>
                        Start the connection process
                        again.
                    </p>

                    <a href="/connect">
                        Connect WHOOP
                    </a>

                </body>
            </html>
            """,
            status_code=400,
        )

    # --------------------------------------------------
    # Validate OAuth state
    # --------------------------------------------------

    if not validate_state(
        state
    ):
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>
                        OAuth Validation Failed
                    </title>
                </head>

                <body style="
                    font-family: Arial, sans-serif;
                    max-width: 700px;
                    margin: 80px auto;
                    padding: 20px;
                    line-height: 1.6;
                ">

                    <h1>
                        OAuth Validation Failed
                    </h1>

                    <p>
                        The OAuth state value could
                        not be verified.
                    </p>

                    <p>
                        Please restart the WHOOP
                        connection process.
                    </p>

                    <a href="/connect">
                        Try Again
                    </a>

                </body>
            </html>
            """,
            status_code=400,
        )

    # --------------------------------------------------
    # Exchange authorization code for tokens
    # --------------------------------------------------

    try:
        tokens = await exchange_code_for_tokens(
            code
        )

    except Exception as exc:
        safe_error = escape(
            str(exc)
        )

        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>
                        Token Exchange Failed
                    </title>
                </head>

                <body style="
                    font-family: Arial, sans-serif;
                    max-width: 700px;
                    margin: 80px auto;
                    padding: 20px;
                    line-height: 1.6;
                ">

                    <h1>
                        WHOOP Connection Failed
                    </h1>

                    <p>
                        WHOOP authorization succeeded,
                        but the token exchange failed.
                    </p>

                    <p>
                        <strong>Error:</strong>
                        {safe_error}
                    </p>

                    <a href="/connect">
                        Try Again
                    </a>

                </body>
            </html>
            """,
            status_code=500,
        )

    # --------------------------------------------------
    # Successful connection
    # --------------------------------------------------

    access_token_received = bool(
        tokens.get(
            "access_token"
        )
    )

    refresh_token_received = bool(
        tokens.get(
            "refresh_token"
        )
    )

    expires_in = tokens.get(
        "expires_in"
    )

    scope = escape(
        str(
            tokens.get("scope")
            or "Not provided"
        )
    )

    return HTMLResponse(
        content=f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>
                    WHOOP Connected
                </title>
            </head>

            <body style="
                font-family: Arial, sans-serif;
                max-width: 700px;
                margin: 80px auto;
                padding: 20px;
                line-height: 1.6;
            ">

                <h1>
                    WHOOP Connected Successfully
                </h1>

                <p>
                    Your WHOOP account is now
                    connected to Personal WHOOP MCP.
                </p>

                <h3>
                    Connection Details
                </h3>

                <p>
                    Access token received:
                    <strong>
                        {access_token_received}
                    </strong>
                </p>

                <p>
                    Refresh token received:
                    <strong>
                        {refresh_token_received}
                    </strong>
                </p>

                <p>
                    Token expires in:
                    <strong>
                        {expires_in} seconds
                    </strong>
                </p>

                <p>
                    Authorized scopes:
                    <strong>
                        {scope}
                    </strong>
                </p>

                <p>
                    You can now use the
                    WHOOP MCP tools.
                </p>

                <p>
                    <a href="/">
                        Back to Home
                    </a>
                </p>

            </body>
        </html>
        """
    )


# --------------------------------------------------
# Privacy Policy
# --------------------------------------------------

@router.get(
    "/privacy",
    response_class=HTMLResponse,
)
async def privacy_policy():
    """
    Display the privacy policy required
    for the WHOOP application.
    """

    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>
                Privacy Policy - Personal WHOOP MCP
            </title>
        </head>

        <body style="
            font-family: Arial, sans-serif;
            max-width: 700px;
            margin: 80px auto;
            padding: 20px;
            line-height: 1.6;
        ">

            <h1>
                Privacy Policy
            </h1>

            <p>
                Personal WHOOP MCP is a personal
                application used to access authorized
                WHOOP health and fitness data through
                the WHOOP API.
            </p>

            <p>
                WHOOP data is used only for personal
                analytics and conversational access
                by the authorized user.
            </p>

            <p>
                The application does not sell WHOOP
                data or share it with unrelated
                third parties.
            </p>

            <p>
                Authentication is handled through
                WHOOP OAuth 2.0. The application
                does not collect or store the user's
                WHOOP password.
            </p>

            <p>
                Access and refresh tokens are used
                only to authenticate authorized
                requests to the WHOOP API.
            </p>

            <p>
                This application is intended for
                personal health and fitness analytics
                and is not a medical diagnostic
                system.
            </p>

            <p>
                <a href="/">
                    Back to Home
                </a>
            </p>

        </body>
    </html>
    """