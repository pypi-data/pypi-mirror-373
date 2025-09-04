import sgqlc.types

api_schema = sgqlc.types.Schema()


########################################################################
# Scalars and Enumerations
########################################################################
class AccessLevelSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("id", "name", "order")


class AccountSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = (
        "creator",
        "id",
        "lastUpdater",
        "name",
        "platformId",
        "systemRegistrationDate",
        "systemUpdateDate",
        "url",
    )


class AutocompleteConceptDestination(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("markers",)


class AutocompleteDocumentDestination(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("links", "markers")


Boolean = sgqlc.types.Boolean


class BulkType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("account", "concept", "document", "issue", "map", "platform")


class ComponentView(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("keyValue", "value")


class CompositeConceptTypeSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("id", "name")


class CompositeConceptTypeWidgetTypeSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("id", "name", "order")


class CompositePropertyTypeSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("id", "name", "registrationDate")


class CompositePropertyValueTemplateSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("id", "name", "registrationDate")


class ConceptLinkTypeSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("conceptType", "id", "name")


class ConceptPropertyTypeSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("name", "registrationDate")


class ConceptPropertyValueTypeSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("dictionary", "id", "name", "regexp", "valueType")


class ConceptSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = (
        "accessLevel",
        "conceptAndDocumentLink",
        "conceptLink",
        "creator",
        "documentLink",
        "id",
        "name",
        "score",
        "systemRegistrationDate",
        "systemUpdateDate",
    )


class ConceptTypeLinkMetadata(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = (
        "creator",
        "endDate",
        "lastUpdater",
        "linkType",
        "registrationDate",
        "startDate",
        "updateDate",
    )


class ConceptTypeMetadata(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = (
        "concept",
        "conceptType",
        "creator",
        "endDate",
        "lastUpdater",
        "markers",
        "name",
        "notes",
        "startDate",
        "systemRegistrationDate",
        "systemUpdateDate",
    )


class ConceptTypeSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("dictionary", "id", "name", "regexp")


class ConceptUpdate(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("link", "linkProperty", "metadata", "property")


class ConceptVariant(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("event", "obj")


class CountryTarget(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("account", "platform")


class DocumentFeedMode(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("all", "deleted", "favorites")


class DocumentFeedSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = (
        "creator",
        "id",
        "lastUpdater",
        "name",
        "systemRegistrationDate",
        "systemUpdateDate",
    )


class DocumentGrouping(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("none", "story")


class DocumentSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = (
        "conceptLink",
        "id",
        "publicationDate",
        "registrationDate",
        "score",
        "text",
        "title",
        "trustLevel",
        "updateDate",
    )


class DocumentSourceType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("external", "internal")


class DocumentType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("image", "text")


class ElementType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("blackList", "whiteList")


class FactStatus(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("approved", "autoApproved", "declined", "hidden", "new")


Float = sgqlc.types.Float

ID = sgqlc.types.ID

Int = sgqlc.types.Int


class IssuePriority(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("High", "Low", "Medium")


class IssueSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = (
        "creator",
        "executor",
        "id",
        "lastUpdater",
        "priority",
        "registrationDate",
        "status",
        "topic",
        "updateDate",
    )


class IssueStatus(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = (
        "canceled",
        "closed",
        "dataRequested",
        "development",
        "improvementRequested",
        "open",
        "reviewRequested",
    )


class LinkDirection(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("in", "out", "undirected")


class Locale(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("eng", "other", "ru")


class Long(sgqlc.types.Scalar):
    __schema__ = api_schema


class NodeType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = (
        "header",
        "image",
        "json",
        "key",
        "list",
        "other",
        "row",
        "table",
        "text",
    )


class PlatformSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = (
        "creator",
        "id",
        "lastUpdater",
        "name",
        "platformType",
        "systemRegistrationDate",
        "systemUpdateDate",
        "url",
    )


class PlatformType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = (
        "blog",
        "database",
        "fileStorage",
        "forum",
        "media",
        "messenger",
        "newsAggregator",
        "procurement",
        "review",
        "socialNetwork",
    )


class PropLinkOrConcept(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("concept", "link")


class RedmineIssueType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("concept", "document")


class ResearchMapSorting(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = (
        "accessLevel",
        "conceptAndDocumentLink",
        "conceptLink",
        "creator",
        "documentLink",
        "id",
        "lastUpdater",
        "name",
        "systemRegistrationDate",
        "systemUpdateDate",
    )


class SortDirection(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("ascending", "descending")


String = sgqlc.types.String


class TrustLevel(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("high", "low", "medium")


class UnixTime(sgqlc.types.Scalar):
    __schema__ = api_schema


class Upload(sgqlc.types.Scalar):
    __schema__ = api_schema


class ValueType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("Date", "Double", "Geo", "Int", "Link", "String", "StringLocale")


class WidgetTypeTableType(sgqlc.types.Enum):
    __schema__ = api_schema
    __choices__ = ("horizontal", "vertical")


########################################################################
# Input Objects
########################################################################
class AccessLevelCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("name", "order")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    order = sgqlc.types.Field(Long, graphql_name="order")


class AccessLevelUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("name",)
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")


class AccountCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "platform_id",
        "name",
        "id",
        "url",
        "country",
        "markers",
        "params",
    )
    platform_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="platformId")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="url")
    country = sgqlc.types.Field(String, graphql_name="country")
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="markers")
    params = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("ParameterInput")),
        graphql_name="params",
    )


class AccountFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "search_string",
        "platform_id",
        "id",
        "country",
        "markers",
        "creator",
        "last_updater",
        "registration_date",
        "update_date",
    )
    search_string = sgqlc.types.Field(String, graphql_name="searchString")
    platform_id = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="platformId")
    id = sgqlc.types.Field(ID, graphql_name="id")
    country = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="country")
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="markers")
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="creator")
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="lastUpdater")
    registration_date = sgqlc.types.Field("TimestampInterval", graphql_name="registrationDate")
    update_date = sgqlc.types.Field("TimestampInterval", graphql_name="updateDate")


class AccountGetOrCreateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("id", "platform_id", "name", "url")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    platform_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="platformId")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="url")


class AccountUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "account_id",
        "platform_id",
        "name",
        "new_id",
        "url",
        "country",
        "markers",
        "params",
    )
    account_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="accountId")
    platform_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="platformId")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    new_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="newId")
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="url")
    country = sgqlc.types.Field(String, graphql_name="country")
    markers = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="markers",
    )
    params = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ParameterInput"))),
        graphql_name="params",
    )


class AliasCreateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("concept_id", "value")
    concept_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptId")
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="value")


class BulkMarkersInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("ids", "bulk_type")
    ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
        graphql_name="ids",
    )
    bulk_type = sgqlc.types.Field(sgqlc.types.non_null(BulkType), graphql_name="bulkType")


class BulkMarkersUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("ids", "bulk_type", "markers_to_delete", "markers_to_add")
    ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
        graphql_name="ids",
    )
    bulk_type = sgqlc.types.Field(sgqlc.types.non_null(BulkType), graphql_name="bulkType")
    markers_to_delete = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="markersToDelete",
    )
    markers_to_add = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="markersToAdd",
    )


class Comment2IssueInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("id_issue", "comment")
    id_issue = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="idIssue")
    comment = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="comment")


class ComponentValueInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("id", "value")
    id = sgqlc.types.Field(ID, graphql_name="id")
    value = sgqlc.types.Field(sgqlc.types.non_null("ValueInput"), graphql_name="value")


class CompositeConceptFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "property_filter_settings",
        "link_filter_settings",
        "concept_variant",
        "name",
        "exact_name",
        "substring",
        "access_level_id",
        "creator",
        "last_updater",
        "creation_date",
        "update_date",
        "markers",
        "has_linked_issues",
        "composite_concept_type_ids",
    )
    property_filter_settings = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("PropertyFilterSettings")),
        graphql_name="propertyFilterSettings",
    )
    link_filter_settings = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("LinkFilterSettings")),
        graphql_name="linkFilterSettings",
    )
    concept_variant = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(ConceptVariant)),
        graphql_name="conceptVariant",
    )
    name = sgqlc.types.Field(String, graphql_name="name")
    exact_name = sgqlc.types.Field(String, graphql_name="exactName")
    substring = sgqlc.types.Field(String, graphql_name="substring")
    access_level_id = sgqlc.types.Field(ID, graphql_name="accessLevelId")
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="creator")
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="lastUpdater")
    creation_date = sgqlc.types.Field("TimestampInterval", graphql_name="creationDate")
    update_date = sgqlc.types.Field("TimestampInterval", graphql_name="updateDate")
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="markers")
    has_linked_issues = sgqlc.types.Field(Boolean, graphql_name="hasLinkedIssues")
    composite_concept_type_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
        graphql_name="compositeConceptTypeIds",
    )


class CompositeConceptTypeCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "name",
        "root_concept_type_id",
        "is_default",
        "layout",
        "has_supporting_documents",
        "has_header_information",
        "show_in_menu",
    )
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    root_concept_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="rootConceptTypeId")
    is_default = sgqlc.types.Field(Boolean, graphql_name="isDefault")
    layout = sgqlc.types.Field(String, graphql_name="layout")
    has_supporting_documents = sgqlc.types.Field(Boolean, graphql_name="hasSupportingDocuments")
    has_header_information = sgqlc.types.Field(Boolean, graphql_name="hasHeaderInformation")
    show_in_menu = sgqlc.types.Field(Boolean, graphql_name="showInMenu")


class CompositeConceptTypeFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "name",
        "creator",
        "last_updater",
        "registration_date",
        "update_date",
    )
    name = sgqlc.types.Field(String, graphql_name="name")
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="creator")
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="lastUpdater")
    registration_date = sgqlc.types.Field("TimestampInterval", graphql_name="registrationDate")
    update_date = sgqlc.types.Field("TimestampInterval", graphql_name="updateDate")


class CompositeConceptTypeUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "name",
        "is_default",
        "layout",
        "has_supporting_documents",
        "has_header_information",
        "show_in_menu",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    is_default = sgqlc.types.Field(Boolean, graphql_name="isDefault")
    layout = sgqlc.types.Field(String, graphql_name="layout")
    has_supporting_documents = sgqlc.types.Field(Boolean, graphql_name="hasSupportingDocuments")
    has_header_information = sgqlc.types.Field(Boolean, graphql_name="hasHeaderInformation")
    show_in_menu = sgqlc.types.Field(Boolean, graphql_name="showInMenu")


class CompositeConceptTypeViewInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("concept_type_id", "composite_concept_type_id")
    concept_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptTypeId")
    composite_concept_type_id = sgqlc.types.Field(ID, graphql_name="compositeConceptTypeId")


class CompositeConceptTypeWidgetTypeColumnInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "name",
        "is_main_properties",
        "list_values",
        "concept_link_type_ids_path",
        "sort_by_column",
        "sort_direction",
        "value_info",
    )
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    is_main_properties = sgqlc.types.Field(Boolean, graphql_name="isMainProperties")
    list_values = sgqlc.types.Field(Boolean, graphql_name="listValues")
    concept_link_type_ids_path = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(ID)),
        graphql_name="conceptLinkTypeIdsPath",
    )
    sort_by_column = sgqlc.types.Field(Boolean, graphql_name="sortByColumn")
    sort_direction = sgqlc.types.Field(SortDirection, graphql_name="sortDirection")
    value_info = sgqlc.types.Field(
        sgqlc.types.non_null("CompositeConceptTypeWidgetTypeColumnValueInfoInput"),
        graphql_name="valueInfo",
    )


class CompositeConceptTypeWidgetTypeColumnValueInfoInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "property_type_id",
        "metadata",
        "link_property_type_id",
        "link_metadata",
    )
    property_type_id = sgqlc.types.Field(ID, graphql_name="propertyTypeId")
    metadata = sgqlc.types.Field(ConceptTypeMetadata, graphql_name="metadata")
    link_property_type_id = sgqlc.types.Field(ID, graphql_name="linkPropertyTypeId")
    link_metadata = sgqlc.types.Field(ConceptTypeLinkMetadata, graphql_name="linkMetadata")


class CompositeConceptTypeWidgetTypeCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("name", "table_type", "composite_concept_type_id", "columns")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    table_type = sgqlc.types.Field(sgqlc.types.non_null(WidgetTypeTableType), graphql_name="tableType")
    composite_concept_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="compositeConceptTypeId")
    columns = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CompositeConceptTypeWidgetTypeColumnInput))),
        graphql_name="columns",
    )


class CompositeConceptTypeWidgetTypeUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("id", "name", "table_type", "columns")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    table_type = sgqlc.types.Field(sgqlc.types.non_null(WidgetTypeTableType), graphql_name="tableType")
    columns = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CompositeConceptTypeWidgetTypeColumnInput))),
        graphql_name="columns",
    )


class CompositeConceptTypeWidgetTypeUpdateOrderInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("composite_concept_type_id", "ids")
    composite_concept_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="compositeConceptTypeId")
    ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
        graphql_name="ids",
    )


class CompositePropertyTypeFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("name", "concept_type_id", "link_type_id")
    name = sgqlc.types.Field(String, graphql_name="name")
    concept_type_id = sgqlc.types.Field(ID, graphql_name="conceptTypeId")
    link_type_id = sgqlc.types.Field(ID, graphql_name="linkTypeId")


class CompositePropertyValueTemplateCreateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("id", "name", "component_value_types")
    id = sgqlc.types.Field(ID, graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    component_value_types = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("NamedValueType"))),
        graphql_name="componentValueTypes",
    )


class CompositePropertyValueTemplateFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "name",
        "creator",
        "last_updater",
        "registration_date",
        "update_date",
    )
    name = sgqlc.types.Field(String, graphql_name="name")
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="creator")
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="lastUpdater")
    registration_date = sgqlc.types.Field("TimestampInterval", graphql_name="registrationDate")
    update_date = sgqlc.types.Field("TimestampInterval", graphql_name="updateDate")


class Concept2IssueInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("id_issue", "concept_ids", "comment")
    id_issue = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="idIssue")
    concept_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
        graphql_name="conceptIds",
    )
    comment = sgqlc.types.Field(String, graphql_name="comment")


class ConceptAddImplicitLinkInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("first_concept_id", "second_concept_id")
    first_concept_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="firstConceptId")
    second_concept_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="secondConceptId")


class ConceptAddInputInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("concept_id", "x_coordinate", "y_coordinate", "group_id")
    concept_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptId")
    x_coordinate = sgqlc.types.Field(Float, graphql_name="xCoordinate")
    y_coordinate = sgqlc.types.Field(Float, graphql_name="yCoordinate")
    group_id = sgqlc.types.Field(ID, graphql_name="groupId")


class ConceptCandidateAddInputInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("document_id", "group_id")
    document_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="documentId")
    group_id = sgqlc.types.Field(ID, graphql_name="groupId")


class ConceptCandidateMoveInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("concept_candidate_id", "x_coordinate", "y_coordinate")
    concept_candidate_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptCandidateId")
    x_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="xCoordinate")
    y_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="yCoordinate")


class ConceptExtraSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("search_on_map", "selected_content")
    search_on_map = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="searchOnMap")
    selected_content = sgqlc.types.Field("ResearchMapSelectedContent", graphql_name="selectedContent")


class ConceptFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "property_filter_settings",
        "link_filter_settings",
        "concept_type_ids",
        "concept_variant",
        "name",
        "exact_name",
        "substring",
        "access_level_id",
        "creator",
        "last_updater",
        "creation_date",
        "update_date",
        "markers",
        "has_linked_issues",
    )
    property_filter_settings = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("PropertyFilterSettings")),
        graphql_name="propertyFilterSettings",
    )
    link_filter_settings = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("LinkFilterSettings")),
        graphql_name="linkFilterSettings",
    )
    concept_type_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="conceptTypeIds")
    concept_variant = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(ConceptVariant)),
        graphql_name="conceptVariant",
    )
    name = sgqlc.types.Field(String, graphql_name="name")
    exact_name = sgqlc.types.Field(String, graphql_name="exactName")
    substring = sgqlc.types.Field(String, graphql_name="substring")
    access_level_id = sgqlc.types.Field(ID, graphql_name="accessLevelId")
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="creator")
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="lastUpdater")
    creation_date = sgqlc.types.Field("TimestampInterval", graphql_name="creationDate")
    update_date = sgqlc.types.Field("TimestampInterval", graphql_name="updateDate")
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="markers")
    has_linked_issues = sgqlc.types.Field(Boolean, graphql_name="hasLinkedIssues")


class ConceptLinkCreationMutationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "concept_from_id",
        "concept_to_id",
        "link_type_id",
        "notes",
        "fact_info",
        "start_date",
        "end_date",
        "access_level_id",
    )
    concept_from_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptFromId")
    concept_to_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptToId")
    link_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="linkTypeId")
    notes = sgqlc.types.Field(String, graphql_name="notes")
    fact_info = sgqlc.types.Field("FactInput", graphql_name="factInfo")
    start_date = sgqlc.types.Field("DateTimeValueInput", graphql_name="startDate")
    end_date = sgqlc.types.Field("DateTimeValueInput", graphql_name="endDate")
    access_level_id = sgqlc.types.Field(ID, graphql_name="accessLevelId")


class ConceptLinkFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("is_event", "concept_link_type", "document_id")
    is_event = sgqlc.types.Field(Boolean, graphql_name="isEvent")
    concept_link_type = sgqlc.types.Field(ID, graphql_name="conceptLinkType")
    document_id = sgqlc.types.Field(ID, graphql_name="documentId")


class ConceptLinkPropertyInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "property_type_id",
        "fact_info",
        "notes",
        "value_input",
        "computable_value",
        "link_id",
        "is_main",
        "start_date",
        "end_date",
    )
    property_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="propertyTypeId")
    fact_info = sgqlc.types.Field("FactInput", graphql_name="factInfo")
    notes = sgqlc.types.Field(String, graphql_name="notes")
    value_input = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ComponentValueInput))),
        graphql_name="valueInput",
    )
    computable_value = sgqlc.types.Field(String, graphql_name="computableValue")
    link_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="linkId")
    is_main = sgqlc.types.Field(Boolean, graphql_name="isMain")
    start_date = sgqlc.types.Field("DateTimeValueInput", graphql_name="startDate")
    end_date = sgqlc.types.Field("DateTimeValueInput", graphql_name="endDate")


class ConceptLinkPropertyTypeCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "link_type_id",
        "name",
        "value_type_id",
        "computable_formula",
        "pretrained_rel_ext_models",
        "notify_on_update",
    )
    link_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="linkTypeId")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    value_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="valueTypeId")
    computable_formula = sgqlc.types.Field(String, graphql_name="computableFormula")
    pretrained_rel_ext_models = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("RelExtModelInput")),
        graphql_name="pretrainedRelExtModels",
    )
    notify_on_update = sgqlc.types.Field(Boolean, graphql_name="notifyOnUpdate")


class ConceptLinkPropertyTypeUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "name",
        "value_type_id",
        "computable_formula",
        "pretrained_rel_ext_models",
        "notify_on_update",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    value_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="valueTypeId")
    computable_formula = sgqlc.types.Field(String, graphql_name="computableFormula")
    pretrained_rel_ext_models = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("RelExtModelInput")),
        graphql_name="pretrainedRelExtModels",
    )
    notify_on_update = sgqlc.types.Field(Boolean, graphql_name="notifyOnUpdate")


class ConceptLinkTypeCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "name",
        "is_directed",
        "is_hierarchical",
        "concept_from_type_id",
        "concept_to_type_id",
        "pretrained_rel_ext_models",
        "notify_on_update",
    )
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    is_directed = sgqlc.types.Field(Boolean, graphql_name="isDirected")
    is_hierarchical = sgqlc.types.Field(Boolean, graphql_name="isHierarchical")
    concept_from_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptFromTypeId")
    concept_to_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptToTypeId")
    pretrained_rel_ext_models = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("RelExtModelInput")),
        graphql_name="pretrainedRelExtModels",
    )
    notify_on_update = sgqlc.types.Field(Boolean, graphql_name="notifyOnUpdate")


class ConceptLinkTypeFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "name",
        "concept_from_type_id",
        "concept_to_type_id",
        "concept_type_and_event_filter",
        "is_directed",
        "is_hierarchical",
        "creator",
        "last_updater",
        "registration_date",
        "update_date",
        "has_rel_ext_models",
    )
    name = sgqlc.types.Field(String, graphql_name="name")
    concept_from_type_id = sgqlc.types.Field(ID, graphql_name="conceptFromTypeId")
    concept_to_type_id = sgqlc.types.Field(ID, graphql_name="conceptToTypeId")
    concept_type_and_event_filter = sgqlc.types.Field("conceptTypeAndEventFilter", graphql_name="conceptTypeAndEventFilter")
    is_directed = sgqlc.types.Field(Boolean, graphql_name="isDirected")
    is_hierarchical = sgqlc.types.Field(Boolean, graphql_name="isHierarchical")
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="creator")
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="lastUpdater")
    registration_date = sgqlc.types.Field("TimestampInterval", graphql_name="registrationDate")
    update_date = sgqlc.types.Field("TimestampInterval", graphql_name="updateDate")
    has_rel_ext_models = sgqlc.types.Field(Boolean, graphql_name="hasRelExtModels")


class ConceptLinkTypeUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "name",
        "concept_from_type_id",
        "concept_to_type_id",
        "pretrained_rel_ext_models",
        "is_directed",
        "is_hierarchical",
        "notify_on_update",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    concept_from_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptFromTypeId")
    concept_to_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptToTypeId")
    pretrained_rel_ext_models = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("RelExtModelInput")),
        graphql_name="pretrainedRelExtModels",
    )
    is_directed = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isDirected")
    is_hierarchical = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isHierarchical")
    notify_on_update = sgqlc.types.Field(Boolean, graphql_name="notifyOnUpdate")


class ConceptLinkUpdateMutationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("id", "notes", "start_date", "end_date", "access_level_id")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    notes = sgqlc.types.Field(String, graphql_name="notes")
    start_date = sgqlc.types.Field("DateTimeValueInput", graphql_name="startDate")
    end_date = sgqlc.types.Field("DateTimeValueInput", graphql_name="endDate")
    access_level_id = sgqlc.types.Field(ID, graphql_name="accessLevelId")


class ConceptMentionCountBatchInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("inputs", "limit", "extend_results")
    inputs = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptMentionCountInput"))),
        graphql_name="inputs",
    )
    limit = sgqlc.types.Field(Int, graphql_name="limit")
    extend_results = sgqlc.types.Field(Boolean, graphql_name="extendResults")


class ConceptMentionCountInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("term", "concept_types")
    term = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="term")
    concept_types = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="conceptTypes")


class ConceptMergeInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("main_concept_id", "merged_concept_id")
    main_concept_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="mainConceptId")
    merged_concept_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="mergedConceptId")


class ConceptMoveInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("concept_id", "x_coordinate", "y_coordinate")
    concept_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptId")
    x_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="xCoordinate")
    y_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="yCoordinate")


class ConceptMutationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "name",
        "concept_type_id",
        "notes",
        "fact_info",
        "markers",
        "access_level_id",
        "start_date",
        "end_date",
    )
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    concept_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptTypeId")
    notes = sgqlc.types.Field(String, graphql_name="notes")
    fact_info = sgqlc.types.Field("FactInput", graphql_name="factInfo")
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="markers")
    access_level_id = sgqlc.types.Field(ID, graphql_name="accessLevelId")
    start_date = sgqlc.types.Field("DateTimeValueInput", graphql_name="startDate")
    end_date = sgqlc.types.Field("DateTimeValueInput", graphql_name="endDate")


class ConceptPropertyCreateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "property_type_id",
        "concept_id",
        "value_input",
        "computable_value",
        "fact_info",
        "notes",
        "is_main",
        "start_date",
        "end_date",
    )
    property_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="propertyTypeId")
    concept_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptId")
    value_input = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ComponentValueInput))),
        graphql_name="valueInput",
    )
    computable_value = sgqlc.types.Field(String, graphql_name="computableValue")
    fact_info = sgqlc.types.Field("FactInput", graphql_name="factInfo")
    notes = sgqlc.types.Field(String, graphql_name="notes")
    is_main = sgqlc.types.Field(Boolean, graphql_name="isMain")
    start_date = sgqlc.types.Field("DateTimeValueInput", graphql_name="startDate")
    end_date = sgqlc.types.Field("DateTimeValueInput", graphql_name="endDate")


class ConceptPropertyFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("only_main", "document_id")
    only_main = sgqlc.types.Field(Boolean, graphql_name="onlyMain")
    document_id = sgqlc.types.Field(ID, graphql_name="documentId")


class ConceptPropertyTypeCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "concept_type_id",
        "name",
        "value_type_id",
        "computable_formula",
        "pretrained_rel_ext_models",
        "notify_on_update",
    )
    concept_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptTypeId")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    value_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="valueTypeId")
    computable_formula = sgqlc.types.Field(String, graphql_name="computableFormula")
    pretrained_rel_ext_models = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("RelExtModelInput")),
        graphql_name="pretrainedRelExtModels",
    )
    notify_on_update = sgqlc.types.Field(Boolean, graphql_name="notifyOnUpdate")


class ConceptPropertyTypeFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "name",
        "concept_type_id",
        "concept_link_type_id",
        "concept_value_type_id",
        "value_type",
        "concept_type_from_link_type_id",
    )
    name = sgqlc.types.Field(String, graphql_name="name")
    concept_type_id = sgqlc.types.Field(ID, graphql_name="conceptTypeId")
    concept_link_type_id = sgqlc.types.Field(ID, graphql_name="conceptLinkTypeId")
    concept_value_type_id = sgqlc.types.Field(ID, graphql_name="conceptValueTypeId")
    value_type = sgqlc.types.Field(ValueType, graphql_name="valueType")
    concept_type_from_link_type_id = sgqlc.types.Field(ID, graphql_name="conceptTypeFromLinkTypeId")


class ConceptPropertyTypeUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "name",
        "value_type_id",
        "computable_formula",
        "pretrained_rel_ext_models",
        "notify_on_update",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    value_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="valueTypeId")
    computable_formula = sgqlc.types.Field(String, graphql_name="computableFormula")
    pretrained_rel_ext_models = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("RelExtModelInput")),
        graphql_name="pretrainedRelExtModels",
    )
    notify_on_update = sgqlc.types.Field(Boolean, graphql_name="notifyOnUpdate")


class ConceptPropertyUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "property_id",
        "is_main",
        "notes",
        "computable_value",
        "start_date",
        "end_date",
        "value_input",
    )
    property_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="propertyId")
    is_main = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isMain")
    notes = sgqlc.types.Field(String, graphql_name="notes")
    computable_value = sgqlc.types.Field(String, graphql_name="computableValue")
    start_date = sgqlc.types.Field("DateTimeValueInput", graphql_name="startDate")
    end_date = sgqlc.types.Field("DateTimeValueInput", graphql_name="endDate")
    value_input = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ComponentValueInput))),
        graphql_name="valueInput",
    )


class ConceptPropertyValueTypeCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "name",
        "value_type",
        "pretrained_nercmodels",
        "value_restriction",
    )
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    value_type = sgqlc.types.Field(sgqlc.types.non_null(ValueType), graphql_name="valueType")
    pretrained_nercmodels = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(String)),
        graphql_name="pretrainedNERCModels",
    )
    value_restriction = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(String)),
        graphql_name="valueRestriction",
    )


class ConceptPropertyValueTypeFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "name",
        "value_type",
        "creator",
        "last_updater",
        "registration_date",
        "update_date",
        "regexp_exists",
        "dictionary_exists",
        "pretrained_nercmodels",
    )
    name = sgqlc.types.Field(String, graphql_name="name")
    value_type = sgqlc.types.Field(ValueType, graphql_name="valueType")
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="creator")
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="lastUpdater")
    registration_date = sgqlc.types.Field("TimestampInterval", graphql_name="registrationDate")
    update_date = sgqlc.types.Field("TimestampInterval", graphql_name="updateDate")
    regexp_exists = sgqlc.types.Field(Boolean, graphql_name="regexpExists")
    dictionary_exists = sgqlc.types.Field(Boolean, graphql_name="dictionaryExists")
    pretrained_nercmodels = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(String)),
        graphql_name="pretrainedNERCModels",
    )


class ConceptPropertyValueTypeUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "name",
        "value_type",
        "pretrained_nercmodels",
        "value_restriction",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    value_type = sgqlc.types.Field(sgqlc.types.non_null(ValueType), graphql_name="valueType")
    pretrained_nercmodels = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="pretrainedNERCModels",
    )
    value_restriction = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="valueRestriction",
    )


class ConceptTypeCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "name",
        "x_coordinate",
        "y_coordinate",
        "pretrained_nercmodels",
        "is_event",
        "show_in_menu",
    )
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    x_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="xCoordinate")
    y_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="yCoordinate")
    pretrained_nercmodels = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(String)),
        graphql_name="pretrainedNERCModels",
    )
    is_event = sgqlc.types.Field(Boolean, graphql_name="isEvent")
    show_in_menu = sgqlc.types.Field(Boolean, graphql_name="showInMenu")


class ConceptTypeFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "name",
        "is_event",
        "creator",
        "last_updater",
        "registration_date",
        "update_date",
        "regexp_exists",
        "dictionary_exists",
        "pretrained_nercmodels",
    )
    name = sgqlc.types.Field(String, graphql_name="name")
    is_event = sgqlc.types.Field(Boolean, graphql_name="isEvent")
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="creator")
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="lastUpdater")
    registration_date = sgqlc.types.Field("TimestampInterval", graphql_name="registrationDate")
    update_date = sgqlc.types.Field("TimestampInterval", graphql_name="updateDate")
    regexp_exists = sgqlc.types.Field(Boolean, graphql_name="regexpExists")
    dictionary_exists = sgqlc.types.Field(Boolean, graphql_name="dictionaryExists")
    pretrained_nercmodels = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(String)),
        graphql_name="pretrainedNERCModels",
    )


class ConceptTypeUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "x_coordinate",
        "y_coordinate",
        "name",
        "pretrained_nercmodels",
        "is_event",
        "show_in_menu",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    x_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="xCoordinate")
    y_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="yCoordinate")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    pretrained_nercmodels = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(String)),
        graphql_name="pretrainedNERCModels",
    )
    is_event = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isEvent")
    show_in_menu = sgqlc.types.Field(Boolean, graphql_name="showInMenu")


class ConceptTypeViewCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("concept_type_id", "name", "show_in_menu", "columns")
    concept_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptTypeId")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    show_in_menu = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="showInMenu")
    columns = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CompositeConceptTypeWidgetTypeColumnInput))),
        graphql_name="columns",
    )


class ConceptTypeViewUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("id", "name", "show_in_menu", "columns")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    show_in_menu = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="showInMenu")
    columns = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CompositeConceptTypeWidgetTypeColumnInput))),
        graphql_name="columns",
    )


class ConceptUnmergeInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("main_concept_id", "merged_concept_id")
    main_concept_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="mainConceptId")
    merged_concept_id = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
        graphql_name="mergedConceptId",
    )


class ConceptUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "concept_id",
        "name",
        "concept_type_id",
        "notes",
        "document_input",
        "markers",
        "access_level_id",
        "start_date",
        "end_date",
    )
    concept_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptId")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    concept_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptTypeId")
    notes = sgqlc.types.Field(String, graphql_name="notes")
    document_input = sgqlc.types.Field("FactInput", graphql_name="documentInput")
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="markers")
    access_level_id = sgqlc.types.Field(ID, graphql_name="accessLevelId")
    start_date = sgqlc.types.Field("DateTimeValueInput", graphql_name="startDate")
    end_date = sgqlc.types.Field("DateTimeValueInput", graphql_name="endDate")


class Coordinate(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("x", "y")
    x = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="x")
    y = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="y")


class CoordinatesInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("latitude", "longitude")
    latitude = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="latitude")
    longitude = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="longitude")


class CountryFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("search_string", "target")
    search_string = sgqlc.types.Field(String, graphql_name="searchString")
    target = sgqlc.types.Field(CountryTarget, graphql_name="target")


class DateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("year", "month", "day")
    year = sgqlc.types.Field(Int, graphql_name="year")
    month = sgqlc.types.Field(Int, graphql_name="month")
    day = sgqlc.types.Field(Int, graphql_name="day")


class DateTimeIntervalInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("start", "end")
    start = sgqlc.types.Field("DateTimeValueInput", graphql_name="start")
    end = sgqlc.types.Field("DateTimeValueInput", graphql_name="end")


class DateTimeIntervalPairInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("start", "end")
    start = sgqlc.types.Field(sgqlc.types.non_null(DateTimeIntervalInput), graphql_name="start")
    end = sgqlc.types.Field(sgqlc.types.non_null(DateTimeIntervalInput), graphql_name="end")


class DateTimeValueInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("date", "time")
    date = sgqlc.types.Field(sgqlc.types.non_null(DateInput), graphql_name="date")
    time = sgqlc.types.Field("TimeInput", graphql_name="time")


class Document2IssueInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("id_issue", "document_ids", "comment")
    id_issue = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="idIssue")
    document_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
        graphql_name="documentIds",
    )
    comment = sgqlc.types.Field(String, graphql_name="comment")


class DocumentAddInputInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("document_id", "x_coordinate", "y_coordinate", "group_id")
    document_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="documentId")
    x_coordinate = sgqlc.types.Field(Float, graphql_name="xCoordinate")
    y_coordinate = sgqlc.types.Field(Float, graphql_name="yCoordinate")
    group_id = sgqlc.types.Field(ID, graphql_name="groupId")


class DocumentAllKBFactsRemoveInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("document_id", "kb_entity_id")
    document_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="documentId")
    kb_entity_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="kbEntityId")


class DocumentAvatarUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("id", "children_document_id")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    children_document_id = sgqlc.types.Field(ID, graphql_name="childrenDocumentId")


class DocumentDeleteCandidateFactInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("document_id", "fact_id")
    document_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="documentId")
    fact_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="factId")


class DocumentDoubleCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("uuid", "double_uuid", "parent_uuid", "concept_id")
    uuid = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="uuid")
    double_uuid = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="doubleUuid")
    parent_uuid = sgqlc.types.Field(ID, graphql_name="parentUuid")
    concept_id = sgqlc.types.Field(ID, graphql_name="conceptId")


class DocumentFeedCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("name", "query", "filter_settings")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    query = sgqlc.types.Field(String, graphql_name="query")
    filter_settings = sgqlc.types.Field("DocumentFilterSettings", graphql_name="filterSettings")


class DocumentFeedFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "search_string",
        "creator",
        "last_updater",
        "registration_date",
        "update_date",
    )
    id = sgqlc.types.Field(ID, graphql_name="id")
    search_string = sgqlc.types.Field(String, graphql_name="searchString")
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="creator")
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="lastUpdater")
    registration_date = sgqlc.types.Field("TimestampInterval", graphql_name="registrationDate")
    update_date = sgqlc.types.Field("TimestampInterval", graphql_name="updateDate")


class DocumentFeedUpdateDocumentsInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("document_ids",)
    document_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
        graphql_name="documentIds",
    )


class DocumentFeedUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("name", "query", "filter_settings")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    query = sgqlc.types.Field(String, graphql_name="query")
    filter_settings = sgqlc.types.Field("DocumentFilterSettings", graphql_name="filterSettings")


class DocumentFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "search_string",
        "substring",
        "named_entities",
        "concepts",
        "platforms",
        "accounts",
        "nerc_num",
        "concepts_num",
        "child_docs_num",
        "publication_date",
        "registration_date",
        "last_update",
        "creator",
        "publication_author",
        "last_updater",
        "access_level_id",
        "links",
        "markers",
        "document_type",
        "source_type",
        "trust_level",
        "has_linked_issues",
        "nested_ids",
        "story",
    )
    search_string = sgqlc.types.Field(String, graphql_name="searchString")
    substring = sgqlc.types.Field(String, graphql_name="substring")
    named_entities = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="namedEntities")
    concepts = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="concepts")
    platforms = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="platforms")
    accounts = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="accounts")
    nerc_num = sgqlc.types.Field("IntervalInt", graphql_name="nercNum")
    concepts_num = sgqlc.types.Field("IntervalInt", graphql_name="conceptsNum")
    child_docs_num = sgqlc.types.Field("IntervalInt", graphql_name="childDocsNum")
    publication_date = sgqlc.types.Field("TimestampInterval", graphql_name="publicationDate")
    registration_date = sgqlc.types.Field("TimestampInterval", graphql_name="registrationDate")
    last_update = sgqlc.types.Field("TimestampInterval", graphql_name="lastUpdate")
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="creator")
    publication_author = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(String)),
        graphql_name="publicationAuthor",
    )
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="lastUpdater")
    access_level_id = sgqlc.types.Field(ID, graphql_name="accessLevelId")
    links = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="links")
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="markers")
    document_type = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(DocumentType)),
        graphql_name="documentType",
    )
    source_type = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(DocumentSourceType)),
        graphql_name="sourceType",
    )
    trust_level = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(TrustLevel)), graphql_name="trustLevel")
    has_linked_issues = sgqlc.types.Field(Boolean, graphql_name="hasLinkedIssues")
    nested_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="nestedIds")
    story = sgqlc.types.Field(String, graphql_name="story")


class DocumentLinkFilterSetting(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("document_type",)
    document_type = sgqlc.types.Field(DocumentType, graphql_name="documentType")


class DocumentMoveInputInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("document_id", "x_coordinate", "y_coordinate")
    document_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="documentId")
    x_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="xCoordinate")
    y_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="yCoordinate")


class DocumentNodeUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("id", "node_id", "language", "translation")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    node_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="nodeId")
    language = sgqlc.types.Field("LanguageUpdateInput", graphql_name="language")
    translation = sgqlc.types.Field("TranslationInput", graphql_name="translation")


class DocumentUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "notes",
        "title",
        "preview_text",
        "publication_date",
        "publication_author",
        "markers",
        "trust_level",
        "platform",
        "account",
        "language",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    notes = sgqlc.types.Field(String, graphql_name="notes")
    title = sgqlc.types.Field(String, graphql_name="title")
    preview_text = sgqlc.types.Field(String, graphql_name="previewText")
    publication_date = sgqlc.types.Field(Long, graphql_name="publicationDate")
    publication_author = sgqlc.types.Field(String, graphql_name="publicationAuthor")
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="markers")
    trust_level = sgqlc.types.Field(TrustLevel, graphql_name="trustLevel")
    platform = sgqlc.types.Field(ID, graphql_name="platform")
    account = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="account")
    language = sgqlc.types.Field(String, graphql_name="language")


class DocumentsTextWithMarkerByDateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("marker", "start_date", "end_date")
    marker = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="marker")
    start_date = sgqlc.types.Field(UnixTime, graphql_name="startDate")
    end_date = sgqlc.types.Field(UnixTime, graphql_name="endDate")


class DocumentsWithConceptByDateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("concept_type_id", "start_date", "end_date")
    concept_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptTypeId")
    start_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name="startDate")
    end_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name="endDate")


class DoubleValueInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("value",)
    value = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="value")


class ExtraSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "hide_child",
        "search_on_map",
        "selected_content",
        "ranking_script",
    )
    hide_child = sgqlc.types.Field(Boolean, graphql_name="hideChild")
    search_on_map = sgqlc.types.Field(Boolean, graphql_name="searchOnMap")
    selected_content = sgqlc.types.Field("ResearchMapSelectedContent", graphql_name="selectedContent")
    ranking_script = sgqlc.types.Field(String, graphql_name="rankingScript")


class FactInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("document_id", "annotations", "fact_id")
    document_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="documentId")
    annotations = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("TextBoundingInput")),
        graphql_name="annotations",
    )
    fact_id = sgqlc.types.Field(ID, graphql_name="factId")


class GeoPointFormInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("latitude", "longitude")
    latitude = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="latitude")
    longitude = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="longitude")


class GeoPointInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("point", "name")
    point = sgqlc.types.Field(CoordinatesInput, graphql_name="point")
    name = sgqlc.types.Field(String, graphql_name="name")


class GeoPointWithNameFormInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("point", "name", "radius")
    point = sgqlc.types.Field(GeoPointFormInput, graphql_name="point")
    name = sgqlc.types.Field(String, graphql_name="name")
    radius = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="radius")


class GroupCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "research_map_id",
        "name",
        "x_coordinate",
        "y_coordinate",
        "collapsed",
        "layout",
    )
    research_map_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="researchMapId")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    x_coordinate = sgqlc.types.Field(Float, graphql_name="xCoordinate")
    y_coordinate = sgqlc.types.Field(Float, graphql_name="yCoordinate")
    collapsed = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="collapsed")
    layout = sgqlc.types.Field(String, graphql_name="layout")


class GroupUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("name", "x_coordinate", "y_coordinate", "collapsed", "layout")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    x_coordinate = sgqlc.types.Field(Float, graphql_name="xCoordinate")
    y_coordinate = sgqlc.types.Field(Float, graphql_name="yCoordinate")
    collapsed = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="collapsed")
    layout = sgqlc.types.Field(String, graphql_name="layout")


class IntValueInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("value",)
    value = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="value")


class InterestObjectMainPropertiesOrderUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("concept_type_id", "ordered_main_property_type_ids")
    concept_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptTypeId")
    ordered_main_property_type_ids = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(ID)),
        graphql_name="orderedMainPropertyTypeIds",
    )


class IntervalDouble(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("start", "end")
    start = sgqlc.types.Field(Float, graphql_name="start")
    end = sgqlc.types.Field(Float, graphql_name="end")


class IntervalInt(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("start", "end")
    start = sgqlc.types.Field(Int, graphql_name="start")
    end = sgqlc.types.Field(Int, graphql_name="end")


class Issue2TaskInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("id_issue", "task_ids", "comment")
    id_issue = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="idIssue")
    task_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
        graphql_name="taskIds",
    )
    comment = sgqlc.types.Field(String, graphql_name="comment")


class IssueCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "topic",
        "description",
        "status",
        "priority",
        "executor_id",
        "execution_time_limit",
        "documents",
        "concepts",
        "issues",
        "markers",
    )
    topic = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="topic")
    description = sgqlc.types.Field(String, graphql_name="description")
    status = sgqlc.types.Field(sgqlc.types.non_null(IssueStatus), graphql_name="status")
    priority = sgqlc.types.Field(sgqlc.types.non_null(IssuePriority), graphql_name="priority")
    executor_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="executorId")
    execution_time_limit = sgqlc.types.Field(UnixTime, graphql_name="executionTimeLimit")
    documents = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
        graphql_name="documents",
    )
    concepts = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
        graphql_name="concepts",
    )
    issues = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
        graphql_name="issues",
    )
    markers = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="markers",
    )


class IssueEditFieldsInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "topic",
        "description",
        "status",
        "priority",
        "executor_id",
        "execution_time_limit",
        "markers",
        "comment",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    topic = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="topic")
    description = sgqlc.types.Field(String, graphql_name="description")
    status = sgqlc.types.Field(sgqlc.types.non_null(IssueStatus), graphql_name="status")
    priority = sgqlc.types.Field(sgqlc.types.non_null(IssuePriority), graphql_name="priority")
    executor_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="executorId")
    execution_time_limit = sgqlc.types.Field(UnixTime, graphql_name="executionTimeLimit")
    markers = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="markers",
    )
    comment = sgqlc.types.Field(String, graphql_name="comment")


class IssueFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "executor",
        "creator",
        "last_updater",
        "status",
        "priority",
        "registration_date",
        "update_date",
        "issue_for_document",
        "issue_for_concept",
        "only_my",
        "issue",
        "concept",
        "document",
        "name",
        "description",
        "execution_time_limit",
        "markers",
    )
    executor = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="executor")
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="creator")
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="lastUpdater")
    status = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(IssueStatus)), graphql_name="status")
    priority = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(IssuePriority)),
        graphql_name="priority",
    )
    registration_date = sgqlc.types.Field("TimestampInterval", graphql_name="registrationDate")
    update_date = sgqlc.types.Field("TimestampInterval", graphql_name="updateDate")
    issue_for_document = sgqlc.types.Field(Boolean, graphql_name="issueForDocument")
    issue_for_concept = sgqlc.types.Field(Boolean, graphql_name="issueForConcept")
    only_my = sgqlc.types.Field(Boolean, graphql_name="onlyMy")
    issue = sgqlc.types.Field(ID, graphql_name="issue")
    concept = sgqlc.types.Field(ID, graphql_name="concept")
    document = sgqlc.types.Field(ID, graphql_name="document")
    name = sgqlc.types.Field(String, graphql_name="name")
    description = sgqlc.types.Field(String, graphql_name="description")
    execution_time_limit = sgqlc.types.Field("TimestampInterval", graphql_name="executionTimeLimit")
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="markers")


class LanguageFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("search_string",)
    search_string = sgqlc.types.Field(String, graphql_name="searchString")


class LanguageInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("id",)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")


class LanguageUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("id",)
    id = sgqlc.types.Field(ID, graphql_name="id")


class LinkFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("link_type_id", "link_direction", "other_concept_id")
    link_type_id = sgqlc.types.Field(ID, graphql_name="linkTypeId")
    link_direction = sgqlc.types.Field(LinkDirection, graphql_name="linkDirection")
    other_concept_id = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="otherConceptId")


class LinkValueInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("link",)
    link = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="link")


class MassUpdateIssueInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "ids",
        "status",
        "priority",
        "executor",
        "execution_time_limit",
        "comment",
    )
    ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
        graphql_name="ids",
    )
    status = sgqlc.types.Field(IssueStatus, graphql_name="status")
    priority = sgqlc.types.Field(IssuePriority, graphql_name="priority")
    executor = sgqlc.types.Field(ID, graphql_name="executor")
    execution_time_limit = sgqlc.types.Field(UnixTime, graphql_name="executionTimeLimit")
    comment = sgqlc.types.Field(String, graphql_name="comment")


class NERCRegexpInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("regexp", "context_regexp", "auto_create")
    regexp = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="regexp")
    context_regexp = sgqlc.types.Field(String, graphql_name="contextRegexp")
    auto_create = sgqlc.types.Field(Boolean, graphql_name="autoCreate")


class NamedValueType(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("name", "value_type_id", "view", "is_required")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    value_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="valueTypeId")
    view = sgqlc.types.Field(ComponentView, graphql_name="view")
    is_required = sgqlc.types.Field(Boolean, graphql_name="isRequired")


class NormalizationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("type_id", "value")
    type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="typeId")
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="value")


class ParameterInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("key", "value")
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="key")
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="value")


class PerformSynchronously(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("perform_synchronously",)
    perform_synchronously = sgqlc.types.Field(Boolean, graphql_name="performSynchronously")


class PlatformCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "name",
        "id",
        "platform_type",
        "url",
        "country",
        "language",
        "markers",
        "params",
    )
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    platform_type = sgqlc.types.Field(sgqlc.types.non_null(PlatformType), graphql_name="platformType")
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="url")
    country = sgqlc.types.Field(String, graphql_name="country")
    language = sgqlc.types.Field(String, graphql_name="language")
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="markers")
    params = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ParameterInput)), graphql_name="params")


class PlatformFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "search_string",
        "id",
        "platform_type",
        "markers",
        "country",
        "language",
        "creator",
        "last_updater",
        "registration_date",
        "update_date",
    )
    search_string = sgqlc.types.Field(String, graphql_name="searchString")
    id = sgqlc.types.Field(ID, graphql_name="id")
    platform_type = sgqlc.types.Field(PlatformType, graphql_name="platformType")
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="markers")
    country = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="country")
    language = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="language")
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="creator")
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="lastUpdater")
    registration_date = sgqlc.types.Field("TimestampInterval", graphql_name="registrationDate")
    update_date = sgqlc.types.Field("TimestampInterval", graphql_name="updateDate")


class PlatformGetOrCreateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("id", "name", "platform_type", "url")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    platform_type = sgqlc.types.Field(sgqlc.types.non_null(PlatformType), graphql_name="platformType")
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="url")


class PlatformUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "platform_id",
        "name",
        "new_id",
        "platform_type",
        "url",
        "country",
        "language",
        "markers",
        "params",
    )
    platform_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="platformId")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    new_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="newId")
    platform_type = sgqlc.types.Field(sgqlc.types.non_null(PlatformType), graphql_name="platformType")
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="url")
    country = sgqlc.types.Field(String, graphql_name="country")
    language = sgqlc.types.Field(String, graphql_name="language")
    markers = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="markers",
    )
    params = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ParameterInput))),
        graphql_name="params",
    )


class PropertyFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "property_type_id",
        "component_id",
        "property_type",
        "string_filter",
        "int_filter",
        "double_filter",
        "date_time_filter",
        "date_time_interval_filter",
        "geo_filter",
    )
    property_type_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="propertyTypeId")
    component_id = sgqlc.types.Field(ID, graphql_name="componentId")
    property_type = sgqlc.types.Field(sgqlc.types.non_null(PropLinkOrConcept), graphql_name="propertyType")
    string_filter = sgqlc.types.Field("StringFilter", graphql_name="stringFilter")
    int_filter = sgqlc.types.Field(IntervalInt, graphql_name="intFilter")
    double_filter = sgqlc.types.Field(IntervalDouble, graphql_name="doubleFilter")
    date_time_filter = sgqlc.types.Field(DateTimeIntervalInput, graphql_name="dateTimeFilter")
    date_time_interval_filter = sgqlc.types.Field(DateTimeIntervalPairInput, graphql_name="dateTimeIntervalFilter")
    geo_filter = sgqlc.types.Field(GeoPointWithNameFormInput, graphql_name="geoFilter")


class RedmineIssueCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "obj_ids",
        "issue_type",
        "subject",
        "assignee_id",
        "tracker_id",
        "status_id",
        "priority_id",
        "due_to",
        "description",
        "related_issues",
    )
    obj_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
        graphql_name="objIds",
    )
    issue_type = sgqlc.types.Field(sgqlc.types.non_null(RedmineIssueType), graphql_name="issueType")
    subject = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="subject")
    assignee_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="assigneeId")
    tracker_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="trackerId")
    status_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="statusId")
    priority_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="priorityId")
    due_to = sgqlc.types.Field(Long, graphql_name="dueTo")
    description = sgqlc.types.Field(String, graphql_name="description")
    related_issues = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="relatedIssues")


class RedmineIssueDefaultParametersInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("obj_ids", "issue_type")
    obj_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
        graphql_name="objIds",
    )
    issue_type = sgqlc.types.Field(sgqlc.types.non_null(RedmineIssueType), graphql_name="issueType")


class RedmineIssueUnlinkInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("object_id", "issue_type", "issue_ids")
    object_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="objectId")
    issue_type = sgqlc.types.Field(sgqlc.types.non_null(RedmineIssueType), graphql_name="issueType")
    issue_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
        graphql_name="issueIds",
    )


class RedmineIssueUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("obj_ids", "issue_type", "issue_ids", "description")
    obj_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
        graphql_name="objIds",
    )
    issue_type = sgqlc.types.Field(sgqlc.types.non_null(RedmineIssueType), graphql_name="issueType")
    issue_ids = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
        graphql_name="issueIds",
    )
    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="description")


class RegexpToUpdate(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("regexp_to_replace", "regexp_to_insert")
    regexp_to_replace = sgqlc.types.Field(NERCRegexpInput, graphql_name="regexpToReplace")
    regexp_to_insert = sgqlc.types.Field(NERCRegexpInput, graphql_name="regexpToInsert")


class RelExtModelInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "source_annotation_type",
        "target_annotation_type",
        "relation_type",
        "invert_direction",
    )
    source_annotation_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="sourceAnnotationType")
    target_annotation_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="targetAnnotationType")
    relation_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="relationType")
    invert_direction = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="invertDirection")


class RelatedDocumentFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("document_type",)
    document_type = sgqlc.types.Field(DocumentType, graphql_name="documentType")


class ResearchMapBatchMoveInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "document_move_input",
        "concept_move_input",
        "concept_candidate_move_input",
    )
    document_move_input = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DocumentMoveInputInput))),
        graphql_name="documentMoveInput",
    )
    concept_move_input = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptMoveInput))),
        graphql_name="conceptMoveInput",
    )
    concept_candidate_move_input = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptCandidateMoveInput))),
        graphql_name="conceptCandidateMoveInput",
    )


class ResearchMapBatchUpdateGroupInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "concept_ids",
        "document_ids",
        "concept_candidate_ids",
        "group_id",
    )
    concept_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="conceptIds")
    document_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="documentIds")
    concept_candidate_ids = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(ID)),
        graphql_name="conceptCandidateIds",
    )
    group_id = sgqlc.types.Field(ID, graphql_name="groupId")


class ResearchMapContentAddInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("documents", "concepts", "concept_candidates")
    documents = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(DocumentAddInputInput)),
        graphql_name="documents",
    )
    concepts = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(ConceptAddInputInput)),
        graphql_name="concepts",
    )
    concept_candidates = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(ConceptCandidateAddInputInput)),
        graphql_name="conceptCandidates",
    )


class ResearchMapContentSelectInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("concepts", "documents", "concept_candidates")
    concepts = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="concepts")
    documents = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="documents")
    concept_candidates = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="conceptCandidates")


class ResearchMapContentUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("concepts", "documents", "concept_candidates")
    concepts = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="concepts")
    documents = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="documents")
    concept_candidates = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="conceptCandidates")


class ResearchMapCreationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "name",
        "concepts",
        "documents",
        "description",
        "access_level_id",
        "markers",
    )
    name = sgqlc.types.Field(String, graphql_name="name")
    concepts = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="concepts")
    documents = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="documents")
    description = sgqlc.types.Field(String, graphql_name="description")
    access_level_id = sgqlc.types.Field(ID, graphql_name="accessLevelId")
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="markers")


class ResearchMapFilterSettings(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "name",
        "description",
        "access_level_id",
        "creator",
        "last_updater",
        "markers",
        "creation_date",
        "update_date",
    )
    name = sgqlc.types.Field(String, graphql_name="name")
    description = sgqlc.types.Field(String, graphql_name="description")
    access_level_id = sgqlc.types.Field(ID, graphql_name="accessLevelId")
    creator = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="creator")
    last_updater = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="lastUpdater")
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="markers")
    creation_date = sgqlc.types.Field("TimestampInterval", graphql_name="creationDate")
    update_date = sgqlc.types.Field("TimestampInterval", graphql_name="updateDate")


class ResearchMapSelectedContent(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("document_ids", "concept_ids")
    document_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="documentIDs")
    concept_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="conceptIDs")


class ResearchMapUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("name", "description", "access_level_id", "markers")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    description = sgqlc.types.Field(String, graphql_name="description")
    access_level_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="accessLevelId")
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="markers")


class SearchElementToUpdate(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("dict", "regexp")
    dict = sgqlc.types.Field("WordsToUpdate", graphql_name="dict")
    regexp = sgqlc.types.Field(RegexpToUpdate, graphql_name="regexp")


class StringFilter(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("str",)
    str = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="str")


class StringLocaleValueInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("value", "locale")
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="value")
    locale = sgqlc.types.Field(sgqlc.types.non_null(Locale), graphql_name="locale")


class StringValueInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("value",)
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="value")


class TextBoundingInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("start", "end", "node_id")
    start = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="start")
    end = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="end")
    node_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="nodeId")


class TimeInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("hour", "minute", "second")
    hour = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="hour")
    minute = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="minute")
    second = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="second")


class TimestampInterval(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("start", "end")
    start = sgqlc.types.Field(UnixTime, graphql_name="start")
    end = sgqlc.types.Field(UnixTime, graphql_name="end")


class TranslationInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("language", "text")
    language = sgqlc.types.Field(sgqlc.types.non_null(LanguageInput), graphql_name="language")
    text = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="text")


class TypeSearchElementUpdateInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("id", "elements_type", "search_element_to_update")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    elements_type = sgqlc.types.Field(sgqlc.types.non_null(ElementType), graphql_name="elementsType")
    search_element_to_update = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(SearchElementToUpdate))),
        graphql_name="searchElementToUpdate",
    )


class UpdateCommentInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("task_change_id", "comment")
    task_change_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="taskChangeId")
    comment = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="comment")


class ValueInput(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = (
        "string_value_input",
        "string_locale_value_input",
        "int_value_input",
        "double_value_input",
        "geo_point_value_input",
        "date_time_value_input",
        "link_value_input",
    )
    string_value_input = sgqlc.types.Field(StringValueInput, graphql_name="stringValueInput")
    string_locale_value_input = sgqlc.types.Field(StringLocaleValueInput, graphql_name="stringLocaleValueInput")
    int_value_input = sgqlc.types.Field(IntValueInput, graphql_name="intValueInput")
    double_value_input = sgqlc.types.Field(DoubleValueInput, graphql_name="doubleValueInput")
    geo_point_value_input = sgqlc.types.Field(GeoPointInput, graphql_name="geoPointValueInput")
    date_time_value_input = sgqlc.types.Field(DateTimeValueInput, graphql_name="dateTimeValueInput")
    link_value_input = sgqlc.types.Field(LinkValueInput, graphql_name="linkValueInput")


class WordsToUpdate(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("word_to_replace", "word_to_insert")
    word_to_replace = sgqlc.types.Field(String, graphql_name="wordToReplace")
    word_to_insert = sgqlc.types.Field(String, graphql_name="wordToInsert")


class conceptTypeAndEventFilter(sgqlc.types.Input):
    __schema__ = api_schema
    __field_names__ = ("full_type", "is_event")
    full_type = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="fullType")
    is_event = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isEvent")


########################################################################
# Output Objects and Interfaces
########################################################################
class AccessLevel(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("id", "name", "order")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    order = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name="order")


class AccessLevelPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("list_access_level", "total")
    list_access_level = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(AccessLevel))),
        graphql_name="listAccessLevel",
    )
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")


class AccountPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("list_account", "total", "total_platforms")
    list_account = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("Account"))),
        graphql_name="listAccount",
    )
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")
    total_platforms = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="totalPlatforms")


class AccountStatistics(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("count_doc",)
    count_doc = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countDoc")


class Annotation(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("start", "end", "value")
    start = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="start")
    end = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="end")
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="value")


class Autocomplete(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("autocomplete",)
    autocomplete = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="autocomplete",
    )


class CommonStringPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("total", "list_string")
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")
    list_string = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="listString",
    )


class CompositeConcept(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "root_concept",
        "composite_concept_type",
        "id",
        "list_concepts",
        "paginate_single_widget",
        "pagination_concept_mention",
        "list_concept_mention",
    )
    root_concept = sgqlc.types.Field(sgqlc.types.non_null("Concept"), graphql_name="rootConcept")
    composite_concept_type = sgqlc.types.Field(
        sgqlc.types.non_null("CompositeConceptType"),
        graphql_name="compositeConceptType",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    list_concepts = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("Concept"))),
        graphql_name="listConcepts",
    )
    paginate_single_widget = sgqlc.types.Field(
        sgqlc.types.non_null("CompositeConceptWidgetRowPagination"),
        graphql_name="paginateSingleWidget",
        args=sgqlc.types.ArgDict(
            (
                (
                    "widget_type_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ID),
                        graphql_name="widgetTypeId",
                        default=None,
                    ),
                ),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
            )
        ),
    )
    pagination_concept_mention = sgqlc.types.Field(
        "ConceptFactPagination",
        graphql_name="paginationConceptMention",
        args=sgqlc.types.ArgDict(
            (
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DocumentLinkFilterSetting),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
            )
        ),
    )
    list_concept_mention = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("ConceptFact")),
        graphql_name="listConceptMention",
    )


class CompositeConceptPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("list_composite_concept", "total")
    list_composite_concept = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CompositeConcept))),
        graphql_name="listCompositeConcept",
    )
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name="total")


class CompositeConceptStatistics(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("count_concept_types",)
    count_concept_types = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countConceptTypes")


class CompositeConceptTypePagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("list_composite_concept_type", "total")
    list_composite_concept_type = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("CompositeConceptType"))),
        graphql_name="listCompositeConceptType",
    )
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")


class CompositeConceptTypeWidgetTypeColumn(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "name",
        "is_main_properties",
        "list_values",
        "sort_by_column",
        "sort_direction",
        "concept_link_types_path",
        "property_type",
        "metadata",
        "link_property_type",
        "link_metadata",
        "sortable",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    is_main_properties = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isMainProperties")
    list_values = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="listValues")
    sort_by_column = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="sortByColumn")
    sort_direction = sgqlc.types.Field(SortDirection, graphql_name="sortDirection")
    concept_link_types_path = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptLinkType"))),
        graphql_name="conceptLinkTypesPath",
    )
    property_type = sgqlc.types.Field("ConceptPropertyType", graphql_name="propertyType")
    metadata = sgqlc.types.Field(ConceptTypeMetadata, graphql_name="metadata")
    link_property_type = sgqlc.types.Field("ConceptPropertyType", graphql_name="linkPropertyType")
    link_metadata = sgqlc.types.Field(ConceptTypeLinkMetadata, graphql_name="linkMetadata")
    sortable = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="sortable")


class CompositeConceptTypeWidgetTypePagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("list_composite_concept_type_widget", "total")
    list_composite_concept_type_widget = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("CompositeConceptTypeWidgetType"))),
        graphql_name="listCompositeConceptTypeWidget",
    )
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")


class CompositeConceptWidgetRowPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("widget_type", "total", "rows")
    widget_type = sgqlc.types.Field(
        sgqlc.types.non_null("CompositeConceptTypeWidgetType"),
        graphql_name="widgetType",
    )
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")
    rows = sgqlc.types.Field(
        sgqlc.types.non_null(
            sgqlc.types.list_of(
                sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("Value")))))
            )
        ),
        graphql_name="rows",
    )


class CompositePropertyValueTemplatePagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("list_composite_property_value_template", "total")
    list_composite_property_value_template = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("CompositePropertyValueTemplate"))),
        graphql_name="listCompositePropertyValueTemplate",
    )
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")


class CompositePropertyValueType(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("id", "name", "value_type", "is_required", "view")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    value_type = sgqlc.types.Field(sgqlc.types.non_null("ConceptPropertyValueType"), graphql_name="valueType")
    is_required = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isRequired")
    view = sgqlc.types.Field(sgqlc.types.non_null(ComponentView), graphql_name="view")


class CompositeValue(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("list_value",)
    list_value = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("NamedValue"))),
        graphql_name="listValue",
    )


class ConceptCandidateFactMention(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("concept", "mention")
    concept = sgqlc.types.Field(sgqlc.types.non_null("ConceptCandidateFact"), graphql_name="concept")
    mention = sgqlc.types.Field(sgqlc.types.non_null("Mention"), graphql_name="mention")


class ConceptCandidateFactWithCoordinates(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "concept_candidate_fact",
        "x_coordinate",
        "y_coordinate",
        "group_id",
    )
    concept_candidate_fact = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptCandidateFact"),
        graphql_name="conceptCandidateFact",
    )
    x_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="xCoordinate")
    y_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="yCoordinate")
    group_id = sgqlc.types.Field(ID, graphql_name="groupId")


class ConceptFactLink(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "concept_id",
        "concept_fact_id",
        "status",
        "is_implicit",
        "concept",
        "concept_fact",
    )
    concept_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptId")
    concept_fact_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptFactId")
    status = sgqlc.types.Field(FactStatus, graphql_name="status")
    is_implicit = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isImplicit")
    concept = sgqlc.types.Field(sgqlc.types.non_null("Concept"), graphql_name="concept")
    concept_fact = sgqlc.types.Field(sgqlc.types.non_null("ConceptCandidateFact"), graphql_name="conceptFact")


class ConceptFactPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("total", "list_concept_fact")
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name="total")
    list_concept_fact = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptFact"))),
        graphql_name="listConceptFact",
    )


class ConceptImplicitLink(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "concept_from_id",
        "concept_to_id",
        "concept_from",
        "concept_to",
        "concept_link_type",
    )
    concept_from_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptFromId")
    concept_to_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptToId")
    concept_from = sgqlc.types.Field(sgqlc.types.non_null("Concept"), graphql_name="conceptFrom")
    concept_to = sgqlc.types.Field(sgqlc.types.non_null("Concept"), graphql_name="conceptTo")
    concept_link_type = sgqlc.types.Field(sgqlc.types.non_null("ConceptLinkType"), graphql_name="conceptLinkType")


class ConceptLinkFactPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("total", "list_concept_link_fact")
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name="total")
    list_concept_link_fact = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptLinkFact"))),
        graphql_name="listConceptLinkFact",
    )


class ConceptLinkPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("total", "list_concept_link")
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name="total")
    list_concept_link = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptLink"))),
        graphql_name="listConceptLink",
    )


class ConceptLinkTypePagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("list_concept_link_type", "total")
    list_concept_link_type = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptLinkType"))),
        graphql_name="listConceptLinkType",
    )
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")


class ConceptLinkTypeStatistics(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("count_property_type",)
    count_property_type = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countPropertyType")


class ConceptMention(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("concept", "mention")
    concept = sgqlc.types.Field(sgqlc.types.non_null("Concept"), graphql_name="concept")
    mention = sgqlc.types.Field(sgqlc.types.non_null("Mention"), graphql_name="mention")


class ConceptMentionCount(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("concept", "count")
    concept = sgqlc.types.Field(sgqlc.types.non_null("Concept"), graphql_name="concept")
    count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="count")


class ConceptPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("total", "show_total", "list_concept")
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name="total")
    show_total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name="showTotal")
    list_concept = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("Concept"))),
        graphql_name="listConcept",
    )


class ConceptPropertyPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("total", "list_concept_property")
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name="total")
    list_concept_property = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptProperty"))),
        graphql_name="listConceptProperty",
    )


class ConceptPropertyTypePagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("list_concept_property_type", "total")
    list_concept_property_type = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptPropertyType"))),
        graphql_name="listConceptPropertyType",
    )
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")


class ConceptPropertyValueStatistics(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "count_concept_type",
        "count_link_type",
        "count_dictionary",
        "count_regexp",
    )
    count_concept_type = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countConceptType")
    count_link_type = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countLinkType")
    count_dictionary = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countDictionary")
    count_regexp = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countRegexp")


class ConceptPropertyValueTypePagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("list_concept_property_value_type", "total")
    list_concept_property_value_type = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptPropertyValueType"))),
        graphql_name="listConceptPropertyValueType",
    )
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")


class ConceptStatistics(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "count_property",
        "count_links_to_objects",
        "count_links_to_events",
        "count_documents_mention",
        "count_research_map",
        "count_links_to_concepts",
        "count_links_to_concepts_and_documents",
    )
    count_property = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countProperty")
    count_links_to_objects = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countLinksToObjects")
    count_links_to_events = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countLinksToEvents")
    count_documents_mention = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countDocumentsMention")
    count_research_map = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countResearchMap")
    count_links_to_concepts = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countLinksToConcepts")
    count_links_to_concepts_and_documents = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countLinksToConceptsAndDocuments")


class ConceptSubscriptions(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("subscriptions", "list_user", "count_users")
    subscriptions = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptUpdate))),
        graphql_name="subscriptions",
    )
    list_user = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("User"))),
        graphql_name="listUser",
    )
    count_users = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countUsers")


class ConceptTypePagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("list_concept_type", "total")
    list_concept_type = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptType"))),
        graphql_name="listConceptType",
    )
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")


class ConceptTypeStatistics(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "count_property_type",
        "count_link_type",
        "count_dictionary",
        "count_regexp",
    )
    count_property_type = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countPropertyType")
    count_link_type = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countLinkType")
    count_dictionary = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countDictionary")
    count_regexp = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countRegexp")


class ConceptTypeViewPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("list_concept_type_view", "total")
    list_concept_type_view = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptTypeView"))),
        graphql_name="listConceptTypeView",
    )
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")


class ConceptView(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("concept", "rows")
    concept = sgqlc.types.Field(sgqlc.types.non_null("Concept"), graphql_name="concept")
    rows = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptViewValue"))))),
        graphql_name="rows",
    )


class ConceptViewPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("total", "list_concept_view")
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name="total")
    list_concept_view = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptView))),
        graphql_name="listConceptView",
    )


class ConceptWithCoordinate(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("concept", "x_coordinate", "y_coordinate", "group_id")
    concept = sgqlc.types.Field(sgqlc.types.non_null("Concept"), graphql_name="concept")
    x_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="xCoordinate")
    y_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="yCoordinate")
    group_id = sgqlc.types.Field(ID, graphql_name="groupId")


class ConceptWithNeighbors(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("concept", "num_of_neighbors")
    concept = sgqlc.types.Field(sgqlc.types.non_null("Concept"), graphql_name="concept")
    num_of_neighbors = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="numOfNeighbors")


class Coordinates(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("latitude", "longitude")
    latitude = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="latitude")
    longitude = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="longitude")


class CountFacet(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("value", "count")
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="value")
    count = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name="count")


class CountryPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("list_country", "total")
    list_country = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="listCountry",
    )
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")


class Date(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("year", "month", "day")
    year = sgqlc.types.Field(Int, graphql_name="year")
    month = sgqlc.types.Field(Int, graphql_name="month")
    day = sgqlc.types.Field(Int, graphql_name="day")


class DateTimeInterval(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("start", "end")
    start = sgqlc.types.Field("DateTimeValue", graphql_name="start")
    end = sgqlc.types.Field("DateTimeValue", graphql_name="end")


class DateTimeValue(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("date", "time")
    date = sgqlc.types.Field(sgqlc.types.non_null(Date), graphql_name="date")
    time = sgqlc.types.Field("Time", graphql_name="time")


class DictValue(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("value",)
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="value")


class DocSpecificMetadata(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "category",
        "last_printed_date",
        "last_modified_by",
        "created_date",
        "comments",
        "author",
        "document_subject",
        "keywords",
        "modified_data",
        "doc_name",
    )
    category = sgqlc.types.Field(String, graphql_name="category")
    last_printed_date = sgqlc.types.Field(UnixTime, graphql_name="lastPrintedDate")
    last_modified_by = sgqlc.types.Field(String, graphql_name="lastModifiedBy")
    created_date = sgqlc.types.Field(UnixTime, graphql_name="createdDate")
    comments = sgqlc.types.Field(String, graphql_name="comments")
    author = sgqlc.types.Field(String, graphql_name="author")
    document_subject = sgqlc.types.Field(String, graphql_name="documentSubject")
    keywords = sgqlc.types.Field(String, graphql_name="keywords")
    modified_data = sgqlc.types.Field(UnixTime, graphql_name="modifiedData")
    doc_name = sgqlc.types.Field(String, graphql_name="docName")


class DocumentFeedPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("list_document_feed", "total")
    list_document_feed = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("DocumentFeed"))),
        graphql_name="listDocumentFeed",
    )
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")


class DocumentFromDocumentFeed(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("document", "is_from_favorites", "is_from_deleted")
    document = sgqlc.types.Field(sgqlc.types.non_null("Document"), graphql_name="document")
    is_from_favorites = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isFromFavorites")
    is_from_deleted = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isFromDeleted")


class DocumentFromDocumentFeedPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("list_document", "total")
    list_document = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DocumentFromDocumentFeed))),
        graphql_name="listDocument",
    )
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")


class DocumentLink(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("parent_id", "child_id")
    parent_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="parentId")
    child_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="childId")


class DocumentMetadata(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "file_name",
        "size",
        "file_type",
        "modified_time",
        "created_time",
        "access_time",
        "doc_specific_metadata",
        "pdf_specific_metadata",
        "image_specific_metadata",
        "source",
        "language",
        "platform",
        "account",
    )
    file_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="fileName")
    size = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name="size")
    file_type = sgqlc.types.Field(String, graphql_name="fileType")
    modified_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name="modifiedTime")
    created_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name="createdTime")
    access_time = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name="accessTime")
    doc_specific_metadata = sgqlc.types.Field(DocSpecificMetadata, graphql_name="docSpecificMetadata")
    pdf_specific_metadata = sgqlc.types.Field("PdfSpecificMetadataGQL", graphql_name="pdfSpecificMetadata")
    image_specific_metadata = sgqlc.types.Field("ImageSpecificMetadataGQL", graphql_name="imageSpecificMetadata")
    source = sgqlc.types.Field(String, graphql_name="source")
    language = sgqlc.types.Field("Language", graphql_name="language")
    platform = sgqlc.types.Field("Platform", graphql_name="platform")
    account = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("Account"))),
        graphql_name="account",
    )


class DocumentPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("list_document", "total")
    list_document = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("Document"))),
        graphql_name="listDocument",
    )
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")


class DocumentWithCoordinates(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("document", "x_coordinate", "y_coordinate", "group_id")
    document = sgqlc.types.Field(sgqlc.types.non_null("Document"), graphql_name="document")
    x_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="xCoordinate")
    y_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="yCoordinate")
    group_id = sgqlc.types.Field(ID, graphql_name="groupId")


class DoubleValue(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("value",)
    value = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="value")


class FactInterface(sgqlc.types.Interface):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "mention",
        "system_registration_date",
        "system_update_date",
        "document",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    mention = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("TextBounding"))),
        graphql_name="mention",
    )
    system_registration_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name="systemRegistrationDate")
    system_update_date = sgqlc.types.Field(UnixTime, graphql_name="systemUpdateDate")
    document = sgqlc.types.Field(sgqlc.types.non_null("Document"), graphql_name="document")


class FlatDocumentStructure(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "text",
        "annotations",
        "metadata",
        "document_id",
        "node_id",
        "hierarchy_level",
        "translated_text",
        "id",
        "language",
    )
    text = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="text")
    annotations = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Annotation))),
        graphql_name="annotations",
    )
    metadata = sgqlc.types.Field(sgqlc.types.non_null("ParagraphMetadata"), graphql_name="metadata")
    document_id = sgqlc.types.Field(ID, graphql_name="documentId")
    node_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="nodeId")
    hierarchy_level = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="hierarchyLevel")
    translated_text = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="translatedText")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    language = sgqlc.types.Field("Language", graphql_name="language")


class GeoPointValue(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("point", "name")
    point = sgqlc.types.Field(Coordinates, graphql_name="point")
    name = sgqlc.types.Field(String, graphql_name="name")


class Group(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "name",
        "x_coordinate",
        "y_coordinate",
        "collapsed",
        "layout",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    x_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="xCoordinate")
    y_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="yCoordinate")
    collapsed = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="collapsed")
    layout = sgqlc.types.Field(String, graphql_name="layout")


class HLAnnotation(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("start", "end")
    start = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="start")
    end = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="end")


class Highlighting(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("highlighting", "annotations")
    highlighting = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="highlighting")
    annotations = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(HLAnnotation))),
        graphql_name="annotations",
    )


class ImageSpecificMetadataGQL(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("height", "width", "orientation")
    height = sgqlc.types.Field(Long, graphql_name="height")
    width = sgqlc.types.Field(Long, graphql_name="width")
    orientation = sgqlc.types.Field(Int, graphql_name="orientation")


class IntValue(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("value",)
    value = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="value")


class IssueChangePagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("total", "list_issue_change")
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name="total")
    list_issue_change = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("IssueChange"))),
        graphql_name="listIssueChange",
    )


class IssueInfo(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "topic",
        "description",
        "status",
        "priority",
        "execution_time_limit",
        "markers",
        "executor",
        "list_concept",
        "list_document",
        "list_issue",
    )
    topic = sgqlc.types.Field(String, graphql_name="topic")
    description = sgqlc.types.Field(String, graphql_name="description")
    status = sgqlc.types.Field(IssueStatus, graphql_name="status")
    priority = sgqlc.types.Field(IssuePriority, graphql_name="priority")
    execution_time_limit = sgqlc.types.Field(UnixTime, graphql_name="executionTimeLimit")
    markers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="markers")
    executor = sgqlc.types.Field("User", graphql_name="executor")
    list_concept = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null("Concept")), graphql_name="listConcept")
    list_document = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("Document")),
        graphql_name="listDocument",
    )
    list_issue = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null("Issue")), graphql_name="listIssue")


class IssuePagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("list_issue", "total")
    list_issue = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("Issue"))),
        graphql_name="listIssue",
    )
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")


class IssueStatistics(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("count_concept", "count_doc", "count_issue")
    count_concept = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countConcept")
    count_doc = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countDoc")
    count_issue = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countIssue")


class Language(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("id",)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")


class LanguagePagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("list_language", "total")
    list_language = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="listLanguage",
    )
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")


class LinkValue(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("link",)
    link = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="link")


class ListsTextsFromDocumentWithMarkerResponse(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("marker_text", "not_marker_text")
    marker_text = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="markerText",
    )
    not_marker_text = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="notMarkerText",
    )


class Markers(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("markers",)
    markers = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="markers",
    )


class Mention(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "document_id",
        "text_bounding",
        "verifier",
        "system_registration_date",
        "system_update_date",
        "access_level",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    document_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="documentId")
    text_bounding = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("TextBounding"))),
        graphql_name="textBounding",
    )
    verifier = sgqlc.types.Field(sgqlc.types.non_null("User"), graphql_name="verifier")
    system_registration_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name="systemRegistrationDate")
    system_update_date = sgqlc.types.Field(UnixTime, graphql_name="systemUpdateDate")
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name="accessLevel")


class MergedConcept(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("concept", "merge_author", "merge_date")
    concept = sgqlc.types.Field(sgqlc.types.non_null("Concept"), graphql_name="concept")
    merge_author = sgqlc.types.Field(sgqlc.types.non_null("User"), graphql_name="mergeAuthor")
    merge_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name="mergeDate")


class MergedConceptPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("total", "list_merged_concept")
    total = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name="total")
    list_merged_concept = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(MergedConcept))),
        graphql_name="listMergedConcept",
    )


class Metrics(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "count_object",
        "count_event",
        "count_entities",
        "count_research_map",
        "count_child_docs",
        "count_concept",
    )
    count_object = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countObject")
    count_event = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countEvent")
    count_entities = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countEntities")
    count_research_map = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countResearchMap")
    count_child_docs = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countChildDocs")
    count_concept = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countConcept")


