from sgqlc.types.datetime import Date
from sgqlc.types import String, Float, Type, Int, list_of, Field, Boolean
from sgqlc.types.relay import Node, Connection
from sgqlc.operation import Operation


class Tag(Type):
    tagId = String


class AssetTypeEvent(Type):
    eventName = String
    isDefault = Boolean
    isMandatory = Boolean
    selected = Boolean


class AssetType(Type):
    id = String
    name = String
    minTags = Int
    active = Boolean
    events = Field(AssetTypeEvent)


class Category(Type):
    id = String
    name = String
    createdAt = Int
    createdBy = String
    ownerId = String
    description = String
    assetType = Field(AssetType)


class AssetLabel(Type):
    assetId = String
    label = String


class Asset(Type):
    id = String
    name = String
    tags = Field(Tag)
    createdAt = Int
    createdBy = String
    lastUpdatedBy = String
    lastUpdatedAt = String
    tagId = String
    status = String
    poiId = String
    categoryId = String
    category = Field(Category)
    assetLabels = Field(AssetLabel)


class PageInfoNode(Type):
    cursor = String
    hasNext = Boolean
    totalPages = Int


class AssetConnection(Type):
    page = list_of(Asset)
    pageInfo = Field(PageInfoNode)


class Zone(Type):
    id = String
    name = String
    createdAt = Int
    createdBy = String
    locationId = String


class Location(Type):
    id = String
    name = String
    createdAt = Int
    createdBy = String
    address = String
    country = String
    city = String
    lat = Float
    lng = Float
    ownerId = String
    locationType = String
    lastUpdatedBy = String
    lastUpdatedAt = String
    zones = Field(Zone)


class PoiAssociation(Type):
    associationType = String
    poiId = String
    associationValue = String


class LocationConnection(Type):
    page = list_of(Location)
    pageInfo = Field(PageInfoNode)


class ZoneConnection(Type):
    page = list_of(Zone)
    pageInfo = Field(PageInfoNode)


class PoiAssociationConnection(Type):
    page = list_of(PoiAssociation)
    pageInfo = Field(PageInfoNode)


class CategoryConnection(Type):
    page = list_of(Category)
    pageInfo = Field(PageInfoNode)


class StringFilter(Type):
    filterType = String
    value = String

    def __to_graphql_input__(self, value, indent, indent_string="\t"):
        return f"{{{self.filterType}: \"{self.value}\"}}"


class Query(Type):
    assets = Field(AssetConnection, args={
        'pageSize': Int,
        'cursor': String,
        'categoryId': StringFilter,
        'id': StringFilter
    })

    locations = Field(LocationConnection, args={
        'pageSize': Int,
        'cursor': String
    })

    zones = Field(ZoneConnection, args={
        'pageSize': Int,
        'cursor': String,
        'locationId': StringFilter
    })

    poi_associations = Field(PoiAssociationConnection, args={
        'pageSize': Int,
        'cursor': String,
        'poiId': StringFilter
    })

    categories = Field(CategoryConnection, args={
        'pageSize': Int,
        'cursor': String
    })