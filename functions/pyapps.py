import docker 
from pyconfigloader import ConfigLoader
from os import sys, path, getcwd
from jinja2 import Template
from json import loads, dump

class Apps():

    def __init__(self):
        self.__docker_client = docker.from_env()
        self.__list_apps = list()
        self.__config_loader = ConfigLoader()
        self.__datas_default = self.__config_loader.get_datas_default()
        self.__apps_list = self.__config_loader.get_datas_apps()
        try:
            self.__py_docker_dir = getcwd()
            self.__domain = self.__datas_default['domain']
            self.__py_docker_configs = self.__py_docker_dir + self.__datas_default['py_docker_configs']
            self.__py_docker_functions = self.__py_docker_dir + self.__datas_default['py_docker_functions']
            self.__py_docker_templates_dir = self.__py_docker_dir + self.__datas_default['py_docker_templates']
            for app in self.__apps_list:
                self.__name = app['name']
                if (self.__name != "proxy_nginx"):
                    self.__list_apps.append(self.__name)
            for app in self.__apps_list:
                self.__name             = app['name']
                self.__network          = app['network']
                self.__ip               = app['ip']
                self.__aliases          = app['aliases']
                self.__image            = app['image']
                self.__ports            = app['ports']
                self.__port_bindings    = app['port_bindings']
                self.__dockerfile_path  = self.__py_docker_dir + app['dockerfile_path']
                self.__dockerfile       = app['dockerfile']
                self.__tag              = app['tag']
                
                """
                    Create template to vhosts.
                """
                try:
                    if (app['template']):
                        if (self.__template_create_vhost(
                                self.__py_docker_templates_dir, 
                                self.__dockerfile_path
                            )):
                            print("\t[ OK ] VHost created.")
                except TypeError as err:
                    print("\t[ Apps __init__ ] ERROR:", err)

                """
                    Function to create imagens Docker.
                """
                self.__create_images_docker(
                    app_name=self.__name,
                    dockerfile_path=self.__dockerfile_path,
                    dockerfile=self.__dockerfile,
                    tag=self.__tag
                )
                sys.exit()
                """
                    Docker RUN.
                """
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
            sys.exit(1)
        except ValueError as err:
            print("[ Apps __init__ ] ERROR :", err)
            sys.exit(1)

    def __create_images_docker(self, app_name, dockerfile_path, dockerfile, tag):
        print("\n[DOCKER] Create image APP: ({}) ...".format(app_name.upper()))
        try:
            print("\tCreating of image {}: Started...".format(app_name.upper()))
            app_tag = self.__docker_client.api.images(name=tag)
            if not app_tag:
                app_name = [ line.decode('utf-8').split("\n")[0] for line in self.__docker_client.api.build(
                    path=dockerfile_path,
                    tag=tag,
                    dockerfile=dockerfile,
                    nocache=False
                    )]
                for result in app_name:
                    res = loads(result)
                    if res.get('stream') != None:
                        print("\t", res.get('stream'), end="")
                print("\t[ OK ] Image created successfully.")
            else:
                print("\t[ OK ] Image {} exists.".format(app_name.upper()))
        except docker.errors.BuildError as err:
            print("[ Apps __create_images_docker ] : ERROR :", err)
            sys.exit(1)
        except docker.errors.APIError as err:
            print("[ Apps __create_images_docker ] : ERROR :", err)
            sys.exit(1)


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

    """
        self.__py_docker_templates_dir, 
        self.__dockerfile_path
    """
    def __template_create_vhost(self, template_dir, dockerfile_path):
        vhost_template = self.__py_docker_templates_dir + 'vhost'
        for app in self.__list_apps:
            vhost_file = dockerfile_path + "vhost_" + app
            if (path.exists(vhost_template)):
                with open(vhost_template, 'r') as obj_vhost:
                    vhost_content = obj_vhost.readlines()
                content = ''
                for line in vhost_content:
                    content = content + line.strip("")
                if (content):
                    template = Template(content)
                    content = template.render(vhost_name=app + self.__domain)
                    with open(vhost_file, 'w') as obj_vhost:
                        obj_vhost.write(content)

app = Apps()