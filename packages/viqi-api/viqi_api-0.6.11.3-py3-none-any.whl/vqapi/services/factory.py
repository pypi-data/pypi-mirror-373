import logging

from vqapi.plugins import filter_classes, find_plugins

from .base_proxy import FuturizedServiceProxy

log = logging.getLogger("vqapi.services")

# SERVICE_PROXIES = {
#     "admin": AdminProxy,
#     "auths": AuthProxy,
#     "blobs": BlobProxy,
#     "meta": DataProxy,
#     "mexes": MexProxy,
#     "datasets": DatasetProxy,
#     "import": ImportProxy,
#     "tables": TableProxy,
#     "pixels": ImageProxy,
#     "dirs": DirProxy,
#     "services": BaseServiceProxy,
#     "futures": FutureProxy,
# }


def import_proxies(name, module):
    """Filter for service proxy for classes with attribute 'service_name'"""
    return [(cls.service_name, cls) for nm, cls in filter_classes(name, module) if hasattr(cls, "service_name")]


class ServiceFactory:
    SERVICE_PROXIES = dict(find_plugins(".", import_proxies))

    # new unified service names (allow all variants for now)
    # TODO: change once all service names are final
    RENAMED_SERVICES = {
        "image_service": "pixels",
        "data_service": "meta",
        "dataset_service": "datasets",
        "auth_service": "auths",
        # "preference": "preferences", # KGK NOT RENAMED in viqi1
        "table": "tables",
        "pipeline": "pipelines",
        "blob_service": "blobs",
        "mex_service": "mexes",
    }

    @classmethod
    def make(cls, session, service_name):
        # translate to new service name
        service_name = cls.RENAMED_SERVICES.get(service_name, service_name)
        svc = cls.SERVICE_PROXIES.get(service_name, FuturizedServiceProxy)
        if session.service_map and service_name not in session.service_map:
            return None
        service = session.service_map[service_name]
        if isinstance(service, str):  #
            service = svc(session, service)
            session.service_map[service_name] = service
        return service
