# Personal WHOOP MCP Server

A self-hosted **Model Context Protocol (MCP) server** that connects your personal WHOOP data to ChatGPT and other MCP-compatible AI clients.

**Developer:** Raghu Ram Komara

The project uses the **WHOOP API + OAuth 2.0** to securely retrieve recovery, sleep, strain, workout, profile, and body-measurement data, then exposes that data through structured MCP tools.

> **Goal:** Turn your personal WHOOP data into reusable AI tools for natural-language health and fitness insights.

---

## What You Can Ask

Once connected, you can ask questions such as:

- How am I doing today?
- Give me my WHOOP summary for this week.
- How has my recovery changed over the last 14 days?
- How has my HRV been recently?
- How has my sleep performance changed this week?
- Summarize my recent workouts.
- Compare my latest recovery with my recent average.

The server retrieves your WHOOP data, normalizes the raw API responses, calculates useful summaries and trends, and returns structured results that ChatGPT can interpret.

---

## Architecture

```text
User
 │
 ▼
ChatGPT / MCP Client
 │
 │ Model Context Protocol
 ▼
Personal WHOOP MCP Server
 │
 ├── MCP tools
 ├── Data normalization
 ├── Trend / summary analytics
 └── Automatic token refresh
 │
 │ OAuth 2.0 + WHOOP REST API
 ▼
WHOOP
 │
 ▼
Recovery / HRV / Sleep / Strain / Workouts
```

### How the pieces work together

```text
WHOOP API
    ↓
Retrieves personal WHOOP data

OAuth 2.0
    ↓
Authorizes access to your WHOOP account

WhoopClient
    ↓
Handles API requests and token refresh

normalizers.py
    ↓
Converts raw WHOOP JSON into concise model-friendly data

analytics.py
    ↓
Calculates deterministic summaries and trends

MCP tools
    ↓
Expose useful capabilities to AI applications

ChatGPT
    ↓
Chooses the appropriate tool and explains the result
```

---

## Features

- WHOOP OAuth 2.0 authorization-code flow
- OAuth state validation
- Access-token and refresh-token handling
- Automatic token refresh
- Recovery, HRV, resting-heart-rate, sleep, strain, workout, profile, and body-measurement access
- Model-friendly data normalization
- Recovery trend analytics
- Weekly health summaries
- Daily health snapshot
- MCP Streamable HTTP transport
- FastAPI web and OAuth routes
- Dockerized setup
- ngrok HTTPS tunnel for local development
- Persistent Docker volume for OAuth tokens

---

# Quick Start

```text
Clone repository
      ↓
Create WHOOP Developer App
      ↓
Create ngrok account/domain
      ↓
Configure .env
      ↓
Run Docker Compose
      ↓
Connect WHOOP
      ↓
Add /mcp URL to ChatGPT
      ↓
Ask questions about your WHOOP data
```

---

# 1. Prerequisites

You need:

- A WHOOP account and active WHOOP membership
- A WHOOP Developer App
- Docker Desktop
- Git
- An ngrok account
- ChatGPT access that supports adding a custom MCP server

If you use the Docker setup, you do not need to install Python locally.

---

