# flake8: noqa

if __import__("typing").TYPE_CHECKING:
    # import apis into api package
    from vrt_lss_account.api.audit_api import AuditApi
    from vrt_lss_account.api.auth_api import AuthApi
    from vrt_lss_account.api.data_api import DataApi
    from vrt_lss_account.api.info_api import InfoApi
    from vrt_lss_account.api.quota_api import QuotaApi
    from vrt_lss_account.api.statistics_api import StatisticsApi
    from vrt_lss_account.api.system_api import SystemApi
    
else:
    from lazy_imports import LazyModule, as_package, load

    load(
        LazyModule(
            *as_package(__file__),
            """# import apis into api package
from vrt_lss_account.api.audit_api import AuditApi
from vrt_lss_account.api.auth_api import AuthApi
from vrt_lss_account.api.data_api import DataApi
from vrt_lss_account.api.info_api import InfoApi
from vrt_lss_account.api.quota_api import QuotaApi
from vrt_lss_account.api.statistics_api import StatisticsApi
from vrt_lss_account.api.system_api import SystemApi

""",
            name=__name__,
            doc=__doc__,
        )
    )
