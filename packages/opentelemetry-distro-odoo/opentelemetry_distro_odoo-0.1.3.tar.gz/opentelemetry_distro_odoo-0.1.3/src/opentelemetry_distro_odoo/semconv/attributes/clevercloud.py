from typing import Final

CC_SCALE: Final = "cc.scale"
"""
The current Scale or the Instance.
Can be :
- nano
- XS
- S
- M
- L
- XL
- 2XL
- 3XL

Or `unknow` if this can't be determined.
"""

CC_APP_NAME: Final = "cc.app.name"
"""
The name of the app monitored. Taken from `CC_APP_NAME` environment variable.
"""

CC_APP_ID: Final = "cc.app.id"
"""
The Clevercloud Id of the application monitored. Taken from `CC_APP_ID` environment variable.
"""

CC_COMMIT: Final = "cc.commit"
"""
The full commit sha deployed
"""

CC_COMMIT_SHORT: Final = "cc.commit.short"
"""
The short 7 first char of the commit deployed
"""

CC_INSTANCE_ID: Final = "cc.instance.id"
CC_INSTANCE_NUMBER: Final = "cc.instance.number"
CC_OWNER: Final = "cc.owner"
CC_DEPLOYMENT: Final = "cc.deployment"
