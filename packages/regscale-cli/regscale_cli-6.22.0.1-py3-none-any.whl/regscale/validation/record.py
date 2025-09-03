#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rich Logging"""


from regscale.core.app.api import Api

# standard python imports
from regscale.core.utils.graphql import GraphQLQuery
from regscale.models.regscale_models.modules import Modules


def validate_regscale_object(parent_id: int, parent_module: str) -> bool:
    """
    Query regscale to confirm the object in question exists.

    :param int parent_id: The RegScale id to query
    :param str parent_module: The RegScale module to query
    :return: Whether the object exists or not
    :rtype: bool
    """
    import inflect  # Optimize import performance

    api = Api()
    query = GraphQLQuery()
    query.start_query()
    result = False
    mods = Modules()
    p = inflect.engine()
    for (
        key,
        val,
    ) in mods.dict().items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
        if val.lower() == parent_module.lower():
            mod_lookup = p.plural(key)
    query.add_query(
        entity=mod_lookup,
        items=[
            "id",
        ],
        where={"id": {"eq": parent_id}},
    )
    query.end_query()

    dat = api.graph(query=query.build())
    if mod_lookup.lower() in [k.lower() for k in dat.keys()] and dat[list(dat.keys())[0]]["totalCount"] > 0:
        result = True
    return result
