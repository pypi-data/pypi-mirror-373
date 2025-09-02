from configurations import values
from wbcore.configurations import DevBaseConfiguration, ProductionBaseConfiguration


class CRMDevBaseConfiguration(DevBaseConfiguration):
    SECRET_KEY = values.Value("THIS-IS-NOT-A-SECRET-KEY", environ_prefix=None)
    DEBUG = values.BooleanValue(True, environ_prefix=None)
    DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
    DISABLE_NOTIFICATION = values.BooleanValue(False, environ_prefix=None)
    DEV_USER = values.Value(None, environ_prefix=None)
    ADD_REVERSION_ADMIN = True
    DEFAULT_CREATE_ENDPOINT_BASENAME = values.Value("wbcrm:activity-list", environ_prefix=None)


class CRMProductionBaseConfiguration(ProductionBaseConfiguration):
    pass
