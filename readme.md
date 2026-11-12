# Licensed Consumer API Client (Python)

A **sample Python implementation** of a client for the **Licensed Consumer API**. It shows how to authenticate requests using HMAC-SHA256 request signing, then call the `getLatestSIFNavEntries` endpoint and parse the NAV (Net Asset Value) response.

> ⚠️ **For licensed clients only.** Access to the Licensed Consumer API — and to the credentials this client uses — is granted only to paying customers under a separate service agreement. This code is provided to licensed clients as a reference integration and is **not** open source. See [Access & Licensing](#access--licensing).
>
> ⚠️ **This is a reference / sample implementation.** It is deliberately small and dependency-light so you can read and adapt it, not a production-hardened SDK. See [Limitations & Known Issues](#limitations--known-issues) before using it in production.

---

## Table of Contents

- [Overview](#overview)
- [Access & Licensing](#access--licensing)
- [Sample Implementation Notice](#sample-implementation-notice)
- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [How Authentication Works](#how-authentication-works)
- [API Reference](#api-reference)
  - [`APIConfig`](#apiconfig)
  - [`HMACAuthenticator`](#hmacauthenticator)
  - [`LicensedAPIClient`](#licensedapiclient)
- [Response Format](#response-format)
  - [Response Schema](#response-schema)
  - [Field Reference](#field-reference)
  - [Parsing the Response](#parsing-the-response)
- [Security Notes](#security-notes)
- [Limitations & Known Issues](#limitations--known-issues)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Overview

The Licensed Consumer API requires every request to be signed. This sample project demonstrates how to:

1. Build a canonical message from the HTTP method, path, query string, and body hash.
2. Sign that message with HMAC-SHA256 using your API secret.
3. Send the base64-encoded signature in the `X-API-SIGNATURE` header alongside your `X-API-KEY`.
4. Parse the JSON response containing SIF NAV entries.

The signing pattern mirrors the common "AWS Signature v4"-style HMAC approach, adapted for this API.

---

## Access & Licensing

**This client and the API it calls are available to paying clients only.**

- **API access is not public.** `api_key` / `api_secret` credentials are issued per subscription, are tied to your account, and are not transferable.
- **This code is provided for use by licensed clients only.** It is supplied as a reference integration under the terms of your service agreement. It is **not** open source and is **not** distributed under a permissive license.
- **Do not redistribute.** Do not publish this code, your credentials, or any part of the API's responses publicly without written permission.
- **Do not share credentials.** Your `api_secret` identifies your subscription and is billed to it. Leaked keys must be rotated immediately — see [Security Notes](#security-notes).

For access, pricing, or to report a leaked credential, contact your account representative.

---

## Sample Implementation Notice

**This repository is a sample implementation written in Python.**

- It is intended as a **reference for integrating** with the Licensed Consumer API, not as a drop-in production library.
- It implements **one endpoint** (`getLatestSIFNavEntries`) and **one request pattern** (an empty-body `POST`).
- It intentionally omits production concerns such as retries, timeouts, structured logging, and secrets management. See [Limitations & Known Issues](#limitations--known-issues).
- The signing logic is written generically, so you can port it to other endpoints or languages with minimal changes.

If you are implementing this in another language, the key details to reproduce are the **canonical message format** and the **header names** described in [How Authentication Works](#how-authentication-works).

---

## Features

- 🔐 HMAC-SHA256 request signing
- 🧩 Pluggable canonical message format (`METHOD\nPATH\nQUERY\nSHA256(body)`)
- 📦 Base64-encoded signature output
- 🧪 Minimal footprint — only `requests` plus the Python standard library
- 🔄 Reusable signing logic for any endpoint, not just the licensed one
- 📊 Documented response schema for the SIF NAV payload

---

## Project Structure

```
.
├── api_client.py     # LicensedAPIClient — builds and sends signed POST requests
├── authenticator.py  # HMACAuthenticator — generates the request signature
├── config.py         # APIConfig — holds base URL, API key, and API secret
└── main.py           # Entry point / usage example
```

---

## Requirements

- **Python 3.8 or newer**
- **`requests`** — the only third-party dependency

Everything else (`hashlib`, `hmac`, `base64`, `urllib.parse`) comes from the Python standard library.

Verify your interpreter:

```bash
python --version        # or: python3 --version
```

---

## Installation

This is a small sample project — no package to install, no build step.

### 1. Get the files

Place the four modules (`api_client.py`, `authenticator.py`, `config.py`, `main.py`) in a single folder. Clone the repository if you have access to it, or copy the files in directly.

### 2. (Recommended) create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows
```

### 3. Install the single dependency

```bash
pip install requests
```

Optionally pin it so the sample stays reproducible — create a `requirements.txt`:

```txt
requests>=2.31,<3
```

Then:

```bash
pip install -r requirements.txt
```

### 4. Sanity check

From the project directory:

```bash
python -c "import requests; print(requests.__version__)"
```

If that prints a version, you're ready to move on to [Configuration](#configuration) and [Usage](#usage).

---

## Configuration

Credentials live in the `APIConfig` object.

```python
from config import APIConfig

config = APIConfig(
    base_url="https://api.example.com",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
)
```

| Parameter    | Type  | Description                                                                 |
| ------------ | ----- | --------------------------------------------------------------------------- |
| `base_url`   | `str` | Base host of the API. Trailing slashes are stripped automatically.          |
| `api_key`    | `str` | Public identifier sent in the `X-API-KEY` header.                           |
| `api_secret` | `str` | Secret used to HMAC-sign requests. **Never commit this to source control.** |

`config.endpoint` resolves to:

```
{base_url}/api/licensed-consumer/getLatestSIFNavEntries
```

---

## Usage

```python
from config import APIConfig
from api_client import LicensedAPIClient

config = APIConfig(
    base_url="https://api.example.com",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
)

client = LicensedAPIClient(config)
response = client.post(config.endpoint)

print("HTTP Status:", response.status_code)
print("Response:", response.text)
```

Run the bundled example:

```bash
python main.py
```

> **Note:** `main.py` ships with `xxxxxx` placeholders. Replace them with real credentials before running.

---

## How Authentication Works

Every request generates a fresh signature:

### 1. Compute the body hash

```
body_hash = SHA256(body).hexdigest()
```

For the current implementation, `body = b""`, so the body hash is the SHA-256 of an empty byte string:

```
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

### 2. Build the canonical message

```
METHOD \n PATH \n QUERY_STRING \n BODY_HASH
```

Example:

```
POST
/api/licensed-consumer/getLatestSIFNavEntries

e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

### 3. Sign with HMAC-SHA256

```
signature = HMAC-SHA256(key=api_secret, msg=canonical_message)
```

### 4. Base64-encode the digest

```
X-API-SIGNATURE: base64(signature)
```

### 5. Send the request

```
X-API-KEY: <your API key>
X-API-SIGNATURE: <base64 signature>
Content-Type: application/json   # when you start sending a body
```

The **path and query string are extracted from the full URL** using `urllib.parse.urlsplit`, so you can pass the full endpoint URL to `post()`.

> ⚠️ **Important:** The canonical message must match exactly what the server expects — same order, same separators, same casing. Any mismatch (e.g., reordering query params, changing the body after signing) will invalidate the signature.

---

## API Reference

### `APIConfig`

```python
APIConfig(base_url: str, api_key: str, api_secret: str)
```

- `base_url` — trailing `/` is stripped.
- `.endpoint` — read-only property returning the full licensed endpoint URL.

---

### `HMACAuthenticator`

```python
HMACAuthenticator.generate_signature(
    api_secret: str,
    method: str,
    path: str,
    query_string: str,
    body: bytes,
) -> str
```

Static method. Returns the base64-encoded HMAC-SHA256 signature.

---

### `LicensedAPIClient`

```python
LicensedAPIClient(config: APIConfig)
```

#### `post(endpoint: str) -> requests.Response`

- Parses `endpoint` to extract `path` and `query`.
- Signs the request with an empty body.
- Sends the signed `POST` and returns the raw `requests.Response`.

You are responsible for calling `.status_code`, `.json()`, or `.text` on the result.

---

## Response Format

A successful call to `getLatestSIFNavEntries` returns a JSON object with a single top-level key, `data`, whose value is a **list of NAV entries** — one per scheme.

### Example Response

```json
{
  "data": [
    {
      "net-asset-value": 11.1816,
      "isin-growth": "INF754K30094",
      "scheme-code": "SIF-120",
      "scheme-name": "Altiva Equity Ex- Top 100 Long - Short Fund",
      "isin-div-reinvestment": "-",
      "scheme-type": "Open Ended Schemes(Equity Oriented Investment Strategies - Equity Ex-Top 100 Long-Short Fund)",
      "fund-house": "Altiva SIF",
      "plan": "Direct Plan",
      "option": "Growth",
      "date-entry": "11-Aug-2026"
    },
    {
      "net-asset-value": 10.0102,
      "isin-growth": "-",
      "scheme-code": "SIF-25",
      "scheme-name": "qsif Equity Ex-Top 100 Long-Short Fund",
      "isin-div-reinvestment": "INF000K30021",
      "scheme-type": "Open Ended Schemes(Equity Oriented Investment Strategies - Equity Ex-Top 100 Long-Short Fund)",
      "fund-house": "qsif SIF",
      "plan": "Regular Plan",
      "option": "IDCW",
      "date-entry": "13-Nov-2025"
    }
  ]
}
```

### Response Schema

```
{
  "data": [                       // array of NAV entry objects
    {
      "net-asset-value":        number,   // NAV per unit, e.g. 11.1816
      "isin-growth":            string,   // ISIN for the growth option, or "-"
      "scheme-code":            string,   // internal scheme identifier, e.g. "SIF-120"
      "scheme-name":            string,   // human-readable scheme name
      "isin-div-reinvestment":  string,   // ISIN for the dividend reinvestment option, or "-"
      "scheme-type":            string,   // category / description of the scheme
      "fund-house":             string,   // asset management company / fund house
      "date-entry":             string    // date in "DD-Mon-YYYY" format, e.g. "11-Aug-2026"
      "plan":                   string    // human-readable scheme plan
      "option":                 string    // human-readable scheme option
    },
    ...
  ]
}
```

### Field Reference

| Field                   | Type     | Description                                                                                  |
| ----------------------- | -------- | -------------------------------------------------------------------------------------------- |
| `net-asset-value`       | `float`  | The Net Asset Value per unit for the scheme on the given date.                               |
| `isin-growth`           | `string` | ISIN of the **growth** option. `"-"` indicates the option is not available / not applicable. |
| `scheme-code`           | `string` | Internal scheme code assigned by the API (e.g. `SIF-120`). Useful as a stable identifier.    |
| `scheme-name`           | `string` | Display name of the scheme.                                                                  |
| `isin-div-reinvestment` | `string` | ISIN of the **dividend reinvestment** option. `"-"` when not available.                      |
| `scheme-type`           | `string` | Full category description of the scheme.                                                     |
| `fund-house`            | `string` | Name of the fund house / asset management company that manages the scheme.                   |
| `date-entry`            | `string` | Date of the NAV entry, formatted as `DD-Mon-YYYY` (e.g. `13-Nov-2025`). Parse accordingly.   |

**Notes on the payload:**

- All keys are **kebab-case** (`net-asset-value`, `date-entry`, …). Access them as dictionary keys, not Python attribute names.
- **`"-"` is used as a null / empty marker** for ISIN fields. Treat it as "not available" rather than a real value.
- **`date-entry` is a locale-style string**, not ISO 8601. If you need a `datetime`, parse with `datetime.strptime(value, "%d-%b-%Y")`.
- Numeric values such as `net-asset-value` are floats — round them explicitly if you need fixed precision for display.

### Parsing the Response

```python
from datetime import datetime

response = client.post(config.endpoint)
response.raise_for_status()

payload = response.json()
entries = payload.get("data", [])

if not isinstance(entries, list):
    raise ValueError(f"Unexpected response shape: {type(entries).__name__}")

for entry in entries:
    nav = entry.get("net-asset-value")
    isin_growth = entry.get("isin-growth")
    if isin_growth == "-":
        isin_growth = None  # normalize the "-" marker

    entry_date = datetime.strptime(entry["date-entry"], "%d-%b-%Y").date()

    print(
        f"{entry['scheme-code']:<10} "
        f"{entry['scheme-name']:<55} "
        f"NAV={nav} "
        f"ISIN={isin_growth} "
        f"Date={entry_date}"
    )
```

---

## Security Notes

- 🪪 **Your credentials are your subscription.** `api_key` / `api_secret` are issued to you or your organization, are billed to that account, and must not be shared outside it.
- 🔒 **Never hard-code `api_secret`** in source files or commit it to Git. Use environment variables, a secrets manager, or a `.env` file (excluded via `.gitignore`).
- 🔁 **Rotate secrets** immediately if they are ever exposed, and notify your account representative.
- 🧾 **Sign exactly what you send** — sign the final body, not a pre-serialized draft.
- 🕒 **Add a timestamp / nonce** if the API supports it, to prevent replay attacks (not currently implemented).
- 🧪 **Verify signatures on the server** with a constant-time comparison (e.g., `hmac.compare_digest`).

---

## Limitations & Known Issues

This is a **minimal sample implementation**. Before production use, consider addressing:

| Issue                 | Description                                                                               |
| --------------------- | ----------------------------------------------------------------------------------------- |
| Empty body only       | `post()` hard-codes `body = b""`. It cannot send a payload yet.                           |
| No JSON support       | No `json=` parameter and no `Content-Type` header.                                        |
| No timeout            | `requests.post` is called without a `timeout`. A hung connection will block indefinitely. |
| No retries            | Transient failures aren't retried.                                                        |
| No error handling     | Non-2xx responses are returned unchecked; callers must validate.                          |
| No logging            | Useful for debugging signature mismatches.                                                |
| Hard-coded endpoint   | Only supports the licensed endpoint via `config.endpoint`.                                |
| No replay protection  | No timestamp/nonce included in the canonical message.                                     |
| Secrets in `main.py`  | Placeholders are fine, but the pattern shouldn't be copied with real secrets.             |
| Fragile field parsing | Response keys use `-` and `"-"` sentinels; any downstream code must handle both.          |

**Suggested next steps:**

1. Accept a `body` / `json` argument in `post()`.
2. Add `timeout=30` to `requests.post`.
3. Wrap calls with `response.raise_for_status()` or explicit status handling.
4. Load credentials from environment variables:

   ```python
   import os
   config = APIConfig(
       base_url=os.environ["API_BASE_URL"],
       api_key=os.environ["API_KEY"],
       api_secret=os.environ["API_SECRET"],
   )
   ```

5. Add a thin typed model (e.g. a `NamedTuple` or `dataclass`) around each response entry to normalize `"-"` → `None` and parse `date-entry` once.

---

## Troubleshooting

| Symptom                               | Likely cause                                      | Fix                                                                                                   |
| ------------------------------------- | ------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `401 Unauthorized`                    | Wrong API key or secret                           | Double-check credentials.                                                                             |
| `403 Forbidden` / signature mismatch  | Canonical message differs from server expectation | Ensure `method`, `path`, `query`, and `body_hash` match exactly. Don't mutate the body after signing. |
| Signature valid locally but rejected  | URL-encoding or query ordering differs            | Pass the URL through `urlsplit` exactly as sent, and preserve query order.                            |
| `requests.exceptions.ConnectionError` | DNS / network / TLS issue                         | Verify `base_url` and connectivity.                                                                   |
| Request hangs                         | No timeout set                                    | Add `timeout=` to `requests.post`.                                                                    |
| `ModuleNotFoundError: requests`       | Dependency not installed                          | `pip install requests`.                                                                               |
| `KeyError: 'date-entry'`              | Response shape changed or entry is malformed      | Use `.get()` and validate the payload before iterating.                                               |
| `ValueError` from `strptime`          | `date-entry` isn't `DD-Mon-YYYY`                  | Inspect the raw value; fall back to returning the string as-is.                                       |

---

## License

**Proprietary — for licensed clients only.**

This software and its documentation are provided to paying customers of the Licensed Consumer API solely for the purpose of integrating with the API, under the terms of their service agreement. No open-source license is granted. Copying, modifying, distributing, sublicensing, or publishing this code — in whole or in part — is permitted only as expressly allowed by that agreement.

Use of the API and all data returned by it remain subject to the same service agreement.
