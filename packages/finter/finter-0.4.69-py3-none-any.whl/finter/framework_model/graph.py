from __future__ import print_function

from finter.rest import ApiException
from finter.api.production_api import ProductionApi
from finter.settings import get_api_client, logger


class Graph:
    @staticmethod
    def get_related(identity_name: str, include: list, relation: list):
        def _conv(x):
            if isinstance(x, str):
                x = [x]
            return x

        include = _conv(include)
        relation = _conv(relation)

        try:
            resp = ProductionApi(
                get_api_client()
            ).production_graph_retrieve(
                identity_name=identity_name,
                include=",".join(include),
                relation=",".join(relation)
            )
        except ApiException as e:
            logger.error("Exception when calling AlphaApi->alpha_base_alpha_cm_retrieve: %s\n" % e)
            raise e
        return resp.related_models

    @staticmethod
    def get_depended(identity_name, include):
        return Graph.get_related(identity_name, include, "depended")["depended"]

    @staticmethod
    def get_affected(identity_name, include):
        return Graph.get_related(identity_name, include, "affected")["affected"]