# 2. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/whoop-mcp-server.git
cd whoop-mcp-server
```

---

# 3. Create a WHOOP Developer App

Open the WHOOP Developer Platform:

**https://developer.whoop.com/**

Sign in with your WHOOP account and create a new application.

WHOOP will provide:

```text
Client ID
Client Secret
```

Keep the **Client Secret private**.

## Required WHOOP Scopes

Enable the scopes used by this project:

```text
read:profile
read:recovery
read:cycles
read:sleep
read:workout
read:body_measurement
offline
```

The `offline` scope allows the server to receive a refresh token so it can refresh expired WHOOP access tokens automatically.

You will configure the Redirect URI after creating your ngrok domain.

---

# 4. Create an ngrok Account

This repository uses ngrok during local development so ChatGPT can reach the MCP server running on your computer.

Create or sign in to an ngrok account:

**https://dashboard.ngrok.com/**

## Get Your ngrok Authtoken

From the ngrok dashboard, copy your account authtoken.

You will use it as:

```env
NGROK_AUTHTOKEN=your_ngrok_authtoken
```

Never commit the real authtoken to GitHub.

## Create or Reserve an ngrok Domain

In the ngrok dashboard, create or reserve a domain.

Example:

```text
your-personal-whoop.ngrok-free.dev
```

You will use this domain for both:

```text
WHOOP OAuth callback:
https://your-personal-whoop.ngrok-free.dev/callback
```

and:

```text
MCP endpoint:
https://your-personal-whoop.ngrok-free.dev/mcp
```

---

# 5. Register the WHOOP Redirect URI

Return to your WHOOP Developer App.

Add this Redirect URI:

```text
https://YOUR_NGROK_DOMAIN/callback
```

Example:

```text
https://your-personal-whoop.ngrok-free.dev/callback
```

The redirect URI must match your environment configuration exactly.

These are different OAuth redirect URIs:

```text
https://example.ngrok-free.dev/callback
https://example.ngrok-free.dev/callback/
http://example.ngrok-free.dev/callback
```

Use the exact HTTPS URL registered in the WHOOP Developer Dashboard.

---

# 6. Create and Configure Your `.env` File

The repository does **not** include a `.env` file because `.env` is intentionally excluded from Git so secrets are never pushed to GitHub.

After cloning the repository, create your own `.env` file in the **project root**, at the same level as `compose.yaml`, `Dockerfile`, and `app.py`.

Your project should look like this:

```text
whoop-mcp-server/
├── .env                 ← create this file
├── .env.example
├── app.py
├── compose.yaml
├── Dockerfile
├── oauth_callback.py
├── pyproject.toml
└── src/
```

The easiest way to create it is to copy the provided template:

```bash
cp .env.example .env
```

Then open `.env` in your editor and replace the placeholder values with your own WHOOP and ngrok credentials.

Use this template:

```env
# WHOOP Developer App credentials
WHOOP_CLIENT_ID=your_whoop_client_id
WHOOP_CLIENT_SECRET=your_whoop_client_secret

# Must exactly match the Redirect URI registered
# in your WHOOP Developer App
WHOOP_REDIRECT_URI=https://your-personal-whoop.ngrok-free.dev/callback

# Hostname only — do not include https://
PUBLIC_HOST=your-personal-whoop.ngrok-free.dev

# ngrok account credentials
NGROK_AUTHTOKEN=your_ngrok_authtoken

# Hostname only — do not include https://
NGROK_DOMAIN=your-personal-whoop.ngrok-free.dev
```

Example:

```env
WHOOP_CLIENT_ID=abc123-your-client-id
WHOOP_CLIENT_SECRET=your-private-client-secret
WHOOP_REDIRECT_URI=https://example-whoop.ngrok-free.dev/callback
PUBLIC_HOST=example-whoop.ngrok-free.dev
NGROK_AUTHTOKEN=your-private-ngrok-authtoken
NGROK_DOMAIN=example-whoop.ngrok-free.dev
```

Important:

- `WHOOP_REDIRECT_URI` **must include** `https://` and `/callback`.
- `PUBLIC_HOST` should contain only the hostname.
- `NGROK_DOMAIN` should contain only the hostname.
- Do not add a trailing `/` to the domain values.
- Never commit `.env` to GitHub.
- Never share your WHOOP Client Secret, WHOOP access/refresh tokens, or ngrok authtoken.

For example, use:

```env
PUBLIC_HOST=your-personal-whoop.ngrok-free.dev
NGROK_DOMAIN=your-personal-whoop.ngrok-free.dev
```

not:

```env
PUBLIC_HOST=https://your-personal-whoop.ngrok-free.dev
NGROK_DOMAIN=https://your-personal-whoop.ngrok-free.dev/
```

You can confirm Git is ignoring your `.env` file with:

```bash
git check-ignore .env
```

Expected output:

```text
.env
```

