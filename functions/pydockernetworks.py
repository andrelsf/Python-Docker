import docker
from os import sys
from pyconfigloader import ConfigLoader

class DockerNetwork():

    def __init__(self):
        self.__docker_client = docker.from_env()
        self.__config_loader = ConfigLoader()
        self.__datas = self.__config_loader.get_datas_network()
        try:
            self.__network_name = self.__datas['name']
            self.__network_subnet = self.__datas['subnet']
            self.__network_gateway = self.__datas['gateway']
            self.__network_driver = self.__datas['driver']
        except TypeError as err:
            print("[ DockerNetwork __init__ ] ERROR:", err)
            sys.exit(1)

    def __create_network_apps(self):
        print("\n[DOCKER] Create Network for APPS: (", self.__network_name.upper(), ") ...")
        try:
            netapps = self.__docker_client.api.networks(names=self.__network_name)
            if not netapps:
                ipam_pool = docker.types.IPAMPool(
                    subnet=self.__network_subnet,
                    gateway=self.__network_gateway
                )
                ipam_config = docker.types.IPAMConfig(
                    pool_configs=[ipam_pool]
                )
                netapps = self.__docker_client.api.create_network(
                    name=self.__network_name,
                    driver=self.__network_driver,
                    ipam=ipam_config
                )
                print("\t[ OK ] Network created!")
            else:
                print("\t[ OK ] Network exists.")
        except docker.errors.APIError as err:
            print("\t[ DockerNetwork __create_network_apps ] ERROR:", err)
            sys.exit(1)