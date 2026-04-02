from datetime import datetime

users: dict[str, dict[str, str]] = {
    "admin@example.com": {
        "id": "00000000-0000-0000-0000-000000000001",
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": "$2b$12$MU/CqldVmT6vws7eh3zxKOpQkDsaT.XBe8ezmuU0qggATNe18O7uG",
        # password: Admin1!pass
    },
    "alice@example.com": {
        "id": "00000000-0000-0000-0000-000000000002",
        "username": "alice",
        "email": "alice@example.com",
        "hashed_password": "$2b$12$33NAdH2zh3/.aOi8FCrKZ.LJubkqOjZvUsTeQx5smRn8EKn0SIR8u",
        # password: User1!pass
    },
    "guest@example.com": {
        "id": "00000000-0000-0000-0000-000000000003",
        "username": "guest_user",
        "email": "guest@example.com",
        "hashed_password": "$2b$12$j8.mhjL/2at10uB1y/XiF.b.m41iu4FySzgdAru3zdX012XWGv5R6",
        # password: Guest1!pass
    },
}
# Maps email -> user record

refresh_tokens: dict[str, str] = {}
# Maps jti -> user_id (allowlist of valid refresh tokens)

brute_force: dict[str, dict[str, int | datetime | None]] = {}
# Tracks failed login attempts per IP address:
# {
#   "192.168.1.1": {
#     "failed_attempts": 3,
#     "locked_until": None  # or a datetime
#   }
# }