class Mutation(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "add_concept",
        "add_concept_link",
        "update_concept_link",
        "add_concept_property",
        "add_concept_link_property",
        "add_concept_fact",
        "delete_concept_fact",
        "add_concept_link_property_fact",
        "delete_concept_link_property_fact",
        "add_concept_property_fact",
        "delete_concept_property_fact",
        "add_concept_link_fact",
        "delete_concept_link_fact",
        "update_concept",
        "update_concept_avatar",
        "update_concept_property",
        "delete_concept_property",
        "delete_concept_link",
        "delete_concept",
        "delete_concept_link_property",
        "merge_concepts",
        "unmerge_concepts",
        "delete_fact",
        "normalize_value",
        "update_concept_subscriptions",
        "add_concept_type",
        "add_composite_concept_type",
        "add_composite_concept_type_widget_type",
        "set_concept_type_default_view",
        "add_concept_property_type",
        "add_concept_link_property_type",
        "add_concept_link_type",
        "add_concept_property_value_type",
        "add_concept_type_view",
        "update_concept_type",
        "update_composite_concept_type",
        "update_composite_concept_type_widget_type",
        "update_composite_concept_type_widget_types_order",
        "update_concept_property_type",
        "update_concept_main_property_type_order",
        "update_concept_link_property_type",
        "update_concept_link_type",
        "update_concept_property_value_type",
        "update_concept_type_view",
        "delete_concept_type_avatar",
        "delete_concept_type",
        "delete_composite_concept_type",
        "delete_composite_concept_type_widget_type",
        "delete_concept_property_type",
        "delete_concept_link_property_type",
        "delete_concept_link_type",
        "delete_concept_property_value_type",
        "delete_concept_type_view",
        "delete_bulk",
        "move_bulk",
        "update_type_search_element",
        "add_composite_property_value_template",
        "update_composite_property_value_template",
        "delete_composite_property_value_template",
        "add_issue",
        "delete_issue",
        "add_concept_to_issue",
        "add_document_to_issue",
        "add_issue_to_issue",
        "delete_document_from_issue",
        "delete_concept_from_issue",
        "delete_issue_from_issue",
        "update_issue",
        "update_issue_massive",
        "add_comment_to_issue",
        "update_issue_comment",
        "delete_issue_comment",
        "update_document",
        "update_document_avatar",
        "remove_candidate_fact_from_document",
        "remove_all_kbfacts_from_document",
        "delete_documents",
        "add_document_double",
        "update_document_node",
        "delete_research_map",
        "bulk_delete_research_map",
        "add_research_map",
        "add_research_map_from_files",
        "update_research_map",
        "add_content_on_research_map",
        "delete_content_from_research_map",
        "batch_move_nodes_on_map",
        "batch_update_group_on_map",
        "add_top_neighbors_on_map",
        "add_concept_fact_neighbors_on_map",
        "set_research_map_active",
        "find_shortest_path_on_map",
        "find_shortest_implicit_path_on_map",
        "add_group",
        "update_group",
        "delete_group",
        "create_redmine_issue",
        "update_redmine_issue",
        "unlink_issues",
        "add_access_level",
        "update_access_level",
        "delete_access_level",
        "add_template_docx",
        "update_markers_bulk",
        "add_platform",
        "update_platform",
        "delete_platform",
        "add_account",
        "update_account",
        "delete_account",
        "add_document_feed",
        "update_document_feed",
        "add_document_to_document_feed_favorites",
        "delete_document_from_document_feed_favorites",
        "delete_document_from_document_feed",
        "restore_document_to_document_feed",
        "delete_document_feed",
        "add_alias_to_concept",
        "get_or_add_account",
        "get_or_add_platform",
        "get_or_add_concept",
    )
    add_concept = sgqlc.types.Field(
        sgqlc.types.non_null("Concept"),
        graphql_name="addConcept",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptMutationInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
                (
                    "performance_control",
                    sgqlc.types.Arg(
                        PerformSynchronously,
                        graphql_name="performanceControl",
                        default={"performSynchronously": True},
                    ),
                ),
                ("file", sgqlc.types.Arg(Upload, graphql_name="file", default=None)),
            )
        ),
    )
    add_concept_link = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptLink"),
        graphql_name="addConceptLink",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptLinkCreationMutationInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
                (
                    "performance_control",
                    sgqlc.types.Arg(
                        PerformSynchronously,
                        graphql_name="performanceControl",
                        default={"performSynchronously": True},
                    ),
                ),
            )
        ),
    )
    update_concept_link = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptLink"),
        graphql_name="updateConceptLink",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptLinkUpdateMutationInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_concept_property = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptProperty"),
        graphql_name="addConceptProperty",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptPropertyCreateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
                (
                    "performance_control",
                    sgqlc.types.Arg(
                        PerformSynchronously,
                        graphql_name="performanceControl",
                        default={"performSynchronously": True},
                    ),
                ),
            )
        ),
    )
    add_concept_link_property = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptProperty"),
        graphql_name="addConceptLinkProperty",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptLinkPropertyInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
                (
                    "performance_control",
                    sgqlc.types.Arg(
                        PerformSynchronously,
                        graphql_name="performanceControl",
                        default={"performSynchronously": True},
                    ),
                ),
            )
        ),
    )
    add_concept_fact = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="addConceptFact",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
                (
                    "fact",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(FactInput),
                        graphql_name="fact",
                        default=None,
                    ),
                ),
                (
                    "performance_control",
                    sgqlc.types.Arg(
                        PerformSynchronously,
                        graphql_name="performanceControl",
                        default={"performSynchronously": True},
                    ),
                ),
            )
        ),
    )
    delete_concept_fact = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteConceptFact",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    add_concept_link_property_fact = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="addConceptLinkPropertyFact",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
                (
                    "fact",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(FactInput),
                        graphql_name="fact",
                        default=None,
                    ),
                ),
                (
                    "performance_control",
                    sgqlc.types.Arg(
                        PerformSynchronously,
                        graphql_name="performanceControl",
                        default={"performSynchronously": True},
                    ),
                ),
            )
        ),
    )
    delete_concept_link_property_fact = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteConceptLinkPropertyFact",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    add_concept_property_fact = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="addConceptPropertyFact",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
                (
                    "fact",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(FactInput),
                        graphql_name="fact",
                        default=None,
                    ),
                ),
                (
                    "performance_control",
                    sgqlc.types.Arg(
                        PerformSynchronously,
                        graphql_name="performanceControl",
                        default={"performSynchronously": True},
                    ),
                ),
            )
        ),
    )
    delete_concept_property_fact = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteConceptPropertyFact",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    add_concept_link_fact = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="addConceptLinkFact",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
                (
                    "fact",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(FactInput),
                        graphql_name="fact",
                        default=None,
                    ),
                ),
                (
                    "performance_control",
                    sgqlc.types.Arg(
                        PerformSynchronously,
                        graphql_name="performanceControl",
                        default={"performSynchronously": True},
                    ),
                ),
            )
        ),
    )
    delete_concept_link_fact = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteConceptLinkFact",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    update_concept = sgqlc.types.Field(
        sgqlc.types.non_null("Concept"),
        graphql_name="updateConcept",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
                (
                    "performance_control",
                    sgqlc.types.Arg(
                        PerformSynchronously,
                        graphql_name="performanceControl",
                        default={"performSynchronously": True},
                    ),
                ),
            )
        ),
    )
    update_concept_avatar = sgqlc.types.Field(
        sgqlc.types.non_null("Concept"),
        graphql_name="updateConceptAvatar",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
                (
                    "document_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ID),
                        graphql_name="documentId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_concept_property = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptProperty"),
        graphql_name="updateConceptProperty",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptPropertyUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_concept_property = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteConceptProperty",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    delete_concept_link = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteConceptLink",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    delete_concept = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteConcept",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    delete_concept_link_property = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteConceptLinkProperty",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    merge_concepts = sgqlc.types.Field(
        sgqlc.types.non_null("Concept"),
        graphql_name="mergeConcepts",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptMergeInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    unmerge_concepts = sgqlc.types.Field(
        sgqlc.types.non_null("Concept"),
        graphql_name="unmergeConcepts",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptUnmergeInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_fact = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteFact",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    normalize_value = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("Value"))),
        graphql_name="normalizeValue",
        args=sgqlc.types.ArgDict(
            (
                (
                    "input",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(NormalizationInput),
                        graphql_name="input",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_concept_subscriptions = sgqlc.types.Field(
        sgqlc.types.non_null("Concept"),
        graphql_name="updateConceptSubscriptions",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
                (
                    "events",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptUpdate))),
                        graphql_name="events",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_concept_type = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptType"),
        graphql_name="addConceptType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptTypeCreationInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
                ("file", sgqlc.types.Arg(Upload, graphql_name="file", default=None)),
            )
        ),
    )
    add_composite_concept_type = sgqlc.types.Field(
        sgqlc.types.non_null("CompositeConceptType"),
        graphql_name="addCompositeConceptType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(CompositeConceptTypeCreationInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_composite_concept_type_widget_type = sgqlc.types.Field(
        sgqlc.types.non_null("CompositeConceptTypeWidgetType"),
        graphql_name="addCompositeConceptTypeWidgetType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(CompositeConceptTypeWidgetTypeCreationInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    set_concept_type_default_view = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="setConceptTypeDefaultView",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(CompositeConceptTypeViewInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_concept_property_type = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptPropertyType"),
        graphql_name="addConceptPropertyType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptPropertyTypeCreationInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_concept_link_property_type = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptPropertyType"),
        graphql_name="addConceptLinkPropertyType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptLinkPropertyTypeCreationInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_concept_link_type = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptLinkType"),
        graphql_name="addConceptLinkType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptLinkTypeCreationInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_concept_property_value_type = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptPropertyValueType"),
        graphql_name="addConceptPropertyValueType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptPropertyValueTypeCreationInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_concept_type_view = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptTypeView"),
        graphql_name="addConceptTypeView",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptTypeViewCreationInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_concept_type = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptType"),
        graphql_name="updateConceptType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptTypeUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
                ("file", sgqlc.types.Arg(Upload, graphql_name="file", default=None)),
            )
        ),
    )
    update_composite_concept_type = sgqlc.types.Field(
        sgqlc.types.non_null("CompositeConceptType"),
        graphql_name="updateCompositeConceptType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(CompositeConceptTypeUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_composite_concept_type_widget_type = sgqlc.types.Field(
        sgqlc.types.non_null("CompositeConceptTypeWidgetType"),
        graphql_name="updateCompositeConceptTypeWidgetType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(CompositeConceptTypeWidgetTypeUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_composite_concept_type_widget_types_order = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="updateCompositeConceptTypeWidgetTypesOrder",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(CompositeConceptTypeWidgetTypeUpdateOrderInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_concept_property_type = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptPropertyType"),
        graphql_name="updateConceptPropertyType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptPropertyTypeUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_concept_main_property_type_order = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptType"),
        graphql_name="updateConceptMainPropertyTypeOrder",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(InterestObjectMainPropertiesOrderUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_concept_link_property_type = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptPropertyType"),
        graphql_name="updateConceptLinkPropertyType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptLinkPropertyTypeUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_concept_link_type = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptLinkType"),
        graphql_name="updateConceptLinkType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptLinkTypeUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_concept_property_value_type = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptPropertyValueType"),
        graphql_name="updateConceptPropertyValueType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptPropertyValueTypeUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_concept_type_view = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptTypeView"),
        graphql_name="updateConceptTypeView",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptTypeViewUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_concept_type_avatar = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptType"),
        graphql_name="deleteConceptTypeAvatar",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    delete_concept_type = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteConceptType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    delete_composite_concept_type = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteCompositeConceptType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    delete_composite_concept_type_widget_type = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteCompositeConceptTypeWidgetType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    delete_concept_property_type = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteConceptPropertyType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    delete_concept_link_property_type = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteConceptLinkPropertyType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    delete_concept_link_type = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteConceptLinkType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    delete_concept_property_value_type = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteConceptPropertyValueType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    delete_concept_type_view = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteConceptTypeView",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    delete_bulk = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of("State")),
        graphql_name="deleteBulk",
        args=sgqlc.types.ArgDict(
            (
                (
                    "ids",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
                        graphql_name="ids",
                        default=None,
                    ),
                ),
            )
        ),
    )
    move_bulk = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptType"))),
        graphql_name="moveBulk",
        args=sgqlc.types.ArgDict(
            (
                (
                    "ids",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
                        graphql_name="ids",
                        default=None,
                    ),
                ),
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Coordinate))),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_type_search_element = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="updateTypeSearchElement",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(TypeSearchElementUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_composite_property_value_template = sgqlc.types.Field(
        sgqlc.types.non_null("CompositePropertyValueTemplate"),
        graphql_name="addCompositePropertyValueTemplate",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(CompositePropertyValueTemplateCreateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_composite_property_value_template = sgqlc.types.Field(
        sgqlc.types.non_null("CompositePropertyValueTemplate"),
        graphql_name="updateCompositePropertyValueTemplate",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(CompositePropertyValueTemplateCreateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_composite_property_value_template = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteCompositePropertyValueTemplate",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    add_issue = sgqlc.types.Field(
        sgqlc.types.non_null("Issue"),
        graphql_name="addIssue",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(IssueCreationInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_issue = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteIssue",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    add_concept_to_issue = sgqlc.types.Field(
        sgqlc.types.non_null("Issue"),
        graphql_name="addConceptToIssue",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Concept2IssueInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_document_to_issue = sgqlc.types.Field(
        sgqlc.types.non_null("Issue"),
        graphql_name="addDocumentToIssue",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Document2IssueInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_issue_to_issue = sgqlc.types.Field(
        sgqlc.types.non_null("Issue"),
        graphql_name="addIssueToIssue",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Issue2TaskInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_document_from_issue = sgqlc.types.Field(
        sgqlc.types.non_null("Issue"),
        graphql_name="deleteDocumentFromIssue",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Document2IssueInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_concept_from_issue = sgqlc.types.Field(
        sgqlc.types.non_null("Issue"),
        graphql_name="deleteConceptFromIssue",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Concept2IssueInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_issue_from_issue = sgqlc.types.Field(
        sgqlc.types.non_null("Issue"),
        graphql_name="deleteIssueFromIssue",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Issue2TaskInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_issue = sgqlc.types.Field(
        sgqlc.types.non_null("Issue"),
        graphql_name="updateIssue",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(IssueEditFieldsInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_issue_massive = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="updateIssueMassive",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(MassUpdateIssueInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_comment_to_issue = sgqlc.types.Field(
        sgqlc.types.non_null("IssueChange"),
        graphql_name="addCommentToIssue",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Comment2IssueInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_issue_comment = sgqlc.types.Field(
        sgqlc.types.non_null("IssueChange"),
        graphql_name="updateIssueComment",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(UpdateCommentInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_issue_comment = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteIssueComment",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    update_document = sgqlc.types.Field(
        sgqlc.types.non_null("Document"),
        graphql_name="updateDocument",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DocumentUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_document_avatar = sgqlc.types.Field(
        sgqlc.types.non_null("Document"),
        graphql_name="updateDocumentAvatar",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DocumentAvatarUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_candidate_fact_from_document = sgqlc.types.Field(
        sgqlc.types.non_null("Document"),
        graphql_name="removeCandidateFactFromDocument",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DocumentDeleteCandidateFactInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    remove_all_kbfacts_from_document = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="removeAllKBFactsFromDocument",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DocumentAllKBFactsRemoveInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_documents = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteDocuments",
        args=sgqlc.types.ArgDict(
            (
                (
                    "ids",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
                        graphql_name="ids",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_document_double = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="addDocumentDouble",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DocumentDoubleCreationInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_document_node = sgqlc.types.Field(
        sgqlc.types.non_null("Document"),
        graphql_name="updateDocumentNode",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DocumentNodeUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_research_map = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteResearchMap",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    bulk_delete_research_map = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="bulkDeleteResearchMap",
        args=sgqlc.types.ArgDict(
            (
                (
                    "ids",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
                        graphql_name="ids",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_research_map = sgqlc.types.Field(
        sgqlc.types.non_null("ResearchMap"),
        graphql_name="addResearchMap",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ResearchMapCreationInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_research_map_from_files = sgqlc.types.Field(
        sgqlc.types.non_null("ResearchMapFromFilesType"),
        graphql_name="addResearchMapFromFiles",
        args=sgqlc.types.ArgDict(
            (
                (
                    "files",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(sgqlc.types.list_of(Upload)),
                        graphql_name="files",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_research_map = sgqlc.types.Field(
        sgqlc.types.non_null("ResearchMap"),
        graphql_name="updateResearchMap",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ResearchMapUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_content_on_research_map = sgqlc.types.Field(
        sgqlc.types.non_null("ResearchMap"),
        graphql_name="addContentOnResearchMap",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ResearchMapContentAddInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_content_from_research_map = sgqlc.types.Field(
        sgqlc.types.non_null("ResearchMap"),
        graphql_name="deleteContentFromResearchMap",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ResearchMapContentUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    batch_move_nodes_on_map = sgqlc.types.Field(
        sgqlc.types.non_null("ResearchMap"),
        graphql_name="batchMoveNodesOnMap",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ResearchMapBatchMoveInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    batch_update_group_on_map = sgqlc.types.Field(
        sgqlc.types.non_null("ResearchMap"),
        graphql_name="batchUpdateGroupOnMap",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ResearchMapBatchUpdateGroupInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_top_neighbors_on_map = sgqlc.types.Field(
        sgqlc.types.non_null("ResearchMap"),
        graphql_name="addTopNeighborsOnMap",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
                ("quantity", sgqlc.types.Arg(Int, graphql_name="quantity", default=10)),
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ResearchMapContentSelectInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_concept_fact_neighbors_on_map = sgqlc.types.Field(
        sgqlc.types.non_null("ResearchMap"),
        graphql_name="addConceptFactNeighborsOnMap",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
                (
                    "concept_id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="conceptId", default=None),
                ),
            )
        ),
    )
    set_research_map_active = sgqlc.types.Field(
        sgqlc.types.non_null("ResearchMap"),
        graphql_name="setResearchMapActive",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    find_shortest_path_on_map = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="findShortestPathOnMap",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
                (
                    "concept_ids",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptAddImplicitLinkInput),
                        graphql_name="conceptIds",
                        default=None,
                    ),
                ),
            )
        ),
    )
    find_shortest_implicit_path_on_map = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="findShortestImplicitPathOnMap",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
                (
                    "concept_ids",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptAddImplicitLinkInput),
                        graphql_name="conceptIds",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_group = sgqlc.types.Field(
        sgqlc.types.non_null(Group),
        graphql_name="addGroup",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GroupCreationInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_group = sgqlc.types.Field(
        sgqlc.types.non_null(Group),
        graphql_name="updateGroup",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(GroupUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_group = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteGroup",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    create_redmine_issue = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="createRedmineIssue",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(RedmineIssueCreationInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_redmine_issue = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="updateRedmineIssue",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(RedmineIssueUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    unlink_issues = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="unlinkIssues",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(RedmineIssueUnlinkInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_access_level = sgqlc.types.Field(
        sgqlc.types.non_null(AccessLevel),
        graphql_name="addAccessLevel",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AccessLevelCreationInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_access_level = sgqlc.types.Field(
        sgqlc.types.non_null(AccessLevel),
        graphql_name="updateAccessLevel",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AccessLevelUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_access_level = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteAccessLevel",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    add_template_docx = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="addTemplateDocx",
        args=sgqlc.types.ArgDict((("file", sgqlc.types.Arg(Upload, graphql_name="file", default=None)),)),
    )
    update_markers_bulk = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="updateMarkersBulk",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(BulkMarkersUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_platform = sgqlc.types.Field(
        sgqlc.types.non_null("Platform"),
        graphql_name="addPlatform",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(PlatformCreationInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
                ("file", sgqlc.types.Arg(Upload, graphql_name="file", default=None)),
            )
        ),
    )
    update_platform = sgqlc.types.Field(
        sgqlc.types.non_null("Platform"),
        graphql_name="updatePlatform",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(PlatformUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
                ("file", sgqlc.types.Arg(Upload, graphql_name="file", default=None)),
            )
        ),
    )
    delete_platform = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deletePlatform",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    add_account = sgqlc.types.Field(
        sgqlc.types.non_null("Account"),
        graphql_name="addAccount",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AccountCreationInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
                ("file", sgqlc.types.Arg(Upload, graphql_name="file", default=None)),
            )
        ),
    )
    update_account = sgqlc.types.Field(
        sgqlc.types.non_null("Account"),
        graphql_name="updateAccount",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AccountUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
                ("file", sgqlc.types.Arg(Upload, graphql_name="file", default=None)),
            )
        ),
    )
    delete_account = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteAccount",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    add_document_feed = sgqlc.types.Field(
        sgqlc.types.non_null("DocumentFeed"),
        graphql_name="addDocumentFeed",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DocumentFeedCreationInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    update_document_feed = sgqlc.types.Field(
        sgqlc.types.non_null("DocumentFeed"),
        graphql_name="updateDocumentFeed",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DocumentFeedUpdateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    add_document_to_document_feed_favorites = sgqlc.types.Field(
        sgqlc.types.non_null("DocumentFeed"),
        graphql_name="addDocumentToDocumentFeedFavorites",
        args=sgqlc.types.ArgDict(
            (
                (
                    "document_feed_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ID),
                        graphql_name="documentFeedId",
                        default=None,
                    ),
                ),
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DocumentFeedUpdateDocumentsInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_document_from_document_feed_favorites = sgqlc.types.Field(
        sgqlc.types.non_null("DocumentFeed"),
        graphql_name="deleteDocumentFromDocumentFeedFavorites",
        args=sgqlc.types.ArgDict(
            (
                (
                    "document_feed_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ID),
                        graphql_name="documentFeedId",
                        default=None,
                    ),
                ),
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DocumentFeedUpdateDocumentsInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_document_from_document_feed = sgqlc.types.Field(
        sgqlc.types.non_null("DocumentFeed"),
        graphql_name="deleteDocumentFromDocumentFeed",
        args=sgqlc.types.ArgDict(
            (
                (
                    "document_feed_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ID),
                        graphql_name="documentFeedId",
                        default=None,
                    ),
                ),
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DocumentFeedUpdateDocumentsInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    restore_document_to_document_feed = sgqlc.types.Field(
        sgqlc.types.non_null("DocumentFeed"),
        graphql_name="restoreDocumentToDocumentFeed",
        args=sgqlc.types.ArgDict(
            (
                (
                    "document_feed_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ID),
                        graphql_name="documentFeedId",
                        default=None,
                    ),
                ),
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DocumentFeedUpdateDocumentsInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    delete_document_feed = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="deleteDocumentFeed",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    add_alias_to_concept = sgqlc.types.Field(
        sgqlc.types.non_null("State"),
        graphql_name="addAliasToConcept",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AliasCreateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    get_or_add_account = sgqlc.types.Field(
        sgqlc.types.non_null(ID),
        graphql_name="getOrAddAccount",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AccountGetOrCreateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    get_or_add_platform = sgqlc.types.Field(
        sgqlc.types.non_null(ID),
        graphql_name="getOrAddPlatform",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(PlatformGetOrCreateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    get_or_add_concept = sgqlc.types.Field(
        sgqlc.types.non_null("Concept"),
        graphql_name="getOrAddConcept",
        args=sgqlc.types.ArgDict(
            (
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptMutationInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
                ("file", sgqlc.types.Arg(Upload, graphql_name="file", default=None)),
                (
                    "take_first_result",
                    sgqlc.types.Arg(Boolean, graphql_name="takeFirstResult", default=False),
                ),
            )
        ),
    )


class NERCRegexp(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("regexp", "context_regexp", "auto_create")
    regexp = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="regexp")
    context_regexp = sgqlc.types.Field(String, graphql_name="contextRegexp")
    auto_create = sgqlc.types.Field(Boolean, graphql_name="autoCreate")


class NamedValue(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("id", "property_value_type", "value")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    property_value_type = sgqlc.types.Field(
        sgqlc.types.non_null(CompositePropertyValueType),
        graphql_name="propertyValueType",
    )
    value = sgqlc.types.Field(sgqlc.types.non_null("Value"), graphql_name="value")


class ParagraphMetadata(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "page_id",
        "line_id",
        "original_text",
        "hidden",
        "text_translations",
        "paragraph_type",
    )
    page_id = sgqlc.types.Field(Int, graphql_name="pageId")
    line_id = sgqlc.types.Field(Int, graphql_name="lineId")
    original_text = sgqlc.types.Field(String, graphql_name="originalText")
    hidden = sgqlc.types.Field(Boolean, graphql_name="hidden")
    text_translations = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("Translation")),
        graphql_name="textTranslations",
    )
    paragraph_type = sgqlc.types.Field(sgqlc.types.non_null(NodeType), graphql_name="paragraphType")


class Parameter(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("key", "value")
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="key")
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="value")


class PdfSpecificMetadataGQL(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("author", "creation_date")
    author = sgqlc.types.Field(String, graphql_name="author")
    creation_date = sgqlc.types.Field(UnixTime, graphql_name="creationDate")


class PlatformPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("list_platform", "total")
    list_platform = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("Platform"))),
        graphql_name="listPlatform",
    )
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")


class PlatformStatistics(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("count_account", "count_doc")
    count_account = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countAccount")
    count_doc = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countDoc")


class Query(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "document",
        "story",
        "pagination_story",
        "pagination_document_markers",
        "concept_type",
        "composite_concept_type",
        "pagination_composite_concept_type",
        "concept_property_type",
        "concept_link_type",
        "concept_property_value_type",
        "list_concept_type",
        "list_user_menu_type",
        "list_concept_property_type",
        "list_concept_link_type",
        "list_concept_property_value_type",
        "pagination_concept_type",
        "pagination_concept_property_type",
        "pagination_concept_link_property_type",
        "pagination_concept_link_type",
        "pagination_concept_property_value_type",
        "composite_concept_property_type",
        "composite_link_property_type",
        "list_composite_concept_property_type",
        "list_composite_link_property_type",
        "pagination_composite_concept_property_type",
        "pagination_composite_link_property_type",
        "composite_property_value_template",
        "list_composite_property_value_template",
        "pagination_composite_property_value_template",
        "concept_type_view",
        "concept",
        "list_concept_by_id",
        "pagination_concept",
        "composite_concept",
        "pagination_composite_concept",
        "list_concept_link_between_fixed_concepts",
        "concept_property",
        "concept_link",
        "pagination_kbrelated_document",
        "issue",
        "pagination_issue",
        "pagination_issue_change",
        "research_map",
        "pagination_research_map",
        "active_research_map",
        "list_top_neighbors_on_map",
        "list_last_research_map",
        "document_autocomplete",
        "concept_autocomplete",
        "get_osm_place_name",
        "get_osm_coordinates",
        "get_redmine_issue_creation_default_parameters",
        "get_redmine_issue_update_default_description",
        "search_similar_redmine_issues",
        "access_level",
        "pagination_access_level",
        "story_fs2_query",
        "concept_fs2_query",
        "markers_bulk",
        "platform",
        "pagination_platform",
        "account",
        "pagination_account",
        "pagination_country",
        "pagination_language",
        "document_feed",
        "pagination_document_feed",
        "mention_search",
        "batch_mention_search",
        "list_document_for_time_period",
        "list_text_from_document_with_marker",
    )
    document = sgqlc.types.Field(
        "Document",
        graphql_name="document",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    story = sgqlc.types.Field(
        "Story",
        graphql_name="story",
        args=sgqlc.types.ArgDict(
            (
                (
                    "ids",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
                        graphql_name="ids",
                        default=None,
                    ),
                ),
            )
        ),
    )
    pagination_story = sgqlc.types.Field(
        sgqlc.types.non_null("StoryPagination"),
        graphql_name="paginationStory",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "grouping",
                    sgqlc.types.Arg(DocumentGrouping, graphql_name="grouping", default="none"),
                ),
                ("query", sgqlc.types.Arg(String, graphql_name="query", default=None)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        DocumentFilterSettings,
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
                (
                    "sort_field",
                    sgqlc.types.Arg(DocumentSorting, graphql_name="sortField", default="score"),
                ),
                (
                    "extra_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ExtraSettings),
                        graphql_name="extraSettings",
                        default=None,
                    ),
                ),
            )
        ),
    )
    pagination_document_markers = sgqlc.types.Field(
        sgqlc.types.non_null(CommonStringPagination),
        graphql_name="paginationDocumentMarkers",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
            )
        ),
    )
    concept_type = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptType"),
        graphql_name="conceptType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    composite_concept_type = sgqlc.types.Field(
        sgqlc.types.non_null("CompositeConceptType"),
        graphql_name="compositeConceptType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    pagination_composite_concept_type = sgqlc.types.Field(
        sgqlc.types.non_null(CompositeConceptTypePagination),
        graphql_name="paginationCompositeConceptType",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(CompositeConceptTypeFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
                (
                    "sort_field",
                    sgqlc.types.Arg(
                        CompositeConceptTypeSorting,
                        graphql_name="sortField",
                        default="id",
                    ),
                ),
            )
        ),
    )
    concept_property_type = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptPropertyType"),
        graphql_name="conceptPropertyType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    concept_link_type = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptLinkType"),
        graphql_name="conceptLinkType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    concept_property_value_type = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptPropertyValueType"),
        graphql_name="conceptPropertyValueType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    list_concept_type = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptType"))),
        graphql_name="listConceptType",
    )
    list_user_menu_type = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("UserMenuType"))),
        graphql_name="listUserMenuType",
    )
    list_concept_property_type = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptPropertyType"))),
        graphql_name="listConceptPropertyType",
    )
    list_concept_link_type = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptLinkType"))),
        graphql_name="listConceptLinkType",
    )
    list_concept_property_value_type = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptPropertyValueType"))),
        graphql_name="listConceptPropertyValueType",
    )
    pagination_concept_type = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptTypePagination),
        graphql_name="paginationConceptType",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptTypeFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
                (
                    "sort_field",
                    sgqlc.types.Arg(ConceptTypeSorting, graphql_name="sortField", default="id"),
                ),
            )
        ),
    )
    pagination_concept_property_type = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptPropertyTypePagination),
        graphql_name="paginationConceptPropertyType",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptPropertyTypeFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
                (
                    "sort_field",
                    sgqlc.types.Arg(
                        ConceptPropertyTypeSorting,
                        graphql_name="sortField",
                        default="name",
                    ),
                ),
            )
        ),
    )
    pagination_concept_link_property_type = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptPropertyTypePagination),
        graphql_name="paginationConceptLinkPropertyType",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptPropertyTypeFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
                (
                    "sort_field",
                    sgqlc.types.Arg(
                        ConceptPropertyTypeSorting,
                        graphql_name="sortField",
                        default="name",
                    ),
                ),
            )
        ),
    )
    pagination_concept_link_type = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptLinkTypePagination),
        graphql_name="paginationConceptLinkType",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptLinkTypeFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
                (
                    "sort_field",
                    sgqlc.types.Arg(ConceptLinkTypeSorting, graphql_name="sortField", default="id"),
                ),
            )
        ),
    )
    pagination_concept_property_value_type = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptPropertyValueTypePagination),
        graphql_name="paginationConceptPropertyValueType",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptPropertyValueTypeFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
                (
                    "sort_field",
                    sgqlc.types.Arg(
                        ConceptPropertyValueTypeSorting,
                        graphql_name="sortField",
                        default="id",
                    ),
                ),
            )
        ),
    )
    composite_concept_property_type = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptPropertyType"),
        graphql_name="compositeConceptPropertyType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    composite_link_property_type = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptPropertyType"),
        graphql_name="compositeLinkPropertyType",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    list_composite_concept_property_type = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptPropertyType"))),
        graphql_name="listCompositeConceptPropertyType",
    )
    list_composite_link_property_type = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptPropertyType"))),
        graphql_name="listCompositeLinkPropertyType",
    )
    pagination_composite_concept_property_type = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptPropertyTypePagination),
        graphql_name="paginationCompositeConceptPropertyType",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(CompositePropertyTypeFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
                (
                    "sort_field",
                    sgqlc.types.Arg(
                        CompositePropertyTypeSorting,
                        graphql_name="sortField",
                        default="name",
                    ),
                ),
            )
        ),
    )
    pagination_composite_link_property_type = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptPropertyTypePagination),
        graphql_name="paginationCompositeLinkPropertyType",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(CompositePropertyTypeFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
                (
                    "sort_field",
                    sgqlc.types.Arg(
                        CompositePropertyTypeSorting,
                        graphql_name="sortField",
                        default="name",
                    ),
                ),
            )
        ),
    )
    composite_property_value_template = sgqlc.types.Field(
        sgqlc.types.non_null("CompositePropertyValueTemplate"),
        graphql_name="compositePropertyValueTemplate",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    list_composite_property_value_template = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("CompositePropertyValueTemplate"))),
        graphql_name="listCompositePropertyValueTemplate",
    )
    pagination_composite_property_value_template = sgqlc.types.Field(
        sgqlc.types.non_null(CompositePropertyValueTemplatePagination),
        graphql_name="paginationCompositePropertyValueTemplate",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(CompositePropertyValueTemplateFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
                (
                    "sort_field",
                    sgqlc.types.Arg(
                        CompositePropertyValueTemplateSorting,
                        graphql_name="sortField",
                        default="id",
                    ),
                ),
            )
        ),
    )
    concept_type_view = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptTypeView"),
        graphql_name="conceptTypeView",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    concept = sgqlc.types.Field(
        "Concept",
        graphql_name="concept",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    list_concept_by_id = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of("Concept")),
        graphql_name="listConceptById",
        args=sgqlc.types.ArgDict(
            (
                (
                    "ids",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
                        graphql_name="ids",
                        default=None,
                    ),
                ),
            )
        ),
    )
    pagination_concept = sgqlc.types.Field(
        ConceptPagination,
        graphql_name="paginationConcept",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("query", sgqlc.types.Arg(String, graphql_name="query", default=None)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        ConceptFilterSettings,
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
                (
                    "sort_field",
                    sgqlc.types.Arg(ConceptSorting, graphql_name="sortField", default="score"),
                ),
            )
        ),
    )
    composite_concept = sgqlc.types.Field(
        sgqlc.types.non_null(CompositeConcept),
        graphql_name="compositeConcept",
        args=sgqlc.types.ArgDict(
            (
                (
                    "composite_concept_type_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ID),
                        graphql_name="compositeConceptTypeId",
                        default=None,
                    ),
                ),
                (
                    "root_concept_id",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ID),
                        graphql_name="rootConceptId",
                        default=None,
                    ),
                ),
            )
        ),
    )
    pagination_composite_concept = sgqlc.types.Field(
        sgqlc.types.non_null(CompositeConceptPagination),
        graphql_name="paginationCompositeConcept",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("query", sgqlc.types.Arg(String, graphql_name="query", default=None)),
                (
                    "composite_concept_filter_settings",
                    sgqlc.types.Arg(
                        CompositeConceptFilterSettings,
                        graphql_name="compositeConceptFilterSettings",
                        default=None,
                    ),
                ),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
                (
                    "sort_field",
                    sgqlc.types.Arg(ConceptSorting, graphql_name="sortField", default="score"),
                ),
            )
        ),
    )
    list_concept_link_between_fixed_concepts = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptLink"))),
        graphql_name="listConceptLinkBetweenFixedConcepts",
        args=sgqlc.types.ArgDict(
            (
                (
                    "ids",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))),
                        graphql_name="ids",
                        default=None,
                    ),
                ),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptLinkFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
            )
        ),
    )
    concept_property = sgqlc.types.Field(
        "ConceptProperty",
        graphql_name="conceptProperty",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    concept_link = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptLink"),
        graphql_name="conceptLink",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    pagination_kbrelated_document = sgqlc.types.Field(
        DocumentPagination,
        graphql_name="paginationKBRelatedDocument",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(RelatedDocumentFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
            )
        ),
    )
    issue = sgqlc.types.Field(
        "Issue",
        graphql_name="issue",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    pagination_issue = sgqlc.types.Field(
        IssuePagination,
        graphql_name="paginationIssue",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(IssueFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
                (
                    "sort_field",
                    sgqlc.types.Arg(IssueSorting, graphql_name="sortField", default="id"),
                ),
            )
        ),
    )
    pagination_issue_change = sgqlc.types.Field(
        sgqlc.types.non_null(IssueChangePagination),
        graphql_name="paginationIssueChange",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
            )
        ),
    )
    research_map = sgqlc.types.Field(
        sgqlc.types.non_null("ResearchMap"),
        graphql_name="researchMap",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    pagination_research_map = sgqlc.types.Field(
        sgqlc.types.non_null("ResearchMapPagination"),
        graphql_name="paginationResearchMap",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ResearchMapFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
                (
                    "sort_field",
                    sgqlc.types.Arg(ResearchMapSorting, graphql_name="sortField", default="id"),
                ),
            )
        ),
    )
    active_research_map = sgqlc.types.Field("ResearchMap", graphql_name="activeResearchMap")
    list_top_neighbors_on_map = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptWithNeighbors))),
        graphql_name="listTopNeighborsOnMap",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ResearchMapContentSelectInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
                ("quantity", sgqlc.types.Arg(Int, graphql_name="quantity", default=10)),
            )
        ),
    )
    list_last_research_map = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ResearchMap"))),
        graphql_name="listLastResearchMap",
    )
    document_autocomplete = sgqlc.types.Field(
        sgqlc.types.non_null(Autocomplete),
        graphql_name="documentAutocomplete",
        args=sgqlc.types.ArgDict(
            (
                (
                    "destination",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AutocompleteDocumentDestination),
                        graphql_name="destination",
                        default=None,
                    ),
                ),
                (
                    "query",
                    sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name="query", default=None),
                ),
            )
        ),
    )
    concept_autocomplete = sgqlc.types.Field(
        sgqlc.types.non_null(Autocomplete),
        graphql_name="conceptAutocomplete",
        args=sgqlc.types.ArgDict(
            (
                (
                    "destination",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AutocompleteConceptDestination),
                        graphql_name="destination",
                        default=None,
                    ),
                ),
                (
                    "query",
                    sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name="query", default=None),
                ),
            )
        ),
    )
    get_osm_place_name = sgqlc.types.Field(
        sgqlc.types.non_null(GeoPointValue),
        graphql_name="getOsmPlaceName",
        args=sgqlc.types.ArgDict(
            (
                (
                    "latitude",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Float),
                        graphql_name="latitude",
                        default=None,
                    ),
                ),
                (
                    "longitude",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(Float),
                        graphql_name="longitude",
                        default=None,
                    ),
                ),
            )
        ),
    )
    get_osm_coordinates = sgqlc.types.Field(
        sgqlc.types.non_null(GeoPointValue),
        graphql_name="getOsmCoordinates",
        args=sgqlc.types.ArgDict(
            (
                (
                    "name",
                    sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name="name", default=None),
                ),
            )
        ),
    )
    get_redmine_issue_creation_default_parameters = sgqlc.types.Field(
        sgqlc.types.non_null("RedmineIssueCreationDefaultParameters"),
        graphql_name="getRedmineIssueCreationDefaultParameters",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(RedmineIssueDefaultParametersInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    get_redmine_issue_update_default_description = sgqlc.types.Field(
        sgqlc.types.non_null(String),
        graphql_name="getRedmineIssueUpdateDefaultDescription",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(RedmineIssueDefaultParametersInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    search_similar_redmine_issues = sgqlc.types.Field(
        sgqlc.types.non_null("RedmineIssuePagination"),
        graphql_name="searchSimilarRedmineIssues",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    access_level = sgqlc.types.Field(
        sgqlc.types.non_null(AccessLevel),
        graphql_name="accessLevel",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    pagination_access_level = sgqlc.types.Field(
        sgqlc.types.non_null(AccessLevelPagination),
        graphql_name="paginationAccessLevel",
        args=sgqlc.types.ArgDict(
            (
                ("query", sgqlc.types.Arg(String, graphql_name="query", default=None)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
                (
                    "sort_field",
                    sgqlc.types.Arg(AccessLevelSorting, graphql_name="sortField", default="id"),
                ),
            )
        ),
    )
    story_fs2_query = sgqlc.types.Field(
        sgqlc.types.non_null(String),
        graphql_name="storyFs2Query",
        args=sgqlc.types.ArgDict(
            (
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DocumentFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "extra_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ExtraSettings),
                        graphql_name="extraSettings",
                        default=None,
                    ),
                ),
            )
        ),
    )
    concept_fs2_query = sgqlc.types.Field(
        sgqlc.types.non_null(String),
        graphql_name="conceptFs2Query",
        args=sgqlc.types.ArgDict(
            (
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
            )
        ),
    )
    markers_bulk = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(Markers)),
        graphql_name="markersBulk",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(BulkMarkersInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    platform = sgqlc.types.Field(
        sgqlc.types.non_null("Platform"),
        graphql_name="platform",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    pagination_platform = sgqlc.types.Field(
        sgqlc.types.non_null(PlatformPagination),
        graphql_name="paginationPlatform",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(PlatformFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
                (
                    "sort_field",
                    sgqlc.types.Arg(PlatformSorting, graphql_name="sortField", default="id"),
                ),
            )
        ),
    )
    account = sgqlc.types.Field(
        sgqlc.types.non_null("Account"),
        graphql_name="account",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    pagination_account = sgqlc.types.Field(
        sgqlc.types.non_null(AccountPagination),
        graphql_name="paginationAccount",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AccountFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
                (
                    "sort_field",
                    sgqlc.types.Arg(AccountSorting, graphql_name="sortField", default="id"),
                ),
            )
        ),
    )
    pagination_country = sgqlc.types.Field(
        sgqlc.types.non_null(CountryPagination),
        graphql_name="paginationCountry",
        args=sgqlc.types.ArgDict(
            (
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(CountryFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
            )
        ),
    )
    pagination_language = sgqlc.types.Field(
        sgqlc.types.non_null(LanguagePagination),
        graphql_name="paginationLanguage",
        args=sgqlc.types.ArgDict(
            (
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(LanguageFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
            )
        ),
    )
    document_feed = sgqlc.types.Field(
        sgqlc.types.non_null("DocumentFeed"),
        graphql_name="documentFeed",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )
    pagination_document_feed = sgqlc.types.Field(
        sgqlc.types.non_null(DocumentFeedPagination),
        graphql_name="paginationDocumentFeed",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DocumentFeedFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
                (
                    "sort_field",
                    sgqlc.types.Arg(DocumentFeedSorting, graphql_name="sortField", default="id"),
                ),
            )
        ),
    )
    mention_search = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptMentionCount))),
        graphql_name="mentionSearch",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptMentionCountInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=5)),
                (
                    "extend_results",
                    sgqlc.types.Arg(Boolean, graphql_name="extendResults", default=False),
                ),
            )
        ),
    )
    batch_mention_search = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptMentionCount))))),
        graphql_name="batchMentionSearch",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptMentionCountBatchInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    list_document_for_time_period = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("Document"))),
        graphql_name="listDocumentForTimePeriod",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DocumentsWithConceptByDateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )
    list_text_from_document_with_marker = sgqlc.types.Field(
        sgqlc.types.non_null(ListsTextsFromDocumentWithMarkerResponse),
        graphql_name="listTextFromDocumentWithMarker",
        args=sgqlc.types.ArgDict(
            (
                (
                    "form",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DocumentsTextWithMarkerByDateInput),
                        graphql_name="form",
                        default=None,
                    ),
                ),
            )
        ),
    )


