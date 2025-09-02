# flake8: noqa

if __import__("typing").TYPE_CHECKING:
    # import apis into api package
    from vrt_lss_agro.api.plan_api import PlanApi
    from vrt_lss_agro.api.system_api import SystemApi
    
else:
    from lazy_imports import LazyModule, as_package, load

    load(
        LazyModule(
            *as_package(__file__),
            """# import apis into api package
from vrt_lss_agro.api.plan_api import PlanApi
from vrt_lss_agro.api.system_api import SystemApi

""",
            name=__name__,
            doc=__doc__,
        )
    )
