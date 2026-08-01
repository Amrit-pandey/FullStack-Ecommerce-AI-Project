# Authentication Flow (Production-Level)

## Authentication Overview

This project uses **OTP-based authentication** with **JWT Access Token**, **JWT Refresh Token**, **HttpOnly Cookies**, **Redis**, and **PostgreSQL**.

Unlike traditional email/password authentication, users authenticate using a One-Time Password (OTP) sent to their email.

The backend is responsible for issuing, validating, refreshing, and invalidating authentication tokens.

---

# Authentication Architecture

```text
Client
   │
   ▼
Request OTP
   │
   ▼
Redis (Store OTP with TTL)
   │
   ▼
Email (Resend)
   │
   ▼
Verify OTP
   │
   ▼
PostgreSQL
(Check Existing User)
   │
   ▼
Create JWT Tokens
   │
   ▼
Set HttpOnly Cookies
   │
   ▼
Authenticated User
```

---

# Authentication Flow

## Step 1. Request OTP

Endpoint

```http
POST /api/v1/auth/request_otp
```

### Flow

1. User enters email.
2. Email is converted to lowercase.
3. Redis checks whether the user is under cooldown.
4. If cooldown exists, return HTTP 429.
5. Generate a secure 6-digit OTP.
6. Store OTP in Redis with a 5-minute expiration.
7. Send OTP using Resend Email API.
8. Return success response.

---

# Why Redis?

Redis is used because OTP is temporary.

Benefits:

* Extremely fast
* Built-in expiration (TTL)
* Automatically deletes expired OTPs
* No unnecessary database writes

---

# Step 2. Verify OTP

Endpoint

```http
POST /api/v1/auth/verify_otp
```

### Flow

1. User submits email and OTP.
2. Backend verifies OTP from Redis.
3. OTP is deleted immediately after successful verification.
4. Invalid or expired OTP returns HTTP 400.

---

# Step 3. Find User

Backend searches PostgreSQL.

Possible cases:

### Existing User

Load existing account.

### New User

Create new user with:

* email
* is_active=True

Commit transaction.

Set:

```text
is_new_user = true
```

---

# Step 4. User Validation

Before login, backend verifies:

* User exists
* Account is active

Inactive users receive HTTP 403.

---

# Step 5. Update Login Time

Update:

```text
last_login
```

Commit changes.

---

# Step 6. Generate Tokens

Two JWTs are created.

## Access Token

Purpose

* Access protected APIs

Contains

* sub (User ID)
* iat
* exp
* type="access"

Short expiration.

Example

30 minutes.

---

## Refresh Token

Purpose

Generate new Access Tokens.

Contains

* sub
* iat
* exp
* type="refresh"

Long expiration.

Example

7 days.

---

# Step 7. Store Tokens

Instead of returning JWTs in the response body, both tokens are stored as HttpOnly Cookies.

Cookies

* access_token
* refresh_token

Cookie configuration

* HttpOnly=True
* SameSite=Lax
* Path=/
* Max-Age configured
* Secure=True (Production)
* Secure=False (Local Development)

Why HttpOnly?

JavaScript cannot read HttpOnly cookies.

This significantly reduces XSS attack risk.

---

# Step 8. Login Response

Backend returns only:

```json
{
    "is_new_user": true
}
```

or

```json
{
    "is_new_user": false
}
```

The frontend decides what to do next.

---

# Existing User Flow

```text
Verify OTP
      │
      ▼
is_new_user = false
      │
      ▼
Call GET /me
      │
      ▼
Load User Profile
      │
      ▼
Open Dashboard
```

---

# New User Flow

```text
Verify OTP
      │
      ▼
is_new_user = true
      │
      ▼
Navigate to Onboarding
      │
      ▼
Complete Profile
      │
      ▼
Call GET /me
      │
      ▼
Open Dashboard
```

---

# Protected Routes

Protected endpoints use:

```text
CurrentUser Dependency
```

Authentication process:

1. Read access_token cookie.
2. Verify JWT signature.
3. Verify expiration.
4. Verify token type is "access".
5. Extract user id.
6. Load user from PostgreSQL.
7. Ensure account is active.
8. Return authenticated user.

If any step fails:

HTTP 401 Unauthorized

---

# GET /me

Endpoint

```http
GET /api/v1/auth/me
```

Purpose

Returns the currently authenticated user.

The frontend uses this endpoint:

* after login
* after page refresh
* after onboarding
* while restoring session

---

# Access Token Expiration

When Access Token expires:

* Browser automatically removes expired cookie.
* Protected APIs return HTTP 401.
* User is **not** logged out immediately because Refresh Token still exists.

---

# Refresh Token Flow

Endpoint

```http
POST /api/v1/auth/refresh
```

Flow

1. Read refresh_token cookie.
2. Verify JWT.
3. Ensure token type is "refresh".
4. Extract user id.
5. Load user from database.
6. Verify account is active.
7. Generate a new Access Token.
8. Replace old access_token cookie.
9. Return success.

The user remains logged in without entering OTP again.

---

# Logout

Endpoint

```http
POST /api/v1/auth/logout
```

Flow

1. Delete access_token cookie.
2. Delete refresh_token cookie.
3. Browser becomes unauthenticated.

Any protected API now returns HTTP 401.

---

# Onboarding

Endpoint

```http
POST /api/v1/user/onboarding
```

Executed only once.

Flow

1. Verify authenticated user.
2. Ensure onboarding is not already completed.
3. Save profile information.
4. Commit changes.
5. Return success message.

The frontend then calls:

```http
GET /api/v1/auth/me
```

to fetch the latest user profile.

---

# Security Features

* OTP expires automatically.
* OTP is single-use.
* OTP cooldown prevents spam.
* JWT contains expiration.
* Separate Access and Refresh Tokens.
* Token type validation.
* HttpOnly Cookies.
* Active user validation.
* Protected routes use dependency injection.
* No tokens stored in Local Storage.
* No sensitive data exposed to frontend.

---

# Complete Authentication Flow

```text
User
 │
 ▼
Request OTP
 │
 ▼
Redis (Store OTP)
 │
 ▼
Email Sent
 │
 ▼
Verify OTP
 │
 ▼
Redis Verification
 │
 ▼
PostgreSQL
 │
 ├──────── Existing User
 │              │
 │              ▼
 │         is_new_user=false
 │              │
 │              ▼
 │           GET /me
 │              │
 │              ▼
 │         Dashboard
 │
 └──────── New User
                │
                ▼
         Create User
                │
                ▼
        is_new_user=true
                │
                ▼
          Onboarding
                │
                ▼
             GET /me
                │
                ▼
           Dashboard

Every protected request

Access Cookie
      │
      ▼
Verify JWT
      │
      ▼
Load User
      │
      ▼
Return Response

Access Token Expired
      │
      ▼
POST /refresh
      │
      ▼
Verify Refresh Token
      │
      ▼
Issue New Access Token
      │
      ▼
Continue Session
```
