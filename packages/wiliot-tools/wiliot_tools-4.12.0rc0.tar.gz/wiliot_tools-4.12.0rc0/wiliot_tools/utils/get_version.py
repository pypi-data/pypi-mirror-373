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

import os.path
from setuptools_scm import get_version as scm_get_version
import sys
import re


def get_version(action_type="current"):
    """

    @param action_type: can be current - egt the current version, next_patch, next_minor, next_major
    @type action_type: str
    @return: the version number
    @rtype: str
    """
    version_root = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    git_root = os.path.abspath(os.path.dirname(version_root))
    if os.path.isdir(os.path.abspath(os.path.join(git_root, ".git"))):
        version = scm_get_version(root=git_root,
                                  git_describe_command="git describe --long --dirty --tags --match [0-9]*.[0-9]*.[0-9]*")
    elif os.path.isfile(os.path.abspath(os.path.join(version_root, "version.py"))):
        from wiliot_tools.version import __version__
        version = __version__
    else:
        print(f"Couldn't get version from file: {os.path.abspath(os.path.join(version_root, 'version.py'))}, retrying setupscm get version")
        # give SCM another shot.. shouldn't get here:
        version = scm_get_version(root=git_root,
                                  git_describe_command="git describe --long --dirty --tags --match [0-9]*.[0-9]*.[0-9]*")

    if action_type == "current":
        return version
    else:
        ver_arr = list(re.split(r"\.", version, 4))
        if len(ver_arr) < 3:
            raise ValueError(f"not enough parts at version {version}!!!")
        if action_type == "next_patch":
            if len(ver_arr) == 3:  # we have a valid patch version and we want to progress by 1:
                ver_arr[2] = int(ver_arr[2]) + 1
        elif action_type == "next_minor":
            ver_arr[2] = 0
            ver_arr[1] = int(ver_arr[1]) + 1
        elif action_type == "next_major":
            ver_arr[2] = 0
            ver_arr[1] = 0
            ver_arr[0] = int(ver_arr[0]) + 1
        return f"{ver_arr[0]}.{ver_arr[1]}.{ver_arr[2]}"


if __name__ == '__main__':
    num_args = len(sys.argv)
    if num_args == 1:
        type = 'current'
    else:
        type = sys.argv[1]

    __version__ = get_version(type)
    print(__version__)
