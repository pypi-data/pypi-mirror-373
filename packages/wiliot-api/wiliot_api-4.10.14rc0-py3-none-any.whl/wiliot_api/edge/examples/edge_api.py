# """
# Copyright (c) 2016- 2023, Wiliot Ltd. All rights reserved.
#
# Redistribution and use of the Software in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#   1. Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   2. Redistributions in binary form, except as used in conjunction with
#   Wiliot's Pixel in a product or a Software update for such product, must reproduce
#   the above copyright notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the distribution.
#
#   3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
#   may be used to endorse or promote products or services derived from this Software,
#   without specific prior written permission.
#
#   4. This Software, with or without modification, must only be used in conjunction
#   with Wiliot's Pixel or with Wiliot's cloud service.
#
#   5. If any Software is provided in binary form under this license, you must not
#   do any of the following:
#   (a) modify, adapt, translate, or create a derivative work of the Software; or
#   (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
#   discover the source code or non-literal aspects (such as the underlying structure,
#   sequence, organization, ideas, or algorithms) of the Software.
#
#   6. If you create a derivative work and/or improvement of any Software, you hereby
#   irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
#   royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
#   right and license to reproduce, use, make, have made, import, distribute, sell,
#   offer for sale, create derivative works of, modify, translate, publicly perform
#   and display, and otherwise commercially exploit such derivative works and improvements
#   (as applicable) in conjunction with Wiliot's products and services.
#
#   7. You represent and warrant that you are not a resident of (and will not use the
#   Software in) a country that the U.S. government has embargoed for use of the Software,
#   nor are you named on the U.S. Treasury Department’s list of Specially Designated
#   Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
#   You must not transfer, export, re-export, import, re-import or divert the Software
#   in violation of any export or re-export control laws and regulations (such as the
#   United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
#   and use restrictions, all as then in effect
#
# THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
# OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
# WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
# QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
# IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
# ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
# FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
# (SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
# (A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
# (B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
# (C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
# """
"""
 The following code snippet shows how to use pyWiliot for Wiliot's cloud services:
 Please change the owner IDs and tag IDs to match your credentials before running the code
"""

# Import the library
from wiliot_api.edge.edge import *
import os

# Define an owner ID
owner_id = "test_owner"  # ToDo: add here your owner ID

# Initialise an Wiliot edge client object
edge = EdgeClient(api_key=os.environ.get('WILIOT_EDGE_API_KEY'), owner_id=owner_id)

# Get a list of gateways owned by the owner
print(edge.get_gateways())

# Get details on a single gateway by its ID
print(edge.get_gateway(gateway_id="my-gateway-id"))

# Update a gateway's configuration
# First get its current configuration
config = edge.get_gateway("my-gateway-id")["reportedConf"]
# Make the required change - for example, change the pacer interval
config["additional"]["pacerInterval"] = 15
# Update the gateway's configuration
edge.update_gateways_configuration(gateways=["my-gateway-id"], config=config)

# Register a new gateway
edge.register_gateway(gateways=["my-new-gateway-id"])

# Delete a gateway from the account (to move to another account, for example)
edge.delete_gateway(gateway_id="my-gateway-id")


# Bridges

# Get a list of all bridges registered under the account with their configuration
print(edge.get_bridges())

# Get a list of all online bridges
print(edge.get_bridges(online=True))

# Get a list of bridges connected to a certain gateway
print(edge.get_bridges(gateway_id="my-gateway-id"))

# Update a bridge configuration
# First, get its current configuration
config = edge.get_bridge(bridge_id="my-bridge-id")["reportedConf"]
# Make the required change - for example, change the energizing pattern
config["additional"]["energizingPattern"] = 50
# Request the configuration change
print(edge.update_bridge_configuration(bridge_id="my-bridge-id", config=config))

# Change a bridge's name
print(edge.update_bridge_configuration(bridge_id="my-bridge-id", name="my_bridge_name"))

# Get a list of commands awaiting execution for a bridge
print(edge.get_bridge_non_dismissed_commands(bridge_id="my-bridge-id"))

# Dismiss all pending commands for a bridge
edge.dismiss_bridge_non_dismissed_commands(bridge_id="my-bridge-id")