class RecordInterface(sgqlc.types.Interface):
    __schema__ = api_schema
    __field_names__ = (
        "system_registration_date",
        "system_update_date",
        "creator",
        "last_updater",
    )
    system_registration_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name="systemRegistrationDate")
    system_update_date = sgqlc.types.Field(UnixTime, graphql_name="systemUpdateDate")
    creator = sgqlc.types.Field(sgqlc.types.non_null("User"), graphql_name="creator")
    last_updater = sgqlc.types.Field("User", graphql_name="lastUpdater")


class RedmineIssue(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "subject",
        "tracker",
        "status",
        "priority",
        "author",
        "assignee",
        "creation_date",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    subject = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="subject")
    tracker = sgqlc.types.Field(sgqlc.types.non_null("RedmineTracker"), graphql_name="tracker")
    status = sgqlc.types.Field(sgqlc.types.non_null("RedmineStatus"), graphql_name="status")
    priority = sgqlc.types.Field(sgqlc.types.non_null("RedminePriority"), graphql_name="priority")
    author = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="author")
    assignee = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="assignee")
    creation_date = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name="creationDate")


class RedmineIssueCreationDefaultParameters(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "subject",
        "description",
        "users",
        "trackers",
        "statuses",
        "priorities",
    )
    subject = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="subject")
    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="description")
    users = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("RedmineUser"))),
        graphql_name="users",
    )
    trackers = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("RedmineTracker"))),
        graphql_name="trackers",
    )
    statuses = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("RedmineStatus"))),
        graphql_name="statuses",
    )
    priorities = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("RedminePriority"))),
        graphql_name="priorities",
    )


class RedmineIssuePagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("list_redmine_issue", "total")
    list_redmine_issue = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(RedmineIssue))),
        graphql_name="listRedmineIssue",
    )
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")


class RedminePriority(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("id", "name")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")


class RedmineStatus(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("id", "name")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")


class RedmineTracker(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("id", "name")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")


class RedmineUser(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("id", "full_name")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    full_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="fullName")


class RelExtModel(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "source_annotation_type",
        "target_annotation_type",
        "relation_type",
        "invert_direction",
    )
    source_annotation_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="sourceAnnotationType")
    target_annotation_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="targetAnnotationType")
    relation_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="relationType")
    invert_direction = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="invertDirection")


class ResearchMapChangedEvent(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("event_name", "research_map")
    event_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="eventName")
    research_map = sgqlc.types.Field(sgqlc.types.non_null("ResearchMap"), graphql_name="researchMap")


class ResearchMapFromFilesType(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("research_maps", "info")
    research_maps = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ResearchMap"))),
        graphql_name="researchMaps",
    )
    info = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of("State")), graphql_name="info")


class ResearchMapPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("total", "list_research_map")
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")
    list_research_map = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ResearchMap"))),
        graphql_name="listResearchMap",
    )


class ResearchMapStatistics(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "object_num",
        "event_num",
        "document_num",
        "concept_num",
        "concept_and_document_num",
    )
    object_num = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="objectNum")
    event_num = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="eventNum")
    document_num = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="documentNum")
    concept_num = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="conceptNum")
    concept_and_document_num = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="conceptAndDocumentNum")


class State(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("is_success",)
    is_success = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isSuccess")


class Story(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "title",
        "system_registration_date",
        "system_update_date",
        "main",
        "list_document",
        "highlighting",
        "count_doc",
        "preview",
        "access_level",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    title = sgqlc.types.Field(String, graphql_name="title")
    system_registration_date = sgqlc.types.Field(sgqlc.types.non_null(UnixTime), graphql_name="systemRegistrationDate")
    system_update_date = sgqlc.types.Field(UnixTime, graphql_name="systemUpdateDate")
    main = sgqlc.types.Field(sgqlc.types.non_null("Document"), graphql_name="main")
    list_document = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("Document"))),
        graphql_name="listDocument",
    )
    highlighting = sgqlc.types.Field(Highlighting, graphql_name="highlighting")
    count_doc = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="countDoc")
    preview = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="preview")
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name="accessLevel")


class StoryPagination(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = (
        "list_story",
        "total",
        "show_total",
        "list_named_entity_count_facet",
        "list_concept_count_facet",
        "list_markers",
        "sources",
        "new_documents_today",
    )
    list_story = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Story))),
        graphql_name="listStory",
    )
    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")
    show_total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="showTotal")
    list_named_entity_count_facet = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CountFacet))),
        graphql_name="listNamedEntityCountFacet",
    )
    list_concept_count_facet = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CountFacet))),
        graphql_name="listConceptCountFacet",
    )
    list_markers = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CountFacet))),
        graphql_name="listMarkers",
    )
    sources = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="sources")
    new_documents_today = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="newDocumentsToday")


class StringLocaleValue(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("value", "locale")
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="value")
    locale = sgqlc.types.Field(sgqlc.types.non_null(Locale), graphql_name="locale")


class StringValue(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("value",)
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="value")


class Subscription(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("research_map_changed",)
    research_map_changed = sgqlc.types.Field(
        sgqlc.types.non_null(ResearchMapChangedEvent),
        graphql_name="researchMapChanged",
        args=sgqlc.types.ArgDict(
            (
                (
                    "id",
                    sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None),
                ),
            )
        ),
    )


class Table(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("cells", "metadata")
    cells = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))))),
        graphql_name="cells",
    )
    metadata = sgqlc.types.Field(sgqlc.types.non_null("TableMetadata"), graphql_name="metadata")


class TableMetadata(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("page_id",)
    page_id = sgqlc.types.Field(Int, graphql_name="pageId")


class TextBounding(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("start", "end", "node_id")
    start = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="start")
    end = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="end")
    node_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="nodeId")


class Time(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("hour", "minute", "second")
    hour = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="hour")
    minute = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="minute")
    second = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="second")


class Translation(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("text", "language")
    text = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="text")
    language = sgqlc.types.Field(sgqlc.types.non_null(Language), graphql_name="language")


class User(sgqlc.types.Type):
    __schema__ = api_schema
    __field_names__ = ("id",)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")


class Account(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "name",
        "url",
        "country",
        "markers",
        "params",
        "platform",
        "image",
        "metric",
        "period",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="url")
    country = sgqlc.types.Field(String, graphql_name="country")
    markers = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="markers",
    )
    params = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Parameter))),
        graphql_name="params",
    )
    platform = sgqlc.types.Field(sgqlc.types.non_null("Platform"), graphql_name="platform")
    image = sgqlc.types.Field(String, graphql_name="image")
    metric = sgqlc.types.Field(sgqlc.types.non_null(AccountStatistics), graphql_name="metric")
    period = sgqlc.types.Field(sgqlc.types.non_null(DateTimeInterval), graphql_name="period")


class CompositeConceptType(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "name",
        "root_concept_type",
        "is_default",
        "layout",
        "has_supporting_documents",
        "has_header_information",
        "metric",
        "pagination_widget_type",
        "list_widget_type",
        "list_concept_link_types_composite_concept_type_consists_of",
        "show_in_menu",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    root_concept_type = sgqlc.types.Field(sgqlc.types.non_null("ConceptType"), graphql_name="rootConceptType")
    is_default = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isDefault")
    layout = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="layout")
    has_supporting_documents = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="hasSupportingDocuments")
    has_header_information = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="hasHeaderInformation")
    metric = sgqlc.types.Field(sgqlc.types.non_null(CompositeConceptStatistics), graphql_name="metric")
    pagination_widget_type = sgqlc.types.Field(
        sgqlc.types.non_null(CompositeConceptTypeWidgetTypePagination),
        graphql_name="paginationWidgetType",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "sort_direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="sortDirection", default="ascending"),
                ),
                (
                    "sorting",
                    sgqlc.types.Arg(
                        CompositeConceptTypeWidgetTypeSorting,
                        graphql_name="sorting",
                        default="order",
                    ),
                ),
            )
        ),
    )
    list_widget_type = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("CompositeConceptTypeWidgetType"))),
        graphql_name="listWidgetType",
    )
    list_concept_link_types_composite_concept_type_consists_of = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptLinkType"))),
        graphql_name="listConceptLinkTypesCompositeConceptTypeConsistsOf",
    )
    show_in_menu = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="showInMenu")


class CompositeConceptTypeWidgetType(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "name",
        "table_type",
        "composite_concept_type",
        "hierarchy",
        "columns_info",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    table_type = sgqlc.types.Field(sgqlc.types.non_null(WidgetTypeTableType), graphql_name="tableType")
    composite_concept_type = sgqlc.types.Field(sgqlc.types.non_null(CompositeConceptType), graphql_name="compositeConceptType")
    hierarchy = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptLinkType"))))),
        graphql_name="hierarchy",
    )
    columns_info = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CompositeConceptTypeWidgetTypeColumn))),
        graphql_name="columnsInfo",
    )


class CompositePropertyValueTemplate(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ("id", "name", "component_value_types")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    component_value_types = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CompositePropertyValueType))),
        graphql_name="componentValueTypes",
    )


class Concept(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "is_actual",
        "name",
        "notes",
        "markers",
        "start_date",
        "end_date",
        "concept_type",
        "pagination_concept_property",
        "pagination_concept_link",
        "pagination_concept_fact",
        "pagination_concept_property_documents",
        "pagination_concept_link_documents",
        "list_concept_fact",
        "image",
        "metric",
        "list_alias",
        "pagination_alias",
        "pagination_merged_concept",
        "list_header_concept_property",
        "pagination_redmine_issues",
        "pagination_issue",
        "access_level",
        "list_subscription",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    is_actual = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isActual")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    notes = sgqlc.types.Field(String, graphql_name="notes")
    markers = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="markers",
    )
    start_date = sgqlc.types.Field(DateTimeValue, graphql_name="startDate")
    end_date = sgqlc.types.Field(DateTimeValue, graphql_name="endDate")
    concept_type = sgqlc.types.Field(sgqlc.types.non_null("ConceptType"), graphql_name="conceptType")
    pagination_concept_property = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptPropertyPagination),
        graphql_name="paginationConceptProperty",
        args=sgqlc.types.ArgDict(
            (
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptPropertyFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
            )
        ),
    )
    pagination_concept_link = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptLinkPagination),
        graphql_name="paginationConceptLink",
        args=sgqlc.types.ArgDict(
            (
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptLinkFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
            )
        ),
    )
    pagination_concept_fact = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptFactPagination),
        graphql_name="paginationConceptFact",
        args=sgqlc.types.ArgDict(
            (
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DocumentLinkFilterSetting),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
            )
        ),
    )
    pagination_concept_property_documents = sgqlc.types.Field(
        sgqlc.types.non_null(DocumentPagination),
        graphql_name="paginationConceptPropertyDocuments",
        args=sgqlc.types.ArgDict(
            (
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptPropertyFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
            )
        ),
    )
    pagination_concept_link_documents = sgqlc.types.Field(
        sgqlc.types.non_null(DocumentPagination),
        graphql_name="paginationConceptLinkDocuments",
        args=sgqlc.types.ArgDict(
            (
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptLinkFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
            )
        ),
    )
    list_concept_fact = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptFact"))),
        graphql_name="listConceptFact",
    )
    image = sgqlc.types.Field(String, graphql_name="image")
    metric = sgqlc.types.Field(sgqlc.types.non_null(ConceptStatistics), graphql_name="metric")
    list_alias = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptProperty"))),
        graphql_name="listAlias",
    )
    pagination_alias = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptPropertyPagination),
        graphql_name="paginationAlias",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
            )
        ),
    )
    pagination_merged_concept = sgqlc.types.Field(
        sgqlc.types.non_null(MergedConceptPagination),
        graphql_name="paginationMergedConcept",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
            )
        ),
    )
    list_header_concept_property = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptProperty"))),
        graphql_name="listHeaderConceptProperty",
    )
    pagination_redmine_issues = sgqlc.types.Field(
        sgqlc.types.non_null(RedmineIssuePagination),
        graphql_name="paginationRedmineIssues",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "sort_direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="sortDirection", default="ascending"),
                ),
            )
        ),
    )
    pagination_issue = sgqlc.types.Field(
        sgqlc.types.non_null(IssuePagination),
        graphql_name="paginationIssue",
        args=sgqlc.types.ArgDict(
            (
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(IssueFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "sort_direction",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(SortDirection),
                        graphql_name="sortDirection",
                        default=None,
                    ),
                ),
                (
                    "sorting",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(IssueSorting),
                        graphql_name="sorting",
                        default=None,
                    ),
                ),
            )
        ),
    )
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name="accessLevel")
    list_subscription = sgqlc.types.Field(sgqlc.types.non_null(ConceptSubscriptions), graphql_name="listSubscription")


class ConceptCandidateFact(sgqlc.types.Type, FactInterface):
    __schema__ = api_schema
    __field_names__ = ("name", "concept_type", "list_concept")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    concept_type = sgqlc.types.Field(sgqlc.types.non_null("ConceptType"), graphql_name="conceptType")
    list_concept = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Concept))),
        graphql_name="listConcept",
    )


class ConceptFact(sgqlc.types.Type, FactInterface, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ("access_level", "concept")
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name="accessLevel")
    concept = sgqlc.types.Field(sgqlc.types.non_null(Concept), graphql_name="concept")


class ConceptLink(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "concept_from_id",
        "concept_to_id",
        "notes",
        "start_date",
        "end_date",
        "concept_from",
        "concept_to",
        "concept_link_type",
        "pagination_concept_link_property",
        "pagination_concept_link_property_documents",
        "pagination_document",
        "list_concept_link_fact",
        "access_level",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    concept_from_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptFromId")
    concept_to_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="conceptToId")
    notes = sgqlc.types.Field(String, graphql_name="notes")
    start_date = sgqlc.types.Field(DateTimeValue, graphql_name="startDate")
    end_date = sgqlc.types.Field(DateTimeValue, graphql_name="endDate")
    concept_from = sgqlc.types.Field(sgqlc.types.non_null(Concept), graphql_name="conceptFrom")
    concept_to = sgqlc.types.Field(sgqlc.types.non_null(Concept), graphql_name="conceptTo")
    concept_link_type = sgqlc.types.Field(sgqlc.types.non_null("ConceptLinkType"), graphql_name="conceptLinkType")
    pagination_concept_link_property = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptPropertyPagination),
        graphql_name="paginationConceptLinkProperty",
        args=sgqlc.types.ArgDict(
            (
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptPropertyFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
            )
        ),
    )
    pagination_concept_link_property_documents = sgqlc.types.Field(
        sgqlc.types.non_null(DocumentPagination),
        graphql_name="paginationConceptLinkPropertyDocuments",
        args=sgqlc.types.ArgDict(
            (
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptPropertyFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
            )
        ),
    )
    pagination_document = sgqlc.types.Field(
        sgqlc.types.non_null(DocumentPagination),
        graphql_name="paginationDocument",
        args=sgqlc.types.ArgDict(
            (
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
            )
        ),
    )
    list_concept_link_fact = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptLinkFact"))),
        graphql_name="listConceptLinkFact",
    )
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name="accessLevel")


class ConceptLinkCandidateFact(sgqlc.types.Type, FactInterface):
    __schema__ = api_schema
    __field_names__ = ("concept_link_type", "fact_from", "fact_to")
    concept_link_type = sgqlc.types.Field(sgqlc.types.non_null("ConceptLinkType"), graphql_name="conceptLinkType")
    fact_from = sgqlc.types.Field("ConceptLikeFact", graphql_name="factFrom")
    fact_to = sgqlc.types.Field("ConceptLikeFact", graphql_name="factTo")


class ConceptLinkFact(sgqlc.types.Type, FactInterface, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ("access_level", "concept_link")
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name="accessLevel")
    concept_link = sgqlc.types.Field(sgqlc.types.non_null(ConceptLink), graphql_name="conceptLink")


class ConceptLinkPropertyFact(sgqlc.types.Type, FactInterface, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ("parent_concept_link", "access_level", "concept_link_property")
    parent_concept_link = sgqlc.types.Field(sgqlc.types.non_null(ConceptLink), graphql_name="parentConceptLink")
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name="accessLevel")
    concept_link_property = sgqlc.types.Field(sgqlc.types.non_null("ConceptProperty"), graphql_name="conceptLinkProperty")


class ConceptLinkType(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "name",
        "is_directed",
        "is_hierarchical",
        "concept_from_type",
        "concept_to_type",
        "pretrained_rel_ext_models",
        "notify_on_update",
        "pagination_concept_link_property_type",
        "list_concept_link_property_type",
        "metric",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    is_directed = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isDirected")
    is_hierarchical = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isHierarchical")
    concept_from_type = sgqlc.types.Field(sgqlc.types.non_null("ConceptType"), graphql_name="conceptFromType")
    concept_to_type = sgqlc.types.Field(sgqlc.types.non_null("ConceptType"), graphql_name="conceptToType")
    pretrained_rel_ext_models = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(RelExtModel))),
        graphql_name="pretrainedRelExtModels",
    )
    notify_on_update = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="notifyOnUpdate")
    pagination_concept_link_property_type = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptPropertyTypePagination),
        graphql_name="paginationConceptLinkPropertyType",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptPropertyTypeFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "sort_direction",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(SortDirection),
                        graphql_name="sortDirection",
                        default=None,
                    ),
                ),
                (
                    "sorting",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptTypeSorting),
                        graphql_name="sorting",
                        default=None,
                    ),
                ),
            )
        ),
    )
    list_concept_link_property_type = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptPropertyType"))),
        graphql_name="listConceptLinkPropertyType",
    )
    metric = sgqlc.types.Field(sgqlc.types.non_null(ConceptLinkTypeStatistics), graphql_name="metric")


class ConceptProperty(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "is_main",
        "property_type",
        "notes",
        "start_date",
        "end_date",
        "pagination_document",
        "access_level",
        "value",
        "list_concept_property_fact",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    is_main = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isMain")
    property_type = sgqlc.types.Field(sgqlc.types.non_null("ConceptPropertyType"), graphql_name="propertyType")
    notes = sgqlc.types.Field(String, graphql_name="notes")
    start_date = sgqlc.types.Field(DateTimeValue, graphql_name="startDate")
    end_date = sgqlc.types.Field(DateTimeValue, graphql_name="endDate")
    pagination_document = sgqlc.types.Field(
        sgqlc.types.non_null(DocumentPagination),
        graphql_name="paginationDocument",
        args=sgqlc.types.ArgDict(
            (
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
            )
        ),
    )
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name="accessLevel")
    value = sgqlc.types.Field(sgqlc.types.non_null("AnyValue"), graphql_name="value")
    list_concept_property_fact = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptPropertyLikeFact"),
        graphql_name="listConceptPropertyFact",
    )


class ConceptPropertyCandidateFact(sgqlc.types.Type, FactInterface):
    __schema__ = api_schema
    __field_names__ = ("concept_property_type", "fact_to", "fact_from")
    concept_property_type = sgqlc.types.Field(sgqlc.types.non_null("ConceptPropertyType"), graphql_name="conceptPropertyType")
    fact_to = sgqlc.types.Field(sgqlc.types.non_null("ConceptPropertyValueCandidateFact"), graphql_name="factTo")
    fact_from = sgqlc.types.Field("ConceptLikeFact", graphql_name="factFrom")


class ConceptPropertyFact(sgqlc.types.Type, FactInterface, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ("parent_concept", "access_level", "concept_property")
    parent_concept = sgqlc.types.Field(sgqlc.types.non_null(Concept), graphql_name="parentConcept")
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name="accessLevel")
    concept_property = sgqlc.types.Field(sgqlc.types.non_null(ConceptProperty), graphql_name="conceptProperty")


class ConceptPropertyType(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "name",
        "pretrained_rel_ext_models",
        "notify_on_update",
        "computable_formula",
        "parent_concept_type",
        "parent_concept_link_type",
        "value_type",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    pretrained_rel_ext_models = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(RelExtModel))),
        graphql_name="pretrainedRelExtModels",
    )
    notify_on_update = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="notifyOnUpdate")
    computable_formula = sgqlc.types.Field(String, graphql_name="computableFormula")
    parent_concept_type = sgqlc.types.Field("ConceptType", graphql_name="parentConceptType")
    parent_concept_link_type = sgqlc.types.Field(ConceptLinkType, graphql_name="parentConceptLinkType")
    value_type = sgqlc.types.Field(sgqlc.types.non_null("AnyValueType"), graphql_name="valueType")


class ConceptPropertyValueCandidateFact(sgqlc.types.Type, FactInterface):
    __schema__ = api_schema
    __field_names__ = ("concept_property_value_type",)
    concept_property_value_type = sgqlc.types.Field(
        sgqlc.types.non_null("ConceptPropertyValueType"),
        graphql_name="conceptPropertyValueType",
    )


