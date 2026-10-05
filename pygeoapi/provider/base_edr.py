# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#
# Copyright (c) 2021 Tom Kralidis
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import logging

from pygeoapi.provider.base import BaseProvider, ProviderInvalidDataError

LOGGER = logging.getLogger(__name__)

EDR_QUERY_TYPES = [
    "position",
    "radius",
    "area",
    "cube",
    "trajectory",
    "corridor",
    "items",
    "locations",
    "instances",
]


class BaseEDRProvider(BaseProvider):
    """Base EDR Provider"""

    query_types = []

    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition

        :returns: pygeoapi.provider.base_edr.BaseEDRProvider
        """

        BaseProvider.__init__(self, provider_def)

    #        self.instances = []

    @classmethod
    def register(cls):
        def inner(fn):
            if fn.__name__ not in EDR_QUERY_TYPES:
                msg = "Invalid EDR Query type"
                LOGGER.error(msg)
                raise ProviderInvalidDataError(msg)

            # Kept for backwards compatibility. Note this list is shared by
            # every provider (``cls`` is BaseEDRProvider at decoration time),
            # so get_query_types() uses the per-method marker below instead.
            cls.query_types.append(fn.__name__)
            fn._edr_query_type = fn.__name__
            return fn

        return inner

    def get_instance(self, instance):
        """
        Validate instance identifier

        :returns: `bool` of whether instance is valid
        """

        return NotImplementedError()

    def get_query_types(self):
        """
        Provide supported query types

        :returns: `list` of EDR query types
        """

        # Only the query types this provider's class actually implements:
        # the shared ``query_types`` list would otherwise advertise every
        # query registered by any loaded provider (e.g. radius on a provider
        # that has no radius method).
        own = [
            qt
            for qt in EDR_QUERY_TYPES
            if getattr(getattr(type(self), qt, None), "_edr_query_type", None)
            == qt
        ]
        if not own:
            return self.query_types
        # Advertise instances only if this provider (for this collection)
        # actually has some: one provider class may serve collections with
        # and without instances.
        if "instances" not in own and callable(
            getattr(type(self), "instances", None)
        ):
            try:
                if self.instances():
                    own.append("instances")
            except Exception as err:
                LOGGER.debug(f"Could not list instances: {err}")
        return own

    def query(self, **kwargs):
        """
        Extract data from collection collection

        :param query_type: query type
        :param wkt: `shapely.geometry` WKT geometry
        :param datetime_: temporal (datestamp or extent)
        :param select_properties: list of parameters
        :param z: vertical level(s)
        :param format_: data format of output
        :param bbox: bbox geometry (for cube queries)
        :param within: distance (for radius queries)
        :param within_units: distance units (for radius queries)
        :param instance: instance name (for instances queries)
        :param limit: number of records to return (for locations queries)
        :param location_id: location identifier (for locations queries)

        :returns: coverage data as `dict` of CoverageJSON or native format
        """

        try:
            return getattr(self, kwargs.get("query_type"))(**kwargs)
        except AttributeError:
            raise NotImplementedError("Query not implemented!")