---

# 7. Run the Project with Docker

Make sure Docker Desktop is running.

Build and start the application:

```bash
docker compose up -d --build
```

Docker Compose starts two services:

```text
personal-whoop-mcp
    └── FastAPI + MCP server

personal-whoop-ngrok
    └── HTTPS tunnel to the MCP server
```

Check the services:

```bash
docker compose ps
```

You should eventually see both containers running, with the application container reporting healthy.

Example:

```text
personal-whoop-mcp      Up (healthy)
personal-whoop-ngrok    Up
```

---

# 8. Check the Logs

Application logs:

```bash
docker compose logs app
```

ngrok logs:

```bash
docker compose logs ngrok
```

Follow all logs live:

```bash
docker compose logs -f
```

---

# 9. Open the Personal WHOOP MCP Home Page

Open:

```text
https://YOUR_NGROK_DOMAIN/
```

You should see the Personal WHOOP MCP landing page with:

```text
Connect WHOOP
Privacy Policy
```

---

# 10. Connect Your WHOOP Account

Open:

```text
https://YOUR_NGROK_DOMAIN/connect
```

The authorization flow is:

```text
/connect
   ↓
WHOOP login
   ↓
WHOOP permissions screen
   ↓
User approves access
   ↓
/callback
   ↓
Authorization code exchanged for tokens
   ↓
WHOOP connection complete
```

After a successful connection, you should see:

```text
WHOOP Connected Successfully
```

with confirmation that an access token and refresh token were received.

The actual token values are not displayed.

---

# 11. MCP Server URL

Once the server is running, your MCP endpoint is:

```text
https://YOUR_NGROK_DOMAIN/mcp
```

This is the URL you provide to MCP-compatible clients.

---

# 12. Optional: Test with MCP Inspector

Before connecting ChatGPT, you can validate the server with MCP Inspector.

Run:

```bash
npx @modelcontextprotocol/inspector@latest
```

In the Inspector:

```text
Transport: Streamable HTTP
```

Server URL:

```text
https://YOUR_NGROK_DOMAIN/mcp
```

Connect and use **List Tools**.

You should see tools similar to:

```text
whoop_server_status
get_my_whoop_profile
get_my_whoop_recovery
get_my_whoop_sleep
get_my_whoop_cycles
get_my_whoop_workouts
get_my_whoop_body_measurements
get_today_health_snapshot
get_weekly_health_summary
get_recovery_trend
```

---

# 12. Add the MCP Server to ChatGPT

In ChatGPT on the web:

1. Open **Plugins**.
2. Select the **+** button.
3. Choose **Add custom MCP server**.
4. Enter a name such as `Personal WHOOP MCP`.
5. For the Server URL, enter:

   ```text
   https://YOUR_NGROK_DOMAIN/mcp
   ```

6. Select:

   ```text
   Authentication: No authentication
   ```

7. Review the connection warning.
8. Select **Create as a plugin**.
9. Install the newly created personal plugin.
10. Open a supported ChatGPT conversation/workflow and select the plugin when you want to use your WHOOP tools.

## Why "No authentication"?

This project already uses WHOOP OAuth between your MCP server and WHOOP:

```text
ChatGPT
   │
   │ MCP
   ▼
Personal WHOOP MCP
   │
   │ WHOOP OAuth 2.0
   ▼
WHOOP
```

The current version does not implement a separate OAuth layer between ChatGPT and the `/mcp` endpoint.

This repository is therefore intended for **personal, single-user, self-hosted use**.

---

# 13. Example Prompts

```text
How am I doing today?
```

```text
Give me my WHOOP summary for this week.
```

```text
How has my recovery changed over the last 14 days?
```

```text
How has my HRV been recently?
```

```text
How has my sleep performance been this week?
```

```text
Summarize my recent training load.
```

```text
Show me my recent workouts.
```

```text
Compare my latest recovery with my recent average.
```

---

# Available MCP Tools

