from yaml import load
from os import path, sys

class ConfigLoader():

    def __init__(self):
        self.__config_path = "/etc/pydocker/configs/configs.yaml"
        self.__datas = self.__load_yaml_file()

    def __load_yaml_file(self):
        if (path.exists(self.__config_path)):
            try:
                with open(self.__config_path, 'r') as obj_file:
                    datas = load(obj_file)
            except FileNotFoundError as err:
                print("[ ConfigLoader __load_yaml_file ] Failed to load file [", self.__config_path, "] : ERROR :", err)
                exit()
            except PermissionError as err:
                print("[ ConfigLoader __load_yaml_file ] Failed to load file [", self.__config_path, "] : ERROR :", err)
                exit()
            else:
                return datas
        else:
            print("[ ConfigLoader __load_yaml_file ] File not found.")


    def __get_datas(self, key_param):
        return self.__datas.get(key_param)

    def get_datas_apps(self):
        docker_apps_datas = self.__get_datas("apps")
        return docker_apps_datas

    def get_datas_network(self):
        docker_datas_network = self.__get_datas("networks")
        return docker_datas_network

    def get_datas_default(self):
        datas_default = self.__get_datas("default")
        return datas_default
