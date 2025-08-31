"""
  Copyright (c) 2016- 2025, Wiliot Ltd. All rights reserved.

  Redistribution and use of the Software in source and binary forms, with or without modification,
   are permitted provided that the following conditions are met:

     1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

     2. Redistributions in binary form, except as used in conjunction with
     Wiliot's Pixel in a product or a Software update for such product, must reproduce
     the above copyright notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the distribution.

     3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
     may be used to endorse or promote products or services derived from this Software,
     without specific prior written permission.

     4. This Software, with or without modification, must only be used in conjunction
     with Wiliot's Pixel or with Wiliot's cloud service.

     5. If any Software is provided in binary form under this license, you must not
     do any of the following:
     (a) modify, adapt, translate, or create a derivative work of the Software; or
     (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
     discover the source code or non-literal aspects (such as the underlying structure,
     sequence, organization, ideas, or algorithms) of the Software.

     6. If you create a derivative work and/or improvement of any Software, you hereby
     irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
     royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
     right and license to reproduce, use, make, have made, import, distribute, sell,
     offer for sale, create derivative works of, modify, translate, publicly perform
     and display, and otherwise commercially exploit such derivative works and improvements
     (as applicable) in conjunction with Wiliot's products and services.

     7. You represent and warrant that you are not a resident of (and will not use the
     Software in) a country that the U.S. government has embargoed for use of the Software,
     nor are you named on the U.S. Treasury Department’s list of Specially Designated
     Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
     You must not transfer, export, re-export, import, re-import or divert the Software
     in violation of any export or re-export control laws and regulations (such as the
     United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
     and use restrictions, all as then in effect

   THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
   OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
   WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
   QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
   IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
   ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
   OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
   FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
   (SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
   (A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
   (B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
   (C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
"""
import json
from enum import Enum
from wiliot_api.api_client import Client, WiliotCloudError
import os


class AssetNotFound(Exception):
    pass


class CategoryNotFound(Exception):
    pass


class LocationNotFound(Exception):
    pass


class ZoneNotFound(Exception):
    pass


class KeyNotFound(Exception):
    pass

class KeyValueNotFound(Exception):
    pass


class TagRole(Enum):
    DEFAULT = 'DEFAULT'
    REFERENCE = 'REFERENCE'


class Event(Enum):
    LOCATION = 'location'
    TEMPERATURE = 'temperature'
    ACTIVE = 'active'
    ASSET_SEEN_IN_LOCATION = 'assetSeenInLocation'


class LocationType(Enum):
    SITE = 'SITE'
    TRANSPORTER = 'TRANSPORTER'


class ZoneAssociationType(Enum):
    BRIDGE = 'bridge'
    TAG = 'tag'


class LocationAssociationType(Enum):
    BRIDGE = 'bridge'

class EntityType(Enum):
    GATEWAY = 'gateway'
    BRIDGE = 'bridge'
    ASSET = 'asset'
    LOCATION = 'location'
    ZONE = 'zone'
    CATEGORY = 'category'


