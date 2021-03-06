'''
Copyright (c) 2017 VMware, Inc. All Rights Reserved.
SPDX-License-Identifier: BSD-2-Clause
'''


import json
import os
import shutil

from utils.commands import pushd
import utils.constants as const
'''
Docker metadata related modules
NOTE: these modules work on a temp folder to which the output of docker save
has already been extracted into
'''

# docker manifest file
manifest_file = 'manifest.json'


def clean_temp():
    '''Remove the temp directory'''
    temp_path = os.path.abspath(const.temp_folder)
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)


def get_image_manifest():
    '''Assuming that there is a temp folder with a manifest.json of
    an image inside, get a dict of the manifest.json file'''
    temp_path = os.path.abspath(const.temp_folder)
    with pushd(temp_path):
        with open(manifest_file) as f:
            json_obj = json.loads(f.read())
    return json_obj


def get_image_layers(manifest):
    '''Given the manifest, return the layers'''
    return manifest[0].get('Layers')


def get_image_config_file(manifest):
    '''Given the manifest, return the config file'''
    return manifest[0].get('Config')


def get_image_repotags(manifest):
    '''Given the manifest, return the list of image tag strings'''
    return manifest[0].get('RepoTags')


def get_layer_sha(layer_path):
    '''Docker's layers are file paths starting with the ID.
    Get just the sha'''
    return os.path.dirname(layer_path)


def get_image_config():
    '''Assuming there now exists a working directory where the image
    metadata exists, return the image config'''
    config_file = get_image_config_file(get_image_manifest())
    # assuming that the config file path is in the same root path as the
    # manifest file
    temp_path = os.path.abspath(const.temp_folder)
    with pushd(temp_path):
        with open(config_file) as f:
            json_obj = json.loads(f.read())
    return json_obj


def get_nonempty_history(config):
    '''Given the image config, return only the dockerfile lines that
    created non-empty layers'''
    history = []
    for item in config['history']:
        if 'empty_layer' not in item.keys():
            if 'created_by' in item.keys():
                history.append(item['created_by'])
            else:
                history.append(item['comment'])
    return history


def get_diff_ids(config):
    '''Given the image config, return the filesystem diff ids'''
    diff_ids = []
    for item in config['rootfs']['diff_ids']:
        diff_ids.append(item.split(':').pop())
    return diff_ids