class ConceptPropertyValueType(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "name",
        "value_type",
        "list_white_dictionary",
        "pretrained_nercmodels",
        "list_white_regexp",
        "value_restriction",
        "list_black_dictionary",
        "metric",
        "list_concept_type",
        "pagination_concept_type",
        "list_concept_link_type",
        "pagination_concept_link_type",
        "list_black_regexp",
        "list_type_search_element",
        "list_type_black_search_element",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    value_type = sgqlc.types.Field(sgqlc.types.non_null(ValueType), graphql_name="valueType")
    list_white_dictionary = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="listWhiteDictionary",
    )
    pretrained_nercmodels = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="pretrainedNERCModels",
    )
    list_white_regexp = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(NERCRegexp))),
        graphql_name="listWhiteRegexp",
    )
    value_restriction = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="valueRestriction",
    )
    list_black_dictionary = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="listBlackDictionary",
    )
    metric = sgqlc.types.Field(sgqlc.types.non_null(ConceptPropertyValueStatistics), graphql_name="metric")
    list_concept_type = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("ConceptType"))),
        graphql_name="listConceptType",
    )
    pagination_concept_type = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptTypePagination),
        graphql_name="paginationConceptType",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
            )
        ),
    )
    list_concept_link_type = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptLinkType))),
        graphql_name="listConceptLinkType",
    )
    pagination_concept_link_type = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptLinkTypePagination),
        graphql_name="paginationConceptLinkType",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
            )
        ),
    )
    list_black_regexp = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(NERCRegexp))),
        graphql_name="listBlackRegexp",
    )
    list_type_search_element = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("TypeSearchElement"))),
        graphql_name="listTypeSearchElement",
    )
    list_type_black_search_element = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("TypeSearchElement"))),
        graphql_name="listTypeBlackSearchElement",
    )


class ConceptType(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "name",
        "x_coordinate",
        "y_coordinate",
        "list_white_dictionary",
        "pretrained_nercmodels",
        "list_white_regexp",
        "is_event",
        "list_black_dictionary",
        "pagination_concept_property_type",
        "metric",
        "pagination_concept_link_type",
        "pagination_concept_type_view",
        "list_composite_concept_type",
        "list_concept_property_type",
        "list_concept_link_type",
        "list_concept_header_property_type",
        "image",
        "non_configurable_dictionary",
        "show_in_menu",
        "list_black_regexp",
        "list_names_dictionary",
        "list_type_search_element",
        "list_type_black_search_element",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    x_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="xCoordinate")
    y_coordinate = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name="yCoordinate")
    list_white_dictionary = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="listWhiteDictionary",
    )
    pretrained_nercmodels = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="pretrainedNERCModels",
    )
    list_white_regexp = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(NERCRegexp))),
        graphql_name="listWhiteRegexp",
    )
    is_event = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isEvent")
    list_black_dictionary = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="listBlackDictionary",
    )
    pagination_concept_property_type = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptPropertyTypePagination),
        graphql_name="paginationConceptPropertyType",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptPropertyTypeFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "sort_direction",
                    sgqlc.types.Arg(
                        SortDirection,
                        graphql_name="sortDirection",
                        default="descending",
                    ),
                ),
                (
                    "sorting",
                    sgqlc.types.Arg(
                        ConceptPropertyTypeSorting,
                        graphql_name="sorting",
                        default="name",
                    ),
                ),
            )
        ),
    )
    metric = sgqlc.types.Field(sgqlc.types.non_null(ConceptTypeStatistics), graphql_name="metric")
    pagination_concept_link_type = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptLinkTypePagination),
        graphql_name="paginationConceptLinkType",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptLinkTypeFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "sort_direction",
                    sgqlc.types.Arg(
                        SortDirection,
                        graphql_name="sortDirection",
                        default="descending",
                    ),
                ),
                (
                    "sorting",
                    sgqlc.types.Arg(ConceptLinkTypeSorting, graphql_name="sorting", default="id"),
                ),
            )
        ),
    )
    pagination_concept_type_view = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptTypeViewPagination),
        graphql_name="paginationConceptTypeView",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
            )
        ),
    )
    list_composite_concept_type = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CompositeConceptType))),
        graphql_name="listCompositeConceptType",
    )
    list_concept_property_type = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptPropertyType))),
        graphql_name="listConceptPropertyType",
    )
    list_concept_link_type = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptLinkType))),
        graphql_name="listConceptLinkType",
    )
    list_concept_header_property_type = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptPropertyType))),
        graphql_name="listConceptHeaderPropertyType",
    )
    image = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="image")
    non_configurable_dictionary = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="nonConfigurableDictionary",
    )
    show_in_menu = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="showInMenu")
    list_black_regexp = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(NERCRegexp))),
        graphql_name="listBlackRegexp",
    )
    list_names_dictionary = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="listNamesDictionary",
    )
    list_type_search_element = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("TypeSearchElement"))),
        graphql_name="listTypeSearchElement",
    )
    list_type_black_search_element = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("TypeSearchElement"))),
        graphql_name="listTypeBlackSearchElement",
    )


class ConceptTypeView(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "name",
        "show_in_menu",
        "concept_type",
        "columns",
        "pagination_concept",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    show_in_menu = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="showInMenu")
    concept_type = sgqlc.types.Field(sgqlc.types.non_null(ConceptType), graphql_name="conceptType")
    columns = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CompositeConceptTypeWidgetTypeColumn))),
        graphql_name="columns",
    )
    pagination_concept = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptViewPagination),
        graphql_name="paginationConcept",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "sort_column",
                    sgqlc.types.Arg(ID, graphql_name="sortColumn", default=None),
                ),
                (
                    "sort_direction",
                    sgqlc.types.Arg(
                        SortDirection,
                        graphql_name="sortDirection",
                        default="descending",
                    ),
                ),
                ("query", sgqlc.types.Arg(String, graphql_name="query", default=None)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        ConceptFilterSettings,
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
            )
        ),
    )


class Document(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "title",
        "external_url",
        "publication_date",
        "publication_author",
        "notes",
        "document_type",
        "highlightings",
        "markers",
        "tables",
        "metadata",
        "uuid",
        "trust_level",
        "score",
        "has_text",
        "parent",
        "list_child",
        "pagination_child",
        "internal_url",
        "avatar",
        "metric",
        "pagination_concept_fact",
        "list_concept_fact",
        "pagination_concept_link_fact",
        "list_concept_link_document_fact",
        "preview",
        "pagination_redmine_issues",
        "pagination_issue",
        "access_level",
        "text",
        "story",
        "list_fact",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    title = sgqlc.types.Field(String, graphql_name="title")
    external_url = sgqlc.types.Field(String, graphql_name="externalUrl")
    publication_date = sgqlc.types.Field(UnixTime, graphql_name="publicationDate")
    publication_author = sgqlc.types.Field(String, graphql_name="publicationAuthor")
    notes = sgqlc.types.Field(String, graphql_name="notes")
    document_type = sgqlc.types.Field(sgqlc.types.non_null(DocumentType), graphql_name="documentType")
    highlightings = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Highlighting))),
        graphql_name="highlightings",
    )
    markers = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="markers",
    )
    tables = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Table))),
        graphql_name="tables",
    )
    metadata = sgqlc.types.Field(DocumentMetadata, graphql_name="metadata")
    uuid = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="uuid")
    trust_level = sgqlc.types.Field(TrustLevel, graphql_name="trustLevel")
    score = sgqlc.types.Field(Float, graphql_name="score")
    has_text = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="hasText")
    parent = sgqlc.types.Field("Document", graphql_name="parent")
    list_child = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("Document"))),
        graphql_name="listChild",
    )
    pagination_child = sgqlc.types.Field(
        sgqlc.types.non_null(DocumentPagination),
        graphql_name="paginationChild",
        args=sgqlc.types.ArgDict(
            (
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(DocumentLinkFilterSetting),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
            )
        ),
    )
    internal_url = sgqlc.types.Field(String, graphql_name="internalUrl")
    avatar = sgqlc.types.Field(String, graphql_name="avatar")
    metric = sgqlc.types.Field(sgqlc.types.non_null(Metrics), graphql_name="metric")
    pagination_concept_fact = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptFactPagination),
        graphql_name="paginationConceptFact",
        args=sgqlc.types.ArgDict(
            (
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
            )
        ),
    )
    list_concept_fact = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptFact))),
        graphql_name="listConceptFact",
    )
    pagination_concept_link_fact = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptLinkFactPagination),
        graphql_name="paginationConceptLinkFact",
        args=sgqlc.types.ArgDict(
            (
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
            )
        ),
    )
    list_concept_link_document_fact = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptLinkFact))),
        graphql_name="listConceptLinkDocumentFact",
    )
    preview = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="preview")
    pagination_redmine_issues = sgqlc.types.Field(
        sgqlc.types.non_null(RedmineIssuePagination),
        graphql_name="paginationRedmineIssues",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "sort_direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="sortDirection", default="ascending"),
                ),
            )
        ),
    )
    pagination_issue = sgqlc.types.Field(
        sgqlc.types.non_null(IssuePagination),
        graphql_name="paginationIssue",
        args=sgqlc.types.ArgDict(
            (
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(IssueFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "sort_direction",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(SortDirection),
                        graphql_name="sortDirection",
                        default=None,
                    ),
                ),
                (
                    "sorting",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(IssueSorting),
                        graphql_name="sorting",
                        default=None,
                    ),
                ),
            )
        ),
    )
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name="accessLevel")
    text = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(FlatDocumentStructure))),
        graphql_name="text",
        args=sgqlc.types.ArgDict(
            (
                (
                    "show_hidden",
                    sgqlc.types.Arg(Boolean, graphql_name="showHidden", default=False),
                ),
            )
        ),
    )
    story = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="story")
    list_fact = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("Fact"))),
        graphql_name="listFact",
    )


class DocumentFeed(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ("id", "name", "search_string", "pagination_document")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    search_string = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="searchString")
    pagination_document = sgqlc.types.Field(
        sgqlc.types.non_null(DocumentFromDocumentFeedPagination),
        graphql_name="paginationDocument",
        args=sgqlc.types.ArgDict(
            (
                (
                    "mode",
                    sgqlc.types.Arg(DocumentFeedMode, graphql_name="mode", default="all"),
                ),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("query", sgqlc.types.Arg(String, graphql_name="query", default=None)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        DocumentFilterSettings,
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
                (
                    "sort_field",
                    sgqlc.types.Arg(DocumentSorting, graphql_name="sortField", default=None),
                ),
                (
                    "extra_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ExtraSettings),
                        graphql_name="extraSettings",
                        default=None,
                    ),
                ),
            )
        ),
    )


class Issue(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "topic",
        "description",
        "status",
        "priority",
        "execution_time_limit",
        "markers",
        "executor",
        "pagination_document",
        "pagination_concept",
        "pagination_issue",
        "metric",
        "pagination_issue_change",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    topic = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="topic")
    description = sgqlc.types.Field(String, graphql_name="description")
    status = sgqlc.types.Field(sgqlc.types.non_null(IssueStatus), graphql_name="status")
    priority = sgqlc.types.Field(sgqlc.types.non_null(IssuePriority), graphql_name="priority")
    execution_time_limit = sgqlc.types.Field(UnixTime, graphql_name="executionTimeLimit")
    markers = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="markers",
    )
    executor = sgqlc.types.Field(sgqlc.types.non_null(User), graphql_name="executor")
    pagination_document = sgqlc.types.Field(
        sgqlc.types.non_null(DocumentPagination),
        graphql_name="paginationDocument",
        args=sgqlc.types.ArgDict(
            (
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
            )
        ),
    )
    pagination_concept = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptPagination),
        graphql_name="paginationConcept",
        args=sgqlc.types.ArgDict(
            (
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
            )
        ),
    )
    pagination_issue = sgqlc.types.Field(
        sgqlc.types.non_null(IssuePagination),
        graphql_name="paginationIssue",
        args=sgqlc.types.ArgDict(
            (
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(IssueFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "sort_direction",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(SortDirection),
                        graphql_name="sortDirection",
                        default=None,
                    ),
                ),
                (
                    "sorting",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(IssueSorting),
                        graphql_name="sorting",
                        default=None,
                    ),
                ),
            )
        ),
    )
    metric = sgqlc.types.Field(sgqlc.types.non_null(IssueStatistics), graphql_name="metric")
    pagination_issue_change = sgqlc.types.Field(
        sgqlc.types.non_null(IssueChangePagination),
        graphql_name="paginationIssueChange",
        args=sgqlc.types.ArgDict(
            (
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
            )
        ),
    )


class IssueChange(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = ("id", "from_", "to", "comment")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    from_ = sgqlc.types.Field(sgqlc.types.non_null(IssueInfo), graphql_name="from")
    to = sgqlc.types.Field(sgqlc.types.non_null(IssueInfo), graphql_name="to")
    comment = sgqlc.types.Field(String, graphql_name="comment")


class Platform(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "name",
        "platform_type",
        "url",
        "country",
        "language",
        "markers",
        "params",
        "image",
        "metric",
        "period",
        "accounts",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    platform_type = sgqlc.types.Field(sgqlc.types.non_null(PlatformType), graphql_name="platformType")
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="url")
    country = sgqlc.types.Field(String, graphql_name="country")
    language = sgqlc.types.Field(String, graphql_name="language")
    markers = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="markers",
    )
    params = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Parameter))),
        graphql_name="params",
    )
    image = sgqlc.types.Field(String, graphql_name="image")
    metric = sgqlc.types.Field(sgqlc.types.non_null(PlatformStatistics), graphql_name="metric")
    period = sgqlc.types.Field(sgqlc.types.non_null(DateTimeInterval), graphql_name="period")
    accounts = sgqlc.types.Field(
        sgqlc.types.non_null(AccountPagination),
        graphql_name="accounts",
        args=sgqlc.types.ArgDict(
            (
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(AccountFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "sort_direction",
                    sgqlc.types.Arg(
                        SortDirection,
                        graphql_name="sortDirection",
                        default="descending",
                    ),
                ),
                (
                    "sorting",
                    sgqlc.types.Arg(AccountSorting, graphql_name="sorting", default="id"),
                ),
            )
        ),
    )


class ResearchMap(sgqlc.types.Type, RecordInterface):
    __schema__ = api_schema
    __field_names__ = (
        "id",
        "name",
        "description",
        "is_temporary",
        "markers",
        "list_concept_with_coordinates",
        "list_concept_candidate_fact_with_coordinates",
        "list_document_with_coordinates",
        "list_concept_link",
        "list_concept_implicit_link",
        "list_concept_mention",
        "list_concept_link_candidate_fact",
        "list_concept_fact_mention",
        "list_concept_fact_link",
        "list_document_link",
        "research_map_statistics",
        "list_group",
        "is_active",
        "access_level",
        "pagination_concept",
        "pagination_story",
        "pagination_research_map",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    description = sgqlc.types.Field(String, graphql_name="description")
    is_temporary = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isTemporary")
    markers = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))),
        graphql_name="markers",
    )
    list_concept_with_coordinates = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptWithCoordinate))),
        graphql_name="listConceptWithCoordinates",
    )
    list_concept_candidate_fact_with_coordinates = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptCandidateFactWithCoordinates))),
        graphql_name="listConceptCandidateFactWithCoordinates",
        args=sgqlc.types.ArgDict(
            (
                (
                    "default_view",
                    sgqlc.types.Arg(Boolean, graphql_name="defaultView", default=True),
                ),
            )
        ),
    )
    list_document_with_coordinates = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DocumentWithCoordinates))),
        graphql_name="listDocumentWithCoordinates",
    )
    list_concept_link = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptLink))),
        graphql_name="listConceptLink",
    )
    list_concept_implicit_link = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptImplicitLink))),
        graphql_name="listConceptImplicitLink",
        args=sgqlc.types.ArgDict(
            (
                (
                    "default_view",
                    sgqlc.types.Arg(Boolean, graphql_name="defaultView", default=True),
                ),
            )
        ),
    )
    list_concept_mention = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptMention))),
        graphql_name="listConceptMention",
    )
    list_concept_link_candidate_fact = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptLinkCandidateFact))),
        graphql_name="listConceptLinkCandidateFact",
        args=sgqlc.types.ArgDict(
            (
                (
                    "default_view",
                    sgqlc.types.Arg(Boolean, graphql_name="defaultView", default=True),
                ),
            )
        ),
    )
    list_concept_fact_mention = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptCandidateFactMention))),
        graphql_name="listConceptFactMention",
        args=sgqlc.types.ArgDict(
            (
                (
                    "default_view",
                    sgqlc.types.Arg(Boolean, graphql_name="defaultView", default=True),
                ),
            )
        ),
    )
    list_concept_fact_link = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ConceptFactLink))),
        graphql_name="listConceptFactLink",
        args=sgqlc.types.ArgDict(
            (
                (
                    "default_view",
                    sgqlc.types.Arg(Boolean, graphql_name="defaultView", default=True),
                ),
            )
        ),
    )
    list_document_link = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DocumentLink))),
        graphql_name="listDocumentLink",
    )
    research_map_statistics = sgqlc.types.Field(
        sgqlc.types.non_null(ResearchMapStatistics),
        graphql_name="researchMapStatistics",
    )
    list_group = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Group))),
        graphql_name="listGroup",
    )
    is_active = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isActive")
    access_level = sgqlc.types.Field(sgqlc.types.non_null(AccessLevel), graphql_name="accessLevel")
    pagination_concept = sgqlc.types.Field(
        sgqlc.types.non_null(ConceptPagination),
        graphql_name="paginationConcept",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                ("query", sgqlc.types.Arg(String, graphql_name="query", default=None)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        ConceptFilterSettings,
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
                (
                    "sort_field",
                    sgqlc.types.Arg(ConceptSorting, graphql_name="sortField", default=None),
                ),
                (
                    "extra_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ConceptExtraSettings),
                        graphql_name="extraSettings",
                        default=None,
                    ),
                ),
            )
        ),
    )
    pagination_story = sgqlc.types.Field(
        sgqlc.types.non_null(StoryPagination),
        graphql_name="paginationStory",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "grouping",
                    sgqlc.types.Arg(DocumentGrouping, graphql_name="grouping", default="none"),
                ),
                ("query", sgqlc.types.Arg(String, graphql_name="query", default=None)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        DocumentFilterSettings,
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
                (
                    "sort_field",
                    sgqlc.types.Arg(DocumentSorting, graphql_name="sortField", default=None),
                ),
                (
                    "extra_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ExtraSettings),
                        graphql_name="extraSettings",
                        default=None,
                    ),
                ),
            )
        ),
    )
    pagination_research_map = sgqlc.types.Field(
        sgqlc.types.non_null(ResearchMapPagination),
        graphql_name="paginationResearchMap",
        args=sgqlc.types.ArgDict(
            (
                ("limit", sgqlc.types.Arg(Int, graphql_name="limit", default=20)),
                ("offset", sgqlc.types.Arg(Int, graphql_name="offset", default=0)),
                (
                    "filter_settings",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(ResearchMapFilterSettings),
                        graphql_name="filterSettings",
                        default=None,
                    ),
                ),
                (
                    "direction",
                    sgqlc.types.Arg(SortDirection, graphql_name="direction", default="descending"),
                ),
                (
                    "sort_field",
                    sgqlc.types.Arg(
                        ResearchMapSorting,
                        graphql_name="sortField",
                        default="conceptAndDocumentLink",
                    ),
                ),
                (
                    "selected_content",
                    sgqlc.types.Arg(
                        ResearchMapSelectedContent,
                        graphql_name="selectedContent",
                        default=None,
                    ),
                ),
            )
        ),
    )


########################################################################
# Unions
########################################################################
class AnyValue(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (
        DateTimeValue,
        GeoPointValue,
        IntValue,
        DoubleValue,
        StringLocaleValue,
        StringValue,
        LinkValue,
        CompositeValue,
    )


class AnyValueType(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (ConceptPropertyValueType, CompositePropertyValueTemplate)


class ConceptLikeFact(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (ConceptCandidateFact, ConceptFact)


class ConceptPropertyLikeFact(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (ConceptPropertyFact, ConceptLinkPropertyFact)


class ConceptViewValue(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (
        DateTimeValue,
        GeoPointValue,
        IntValue,
        DoubleValue,
        StringLocaleValue,
        StringValue,
        LinkValue,
        CompositeValue,
        Concept,
        ConceptType,
        ConceptLinkType,
        User,
    )


class Fact(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (
        ConceptCandidateFact,
        ConceptFact,
        ConceptLinkCandidateFact,
        ConceptLinkFact,
        ConceptPropertyCandidateFact,
        ConceptPropertyFact,
        ConceptPropertyValueCandidateFact,
        ConceptLinkPropertyFact,
    )


class TypeSearchElement(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (DictValue, NERCRegexp)


class UserMenuType(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (ConceptType, CompositeConceptType, ConceptTypeView)


class Value(sgqlc.types.Union):
    __schema__ = api_schema
    __types__ = (
        DateTimeValue,
        GeoPointValue,
        IntValue,
        DoubleValue,
        StringLocaleValue,
        StringValue,
        LinkValue,
    )


########################################################################
# Schema Entry Points
########################################################################
api_schema.query_type = Query
api_schema.mutation_type = Mutation
api_schema.subscription_type = Subscription
