import docker 
from pyconfigloader import ConfigLoader
from os import sys, path

class Apps():

    def __init__(self):
        self.__list_apps = list()
        self.__docker_client = docker.from_env()
        self.__config_loader = ConfigLoader()
        self.__datas_default = self.__config_loader.get_datas_default()
        self.__apps_list = self.__config_loader.get_datas_apps()
        try:
            self.__domain = self.__datas_default['domain']
            self.__py_docker_dir = self.__datas_default['py_docker_dir']
            self.__py_docker_configs = self.__datas_default['py_docker_config']
            self.__py_docker_functions = self.__datas_default['py_docker_functions']
            for app in self.__list_apps:
                self.__name = app['name']
                if self.__name != "proxy_nginx":
                    self.__list_apps.append(self.__name)
            for app in self.__apps_list:
                self.__name             = app['name']
                self.__network          = app['network']
                self.__ip               = app['ip']
                self.__aliases          = app['aliases']
                self.__image            = app['image']
                self.__ports            = app['ports']
                self.__port_bindings    = dict(app['port_bindings'])
                self.__dockerfile_path  = app['dockerfile_path']
                self.__dockerfile       = app['dockerfile']
                self.__tag              = app['tag']
                try:
                    if app['template']:
                        self.__template = app['template']
                        if (self.__template_create_vhost(
                                self.__template, 
                                self.__dockerfile_path
                            )):
                            print("\t[ OK ] VHost created.")
                except TypeError as err:
                    print("\t[ Apps __init__ ] ERROR:", err)
                self.__create_images_docker(
                    app_name=self.__name,
                    dockerfile_path=self.__dockerfile_path,
                    dockerfile=self.__dockerfile,
                    tag=self.__tag
                )
                self.__docker_run( 
                    app_name=self.__name,
                    network=self.__network,
                    ip=self.__ip,
                    aliases=self.__aliases,
                    image=self.__image,
                    ports=self.__ports,
                    port_bindings=self.__port_bindings
                )
        except TypeError as err:
            print("[ Apps __init__ ] ERROR :", err)
            exit()


    def __create_images_docker(self, app_name, dockerfile_path, dockerfile, tag):
        print("\n[DOCKER] Create image APP: (", app_name.upper(), ") ...")
        try:
            print("\tCreating of image ", app_name.upper(), ": Started...")
            app_tag = self.__docker_client.api.images(name=tag)
            if not app_tag:
                app_name = [ line for line in self.__docker_client.api.build(
                    path=dockerfile_path,
                    tag=tag,
                    dockerfile=dockerfile,
                    nocache=True
                    )]
                print("\t[ OK ] Image", app_name.upper(), "created successfully.")
            else:
                print("\t[ OK ] Image", app_name.upper(), "exists.")
        except docker.errors.BuildError as err:
            print("[ Apps __create_images_docker ] : ERROR :", err)
            exit()
        except docker.errors.APIError as err:
            print("[ Apps __create_images_docker ] : ERROR :", err)
            exit()


    def __docker_run(self, app_name, network, ip, aliases, image, ports, port_bindings):
        print("\n[DOCKER] Run images APP: (", app_name.upper(), ")...")
        try:
            print("\tDocker run", app_name.upper(), ": Started...")
            is_running = self.__docker_client.api.containers(
                filters={'name': app_name, 'status': 'running'}
            )
            if not is_running:
                network_config = self.__docker_client.api.create_networking_config({
                    network: self.__docker_client.api.create_endpoint_config(
                        ipv4_address=ip,
                        aliases=aliases
                    )
                })
                app_name = self.__docker_client.api.create_container(
                    image=image, name=app_name, networking_config=network_config,
                    ports=ports, host_config=self.__docker_client.api.create_host_config(
                        port_bindings=port_bindings, auto_remove=True
                    )
                )
                print("\tID:", app_name['Id'])
                self.__docker_client.api.start(app_name)
                print("\n\t[ OK ] APP Started.")
        except docker.errors.ContainerError as err:
            print("\t[ Apps __docker_run ] ERROR:", err)
        except docker.errors.ImageNotFound as err:
            print("\t[ Apps __docker_run ] ERROR:", err)
        except docker.errors.ImageLoadError as err:
            print("\t[ Apps __docker_run ] ERROR:", err)


    def __template_create_vhost(self, template, dockerfile_path):
        for app in self.__list_apps:
            dir_vhost = self.__py_docker_configs + "vhost_" + app
            if (path.exists(dir_vhost)):
                with open(dir_vhost, 'w') as content_vhost:
                    content_vhost.write(
                        template % (
                            app, self.__domain, 
                            app, self.__domain
                        )
                    )
            else:
                print("[ Apps __template_create_vhost ] ERROR: File not found.")
                exit()
        return True
        