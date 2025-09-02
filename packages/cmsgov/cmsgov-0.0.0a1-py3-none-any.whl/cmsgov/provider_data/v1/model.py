from __future__ import annotations
import datetime
import decimal
import typing
import sob


class JsonOrCsvQueryOkResponse(sob.Object):
    """
    Attributes:
        results:
        count:
        schema:
        query:
    """

    __slots__: tuple[str, ...] = (
        "results",
        "count",
        "schema",
        "query",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        results: (
            JsonOrCsvQueryOkResponseResults
            | None
        ) = None,
        count: (
            int
            | None
        ) = None,
        schema: (
            sob.Array
            | sob.Dictionary
            | None
        ) = None,
        query: (
            sob.Dictionary
            | None
        ) = None
    ) -> None:
        self.results: (
            JsonOrCsvQueryOkResponseResults
            | None
        ) = results
        self.count: (
            int
            | None
        ) = count
        self.schema: (
            sob.Array
            | sob.Dictionary
            | None
        ) = schema
        self.query: (
            sob.Dictionary
            | None
        ) = query
        super().__init__(_data)


class JsonOrCsvQueryOkResponseResults(sob.Array):

    def __init__(
        self,
        items: (
            typing.Iterable[
                sob.Dictionary
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class Dataset(sob.Object):
    """
    The metadata format for all federal open data. Validates a single JSON
    object entry (as opposed to entire Data.json catalog).

    Attributes:
        type_: IRI for the JSON-LD data type. This should be dcat:Dataset
            for each Dataset.
        title: Human-readable name of the asset. Should be in plain English
            and include sufficient detail to facilitate search and discovery.
        identifier: A unique identifier for the dataset or API as
            maintained within an Agency catalog or database.
        description: Human-readable description (e.g., an abstract) with
            sufficient detail to enable a user to quickly understand whether
            the asset is of interest.
        access_level: The degree to which this dataset could be made
            publicly-available, regardless of whether it has been made
            available. Choices: public (Data asset is or could be made publicly
            available to all without restrictions), restricted public (Data
            asset is available under certain use restrictions), or non-public (
            Data asset is not available to members of the public).
        rights: This may include information regarding access or
            restrictions based on privacy, security, or other policies. This
            should also provide an explanation for the selected "accessLevel"
            including instructions for how to access a restricted file, if
            applicable, or explanation for why a "non-public" or "restricted
            public" data assetis not "public," if applicable. Text, 255
            characters.
        accrual_periodicity: Frequency with which dataset is published.
        described_by: URL to the data dictionary for the dataset or API.
            Note that documentation other than a data dictionary can be
            referenced using Related Documents as shown in the expanded fields.
        described_by_type: The machine-readable file format (IANA Media
            Type or MIME Type) of the distribution’s describedBy URL.
        issued: Date of formal issuance.
        modified: Most recent date on which the dataset was changed,
            updated or modified.
        released: Date on which the dataset is scheduled to be published.
        next_update_date: The date on which the dataset is expected to be
            updated next.
        license_: The license dataset or API is published with. See <a href
            ="https://project-open-data.cio.gov/open-licenses/">Open Licenses</
            a> for more information.
        spatial: The <a href="https://project-open-data.cio.gov/v1.1/
            schema/#spatial">spatial coverage</a> of the dataset. Could include
            a spatial region like a bounding box or a named place.
        temporal: The <a href="https://project-open-data.cio.gov/v1.1/
            schema/#temporal">start and end dates</a> for which the dataset is
            applicable, separated by a "/" (i.e., 2000-01-15T00:45:00Z/2010-01-
            15T00:06:00Z).
        is_part_of: The collection of which the dataset is a subset.
        publisher: A Dataset Publisher Organization.
        bureau_code: Federal agencies, combined agency and bureau code from
             <a href="http://www.whitehouse.gov/sites/default/files/omb/assets/
            a11_current_year/app_c.pdf">OMB Circular A-11, Appendix C</a> in
            the format of <code>015:010</code>.
        program_code: Federal agencies, list the primary program related to
            this data asset, from the <a href="http://goals.performance.gov/
            sites/default/files/images/
            FederalProgramInventory_FY13_MachineReadable_091613.xls">Federal
            Program Inventory</a>. Use the format of <code>015:001</code>
        contact_point: A Dataset ContactPoint as a vCard object.
        theme: Main thematic category of the dataset.
        keyword: Tags (or keywords) help users discover your dataset;
            please include terms that would be used by technical and non-
            technical users.
        distribution: A distribution is a container for the data object.
            Each distribution should contain one accessURL or downloadURL. When
            providing a downloadURL, also include the format of the file.
        references: Related documents such as technical information about a
            dataset, developer documentation, etc.
        archive_exclude: For excluding this dataset from its provider's '
            download all datasets'.
        landing_page:
    """

    __slots__: tuple[str, ...] = (
        "type_",
        "title",
        "identifier",
        "description",
        "access_level",
        "rights",
        "accrual_periodicity",
        "described_by",
        "described_by_type",
        "issued",
        "modified",
        "released",
        "next_update_date",
        "license_",
        "spatial",
        "temporal",
        "is_part_of",
        "publisher",
        "bureau_code",
        "program_code",
        "contact_point",
        "theme",
        "keyword",
        "distribution",
        "references",
        "archive_exclude",
        "landing_page",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        type_: (
            str
            | None
        ) = None,
        title: (
            str
            | None
        ) = None,
        identifier: (
            str
            | None
        ) = None,
        description: (
            str
            | None
        ) = None,
        access_level: (
            str
            | None
        ) = None,
        rights: (
            str
            | sob.Null
            | None
        ) = None,
        accrual_periodicity: (
            str
            | None
        ) = None,
        described_by: (
            str
            | None
        ) = None,
        described_by_type: (
            str
            | None
        ) = None,
        issued: (
            str
            | None
        ) = None,
        modified: (
            str
            | None
        ) = None,
        released: (
            str
            | None
        ) = None,
        next_update_date: (
            str
            | None
        ) = None,
        license_: (
            str
            | None
        ) = None,
        spatial: (
            str
            | None
        ) = None,
        temporal: (
            str
            | None
        ) = None,
        is_part_of: (
            str
            | None
        ) = None,
        publisher: (
            DatasetPublisher
            | None
        ) = None,
        bureau_code: (
            DatasetBureauCode
            | None
        ) = None,
        program_code: (
            DatasetProgramCode
            | None
        ) = None,
        contact_point: (
            DatasetContactPoint
            | sob.Dictionary
            | None
        ) = None,
        theme: (
            DatasetTheme
            | None
        ) = None,
        keyword: (
            DatasetKeyword
            | None
        ) = None,
        distribution: (
            DatasetDistributions
            | None
        ) = None,
        references: (
            DatasetReferences
            | None
        ) = None,
        archive_exclude: (
            bool
            | None
        ) = None,
        landing_page: (
            str
            | None
        ) = None
    ) -> None:
        self.type_: (
            str
            | None
        ) = type_
        self.title: (
            str
            | None
        ) = title
        self.identifier: (
            str
            | None
        ) = identifier
        self.description: (
            str
            | None
        ) = description
        self.access_level: (
            str
            | None
        ) = access_level
        self.rights: (
            str
            | sob.Null
            | None
        ) = rights
        self.accrual_periodicity: (
            str
            | None
        ) = accrual_periodicity
        self.described_by: (
            str
            | None
        ) = described_by
        self.described_by_type: (
            str
            | None
        ) = described_by_type
        self.issued: (
            str
            | None
        ) = issued
        self.modified: (
            str
            | None
        ) = modified
        self.released: (
            str
            | None
        ) = released
        self.next_update_date: (
            str
            | None
        ) = next_update_date
        self.license_: (
            str
            | None
        ) = license_
        self.spatial: (
            str
            | None
        ) = spatial
        self.temporal: (
            str
            | None
        ) = temporal
        self.is_part_of: (
            str
            | None
        ) = is_part_of
        self.publisher: (
            DatasetPublisher
            | None
        ) = publisher
        self.bureau_code: (
            DatasetBureauCode
            | None
        ) = bureau_code
        self.program_code: (
            DatasetProgramCode
            | None
        ) = program_code
        self.contact_point: (
            DatasetContactPoint
            | sob.Dictionary
            | None
        ) = contact_point
        self.theme: (
            DatasetTheme
            | None
        ) = theme
        self.keyword: (
            DatasetKeyword
            | None
        ) = keyword
        self.distribution: (
            DatasetDistributions
            | None
        ) = distribution
        self.references: (
            DatasetReferences
            | None
        ) = references
        self.archive_exclude: (
            bool
            | None
        ) = archive_exclude
        self.landing_page: (
            str
            | None
        ) = landing_page
        super().__init__(_data)


class DatasetBureauCode(sob.Array):
    """
    Federal agencies, combined agency and bureau code from <a href="http://www.
    whitehouse.gov/sites/default/files/omb/assets/a11_current_year/app_c.pdf">
    OMB Circular A-11, Appendix C</a> in the format of <code>015:010</code>.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class DatasetContactPoint(sob.Object):
    """
    A Dataset ContactPoint as a vCard object.

    Attributes:
        type_: IRI for the JSON-LD data type. This should be vcard:Contact
            for contactPoint.
        fn: A full formatted name, e.g. Firstname Lastname.
        has_email: Email address for the contact name.
        has_url: URL for the contact
    """

    __slots__: tuple[str, ...] = (
        "type_",
        "fn",
        "has_email",
        "has_url",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        type_: (
            str
            | None
        ) = None,
        fn: (
            str
            | None
        ) = None,
        has_email: (
            str
            | None
        ) = None,
        has_url: (
            str
            | None
        ) = None
    ) -> None:
        self.type_: (
            str
            | None
        ) = type_
        self.fn: (
            str
            | None
        ) = fn
        self.has_email: (
            str
            | None
        ) = has_email
        self.has_url: (
            str
            | None
        ) = has_url
        super().__init__(_data)


class DatasetDistributions(sob.Array):
    """
    A distribution is a container for the data object. Each distribution should
    contain one accessURL or downloadURL. When providing a downloadURL, also
    include the format of the file.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                DatasetDistribution
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class DatasetDistribution(sob.Object):
    """
    Attributes:
        type_: IRI for the JSON-LD data type. This should be dcat:
            Distribution for each Distribution.
        title: Human-readable name of the file.
        description: Human-readable description of the file.
        format_: A human-readable description of the file format of a
            distribution (i.e. csv, pdf, kml, etc.).
        media_type: The machine-readable file format (<a href="https://www.
            iana.org/assignments/media-types/media-types.xhtml">IANA Media Type
            or MIME Type</a>) of the distribution’s downloadURL.
        download_url: URL providing direct access to a downloadable file of
            a dataset.
        access_url: URL providing indirect access to a dataset.
        conforms_to: URI used to identify a standardized specification the
            distribution conforms to.
        described_by: URL to the data dictionary for the distribution found
            at the downloadURL.
        described_by_type: The machine-readable file format (IANA Media
            Type or MIME Type) of the distribution’s describedBy URL.
    """

    __slots__: tuple[str, ...] = (
        "type_",
        "title",
        "description",
        "format_",
        "media_type",
        "download_url",
        "access_url",
        "conforms_to",
        "described_by",
        "described_by_type",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        type_: (
            str
            | None
        ) = None,
        title: (
            str
            | None
        ) = None,
        description: (
            str
            | None
        ) = None,
        format_: (
            str
            | None
        ) = None,
        media_type: (
            str
            | None
        ) = None,
        download_url: (
            str
            | None
        ) = None,
        access_url: (
            str
            | None
        ) = None,
        conforms_to: (
            str
            | None
        ) = None,
        described_by: (
            str
            | None
        ) = None,
        described_by_type: (
            str
            | None
        ) = None
    ) -> None:
        self.type_: (
            str
            | None
        ) = type_
        self.title: (
            str
            | None
        ) = title
        self.description: (
            str
            | None
        ) = description
        self.format_: (
            str
            | None
        ) = format_
        self.media_type: (
            str
            | None
        ) = media_type
        self.download_url: (
            str
            | None
        ) = download_url
        self.access_url: (
            str
            | None
        ) = access_url
        self.conforms_to: (
            str
            | None
        ) = conforms_to
        self.described_by: (
            str
            | None
        ) = described_by
        self.described_by_type: (
            str
            | None
        ) = described_by_type
        super().__init__(_data)


class DatasetKeyword(sob.Array):
    """
    Tags (or keywords) help users discover your dataset; please include terms
    that would be used by technical and non-technical users.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class DatasetProgramCode(sob.Array):
    """
    Federal agencies, list the primary program related to this data asset, from
    the <a href="http://goals.performance.gov/sites/default/files/images/
    FederalProgramInventory_FY13_MachineReadable_091613.xls">Federal Program
    Inventory</a>. Use the format of <code>015:001</code>
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class DatasetPublisher(sob.Object):
    """
    A Dataset Publisher Organization.

    Attributes:
        type_: IRI for the JSON-LD data type. This should be org:
            Organization for each publisher
        name:
        sub_organization_of:
    """

    __slots__: tuple[str, ...] = (
        "type_",
        "name",
        "sub_organization_of",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        type_: (
            str
            | None
        ) = None,
        name: (
            str
            | None
        ) = None,
        sub_organization_of: (
            str
            | None
        ) = None
    ) -> None:
        self.type_: (
            str
            | None
        ) = type_
        self.name: (
            str
            | None
        ) = name
        self.sub_organization_of: (
            str
            | None
        ) = sub_organization_of
        super().__init__(_data)


class DatasetReferences(sob.Array):
    """
    Related documents such as technical information about a dataset, developer
    documentation, etc.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class DatasetTheme(sob.Array):
    """
    Main thematic category of the dataset.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class Datasets(sob.Array):
    """
    An array of datasets.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                Dataset
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class DatastoreQuery(sob.Object):
    """
    Schema for DKAN datastore queries

    Attributes:
        resources: Resources to query against and aliases. Usually you will
            add only one resource to this array, but if performing a join, list
            the primary resource first and then add resources to be used in the
            joins array.
        properties:
        conditions: Conditions or groups of conditions for the query, bound
            by 'and' operator.
        joins: Joins
        groupings: Properties or aliases to group results by.
        limit: Limit for maximum number of records returned. Pass zero for
            no limit (may be restricted by user permissions).
        offset: Number of records to offset by or skip before returning
            first record.
        sorts: Result sorting directives.
        count: Return a count of the total rows returned by the query,
            ignoring the limit/offset.
        results: Return the result set. Set to false and set count to true
            to receive only a count of matches.
        schema: Return the schema for the datastore collection.
        keys: Return results as an array of keyed objects, with the column
            machine names as keys. If false, results will be an array of simple
            arrays of values.
        format_: Format to return data in. Default is JSON, can be set to
            CSV.
        row_ids: Flag to include the result_number column in output.
            Default is FALSE
    """

    __slots__: tuple[str, ...] = (
        "resources",
        "properties",
        "conditions",
        "joins",
        "groupings",
        "limit",
        "offset",
        "sorts",
        "count",
        "results",
        "schema",
        "keys",
        "format_",
        "row_ids",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        resources: (
            DatastoreQueryResources
            | None
        ) = None,
        properties: (
            DatastoreQueryProperties
            | None
        ) = None,
        conditions: (
            DatastoreQueryConditions
            | None
        ) = None,
        joins: (
            DatastoreQueryJoins
            | None
        ) = None,
        groupings: (
            DatastoreQueryGroupings
            | None
        ) = None,
        limit: (
            int
            | None
        ) = None,
        offset: (
            int
            | None
        ) = None,
        sorts: (
            DatastoreQuerySorts
            | None
        ) = None,
        count: (
            bool
            | None
        ) = None,
        results: (
            bool
            | None
        ) = None,
        schema: (
            bool
            | None
        ) = None,
        keys: (
            bool
            | None
        ) = None,
        format_: (
            str
            | None
        ) = None,
        row_ids: (
            bool
            | None
        ) = None
    ) -> None:
        self.resources: (
            DatastoreQueryResources
            | None
        ) = resources
        self.properties: (
            DatastoreQueryProperties
            | None
        ) = properties
        self.conditions: (
            DatastoreQueryConditions
            | None
        ) = conditions
        self.joins: (
            DatastoreQueryJoins
            | None
        ) = joins
        self.groupings: (
            DatastoreQueryGroupings
            | None
        ) = groupings
        self.limit: (
            int
            | None
        ) = limit
        self.offset: (
            int
            | None
        ) = offset
        self.sorts: (
            DatastoreQuerySorts
            | None
        ) = sorts
        self.count: (
            bool
            | None
        ) = count
        self.results: (
            bool
            | None
        ) = results
        self.schema: (
            bool
            | None
        ) = schema
        self.keys: (
            bool
            | None
        ) = keys
        self.format_: (
            str
            | None
        ) = format_
        self.row_ids: (
            bool
            | None
        ) = row_ids
        super().__init__(_data)


class DatastoreQueryConditions(sob.Array):
    """
    Conditions or groups of conditions for the query, bound by 'and' operator.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                DatastoreQueryCondition
                | DatastoreQueryConditionGroup
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class DatastoreQueryGroupings(sob.Array):
    """
    Properties or aliases to group results by.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
                | DatastoreQueryResourceProperty
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class DatastoreQueryJoins(sob.Array):
    """
    Joins
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                DatastoreQueryJoinsItem
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class DatastoreQueryJoinsItem(sob.Object):
    """
    Attributes:
        resource: Alias to resource set in resources array. Not needed when
            only querying against one resource.
        condition: Condition object including property, value and operator.
            If querying only one resource, the "resource" does not need to be
            specified.
    """

    __slots__: tuple[str, ...] = (
        "resource",
        "condition",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        resource: (
            str
            | None
        ) = None,
        condition: (
            DatastoreQueryCondition
            | None
        ) = None
    ) -> None:
        self.resource: (
            str
            | None
        ) = resource
        self.condition: (
            DatastoreQueryCondition
            | None
        ) = condition
        super().__init__(_data)


class DatastoreQueryProperties(sob.Array):

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
                | DatastoreQueryPropertyResource
                | DatastoreQueryPropertyExpression
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class DatastoreQueryPropertyResource(sob.Object):
    """
    Attributes:
        resource: Alias to resource set in resources array. Not needed when
            only querying against one resource.
        property_: The property/column or alias to filter by. Should not
            include collection/table alias.
        alias:
    """

    __slots__: tuple[str, ...] = (
        "resource",
        "property_",
        "alias",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        resource: (
            str
            | None
        ) = None,
        property_: (
            str
            | None
        ) = None,
        alias: (
            str
            | None
        ) = None
    ) -> None:
        self.resource: (
            str
            | None
        ) = resource
        self.property_: (
            str
            | None
        ) = property_
        self.alias: (
            str
            | None
        ) = alias
        super().__init__(_data)


class DatastoreQueryPropertyExpression(sob.Object):
    """
    Attributes:
        expression: Arithmetic or aggregate expression performed on one or
            more properties.
        alias:
    """

    __slots__: tuple[str, ...] = (
        "expression",
        "alias",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        expression: (
            DatastoreQueryExpression
            | None
        ) = None,
        alias: (
            str
            | None
        ) = None
    ) -> None:
        self.expression: (
            DatastoreQueryExpression
            | None
        ) = expression
        self.alias: (
            str
            | None
        ) = alias
        super().__init__(_data)


class DatastoreQueryResources(sob.Array):
    """
    Resources to query against and aliases. Usually you will add only one
    resource to this array, but if performing a join, list the primary resource
    first and then add resources to be used in the joins array.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                DatastoreQueryResource
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class DatastoreQueryResource(sob.Object):
    """
    Attributes:
        alias: Alias to use to refer to this resource elsewhere in the
            query.
        id_:
    """

    __slots__: tuple[str, ...] = (
        "alias",
        "id_",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        alias: (
            str
            | None
        ) = None,
        id_: (
            str
            | None
        ) = None
    ) -> None:
        self.alias: (
            str
            | None
        ) = alias
        self.id_: (
            str
            | None
        ) = id_
        super().__init__(_data)


class DatastoreQuerySorts(sob.Array):
    """
    Result sorting directives.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                DatastoreQuerySort
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class DatastoreQueryCondition(sob.Object):
    """
    Condition object including property, value and operator. If querying only
    one resource, the "resource" does not need to be specified.

    Attributes:
        resource: Alias to resource set in resources array. Not needed when
            only querying against one resource.
        property_: The property/column or alias to filter by. Should not
            include collection/table alias.
        value: The value to filter against.
        operator: Condition operator
    """

    __slots__: tuple[str, ...] = (
        "resource",
        "property_",
        "value",
        "operator",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        resource: (
            str
            | None
        ) = None,
        property_: (
            str
            | None
        ) = None,
        value: (
            sob.Array
            | str
            | decimal.Decimal
            | float
            | int
            | DatastoreQueryConditionValueAnyOf2
            | DatastoreQueryResourceProperty
            | None
        ) = None,
        operator: (
            str
            | None
        ) = None
    ) -> None:
        self.resource: (
            str
            | None
        ) = resource
        self.property_: (
            str
            | None
        ) = property_
        self.value: (
            sob.Array
            | str
            | decimal.Decimal
            | float
            | int
            | DatastoreQueryConditionValueAnyOf2
            | DatastoreQueryResourceProperty
            | None
        ) = value
        self.operator: (
            str
            | None
        ) = operator
        super().__init__(_data)


class DatastoreQueryConditionValueAnyOf2(sob.Array):

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
                | decimal.Decimal
                | float
                | int
                | str
                | float
                | int
                | decimal.Decimal
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class DatastoreQueryConditionGroup(sob.Object):
    """
    Group of conditions bound by 'and'/'or' operators.

    Attributes:
        group_operator:
        conditions:
    """

    __slots__: tuple[str, ...] = (
        "group_operator",
        "conditions",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        group_operator: (
            str
            | None
        ) = None,
        conditions: (
            DatastoreQueryConditionGroupConditions
            | None
        ) = None
    ) -> None:
        self.group_operator: (
            str
            | None
        ) = group_operator
        self.conditions: (
            DatastoreQueryConditionGroupConditions
            | None
        ) = conditions
        super().__init__(_data)


class DatastoreQueryConditionGroupConditions(sob.Array):

    def __init__(
        self,
        items: (
            typing.Iterable[
                DatastoreQueryCondition
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class DatastoreQueryExpression(sob.Object):
    """
    Arithmetic or aggregate expression performed on one or more properties.

    Attributes:
        operator: Expression operator. Note that performing expressions on
            text or other non-numeric data types my yield unexpected results.
        operands: Arithmetic operators will require two operands, aggregate
            operators should take only one. Do not combine arithmetic and
            aggregate operators in a single query.
    """

    __slots__: tuple[str, ...] = (
        "operator",
        "operands",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        operator: (
            str
            | None
        ) = None,
        operands: (
            DatastoreQueryExpressionOperands
            | None
        ) = None
    ) -> None:
        self.operator: (
            str
            | None
        ) = operator
        self.operands: (
            DatastoreQueryExpressionOperands
            | None
        ) = operands
        super().__init__(_data)


class DatastoreQueryExpressionOperands(sob.Array):
    """
    Arithmetic operators will require two operands, aggregate operators should
    take only one. Do not combine arithmetic and aggregate operators in a
    single query.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                float
                | int
                | decimal.Decimal
                | str
                | DatastoreQueryResourceProperty
                | DatastoreQueryExpressionOperandsItemAnyOf3
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class DatastoreQueryExpressionOperandsItemAnyOf3(sob.Object):
    """
    Attributes:
        expression: Arithmetic or aggregate expression performed on one or
            more properties.
    """

    __slots__: tuple[str, ...] = (
        "expression",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        expression: (
            typing.Any
            | None
        ) = None
    ) -> None:
        self.expression: (
            typing.Any
            | None
        ) = expression
        super().__init__(_data)


class DatastoreQueryResourceProperty(sob.Object):
    """
    Property name with optional collection/table alias.

    Attributes:
        resource: Alias to resource set in resources array. Not needed when
            only querying against one resource.
        property_: The property/column or alias to filter by. Should not
            include collection/table alias.
    """

    __slots__: tuple[str, ...] = (
        "resource",
        "property_",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        resource: (
            str
            | None
        ) = None,
        property_: (
            str
            | None
        ) = None
    ) -> None:
        self.resource: (
            str
            | None
        ) = resource
        self.property_: (
            str
            | None
        ) = property_
        super().__init__(_data)


class DatastoreQuerySort(sob.Object):
    """
    Properties to sort by in a particular order.

    Attributes:
        resource: Alias to resource set in resources array. Not needed when
            only querying against one resource.
        property_: The property/column or alias to filter by. Should not
            include collection/table alias.
        order: Order to sort in, lowercase.
    """

    __slots__: tuple[str, ...] = (
        "resource",
        "property_",
        "order",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        resource: (
            str
            | None
        ) = None,
        property_: (
            str
            | None
        ) = None,
        order: (
            str
            | None
        ) = None
    ) -> None:
        self.resource: (
            str
            | None
        ) = resource
        self.property_: (
            str
            | None
        ) = property_
        self.order: (
            str
            | None
        ) = order
        super().__init__(_data)


class DatastoreResourceQuery(sob.Object):
    """
    Schema for DKAN datastore queries. When querying against a specific
    resource, the "resource" property is always optional. If you want to set it
    explicitly, note that it will be aliased to simply "t".

    Attributes:
        properties:
        conditions: Conditions or groups of conditions for the query, bound
            by 'and' operator.
        groupings: Properties or aliases to group results by.
        limit: Limit for maximum number of records returned. Pass zero for
            no limit (may be restricted by user permissions).
        offset: Number of records to offset by or skip before returning
            first record.
        sorts: Result sorting directives.
        count: Return a count of the total rows returned by the query,
            ignoring the limit/offset.
        results: Return the result set. Set to false and set count to true
            to receive only a count of matches.
        schema: Return the schema for the datastore collection.
        keys: Return results as an array of keyed objects, with the column
            machine names as keys. If false, results will be an array of simple
            arrays of values.
        format_: Format to return data in. Default is JSON, can be set to
            CSV.
        row_ids: Flag to include the result_number column in output.
            Default is FALSE
    """

    __slots__: tuple[str, ...] = (
        "properties",
        "conditions",
        "groupings",
        "limit",
        "offset",
        "sorts",
        "count",
        "results",
        "schema",
        "keys",
        "format_",
        "row_ids",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        properties: (
            DatastoreResourceQueryProperties
            | None
        ) = None,
        conditions: (
            DatastoreResourceQueryConditions
            | None
        ) = None,
        groupings: (
            DatastoreResourceQueryGroupings
            | None
        ) = None,
        limit: (
            int
            | None
        ) = None,
        offset: (
            int
            | None
        ) = None,
        sorts: (
            DatastoreResourceQuerySorts
            | None
        ) = None,
        count: (
            bool
            | None
        ) = None,
        results: (
            bool
            | None
        ) = None,
        schema: (
            bool
            | None
        ) = None,
        keys: (
            bool
            | None
        ) = None,
        format_: (
            str
            | None
        ) = None,
        row_ids: (
            bool
            | None
        ) = None
    ) -> None:
        self.properties: (
            DatastoreResourceQueryProperties
            | None
        ) = properties
        self.conditions: (
            DatastoreResourceQueryConditions
            | None
        ) = conditions
        self.groupings: (
            DatastoreResourceQueryGroupings
            | None
        ) = groupings
        self.limit: (
            int
            | None
        ) = limit
        self.offset: (
            int
            | None
        ) = offset
        self.sorts: (
            DatastoreResourceQuerySorts
            | None
        ) = sorts
        self.count: (
            bool
            | None
        ) = count
        self.results: (
            bool
            | None
        ) = results
        self.schema: (
            bool
            | None
        ) = schema
        self.keys: (
            bool
            | None
        ) = keys
        self.format_: (
            str
            | None
        ) = format_
        self.row_ids: (
            bool
            | None
        ) = row_ids
        super().__init__(_data)


class DatastoreResourceQueryConditions(sob.Array):
    """
    Conditions or groups of conditions for the query, bound by 'and' operator.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                DatastoreQueryCondition
                | DatastoreQueryConditionGroup
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class DatastoreResourceQueryGroupings(sob.Array):
    """
    Properties or aliases to group results by.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
                | DatastoreQueryResourceProperty
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class DatastoreResourceQueryProperties(sob.Array):

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
                | DatastoreResourceQueryPropertiesItemAnyOf1
                | DatastoreResourceQueryPropertiesItemAnyOf2
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class DatastoreResourceQueryPropertiesItemAnyOf1(sob.Object):
    """
    Attributes:
        resource: Alias to resource set in resources array. Not needed when
            only querying against one resource.
        property_: The property/column or alias to filter by. Should not
            include collection/table alias.
        alias:
    """

    __slots__: tuple[str, ...] = (
        "resource",
        "property_",
        "alias",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        resource: (
            str
            | None
        ) = None,
        property_: (
            str
            | None
        ) = None,
        alias: (
            str
            | None
        ) = None
    ) -> None:
        self.resource: (
            str
            | None
        ) = resource
        self.property_: (
            str
            | None
        ) = property_
        self.alias: (
            str
            | None
        ) = alias
        super().__init__(_data)


class DatastoreResourceQueryPropertiesItemAnyOf2(sob.Object):
    """
    Attributes:
        expression: Arithmetic or aggregate expression performed on one or
            more properties.
        alias:
    """

    __slots__: tuple[str, ...] = (
        "expression",
        "alias",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        expression: (
            DatastoreQueryExpression
            | None
        ) = None,
        alias: (
            str
            | None
        ) = None
    ) -> None:
        self.expression: (
            DatastoreQueryExpression
            | None
        ) = expression
        self.alias: (
            str
            | None
        ) = alias
        super().__init__(_data)


class DatastoreResourceQuerySorts(sob.Array):
    """
    Result sorting directives.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                DatastoreQuerySort
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class ErrorResponse(sob.Object):
    """
    Attributes:
        message: Error message.
        status:
        timestamp:
        data: Arbitrary object storing more detailed data on the error
            message.
    """

    __slots__: tuple[str, ...] = (
        "message",
        "status",
        "timestamp",
        "data",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        message: (
            str
            | None
        ) = None,
        status: (
            int
            | None
        ) = None,
        timestamp: (
            datetime.datetime
            | None
        ) = None,
        data: (
            sob.Dictionary
            | None
        ) = None
    ) -> None:
        self.message: (
            str
            | None
        ) = message
        self.status: (
            int
            | None
        ) = status
        self.timestamp: (
            datetime.datetime
            | None
        ) = timestamp
        self.data: (
            sob.Dictionary
            | None
        ) = data
        super().__init__(_data)


class Facets(sob.Array):
    """
    Array of facet values.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                FacetsItem
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class FacetsItem(sob.Object):
    """
    Attributes:
        type_: Machine name for the metastore property to filter on.
        name: The facet filter value, for instance, the tet of a keyword to
            filter by
        total: Number of results in the current result set that match this
            filter.
    """

    __slots__: tuple[str, ...] = (
        "type_",
        "name",
        "total",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        type_: (
            str
            | None
        ) = None,
        name: (
            str
            | None
        ) = None,
        total: (
            str
            | int
            | None
        ) = None
    ) -> None:
        self.type_: (
            str
            | None
        ) = type_
        self.name: (
            str
            | None
        ) = name
        self.total: (
            str
            | int
            | None
        ) = total
        super().__init__(_data)


class HarvestPlan(sob.Object):
    """
    Attributes:
        identifier:
        extract:
        load:
    """

    __slots__: tuple[str, ...] = (
        "identifier",
        "extract",
        "load",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        identifier: (
            str
            | None
        ) = None,
        extract: (
            HarvestPlanExtract
            | None
        ) = None,
        load: (
            HarvestPlanLoad
            | None
        ) = None
    ) -> None:
        self.identifier: (
            str
            | None
        ) = identifier
        self.extract: (
            HarvestPlanExtract
            | None
        ) = extract
        self.load: (
            HarvestPlanLoad
            | None
        ) = load
        super().__init__(_data)


class HarvestPlanExtract(sob.Object):
    """
    Attributes:
        type_:
        uri:
    """

    __slots__: tuple[str, ...] = (
        "type_",
        "uri",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        type_: (
            str
            | None
        ) = None,
        uri: (
            str
            | None
        ) = None
    ) -> None:
        self.type_: (
            str
            | None
        ) = type_
        self.uri: (
            str
            | None
        ) = uri
        super().__init__(_data)


class HarvestPlanLoad(sob.Object):
    """
    Attributes:
        type_:
    """

    __slots__: tuple[str, ...] = (
        "type_",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        type_: (
            str
            | None
        ) = None
    ) -> None:
        self.type_: (
            str
            | None
        ) = type_
        super().__init__(_data)


class MetastoreNewRevision(sob.Object):
    """
    When creating a new revision, you may only submit a message and state.

    Attributes:
        message: Revision log message.
        state: The workflow state of this revision. Currently five states
            are supported in DKAN.
    """

    __slots__: tuple[str, ...] = (
        "message",
        "state",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        message: (
            str
            | None
        ) = None,
        state: (
            str
            | None
        ) = None
    ) -> None:
        self.message: (
            str
            | None
        ) = message
        self.state: (
            str
            | None
        ) = state
        super().__init__(_data)


class MetastoreRevision(sob.Object):
    """
    Attributes:
        identifier: Revision identifier.
        published: Is this the currently published revision?.
        message: Revision log message.
        modified: Timestamp of this revision/modification.
        state: The workflow state of this revision. Currently five states
            are supported in DKAN.
    """

    __slots__: tuple[str, ...] = (
        "identifier",
        "published",
        "message",
        "modified",
        "state",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        identifier: (
            str
            | None
        ) = None,
        published: (
            bool
            | None
        ) = None,
        message: (
            str
            | None
        ) = None,
        modified: (
            datetime.datetime
            | None
        ) = None,
        state: (
            str
            | None
        ) = None
    ) -> None:
        self.identifier: (
            str
            | None
        ) = identifier
        self.published: (
            bool
            | None
        ) = published
        self.message: (
            str
            | None
        ) = message
        self.modified: (
            datetime.datetime
            | None
        ) = modified
        self.state: (
            str
            | None
        ) = state
        super().__init__(_data)


class MetastoreWriteResponse(sob.Object):
    """
    Attributes:
        endpoint: Path to the metadata from the API.
        identifier: Identifier for metadata just created or modified.
    """

    __slots__: tuple[str, ...] = (
        "endpoint",
        "identifier",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        endpoint: (
            str
            | None
        ) = None,
        identifier: (
            str
            | None
        ) = None
    ) -> None:
        self.endpoint: (
            str
            | None
        ) = endpoint
        self.identifier: (
            str
            | None
        ) = identifier
        super().__init__(_data)


class DatastoreImportsPostRequest(sob.Object):
    """
    Attributes:
        plan_id:
    """

    __slots__: tuple[str, ...] = (
        "plan_id",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        plan_id: (
            str
            | None
        ) = None
    ) -> None:
        self.plan_id: (
            str
            | None
        ) = plan_id
        super().__init__(_data)


class DatastoreImportDeleteResponse(sob.Object):
    """
    Attributes:
        message:
    """

    __slots__: tuple[str, ...] = (
        "message",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        message: (
            str
            | None
        ) = None
    ) -> None:
        self.message: (
            str
            | None
        ) = message
        super().__init__(_data)


class DatastoreImportGetResponse(sob.Object):
    """
    Attributes:
        num_of_rows:
        num_of_columns:
        columns:
    """

    __slots__: tuple[str, ...] = (
        "num_of_rows",
        "num_of_columns",
        "columns",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        num_of_rows: (
            int
            | None
        ) = None,
        num_of_columns: (
            int
            | None
        ) = None,
        columns: (
            sob.Dictionary
            | None
        ) = None
    ) -> None:
        self.num_of_rows: (
            int
            | None
        ) = num_of_rows
        self.num_of_columns: (
            int
            | None
        ) = num_of_columns
        self.columns: (
            sob.Dictionary
            | None
        ) = columns
        super().__init__(_data)


class DatastoreSqlGetResponse(sob.Array):

    def __init__(
        self,
        items: (
            typing.Iterable[
                sob.Dictionary
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class HarvestPlansGetResponse(sob.Array):

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class HarvestPlansPostResponse(sob.Object):
    """
    Attributes:
        endpoint:
        identifier:
    """

    __slots__: tuple[str, ...] = (
        "endpoint",
        "identifier",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        endpoint: (
            str
            | None
        ) = None,
        identifier: (
            str
            | None
        ) = None
    ) -> None:
        self.endpoint: (
            str
            | None
        ) = endpoint
        self.identifier: (
            str
            | None
        ) = identifier
        super().__init__(_data)


class HarvestRunsGetResponse(sob.Array):

    def __init__(
        self,
        items: (
            typing.Iterable[
                sob.Dictionary
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class HarvestRunsPostRequest(sob.Object):
    """
    Attributes:
        plan_id:
    """

    __slots__: tuple[str, ...] = (
        "plan_id",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        plan_id: (
            str
            | None
        ) = None
    ) -> None:
        self.plan_id: (
            str
            | None
        ) = plan_id
        super().__init__(_data)


class HarvestRunsPostResponse(sob.Object):
    """
    Attributes:
        identifier:
        result:
    """

    __slots__: tuple[str, ...] = (
        "identifier",
        "result",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        identifier: (
            str
            | None
        ) = None,
        result: (
            str
            | None
        ) = None
    ) -> None:
        self.identifier: (
            str
            | None
        ) = identifier
        self.result: (
            str
            | None
        ) = result
        super().__init__(_data)


class MetastoreSchemasDatasetItemsPatchRequest(sob.Object):
    """
    The metadata format for all federal open data. Validates a single JSON
    object entry (as opposed to entire Data.json catalog).

    Attributes:
        type_: IRI for the JSON-LD data type. This should be dcat:Dataset
            for each Dataset.
        title: Human-readable name of the asset. Should be in plain English
            and include sufficient detail to facilitate search and discovery.
        identifier: A unique identifier for the dataset or API as
            maintained within an Agency catalog or database.
        description: Human-readable description (e.g., an abstract) with
            sufficient detail to enable a user to quickly understand whether
            the asset is of interest.
        access_level: The degree to which this dataset could be made
            publicly-available, regardless of whether it has been made
            available. Choices: public (Data asset is or could be made publicly
            available to all without restrictions), restricted public (Data
            asset is available under certain use restrictions), or non-public (
            Data asset is not available to members of the public).
        rights: This may include information regarding access or
            restrictions based on privacy, security, or other policies. This
            should also provide an explanation for the selected "accessLevel"
            including instructions for how to access a restricted file, if
            applicable, or explanation for why a "non-public" or "restricted
            public" data assetis not "public," if applicable. Text, 255
            characters.
        accrual_periodicity: Frequency with which dataset is published.
        described_by: URL to the data dictionary for the dataset or API.
            Note that documentation other than a data dictionary can be
            referenced using Related Documents as shown in the expanded fields.
        described_by_type: The machine-readable file format (IANA Media
            Type or MIME Type) of the distribution’s describedBy URL.
        issued: Date of formal issuance.
        modified: Most recent date on which the dataset was changed,
            updated or modified.
        released: Date on which the dataset is scheduled to be published.
        next_update_date: The date on which the dataset is expected to be
            updated next.
        license_: The license dataset or API is published with. See <a href
            ="https://project-open-data.cio.gov/open-licenses/">Open Licenses</
            a> for more information.
        spatial: The <a href="https://project-open-data.cio.gov/v1.1/
            schema/#spatial">spatial coverage</a> of the dataset. Could include
            a spatial region like a bounding box or a named place.
        temporal: The <a href="https://project-open-data.cio.gov/v1.1/
            schema/#temporal">start and end dates</a> for which the dataset is
            applicable, separated by a "/" (i.e., 2000-01-15T00:45:00Z/2010-01-
            15T00:06:00Z).
        is_part_of: The collection of which the dataset is a subset.
        publisher: A Dataset Publisher Organization.
        bureau_code: Federal agencies, combined agency and bureau code from
             <a href="http://www.whitehouse.gov/sites/default/files/omb/assets/
            a11_current_year/app_c.pdf">OMB Circular A-11, Appendix C</a> in
            the format of <code>015:010</code>.
        program_code: Federal agencies, list the primary program related to
            this data asset, from the <a href="http://goals.performance.gov/
            sites/default/files/images/
            FederalProgramInventory_FY13_MachineReadable_091613.xls">Federal
            Program Inventory</a>. Use the format of <code>015:001</code>
        contact_point: A Dataset ContactPoint as a vCard object.
        theme: Main thematic category of the dataset.
        keyword: Tags (or keywords) help users discover your dataset;
            please include terms that would be used by technical and non-
            technical users.
        distribution: A distribution is a container for the data object.
            Each distribution should contain one accessURL or downloadURL. When
            providing a downloadURL, also include the format of the file.
        references: Related documents such as technical information about a
            dataset, developer documentation, etc.
        archive_exclude: For excluding this dataset from its provider's '
            download all datasets'.
    """

    __slots__: tuple[str, ...] = (
        "type_",
        "title",
        "identifier",
        "description",
        "access_level",
        "rights",
        "accrual_periodicity",
        "described_by",
        "described_by_type",
        "issued",
        "modified",
        "released",
        "next_update_date",
        "license_",
        "spatial",
        "temporal",
        "is_part_of",
        "publisher",
        "bureau_code",
        "program_code",
        "contact_point",
        "theme",
        "keyword",
        "distribution",
        "references",
        "archive_exclude",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        type_: (
            str
            | None
        ) = None,
        title: (
            str
            | None
        ) = None,
        identifier: (
            str
            | None
        ) = None,
        description: (
            str
            | None
        ) = None,
        access_level: (
            str
            | None
        ) = None,
        rights: (
            str
            | sob.Null
            | None
        ) = None,
        accrual_periodicity: (
            str
            | None
        ) = None,
        described_by: (
            str
            | None
        ) = None,
        described_by_type: (
            str
            | None
        ) = None,
        issued: (
            str
            | None
        ) = None,
        modified: (
            str
            | None
        ) = None,
        released: (
            str
            | None
        ) = None,
        next_update_date: (
            str
            | None
        ) = None,
        license_: (
            str
            | None
        ) = None,
        spatial: (
            str
            | None
        ) = None,
        temporal: (
            str
            | None
        ) = None,
        is_part_of: (
            str
            | None
        ) = None,
        publisher: (
            MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaPublisher  # noqa: E501
            | None
        ) = None,
        bureau_code: (
            MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaBureauCode  # noqa: E501
            | None
        ) = None,
        program_code: (
            MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaProgramCode  # noqa: E501
            | None
        ) = None,
        contact_point: (
            MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaContactPoint  # noqa: E501
            | sob.Dictionary
            | None
        ) = None,
        theme: (
            MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaTheme  # noqa: E501
            | None
        ) = None,
        keyword: (
            MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaKeyword  # noqa: E501
            | None
        ) = None,
        distribution: (
            MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaDistribution  # noqa: E501
            | None
        ) = None,
        references: (
            MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaReferences  # noqa: E501
            | None
        ) = None,
        archive_exclude: (
            bool
            | None
        ) = None
    ) -> None:
        self.type_: (
            str
            | None
        ) = type_
        self.title: (
            str
            | None
        ) = title
        self.identifier: (
            str
            | None
        ) = identifier
        self.description: (
            str
            | None
        ) = description
        self.access_level: (
            str
            | None
        ) = access_level
        self.rights: (
            str
            | sob.Null
            | None
        ) = rights
        self.accrual_periodicity: (
            str
            | None
        ) = accrual_periodicity
        self.described_by: (
            str
            | None
        ) = described_by
        self.described_by_type: (
            str
            | None
        ) = described_by_type
        self.issued: (
            str
            | None
        ) = issued
        self.modified: (
            str
            | None
        ) = modified
        self.released: (
            str
            | None
        ) = released
        self.next_update_date: (
            str
            | None
        ) = next_update_date
        self.license_: (
            str
            | None
        ) = license_
        self.spatial: (
            str
            | None
        ) = spatial
        self.temporal: (
            str
            | None
        ) = temporal
        self.is_part_of: (
            str
            | None
        ) = is_part_of
        self.publisher: (
            MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaPublisher  # noqa: E501
            | None
        ) = publisher
        self.bureau_code: (
            MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaBureauCode  # noqa: E501
            | None
        ) = bureau_code
        self.program_code: (
            MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaProgramCode  # noqa: E501
            | None
        ) = program_code
        self.contact_point: (
            MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaContactPoint  # noqa: E501
            | sob.Dictionary
            | None
        ) = contact_point
        self.theme: (
            MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaTheme  # noqa: E501
            | None
        ) = theme
        self.keyword: (
            MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaKeyword  # noqa: E501
            | None
        ) = keyword
        self.distribution: (
            MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaDistribution  # noqa: E501
            | None
        ) = distribution
        self.references: (
            MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaReferences  # noqa: E501
            | None
        ) = references
        self.archive_exclude: (
            bool
            | None
        ) = archive_exclude
        super().__init__(_data)


class MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaBureauCode(  # noqa: E501
    sob.Array
):
    """
    Federal agencies, combined agency and bureau code from <a href="http://www.
    whitehouse.gov/sites/default/files/omb/assets/a11_current_year/app_c.pdf">
    OMB Circular A-11, Appendix C</a> in the format of <code>015:010</code>.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaContactPoint(  # noqa: E501
    sob.Object
):
    """
    A Dataset ContactPoint as a vCard object.

    Attributes:
        type_: IRI for the JSON-LD data type. This should be vcard:Contact
            for contactPoint.
        fn: A full formatted name, e.g. Firstname Lastname.
        has_email: Email address for the contact name.
        has_url: URL for the contact
    """

    __slots__: tuple[str, ...] = (
        "type_",
        "fn",
        "has_email",
        "has_url",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        type_: (
            str
            | None
        ) = None,
        fn: (
            str
            | None
        ) = None,
        has_email: (
            str
            | None
        ) = None,
        has_url: (
            str
            | None
        ) = None
    ) -> None:
        self.type_: (
            str
            | None
        ) = type_
        self.fn: (
            str
            | None
        ) = fn
        self.has_email: (
            str
            | None
        ) = has_email
        self.has_url: (
            str
            | None
        ) = has_url
        super().__init__(_data)


class MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaDistribution(  # noqa: E501
    sob.Array
):
    """
    A distribution is a container for the data object. Each distribution should
    contain one accessURL or downloadURL. When providing a downloadURL, also
    include the format of the file.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaDistributionItem  # noqa: E501
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaDistributionItem(  # noqa: E501
    sob.Object
):
    """
    Attributes:
        type_: IRI for the JSON-LD data type. This should be dcat:
            Distribution for each Distribution.
        title: Human-readable name of the file.
        description: Human-readable description of the file.
        format_: A human-readable description of the file format of a
            distribution (i.e. csv, pdf, kml, etc.).
        media_type: The machine-readable file format (<a href="https://www.
            iana.org/assignments/media-types/media-types.xhtml">IANA Media Type
            or MIME Type</a>) of the distribution’s downloadURL.
        download_url: URL providing direct access to a downloadable file of
            a dataset.
        access_url: URL providing indirect access to a dataset.
        conforms_to: URI used to identify a standardized specification the
            distribution conforms to.
        described_by: URL to the data dictionary for the distribution found
            at the downloadURL.
        described_by_type: The machine-readable file format (IANA Media
            Type or MIME Type) of the distribution’s describedBy URL.
    """

    __slots__: tuple[str, ...] = (
        "type_",
        "title",
        "description",
        "format_",
        "media_type",
        "download_url",
        "access_url",
        "conforms_to",
        "described_by",
        "described_by_type",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        type_: (
            str
            | None
        ) = None,
        title: (
            str
            | None
        ) = None,
        description: (
            str
            | None
        ) = None,
        format_: (
            str
            | None
        ) = None,
        media_type: (
            str
            | None
        ) = None,
        download_url: (
            str
            | None
        ) = None,
        access_url: (
            str
            | None
        ) = None,
        conforms_to: (
            str
            | None
        ) = None,
        described_by: (
            str
            | None
        ) = None,
        described_by_type: (
            str
            | None
        ) = None
    ) -> None:
        self.type_: (
            str
            | None
        ) = type_
        self.title: (
            str
            | None
        ) = title
        self.description: (
            str
            | None
        ) = description
        self.format_: (
            str
            | None
        ) = format_
        self.media_type: (
            str
            | None
        ) = media_type
        self.download_url: (
            str
            | None
        ) = download_url
        self.access_url: (
            str
            | None
        ) = access_url
        self.conforms_to: (
            str
            | None
        ) = conforms_to
        self.described_by: (
            str
            | None
        ) = described_by
        self.described_by_type: (
            str
            | None
        ) = described_by_type
        super().__init__(_data)


class MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaKeyword(  # noqa: E501
    sob.Array
):
    """
    Tags (or keywords) help users discover your dataset; please include terms
    that would be used by technical and non-technical users.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaProgramCode(  # noqa: E501
    sob.Array
):
    """
    Federal agencies, list the primary program related to this data asset, from
    the <a href="http://goals.performance.gov/sites/default/files/images/
    FederalProgramInventory_FY13_MachineReadable_091613.xls">Federal Program
    Inventory</a>. Use the format of <code>015:001</code>
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaPublisher(  # noqa: E501
    sob.Object
):
    """
    A Dataset Publisher Organization.

    Attributes:
        type_: IRI for the JSON-LD data type. This should be org:
            Organization for each publisher
        name:
        sub_organization_of:
    """

    __slots__: tuple[str, ...] = (
        "type_",
        "name",
        "sub_organization_of",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        type_: (
            str
            | None
        ) = None,
        name: (
            str
            | None
        ) = None,
        sub_organization_of: (
            str
            | None
        ) = None
    ) -> None:
        self.type_: (
            str
            | None
        ) = type_
        self.name: (
            str
            | None
        ) = name
        self.sub_organization_of: (
            str
            | None
        ) = sub_organization_of
        super().__init__(_data)


class MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaReferences(  # noqa: E501
    sob.Array
):
    """
    Related documents such as technical information about a dataset, developer
    documentation, etc.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaTheme(  # noqa: E501
    sob.Array
):
    """
    Main thematic category of the dataset.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class MetastoreSchemasDatasetItemsIdentifierPatchRequest(sob.Object):
    """
    The metadata format for all federal open data. Validates a single JSON
    object entry (as opposed to entire Data.json catalog).

    Attributes:
        type_: IRI for the JSON-LD data type. This should be dcat:Dataset
            for each Dataset.
        title: Human-readable name of the asset. Should be in plain English
            and include sufficient detail to facilitate search and discovery.
        identifier: A unique identifier for the dataset or API as
            maintained within an Agency catalog or database.
        description: Human-readable description (e.g., an abstract) with
            sufficient detail to enable a user to quickly understand whether
            the asset is of interest.
        access_level: The degree to which this dataset could be made
            publicly-available, regardless of whether it has been made
            available. Choices: public (Data asset is or could be made publicly
            available to all without restrictions), restricted public (Data
            asset is available under certain use restrictions), or non-public (
            Data asset is not available to members of the public).
        rights: This may include information regarding access or
            restrictions based on privacy, security, or other policies. This
            should also provide an explanation for the selected "accessLevel"
            including instructions for how to access a restricted file, if
            applicable, or explanation for why a "non-public" or "restricted
            public" data assetis not "public," if applicable. Text, 255
            characters.
        accrual_periodicity: Frequency with which dataset is published.
        described_by: URL to the data dictionary for the dataset or API.
            Note that documentation other than a data dictionary can be
            referenced using Related Documents as shown in the expanded fields.
        described_by_type: The machine-readable file format (IANA Media
            Type or MIME Type) of the distribution’s describedBy URL.
        issued: Date of formal issuance.
        modified: Most recent date on which the dataset was changed,
            updated or modified.
        released: Date on which the dataset is scheduled to be published.
        next_update_date: The date on which the dataset is expected to be
            updated next.
        license_: The license dataset or API is published with. See <a href
            ="https://project-open-data.cio.gov/open-licenses/">Open Licenses</
            a> for more information.
        spatial: The <a href="https://project-open-data.cio.gov/v1.1/
            schema/#spatial">spatial coverage</a> of the dataset. Could include
            a spatial region like a bounding box or a named place.
        temporal: The <a href="https://project-open-data.cio.gov/v1.1/
            schema/#temporal">start and end dates</a> for which the dataset is
            applicable, separated by a "/" (i.e., 2000-01-15T00:45:00Z/2010-01-
            15T00:06:00Z).
        is_part_of: The collection of which the dataset is a subset.
        publisher: A Dataset Publisher Organization.
        bureau_code: Federal agencies, combined agency and bureau code from
             <a href="http://www.whitehouse.gov/sites/default/files/omb/assets/
            a11_current_year/app_c.pdf">OMB Circular A-11, Appendix C</a> in
            the format of <code>015:010</code>.
        program_code: Federal agencies, list the primary program related to
            this data asset, from the <a href="http://goals.performance.gov/
            sites/default/files/images/
            FederalProgramInventory_FY13_MachineReadable_091613.xls">Federal
            Program Inventory</a>. Use the format of <code>015:001</code>
        contact_point: A Dataset ContactPoint as a vCard object.
        theme: Main thematic category of the dataset.
        keyword: Tags (or keywords) help users discover your dataset;
            please include terms that would be used by technical and non-
            technical users.
        distribution: A distribution is a container for the data object.
            Each distribution should contain one accessURL or downloadURL. When
            providing a downloadURL, also include the format of the file.
        references: Related documents such as technical information about a
            dataset, developer documentation, etc.
        archive_exclude: For excluding this dataset from its provider's '
            download all datasets'.
    """

    __slots__: tuple[str, ...] = (
        "type_",
        "title",
        "identifier",
        "description",
        "access_level",
        "rights",
        "accrual_periodicity",
        "described_by",
        "described_by_type",
        "issued",
        "modified",
        "released",
        "next_update_date",
        "license_",
        "spatial",
        "temporal",
        "is_part_of",
        "publisher",
        "bureau_code",
        "program_code",
        "contact_point",
        "theme",
        "keyword",
        "distribution",
        "references",
        "archive_exclude",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        type_: (
            str
            | None
        ) = None,
        title: (
            str
            | None
        ) = None,
        identifier: (
            str
            | None
        ) = None,
        description: (
            str
            | None
        ) = None,
        access_level: (
            str
            | None
        ) = None,
        rights: (
            str
            | sob.Null
            | None
        ) = None,
        accrual_periodicity: (
            str
            | None
        ) = None,
        described_by: (
            str
            | None
        ) = None,
        described_by_type: (
            str
            | None
        ) = None,
        issued: (
            str
            | None
        ) = None,
        modified: (
            str
            | None
        ) = None,
        released: (
            str
            | None
        ) = None,
        next_update_date: (
            str
            | None
        ) = None,
        license_: (
            str
            | None
        ) = None,
        spatial: (
            str
            | None
        ) = None,
        temporal: (
            str
            | None
        ) = None,
        is_part_of: (
            str
            | None
        ) = None,
        publisher: (
            MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaPublisher  # noqa: E501
            | None
        ) = None,
        bureau_code: (
            MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaBureauCode  # noqa: E501
            | None
        ) = None,
        program_code: (
            MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaProgramCode  # noqa: E501
            | None
        ) = None,
        contact_point: (
            MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaContactPoint  # noqa: E501
            | sob.Dictionary
            | None
        ) = None,
        theme: (
            MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaTheme  # noqa: E501
            | None
        ) = None,
        keyword: (
            MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaKeyword  # noqa: E501
            | None
        ) = None,
        distribution: (
            MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaDistribution  # noqa: E501
            | None
        ) = None,
        references: (
            MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaReferences  # noqa: E501
            | None
        ) = None,
        archive_exclude: (
            bool
            | None
        ) = None
    ) -> None:
        self.type_: (
            str
            | None
        ) = type_
        self.title: (
            str
            | None
        ) = title
        self.identifier: (
            str
            | None
        ) = identifier
        self.description: (
            str
            | None
        ) = description
        self.access_level: (
            str
            | None
        ) = access_level
        self.rights: (
            str
            | sob.Null
            | None
        ) = rights
        self.accrual_periodicity: (
            str
            | None
        ) = accrual_periodicity
        self.described_by: (
            str
            | None
        ) = described_by
        self.described_by_type: (
            str
            | None
        ) = described_by_type
        self.issued: (
            str
            | None
        ) = issued
        self.modified: (
            str
            | None
        ) = modified
        self.released: (
            str
            | None
        ) = released
        self.next_update_date: (
            str
            | None
        ) = next_update_date
        self.license_: (
            str
            | None
        ) = license_
        self.spatial: (
            str
            | None
        ) = spatial
        self.temporal: (
            str
            | None
        ) = temporal
        self.is_part_of: (
            str
            | None
        ) = is_part_of
        self.publisher: (
            MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaPublisher  # noqa: E501
            | None
        ) = publisher
        self.bureau_code: (
            MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaBureauCode  # noqa: E501
            | None
        ) = bureau_code
        self.program_code: (
            MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaProgramCode  # noqa: E501
            | None
        ) = program_code
        self.contact_point: (
            MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaContactPoint  # noqa: E501
            | sob.Dictionary
            | None
        ) = contact_point
        self.theme: (
            MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaTheme  # noqa: E501
            | None
        ) = theme
        self.keyword: (
            MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaKeyword  # noqa: E501
            | None
        ) = keyword
        self.distribution: (
            MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaDistribution  # noqa: E501
            | None
        ) = distribution
        self.references: (
            MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaReferences  # noqa: E501
            | None
        ) = references
        self.archive_exclude: (
            bool
            | None
        ) = archive_exclude
        super().__init__(_data)


class MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaBureauCode(  # noqa: E501
    sob.Array
):
    """
    Federal agencies, combined agency and bureau code from <a href="http://www.
    whitehouse.gov/sites/default/files/omb/assets/a11_current_year/app_c.pdf">
    OMB Circular A-11, Appendix C</a> in the format of <code>015:010</code>.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaContactPoint(  # noqa: E501
    sob.Object
):
    """
    A Dataset ContactPoint as a vCard object.

    Attributes:
        type_: IRI for the JSON-LD data type. This should be vcard:Contact
            for contactPoint.
        fn: A full formatted name, e.g. Firstname Lastname.
        has_email: Email address for the contact name.
        has_url: URL for the contact
    """

    __slots__: tuple[str, ...] = (
        "type_",
        "fn",
        "has_email",
        "has_url",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        type_: (
            str
            | None
        ) = None,
        fn: (
            str
            | None
        ) = None,
        has_email: (
            str
            | None
        ) = None,
        has_url: (
            str
            | None
        ) = None
    ) -> None:
        self.type_: (
            str
            | None
        ) = type_
        self.fn: (
            str
            | None
        ) = fn
        self.has_email: (
            str
            | None
        ) = has_email
        self.has_url: (
            str
            | None
        ) = has_url
        super().__init__(_data)


class MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaDistribution(  # noqa: E501
    sob.Array
):
    """
    A distribution is a container for the data object. Each distribution should
    contain one accessURL or downloadURL. When providing a downloadURL, also
    include the format of the file.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaDistributionItem  # noqa: E501
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaDistributionItem(  # noqa: E501
    sob.Object
):
    """
    Attributes:
        type_: IRI for the JSON-LD data type. This should be dcat:
            Distribution for each Distribution.
        title: Human-readable name of the file.
        description: Human-readable description of the file.
        format_: A human-readable description of the file format of a
            distribution (i.e. csv, pdf, kml, etc.).
        media_type: The machine-readable file format (<a href="https://www.
            iana.org/assignments/media-types/media-types.xhtml">IANA Media Type
            or MIME Type</a>) of the distribution’s downloadURL.
        download_url: URL providing direct access to a downloadable file of
            a dataset.
        access_url: URL providing indirect access to a dataset.
        conforms_to: URI used to identify a standardized specification the
            distribution conforms to.
        described_by: URL to the data dictionary for the distribution found
            at the downloadURL.
        described_by_type: The machine-readable file format (IANA Media
            Type or MIME Type) of the distribution’s describedBy URL.
    """

    __slots__: tuple[str, ...] = (
        "type_",
        "title",
        "description",
        "format_",
        "media_type",
        "download_url",
        "access_url",
        "conforms_to",
        "described_by",
        "described_by_type",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        type_: (
            str
            | None
        ) = None,
        title: (
            str
            | None
        ) = None,
        description: (
            str
            | None
        ) = None,
        format_: (
            str
            | None
        ) = None,
        media_type: (
            str
            | None
        ) = None,
        download_url: (
            str
            | None
        ) = None,
        access_url: (
            str
            | None
        ) = None,
        conforms_to: (
            str
            | None
        ) = None,
        described_by: (
            str
            | None
        ) = None,
        described_by_type: (
            str
            | None
        ) = None
    ) -> None:
        self.type_: (
            str
            | None
        ) = type_
        self.title: (
            str
            | None
        ) = title
        self.description: (
            str
            | None
        ) = description
        self.format_: (
            str
            | None
        ) = format_
        self.media_type: (
            str
            | None
        ) = media_type
        self.download_url: (
            str
            | None
        ) = download_url
        self.access_url: (
            str
            | None
        ) = access_url
        self.conforms_to: (
            str
            | None
        ) = conforms_to
        self.described_by: (
            str
            | None
        ) = described_by
        self.described_by_type: (
            str
            | None
        ) = described_by_type
        super().__init__(_data)


class MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaKeyword(  # noqa: E501
    sob.Array
):
    """
    Tags (or keywords) help users discover your dataset; please include terms
    that would be used by technical and non-technical users.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaProgramCode(  # noqa: E501
    sob.Array
):
    """
    Federal agencies, list the primary program related to this data asset, from
    the <a href="http://goals.performance.gov/sites/default/files/images/
    FederalProgramInventory_FY13_MachineReadable_091613.xls">Federal Program
    Inventory</a>. Use the format of <code>015:001</code>
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaPublisher(  # noqa: E501
    sob.Object
):
    """
    A Dataset Publisher Organization.

    Attributes:
        type_: IRI for the JSON-LD data type. This should be org:
            Organization for each publisher
        name:
        sub_organization_of:
    """

    __slots__: tuple[str, ...] = (
        "type_",
        "name",
        "sub_organization_of",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        type_: (
            str
            | None
        ) = None,
        name: (
            str
            | None
        ) = None,
        sub_organization_of: (
            str
            | None
        ) = None
    ) -> None:
        self.type_: (
            str
            | None
        ) = type_
        self.name: (
            str
            | None
        ) = name
        self.sub_organization_of: (
            str
            | None
        ) = sub_organization_of
        super().__init__(_data)


class MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaReferences(  # noqa: E501
    sob.Array
):
    """
    Related documents such as technical information about a dataset, developer
    documentation, etc.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaTheme(  # noqa: E501
    sob.Array
):
    """
    Main thematic category of the dataset.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class MetastoreSchemasSchemaIdItemsGetResponse(sob.Array):
    """
    Array of metastore items matching the chosen schema.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                sob.Dictionary
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class MetastoreSchemasSchemaIdItemsIdentifierRevisionsGetResponse(sob.Array):
    """
    Array of revision objects.
    """

    def __init__(
        self,
        items: (
            typing.Iterable[
                MetastoreRevision
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class MetastoreSchemaRevisionPostRequest(sob.Object):
    """
    Attributes:
        message: Revision log message.
        state: The workflow state of this revision. Currently five states
            are supported in DKAN.
    """

    __slots__: tuple[str, ...] = (
        "message",
        "state",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        message: (
            str
            | None
        ) = None,
        state: (
            str
            | None
        ) = None
    ) -> None:
        self.message: (
            str
            | None
        ) = message
        self.state: (
            str
            | None
        ) = state
        super().__init__(_data)


class SortSearch(sob.Array):

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class SortSearchOrder(sob.Array):

    def __init__(
        self,
        items: (
            typing.Iterable[
                str
            ]
            | sob.abc.Readable
            | str
            | bytes
            | None
        ) = None
    ) -> None:
        super().__init__(items)


class SearchGetResponse(sob.Object):
    """
    Attributes:
        total: Total search results for query.
        results: An object with keys following the format "dkan_dataset/[
            uuid]", containing full dataset objects from the DKAN metastore.
        facets: Array of facet values.
    """

    __slots__: tuple[str, ...] = (
        "total",
        "results",
        "facets",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        total: (
            str
            | int
            | None
        ) = None,
        results: (
            sob.Array
            | sob.Dictionary
            | None
        ) = None,
        facets: (
            Facets
            | None
        ) = None
    ) -> None:
        self.total: (
            str
            | int
            | None
        ) = total
        self.results: (
            sob.Array
            | sob.Dictionary
            | None
        ) = results
        self.facets: (
            Facets
            | None
        ) = facets
        super().__init__(_data)


class SearchFacetsGetResponse(sob.Object):
    """
    Attributes:
        facets: Array of facet values.
        time: Execution time.
        results: An object with keys following the format "dkan_dataset/[
            uuid]", containing full dataset objects from the DKAN metastore.
        total: Total search results for query.
    """

    __slots__: tuple[str, ...] = (
        "facets",
        "time",
        "results",
        "total",
    )

    def __init__(
        self,
        _data: (
            sob.abc.Dictionary
            | typing.Mapping[
                str,
                sob.abc.MarshallableTypes
            ]
            | typing.Iterable[
                tuple[
                    str,
                    sob.abc.MarshallableTypes
                ]
            ]
            | sob.abc.Readable
            | typing.IO
            | str
            | bytes
            | None
        ) = None,
        facets: (
            Facets
            | None
        ) = None,
        time: (
            float
            | int
            | decimal.Decimal
            | None
        ) = None,
        results: (
            sob.Array
            | sob.Dictionary
            | None
        ) = None,
        total: (
            str
            | int
            | None
        ) = None
    ) -> None:
        self.facets: (
            Facets
            | None
        ) = facets
        self.time: (
            float
            | int
            | decimal.Decimal
            | None
        ) = time
        self.results: (
            sob.Array
            | sob.Dictionary
            | None
        ) = results
        self.total: (
            str
            | int
            | None
        ) = total
        super().__init__(_data)


sob.get_writable_object_meta(  # type: ignore
    JsonOrCsvQueryOkResponse
).properties = sob.Properties([
    (
        'results',
        sob.Property(
            types=sob.MutableTypes([
                JsonOrCsvQueryOkResponseResults
            ])
        )
    ),
    ('count', sob.IntegerProperty()),
    (
        'schema',
        sob.Property(
            types=sob.MutableTypes([
                sob.Array,
                sob.Dictionary
            ])
        )
    ),
    (
        'query',
        sob.Property(
            types=sob.MutableTypes([
                sob.Dictionary
            ])
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    JsonOrCsvQueryOkResponseResults
).item_types = sob.MutableTypes([
    sob.Dictionary
])
sob.get_writable_object_meta(  # type: ignore
    Dataset
).properties = sob.Properties([
    (
        'type_',
        sob.StringProperty(
            name="@type"
        )
    ),
    (
        'title',
        sob.StringProperty(
            required=True
        )
    ),
    (
        'identifier',
        sob.StringProperty(
            required=True
        )
    ),
    (
        'description',
        sob.StringProperty(
            required=True
        )
    ),
    (
        'access_level',
        sob.EnumeratedProperty(
            name="accessLevel",
            required=True,
            types=sob.Types([
                str
            ]),
            values={
                "non-public",
                "private",
                "public",
                "restricted public"
            }
        )
    ),
    (
        'rights',
        sob.Property(
            types=sob.MutableTypes([
                sob.StringProperty(),
                sob.Null
            ])
        )
    ),
    (
        'accrual_periodicity',
        sob.EnumeratedProperty(
            name="accrualPeriodicity",
            types=sob.Types([
                str
            ]),
            values={
                "R/P0.33M",
                "R/P0.33W",
                "R/P0.5M",
                "R/P10Y",
                "R/P1D",
                "R/P1M",
                "R/P1W",
                "R/P1Y",
                "R/P2M",
                "R/P2W",
                "R/P2Y",
                "R/P3.5D",
                "R/P3M",
                "R/P3Y",
                "R/P4M",
                "R/P4Y",
                "R/P6M",
                "R/PT1H",
                "R/PT1S",
                "irregular"
            }
        )
    ),
    (
        'described_by',
        sob.StringProperty(
            name="describedBy"
        )
    ),
    (
        'described_by_type',
        sob.StringProperty(
            name="describedByType"
        )
    ),
    ('issued', sob.StringProperty()),
    (
        'modified',
        sob.StringProperty(
            required=True
        )
    ),
    (
        'released',
        sob.StringProperty(
            required=True
        )
    ),
    (
        'next_update_date',
        sob.StringProperty(
            name="nextUpdateDate"
        )
    ),
    (
        'license_',
        sob.StringProperty(
            name="license"
        )
    ),
    ('spatial', sob.StringProperty()),
    ('temporal', sob.StringProperty()),
    (
        'is_part_of',
        sob.StringProperty(
            name="isPartOf"
        )
    ),
    (
        'publisher',
        sob.Property(
            required=True,
            types=sob.MutableTypes([
                DatasetPublisher
            ])
        )
    ),
    (
        'bureau_code',
        sob.Property(
            name="bureauCode",
            required=True,
            types=sob.MutableTypes([
                DatasetBureauCode
            ])
        )
    ),
    (
        'program_code',
        sob.Property(
            name="programCode",
            required=True,
            types=sob.MutableTypes([
                DatasetProgramCode
            ])
        )
    ),
    (
        'contact_point',
        sob.Property(
            name="contactPoint",
            required=True,
            types=sob.MutableTypes([
                DatasetContactPoint,
                sob.Dictionary
            ])
        )
    ),
    (
        'theme',
        sob.Property(
            types=sob.MutableTypes([
                DatasetTheme
            ])
        )
    ),
    (
        'keyword',
        sob.Property(
            required=True,
            types=sob.MutableTypes([
                DatasetKeyword
            ])
        )
    ),
    (
        'distribution',
        sob.Property(
            types=sob.MutableTypes([
                DatasetDistributions
            ])
        )
    ),
    (
        'references',
        sob.Property(
            types=sob.MutableTypes([
                DatasetReferences
            ])
        )
    ),
    (
        'archive_exclude',
        sob.BooleanProperty(
            name="archiveExclude"
        )
    ),
    (
        'landing_page',
        sob.StringProperty(
            name="landingPage"
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    DatasetBureauCode
).item_types = sob.MutableTypes([
    sob.StringProperty()
])
sob.get_writable_object_meta(  # type: ignore
    DatasetContactPoint
).properties = sob.Properties([
    (
        'type_',
        sob.EnumeratedProperty(
            name="@type",
            types=sob.Types([
                str
            ]),
            values={
                "vcard:Contact"
            }
        )
    ),
    (
        'fn',
        sob.StringProperty(
            required=True
        )
    ),
    (
        'has_email',
        sob.StringProperty(
            name="hasEmail"
        )
    ),
    (
        'has_url',
        sob.StringProperty(
            name="hasURL"
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    DatasetDistributions
).item_types = sob.MutableTypes([
    DatasetDistribution
])
sob.get_writable_object_meta(  # type: ignore
    DatasetDistribution
).properties = sob.Properties([
    (
        'type_',
        sob.StringProperty(
            name="@type"
        )
    ),
    ('title', sob.StringProperty()),
    ('description', sob.StringProperty()),
    (
        'format_',
        sob.StringProperty(
            name="format"
        )
    ),
    (
        'media_type',
        sob.StringProperty(
            name="mediaType"
        )
    ),
    (
        'download_url',
        sob.Property(
            name="downloadURL",
            types=sob.MutableTypes([
                str
            ])
        )
    ),
    (
        'access_url',
        sob.StringProperty(
            name="accessURL"
        )
    ),
    (
        'conforms_to',
        sob.StringProperty(
            name="conformsTo"
        )
    ),
    (
        'described_by',
        sob.StringProperty(
            name="describedBy"
        )
    ),
    (
        'described_by_type',
        sob.StringProperty(
            name="describedByType"
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    DatasetKeyword
).item_types = sob.MutableTypes([
    sob.StringProperty()
])
sob.get_writable_array_meta(  # type: ignore
    DatasetProgramCode
).item_types = sob.MutableTypes([
    sob.StringProperty()
])
sob.get_writable_object_meta(  # type: ignore
    DatasetPublisher
).properties = sob.Properties([
    (
        'type_',
        sob.StringProperty(
            name="@type"
        )
    ),
    (
        'name',
        sob.StringProperty(
            required=True
        )
    ),
    (
        'sub_organization_of',
        sob.StringProperty(
            name="subOrganizationOf"
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    DatasetReferences
).item_types = sob.MutableTypes([
    sob.StringProperty()
])
sob.get_writable_array_meta(  # type: ignore
    DatasetTheme
).item_types = sob.MutableTypes([
    sob.StringProperty()
])
sob.get_writable_array_meta(  # type: ignore
    Datasets
).item_types = sob.MutableTypes([
    Dataset
])
sob.get_writable_object_meta(  # type: ignore
    DatastoreQuery
).properties = sob.Properties([
    (
        'resources',
        sob.Property(
            types=sob.MutableTypes([
                DatastoreQueryResources
            ])
        )
    ),
    (
        'properties',
        sob.Property(
            types=sob.MutableTypes([
                DatastoreQueryProperties
            ])
        )
    ),
    (
        'conditions',
        sob.Property(
            types=sob.MutableTypes([
                DatastoreQueryConditions
            ])
        )
    ),
    (
        'joins',
        sob.Property(
            types=sob.MutableTypes([
                DatastoreQueryJoins
            ])
        )
    ),
    (
        'groupings',
        sob.Property(
            types=sob.MutableTypes([
                DatastoreQueryGroupings
            ])
        )
    ),
    ('limit', sob.IntegerProperty()),
    ('offset', sob.IntegerProperty()),
    (
        'sorts',
        sob.Property(
            types=sob.MutableTypes([
                DatastoreQuerySorts
            ])
        )
    ),
    ('count', sob.BooleanProperty()),
    ('results', sob.BooleanProperty()),
    ('schema', sob.BooleanProperty()),
    ('keys', sob.BooleanProperty()),
    (
        'format_',
        sob.EnumeratedProperty(
            name="format",
            types=sob.Types([
                str
            ]),
            values={
                "csv",
                "json"
            }
        )
    ),
    (
        'row_ids',
        sob.BooleanProperty(
            name="rowIds"
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    DatastoreQueryConditions
).item_types = sob.MutableTypes([
    DatastoreQueryCondition,
    DatastoreQueryConditionGroup
])
sob.get_writable_array_meta(  # type: ignore
    DatastoreQueryGroupings
).item_types = sob.MutableTypes([
    sob.StringProperty(),
    DatastoreQueryResourceProperty
])
sob.get_writable_array_meta(  # type: ignore
    DatastoreQueryJoins
).item_types = sob.MutableTypes([
    DatastoreQueryJoinsItem
])
sob.get_writable_object_meta(  # type: ignore
    DatastoreQueryJoinsItem
).properties = sob.Properties([
    (
        'resource',
        sob.StringProperty(
            required=True
        )
    ),
    (
        'condition',
        sob.Property(
            required=True,
            types=sob.MutableTypes([
                DatastoreQueryCondition
            ])
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    DatastoreQueryProperties
).item_types = sob.MutableTypes([
    sob.StringProperty(),
    DatastoreQueryPropertyResource,
    DatastoreQueryPropertyExpression
])
sob.get_writable_object_meta(  # type: ignore
    DatastoreQueryPropertyResource
).properties = sob.Properties([
    (
        'resource',
        sob.StringProperty(
            required=True
        )
    ),
    (
        'property_',
        sob.StringProperty(
            name="property",
            required=True
        )
    ),
    ('alias', sob.StringProperty())
])
sob.get_writable_object_meta(  # type: ignore
    DatastoreQueryPropertyExpression
).properties = sob.Properties([
    (
        'expression',
        sob.Property(
            required=True,
            types=sob.MutableTypes([
                DatastoreQueryExpression
            ])
        )
    ),
    (
        'alias',
        sob.StringProperty(
            required=True
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    DatastoreQueryResources
).item_types = sob.MutableTypes([
    DatastoreQueryResource
])
sob.get_writable_object_meta(  # type: ignore
    DatastoreQueryResource
).properties = sob.Properties([
    ('alias', sob.StringProperty()),
    (
        'id_',
        sob.StringProperty(
            name="id"
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    DatastoreQuerySorts
).item_types = sob.MutableTypes([
    DatastoreQuerySort
])
sob.get_writable_object_meta(  # type: ignore
    DatastoreQueryCondition
).properties = sob.Properties([
    ('resource', sob.StringProperty()),
    (
        'property_',
        sob.StringProperty(
            name="property",
            required=True
        )
    ),
    (
        'value',
        sob.Property(
            required=True,
            types=sob.MutableTypes([
                sob.Array,
                str,
                decimal.Decimal,
                float,
                int,
                DatastoreQueryConditionValueAnyOf2,
                DatastoreQueryResourceProperty
            ])
        )
    ),
    (
        'operator',
        sob.EnumeratedProperty(
            types=sob.Types([
                str
            ]),
            values={
                "<",
                "<=",
                "<>",
                "=",
                ">",
                ">=",
                "between",
                "contains",
                "in",
                "is_empty",
                "like",
                "match",
                "not in",
                "not_empty",
                "starts with"
            }
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    DatastoreQueryConditionValueAnyOf2
).item_types = sob.MutableTypes([
    sob.Property(
        types=sob.MutableTypes([
            str,
            decimal.Decimal,
            float,
            int
        ])
    ),
    sob.StringProperty(),
    sob.NumberProperty()
])
sob.get_writable_object_meta(  # type: ignore
    DatastoreQueryConditionGroup
).properties = sob.Properties([
    (
        'group_operator',
        sob.EnumeratedProperty(
            name="groupOperator",
            types=sob.Types([
                str
            ]),
            values={
                "and",
                "or"
            }
        )
    ),
    (
        'conditions',
        sob.Property(
            required=True,
            types=sob.MutableTypes([
                DatastoreQueryConditionGroupConditions
            ])
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    DatastoreQueryConditionGroupConditions
).item_types = sob.MutableTypes([
    DatastoreQueryCondition
])
sob.get_writable_object_meta(  # type: ignore
    DatastoreQueryExpression
).properties = sob.Properties([
    (
        'operator',
        sob.EnumeratedProperty(
            types=sob.Types([
                str
            ]),
            values={
                "%",
                "*",
                "+",
                "-",
                "/",
                "avg",
                "count",
                "max",
                "min",
                "sum"
            }
        )
    ),
    (
        'operands',
        sob.Property(
            types=sob.MutableTypes([
                DatastoreQueryExpressionOperands
            ])
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    DatastoreQueryExpressionOperands
).item_types = sob.MutableTypes([
    sob.NumberProperty(),
    sob.StringProperty(),
    DatastoreQueryResourceProperty,
    DatastoreQueryExpressionOperandsItemAnyOf3
])
sob.get_writable_object_meta(  # type: ignore
    DatastoreQueryExpressionOperandsItemAnyOf3
).properties = sob.Properties([
    ('expression', sob.Property())
])
sob.get_writable_object_meta(  # type: ignore
    DatastoreQueryResourceProperty
).properties = sob.Properties([
    ('resource', sob.StringProperty()),
    (
        'property_',
        sob.StringProperty(
            name="property",
            required=True
        )
    )
])
sob.get_writable_object_meta(  # type: ignore
    DatastoreQuerySort
).properties = sob.Properties([
    ('resource', sob.StringProperty()),
    (
        'property_',
        sob.StringProperty(
            name="property"
        )
    ),
    (
        'order',
        sob.EnumeratedProperty(
            types=sob.Types([
                str
            ]),
            values={
                "asc",
                "desc"
            }
        )
    )
])
sob.get_writable_object_meta(  # type: ignore
    DatastoreResourceQuery
).properties = sob.Properties([
    (
        'properties',
        sob.Property(
            types=sob.MutableTypes([
                DatastoreResourceQueryProperties
            ])
        )
    ),
    (
        'conditions',
        sob.Property(
            types=sob.MutableTypes([
                DatastoreResourceQueryConditions
            ])
        )
    ),
    (
        'groupings',
        sob.Property(
            types=sob.MutableTypes([
                DatastoreResourceQueryGroupings
            ])
        )
    ),
    ('limit', sob.IntegerProperty()),
    ('offset', sob.IntegerProperty()),
    (
        'sorts',
        sob.Property(
            types=sob.MutableTypes([
                DatastoreResourceQuerySorts
            ])
        )
    ),
    ('count', sob.BooleanProperty()),
    ('results', sob.BooleanProperty()),
    ('schema', sob.BooleanProperty()),
    ('keys', sob.BooleanProperty()),
    (
        'format_',
        sob.EnumeratedProperty(
            name="format",
            types=sob.Types([
                str
            ]),
            values={
                "csv",
                "json"
            }
        )
    ),
    (
        'row_ids',
        sob.BooleanProperty(
            name="rowIds"
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    DatastoreResourceQueryConditions
).item_types = sob.MutableTypes([
    DatastoreQueryCondition,
    DatastoreQueryConditionGroup
])
sob.get_writable_array_meta(  # type: ignore
    DatastoreResourceQueryGroupings
).item_types = sob.MutableTypes([
    sob.StringProperty(),
    DatastoreQueryResourceProperty
])
sob.get_writable_array_meta(  # type: ignore
    DatastoreResourceQueryProperties
).item_types = sob.MutableTypes([
    sob.StringProperty(),
    DatastoreResourceQueryPropertiesItemAnyOf1,
    DatastoreResourceQueryPropertiesItemAnyOf2
])
sob.get_writable_object_meta(  # type: ignore
    DatastoreResourceQueryPropertiesItemAnyOf1
).properties = sob.Properties([
    (
        'resource',
        sob.StringProperty(
            required=True
        )
    ),
    (
        'property_',
        sob.StringProperty(
            name="property",
            required=True
        )
    ),
    ('alias', sob.StringProperty())
])
sob.get_writable_object_meta(  # type: ignore
    DatastoreResourceQueryPropertiesItemAnyOf2
).properties = sob.Properties([
    (
        'expression',
        sob.Property(
            required=True,
            types=sob.MutableTypes([
                DatastoreQueryExpression
            ])
        )
    ),
    (
        'alias',
        sob.StringProperty(
            required=True
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    DatastoreResourceQuerySorts
).item_types = sob.MutableTypes([
    DatastoreQuerySort
])
sob.get_writable_object_meta(  # type: ignore
    ErrorResponse
).properties = sob.Properties([
    ('message', sob.StringProperty()),
    ('status', sob.IntegerProperty()),
    ('timestamp', sob.DateTimeProperty()),
    (
        'data',
        sob.Property(
            types=sob.MutableTypes([
                sob.Dictionary
            ])
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    Facets
).item_types = sob.MutableTypes([
    FacetsItem
])
sob.get_writable_object_meta(  # type: ignore
    FacetsItem
).properties = sob.Properties([
    (
        'type_',
        sob.StringProperty(
            name="type"
        )
    ),
    ('name', sob.StringProperty()),
    (
        'total',
        sob.Property(
            types=sob.MutableTypes([
                str,
                int
            ])
        )
    )
])
sob.get_writable_object_meta(  # type: ignore
    HarvestPlan
).properties = sob.Properties([
    (
        'identifier',
        sob.StringProperty(
            required=True
        )
    ),
    (
        'extract',
        sob.Property(
            required=True,
            types=sob.MutableTypes([
                HarvestPlanExtract
            ])
        )
    ),
    (
        'load',
        sob.Property(
            required=True,
            types=sob.MutableTypes([
                HarvestPlanLoad
            ])
        )
    )
])
sob.get_writable_object_meta(  # type: ignore
    HarvestPlanExtract
).properties = sob.Properties([
    (
        'type_',
        sob.StringProperty(
            name="type",
            required=True
        )
    ),
    (
        'uri',
        sob.StringProperty(
            required=True
        )
    )
])
sob.get_writable_object_meta(  # type: ignore
    HarvestPlanLoad
).properties = sob.Properties([
    (
        'type_',
        sob.StringProperty(
            name="type",
            required=True
        )
    )
])
sob.get_writable_object_meta(  # type: ignore
    MetastoreNewRevision
).properties = sob.Properties([
    ('message', sob.StringProperty()),
    (
        'state',
        sob.EnumeratedProperty(
            required=True,
            types=sob.Types([
                str
            ]),
            values={
                "archived",
                "draft",
                "hidden",
                "orphaned",
                "published"
            }
        )
    )
])
sob.get_writable_object_meta(  # type: ignore
    MetastoreRevision
).properties = sob.Properties([
    ('identifier', sob.StringProperty()),
    ('published', sob.BooleanProperty()),
    ('message', sob.StringProperty()),
    ('modified', sob.DateTimeProperty()),
    (
        'state',
        sob.EnumeratedProperty(
            types=sob.Types([
                str
            ]),
            values={
                "archived",
                "draft",
                "hidden",
                "orphaned",
                "published"
            }
        )
    )
])
sob.get_writable_object_meta(  # type: ignore
    MetastoreWriteResponse
).properties = sob.Properties([
    ('endpoint', sob.StringProperty()),
    ('identifier', sob.StringProperty())
])
sob.get_writable_object_meta(  # type: ignore
    DatastoreImportsPostRequest
).properties = sob.Properties([
    ('plan_id', sob.StringProperty())
])
sob.get_writable_object_meta(  # type: ignore
    DatastoreImportDeleteResponse
).properties = sob.Properties([
    (
        'message',
        sob.StringProperty(
            required=True
        )
    )
])
sob.get_writable_object_meta(  # type: ignore
    DatastoreImportGetResponse
).properties = sob.Properties([
    (
        'num_of_rows',
        sob.IntegerProperty(
            name="numOfRows",
            required=True
        )
    ),
    (
        'num_of_columns',
        sob.IntegerProperty(
            name="numOfColumns",
            required=True
        )
    ),
    (
        'columns',
        sob.Property(
            required=True,
            types=sob.MutableTypes([
                sob.Dictionary
            ])
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    DatastoreSqlGetResponse
).item_types = sob.MutableTypes([
    sob.Dictionary
])
sob.get_writable_array_meta(  # type: ignore
    HarvestPlansGetResponse
).item_types = sob.MutableTypes([
    sob.StringProperty()
])
sob.get_writable_object_meta(  # type: ignore
    HarvestPlansPostResponse
).properties = sob.Properties([
    ('endpoint', sob.StringProperty()),
    (
        'identifier',
        sob.StringProperty(
            required=True
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    HarvestRunsGetResponse
).item_types = sob.MutableTypes([
    sob.Dictionary
])
sob.get_writable_object_meta(  # type: ignore
    HarvestRunsPostRequest
).properties = sob.Properties([
    (
        'plan_id',
        sob.StringProperty(
            required=True
        )
    )
])
sob.get_writable_object_meta(  # type: ignore
    HarvestRunsPostResponse
).properties = sob.Properties([
    (
        'identifier',
        sob.StringProperty(
            required=True
        )
    ),
    (
        'result',
        sob.StringProperty(
            required=True
        )
    )
])
sob.get_writable_object_meta(  # type: ignore
    MetastoreSchemasDatasetItemsPatchRequest
).properties = sob.Properties([
    (
        'type_',
        sob.StringProperty(
            name="@type"
        )
    ),
    ('title', sob.StringProperty()),
    ('identifier', sob.StringProperty()),
    ('description', sob.StringProperty()),
    (
        'access_level',
        sob.EnumeratedProperty(
            name="accessLevel",
            types=sob.Types([
                str
            ]),
            values={
                "non-public",
                "private",
                "public",
                "restricted public"
            }
        )
    ),
    (
        'rights',
        sob.Property(
            types=sob.MutableTypes([
                sob.StringProperty(),
                sob.Null
            ])
        )
    ),
    (
        'accrual_periodicity',
        sob.EnumeratedProperty(
            name="accrualPeriodicity",
            types=sob.Types([
                str
            ]),
            values={
                "R/P0.33M",
                "R/P0.33W",
                "R/P0.5M",
                "R/P10Y",
                "R/P1D",
                "R/P1M",
                "R/P1W",
                "R/P1Y",
                "R/P2M",
                "R/P2W",
                "R/P2Y",
                "R/P3.5D",
                "R/P3M",
                "R/P3Y",
                "R/P4M",
                "R/P4Y",
                "R/P6M",
                "R/PT1H",
                "R/PT1S",
                "irregular"
            }
        )
    ),
    (
        'described_by',
        sob.StringProperty(
            name="describedBy"
        )
    ),
    (
        'described_by_type',
        sob.StringProperty(
            name="describedByType"
        )
    ),
    ('issued', sob.StringProperty()),
    ('modified', sob.StringProperty()),
    ('released', sob.StringProperty()),
    (
        'next_update_date',
        sob.StringProperty(
            name="nextUpdateDate"
        )
    ),
    (
        'license_',
        sob.StringProperty(
            name="license"
        )
    ),
    ('spatial', sob.StringProperty()),
    ('temporal', sob.StringProperty()),
    (
        'is_part_of',
        sob.StringProperty(
            name="isPartOf"
        )
    ),
    (
        'publisher',
        sob.Property(
            types=sob.MutableTypes([
                MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaPublisher  # noqa: E501
            ])
        )
    ),
    (
        'bureau_code',
        sob.Property(
            name="bureauCode",
            types=sob.MutableTypes([
                MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaBureauCode  # noqa: E501
            ])
        )
    ),
    (
        'program_code',
        sob.Property(
            name="programCode",
            types=sob.MutableTypes([
                MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaProgramCode  # noqa: E501
            ])
        )
    ),
    (
        'contact_point',
        sob.Property(
            name="contactPoint",
            types=sob.MutableTypes([
                MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaContactPoint,  # noqa: E501
                sob.Dictionary
            ])
        )
    ),
    (
        'theme',
        sob.Property(
            types=sob.MutableTypes([
                MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaTheme  # noqa: E501
            ])
        )
    ),
    (
        'keyword',
        sob.Property(
            types=sob.MutableTypes([
                MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaKeyword  # noqa: E501
            ])
        )
    ),
    (
        'distribution',
        sob.Property(
            types=sob.MutableTypes([
                MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaDistribution  # noqa: E501
            ])
        )
    ),
    (
        'references',
        sob.Property(
            types=sob.MutableTypes([
                MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaReferences  # noqa: E501
            ])
        )
    ),
    (
        'archive_exclude',
        sob.BooleanProperty(
            name="archiveExclude"
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaBureauCode  # noqa: E501
).item_types = sob.MutableTypes([
    sob.StringProperty()
])
sob.get_writable_object_meta(  # type: ignore
    MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaContactPoint  # noqa: E501
).properties = sob.Properties([
    (
        'type_',
        sob.EnumeratedProperty(
            name="@type",
            types=sob.Types([
                str
            ]),
            values={
                "vcard:Contact"
            }
        )
    ),
    ('fn', sob.StringProperty()),
    (
        'has_email',
        sob.StringProperty(
            name="hasEmail"
        )
    ),
    (
        'has_url',
        sob.StringProperty(
            name="hasURL"
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaDistribution  # noqa: E501
).item_types = sob.MutableTypes([
    MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaDistributionItem  # noqa: E501
])
sob.get_writable_object_meta(  # type: ignore
    MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaDistributionItem  # noqa: E501
).properties = sob.Properties([
    (
        'type_',
        sob.StringProperty(
            name="@type"
        )
    ),
    ('title', sob.StringProperty()),
    ('description', sob.StringProperty()),
    (
        'format_',
        sob.StringProperty(
            name="format"
        )
    ),
    (
        'media_type',
        sob.StringProperty(
            name="mediaType"
        )
    ),
    (
        'download_url',
        sob.Property(
            name="downloadURL",
            types=sob.MutableTypes([
                str
            ])
        )
    ),
    (
        'access_url',
        sob.StringProperty(
            name="accessURL"
        )
    ),
    (
        'conforms_to',
        sob.StringProperty(
            name="conformsTo"
        )
    ),
    (
        'described_by',
        sob.StringProperty(
            name="describedBy"
        )
    ),
    (
        'described_by_type',
        sob.StringProperty(
            name="describedByType"
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaKeyword  # noqa: E501
).item_types = sob.MutableTypes([
    sob.StringProperty()
])
sob.get_writable_array_meta(  # type: ignore
    MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaProgramCode  # noqa: E501
).item_types = sob.MutableTypes([
    sob.StringProperty()
])
sob.get_writable_object_meta(  # type: ignore
    MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaPublisher  # noqa: E501
).properties = sob.Properties([
    (
        'type_',
        sob.StringProperty(
            name="@type"
        )
    ),
    ('name', sob.StringProperty()),
    (
        'sub_organization_of',
        sob.StringProperty(
            name="subOrganizationOf"
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaReferences  # noqa: E501
).item_types = sob.MutableTypes([
    sob.StringProperty()
])
sob.get_writable_array_meta(  # type: ignore
    MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaTheme  # noqa: E501
).item_types = sob.MutableTypes([
    sob.StringProperty()
])
sob.get_writable_object_meta(  # type: ignore
    MetastoreSchemasDatasetItemsIdentifierPatchRequest
).properties = sob.Properties([
    (
        'type_',
        sob.StringProperty(
            name="@type"
        )
    ),
    ('title', sob.StringProperty()),
    ('identifier', sob.StringProperty()),
    ('description', sob.StringProperty()),
    (
        'access_level',
        sob.EnumeratedProperty(
            name="accessLevel",
            types=sob.Types([
                str
            ]),
            values={
                "non-public",
                "private",
                "public",
                "restricted public"
            }
        )
    ),
    (
        'rights',
        sob.Property(
            types=sob.MutableTypes([
                sob.StringProperty(),
                sob.Null
            ])
        )
    ),
    (
        'accrual_periodicity',
        sob.EnumeratedProperty(
            name="accrualPeriodicity",
            types=sob.Types([
                str
            ]),
            values={
                "R/P0.33M",
                "R/P0.33W",
                "R/P0.5M",
                "R/P10Y",
                "R/P1D",
                "R/P1M",
                "R/P1W",
                "R/P1Y",
                "R/P2M",
                "R/P2W",
                "R/P2Y",
                "R/P3.5D",
                "R/P3M",
                "R/P3Y",
                "R/P4M",
                "R/P4Y",
                "R/P6M",
                "R/PT1H",
                "R/PT1S",
                "irregular"
            }
        )
    ),
    (
        'described_by',
        sob.StringProperty(
            name="describedBy"
        )
    ),
    (
        'described_by_type',
        sob.StringProperty(
            name="describedByType"
        )
    ),
    ('issued', sob.StringProperty()),
    ('modified', sob.StringProperty()),
    ('released', sob.StringProperty()),
    (
        'next_update_date',
        sob.StringProperty(
            name="nextUpdateDate"
        )
    ),
    (
        'license_',
        sob.StringProperty(
            name="license"
        )
    ),
    ('spatial', sob.StringProperty()),
    ('temporal', sob.StringProperty()),
    (
        'is_part_of',
        sob.StringProperty(
            name="isPartOf"
        )
    ),
    (
        'publisher',
        sob.Property(
            types=sob.MutableTypes([
                MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaPublisher  # noqa: E501
            ])
        )
    ),
    (
        'bureau_code',
        sob.Property(
            name="bureauCode",
            types=sob.MutableTypes([
                MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaBureauCode  # noqa: E501
            ])
        )
    ),
    (
        'program_code',
        sob.Property(
            name="programCode",
            types=sob.MutableTypes([
                MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaProgramCode  # noqa: E501
            ])
        )
    ),
    (
        'contact_point',
        sob.Property(
            name="contactPoint",
            types=sob.MutableTypes([
                MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaContactPoint,  # noqa: E501
                sob.Dictionary
            ])
        )
    ),
    (
        'theme',
        sob.Property(
            types=sob.MutableTypes([
                MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaTheme  # noqa: E501
            ])
        )
    ),
    (
        'keyword',
        sob.Property(
            types=sob.MutableTypes([
                MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaKeyword  # noqa: E501
            ])
        )
    ),
    (
        'distribution',
        sob.Property(
            types=sob.MutableTypes([
                MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaDistribution  # noqa: E501
            ])
        )
    ),
    (
        'references',
        sob.Property(
            types=sob.MutableTypes([
                MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaReferences  # noqa: E501
            ])
        )
    ),
    (
        'archive_exclude',
        sob.BooleanProperty(
            name="archiveExclude"
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaBureauCode  # noqa: E501
).item_types = sob.MutableTypes([
    sob.StringProperty()
])
sob.get_writable_object_meta(  # type: ignore
    MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaContactPoint  # noqa: E501
).properties = sob.Properties([
    (
        'type_',
        sob.EnumeratedProperty(
            name="@type",
            types=sob.Types([
                str
            ]),
            values={
                "vcard:Contact"
            }
        )
    ),
    ('fn', sob.StringProperty()),
    (
        'has_email',
        sob.StringProperty(
            name="hasEmail"
        )
    ),
    (
        'has_url',
        sob.StringProperty(
            name="hasURL"
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaDistribution  # noqa: E501
).item_types = sob.MutableTypes([
    MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaDistributionItem  # noqa: E501
])
sob.get_writable_object_meta(  # type: ignore
    MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaDistributionItem  # noqa: E501
).properties = sob.Properties([
    (
        'type_',
        sob.StringProperty(
            name="@type"
        )
    ),
    ('title', sob.StringProperty()),
    ('description', sob.StringProperty()),
    (
        'format_',
        sob.StringProperty(
            name="format"
        )
    ),
    (
        'media_type',
        sob.StringProperty(
            name="mediaType"
        )
    ),
    (
        'download_url',
        sob.Property(
            name="downloadURL",
            types=sob.MutableTypes([
                str
            ])
        )
    ),
    (
        'access_url',
        sob.StringProperty(
            name="accessURL"
        )
    ),
    (
        'conforms_to',
        sob.StringProperty(
            name="conformsTo"
        )
    ),
    (
        'described_by',
        sob.StringProperty(
            name="describedBy"
        )
    ),
    (
        'described_by_type',
        sob.StringProperty(
            name="describedByType"
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaKeyword  # noqa: E501
).item_types = sob.MutableTypes([
    sob.StringProperty()
])
sob.get_writable_array_meta(  # type: ignore
    MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaProgramCode  # noqa: E501
).item_types = sob.MutableTypes([
    sob.StringProperty()
])
sob.get_writable_object_meta(  # type: ignore
    MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaPublisher  # noqa: E501
).properties = sob.Properties([
    (
        'type_',
        sob.StringProperty(
            name="@type"
        )
    ),
    ('name', sob.StringProperty()),
    (
        'sub_organization_of',
        sob.StringProperty(
            name="subOrganizationOf"
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaReferences  # noqa: E501
).item_types = sob.MutableTypes([
    sob.StringProperty()
])
sob.get_writable_array_meta(  # type: ignore
    MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaTheme  # noqa: E501
).item_types = sob.MutableTypes([
    sob.StringProperty()
])
sob.get_writable_array_meta(  # type: ignore
    MetastoreSchemasSchemaIdItemsGetResponse
).item_types = sob.MutableTypes([
    sob.Dictionary
])
sob.get_writable_array_meta(  # type: ignore
    MetastoreSchemasSchemaIdItemsIdentifierRevisionsGetResponse
).item_types = sob.MutableTypes([
    MetastoreRevision
])
sob.get_writable_object_meta(  # type: ignore
    MetastoreSchemaRevisionPostRequest
).properties = sob.Properties([
    ('message', sob.StringProperty()),
    (
        'state',
        sob.EnumeratedProperty(
            types=sob.Types([
                str
            ]),
            values={
                "archived",
                "draft",
                "hidden",
                "orphaned",
                "published"
            }
        )
    )
])
sob.get_writable_array_meta(  # type: ignore
    SortSearch
).item_types = sob.MutableTypes([
    sob.StringProperty()
])
sob.get_writable_array_meta(  # type: ignore
    SortSearchOrder
).item_types = sob.MutableTypes([
    sob.StringProperty()
])
sob.get_writable_object_meta(  # type: ignore
    SearchGetResponse
).properties = sob.Properties([
    (
        'total',
        sob.Property(
            types=sob.MutableTypes([
                str,
                int
            ])
        )
    ),
    (
        'results',
        sob.Property(
            types=sob.MutableTypes([
                sob.Array,
                sob.Dictionary
            ])
        )
    ),
    (
        'facets',
        sob.Property(
            types=sob.MutableTypes([
                Facets
            ])
        )
    )
])
sob.get_writable_object_meta(  # type: ignore
    SearchFacetsGetResponse
).properties = sob.Properties([
    (
        'facets',
        sob.Property(
            types=sob.MutableTypes([
                Facets
            ])
        )
    ),
    ('time', sob.NumberProperty()),
    (
        'results',
        sob.Property(
            types=sob.MutableTypes([
                sob.Array,
                sob.Dictionary
            ])
        )
    ),
    (
        'total',
        sob.Property(
            types=sob.MutableTypes([
                str,
                int
            ])
        )
    )
])
# The following is used to retain class names when re-generating
# this model from an updated OpenAPI document
_POINTERS_CLASSES: typing.Dict[str, typing.Type[sob.abc.Model]] = {
    "#/components/responses/200JsonOrCsvQueryOk/content/application~1json/schema":  # noqa
    JsonOrCsvQueryOkResponse,
    "#/components/responses/200JsonOrCsvQueryOk/content/application~1json/schema/properties/results":  # noqa
    JsonOrCsvQueryOkResponseResults,
    "#/components/schemas/dataset": Dataset,
    "#/components/schemas/dataset/properties/bureauCode": DatasetBureauCode,
    "#/components/schemas/dataset/properties/contactPoint":
    DatasetContactPoint,
    "#/components/schemas/dataset/properties/distribution":
    DatasetDistributions,
    "#/components/schemas/dataset/properties/distribution/items":
    DatasetDistribution,
    "#/components/schemas/dataset/properties/keyword": DatasetKeyword,
    "#/components/schemas/dataset/properties/programCode": DatasetProgramCode,
    "#/components/schemas/dataset/properties/publisher": DatasetPublisher,
    "#/components/schemas/dataset/properties/references": DatasetReferences,
    "#/components/schemas/dataset/properties/theme": DatasetTheme,
    "#/components/schemas/datasets": Datasets,
    "#/components/schemas/datastoreQuery": DatastoreQuery,
    "#/components/schemas/datastoreQuery/properties/conditions":
    DatastoreQueryConditions,
    "#/components/schemas/datastoreQuery/properties/groupings":
    DatastoreQueryGroupings,
    "#/components/schemas/datastoreQuery/properties/joins":
    DatastoreQueryJoins,
    "#/components/schemas/datastoreQuery/properties/joins/items":
    DatastoreQueryJoinsItem,
    "#/components/schemas/datastoreQuery/properties/properties":
    DatastoreQueryProperties,
    "#/components/schemas/datastoreQuery/properties/properties/items/anyOf/1":
    DatastoreQueryPropertyResource,
    "#/components/schemas/datastoreQuery/properties/properties/items/anyOf/2":
    DatastoreQueryPropertyExpression,
    "#/components/schemas/datastoreQuery/properties/resources":
    DatastoreQueryResources,
    "#/components/schemas/datastoreQuery/properties/resources/items":
    DatastoreQueryResource,
    "#/components/schemas/datastoreQuery/properties/sorts":
    DatastoreQuerySorts,
    "#/components/schemas/datastoreQueryCondition": DatastoreQueryCondition,
    "#/components/schemas/datastoreQueryCondition/properties/value/anyOf/2":
    DatastoreQueryConditionValueAnyOf2,
    "#/components/schemas/datastoreQueryConditionGroup":
    DatastoreQueryConditionGroup,
    "#/components/schemas/datastoreQueryConditionGroup/properties/conditions":
    DatastoreQueryConditionGroupConditions,
    "#/components/schemas/datastoreQueryExpression": DatastoreQueryExpression,
    "#/components/schemas/datastoreQueryExpression/properties/operands":
    DatastoreQueryExpressionOperands,
    "#/components/schemas/datastoreQueryExpression/properties/operands/items/anyOf/3":  # noqa
    DatastoreQueryExpressionOperandsItemAnyOf3,
    "#/components/schemas/datastoreQueryResourceProperty":
    DatastoreQueryResourceProperty,
    "#/components/schemas/datastoreQuerySort": DatastoreQuerySort,
    "#/components/schemas/datastoreResourceQuery": DatastoreResourceQuery,
    "#/components/schemas/datastoreResourceQuery/properties/conditions":
    DatastoreResourceQueryConditions,
    "#/components/schemas/datastoreResourceQuery/properties/groupings":
    DatastoreResourceQueryGroupings,
    "#/components/schemas/datastoreResourceQuery/properties/properties":
    DatastoreResourceQueryProperties,
    "#/components/schemas/datastoreResourceQuery/properties/properties/items/anyOf/1":  # noqa
    DatastoreResourceQueryPropertiesItemAnyOf1,
    "#/components/schemas/datastoreResourceQuery/properties/properties/items/anyOf/2":  # noqa
    DatastoreResourceQueryPropertiesItemAnyOf2,
    "#/components/schemas/datastoreResourceQuery/properties/sorts":
    DatastoreResourceQuerySorts,
    "#/components/schemas/errorResponse": ErrorResponse,
    "#/components/schemas/facets": Facets,
    "#/components/schemas/facets/items": FacetsItem,
    "#/components/schemas/harvestPlan": HarvestPlan,
    "#/components/schemas/harvestPlan/properties/extract": HarvestPlanExtract,
    "#/components/schemas/harvestPlan/properties/load": HarvestPlanLoad,
    "#/components/schemas/metastoreNewRevision": MetastoreNewRevision,
    "#/components/schemas/metastoreRevision": MetastoreRevision,
    "#/components/schemas/metastoreWriteResponse": MetastoreWriteResponse,
    "#/paths/~1datastore~1imports/post/requestBody/content/application~1json/schema":  # noqa
    DatastoreImportsPostRequest,
    "#/paths/~1datastore~1imports~1{identifier}/delete/responses/200/content/application~1json/schema":  # noqa
    DatastoreImportDeleteResponse,
    "#/paths/~1datastore~1imports~1{identifier}/get/responses/200/content/application~1json/schema":  # noqa
    DatastoreImportGetResponse,
    "#/paths/~1datastore~1sql/get/responses/200/content/application~1json/schema":  # noqa
    DatastoreSqlGetResponse,
    "#/paths/~1harvest~1plans/get/responses/200/content/application~1json/schema":  # noqa
    HarvestPlansGetResponse,
    "#/paths/~1harvest~1plans/post/responses/200/content/application~1json/schema":  # noqa
    HarvestPlansPostResponse,
    "#/paths/~1harvest~1runs/get/responses/200/content/application~1json/schema":  # noqa
    HarvestRunsGetResponse,
    "#/paths/~1harvest~1runs/post/requestBody/content/application~1json/schema":  # noqa
    HarvestRunsPostRequest,
    "#/paths/~1harvest~1runs/post/responses/200/content/application~1json/schema":  # noqa
    HarvestRunsPostResponse,
    "#/paths/~1metastore~1schemas~1dataset~1items/patch/requestBody/content/application~1json/schema":  # noqa
    MetastoreSchemasDatasetItemsPatchRequest,
    "#/paths/~1metastore~1schemas~1dataset~1items/patch/requestBody/content/application~1json/schema/properties/bureauCode":  # noqa
    MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaBureauCode,  # noqa
    "#/paths/~1metastore~1schemas~1dataset~1items/patch/requestBody/content/application~1json/schema/properties/contactPoint":  # noqa
    MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaContactPoint,  # noqa
    "#/paths/~1metastore~1schemas~1dataset~1items/patch/requestBody/content/application~1json/schema/properties/distribution":  # noqa
    MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaDistribution,  # noqa
    "#/paths/~1metastore~1schemas~1dataset~1items/patch/requestBody/content/application~1json/schema/properties/distribution/items":  # noqa
    MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaDistributionItem,  # noqa
    "#/paths/~1metastore~1schemas~1dataset~1items/patch/requestBody/content/application~1json/schema/properties/keyword":  # noqa
    MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaKeyword,  # noqa
    "#/paths/~1metastore~1schemas~1dataset~1items/patch/requestBody/content/application~1json/schema/properties/programCode":  # noqa
    MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaProgramCode,  # noqa
    "#/paths/~1metastore~1schemas~1dataset~1items/patch/requestBody/content/application~1json/schema/properties/publisher":  # noqa
    MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaPublisher,  # noqa
    "#/paths/~1metastore~1schemas~1dataset~1items/patch/requestBody/content/application~1json/schema/properties/references":  # noqa
    MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaReferences,  # noqa
    "#/paths/~1metastore~1schemas~1dataset~1items/patch/requestBody/content/application~1json/schema/properties/theme":  # noqa
    MetastoreSchemasDatasetItemsPatchRequestBodyContentApplicationJsonSchemaTheme,  # noqa
    "#/paths/~1metastore~1schemas~1dataset~1items~1{identifier}/patch/requestBody/content/application~1json/schema":  # noqa
    MetastoreSchemasDatasetItemsIdentifierPatchRequest,
    "#/paths/~1metastore~1schemas~1dataset~1items~1{identifier}/patch/requestBody/content/application~1json/schema/properties/bureauCode":  # noqa
    MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaBureauCode,  # noqa
    "#/paths/~1metastore~1schemas~1dataset~1items~1{identifier}/patch/requestBody/content/application~1json/schema/properties/contactPoint":  # noqa
    MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaContactPoint,  # noqa
    "#/paths/~1metastore~1schemas~1dataset~1items~1{identifier}/patch/requestBody/content/application~1json/schema/properties/distribution":  # noqa
    MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaDistribution,  # noqa
    "#/paths/~1metastore~1schemas~1dataset~1items~1{identifier}/patch/requestBody/content/application~1json/schema/properties/distribution/items":  # noqa
    MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaDistributionItem,  # noqa
    "#/paths/~1metastore~1schemas~1dataset~1items~1{identifier}/patch/requestBody/content/application~1json/schema/properties/keyword":  # noqa
    MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaKeyword,  # noqa
    "#/paths/~1metastore~1schemas~1dataset~1items~1{identifier}/patch/requestBody/content/application~1json/schema/properties/programCode":  # noqa
    MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaProgramCode,  # noqa
    "#/paths/~1metastore~1schemas~1dataset~1items~1{identifier}/patch/requestBody/content/application~1json/schema/properties/publisher":  # noqa
    MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaPublisher,  # noqa
    "#/paths/~1metastore~1schemas~1dataset~1items~1{identifier}/patch/requestBody/content/application~1json/schema/properties/references":  # noqa
    MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaReferences,  # noqa
    "#/paths/~1metastore~1schemas~1dataset~1items~1{identifier}/patch/requestBody/content/application~1json/schema/properties/theme":  # noqa
    MetastoreSchemasDatasetItemsIdentifierPatchRequestBodyContentApplicationJsonSchemaTheme,  # noqa
    "#/paths/~1metastore~1schemas~1{schema_id}~1items/get/responses/200/content/application~1json/schema":  # noqa
    MetastoreSchemasSchemaIdItemsGetResponse,
    "#/paths/~1metastore~1schemas~1{schema_id}~1items~1{identifier}~1revisions/get/responses/200/content/application~1json/schema":  # noqa
    MetastoreSchemasSchemaIdItemsIdentifierRevisionsGetResponse,
    "#/paths/~1metastore~1schemas~1{schema_id}~1items~1{identifier}~1revisions/post/requestBody/content/application~1json/schema":  # noqa
    MetastoreSchemaRevisionPostRequest,
    "#/paths/~1search/get/parameters/3/schema": SortSearch,
    "#/paths/~1search/get/parameters/4/schema": SortSearchOrder,
    "#/paths/~1search/get/responses/200/content/application~1json/schema":
    SearchGetResponse,
    "#/paths/~1search~1facets/get/responses/200/content/application~1json/schema":  # noqa
    SearchFacetsGetResponse,
}