class PlatformClient(Client):
    def __init__(self, api_key, owner_id, env='prod', region='us-east-2', cloud='', log_file=None, logger_=None,
                 keep_alive=True, initiator_name=None, base_url=None):
        self.client_path = "traceability/owner/{owner_id}/".format(owner_id=owner_id)
        self.owner_id = owner_id
        super().__init__(api_key=api_key, env=env, region=region, cloud=cloud, log_file=log_file, logger_=logger_,
                         keep_alive=keep_alive, initiator_name=initiator_name, base_url=base_url)

    # Tag calls

    def get_pixels(self, limit=None, next=None, begin=None, contains=None):
        """
        Get an owner's pixels
        :param limit: Optional integer - limit the number of pixels to return (default: 50)
        :param next: Optional string - the page to start from (obtained from the last call to this function)
        :param begin: Optional string - if provided only pixel with IDs that start with this string will be returned
        :param contains: Optional string - if provided only pixel with IDs that contains this string will be returned.
                         overrides the begin paramater
        :return: A tuple containing the list of pixels and the ID of the next page (or None if the last page was returned)
        """
        path = "pixel"
        params = {
            'limit': limit,
            'next': next,
            'begin': begin,
            'contains': contains
        }
        res = self._get(path, params=params, override_client_path="owner/{owner_id}/".format(owner_id=self.owner_id))
        return res['data'], res.get("next", None)

    def get_pixel_count(self, begin=None, contains=None):
        """
        Get a pixel count for owner
        :param begin: Optional string - if provided only pixel with IDs that start with this string will be counted
        :param contains: Optional string - if provided only pixel with IDs that contains this string will be counted.
                         overrides the begin paramater
        :return: The number of pixels
        """
        path = "pixel/count"
        params = {
            'begin': begin,
            'contains': contains
        }
        res = self._get(path, params=params, override_client_path="owner/{owner_id}/".format(owner_id=self.owner_id))
        return res['data']

    # Asset calls

    def get_assets(self):
        """
        Get all assets or a subset of assets
        :return: A list of asset dictionaries
        """
        path = "metadataFetch"

        has_next = True
        cursor = None
        assets = []
        from .platform_models import Query, Operation, StringFilter

        while True:
            query = Operation(Query)
            if not has_next:
                break
            if cursor is not None:
                query.assets(cursor=cursor)
            else:
                query.assets()
            # query.assets.page.__fields__()
            # Define the fields to return
            query.assets.page.id()
            query.assets.page.name()
            query.assets.page.tags()
            query.assets.page.createdAt()
            query.assets.page.createdBy()
            query.assets.page.lastUpdatedAt()
            query.assets.page.lastUpdatedBy()
            query.assets.page.tagId()
            query.assets.page.status()
            query.assets.page.poiId()
            query.assets.page.categoryId()
            query.assets.page.category.id()
            query.assets.page.category.name()
            query.assets.page.assetLabels.label()
            query.assets.pageInfo()
            payload = {
                "query": f"{{{query.assets()}}}"
            }
            res = self._post(path, payload=payload)
            has_next = res['data']['assets']['pageInfo']['hasNext']
            cursor = res['data']['assets']['pageInfo']['cursor']
            assets += res["data"]["assets"]["page"]

        return assets

    def get_asset(self, asset_id):
        """
        Get a single assets for a project
        :param asset_id: string
        :return: a dictionary with asset properties
        :raises: An AssetNotFound exception if an asset with the
        provided ID cannot be found
        """
        path = f"asset/{asset_id}"
        res = self._get(path)
        try:
            return res["data"]
        except KeyError:
            raise AssetNotFound

    def create_asset(self,
                     name, category_id, pixels, asset_id=None,
                     status=None):
        """
        Create an asset, and optionally assign pixels
        :param name: String - required - A name for the asset (required)
        :param category_id: String - required - the type of asset
        :param pixels: List - required - of dictionaries for asset pixels. Each item should be a dictionary with the
        following keys:
         > tagId: string
         > role: Enum: TagRole
        :param asset_id: String - optional. If not provided an asset ID will be generated automatically
        :param status: String - optional - A status
        :return: The created asset if successful
        """
        assert isinstance(pixels, list), "Expecting a list of strings for pixels_ids"
        path = "asset"
        payload = {
            "id": asset_id,
            "name": name,
            "categoryId": category_id,
            "tags": [{
                'tagId': t['tagId'],
                'role': t['role'].value
            } for t in pixels],
            "status": status
        }
        try:
            res = self._post(path, payload, override_api_version="v2")
            return res['data']
        except WiliotCloudError as e:
            print("Failed to create asset")
            raise e

    def batch_create_assets_from_file(self, file_path):
        """
        Request a change of ownership for a range of pixel IDs
        :param file_path : full path to a csv file containing the following columns (in order):
        :                   * tagId
        :                   * categoryId
        :                   * assetId
        :raises: WiliotCloudError
        """
        path = "batch-asset"
        with open(file_path, 'rb') as f:
            files_to_send = [
                ('file', (os.path.basename(file_path), f, 'text/csv'))
            ]
            try:
                res = self._post_with_files(path, files=files_to_send)
                return res.get("requestId", None)
            except WiliotCloudError as e:
                print("Failed to request batch asset creation")
                raise e

    def get_batch_asset_request_report(self, request_id, report_type="full"):
        """
        Get the report for batch asset creation request
        :param request_id: String - Required - the request ID to fetch
        :param report_type: String - The type of report to generate
        :returns: A dictionary with request report details
        """
        path = f"batch-asset/request/{request_id}"
        params = {
            'reportType': report_type
        }
        res = self._get(path=path, params=params)
        return res

    def update_asset(self, asset):
        """
        Update an asset. The following asset properties can be updated:
        * Category
        * Name
        :param asset: Dictionary describing the new asset properties
        :return: The updated asset if successful
        """
        path = "asset/{}".format(asset["id"])
        payload = {
            "name": asset.get("name", None),
            "categoryId": asset.get("categoryId", None),
            "status": asset.get("status", None)
        }
        try:
            res = self._put(path, payload, override_api_version="v2")
            return res['data']
        except WiliotCloudError as e:
            print("Failed to update asset")
            raise e

    def delete_asset(self, asset_id):
        """
        Delete an asset by its ID
        :param asset_id: String - required - the ID of the asset to delete
        :return: True if the asset was deleted
        """
        path = "asset/{}".format(asset_id)
        try:
            res = self._delete(path, override_api_version="v2")
            return res['message'].lower().find("success") != -1
        except WiliotCloudError as e:
            print("Failed to delete asset")
            raise e
        
    def associate_pixel_to_asset(self, asset_id, pixel_id):
        """
        Associate a pixel to an existing asset
        :param asset_id: String - required - the ID of the asset to associate the pixel with
        :param pixel_id: String - required - the ID of the pixel to associate with the asset
        :return: True if association was successful.
        """
        path = f"asset/{asset_id}/tag/{pixel_id}"
        try:
            res = self._post(path, payload={})
            return res['message'].lower().find("success") != -1
        except WiliotCloudError as e:
            print("Failed to associate pixel to asset")
            raise e

    def disassociate_pixel_from_asset(self, asset_id, pixel_id):
        """
        Disassociate a pixel from an asset
        :param asset_id: String - required - the ID of the asset to disassociate the pixel from
        :param pixel_id: String - required - the ID of the pixel to disassociate from the asset
        :return: True if disassociation was successful.
        """
        path = f"asset/{asset_id}/tag/{pixel_id}"
        try:
            res = self._delete(path, payload={})
            return res['message'].lower().find("success") != -1
        except WiliotCloudError as e:
            print("Failed to disassociate pixel from asset")
            raise e

    def update_pixel_to_asset_association(self, asset_id, pixels_to_associate=[], pixels_to_disassociate=[]):
        """
        Update multiple pixels association to an asset in a single call
        :param asset_id: String - required - the ID of the asset to associate the pixel with
        :param pixels_to_associate: List of String - optional - the list of pixels to associate to the asset
        :param pixels_to_disassociate: List of String - optional - the list of pixels to disassociate from the asset
        :returns: True if all requested pixels were successfully updated.
        """
        path = f"asset/{asset_id}/association/pixel"
        payload = {
            "associations": pixels_to_associate,
            "disassociations": pixels_to_disassociate
        }
        res = self._patch(path, payload=payload, override_client_path=f"owner/{self.owner_id}/")
        return sorted(res['data']['associated']) == sorted(pixels_to_associate) and\
            sorted(res['data']['disassociated']) == sorted(pixels_to_disassociate)

    # Category calls

    def get_categories(self):
        """
        Get all asset categories
        :return: a list of dictionaries with categories
        """
        path = "metadataFetch"

        has_next = True
        cursor = None
        categories = []
        from .platform_models import Query, Operation, StringFilter

        while True:
            query = Operation(Query)
            if not has_next:
                break
            if cursor is not None:
                query.categories(cursor=cursor)
            else:
                query.categories()
            query.categories.page.__fields__()
            query.categories.pageInfo()
            payload = {
                "query": f"{{{query.categories()}}}"
            }
            res = self._post(path, payload=payload)
            has_next = res['data']['categories']['pageInfo']['hasNext']
            cursor = res['data']['categories']['pageInfo']['cursor']
            categories += res["data"]["categories"]["page"]

        return categories

    def get_category(self, category_id):
        """
        Get a single asset type for a project
        :param category_id: string
        :return: a dictionary with asset type properties
        :raises: An AssetTypeNotFound exception if an asset with the
        provided ID cannot be found
        """
        path = "category/{}".format(category_id)
        res = self._get(path)
        if len(res.get('data', [])) == 0:
            raise CategoryNotFound
        return res.get('data', [])

    def create_category(self, name, asset_type_id, events, category_id=None, sku=None, description=None):
        """
        Create a category
        :param name: String - required - A unique name for the category
        :param asset_type_id: Int - required - the base asset type for this category (obtained from the list of
        available asset types)
        :param events: List of EVENTS to enable for assets of this category
        :param category_id: String - optional - If not provided an asset ID will be generated automatically
        :param sku: String - optional - A SKU/UPC to link the category to
        :param description: String - optional - A description for the category
        :return: The created asset if successful
        """
        # Make sure events is a list of Events
        assert isinstance(events, list) and all(isinstance(element, Event) for element in events), "events argument must be a list of Event(s)"
        path = "category"
        payload = {
            "assetType": {
                "events": [
                    {
                        "selected": True,
                        "eventName": e.value if isinstance(e, Event) else e
                    } for e in events
                ],
                "id": asset_type_id
            },
            "id": category_id,
            "name": name,
            "description": description,
            "sku_upc": sku
        }
        try:
            res = self._post(path, payload)
            return res['data']
        except WiliotCloudError as e:
            print("Failed to create category")
            raise e

    def update_category(self, category):
        """
        Update a category
        :param category: Dictionary describing the category
        :return: The updated category if successful
        """
        path = "category/{}".format(category['id'])
        try:
            res = self._put(path, category)
            return res['data']
        except WiliotCloudError as e:
            print("Failed to update asset type")
            raise e

    def delete_category(self, category_id):
        """
        Delete a category by its ID
        :param category_id: String - required - the ID of the category to delete
        :return: True if the asset was deleted
        """
        path = "category/{}".format(category_id)
        try:
            res = self._delete(path)
            print(res['message'])
            return res['message'].lower().find("success") != -1
        except WiliotCloudError as e:
            print("Failed to delete category")
            raise e

    # Asset types
    def get_asset_types(self):
        """
        Get all asset types
        :return: a list of dictionaries with asset types
        """
        path = "asset-type"
        res = self._get(path)
        return res.get('data', [])

    # Locations
    def get_locations(self):
        """
        Get all locations
        :return: A list of dictionaries representing locations
        """
        path = "metadataFetch"

        has_next = True
        cursor = None
        locations = []
        from .platform_models import Query, Operation, StringFilter

        while True:
            query = Operation(Query)
            if not has_next:
                break
            if cursor is not None:
                query.locations(cursor=cursor)
            else:
                query.locations()
            query.locations.page.__fields__()
            query.locations.pageInfo()
            payload = {
                "query": f"{{{query.locations()}}}"
            }
            res = self._post(path, payload=payload)
            has_next = res['data']['locations']['pageInfo']['hasNext']
            cursor = res['data']['locations']['pageInfo']['cursor']
            locations += res["data"]["locations"]["page"]

        return locations

    def get_location(self, location_id):
        """
        Get one location
        :param location_id: String - required - the ID of the location to return
        :return: A dictionary representing the location
        :raise: A LocationNotFound if a location with the provided ID does not exist
        """
        path = f"location/{location_id}"
        res = self._get(path)
        if len(res.get('data', [])) == 0:
            raise LocationNotFound
        return res.get('data', [])

    def create_location(self, location_type, name=None, location_id=None, lat=None, lng=None,
                        address=None, city=None, country=None):
        """
        Create a new location
        :param location_type: LocationType Enum - Required - the type of location
        :param name: String - optional - A name for the location
        :param location_id: String - optional - A unique ID for the new location. A unique ID will be auto generated
        if one is not provided
        :param lat: Float - Optional - The latitude value for the location - required only for location type SITE
        :param lng: Float - Optional - The longitude value for the location - required only for location type SITE
        :param address: String - Optional - A street address for the location
        :param city: String - Optional - The location's city
        :param country: String - Optional - the location's country
        :return: The created location if successful
        """
        path = "location"
        payload = {
            'locationType': location_type.value,
            'id': location_id,
            'name': name,
            'lat': lat,
            'lng': lng,
            'address': address,
            'city': city,
            'country': country
        }
        try:
            res = self._post(path, payload)
            return res['data']
        except WiliotCloudError as e:
            print("Failed to create location")
            raise e

    def update_location(self, location):
        """
        Update a location
        :param location: Dictionary - Required - The updated location dictionary. All location properties, except for
        location ID can be updated
        :return: The updated location if successful
        :raise: LocationNotFound if the requested location does not exit
        """
        path = f"location/{location['id']}"
        payload = {
            'locationType': location['locationType'].value if isinstance(location, LocationType) else location['locationType'],
            'name': location.get('name', None),
            'lat': location.get('lat', None),
            'lng': location.get('lng', None),
            'address': location.get('address', None),
            'city': location.get('city', None),
            'country': location.get('country', None)
        }
        try:
            res = self._put(path, payload)
            return res['data']
        except WiliotCloudError as e:
            print("Failed to update location")
            raise e

    def delete_location(self, location_id):
        """
        Delete a location
        :param location_id: String - Required - The ID of the location to delete
        :return: True if the location was deleted
        """
        path = f"location/{location_id}"
        try:
            res = self._delete(path)
            return res['message'].lower().find("success") != -1
        except WiliotCloudError as e:
            print("Failed to delete location")
            raise e

    # Associations
    def get_location_associations(self, location_id):
        """
        Get all associations for a given location
        :param location_id: String - Required - The location ID to return associations for
        :return: A list of associations
        """
        path = "fetchMetadata"

        has_next = True
        cursor = None
        poi_associations = []
        from .platform_models import Query, Operation, StringFilter

        while True:
            query = Operation(Query)
            if not has_next:
                break
            if cursor is not None:
                query.poi_associations(poiId={'filterType': 'equalTo', 'value': location_id}, cursor=cursor)
            else:
                query.poi_associations(poiId={'filterType': 'equalTo', 'value': location_id})
            query.poi_associations.page.__fields__()
            query.poi_associations.pageInfo()
            payload = {
                "query": f"{{{query.poi_associations()}}}"
            }
            res = self._post(path, payload=payload)
            has_next = res['data']['poiAssociations']['pageInfo']['hasNext']
            cursor = res['data']['poiAssociations']['pageInfo']['cursor']
            poi_associations += res["data"]["poiAssociations"]["page"]

        return poi_associations

    def create_location_association(self, location_id, association_type, association_value):
        """
        Create a new association for a location
        :param location_id: String - Required - The ID of the location to create the association for
        :param association_type: LocationAssociationType - Required - The type of association
        :param association_value: String - Required - The value of the association (the bridge ID in case of a bridge
         association)
        :return: The new association that was created
        """
        path = f"location/{location_id}/association"
        payload = {
            'associationValue': association_value,
            'associationType': association_type.value
        }
        try:
            res = self._post(path, payload=payload)
            return res['data']
        except WiliotCloudError as e:
            print("Failed to create location association")
            raise e

    def delete_location_association(self, location_id, association_value):
        """
        Delete one location association
        :param location_id: String - Required - The ID of the location to delete associations for
        :param association_value: String - Required - Provide a value to delete only one association
        value.
        :return: True if successful
        """
        path = f"location/{location_id}/association/{association_value}"
        try:
            res = self._delete(path)
            return res['message'].lower().find("success") != -1
        except WiliotCloudError as e:
            print("Failed to delete a location association")
            raise e

    def delete_location_associations(self, location_id):
        """
        Delete all location associations
        :param location_id: String - Required - The ID of the location to delete associations for
        value.
        :return: True if successful
        """
        path = f"location/{location_id}/association"
        try:
            res = self._delete(path)
            return res['message'].lower().find("success") != -1
        except WiliotCloudError as e:
            print("Failed to delete location associations")
            raise e

    def get_zone_associations(self, zone_id):
        """
        Get all associations for a given zone
        :param location_id: String - Required - The location ID the zone belongs to
        :param zone_id: String - Required - The zone ID to query
        :return: A list of associations
        """
        path = "fetchMetadata"

        has_next = True
        cursor = None
        poi_associations = []
        from .platform_models import Query, Operation, StringFilter

        while True:
            query = Operation(Query)
            if not has_next:
                break
            if cursor is not None:
                query.poi_associations(poiId={'filterType': 'equalTo', 'value': zone_id}, cursor=cursor)
            else:
                query.poi_associations(poiId={'filterType': 'equalTo', 'value': zone_id})
            query.poi_associations.page.__fields__()
            query.poi_associations.pageInfo()
            payload = {
                "query": f"{{{query.poi_associations()}}}"
            }
            res = self._post(path, payload=payload)
            has_next = res['data']['poiAssociations']['pageInfo']['hasNext']
            cursor = res['data']['poiAssociations']['pageInfo']['cursor']
            poi_associations += res["data"]["poiAssociations"]["page"]

        return poi_associations

    def create_zone_association(self, location_id, zone_id, association_type, association_value):
        """
        Create a new association for a location
        :param location_id: String - Required - The ID of the location to create the association for
        :param zone_id: String - Required -  The ID of the zone to create the association for
        :param association_type: ZoneAssociationType - Required - The type of association
        :param association_value: String - Required - The value of the association (bridge ID in case of bridge)
        :return: The new association that was created
        """
        path = f"location/{location_id}/zone/{zone_id}/association"
        payload = {
            'associationValue': association_value,
            'associationType': association_type.value
        }
        try:
            res = self._post(path, payload=payload)
            return res['data']
        except WiliotCloudError as e:
            print("Failed to create location association")
            raise e

    def delete_zone_association(self, location_id, zone_id, association_value):
        """
        Delete one zone association
        :param location_id: String - Required - The ID of the location the zone belongs to
        :param zone_id: String - Required - The ID of the zone to delete the association from
        :param association_value: String - Required - Provide a value to delete only one association
        value.
        :return: True if successful
        """
        path = f"location/{location_id}/zone/{zone_id}/association/{association_value}"
        try:
            res = self._delete(path)
            return res['message'].lower().find("success") != -1
        except WiliotCloudError as e:
            print("Failed to delete a zone association")
            raise e

    def delete_zone_associations(self, location_id, zone_id):
        """
        Delete all zone associations
        :param location_id: String - Required - The ID of the location the zone belongs to
        :param zone_id: String - Required - The ID of the zone to delete the associations from
        :return: True if successful
        """
        path = f"location/{location_id}/zone/{zone_id}/association"
        try:
            res = self._delete(path)
            return res['message'].lower().find("success") != -1
        except WiliotCloudError as e:
            print("Failed to delete zone associations")

    # Zones
    def get_zones(self, location_id=None):
        """
        Get all zones (can be filtered by location)
        :param location_id: The ID of the location to return zones belonging to
        :return: A list of zones
        """
        path = "fetchMetdata"

        has_next = True
        cursor = None
        zones = []
        from .platform_models import Query, Operation, StringFilter

        while True:
            query = Operation(Query)
            if not has_next:
                break
            if cursor is not None:
                if location_id is not None:
                    query.zones(locationId={'value': location_id, 'filterType': 'equalTo'}, cursor=cursor)
                else:
                    query.zones(cursor=cursor)
            else:
                if location_id is not None:
                    query.zones(locationId={'value': location_id, 'filterType': 'equalTo'})
                else:
                    query.zones()
            query.zones.page.__fields__()
            query.zones.pageInfo()
            payload = {
                "query": f"{{{query.zones()}}}"
            }
            res = self._post(path, payload=payload)
            has_next = res['data']['zones']['pageInfo']['hasNext']
            cursor = res['data']['zones']['pageInfo']['cursor']
            zones += res["data"]["zones"]["page"]

        return zones

    def get_zone(self, location_id, zone_id):
        """
        Get all zones under a location
        :param location_id: The ID of the location the zone belongs to
        :param zone_id: The ID of the zone to return
        :return: A list of zones
        :raise: A ZoneNotFound exception if a zone with the requested ID does not exist
        """
        path = f"location/{location_id}/zone/{zone_id}"
        res = self._get(path)
        if len(res.get('data', [])) == 0:
            raise ZoneNotFound
        return res.get('data', [])

    def create_zone(self, name, location_id, zone_id=None):
        """
        Create a new zone
        :param name: String - Required - A human-readable name for the zone
        :param location_id: String - Required - The ID the zone will belong to
        :param zone_id: String - optional - The ID to give to the zone.
        If none is provided an ID will be automatically generated
        :return: The created zone
        """
        path = f"location/{location_id}/zone"
        payload = {
            'name': name,
            'id': zone_id
        }
        try:
            res = self._post(path, payload)
            return res['data']
        except WiliotCloudError as e:
            print("Failed to create zone")
            raise e

    def update_zone(self, location_id, zone):
        """
        Update a zone
        :param location_id: String - Required - The ID of the location the zone belongs to
        :param zone: Dictionary - Required - The updated zone dictionary. All location properties, except for
        zone ID can be updated
        :return: The updated zone if successful
        """
        path = f"location/{location_id}/zone/{zone['id']}"
        payload = {
            'name': zone['name'],
            'id': zone['id'],
            'locationId': zone['locationId']
        }
        try:
            res = self._put(path, payload)
            return res['data']
        except WiliotCloudError as e:
            print("Failed to update zone")
            raise e

    def delete_zone(self, location_id, zone_id):
        """
        Delete a zone
        :param location_id: String - Required - The ID of the location the zone belongs to
        :param zone_id: String - Required - The ID of the location to delete
        :return: True if the location was deleted
        """
        path = f"location/{location_id}/zone/{zone_id}"
        try:
            res = self._delete(path)
            return res['message'].lower().find("success") != -1
        except WiliotCloudError as e:
            print("Failed to delete zone")
            raise e

    def query_metadata(self,  query):
        """
        Execute a query to get metadata
        :param query: String - Required - The query to send
        """
        path = f"metadataFetch"
        payload = {
            "query": query
        }
        try:
            res = self._post(path, payload)
            return res["data"]
        except WiliotCloudError as e:
            print("Failed to query metadata")
            raise e

    def get_event_count(self, connection_id, start_time, end_time):
        """
        Get number of events sent through a C2C connection
        :param connection_id: String - The connection ID to query for
        :param start_time: Integer - timestamp in seconds to start counting from
        :param end_time: Integer - timestamp in seconds to end counting at
        """
        path = f"connection/{connection_id}/startTime/{start_time}/endTime/{end_time}/events"
        print(path)
        res = self._get(path, override_client_path=f"owner/{self.owner_id}/")
        return res

    #### New Labels ##########
    def _create_labels(self, entity_type: EntityType, keys: list):
        """
        Create a new label (more precisely, a label key)
        :param entity_type: EntityType - The entity type (one of the EntityTypes) - required
        :param keys: List: Required - list of strings to create labels from
        """
        path = "label"
        payload = [
            {
                "entityType": entity_type.value,
                "key": k
            }
            for k in keys
        ]
        res = self._post(path, payload)
        return res

    def _get_labels(self, entity_type: EntityType=None, key: str=None):
        """
        Get a list of labels
        :param entity_type: EntityType: Optional -Only return labels for entities of this type
        :param key: String: Optional - only return labels with this key in them
        """
        path = "label"
        params = {}
        if entity_type is not None:
            params[ 'entityType'] = entity_type.value
        if key is not None:
            params['key'] = key
        res = self._get(path, params=params)
        return res['data']

    def _update_label(self, label_id: str, key: str):
        """
        Update a label's key
        :param label_id: String - required - The label's ID
        :param key: String: String - Required - The new key for the label
        """
        path = f"label/{label_id}"
        payload = {
            'key': key
        }
        try:
            res = self._patch(path, payload)
            if res['status_code'] == 200:
                return True
            else:
                return False
        except WiliotCloudError as wce:
            print(f"Failed to updated label {label_id}")
            raise wce

    def _delete_label(self, label_id: str):
        """
        Delete a label - Will also delete all instantiated versions of this label
        :param label_id: String - required - The label's ID
        returns: True is label was successfully deleted
        """
        path = f"label/{label_id}"
        try:
            res = self._delete(path)
            return res['status_code'] == 200
        except WiliotCloudError as wce:
            print(f"Failed to delete label {label_id}")
            raise wce

    def _associate_labels_to_entities(self, entity_type: EntityType, entity_ids: list, label_values: list):
        """
        Associate one or more existing labels to an entity
        :param entity_type: EntityType - Required - The type of entity to associate with the label
        :param entity_ids: List - Required - A list of entity IDs to associate with the label
        :param label_values: List - Required - List of dictionaries representing labels to associate with the
        entity and their values. Each element in the list should be a dictionary with the following fields:
            labelId - The ID of the label to associate
            value - The value to assign to this label
            For example: {"labelId": "7820d54e-eb2c-40db-9bbd-e8271ec06f95", "value": "5G"}
        :return: True is entity was successfully associated
        """
        path = f"entity/{entity_type.value}/label"
        assert all([isinstance(e, dict) and 'labelId' in list(e.keys()) and 'value' in list(e.keys()) for e in label_values]), f"label_values must contain a list of dictionaries each with a labelId field and a value field each"
        payload = [{
            'entityId': entity_id,
            'labels': label_values
        } for entity_id in entity_ids]
        res = self._post(path, payload)
        return res

    def _update_label_value_for_entities(self, entity_type: EntityType, entity_ids: list, label_values: list):
        """
        Update the association value for one ore more entities
        :param entity_type: EntityType - Required - The type of entity to update the value for
        :param entity_ids: List - Required - A list of entity IDs to update the value for
        :param label_values: List - Required - List of dictionaries representing labels to update
        Each element should be a discionary with the following fields
            labelId - The ID of the label to associate
            value - The value to update for this label
            For example: {"labelId": "7820d54e-eb2c-40db-9bbd-e8271ec06f95", "value": "5G"}
        """
        path = f"entity/{entity_type.value}/label"
        assert all([isinstance(e, dict) and 'labelId' in list(e.keys()) and 'value' in list(e.keys()) for e in label_values]), f"label_values must contain a list of dictionaries each with a labelId field and a value field each"
        payload = [{
            'entityId': entity_id,
            'labels': label_values
        } for entity_id in entity_ids]
        res = self._patch(path, payload)
        return res

    def _disassociate_labels_from_entities(self, entity_type: EntityType, entity_ids: list, labels: list):
        """
        Disassociate one or more existing labels to an entity
        :param entity_type: EntityType - Required - The type of entity to disassociate from the label
        :param entity_ids: List - Required - A list of entity IDs to disassociate from the label
        :param label_values: List - Required - List of label IDs to disassociate
        :return: True is entities was successfully disassociated
        """
        path = f"entity/{entity_type.value}/label"
        payload = [{
            'entityId': entity_id,
            'labelIds': labels
        } for entity_id in entity_ids]
        res = self._delete(path, payload)
        return res['status_code'] == 200

    def get_entity_type_keys_values(self, entity_type: EntityType, entity_id: str = None, key: str = None):
        """
        Get multiple key value pairs for an entity type. Filterable by entity ID and by key
        :param entity_type: EntityType - required - the type of entity to return labels and values for
        :param entity_id: String - Optional - If provided returns only label and value pairs for the entity with the
        specified entity_id
        :param key: String - optional - filter only labels with the specified key
        """
        if entity_id is None:
            path = f"entity/{entity_type.value}/label"
        else:
            path = f"entity/{entity_type.value}/{entity_id}/label"
        params = {}
        if key is not None:
            params['key'] = key
        return self._get(path, params=params).get('data',[])

    def get_label_values(self, entity_type: EntityType, label_id: str=None):
        """
        Get all values of a label for a specific entity type
        :param entity_type: EntityType - Required - the type of entity to search for
        :param label_id: String - Required - the label ID to search for
        """
        path = f"entity/{entity_type.value}/label/{label_id}/values"
        return self._get(path)

    def set_keys_values_for_entities(self, entity_type: EntityType, entity_ids: list, keys_values: dict, overwrite_existing: bool = False):
        """
        Create a new key value pair for a list of entities
        :param entity_type: EntityType - Required - the entity type of the entity to add the key value pair to
        :param entity_ids: List - Required - a list of entity IDs to add the key value pairs to
        :param keys_values: Dictionary - Required - A dictionary of key and values to add to the specified entities
        :param overwrite_existing: Boolean - Optional - If True any existing association to the requested labels will be overwritten
        :return: Boolean - True if successful, False otherwise
        """
        # For each key value pair in the keys_value dictionary - create the label if it doesn't already exist
        key_ids_and_values = {}
        for key, value in keys_values.items():
            try:
                res = self._create_labels(entity_type=entity_type, keys=[key])
                # Since we're only trying to create a single label - a success means we were able to
                if res['status_code'] == 200:
                    label_id = res['data'][0]['id']
                elif res['status_code'] == 207:
                    label_id = res['data']['failedLabels'][0].get('labelId', None)
                else:
                    print(
                        f"Failed to create label {key} for entity type {entity_type} due to: {wce.args[0]}. Will not create a key-value pair")
                    continue
                key_ids_and_values[label_id] = value
            except WiliotCloudError as wce:
                # Check if the error is that the label already exists
                if wce.args[0].get('data', {}).get('failedLabels', [{}])[0].get('reason', '').find('exist') != -1:
                    label_id = wce.args[0]['data']['failedLabels'][0].get('labelId', None)
                    key_ids_and_values[label_id] = value
                else:
                    print(f"Failed to create label {key} for entity type {entity_type} due to: {wce.args[0]}. Will not create a key-value pair")
                    continue
        # Once we have a label ID - new or existing - associate a new value for a specific entity
        try:
            res = self._associate_labels_to_entities(entity_type=entity_type,
                                                     entity_ids=entity_ids,
                                                     label_values=[{'labelId': key,
                                                                    'value': value} for key, value in key_ids_and_values.items()])
            if res['status_code'] == 200:
                return True
            elif res['status_code'] == 207:
                # Partial success
                if overwrite_existing:
                    for entity in res['data']:
                        if entity['status'].lower() != 'success':
                            for label in entity['failedLabels']:
                                if label['reason'].find('exist') != -1:
                                    # If there is already a value associated with this label for this entity - update it
                                    self._update_label_value_for_entities(entity_type=entity_type,
                                                                          entity_ids=[entity['entityId']],
                                                                          label_values=[{'labelId': key,
                                                                                         'value': value} for key, value in key_ids_and_values.items()])
                                    return True
            else:
                return False

        except WiliotCloudError as wce:
            # If asked to overwrite - examine the results
            if overwrite_existing:
                for entity in wce.args[0]['data']:
                    for label in entity.get('failedLabels'):
                        if label.get('reason').find('exists') != -1:
                            value = key_ids_and_values[label['labelId']]
                            self._update_label_value_for_entities(entity_type=entity_type,
                                                                  entity_ids=[entity['entityId']],
                                                                  label_values=[{'labelId': label['labelId'],
                                                                                 'value': key_ids_and_values[label['labelId']]}])
                return True
            else:
                raise

    def get_entity_keys_values(self, entity_type: EntityType, entity_id: str, key: str=None):
        """
        Get all key value pairs for an entity
        :param entity_type: EntityType - Required - the entity type of the entity to add the key value pair to
        :param entity_id: String - Required - the ID of the entity to query
        :param key: String - Optional - filter only values for the provided key
        :return: List of key value pairs for the provided entity
        """
        path = f"/entity/{entity_type.value}/{entity_id}/label"
        params = {}
        if key is not None:
            params['key'] = key
        entity_key_values = self._get(path=path, params=params)
        return entity_key_values.get('data', [])

    def delete_entities_key_value(self, entity_type: EntityType, entity_ids: list, key: str):
        """
        Delete a key value pair for the provided entity
        :param entity_type: EntityType - Required - The entity type of the entity to delete the key value
        :param entity_ids: List - Required - A list of the entity IDs of the entities to delete the key for
        :param key: String - Required - A key to remove
        """
        assert isinstance(entity_ids, list), "entity_ids must be a list"
        path = f"/entity/{entity_type.value}/label"
        try:
            # Get all labels
            label = self._get_labels(entity_type=entity_type, key=key)[0]
            label_ids = [label['id']]
        except IndexError:
            raise KeyNotFound
        payload = [{
            'entityId': entity_id,
            'labelIds': label_ids
        } for entity_id in entity_ids]
        try:
            res = self._delete(path, payload)
        except Exception as e:
            res = json.loads(e.args[0])
            if res.get('data', {})[0].get('failedLabels', [])[0].get('reason').lower().find('not found') != -1:
                raise KeyValueNotFound
            else:
                raise e
        return res['status_code'] == 200

    # Generic events API
    def generate_generic_event(self, asset_id: str, category_id: str, event_name: str, value: str,
                               key_set: list, confidence: float = 1.0, start: int = None, end: int = None):
        """
        Generate a generic event
        :param asset_id: String - Required - The event's asset ID
        :param category_id: String - required - The events category ID
        """
        path = "event-api-record"
        payload = {
            "assetId": asset_id,
            "categoryId": category_id,
            "eventName": event_name,
            "value": value,
            "keySet": [
                {"key": ks["key"], "value": ks["value"]} for ks in key_set
            ],
            "confidence": confidence,
        }
        if start is not None:
            payload["start"] = start
        if end is not None:
            payload["end"] = end
        try:
            res = self._post(path, payload, override_client_path="owner/{owner_id}/".format(owner_id=self.owner_id))
            return res['status_code'] == 200
        except WiliotCloudError as wce:
            print(f"Failed to generate generic event due to: {wce.args[0]}")

    # Verification API calls

    def verify_pixels(self, pixel_ids: list, start_time: str):
        """
        Check whether packets from the provided pixels were uploaded to the cloud
        :param pixel_ids: List of pixel IDs to check
        :param start_time: String - Required - When to check from. Should be between NOW-12h and NOW
        """
        path = "verify/pixel"
        params = {
            'ids': ','.join(pixel_ids),
            'startTime': start_time
        }
        res = self._get(path, params=params, override_client_path="owner/{owner_id}/".format(owner_id=self.owner_id))
        return res['data']
