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

import datetime
import os
import shutil
from sys import platform
from enum import Enum
import datetime


def release_for_partners(wiliot_pkg_list=None, folder_to_save='', wiliot_ver='', branch_name='master',
                         username_bitbucket=None, password_bitbucket=None):
    # check user inputs
    if wiliot_pkg_list is None:
        wiliot_pkg_list = ['wiliot-deployment-tools', 'wiliot-testers', 'wiliot-tools',
                           'wiliot-core', 'wiliot-api']  # all repos
    elif isinstance(wiliot_pkg_list, str):
        wiliot_pkg_list = wiliot_pkg_list.split(',')
    if folder_to_save == '':
        folder_to_save = os.path.join(os.path.expanduser('~'), 'Desktop')

    if wiliot_ver == '':
        wiliot_ver = datetime.datetime.strftime(datetime.datetime.now(), '%d-%m-%Y')

    # clone pywiliot repos:
    print("---------------------------\nopen a new folder under the specified folder:\n---------------------------")
    wiliot_folder_name = f'pywiliot_{wiliot_ver}@need_to_delete'
    wiliot_folder_path = os.path.join(folder_to_save, wiliot_folder_name)
    if os.path.isdir(wiliot_folder_path):
        raise FileExistsError(f'A folder with the same name is already exist ({wiliot_folder_path}), '
                        f'please rename wiliot_ver or change the folder location')
    os.makedirs(wiliot_folder_path)

    # clone all relevant packages
    for package_name in wiliot_pkg_list:
        repo_name = 'py' + package_name
        folder_name = package_name.replace('-', '_')

        print(f'--------------------------------------------------------------------\n'
              f'Clone wiliot package: {package_name}\n'
              f'--------------------------------------------------------------------')
        repo_folder = os.path.join(wiliot_folder_path, repo_name)
        if username_bitbucket is None and password_bitbucket is None:
            p = os.popen(f'git clone --single-branch --branch {branch_name} git@bitbucket.org:wiliot/{repo_name}.git '
                         f'{repo_folder}')
            rsp = p.read()
            print(rsp)

        elif username_bitbucket is not None and password_bitbucket is not None:
            p = os.popen(f'git clone https://{username_bitbucket}:{password_bitbucket}@bitbucket.org'
                         f'/wiliot/{repo_name}.git@{branch_name} {wiliot_folder_path}')
            rsp = p.read()
            print(rsp)
        else:
            print('you Must specified both username and password or do NOT specified neither '
                  'for installation using SSH key')
            return

        print("--------------------------------------------------------------------\n"
              "Remove unnecessary files from folder:\n"
              "--------------------------------------------------------------------")
        f_to_delete = []
        for (dir_path, dir_names, filenames) in os.walk(repo_folder):
            if 'internal' in dir_names:
                f_to_delete.append(os.path.join(dir_path, 'internal'))
        for f in f_to_delete:
            try:
                shutil.rmtree(f)
                print(f'remove {f}')
            except Exception as e:
                print(f'could not remove {f} due to {e}')
        shutil.copytree(os.path.join(repo_folder, folder_name),
                        os.path.join(os.path.join(folder_to_save, wiliot_folder_name.split('@')[0]), folder_name))

    print("done")


if __name__ == '__main__':
    # release_for_partners(wiliot_pkg_list='wiliot-tools,wiliot-core', folder_to_save='C:/Users/shunit/Desktop/test_p',
    #                      wiliot_ver='5.5.5')
    import argparse

    parser = argparse.ArgumentParser(description='Update Wiliot Internal Packages')
    parser.add_argument('-p', '--package_list', help='list of package names separated by comma. '
                                                     'valid option(wiliot-api,wiliot-core,'
                                                     'wiliot-tools,wiliot-testers,wiliot-deployment-tools')
    parser.add_argument('-f', '--folder_to_save', help='The folder to save the output files')
    parser.add_argument('-b', '--branch_name', help='The branch name you want to use. the default is master',
                        default='master')
    parser.add_argument('-v', '--wiliot_version', help='If specified, all packages will be stored under a folder name '
                                                       '"pwiliot_VERSION". default will be the current date',
                        default='')
    parser.add_argument('-u', '--username', help='If specified, install based username and password and not SHH key',
                        default=None)
    parser.add_argument('-pass', '--password',
                        help='If specified,  install based username and password and not SHH key',
                        default=None)
    args = parser.parse_args()
    package_list_str = args.package_list
    package_list = package_list_str.split(',')

    release_for_partners(wiliot_pkg_list=package_list, folder_to_save=args.folder_to_save,
                         wiliot_ver=args.wiliot_version, branch_name=args.branch_name,
                         username_bitbucket=args.username, password_bitbucket=args.password)
