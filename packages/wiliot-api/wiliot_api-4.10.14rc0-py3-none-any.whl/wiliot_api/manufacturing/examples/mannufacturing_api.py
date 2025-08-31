# """
# Copyright (c) 2016- 2025, Wiliot Ltd. All rights reserved.
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
 The following code snippet shows how to use pyWiliot for Wiliot's Manufacturing API:
 To use, please make sure to define the following environment variables to store your Wiliot API credentials:
 WILIOT_OAUTH_USERNAME
 WILIOT_OAUTH_PASSWORD
"""

# Import the library
from wiliot_api.manufacturing.manufacturing import *
import os

# Initialise an Wiliot client object
wiliot_manufacturing = ManufacturingClient(os.environ.get('WILIOT_OAUTH_USERNAME'),
                                           os.environ.get('WILIOT_OAUTH_PASSWORD'))

# Change the owner for a sequence of pixel IDs - useful for changing consecutive IDs - like part of a reel
req = wiliot_manufacturing.change_pixel_owner_by_range("first_pixel_id", "last_pixel_id", "from_owner_id",
                                                       "to_owner_id")

# Change the owner for a list of pixel IDs - When non-consecutive IDs need changing - up to 3000 pixels
req = wiliot_manufacturing.change_pixel_owner_by_list(["tag_1", "tag_2", "tag_3"], "from_owner_id", "to_owner_id")

# Change the owner of pixels by file - when needing to change more than 3000, non-consecutive IDs
#
# The file should be formatted as follows:
# tagId
# tag_1_id
# tag_2_id
# .....
req = wiliot_manufacturing.change_pixel_owner_by_file("from_owner_id", "to_owner_id", "/path/to/file")

# Each of the functions above returns a string representing a request ID. To check on the status of the request
print(wiliot_manufacturing.get_pixel_change_request_status(req))
