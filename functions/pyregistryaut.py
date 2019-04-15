"""
    TODO study

import os.path

import docker

registry_url = 'registry.example.com'
img_name = 'someuser/some-image'

client = docker.from_env()
img = client.images.get(img_name)
assert img.tag(os.path.join(registry_url, img_name))
client.login(
  username=registry_configs['USERNAME'],
  password=registry_config['PASSWORD'],
  registry=registry_url
)
client.images.push(os.path.join(registry_url, img_name))
"""