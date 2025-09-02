import uuid

from zendo.config import appname

APP_ID = f"{appname}-{uuid.uuid4()}"
APP_MAIN_CONTENT_ID = f"{APP_ID}-current-layout"
