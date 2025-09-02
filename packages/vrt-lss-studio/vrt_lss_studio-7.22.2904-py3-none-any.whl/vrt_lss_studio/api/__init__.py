# flake8: noqa

if __import__("typing").TYPE_CHECKING:
    # import apis into api package
    from vrt_lss_studio.api.backups_api import BackupsApi
    from vrt_lss_studio.api.custom_fields_api import CustomFieldsApi
    from vrt_lss_studio.api.custom_icons_api import CustomIconsApi
    from vrt_lss_studio.api.experiments_api import ExperimentsApi
    from vrt_lss_studio.api.explorer_api import ExplorerApi
    from vrt_lss_studio.api.external_routing_api import ExternalRoutingApi
    from vrt_lss_studio.api.facts_api import FactsApi
    from vrt_lss_studio.api.hardlinks_api import HardlinksApi
    from vrt_lss_studio.api.locations_api import LocationsApi
    from vrt_lss_studio.api.orders_api import OrdersApi
    from vrt_lss_studio.api.performers_api import PerformersApi
    from vrt_lss_studio.api.system_api import SystemApi
    from vrt_lss_studio.api.transports_api import TransportsApi
    from vrt_lss_studio.api.trips_api import TripsApi
    from vrt_lss_studio.api.user_api import UserApi
    
else:
    from lazy_imports import LazyModule, as_package, load

    load(
        LazyModule(
            *as_package(__file__),
            """# import apis into api package
from vrt_lss_studio.api.backups_api import BackupsApi
from vrt_lss_studio.api.custom_fields_api import CustomFieldsApi
from vrt_lss_studio.api.custom_icons_api import CustomIconsApi
from vrt_lss_studio.api.experiments_api import ExperimentsApi
from vrt_lss_studio.api.explorer_api import ExplorerApi
from vrt_lss_studio.api.external_routing_api import ExternalRoutingApi
from vrt_lss_studio.api.facts_api import FactsApi
from vrt_lss_studio.api.hardlinks_api import HardlinksApi
from vrt_lss_studio.api.locations_api import LocationsApi
from vrt_lss_studio.api.orders_api import OrdersApi
from vrt_lss_studio.api.performers_api import PerformersApi
from vrt_lss_studio.api.system_api import SystemApi
from vrt_lss_studio.api.transports_api import TransportsApi
from vrt_lss_studio.api.trips_api import TripsApi
from vrt_lss_studio.api.user_api import UserApi

""",
            name=__name__,
            doc=__doc__,
        )
    )