| Tool | Purpose |
|---|---|
| `whoop_server_status` | Check whether the MCP server and WHOOP connection are available |
| `get_my_whoop_profile` | Retrieve basic WHOOP profile information |
| `get_my_whoop_recovery` | Retrieve recent recovery, HRV, RHR, and related recovery metrics |
| `get_my_whoop_sleep` | Retrieve recent sleep metrics |
| `get_my_whoop_cycles` | Retrieve daily strain / physiological cycle data |
| `get_my_whoop_workouts` | Retrieve recent workout activity |
| `get_my_whoop_body_measurements` | Retrieve available body measurements |
| `get_today_health_snapshot` | Get a concise current WHOOP snapshot |
| `get_weekly_health_summary` | Generate a deterministic 7-day health and training summary |
| `get_recovery_trend` | Analyze recovery trends over a selected period |

---

# How the Data Is Processed

```text
WHOOP API
   ↓
Raw JSON
   ↓
normalizers.py
   ↓
Clean model-friendly records
   ↓
analytics.py
   ↓
Deterministic summaries / trends
   ↓
MCP tools
   ↓
ChatGPT interpretation
```

Calculations such as averages and trend summaries are performed in Python rather than asking the language model to calculate everything from raw data.

---

# Automatic Token Refresh

WHOOP access tokens expire.

If WHOOP returns an authentication failure because the access token has expired, the server automatically:

```text
Detects expired access token
        ↓
Uses refresh token
        ↓
Requests new WHOOP tokens
        ↓
Stores latest access + refresh token
        ↓
Retries the original API request
```

The `offline` WHOOP scope is required for this flow.

---

# Project Structure

```text
whoop-mcp-server/
├── app.py
├── oauth_callback.py
├── Dockerfile
├── compose.yaml
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── .dockerignore
│
├── src/
│   └── whoop_mcp/
│       ├── __init__.py
│       ├── config.py
│       ├── oauth.py
│       ├── whoop_client.py
│       ├── normalizers.py
│       ├── analytics.py
│       ├── exceptions.py
│       └── server.py
│
└── tests/
    ├── test_analytics.py
    └── test_whoop.py
```

---

# Security

This project handles personal health and fitness data.

Do not commit or publish:

```text
.env
.data/
WHOOP_CLIENT_SECRET
WHOOP access tokens
WHOOP refresh tokens
NGROK_AUTHTOKEN
```

The repository should include these entries in `.gitignore`:

```gitignore
.env
.data/
.venv/
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
.DS_Store
```

The current implementation is designed for:

> **One user, one WHOOP account, one self-hosted MCP instance.**

Do not expose the current unauthenticated `/mcp` endpoint as a permanent public multi-user service.

For a production or multi-user version, add MCP-layer authentication, per-user identity, encrypted token storage, and a database-backed credential store.

---

# Disclaimer

This project is intended for personal health/fitness analytics, software-development education, and experimentation with MCP.

It is **not a medical diagnostic system** and should not be used as a substitute for professional medical advice, diagnosis, or treatment.

---

# References

- WHOOP Developer Platform: https://developer.whoop.com/
- WHOOP OAuth Documentation: https://developer.whoop.com/docs/developing/oauth/
- ngrok Dashboard: https://dashboard.ngrok.com/
- ngrok Documentation: https://ngrok.com/docs/
- OpenAI Custom MCP Server Guide: https://developers.openai.com/api/docs/guides/custom-mcp-server
- Model Context Protocol: https://modelcontextprotocol.io/

---

# Developer

**Raghu Ram Komara**

## Built With

- Python
- Model Context Protocol (MCP)
- FastAPI
- httpx
- OAuth 2.0
- WHOOP API
- Docker
- Docker Compose
- ngrok

---

## Project Goal

The purpose of this project is not to replace WHOOP's native experience.

It demonstrates how personal data from an external platform can be exposed as **structured, reusable AI capabilities** through MCP.

> **WHOOP is the data source. OAuth secures access. Python retrieves and analyzes the data. MCP exposes the capabilities. ChatGPT interprets the results.**
