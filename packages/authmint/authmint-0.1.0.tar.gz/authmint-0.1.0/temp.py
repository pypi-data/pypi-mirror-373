from datetime import timedelta
from authmint.services import TokenMint
from authmint.settings import Settings
import os

os.environ["TOKEN_ACTIVE_KEY_ID"] = "2025-08-rot-1"
# os.environ["TOKEN_PRIVATE_KEY_2025-08-rot-1"] = (
#     "-----BEGIN PRIVATE KEY-----MC4CAQAwBQYDK2VwBCIEIDjncnbxpCztrW6Vmj5CqydWgCuiKRm13EPEPorLUtpW-----END PRIVATE KEY-----"
# )

# 3. Create token manager
user_mint = TokenMint(
    Settings(
        issuer="my-app",
        audience="my-client",
        purpose="access",
        expiry_duration=timedelta(minutes=5),
    )
)


token = user_mint.generate_token(
    subject_id="user-123",
    extra_claims={"role": "admin"},
)

print("JWT:", token)

# user_mint.revoke_token(token)

try:
    claims = user_mint.validate_token(token)
    print("Valid claims:", claims)
except Exception as e:
    print("Token validation failed:", e)
