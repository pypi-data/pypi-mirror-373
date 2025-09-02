from odp.util.check_version import check_library_version

# FIXME: This is only for compatibility with pydantic and should be removed
if check_library_version("pydantic") == "1.10.20":
    from pydantic import BaseModel, Field, PrivateAttr, SecretStr
else:
    from .cheapdantic import BaseModel, Field, PrivateAttr, SecretStr
