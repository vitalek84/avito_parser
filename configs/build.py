# -*- coding: utf-8 -*-

import os
import sys
import json


def build():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dest_dir = os.path.join(base_dir, 'build')
    base = get_base_config(base_dir)
    configs = get_configs(base_dir)

    for config in configs:
        for k, v in base.items():
            if k not in config:
                config['source'][k] = v
        
        config_path = os.path.join(dest_dir, config['name'])
        print('Saving {} config'.format(config_path))
        with open(config_path, 'w+') as fd:
            json.dump(config['source'], fd, indent=2)



def get_base_config(base_dir):
    path = os.path.join(base_dir, 'base.json')
    with open(path, 'r') as fd:
        return json.load(fd)


def get_configs(base_dir):
    path = os.path.join(base_dir, "sources")
    configs = []
    for i in os.listdir(path):
        if i.endswith('.json'):
            config_path = os.path.join(path, i)
            with open(config_path, 'r') as fd:
                configs.append({
                    'path': config_path,
                    'name': i,
                    'source': json.load(fd)
                })
    return configs


if __name__ == '__main__':
    build()