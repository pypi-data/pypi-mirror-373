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
from wiliot_api.api_client import Client, WiliotCloudError
from enum import Enum


class GatewayNotFound(Exception):
    pass


class UnknownGatewayConfKey(Exception):
    pass


class SurveyNotFound(Exception):
    pass

class SurveyStillRunning(Exception):
    pass


class BridgeAction(Enum):
    BLINK_LED = 'blinkBridgeLed'
    REBOOT = 'rebootBridge'


class EdgeClient(Client):
    def __init__(self, api_key, owner_id, env='prod', region='us-east-2', cloud='', log_file=None, logger_=None,
                 keep_alive=True, base_url=None):
        self.client_path = f"owner/{owner_id}/".format(owner_id=owner_id)
        self.owner_id = owner_id
        super().__init__(api_key=api_key, env=env, region=region, cloud=cloud, log_file=log_file, logger_=logger_,
                         keep_alive=keep_alive, base_url=base_url)

    def get_gateways(self, params={}):
        """
        Get a list of gateways owned by the owner
        :param params: Optional - a dictionary of allowed parameters to pass to the endpoint. Acceptable keys are:
                       search_query - a string that filters returned gateways by any field
                       ids = a string made of comma separated gateway IDs
                       online - Boolean. True= return only online gateways
                       busy - Boolean
                       active - Boolean
                       order_by - one of: gateway_id/gateway_name, gateway_type
        :return: A list of gateways
        """
        path = "gateway"
        all_gateways = []
        final_params = params.copy()
        while True:
            response = self._get(path, params=final_params)
            all_gateways += response["data"]
            if response.get("meta", {}).get("hasNext"):
                final_params['cursor'] = response["meta"]["cursor"]
            else:
                break
        return all_gateways

    def get_gateway(self, gateway_id):
        """
        Get a gateway's details including the applications it's associated with
        :param gateway_id:
        :return: A dictionary containing the information returned by the API
        """
        path = "gateway/{}".format(gateway_id)
        try:
            result = self._get(path)
            return result["data"]
        except WiliotCloudError as wce:
            if wce.args[0]['status_code'] == 404:
                raise GatewayNotFound
            else:
                raise wce

    def register_gateway(self, gateways):
        """
        Register one or more Wiliot gateways
        :param gateways: list of gateway IDs to register
        :return: True if successful
        """
        assert isinstance(gateways, list), "gateways parameter must be a list of gateway IDs"
        payload = {
            "gateways": gateways
        }
        path = "gateway"
        response = self._put(path=path, payload=payload)
        return response["data"].lower() == "ok"

    def approve_gateway(self, gateway_id):
        """
        Approve a gateway. This endpoint must be called before a gateway can start pushing
        Wiliot packet payloads to the Wiliot cloud
        :param gateway_id: The ID of the gateway to approve
        the API will return a userCode only gateways in a 'registered' state
        :return: True if successful
        """
        path = "gateway/{}/approve".format(gateway_id)
        payload = {}
        response = self._post(path, payload)
        return response["data"].lower() == "ok"

    def delete_gateway(self, gateway_id):
        """
        Delete a gateway from the Wiliot cloud. This gateway will no longer be able to push Wiliot packet
        payloads to the Wiliot cloud
        :param gateway_id: The Id of the gateway to delete
        :return: True if successful
        """
        path = "gateway/{}".format(gateway_id)
        response = self._delete(path, payload={})
        return response['message'].lower().find("success") != -1

    def update_gateway_configuration(self, gateway_id, config, gateway_name=None):
        path = f"gateway/{gateway_id}"
        payload = {
            "desired": config
        }
        if gateway_name is not None:
            payload['gatewayName'] = gateway_name
        response = self._post(path=path, payload=payload)
        return response.get('message').lower().find('success') != -1

    def update_gateways_configuration(self, gateways, config):
        """
        Update one or more gateways' configuration
        :param gateways: A list of gateway IDs
        :param config: A dictionary - The desired configuration
        :return: True if successful
        """
        assert isinstance(gateways, list), "gateways argument must be a list"
        payload = {
            "desired": config,
            "gateways": gateways
        }

        path = "gateway"
        response = self._post(path=path, payload=payload)
        return response.get('message').lower().find('ok') != -1

    def register_third_party_gateway(self, gateway_id, gateway_type, gateway_name):
        """
        Register a third-party (non-Wiliot) gateway and receive an access and refresh token
        to be used by the gateway for sending tag payloads to the Wiliot cloud
        :param gateway_id: String - A unique ID for the gateway
        :param gateway_type: String - Can be used to group gateways of the same type
        :param gateway_name: String - A human readable name for the gateway
        :return: A dictionary of the following format:
        {
            "data": {
                "access_token": "...",
                "expires_in": 43199,
                "refresh_token": "...",
                "token_type": "Bearer",
                "userId": "...",
                "ownerId": "wiliot_cloud"
            }
        }
        """
        path = "gateway/{}/mobile".format(gateway_id)
        payload = {
            "gatewayType": gateway_type,
            "gatewayName": gateway_name
        }
        response = self._post(path, payload=payload)
        return response

    def send_custom_message_to_gateway(self, gateway_id, custom_message):
        """
        Send custom message to gateway
        :param gateway_id: String - The ID of the gateway
        :param custom_message: String - Custom message to send
        :return: Bool - True if successful
        """
        path = "gateway/{}/custom-message".format(gateway_id)
        payload = custom_message
        response = self._post(path, payload=payload)
        return response.get('data').lower() == 'ok'

    # Bridge related functionality
    def get_bridges_connected_to_gateway(self, gateway):
        """
        Get a list of gateways connected (controlled by) a gateway
        :param gateway: String - A Gateway ID to query for
        :return: A list of dictionaries for all bridges
        """
        path = "gateway/{}/bridge".format(gateway)
        try:
            res = self._get(path)
            return res["data"]
        except WiliotCloudError as e:
            if e.args[0]['message'].lower().find("not found") != -1:
                raise WiliotCloudError("Gateway {} could not be found".format(gateway))
            else:
                raise

    def get_bridges(self, online=None, gateway_id=None, params={}):
        """
        Get all bridges "seen" by gateways owned by the owner
        :param online: A boolean - optional. Allows to filter only online (True) or offline (False) bridges
        :param gateway_id: A string - optional. Allows to filer only bridges currently connected to the gateway
        :param params: Optional - a dictionary of allowed parameters to pass to the endpoint. Acceptable keys are:
               search_query - a string that filters returned gateways by any field
               ids = a string made of comma separated gateway IDs
               online - Boolean. True= return only online gateways
               activeDebugBridges - Boolean - if True returns only bridges currently being used to run a site survey
               locationId - Only return bridges associated with the provided locationId
               zoneId - Only return bridges associated with the provided zoneId
               order_by - one of: gateway_id/gateway_name, gateway_type
               withConnections - Boolean - whether to return a list of connections for each bridge
        :return: A list of bridges
        """
        path = "bridge"
        final_params = params.copy()
        if online is not None:
            final_params['online'] = online
        try:
            all_bridges = []
            while True:
                res = self._get(path, params=final_params)
                bridges = res["data"]
                if gateway_id is not None:
                    bridges = [b for b in bridges if any([c["connected"] and c["gatewayId"] == gateway_id for c
                                                          in b["connections"]])]
                all_bridges += bridges
                if res.get("meta", {}).get("hasNext"):
                    final_params["cursor"] = res["meta"]["cursor"]
                else:
                    break
            return all_bridges
        except WiliotCloudError:
            raise

    def get_bridge(self, bridge_id, params={}):
        """
        Get information about a specific bridge
        :param bridge_id: String - the ID of the bridge to get information about
        :param params: Optional - a dictionary of allowed parameters to pass to the endpoint. Acceptable keys are:
               activeDebugBridges - Boolean - if True returns only bridges currently being used to run a site survey
               withConnections - Boolean - whether to return a list of connections for the bridge
        :return: A dictionary containing bridge information
        :raises: WiliotCloudError if bridge cannot be found
        """
        path = "bridge/{}".format(bridge_id)
        try:
            res = self._get(path, params=params)
            return res["data"]
        except WiliotCloudError as e:
            raise

    def claim_bridge(self, bridge_id):
        """
        Claim bridge ownership
        :param bridge_id: String - The ID of the bridge to claim
        :return: True if successful
        """
        path = "bridge/{}/claim".format(bridge_id)
        try:
            res = self._post(path, None)
            return res["message"].lower().find("successfully") != -1
        except WiliotCloudError as e:
            print("Failed to claim bridge")
            raise WiliotCloudError("Failed to claim bridge. Received the following error: {}".format(e.args[0]))

    def get_bridge_versions(self, include_beta=False):
        """
        Get all bridge versions
        :param include_beta: Boolean - If True returns also beta bridge versions
        """
        path = "bridge/version"
        res = self._get(path, params={'include_beta': include_beta}, override_client_path="")
        return res["data"]

    def get_bridge_non_dismissed_commands(self, bridge_id: str):
        """
        Get all non-dismissed commands for a given bridge
        :param bridge_id: String - The ID of the bridge to get non-dismissed commands for
        """
        path = f"bridge/{bridge_id}/command"
        res = self._get(path)
        return res["data"]

    def dismiss_bridge_non_dismissed_commands(self, bridge_id: str):
        """
        Dismiss all non-dismissed commands for a given bridge
        :param bridge_id: String - The ID of the bridge to get non-dismissed commands for
        :return: True if successful
        """
        path = f"bridge/{bridge_id}/dismiss"
        payload = {}
        try:
            res = self._post(path, payload=payload)
            return res['status_code'] == 200
        except WiliotCloudError as e:
            raise WiliotCloudError(
                "Failed to dismiss non-dismissed commands for bridge. Received the following error: {}".format(e.args[0]))

    def unclaim_bridge(self, bridge_id: str):
        """
        Release ownership of claimed bridge
        :param bridge_id: String - The ID of the bridge to unclaim
        :return: True if successful
        """
        path = "bridge/unclaim"
        payload = {
            "ids": [bridge_id]
        }
        try:
            res = self._post(path, payload)
            return res["message"].lower().find("successfully") != -1
        except WiliotCloudError as e:
            print("Failed to release bridge")
            raise WiliotCloudError(
                "Failed to release claimed bridge. Received the following error: {}".format(e.args[0]))

    def unclaim_bridges(self, bridge_ids: list):
        """
        Release ownership of claimed bridge
        :param bridge_ids: List - A list of bridges to unclaim
        :return: True if successful
        """
        path = "bridge/unclaim"
        payload = {
            "ids": bridge_ids
        }
        try:
            res = self._post(path, payload)
            return res["message"].lower().find("successfully") != -1
        except WiliotCloudError as e:
            print("Failed to release bridge")
            raise WiliotCloudError(
                "Failed to release claimed bridge. Received the following error: {}".format(e.args[0]))

    def _generate_bridge_configuration_payload(self, bridge_info, config={}):
        """
        Creates a payload for updating bridge(s) configuration. Can handle both legacy and MEL
        type configuration structures.
        :param bridge_info: Required - a dictionary returned by the get_bridge() function
        :param config: A dictionary containing the changed configuration items
        :returns: A payload that can be sent to update_bridge(s)_configuration endpoints
        """
        payload = {}
        # Bridge configuration has a "config" key - flat configuration structure
        if len(bridge_info.get("config", {}).keys()):
            payload["config"] = {}
            # Look for the keys from the provided config dictionary in the existing configuration
            for key in list(config.keys()):
                if key in list(bridge_info["config"].keys()):
                    payload["config"][key] = config[key]
                else:
                    print(f"Key {key} does not exist in bridge {bridge_info['id']} config")
        # Bridge configuration has a "modules" key - hierarchical configuration structure
        elif len(bridge_info.get("modules", {}).keys()):
            payload["modules"] = {}
            # If the provided config is already arranged in the required hierarchy
            if set(config.keys()).issubset(bridge_info["modules"].keys()):
                # Use the provided config as is
                payload["modules"] = config
            else:
                payload['modules'] = {}
                for key in config.keys():
                    if key in bridge_info["modules"].keys():
                        payload['modules'][key] = config[key]
                    elif key == 'version' or key == 'desiredVersion':
                        payload['desiredVersion'] = config[key]
                    else:
                        try:
                            parent_module = [m for m in bridge_info['modules'].keys() if
                                             key in list(bridge_info['modules'][m]['config'].keys())][0]
                            try:
                                payload["modules"][parent_module][key] = config[key]
                            except KeyError:
                                payload["modules"][parent_module] = {key: config[key]}
                        except IndexError:
                            print(f"Could not find parent module for config key {key}. Will not apply it")
                            continue
        # Neither keys exist - error state
        else:
            raise Exception("Returned bridge info does not contain configuration values")
        return payload

    def update_bridge_configuration(self, bridge_id, config={}, name=None):
        """
        Update a bridge's configuration
        :param bridge_id: A string - The ID of the bridge being updated
        :param config: Optional A dictionary of configuration keys and values
        :param name: Optional String - Specified the name for the bridge
        :return: True if the configuration update was received successfully. Note, that this is not an indication
        that a bridge's configuration was updated. To verify that configuration has been updated read the bridge
        configuration and compare to the requested values
        """
        # Obtain the current bridge configuration
        bridge_info = self.get_bridge(bridge_id)
        payload = self._generate_bridge_configuration_payload(bridge_info, config)

        path = "bridge/{}".format(bridge_id)
        if name is not None:
            payload["name"] = name
        try:
            res = self._put(path, payload)
            return res["message"].lower().find("updated bridge success") != -1
        except WiliotCloudError as e:
            print("Failed to update bridge configuration")
            raise WiliotCloudError(
                "Failed to update bridge configuration. Received the following error: {}".format(e.args[0]))

    def update_bridges_configuration(self, bridge_ids, config={}):
        """
        Update multiple bridges' configuration
        :param bridge_ids: A list of bridge IDs
        :param config: A dictionary of configuration keys and values
        :return: True if the configuration update was received successfully. Note, that this is not an indication
        that a bridge's configuration was updated. To verify that configuration has been updated read the bridge
        configuration and compare to the requested values
        """
        path = "bridge"
        # For this API call to work, all specified bridges must have the same firmware version, so getting
        # the bridge information from one of them should be enough
        bridge_info = self.get_bridge(bridge_ids[0])
        payload = self._generate_bridge_configuration_payload(bridge_info, config)
        payload['ids'] = bridge_ids
        try:
            res = self._put(path, payload)
            return res["message"].lower().find("updated success") != -1
        except WiliotCloudError as e:
            print("Failed to update bridges' configuration")
            raise WiliotCloudError(
                "Failed to update bridges' configuration. Received the following error: {}".format(e.args[0]))

    def send_action_to_bridge(self, bridge_id, action):
        """
        Send an action to a bridge
        :param bridge_id: String - the ID of the bridge to send the action to
        :param action: BridgeAction
        :return: True if the cloud successfully sent the action to the bridge, False otherwise
        """
        assert isinstance(action, BridgeAction), "action argument must be of type BridgeAction"
        path = "bridge/{}/action".format(bridge_id)
        payload = {
            "action": action.value
        }
        try:
            res = self._post(path, payload)
            return res['message'].lower().find("success") != -1
        except WiliotCloudError as e:
            print("Failed to send action to bridge")
            raise WiliotCloudError(
                "Failed to send action to bridge. Received the following error: {}".format(e.args[0]))

    def unassign_bridge_template(self, bridge_id: str):
        """
        Unassign a bridge from a template
        :param bridge_id: The ID of the bridge to unassign
        """
        path = f"bridge/{bridge_id}/unassign-template"
        payload = {}
        response = self._post(path, payload)
        return response['status_code'] == 200

    def start_survey(self, name: str, duration_ms: int, bridges: list):
        """
        Start a debug survey
        :param name: String - The name of the survey
        :param duration_ms: Integer - The duration of the survey in ms
        :param bridges: List of Bridges to include in the survey
        :return: A dictionary with the API call results. It includes, among other things the survey ID which
        can later be used to download the survey results
        """
        path = "survey"
        payload = {
            "surveyName": name,
            "durationMs": duration_ms,
            "bridges": bridges,
            "sendEmail": True
        }
        try:
            res = self._post(path, payload)
            return res["data"]
        except WiliotCloudError as e:
            raise WiliotCloudError(f"Failed to start survey with the following error: {e.args[0]}")

    def stop_survey(self, survey_id):
        """
        Stop a survey while it's running
        :param survey_id: String - The ID of the survey to stop
        :return: True if the survey was stopped
        """
        path = f"survey/{survey_id}/stop"
        try:
            response = self._delete(path)
            return response['message'].lower().find("success") != -1
        except WiliotCloudError as e:
            raise WiliotCloudError(f"Failed to stop survey with the following error: {e.args[0]}")

    def get_surveys(self):
        """
        Get All surveys conducted for an owner in the past 30 days
        """
        path = "survey"
        try:
            response = self._get(path)
            return response["data"]
        except WiliotCloudError as e:
            raise WiliotCloudError(f"Failed to get surveys due to error: {e.args[0]}")

    def get_survey_details(self, survey_id):
        """
        Get a specific survey's details
        :param survey_id: String - The ID of the survey to retrieve
        :raises SurveyNotFound: If the survey does not exist
        """
        path = f"survey/{survey_id}"
        try:
            response = self._get(path)
            return response["data"]
        except WiliotCloudError as e:
            if e.args[0]['status_code'] == 404:
                raise SurveyNotFound
            else:
                raise WiliotCloudError(f"Failed to get survey with the following error: {e.args[0]}")

    def get_survey_result(self, survey_id: str, output_directory: str = None):
        """
        Download a file containing a survey's result
        :param survey_id: String - The survey's ID (returned by a call to start_survey)
        :param output_directory: A string with the path to the desired output directory. If not provided the current
        directory will be used.
        :returns: The full path to the file containing the survey's result'
        """
        path = f"survey/{survey_id}/download"
        try:
            response = self._get_binary_file(path=path, output_directory=output_directory)
        except WiliotCloudError as wce:
            raise WiliotCloudError(f"Failed to get survey results with the following error: {wce.args}")
        return response

    # Pixel verification related API

    def get_verification_bridges(self):
        """
        Get the IDs of all bridges participating in verification
        """
        path = "verify/bridge"
        response = self._get(path)
        verification_bridges = [b['bridgeId'] for b in response["data"]]
        while response['metadata']['pagination']['nextCursor'] is not None:
            payload = {
                'nextCursor': response['metadata']['pagination']['nextCursor'],
                'pageSize': 100
            }
            response = self._get(path, params=payload)
            verification_bridges = verification_bridges + [b['bridgeId'] for b in response["data"]]

        return verification_bridges

    def add_verification_bridge(self, bridge_id):
        """
        Add a bridge to the list of verification bridges
        :param bridge_id: String - The ID of the bridge to add
        """
        path = "verify/bridge"
        payload = {
            "bridgeId": bridge_id
        }
        try:
            res = self._post(path, payload)
            return res["data"]
        except WiliotCloudError as e:
            raise WiliotCloudError(f"Failed to add bridge with the following error: {e.args[0]}")

    def delete_verification_bridge(self, bridge_id):
        """
        Delete a bridge from the verification bridges list
        :param bridge_id: String - The ID of the bridge to delete
        """
        path = f"verify/bridge/{bridge_id}"
        try:
            res = self._delete(path)
            return res["data"]
        except WiliotCloudError as e:
            raise WiliotCloudError(f"Failed to delete bridge with the following error: {e.args[0]}")


