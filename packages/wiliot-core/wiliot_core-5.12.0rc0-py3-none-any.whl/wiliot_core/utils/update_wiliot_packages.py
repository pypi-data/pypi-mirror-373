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


import shutil
from os import popen
from os.path import join, isdir
from sys import platform
from enum import Enum
import os
import json
try:
    from tkinter import messagebox
except ModuleNotFoundError as e:
    print(f'could not import tkinter: {e}')


class WiliotPackages(Enum):
    CLOUD = ['pywiliot-api']
    CORE = ['pywiliot-core', 'pywiliot-api']
    TOOLS = ['pywiliot-tools', 'pywiliot-core', 'pywiliot-api']
    DEPLOYMENT = ['pywiliot-deployment-tools', 'pywiliot-tools', 'pywiliot-core', 'pywiliot-api']
    TESTERS = ['pywiliot-testers', 'pywiliot-tools', 'pywiliot-core', 'pywiliot-api']


def update_internal_wiliot_packages(wiliot_repo=WiliotPackages.CLOUD, branch_name='master',
                                    overwrite=False, no_wiliot_dep=False,
                                    username_bitbucket=None, password_bitbucket=None,
                                    install_from_local_folder='', install_from_git_folder='',
                                    branch_name_for_dep='master'):
    # check platform command prefix
    python_ver = ''
    if platform == "darwin" or platform == 'linux':
        # macos or linux
        python_ver = '3'
    # install pywiliot and requirements:
    # update dependencies
    print("----------------------------------\nupdate pip:\n----------------------------------")
    p = popen(f'python{python_ver} -m pip install --upgrade pip')
    rsp = p.read()
    print(rsp)
    pkg_versions = []
    req_status = []
    for repo_num, repo_name in enumerate(wiliot_repo.value):
        need_to_install = True
        package_name = repo_name.replace('py', '')
        folder_name = package_name.replace('-', '_')
        print('check if package already exist')
        p = popen(f'pip{python_ver} show {package_name}')
        rsp = p.read()
        print(rsp)
        if package_name in rsp:
            if overwrite:
                print(f'--------------------------------------------------------------------\n'
                      f'uninstall existing package: {package_name}\n'
                      f'--------------------------------------------------------------------\n')
                p = popen(f'pip{python_ver} uninstall {package_name} -y')
            else:
                print(f'--------------------------------------------------------------------\n'
                      f'for uninstall existing package: {package_name}, please press ENTER\n'
                      f'--------------------------------------------------------------------\n')
                p = popen(f'pip{python_ver} uninstall {package_name}')
            rsp = p.read()
            print(rsp)
        print(f'--------------------------------------------------------------------\n'
              f'update wiliot package: {package_name}\n'
              f'--------------------------------------------------------------------')
        if install_from_local_folder or install_from_git_folder:
            local_repo_path = join(install_from_local_folder if install_from_local_folder else install_from_git_folder,
                                   repo_name)
            if isdir(local_repo_path):
                p = popen(f'pip{python_ver} install -e {local_repo_path}  --upgrade')
                rsp = p.read()
                print(rsp)
                need_to_install = False
            else:
                print(f'{repo_name} does not exist in local folder, try to install from bitbucket')

        if need_to_install:
            if username_bitbucket is None and password_bitbucket is None:
                if repo_num == 0:
                    p = popen(f'pip{python_ver} install git+ssh://git@bitbucket.org/wiliot/{repo_name}.git'
                              f'@{branch_name}#egg={folder_name} --upgrade')
                else:
                    p = popen(f'pip{python_ver} install git+ssh://git@bitbucket.org/wiliot/{repo_name}.git'
                              f'@{branch_name_for_dep}#egg={folder_name} --upgrade')
                rsp = p.read()
                print(rsp)
                if 'Successfully installed' not in rsp.split('\n')[-2]:
                    print(
                        f'problem with ssh key credentials. Please rerun the script using username (-u) and password (-p).'
                        f'\nTo extract Attlasian username and password go to '
                        f'https://wiliot.atlassian.net/wiki/spaces/SW/pages/2890662124/'
                        f'PyWiliot+Installation+Guidelines+-+Private#using-username-and-password%3A')
                    return
            elif username_bitbucket is not None and password_bitbucket is not None:
                if repo_num == 0:
                    p = popen(
                        f'pip{python_ver} install git+https://{username_bitbucket}:{password_bitbucket}@bitbucket.org'
                        f'/wiliot/{repo_name}.git@{branch_name}#egg={folder_name} --upgrade')
                else:
                    p = popen(
                        f'pip{python_ver} install git+https://{username_bitbucket}:{password_bitbucket}@bitbucket.org'
                        f'/wiliot/{repo_name}.git@{branch_name_for_dep}#egg={folder_name} --upgrade')
                rsp = p.read()
                print(rsp)
            else:
                print('you Must specified both username and password or do NOT specified neither '
                      'for installation using SSH key')
                return

        print(f'check wiliot package: {package_name}')
        p = popen(f'pip{python_ver} show {package_name}')
        rsp = p.read()
        print(rsp)
        if 'Location' in rsp:
            pkg_versions.append(rsp.split('Version: ')[1].split('\n')[0])
            req_path = rsp.split('Location: ')[-1].split('\n')[0]
            if install_from_git_folder:
                if 'Editable project location: ' in rsp:
                    req_path = rsp.split('Editable project location: ')[-1].split('\n')[0]
            elif install_from_local_folder:
                site_packages_path = join(req_path, folder_name)
                if isdir(site_packages_path):
                    shutil.rmtree(site_packages_path)
                shutil.copytree(join(install_from_local_folder, repo_name, folder_name), site_packages_path)
                req_path = join(install_from_local_folder, repo_name)

            print("--------------------------------------------------------------------\n"
                  "update dependencies:\n"
                  "--------------------------------------------------------------------")
            requirements_path = join(req_path, folder_name, 'requirements.txt')
            p = popen(f'pip{python_ver} install -r "{requirements_path}"')
            rsp = p.read()
            print(rsp)
            req_status.append('ERROR' not in rsp)
        else:
            pkg_versions.append('')
            req_status.append(False)

        if no_wiliot_dep:
            break

    print('done installation')
    print("************************************************************************\n"
          "********************            Summary            *********************\n"
          "************************************************************************")
    for i, repo_name in enumerate(wiliot_repo.value):
        package_name = repo_name.replace('py', '')
        is_installed = f'installed [{pkg_versions[i]}]' if pkg_versions[i] else 'NOT installed'
        sum_str = f'{package_name} was {is_installed}'
        if is_installed:
            req_is_installed = 'installed' if req_status[i] else 'NOT installed'
            sum_str += f'and the dependencies were {req_is_installed}'
        print(sum_str)
        if no_wiliot_dep:
            break


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Update Wiliot Internal Packages')
    parser.add_argument('-p', '--package_name', help='The package name. valid option(wiliot-api, wiliot-core, '
                                                     'wiliot-tools, wiliot-testers, wiliot-deployment-tools')
    parser.add_argument('-b', '--branch_name', help='The branch name you want to use. the default is master',
                        default='master')
    parser.add_argument('-w', '--overwrite', help='If specified, all wiliot existed packages will be overwrite '
                                                  'with the new installation', default=False, action='store_true')
    parser.add_argument('-n', '--no_wiliot_dep', help='If specified, install the main package without wiliot '
                                                      'dependencies packages', default=False, action='store_true')
    parser.add_argument('-u', '--username', help='If specified, install based username and password and not SHH key',
                        default=None)
    parser.add_argument('-pass', '--password', help='If specified, install based username and password and not SHH key',
                        default=None)
    parser.add_argument('-l', '--local_folder', help='If specified, install packages from the specified local folder')
    parser.add_argument('-g', '--git_folder', help='FOR DEVELOPERS. If specified, install packages from the specified'
                                                   'folder, which assumed to be your git workspace')
    parser.add_argument('-b-for-dep', '--branch_for_dependencies',
                        help='if specified, all wiliot package dependencies will be installed for this branch '
                             '(default master)', default='master')
    args = parser.parse_args()
    package_name = args.package_name
    branch_name = args.branch_name
    is_overwrite = args.overwrite
    is_no_wiliot_dep = args.no_wiliot_dep
    username = args.username
    password = args.password
    local_folder = args.local_folder
    git_folder = args.git_folder
    branch_for_dep = args.branch_for_dependencies
    err_msg = 'please add package name, e.g. update_wiliot_packages.py -p wiliot-api.\n' \
              'The valid packages names are: wiliot-api, wiliot-core, wiliot-tools, wiliot-testers, ' \
              'wiliot-deployment-tools'
    if package_name != None:
        try:
            repo_name = None
            for package in WiliotPackages.__members__.values():
                if package_name in package.value[0]:
                    repo_name = package
                    break
            if repo_name is None:
                print(err_msg)
            else:
                update_internal_wiliot_packages(wiliot_repo=repo_name, branch_name=branch_name,
                                                overwrite=is_overwrite, no_wiliot_dep=is_no_wiliot_dep,
                                                username_bitbucket=username, password_bitbucket=password,
                                                install_from_local_folder=local_folder,
                                                install_from_git_folder=git_folder,
                                                branch_name_for_dep=branch_for_dep)
        except Exception as e:
            print('Error during update packages  [ERROR: {}]'.format(e))

    else:
        print('package must be specified')
