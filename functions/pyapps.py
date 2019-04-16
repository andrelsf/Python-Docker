import docker 
from pyconfigloader import ConfigLoader
from time import sleep
from os import sys, path, getcwd, remove
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
                self.__backend = app['backend']
                if (self.__backend):
                    self.__list_apps.append(app)
            for app in self.__apps_list:
                self.__name             = app['name']
                self.__base_image       = app['base_image']
                self.__network          = app['network']
                self.__ip               = app['ip']
                self.__aliases          = app['aliases']
                self.__image            = app['image']
                self.__ports            = app['ports']
                self.__port_bindings    = loads(app['port_bindings'])
                self.__dockerfile_path  = self.__py_docker_dir + app['dockerfile_path']
                self.__dockerfile       = app['dockerfile']
                self.__tag              = app['tag']
                self.__template         = app['template']
                self.__template_file    = app['template_file']
                self.__backend          = app['backend']

                """
                    Create template.
                """
                try:
                    if (self.__template):
                        if (self.__create_dockerfile(
                                    self.__name,
                                    self.__template_file,
                                    self.__base_image,
                                    self.__py_docker_templates_dir, 
                                    self.__dockerfile_path
                                )):
                            print("\t[ OK ] Dockerfile created.")
                        if (not self.__backend):
                            self.__create_haproxy_cfg(
                                self.__name,
                                self.__ip,
                                self.__network,
                                self.__py_docker_templates_dir,
                                self.__dockerfile_path
                            )
                            print("\t[ OK ] HAProxy file created.")
                except TypeError as err:
                    print("\t[ Apps __init__ ] ERROR:", err)
            
                """
                    Function to create imagens Docker.
                """
                self.__create_images_docker(
                    app_name=self.__name,
                    dockerfile_path=self.__dockerfile_path,
                    dockerfile=self.__dockerfile,
                    tag=self.__tag,
                    base_image=self.__base_image
                )

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

    def __create_images_docker(self, app_name, dockerfile_path, dockerfile, tag, base_image):
        print("\n[DOCKER] Create image APP: ({}) ...".format(app_name.upper()))
        try:
            print("\tCreating of image {}: Started...".format(app_name.upper()))
            app_tag = self.__docker_client.api.images(name=tag)
            if not app_tag:
                build_app_name = [ line.decode('utf-8').split("\n")[0] for line in self.__docker_client.api.build(
                    path=dockerfile_path,
                    tag=tag,
                    dockerfile=dockerfile,
                    nocache=False
                    )]
                for result in build_app_name:
                    res = loads(result)
                    if res.get('stream'):
                        pass
                        print("\t", res.get('stream'), end="")
                    elif (res.get('errorDetail')):
                        print("\t", res.get('errorDetail').get('message'), end="")
                        result = self.__docker_client.api.remove_image(
                                image=base_image, 
                                force=True, 
                                noprune=False
                            )
                        print("\n\tRemoved image [" + result[1].get('Untagged') + "].")
                        sys.exit(1)
                print("\t[ OK ] Image created successfully.")
            else:
                print("\t[ OK ] Image {} exists.".format(app_name.upper()))
        except docker.errors.BuildError as err:
            print("[ Apps __create_images_docker ] : ", err)
            sys.exit(1)
        except docker.errors.APIError as err:
            print("[ Apps __create_images_docker ] : ", err)
            sys.exit(1)


    def __is_running(self, app_name):
        is_running = self.__docker_client.api.containers(
                filters={'name': app_name, 'status': 'running'}
            )
        if is_running:
            return True
        else:
            return False


    def __docker_run(self, app_name, network, ip, aliases, image, ports, port_bindings):
        print("\n[DOCKER] Run images APP: (", app_name.upper(), ")...")
        try:
            print("\tDocker RUN", app_name.upper(), ": Started...")
            is_running = self.__is_running(app_name)
            if (not is_running):
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
                sleep(5)
                is_running = self.__is_running(app_name)
                if (not is_running):
                    print("\t[ ERROR ] App terminated abruptly")
                    sys.exit(1)
                print("\t[ OK ] APP Started.")
            else:
                print("\t[ Warnning ] APP is Running.")
        except docker.errors.ContainerError as err:
            print("\t[ Apps __docker_run ] : ", err)
            sys.exit(1)
        except docker.errors.ImageNotFound as err:
            print("\t[ Apps __docker_run ] : ", err)
            sys.exit(1)
        except docker.errors.ImageLoadError as err:
            print("\t[ Apps __docker_run ] : ", err)
            sys.exit(1)
        except docker.errors.APIError as err:
            print("\t[ Apps __docker_run ] : ", err)
            sys.exit(1)

    """
        self.__py_docker_templates_dir, 
        self.__dockerfile_path
    """
    def __create_dockerfile(self, app_name, template_file, base_image, template_dir, dockerfile_path):
        print("[ Dockerfile ] Create Dockerfile ", app_name)
        dockerfile_template = template_dir + template_file
        # for app in self.__list_apps:
        dockerfile_file = dockerfile_path + "Dockerfile"
        if (path.exists(dockerfile_template)):
            with open(dockerfile_template, 'r') as obj_vhost:
                dockerfile_content = obj_vhost.readlines()
            content = ''
            for line in dockerfile_content:
                content = content + line.strip("")
            if (content):
                template = Template(content)
                content = template.render(base_image=base_image, app_name=app_name)
                with open(dockerfile_file, 'w') as obj_vhost:
                    obj_vhost.write(content)
                return True


    def __create_haproxy_cfg(self, app_name, ip_address, network_name, template_dir, haproxy_path):
        haproxy_template = template_dir + "haproxy.cfg"
        backends_template = template_dir + "backends"
        haproxy_file = haproxy_path + "haproxy.cfg"
        if (path.exists(haproxy_template)):
            with open(haproxy_template, 'r') as template:
                haproxy_content = template.readlines()
            with open(backends_template, 'r') as obj_backends:
                content_backends = obj_backends.readlines()
            content = '\n'
            for line in haproxy_content:
                content = content + line.strip("")
            if (content):
                template = Template(content)
                content = template.render(APP=network_name, IP=ip_address)
                with open(haproxy_file, "w") as obj_haproxy:
                    obj_haproxy.write(content)
                content = '\n'
                for line in content_backends:
                    content = content + line.strip("")
                template = Template(content)
                for app in self.__list_apps:
                    content = template.render(app=app['name'], ip_app=app['ip'])
                    with open(haproxy_file, 'a') as obj_haproxy:
                        obj_haproxy.write(content)


app = Apps()