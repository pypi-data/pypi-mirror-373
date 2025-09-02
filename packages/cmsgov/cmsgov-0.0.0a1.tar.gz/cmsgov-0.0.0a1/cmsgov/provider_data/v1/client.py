from __future__ import annotations

import oapi
import sob
import typing
from . import model
from logging import Logger


class Client(oapi.client.Client):

    def __init__(
        self,
        url: str | None = (
            "https://data.cms.gov/provider-data/api/1"
        ),
        user: str | None = None,
        password: str | None = None,
        api_key: str | None = None,
        timeout: int = 0,
        retry_number_of_attempts: int = 3,
        logger: Logger | None = None,
        echo: bool = False,
    ) -> None:
        """
        Parameters:
            url: The base URL for API requests.
            user: A user name for use with HTTP basic authentication.
            password:  A password for use with HTTP basic authentication.
            api_key: An API key with which to authenticate requests.
            timeout: The number of seconds before a request will timeout
                and throw an error. If this is 0 (the default), the system
                default timeout will be used.
            retry_number_of_attempts: The number of times to retry
                a request which results in an error.
            logger:
                A `logging.Logger` to which requests should be logged.
            echo: If `True`, requests/responses are printed as
                they occur.
        """

        super().__init__(
            url=url,
            user=user,
            password=password,
            api_key=api_key,
            timeout=timeout,
            retry_number_of_attempts=retry_number_of_attempts,
            logger=logger,
            echo=echo,
        )

    def get_datastore_imports(
        self,
    ) -> sob.abc.Dictionary:
        """
        Returns a list of all stored importers, with data about their file
        fetcher and status.
        """
        response: sob.abc.Readable = self.request(
            "/datastore/imports",
            method="GET",
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                sob.Dictionary,
            )
        )

    def post_datastore_imports(
        self,
        datastore_imports_post_request: (
            model.DatastoreImportsPostRequest
        ),
    ) -> sob.abc.Dictionary:
        """
        Immediately starts the import process for a datastore.

        Parameters:
            datastore_imports_post_request:
        """
        response: sob.abc.Readable = self.request(
            "/datastore/imports",
            method="POST",
            json=datastore_imports_post_request,
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                sob.Dictionary,
            )
        )

    def get_datastore_imports_identifier(
        self,
        identifier: str,
    ) -> model.DatastoreImportGetResponse:
        """
        Returns the numbers of rows and columns, and a list of columns headers
        from the datastore.

        Parameters:
            identifier: A datastore id. Note: there is an inconsistency in
                this API that will be addressed in the future: The expected
                format is different from the format supplied in /api/1/
                datastore/imports.
        """
        response: sob.abc.Readable = self.request(
            "/datastore/imports/{identifier}".format(**{
                "identifier": str(oapi.client.format_argument_value(
                    "identifier",
                    identifier,
                    style="simple",
                    explode=False,
                )),
            }),
            method="GET",
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                model.DatastoreImportGetResponse,
            )
        )

    def delete_datastore_imports_identifier(
        self,
        identifier: str,
    ) -> model.DatastoreImportDeleteResponse:
        """
        Delete one or more datastores. If the uuid parameter is that of a
        resource, delete that resource. If the uuid parameter is that of a
        dataset, delete all resources of that dataset.

        Parameters:
            identifier: A datastore id. Note: there is an inconsistency in
                this API that will be addressed in the future: The expected
                format is different from the format supplied in /api/1/
                datastore/imports.
        """
        response: sob.abc.Readable = self.request(
            "/datastore/imports/{identifier}".format(**{
                "identifier": str(oapi.client.format_argument_value(
                    "identifier",
                    identifier,
                    style="simple",
                    explode=False,
                )),
            }),
            method="DELETE",
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                model.DatastoreImportDeleteResponse,
            )
        )

    def get_datastore_query(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        count: bool | None = None,
        results: bool | None = None,
        schema: bool | None = None,
        keys: bool | None = None,
        format_: str | None = None,
        row_ids: bool | None = None,
        resources: (
            model.DatastoreQueryResources
            | None
        ) = None,
        properties: (
            model.DatastoreQueryProperties
            | None
        ) = None,
        conditions: (
            model.DatastoreQueryConditions
            | None
        ) = None,
        joins: (
            model.DatastoreQueryJoins
            | None
        ) = None,
        groupings: (
            model.DatastoreQueryGroupings
            | None
        ) = None,
        sorts: (
            model.DatastoreQuerySorts
            | None
        ) = None,
    ) -> (
        model.JsonOrCsvQueryOkResponse
        | str
    ):
        """
        Simple GET equivalent of a POST query. Note that parameters containing
        arrays or objects are not yet supported by SwaggerUI. For conditions,
        sorts, and other complex parameters, write your query in JSON and then
        convert to a nested query string. See [this web tool](https://www.
        convertonline.io/convert/json-to-query-string) for an example.

        Parameters:
            limit:
            offset:
            count:
            results:
            schema:
            keys:
            format_:
            row_ids:
            resources: Resources to query against and aliases. Usually you
                will add only one resource to this array, but if performing a
                join, list the primary resource first and then add resources to
                be used in the joins array.
            properties:
            conditions: Conditions or groups of conditions for the query,
                bound by 'and' operator.
            joins: Joins
            groupings: Properties or aliases to group results by.
            sorts: Result sorting directives.
        """
        response: sob.abc.Readable = self.request(
            "/datastore/query",
            method="GET",
            query={
                "limit": oapi.client.format_argument_value(
                    "limit",
                    limit,
                    style="deepObject",
                    explode=True,
                ),
                "offset": oapi.client.format_argument_value(
                    "offset",
                    offset,
                    style="deepObject",
                    explode=True,
                ),
                "count": oapi.client.format_argument_value(
                    "count",
                    count,
                    style="deepObject",
                    explode=True,
                ),
                "results": oapi.client.format_argument_value(
                    "results",
                    results,
                    style="deepObject",
                    explode=True,
                ),
                "schema": oapi.client.format_argument_value(
                    "schema",
                    schema,
                    style="deepObject",
                    explode=True,
                ),
                "keys": oapi.client.format_argument_value(
                    "keys",
                    keys,
                    style="deepObject",
                    explode=True,
                ),
                "format": oapi.client.format_argument_value(
                    "format",
                    format_,
                    style="deepObject",
                    explode=True,
                ),
                "rowIds": oapi.client.format_argument_value(
                    "rowIds",
                    row_ids,
                    style="deepObject",
                    explode=True,
                ),
                "resources": oapi.client.format_argument_value(
                    "resources",
                    resources,
                    style="deepObject",
                    explode=True,
                ),
                "properties": oapi.client.format_argument_value(
                    "properties",
                    properties,
                    style="deepObject",
                    explode=True,
                ),
                "conditions": oapi.client.format_argument_value(
                    "conditions",
                    conditions,
                    style="deepObject",
                    explode=True,
                ),
                "joins": oapi.client.format_argument_value(
                    "joins",
                    joins,
                    style="deepObject",
                    explode=True,
                ),
                "groupings": oapi.client.format_argument_value(
                    "groupings",
                    groupings,
                    style="deepObject",
                    explode=True,
                ),
                "sorts": oapi.client.format_argument_value(
                    "sorts",
                    sorts,
                    style="deepObject",
                    explode=True,
                ),
            },
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response, coerce_unparseable=str),
            types=(
                model.JsonOrCsvQueryOkResponse,
                sob.StringProperty(),
            )
        )

    def post_datastore_query(
        self,
        datastore_query: (
            model.DatastoreQuery
        ),
    ) -> (
        model.JsonOrCsvQueryOkResponse
        | str
    ):
        """
        Query one or more datastore resources

        Parameters:
            datastore_query: Schema for DKAN datastore queries
        """
        response: sob.abc.Readable = self.request(
            "/datastore/query",
            method="POST",
            json=datastore_query,
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response, coerce_unparseable=str),
            types=(
                model.JsonOrCsvQueryOkResponse,
                sob.StringProperty(),
            )
        )

    def get_datastore_query_download(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        count: bool | None = None,
        results: bool | None = None,
        schema: bool | None = None,
        keys: bool | None = None,
        format_: str | None = None,
        row_ids: bool | None = None,
        resources: (
            model.DatastoreQueryResources
            | None
        ) = None,
        properties: (
            model.DatastoreQueryProperties
            | None
        ) = None,
        conditions: (
            model.DatastoreQueryConditions
            | None
        ) = None,
        joins: (
            model.DatastoreQueryJoins
            | None
        ) = None,
        groupings: (
            model.DatastoreQueryGroupings
            | None
        ) = None,
        sorts: (
            model.DatastoreQuerySorts
            | None
        ) = None,
    ) -> str:
        """
        Simple GET equivalent of a POST query. Note that parameters containing
        arrays or objects are not yet supported by SwaggerUI. For conditions,
        sorts, and other complex parameters, write your query in JSON and then
        convert to a nested query string. See [this web tool](https://www.
        convertonline.io/convert/json-to-query-string) for an example.

        Parameters:
            limit:
            offset:
            count:
            results:
            schema:
            keys:
            format_:
            row_ids:
            resources: Resources to query against and aliases. Usually you
                will add only one resource to this array, but if performing a
                join, list the primary resource first and then add resources to
                be used in the joins array.
            properties:
            conditions: Conditions or groups of conditions for the query,
                bound by 'and' operator.
            joins: Joins
            groupings: Properties or aliases to group results by.
            sorts: Result sorting directives.
        """
        response: sob.abc.Readable = self.request(
            "/datastore/query/download",
            method="GET",
            query={
                "limit": oapi.client.format_argument_value(
                    "limit",
                    limit,
                    style="deepObject",
                    explode=True,
                ),
                "offset": oapi.client.format_argument_value(
                    "offset",
                    offset,
                    style="deepObject",
                    explode=True,
                ),
                "count": oapi.client.format_argument_value(
                    "count",
                    count,
                    style="deepObject",
                    explode=True,
                ),
                "results": oapi.client.format_argument_value(
                    "results",
                    results,
                    style="deepObject",
                    explode=True,
                ),
                "schema": oapi.client.format_argument_value(
                    "schema",
                    schema,
                    style="deepObject",
                    explode=True,
                ),
                "keys": oapi.client.format_argument_value(
                    "keys",
                    keys,
                    style="deepObject",
                    explode=True,
                ),
                "format": oapi.client.format_argument_value(
                    "format",
                    format_,
                    style="deepObject",
                    explode=True,
                ),
                "rowIds": oapi.client.format_argument_value(
                    "rowIds",
                    row_ids,
                    style="deepObject",
                    explode=True,
                ),
                "resources": oapi.client.format_argument_value(
                    "resources",
                    resources,
                    style="deepObject",
                    explode=True,
                ),
                "properties": oapi.client.format_argument_value(
                    "properties",
                    properties,
                    style="deepObject",
                    explode=True,
                ),
                "conditions": oapi.client.format_argument_value(
                    "conditions",
                    conditions,
                    style="deepObject",
                    explode=True,
                ),
                "joins": oapi.client.format_argument_value(
                    "joins",
                    joins,
                    style="deepObject",
                    explode=True,
                ),
                "groupings": oapi.client.format_argument_value(
                    "groupings",
                    groupings,
                    style="deepObject",
                    explode=True,
                ),
                "sorts": oapi.client.format_argument_value(
                    "sorts",
                    sorts,
                    style="deepObject",
                    explode=True,
                ),
            },
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response, coerce_unparseable=str),
            types=(
                sob.StringProperty(),
            )
        )

    def post_datastore_query_download(
        self,
        datastore_query: (
            model.DatastoreQuery
        ),
    ) -> str:
        """
        Query one or more datastore resources for file download

        Parameters:
            datastore_query: Schema for DKAN datastore queries
        """
        response: sob.abc.Readable = self.request(
            "/datastore/query/download",
            method="POST",
            json=datastore_query,
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response, coerce_unparseable=str),
            types=(
                sob.StringProperty(),
            )
        )

    def get_datastore_query_distribution_id(
        self,
        distribution_id: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
        count: bool | None = None,
        results: bool | None = None,
        schema: bool | None = None,
        keys: bool | None = None,
        format_: str | None = None,
        row_ids: bool | None = None,
        resources: (
            model.DatastoreQueryResources
            | None
        ) = None,
        properties: (
            model.DatastoreQueryProperties
            | None
        ) = None,
        conditions: (
            model.DatastoreQueryConditions
            | None
        ) = None,
        joins: (
            model.DatastoreQueryJoins
            | None
        ) = None,
        groupings: (
            model.DatastoreQueryGroupings
            | None
        ) = None,
        sorts: (
            model.DatastoreQuerySorts
            | None
        ) = None,
    ) -> (
        model.JsonOrCsvQueryOkResponse
        | str
    ):
        """
        Simple GET equivalent of a POST query. Note that parameters containing
        arrays or objects are not yet supported by SwaggerUI. For conditions,
        sorts, and other complex parameters, write your query in JSON and then
        convert to a nested query string. See [this web tool](https://www.
        convertonline.io/convert/json-to-query-string) for an example.

        Parameters:
            distribution_id: A distribution ID
            limit:
            offset:
            count:
            results:
            schema:
            keys:
            format_:
            row_ids:
            resources: Resources to query against and aliases. Usually you
                will add only one resource to this array, but if performing a
                join, list the primary resource first and then add resources to
                be used in the joins array.
            properties:
            conditions: Conditions or groups of conditions for the query,
                bound by 'and' operator.
            joins: Joins
            groupings: Properties or aliases to group results by.
            sorts: Result sorting directives.
        """
        response: sob.abc.Readable = self.request(
            "/datastore/query/{distributionId}".format(**{
                "distributionId": str(oapi.client.format_argument_value(
                    "distributionId",
                    distribution_id,
                    style="simple",
                    explode=False,
                )),
            }),
            method="GET",
            query={
                "limit": oapi.client.format_argument_value(
                    "limit",
                    limit,
                    style="deepObject",
                    explode=True,
                ),
                "offset": oapi.client.format_argument_value(
                    "offset",
                    offset,
                    style="deepObject",
                    explode=True,
                ),
                "count": oapi.client.format_argument_value(
                    "count",
                    count,
                    style="deepObject",
                    explode=True,
                ),
                "results": oapi.client.format_argument_value(
                    "results",
                    results,
                    style="deepObject",
                    explode=True,
                ),
                "schema": oapi.client.format_argument_value(
                    "schema",
                    schema,
                    style="deepObject",
                    explode=True,
                ),
                "keys": oapi.client.format_argument_value(
                    "keys",
                    keys,
                    style="deepObject",
                    explode=True,
                ),
                "format": oapi.client.format_argument_value(
                    "format",
                    format_,
                    style="deepObject",
                    explode=True,
                ),
                "rowIds": oapi.client.format_argument_value(
                    "rowIds",
                    row_ids,
                    style="deepObject",
                    explode=True,
                ),
                "resources": oapi.client.format_argument_value(
                    "resources",
                    resources,
                    style="deepObject",
                    explode=True,
                ),
                "properties": oapi.client.format_argument_value(
                    "properties",
                    properties,
                    style="deepObject",
                    explode=True,
                ),
                "conditions": oapi.client.format_argument_value(
                    "conditions",
                    conditions,
                    style="deepObject",
                    explode=True,
                ),
                "joins": oapi.client.format_argument_value(
                    "joins",
                    joins,
                    style="deepObject",
                    explode=True,
                ),
                "groupings": oapi.client.format_argument_value(
                    "groupings",
                    groupings,
                    style="deepObject",
                    explode=True,
                ),
                "sorts": oapi.client.format_argument_value(
                    "sorts",
                    sorts,
                    style="deepObject",
                    explode=True,
                ),
            },
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response, coerce_unparseable=str),
            types=(
                model.JsonOrCsvQueryOkResponse,
                sob.StringProperty(),
            )
        )

    def post_datastore_query_distribution_id(
        self,
        datastore_resource_query: (
            model.DatastoreResourceQuery
        ),
        distribution_id: str,
    ) -> (
        model.JsonOrCsvQueryOkResponse
        | str
    ):
        """
        Query a single datastore resource

        Parameters:
            datastore_resource_query: Schema for DKAN datastore queries.
                When querying against a specific resource, the "resource"
                property is always optional. If you want to set it explicitly,
                note that it will be aliased to simply "t".
            distribution_id: A distribution ID
        """
        response: sob.abc.Readable = self.request(
            "/datastore/query/{distributionId}".format(**{
                "distributionId": str(oapi.client.format_argument_value(
                    "distributionId",
                    distribution_id,
                    style="simple",
                    explode=False,
                )),
            }),
            method="POST",
            json=datastore_resource_query,
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response, coerce_unparseable=str),
            types=(
                model.JsonOrCsvQueryOkResponse,
                sob.StringProperty(),
            )
        )

    def get_datastore_query_dataset_id_index(
        self,
        dataset_id: str,
        index: int,
        *,
        limit: int | None = None,
        offset: int | None = None,
        count: bool | None = None,
        results: bool | None = None,
        schema: bool | None = None,
        keys: bool | None = None,
        format_: str | None = None,
        row_ids: bool | None = None,
        resources: (
            model.DatastoreQueryResources
            | None
        ) = None,
        properties: (
            model.DatastoreQueryProperties
            | None
        ) = None,
        conditions: (
            model.DatastoreQueryConditions
            | None
        ) = None,
        joins: (
            model.DatastoreQueryJoins
            | None
        ) = None,
        groupings: (
            model.DatastoreQueryGroupings
            | None
        ) = None,
        sorts: (
            model.DatastoreQuerySorts
            | None
        ) = None,
    ) -> (
        model.JsonOrCsvQueryOkResponse
        | str
    ):
        """
        Simple GET equivalent of a POST query -- see the POST endpoint
        documentation for full query schema. A few basic parameters are
        provided here as examples. For more reliable queries, write your query
        in JSON and then convert to a query string. See [this web tool](https:/
        /www.convertonline.io/convert/json-to-query-string) for an example.

        Parameters:
            dataset_id: A dataset ID
            index: The index of a distribution in a dataset's distribution
                array. For instance, the first distribution in a dataset would
                have an index of "0," the second would have "1", etc.
            limit:
            offset:
            count:
            results:
            schema:
            keys:
            format_:
            row_ids:
            resources: Resources to query against and aliases. Usually you
                will add only one resource to this array, but if performing a
                join, list the primary resource first and then add resources to
                be used in the joins array.
            properties:
            conditions: Conditions or groups of conditions for the query,
                bound by 'and' operator.
            joins: Joins
            groupings: Properties or aliases to group results by.
            sorts: Result sorting directives.
        """
        response: sob.abc.Readable = self.request(
            "/datastore/query/{datasetId}/{index}".format(**{
                "datasetId": str(oapi.client.format_argument_value(
                    "datasetId",
                    dataset_id,
                    style="simple",
                    explode=False,
                )),
                "index": str(oapi.client.format_argument_value(
                    "index",
                    index,
                    style="simple",
                    explode=False,
                )),
            }),
            method="GET",
            query={
                "limit": oapi.client.format_argument_value(
                    "limit",
                    limit,
                    style="deepObject",
                    explode=True,
                ),
                "offset": oapi.client.format_argument_value(
                    "offset",
                    offset,
                    style="deepObject",
                    explode=True,
                ),
                "count": oapi.client.format_argument_value(
                    "count",
                    count,
                    style="deepObject",
                    explode=True,
                ),
                "results": oapi.client.format_argument_value(
                    "results",
                    results,
                    style="deepObject",
                    explode=True,
                ),
                "schema": oapi.client.format_argument_value(
                    "schema",
                    schema,
                    style="deepObject",
                    explode=True,
                ),
                "keys": oapi.client.format_argument_value(
                    "keys",
                    keys,
                    style="deepObject",
                    explode=True,
                ),
                "format": oapi.client.format_argument_value(
                    "format",
                    format_,
                    style="deepObject",
                    explode=True,
                ),
                "rowIds": oapi.client.format_argument_value(
                    "rowIds",
                    row_ids,
                    style="deepObject",
                    explode=True,
                ),
                "resources": oapi.client.format_argument_value(
                    "resources",
                    resources,
                    style="deepObject",
                    explode=True,
                ),
                "properties": oapi.client.format_argument_value(
                    "properties",
                    properties,
                    style="deepObject",
                    explode=True,
                ),
                "conditions": oapi.client.format_argument_value(
                    "conditions",
                    conditions,
                    style="deepObject",
                    explode=True,
                ),
                "joins": oapi.client.format_argument_value(
                    "joins",
                    joins,
                    style="deepObject",
                    explode=True,
                ),
                "groupings": oapi.client.format_argument_value(
                    "groupings",
                    groupings,
                    style="deepObject",
                    explode=True,
                ),
                "sorts": oapi.client.format_argument_value(
                    "sorts",
                    sorts,
                    style="deepObject",
                    explode=True,
                ),
            },
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response, coerce_unparseable=str),
            types=(
                model.JsonOrCsvQueryOkResponse,
                sob.StringProperty(),
            )
        )

    def post_datastore_query_dataset_id_index(
        self,
        datastore_resource_query: (
            model.DatastoreResourceQuery
        ),
        dataset_id: str,
        index: int,
    ) -> (
        model.JsonOrCsvQueryOkResponse
        | str
    ):
        """
        Query a single datastore resource

        Parameters:
            datastore_resource_query: Schema for DKAN datastore queries.
                When querying against a specific resource, the "resource"
                property is always optional. If you want to set it explicitly,
                note that it will be aliased to simply "t".
            dataset_id: A dataset ID
            index: The index of a distribution in a dataset's distribution
                array. For instance, the first distribution in a dataset would
                have an index of "0," the second would have "1", etc.
        """
        response: sob.abc.Readable = self.request(
            "/datastore/query/{datasetId}/{index}".format(**{
                "datasetId": str(oapi.client.format_argument_value(
                    "datasetId",
                    dataset_id,
                    style="simple",
                    explode=False,
                )),
                "index": str(oapi.client.format_argument_value(
                    "index",
                    index,
                    style="simple",
                    explode=False,
                )),
            }),
            method="POST",
            json=datastore_resource_query,
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response, coerce_unparseable=str),
            types=(
                model.JsonOrCsvQueryOkResponse,
                sob.StringProperty(),
            )
        )

    def get_datastore_query_distribution_id_download(
        self,
        distribution_id: str,
        *,
        format_: str | None = None,
        resources: (
            model.DatastoreQueryResources
            | None
        ) = None,
        properties: (
            model.DatastoreQueryProperties
            | None
        ) = None,
        conditions: (
            model.DatastoreQueryConditions
            | None
        ) = None,
        joins: (
            model.DatastoreQueryJoins
            | None
        ) = None,
        groupings: (
            model.DatastoreQueryGroupings
            | None
        ) = None,
        sorts: (
            model.DatastoreQuerySorts
            | None
        ) = None,
    ) -> str:
        """
        Like the other datastore query GET endpoints, additional parameters may
        be added by serializing a query JSON object (documented in the POST
        endpoints) into a query string.

        Parameters:
            distribution_id: A distribution ID
            format_: Response format. Currently, only csv is supported.
            resources: Resources to query against and aliases. Usually you
                will add only one resource to this array, but if performing a
                join, list the primary resource first and then add resources to
                be used in the joins array.
            properties:
            conditions: Conditions or groups of conditions for the query,
                bound by 'and' operator.
            joins: Joins
            groupings: Properties or aliases to group results by.
            sorts: Result sorting directives.
        """
        response: sob.abc.Readable = self.request(
            "/datastore/query/{distributionId}/download".format(**{
                "distributionId": str(oapi.client.format_argument_value(
                    "distributionId",
                    distribution_id,
                    style="simple",
                    explode=False,
                )),
            }),
            method="GET",
            query={
                "format": oapi.client.format_argument_value(
                    "format",
                    format_,
                    style="deepObject",
                    explode=True,
                ),
                "resources": oapi.client.format_argument_value(
                    "resources",
                    resources,
                    style="deepObject",
                    explode=True,
                ),
                "properties": oapi.client.format_argument_value(
                    "properties",
                    properties,
                    style="deepObject",
                    explode=True,
                ),
                "conditions": oapi.client.format_argument_value(
                    "conditions",
                    conditions,
                    style="deepObject",
                    explode=True,
                ),
                "joins": oapi.client.format_argument_value(
                    "joins",
                    joins,
                    style="deepObject",
                    explode=True,
                ),
                "groupings": oapi.client.format_argument_value(
                    "groupings",
                    groupings,
                    style="deepObject",
                    explode=True,
                ),
                "sorts": oapi.client.format_argument_value(
                    "sorts",
                    sorts,
                    style="deepObject",
                    explode=True,
                ),
            },
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response, coerce_unparseable=str),
            types=(
                sob.StringProperty(),
            )
        )

    def get_datastore_query_dataset_id_index_download(
        self,
        dataset_id: str,
        index: int,
        *,
        format_: str | None = None,
        resources: (
            model.DatastoreQueryResources
            | None
        ) = None,
        properties: (
            model.DatastoreQueryProperties
            | None
        ) = None,
        conditions: (
            model.DatastoreQueryConditions
            | None
        ) = None,
        joins: (
            model.DatastoreQueryJoins
            | None
        ) = None,
        groupings: (
            model.DatastoreQueryGroupings
            | None
        ) = None,
        sorts: (
            model.DatastoreQuerySorts
            | None
        ) = None,
    ) -> str:
        """
        Like the other datastore query GET endpoints, additional parameters may
        be added by serializing a query JSON object (documented in the POST
        endpoints) into a query string.

        Parameters:
            dataset_id: A dataset ID
            index: The index of a distribution in a dataset's distribution
                array. For instance, the first distribution in a dataset would
                have an index of "0," the second would have "1", etc.
            format_: Response format. Currently, only csv is supported.
            resources: Resources to query against and aliases. Usually you
                will add only one resource to this array, but if performing a
                join, list the primary resource first and then add resources to
                be used in the joins array.
            properties:
            conditions: Conditions or groups of conditions for the query,
                bound by 'and' operator.
            joins: Joins
            groupings: Properties or aliases to group results by.
            sorts: Result sorting directives.
        """
        response: sob.abc.Readable = self.request(
            "/datastore/query/{datasetId}/{index}/download".format(**{
                "datasetId": str(oapi.client.format_argument_value(
                    "datasetId",
                    dataset_id,
                    style="simple",
                    explode=False,
                )),
                "index": str(oapi.client.format_argument_value(
                    "index",
                    index,
                    style="simple",
                    explode=False,
                )),
            }),
            method="GET",
            query={
                "format": oapi.client.format_argument_value(
                    "format",
                    format_,
                    style="deepObject",
                    explode=True,
                ),
                "resources": oapi.client.format_argument_value(
                    "resources",
                    resources,
                    style="deepObject",
                    explode=True,
                ),
                "properties": oapi.client.format_argument_value(
                    "properties",
                    properties,
                    style="deepObject",
                    explode=True,
                ),
                "conditions": oapi.client.format_argument_value(
                    "conditions",
                    conditions,
                    style="deepObject",
                    explode=True,
                ),
                "joins": oapi.client.format_argument_value(
                    "joins",
                    joins,
                    style="deepObject",
                    explode=True,
                ),
                "groupings": oapi.client.format_argument_value(
                    "groupings",
                    groupings,
                    style="deepObject",
                    explode=True,
                ),
                "sorts": oapi.client.format_argument_value(
                    "sorts",
                    sorts,
                    style="deepObject",
                    explode=True,
                ),
            },
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response, coerce_unparseable=str),
            types=(
                sob.StringProperty(),
            )
        )

    def get_datastore_sql(
        self,
        query: str,
        *,
        show_db_columns: bool | None = None,
    ) -> model.DatastoreSqlGetResponse:
        """
        Interact with resources in the datastore using an SQL-like syntax.

        Parameters:
            query: A SQL-like query.
                A `SELECT` using the `show_db_columns` parameter will make it
                easier to build queries against the data as
                it returns columns without spaces and in some cases, truncated
                names where the human readable column header
                is very long.
                `/api/1/datastore/sql?query=[SELECT * FROM DATASTORE_UUID][
                LIMIT 1 OFFSET 0];&show_db_columns`
                You can then build the `SELECT` part of the query. Do not use
                spaces between its arguments.
                `/api/1/datastore/sql?query=[SELECT a,b,c, FROM DATASTORE_UUID]
                `
                `WHERE` can use any column in the data.
                `/api/1/datastore/sql?query=[SELECT a,b FROM DATASTORE_UUID][
                WHERE c = "CCC"];&show_db_columns`
                `LIMIT` and `OFFSET` allow you to get more than the 500 record
                limit, by using successive queries:
                `/api/1/datastore/sql?query=[SELECT a,b,c FROM DATASTORE_UUID][
                WHERE d = "CCC"][LIMIT 500 OFFSET 0];&show_db_columns`
                `/api/1/datastore/sql?query=[SELECT a,b,c FROM DATASTORE_UUID][
                WHERE d = "DDD"][LIMIT 500 OFFSET 500];&show_db_columns`
                Note: `SELECT`, `WHERE` and `LIMIT...OFFSET` clauses must each
                be included within brackets `[ ]`.
            show_db_columns: Add `&show_db_columns` to return columns
                without spaces and in some cases, truncated names where the
                human
                readable column header is very long.
        """
        response: sob.abc.Readable = self.request(
            "/datastore/sql",
            method="GET",
            query={
                "query": oapi.client.format_argument_value(
                    "query",
                    query,
                    style="form",
                    explode=True,
                ),
                "show_db_columns": oapi.client.format_argument_value(
                    "show_db_columns",
                    show_db_columns,
                    style="form",
                    explode=True,
                ),
            },
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                model.DatastoreSqlGetResponse,
            )
        )

    def get_harvest_plans(
        self,
    ) -> model.HarvestPlansGetResponse:
        """
        Lists the identifiers of all registered harvests.
        """
        response: sob.abc.Readable = self.request(
            "/harvest/plans",
            method="GET",
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                model.HarvestPlansGetResponse,
            )
        )

    def post_harvest_plans(
        self,
        harvest_plan: (
            model.HarvestPlan
        ),
    ) -> model.HarvestPlansPostResponse:
        """
        Registers a new harvest, after validating against our schema.

        Parameters:
            harvest_plan:
        """
        response: sob.abc.Readable = self.request(
            "/harvest/plans",
            method="POST",
            json=harvest_plan,
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                model.HarvestPlansPostResponse,
            )
        )

    def get_harvest_plans_plan_id(
        self,
        plan_id: str,
    ) -> model.HarvestPlan:
        """
        Get the json plan of a registered harvest, based on the its harvest id.

        Parameters:
            plan_id: A harvest plan identifier
        """
        response: sob.abc.Readable = self.request(
            "/harvest/plans/{plan_id}".format(**{
                "plan_id": str(oapi.client.format_argument_value(
                    "plan_id",
                    plan_id,
                    style="simple",
                    explode=False,
                )),
            }),
            method="GET",
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                model.HarvestPlan,
            )
        )

    def get_harvest_runs_run_id(
        self,
        run_id: str,
    ) -> sob.abc.Dictionary:
        """
        Gives information about a previous run for a specific harvest run.

        Parameters:
            run_id: A harvest run identifier
        """
        response: sob.abc.Readable = self.request(
            "/harvest/runs/{run_id}".format(**{
                "run_id": str(oapi.client.format_argument_value(
                    "run_id",
                    run_id,
                    style="simple",
                    explode=False,
                )),
            }),
            method="GET",
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                sob.Dictionary,
            )
        )

    def get_harvest_runs(
        self,
        plan: str,
    ) -> model.HarvestRunsGetResponse:
        """
        Lists the identifiers (timestamps) of previous runs for a particular
        harvest id.

        Parameters:
            plan: A harvest plan identifier
        """
        response: sob.abc.Readable = self.request(
            "/harvest/runs",
            method="GET",
            query={
                "plan": oapi.client.format_argument_value(
                    "plan",
                    plan,
                    style="form",
                    explode=True,
                ),
            },
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                model.HarvestRunsGetResponse,
            )
        )

    def post_harvest_runs(
        self,
        harvest_runs_post_request: (
            model.HarvestRunsPostRequest
        ),
    ) -> model.HarvestRunsPostResponse:
        """
        Runs a harvest for a specific plan identifier inside json object
        payload.

        Parameters:
            harvest_runs_post_request:
        """
        response: sob.abc.Readable = self.request(
            "/harvest/runs",
            method="POST",
            json=harvest_runs_post_request,
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                model.HarvestRunsPostResponse,
            )
        )

    def get_metastore_schemas(
        self,
    ) -> sob.abc.Dictionary:
        """
        Get list of all schemas
        """
        response: sob.abc.Readable = self.request(
            "/metastore/schemas",
            method="GET",
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                sob.Dictionary,
            )
        )

    def get_metastore_schemas_schema_id(
        self,
        schema_id: str,
    ) -> sob.abc.Dictionary:
        """
        Get a specific schema

        Parameters:
            schema_id: The name a of a specific schema. For instance, "
                dataset."
        """
        response: sob.abc.Readable = self.request(
            "/metastore/schemas/{schema_id}".format(**{
                "schema_id": str(oapi.client.format_argument_value(
                    "schema_id",
                    schema_id,
                    style="simple",
                    explode=False,
                )),
            }),
            method="GET",
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                sob.Dictionary,
            )
        )

    def get_metastore_schemas_schema_id_items(
        self,
        schema_id: str,
        *,
        show_reference_ids: bool | None = None,
    ) -> model.MetastoreSchemasSchemaIdItemsGetResponse:
        """
        Get all items for a specific schema (e.g., "dataset")

        Parameters:
            schema_id: The name a of a specific schema. For instance, "
                dataset."
            show_reference_ids: Metastore objects often include references
                to other objects stored in other schemas. These references are
                usually hidden in responses. Some identifiers are necessary to
                work with other API endpoints (e.g. datastore endpoints may
                require the distribution identifier). Add `?show-reference-ids`
                to show the identifiers generated by DKAN.
        """
        response: sob.abc.Readable = self.request(
            "/metastore/schemas/{schema_id}/items".format(**{
                "schema_id": str(oapi.client.format_argument_value(
                    "schema_id",
                    schema_id,
                    style="simple",
                    explode=False,
                )),
            }),
            method="GET",
            query={
                "show-reference-ids": oapi.client.format_argument_value(
                    "show-reference-ids",
                    show_reference_ids,
                    style="form",
                    explode=True,
                ),
            },
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                model.MetastoreSchemasSchemaIdItemsGetResponse,
            )
        )

    def get_metastore_schemas_schema_id_items_identifier_revisions(
        self,
        schema_id: str,
        identifier: str,
    ) -> model.MetastoreSchemasSchemaIdItemsIdentifierRevisionsGetResponse:
        """
        Get all revisions for an item.

        Parameters:
            schema_id: The name a of a specific schema. For instance, "
                dataset."
            identifier: A dataset identifier
        """
        response: sob.abc.Readable = self.request(
            "/metastore/schemas/{schema_id}/items/{identifier}/revisions".format(**{  # noqa: E501
                "schema_id": str(oapi.client.format_argument_value(
                    "schema_id",
                    schema_id,
                    style="simple",
                    explode=False,
                )),
                "identifier": str(oapi.client.format_argument_value(
                    "identifier",
                    identifier,
                    style="simple",
                    explode=False,
                )),
            }),
            method="GET",
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                model.MetastoreSchemasSchemaIdItemsIdentifierRevisionsGetResponse,  # noqa: E501
            )
        )

    def post_metastore_schemas_schema_id_items_identifier_revisions(
        self,
        metastore_schema_revision_post_request: (
            model.MetastoreSchemaRevisionPostRequest
        ),
        schema_id: str,
        identifier: str,
    ) -> model.MetastoreWriteResponse:
        """
        Create new item revision/state.

        Parameters:
            metastore_schema_revision_post_request:
            schema_id: The name a of a specific schema. For instance, "
                dataset."
            identifier: A dataset identifier
        """
        response: sob.abc.Readable = self.request(
            "/metastore/schemas/{schema_id}/items/{identifier}/revisions".format(**{  # noqa: E501
                "schema_id": str(oapi.client.format_argument_value(
                    "schema_id",
                    schema_id,
                    style="simple",
                    explode=False,
                )),
                "identifier": str(oapi.client.format_argument_value(
                    "identifier",
                    identifier,
                    style="simple",
                    explode=False,
                )),
            }),
            method="POST",
            json=metastore_schema_revision_post_request,
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                model.MetastoreWriteResponse,
            )
        )

    def get_metastore_schemas_schema_id_items_identifier_revisions_revision_id(
        self,
        schema_id: str,
        identifier: str,
        revision_id: str,
    ) -> model.MetastoreRevision:
        """
        Get all revisions for an item.

        Parameters:
            schema_id: The name a of a specific schema. For instance, "
                dataset."
            identifier: A dataset identifier
            revision_id: Revision identifier. Use "identifier" property
                from revision object.
        """
        response: sob.abc.Readable = self.request(
            "/metastore/schemas/{schema_id}/items/{identifier}/revisions/{revision_id}".format(**{  # noqa: E501
                "schema_id": str(oapi.client.format_argument_value(
                    "schema_id",
                    schema_id,
                    style="simple",
                    explode=False,
                )),
                "identifier": str(oapi.client.format_argument_value(
                    "identifier",
                    identifier,
                    style="simple",
                    explode=False,
                )),
                "revision_id": str(oapi.client.format_argument_value(
                    "revision_id",
                    revision_id,
                    style="simple",
                    explode=False,
                )),
            }),
            method="GET",
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                model.MetastoreRevision,
            )
        )

    def get_metastore_schemas_dataset_items(
        self,
        *,
        show_reference_ids: bool | None = None,
    ) -> model.Datasets:
        """
        Get all datasets.

        Parameters:
            show_reference_ids: Metastore objects often include references
                to other objects stored in other schemas. These references are
                usually hidden in responses. Some identifiers are necessary to
                work with other API endpoints (e.g. datastore endpoints may
                require the distribution identifier). Add `?show-reference-ids`
                to show the identifiers generated by DKAN.
        """
        response: sob.abc.Readable = self.request(
            "/metastore/schemas/dataset/items",
            method="GET",
            query={
                "show-reference-ids": oapi.client.format_argument_value(
                    "show-reference-ids",
                    show_reference_ids,
                    style="form",
                    explode=True,
                ),
            },
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                model.Datasets,
            )
        )

    def put_metastore_schemas_dataset_items(
        self,
        dataset: (
            model.Dataset
        ),
        identifier: str,
    ) -> model.MetastoreWriteResponse:
        """
        Object will be completely replaced; optional properties not included in
        the request will be deleted.

        Automatic example not yet available; try retrieving a dataset via GET,
        changing values, and pasting to test. If no item exists with the
        provided identifier, it will be created.

        Parameters:
            dataset: The metadata format for all federal open data.
                Validates a single JSON object entry (as opposed to entire
                Data.json catalog).
            identifier: A dataset identifier
        """
        response: sob.abc.Readable = self.request(
            "/metastore/schemas/dataset/items".format(**{
                "identifier": str(oapi.client.format_argument_value(
                    "identifier",
                    identifier,
                    style="simple",
                    explode=False,
                )),
            }),
            method="PUT",
            json=dataset,
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                model.MetastoreWriteResponse,
            )
        )

    def patch_metastore_schemas_dataset_items(
        self,
        metastore_schemas_dataset_items_patch_request: (
            model.MetastoreSchemasDatasetItemsPatchRequest
        ),
        identifier: str,
    ) -> model.MetastoreWriteResponse:
        """
        Values provided will replace existing values, but required values may
        be omitted.

        Automatic example not yet available; try retrieving a dataset via GET,
        changing values, removing unchanged properties, and pasting to test.

        Parameters:
            metastore_schemas_dataset_items_patch_request: The metadata
                format for all federal open data. Validates a single JSON
                object entry (as opposed to entire Data.json catalog).
            identifier: A dataset identifier
        """
        response: sob.abc.Readable = self.request(
            "/metastore/schemas/dataset/items".format(**{
                "identifier": str(oapi.client.format_argument_value(
                    "identifier",
                    identifier,
                    style="simple",
                    explode=False,
                )),
            }),
            method="PATCH",
            json=metastore_schemas_dataset_items_patch_request,
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                model.MetastoreWriteResponse,
            )
        )

    def get_metastore_schemas_dataset_items_identifier(
        self,
        identifier: str,
        *,
        show_reference_ids: bool | None = None,
    ) -> model.Dataset:
        """
        Get a single dataset.

        Parameters:
            identifier: A dataset identifier
            show_reference_ids: Metastore objects often include references
                to other objects stored in other schemas. These references are
                usually hidden in responses. Some identifiers are necessary to
                work with other API endpoints (e.g. datastore endpoints may
                require the distribution identifier). Add `?show-reference-ids`
                to show the identifiers generated by DKAN.
        """
        response: sob.abc.Readable = self.request(
            "/metastore/schemas/dataset/items/{identifier}".format(**{
                "identifier": str(oapi.client.format_argument_value(
                    "identifier",
                    identifier,
                    style="simple",
                    explode=False,
                )),
            }),
            method="GET",
            query={
                "show-reference-ids": oapi.client.format_argument_value(
                    "show-reference-ids",
                    show_reference_ids,
                    style="form",
                    explode=True,
                ),
            },
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                model.Dataset,
            )
        )

    def put_metastore_schemas_dataset_items_identifier(
        self,
        dataset: (
            model.Dataset
        ),
        identifier: str,
    ) -> model.MetastoreWriteResponse:
        """
        Object will be completely replaced; optional properties not included in
        the request will be deleted.

        Automatic example not yet available; try retrieving a dataset via GET,
        changing values, and pasting to test. If no item exists with the
        provided identifier, it will be created.

        Parameters:
            dataset: The metadata format for all federal open data.
                Validates a single JSON object entry (as opposed to entire
                Data.json catalog).
            identifier: A dataset identifier
        """
        response: sob.abc.Readable = self.request(
            "/metastore/schemas/dataset/items/{identifier}".format(**{
                "identifier": str(oapi.client.format_argument_value(
                    "identifier",
                    identifier,
                    style="simple",
                    explode=False,
                )),
            }),
            method="PUT",
            json=dataset,
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                model.MetastoreWriteResponse,
            )
        )

    def patch_metastore_schemas_dataset_items_identifier(
        self,
        metastore_schemas_dataset_items_identifier_patch_request: (
            model.MetastoreSchemasDatasetItemsIdentifierPatchRequest
        ),
        identifier: str,
    ) -> model.MetastoreWriteResponse:
        """
        Values provided will replace existing values, but required values may
        be omitted.

        Automatic example not yet available; try retrieving a dataset via GET,
        changing values, removing unchanged properties, and pasting to test.

        Parameters:
            metastore_schemas_dataset_items_identifier_patch_request: The
                metadata format for all federal open data. Validates a single
                JSON object entry (as opposed to entire Data.json catalog).
            identifier: A dataset identifier
        """
        response: sob.abc.Readable = self.request(
            "/metastore/schemas/dataset/items/{identifier}".format(**{
                "identifier": str(oapi.client.format_argument_value(
                    "identifier",
                    identifier,
                    style="simple",
                    explode=False,
                )),
            }),
            method="PATCH",
            json=metastore_schemas_dataset_items_identifier_patch_request,
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                model.MetastoreWriteResponse,
            )
        )

    def get_search(
        self,
        *,
        fulltext: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        sort: (
            model.SortSearch
            | None
        ) = None,
        sort_order: (
            model.SortSearchOrder
            | None
        ) = None,
        facets: str | None = None,
        theme: str | None = None,
        keyword: str | None = None,
    ) -> model.SearchGetResponse:
        """
        Search description.

        Parameters:
            fulltext: Full-text search to run against any metadata fields
                indexed for fulltext searches.
            page: The page of the result set.
            page_size: How many results per page.
            sort: Which property to sort results on. Available properties
                : <em class="placeholder">access_level, description, keyword,
                modified, theme, title, title_string, search_api_relevance</em>
            sort_order: Sort results in ascending or descending order.
                Allowed values: <em>asc, desc</em>
            facets: Request information on facets. Pass a comma-separated
                list to get specific facets. Pass an empty value or "0" for no
                facet infrmation. Omit this parameter to get all facet
                information.
            theme: Filter results using <em class="placeholder">theme</em>
                facet.
            keyword: Filter results using <em class="placeholder">keyword</
                em> facet.
        """
        response: sob.abc.Readable = self.request(
            "/search",
            method="GET",
            query={
                "fulltext": oapi.client.format_argument_value(
                    "fulltext",
                    fulltext,
                    style="form",
                    explode=True,
                ),
                "page": oapi.client.format_argument_value(
                    "page",
                    page,
                    style="form",
                    explode=True,
                ),
                "page-size": oapi.client.format_argument_value(
                    "page-size",
                    page_size,
                    style="form",
                    explode=True,
                ),
                "sort": oapi.client.format_argument_value(
                    "sort",
                    sort,
                    style="form",
                    explode=False,
                ),
                "sort-order": oapi.client.format_argument_value(
                    "sort-order",
                    sort_order,
                    style="form",
                    explode=False,
                ),
                "facets": oapi.client.format_argument_value(
                    "facets",
                    facets,
                    style="form",
                    explode=False,
                ),
                "theme": oapi.client.format_argument_value(
                    "theme",
                    theme,
                    style="form",
                    explode=True,
                ),
                "keyword": oapi.client.format_argument_value(
                    "keyword",
                    keyword,
                    style="form",
                    explode=True,
                ),
            },
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                model.SearchGetResponse,
            )
        )

    def get_search_facets(
        self,
    ) -> model.SearchFacetsGetResponse:
        """
        Retrieve search facet information
        """
        response: sob.abc.Readable = self.request(
            "/search/facets",
            method="GET",
        )
        return sob.unmarshal(  # type: ignore
            sob.deserialize(response),
            types=(
                model.SearchFacetsGetResponse,
            )
        )
