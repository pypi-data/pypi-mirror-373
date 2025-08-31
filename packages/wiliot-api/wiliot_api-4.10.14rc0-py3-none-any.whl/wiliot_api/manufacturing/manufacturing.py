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
from enum import Enum
import os.path
from wiliot_api.api_client import Client, WiliotCloudError
import datetime
from uuid import uuid4
import jwt


class SensorsType(Enum):
    TEMPERATURE = {'url_name': 'temperatureCalibration', 'file_name': 'temperature_calibration'}


class SensorsActionsType(Enum):
    PROCESS_ONLY = {'processSensorFlag': 'true', 'updateSensorFlag': 'false'}
    PROCESS_AND_UPDATE = {'processSensorFlag': 'true', 'updateSensorFlag': 'true'}
    UPDATE_ONLY = {'processSensorFlag': 'false', 'updateSensorFlag': 'true'}


class TesterType(Enum):
    OFFLINE_TEST = 'offline-test'
    SAMPLE_TEST = 'sample-test'
    YIELD_TEST = 'yield-test'
    CONVERSION_YIELD_TEST = 'conversion-yield-test'
    ASSOCIATION_AND_VERIFICATION_TEST = 'association-and-verification-test'


class ManufacturingClient(Client):
    def __init__(self, oauth_username=None, oauth_password=None, api_key=None,
                 env='prod', region='us-east-2', cloud='', log_file=None, logger_=None, keep_alive=True, owner_id='', base_url=None):
        self.client_path = "manufacturing/"
        self.owner_id = owner_id
        super().__init__(oauth_username=oauth_username,
                         oauth_password=oauth_password, api_key=api_key,
                         env=env, region=region, cloud=cloud, log_file=log_file, logger_=logger_, keep_alive=keep_alive, base_url=base_url)

    # Pixel Ownership Change functions

    def change_pixel_owner_by_range(self, from_owner_id='', to_owner_id='', from_pixel_id='', to_pixel_id='',
                                    destination_cloud=None):
        """
        Request a change of ownership for a range of pixel IDs
        :param from_owner_id: String - the ID of the current owner
        :param to_owner_id: String - The ID of the new owner
        :param from_pixel_id: String - The first pixel ID
        :param to_pixel_id: String - The last pixel ID
        :param destination_cloud: String optional - The destination cloud to transfer to.
                                  Can be either GCP or None (same cloud - AWS)
        :return: The request tracking ID for future queries if successful. None, otherwise
        :raises: WiliotCloudError
        """
        from_owner_id = from_owner_id if from_owner_id else self.owner_id
        assert to_owner_id != '', "to_owner_id must be set"
        assert from_pixel_id != '' and to_pixel_id != '', "from_pixel_id and to_pixel_id must be set"

        path = "ownerChange"
        parameters = {
            "fromOwner": from_owner_id,
            "toOwner": to_owner_id
        }
        if destination_cloud is not None:
            parameters['destinationCloud'] = destination_cloud
        payload = {
            "fromTo": {
                "from": from_pixel_id,
                "to": to_pixel_id
            }
        }
        try:
            res = self._post(path, payload, params=parameters)
            return res.get("trackingRequestId", None)
        except WiliotCloudError as e:
            print("Failed to request pixel ownership change")
            raise e

    def change_pixel_owner_by_list(self, from_owner_id='', to_owner_id='', pixel_id_list=None, destination_cloud=None):
        """
        Request a change of ownership for a range of pixel IDs
        :param from_owner_id: String - the ID of the current owner
        :param to_owner_id: String - The ID of the new owner
        :param pixel_id_list: List of pixel IDs
        :param destination_cloud: String optional - The destination cloud to transfer to.
                                  Can be either GCP or None (same cloud - AWS)
        :return: The request tracking ID for future queries if successful. None, otherwise
        :raises: WiliotCloudError
        """
        from_owner_id = from_owner_id if from_owner_id else self.owner_id
        assert to_owner_id != '', "to_owner_id must be set"
        assert isinstance(pixel_id_list, list), "pixel_id_list must be a list"
        path = "ownerChange"
        parameters = {
            "fromOwner": from_owner_id,
            "toOwner": to_owner_id
        }
        if destination_cloud is not None:
            parameters['destinationCloud'] = destination_cloud
        payload = {
            "tagIds": pixel_id_list
        }
        try:
            res = self._post(path, payload, params=parameters)
            return res.get("trackingRequestId", None)
        except WiliotCloudError as e:
            print("Failed to request pixel ownership change")
            raise e

    def change_pixel_owner_by_file(self, from_owner_id='', to_owner_id='', pixel_id_file_path='', destination_cloud=None):
        """
        Request a change of ownership for a range of pixel IDs
        :param from_owner_id: String - the ID of the current owner
        :param to_owner_id: String - The ID of the new owner
        :param pixel_id_file_path : full path to a csv file containing one column called tagId
        :param destination_cloud: String optional - The destination cloud to transfer to.
                                  Can be either GCP or None (same cloud - AWS)
        :return: The request tracking ID for future queries if successful. None, otherwise
        :raises: WiliotCloudError
        """
        from_owner_id = from_owner_id if from_owner_id else self.owner_id
        assert to_owner_id != '', "to_owner_id must be set"
        assert os.path.isfile(pixel_id_file_path), f"pixel_id_file_path {pixel_id_file_path} is not a file"

        path = "ownerChange"
        parameters = {
            "fromOwner": from_owner_id,
            "toOwner": to_owner_id
        }
        if destination_cloud is not None:
            parameters['destinationCloud'] = destination_cloud
        with open(pixel_id_file_path, 'rb') as f:
            files_to_send = [
                ('file', (os.path.basename(pixel_id_file_path), f, 'text/csv'))
            ]
            try:
                res = self._post_with_files(path, files=files_to_send, params=parameters)
                return res.get("trackingRequestId", None)
            except WiliotCloudError as e:
                print("Failed to request pixel ownership change")
                raise e

    def get_pixel_change_request_status(self, request_tracking_id):
        """
        Get information about the status of an ownership change request
        :param request_tracking_id: String - The request tracking ID returned from the change pixel owner request call
        :return: A dictionary with information about the details and the progress of the request
        """
        path = "ownerChange"
        res = self._get(path, {'requestId': request_tracking_id})
        return res

    def get_pixel_change_request_details(self, request_tracking_id, out_file):
        """
        Get detailed information about each of the pixels change of ownership was requested for
        :param request_tracking_id: String - The request tracking ID returned from the change pixel owner request call
        :param out_file: A file handle - to write the returned values to, e.g. f = open('test.csv', 'w')
        :return: A CSV file with a line per tag
        """
        path = "ownerChange/tagsInfo"
        params = {
            'requestId': request_tracking_id
        }
        res = self._get_file(path, out_file, params=params)
        return res

    def get_pixel_change_requests(self, owner_id=''):
        """
        Get a list of owner change requests made historically
        :return:
        """
        owner_id = owner_id if owner_id else self.owner_id
        path = "ownerChange/requestsList"
        params = {
            'ownerId': owner_id,
            'cursor': None
        }
        has_next = True
        items = []
        while has_next:
            res = self._get(path, params=params)
            items = items + res['items']
            has_next = res['meta']['hasNext']
            params['cursor'] = res['meta']['cursor']
        return items

    # Pixel import API calls

    def import_pixels(self, owner_id='', request_id=''):
        """
        Import pixels into an account in another cloud
        :param owner_id: String - the owner ID to import the pixel into
        :param request_id: String - The request ID of the original change owner request
        :return: The value returned from the API
        """
        owner_id = owner_id if owner_id else self.owner_id
        assert request_id != '', "request_id must be set"

        path = f"owner/{owner_id}/pixelImport/{request_id}"
        try:
            res = self._post(path=path, payload={})
            return res
        except WiliotCloudError as wce:
            print("Failed to request pixel ownership change")
            raise wce

    def get_import_pixel_requests(self, owner_id=''):
        """
        Get a list of all pixel import request for an owner
        :param owner_id: String - The owner ID the pixel import request was made to
        :return: The list of requests
        """
        owner_id = owner_id if owner_id else self.owner_id

        path = f"owner/{owner_id}/pixelImport"
        res = self._get(path=path)
        return res

    def get_import_pixel_request(self, owner_id='', request_id=''):
        """
        Get information about a pixel import request
        :param owner_id: String - The owner ID the pixel import request was made to
        :param request_id: String - The request ID
        :return: The request info
        """
        owner_id = owner_id if owner_id else self.owner_id
        assert request_id != '', "request_id must be set"

        path = f"owner/{owner_id}/pixelImport/{request_id}"
        res = self._get(path=path)
        return res

    # Shipment Approval API calls

    def post_shipment_approval_request(self, external_id_prefix):
        """
        Request approval for a shipment with a specific external ID prefix.

        :param external_id_prefix: String - The reel external ID prefix for the shipment.
        :return: The tracking request ID if successful, otherwise None.
        :raises: WiliotCloudError if the request fails.
        """
        path = "shipmentApproval"
        try:
            res = self._post(path, {}, params={'externalIdPrefix': external_id_prefix})
            return res.get("trackingRequestId", None)
        except WiliotCloudError as e:
            print("Failed to request shipment approval")
            raise e

    def get_shipment_approval_request_status(self, request_id):
        """
        Get the status of a shipment approval request.

        :param request_id: String - The request tracking ID.
        :return: The status of the shipment approval request.
        """
        path = "shipmentApproval"
        res = self._get(path, {'requestId': request_id})
        return res

    def get_shipment_approval_request_details(self, request_id, out_file):
        """
        Get detailed information about a shipment approval request and save it to a file.
        :param request_id: String - The request tracking ID.
        :param out_file: String - The path to save the request details. e.g. f = open('test.csv', 'w')
        :return: A CSV file with a line per tag
        """
        path = "shipmentApproval/tagsInfo"
        res = self._get_file(path, out_file, {'requestId': request_id})
        return res

    def parse_payload(self, packet_version: str, flow_version: str, payloads: list, owner_id: str='', verbose: bool=False):
        """
        Parse a tag's payload
        :param packet_version: String - The packet version of the payload
        :param flow_version: String - The flow version of the payload in format "0xXXX"
        :param payloads: valid Wiliot tag payloads starting with the manufacturer ID
        :param owner_id: String - The ID of the owner to resolve this payload for
        :param verbose: Bool
        :return: A dictionary from the returned JSON
        """
        owner_id = owner_id if owner_id else self.owner_id
        flow_version = flow_version[2:-2] + '.' + flow_version[-2:]
        payload = {
            "packetVersion": packet_version,
            "flowVersion": flow_version,
            "payloads" : payloads
        }
        res = self._post("parsing", payload, override_client_path=f"owner/{owner_id}/", verbose=verbose)
        return res['data']
    
    def resolve_payload(self, payload, owner_id='', verbose=False):
        """
        Resolve a tag's payload
        :param payload: valid Wiliot tag payload starting with the manufacturer ID
        :param owner_id: String - The ID of the owner to resolve this payload for
        :param verbose: Bool
        :return: A dictionary from the returned JSON
        """
        owner_id = owner_id if owner_id else self.owner_id

        allowed_roles_to_resolve = ['manufacturing', 'resolve', 'asset-creator']
        now_ts = int(datetime.datetime.now().timestamp())
        decoded_token = jwt.decode(self.auth_obj.token['access_token'], options={"verify_signature": False})
        # Make sure the roles included in the token include "manufacturing"
        if not any([allowed in decoded_token['roles'] for allowed in allowed_roles_to_resolve]):
            raise Exception("The provided API key is not a manufacturing API key. Please use the appropriate key")
        # Make sure that the generated token allows access to the requested owner
        if owner_id not in decoded_token['owners'].keys() and owner_id != 'wiliot_cloud-ops':
            raise Exception(f"The provided API key does not belong to the requested owner ID: {owner_id}")
        payload = {
            'timestamp': now_ts,
            'packets': [
                {
                    'timestamp': now_ts,
                    'payload': payload
                }
            ],
            'gatewayType': 'cli',
            'gatewayId': str(uuid4())
        }
        res = self._post("resolve", payload, override_client_path=f"owner/{owner_id}/", verbose=verbose)
        return res['data'][0]

    def safe_resolve_payload(self, payload, owner_id='', verbose=False):
        """
        resolve payload with exception handling
        :param payload: valid Wiliot tag payload starting with the manufacturer ID
        :param owner_id: String - The ID of the owner to resolve this payload for
        :param verbose: bool - if true the resolve payload exception are printed, otherwise - are ignored
        :return: A dictionary from the returned JSON
        """
        owner_id = owner_id if owner_id else self.owner_id

        try:
            data = self.resolve_payload(payload=payload, owner_id=owner_id, verbose=verbose)
        except Exception as e:
            if "module 'jwt' has no attribute 'decode'" in e.__str__():
                print('please uninstall jwt python package and install the latest pyjwt package')
            if verbose:
                print(e)
            return {'externalId': 'no_external_id'}
        return data

    # Serialization API calls

    def serialize_tags(self, owner_id='', tags_payload_file_path=''):
        """
        Request to serialize (set tag ID) for tag(s) by payload
        :param owner_id: String - the ID of the tags' owner
        :param tags_payload_file_path : full path to a csv file containing two columns:
            payload
            tagId
        :return: The request tracking ID for future queries if successful. None, otherwise
        :raises: WiliotCloudError
        """
        owner_id = owner_id if owner_id else self.owner_id
        assert os.path.isfile(tags_payload_file_path), f"tags_payload_file_path {tags_payload_file_path} is not a file"

        path = "serialization"
        parameters = {
            "owner": owner_id,
        }
        with open(tags_payload_file_path, 'rb') as f:
            files_to_send = [
                ('file', (os.path.basename(tags_payload_file_path), f, 'text/csv'))
            ]
            try:
                res = self._post_with_files(path, files=files_to_send, params=parameters)
                return res.get("trackingRequestId", None)
            except WiliotCloudError as e:
                print("Failed to request pixel ownership change")
                raise e

    def get_tags_serialization_request_details(self, request_tracking_id):
        """
        Get information about the status of a tag serialization request
        :param request_tracking_id: String - The request tracking ID returned from the serialize_tags call
        :return: A dictionary with information about the details and the progress of the request
        """
        path = "serialization"
        res = self._get(path, params={'requestId': request_tracking_id})
        return res

    def get_tags_serialization_request_info(self, request_tracking_id, out_file):
        """
        Get details about a tags serialization request
        :param request_tracking_id: String - The request tracking ID returned from the serialize_tags call
        :param out_file: A file handle - to write the returned values to,  e.g. f = open('test.csv', 'w')
        :return: A CSV file with a line per tag
        """
        path = "serialization/tagsInfo"
        params = {
            'requestId': request_tracking_id
        }
        res = self._get_file(path, out_file, params=params)
        return res

    def get_tags_serialization_requests(self, owner_id=''):
        """
        Get a list of tag serialization requests made historically
        :return:
        """
        owner_id = owner_id if owner_id else self.owner_id
        path = "serialization/requestsList"
        params = {
            'ownerId': owner_id,
            'cursor': None
        }
        has_next = True
        items = []
        while has_next:
            res = self._get(path, params=params)
            items = items + res['items']
            has_next = res['meta']['hasNext']
            params['cursor'] = res['meta']['cursor']
        return items

    def upload_testers_data(self, tester_type, file_path, verbose=False):
        """
        upload testers log data run_data / packets_data to cloud
        :param tester_type: one of the option: offline-test, sample-test, yield-test
        :type tester_type: TesterType
        :param file_path: file full path for uploading tester data to cloud
        :type file_path: str
        :param verbose: log the response from cloud
        :type verbose: bool
        :return: success status
        :rtype: bool
        """
        file_name = os.path.basename(file_path)
        assert 'run_data' in file_name or 'packets_data' in file_name, \
            "file name must contains 'run_data' or 'packets_data' depending on the data type"

        common_run_name = file_name.split('@')[0]
        assert len(common_run_name) <= 64, f'common run name MUST be shorter then 64 characters, The specified common run name is {len(common_run_name)}'

        url = f'upload/testerslogs/{tester_type.value}'
        if 'run_data' in file_name:
            url += '/runs-indicators'
        elif 'packets_data' in file_name:
            url += '/packets-indicators'

        with open(file_path, 'rb') as f:
            files_to_send = [
                ('file', (file_name, f, 'text/csv'))
            ]
            res = self._post_with_files(url, files=files_to_send)
        if verbose:
            self.logger.info(res)

        return True

    def get_reel_id(self, owner_id='', payload='', reel_id_3_char=False, gen_type=None):
        """
        api to receive reel number from cloud
        :param owner_id:
        :type owner_id: str or int
        :param payload: should be {"printerId": <tester_station_name>}
        :type payload: dict
        :param reel_id_3_char: to indicate if reel id should be 3. the default is 4 characters for reel id
        :type reel_id_3_char: bool
        :param gen_type: reel generation - e.g. gen2
        :type gen_type: str or int
        :return: the reel id
        :rtype: str
        """
        owner_id = owner_id if owner_id else self.owner_id
        assert payload, "payload must be set"

        url_path = f'{owner_id}/tag/roll/print'
        reel_id_type = {'reelIdType': 'threeCharacters'} if reel_id_3_char else {}
        if gen_type is not None:
            gen_type = str(gen_type).lower()
            if '2' in gen_type or 'two' in gen_type:
                reel_id_type['generation'] = 'two'
            elif '3' in gen_type or 'three' in gen_type:
                reel_id_type['generation'] = 'three'
            else:
                raise Exception(f'unsupported gen_type: {gen_type}, gen type can be 2 or 3')

        res = self._post(path=url_path, url_params=reel_id_type,
                         payload=payload, override_client_path='owner/', verbose=True)
        return res

    def get_file_for_ppfp(self, common_run_name, tester_type, out_file):
        """
        get zip file for post process for partners. The file should include all tables
        based on the specified common run name
        :param common_run_name: the name of the run to extarct the post process tables
        :type common_run_name: str
        :param tester_type: can be offline-test, sample-test or yield-test (Future)
        :type tester_type: str
        :param out_file: zip file to save the output tables. e.g. f = open('test.zip', 'w')
        :type out_file: file object
        :return: response info
        :rtype: bool or str
        """
        url = f'upload/testerslogs/{tester_type}?commonRunName={common_run_name}'
        res = self._get_file(path=url, out_file=out_file, file_type='zip')

        return res

    def upload_calibrated_temperature_label(self, owner_id='', external_id='', tag_temperature=float('nan'), sensor_temperature=float('nan'),
                                            measurement_error=0, verbose=False):
        """
        uploading calibration points for temperature calibration process
        :param owner_id: the owner id of the tags
        :type owner_id: str or int
        :param external_id: the external id of the tag
        :type external_id: str
        :param tag_temperature: tag's temperature
        :type tag_temperature: float
        :param sensor_temperature: sensor's temperature
        :type sensor_temperature: float
        :param measurement_error: measurement error
        :type measurement_error: float
        :param verbose
        :type verbose: bool


        :return: success status
        :rtype: bool
        """
        owner_id = owner_id if owner_id else self.owner_id
        assert external_id, "external_id must be set"
        assert isinstance(tag_temperature, float) and str(tag_temperature) != 'nan', \
            "tag_temperature must be a valid float"
        assert isinstance(sensor_temperature, float) and str(sensor_temperature) != 'nan', \
            "sensor_temperature must be a valid float"

        if isinstance(measurement_error, float) and str(measurement_error) == 'nan':
            measurement_error = 0.0

        url = f'{owner_id}/data-label'
        payload = {"externalId": external_id,
                   "labelType": "TEMPERATURE",
                   "numericData": round(tag_temperature, 2),
                   "numericLabelValue": round(sensor_temperature, 2),
                   "measurementError": measurement_error}

        res = self._post(path=url, payload=payload, override_client_path='owner/', verbose=verbose)
        if verbose:
            self.logger.info(res)

        return True

    def upload_sensors_data(self,  owner_id='', file_path=None,
                            sensor_type=SensorsType.TEMPERATURE,
                            action_type=SensorsActionsType.PROCESS_ONLY,
                            common_run_name=None,
                            verbose=False):
        """
        upload sensors data to cloud
        actions types:
            process only - only add data to db tables,
            process and update also update the data label of the tags and calibrate them,
            only update takes the already processed data in the DB and update the tags labels to calibrate them
        :param sensor_type: one of the option: offline-test, sample-test, yield-test
        :type sensor_type: SensorsType
        :param action_type: options to different process once the data is uploaded
        :type action_type: SensorsActionsType
        :param file_path: file full path for uploading sensors data to cloud
        :type file_path: str or None
        :param common_run_name: relevant only for action type SensorsActionsType.UPDATE_ONLY.
        :type common_run_name: str
        :param owner_id: the owner id of the tags
        :type owner_id: str
        :param verbose: log the response from cloud
        :type verbose: bool
        :return: success status
        :rtype: bool
        """
        owner_id = owner_id if owner_id else self.owner_id
        if action_type == SensorsActionsType.UPDATE_ONLY:
            files_to_send = None
            assert common_run_name, \
                f"for UPDATE ONLY action type, common run name must be selected but passed: {common_run_name}"
            url_params = {'commonRunName': common_run_name, 'ownerId': owner_id}
            f = None
        else:
            file_name = os.path.basename(file_path)
            assert sensor_type.value['file_name'] in file_name, \
                f"file name must contains {sensor_type.value['file_name']} when selecting {sensor_type.name}"
            f = open(file_path, 'rb')
            files_to_send = [('file', (file_name, f, 'text/csv'))]
            url_params = {'ownerId': owner_id}

        url = f'upload/sensorData/{sensor_type.value["url_name"]}'
        url_params = {**url_params, **action_type.value}

        res = self._post_with_files(url, files=files_to_send, url_params=url_params)

        if verbose:
            self.logger.info(res)
        if f is not None:
            f.close()

        return True

    def partner_upload_file_to_s3(self, file_path=None, directory=None, file_name=None):
        """
        Uploads a specified file to the Wiliot cloud bucket.

        This method checks that the provided file is in JSON or CSV format, then uploads it to the specified
        directory in the cloud. If the file format is unsupported, an exception is raised. It sends the file
        as multipart form data to the cloud endpoint.

        :param file_path: Full local path of the file to upload.
        :type file_path: str
        :param directory: Cloud directory where the file will be uploaded.
        :type directory: str or None
        :return: Response from the cloud indicating the success or failure of the upload.
        :rtype: dict
        :raises Exception: If the file extension is not JSON or CSV.
        """
        if not (file_path.lower().endswith(".json") or file_path.lower().endswith(".csv")):
            raise Exception("Invalid file type: only .json and .csv files are supported for upload.")
        if file_name is None:
            file_name = os.path.basename(file_path)
        mime_type = 'application/json' if file_path.lower().endswith(".json") else 'text/csv'

        url = f'/partner/uploadFile/{directory}'

        try:
            with open(file_path, 'rb') as f:
                files_to_send = [('file', (file_name, f, mime_type))]
                res = self._post_with_files(url, files=files_to_send)
            return res

        except WiliotCloudError as e:
            self.logger.error(f"Failed to upload file to {url}. Error: {e}")
            raise Exception(f"File upload failed with error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred during file upload: {e}")
            raise e

    def get_sensors_data_details(self, common_run_name, owner_id='', sensor_type=SensorsType.TEMPERATURE):
        """
        Get information about the status of a tag serialization request
        :param common_run_name: relevant only for action type SensorsActionsType.UPDATE_ONLY.
        :type common_run_name: str
        :param owner_id: the owner id of the tags
        :type owner_id: str
        :param sensor_type: one of the option: offline-test, sample-test, yield-test
        :type sensor_type: SensorsType
        :return: A dictionary with information about the details and the progress of the request
        """
        owner_id = owner_id if owner_id else self.owner_id
        url = f'upload/sensorData/{sensor_type.value["url_name"]}'
        url_params = {'ownerId': owner_id, 'commonRunName': common_run_name}
        res = self._get(url, params=url_params)
        return res

    def get_sensors_data_tags_info(self, out_file, common_run_name, owner_id='', sensor_type=SensorsType.TEMPERATURE):
        """
        Get details about a tags serialization request
        :param common_run_name: relevant only for action type SensorsActionsType.UPDATE_ONLY.
        :type common_run_name: str
        :param owner_id: the owner id of the tags
        :type owner_id: str
        :param out_file: A file handle - to write the returned values to, e.g. f = open('test.csv', 'w')
        :param sensor_type: one of the option: offline-test, sample-test, yield-test
        :type sensor_type: SensorsType
        :return: A CSV file with a line per tag
        """
        owner_id = owner_id if owner_id else self.owner_id
        url = f'upload/sensorData/{sensor_type.value["url_name"]}/tagsInfo'
        url_params = {'ownerId': owner_id, 'commonRunName': common_run_name}
        res = self._get_file(url, out_file, params=url_params)
        return res