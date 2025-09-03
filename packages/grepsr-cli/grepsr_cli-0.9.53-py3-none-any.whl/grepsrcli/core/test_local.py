from os import path, system, makedirs
import re
import json
import subprocess
from typing import Any, Dict
from .message_log import Log
from .config import load_config, config_path as CONFIG_PATH
from .utils import (
    get_docker_entrypoints,
    load_json,
    write_text,
    read_text,
    remove_docker_container,
    get_file_from_docker,
    copy_contents_to_docker,
    get_docker_working_dir,
    cmd_shell_exec,
)

class TestLocal:
    def __init__(self, type, base_path, plugin_name, params=None, params_file=None, is_multi_proc=False):
        self.type = type
        self.plugin_name = plugin_name
        self.base_path = base_path

        self.tmp_path = path.expanduser('~') + '/.grepsr/tmp/'
        self.config = load_config('config.yml')
        self.type_config = self.config[type]
        self.params = params
        self.params_file = params_file
        self.is_multi_proc = is_multi_proc

        self.supp_file_dir = path.join((self.tmp_path.rstrip('/')), '_supporting_files')
        try:
            makedirs(self.supp_file_dir, exist_ok=True)
        except:
            pass

    def test_script(self):
        if self.type == "php":
            if "env" in self.type_config:
                if self.type_config['env']:
                    self.test_script_php(env=True)
                else:
                    self.test_script_php(env=False)
            else:
                self.test_script_php(env=False)
        elif self.type == "php_next":
            self.test_script_php_next()
        elif self.type == 'node':
            self.test_script_node()

    def test_script_php(self, env=False):
        if self.is_multi_proc is None:
            # only use the value of multiprocess if it is not passed explicitly from cmd line
            try:
                self.is_multi_proc = 1 if self.type_config['multiprocess'] == True else 0
            except KeyError:
                pass
        env_vars = []
        if env:
            env_vars = [
                f'-e {env_var}={self.type_config["env"][env_var]}' for env_var in self.type_config["env"].keys()
            ]
        sdk_args_list = [
            f'-s {self.plugin_name}',
        ]
        if self.is_multi_proc is not None:
            sdk_args_list.append(f'-m {self.is_multi_proc}')
        docker_image_name = self.type_config["sdk_image"]
        json_content = self.params
        pre_entrypoint = self.type_config.get('pre_entry_run_file')
        only_service = (not self.params) and (not self.params_file) and (not pre_entrypoint)
        bash_cmd = ''
        if only_service:
            sdk_args = ' '.join(sdk_args_list)
        else:
            if self.params_file:
                # should be able to pass any path, not limited to just tmp/
                fp = path.expandvars(path.expanduser((self.params_file)))
                if not path.isabs(fp):
                    fp = path.join(self.tmp_path, fp)
                with open(fp, 'r', encoding='UTF-8') as fd:
                    json_content = fd.read()

            pipe_params = ''
            sh_contents = ['#!/bin/bash']
            if json_content:
                sdk_args_list.append("-p")

                # json decode and encode is required to remove spaces from the passed params
                # because the bash shell file that forwards argument is not quoted ($@)
                # which causes it to treat spaces anywhere as being a different argv
                params_decoded = json.loads(json_content)
                compact_json = json.dumps({'params': params_decoded}, separators=(',', ':'))
                # now that all non important spaces are removed, replace spaces
                # inside (keys and) values with unicode code-point which is luckily accepted by shell.
                # hack: if the shell cannot handle space char, sneak the space with a makeup.
                compact_json = compact_json.replace(' ', '\\u0020')
                
                tmp_json_file = '_gcli_internal_params_tmp.json'
                # write the compacted json, to tmp/ directory whcih will get mounted 
                # to docker container. Params are written to temporary file and not passed
                # in the shell due to quoting issues.
                write_text(path.join(self.tmp_path, tmp_json_file), compact_json)
                pipe_params = f"$(</tmp/{tmp_json_file})"
                
            
            custom_shell_file = '_gcli_internal_shell_file.sh'
            custom_shell_file_local = path.join(self.tmp_path, custom_shell_file)
            
            if pre_entrypoint:
                sh_contents.append(read_text(path.join(self.tmp_path, pre_entrypoint)))
                
            sdk_args = ' '.join(sdk_args_list)
            original_entrypoints = get_docker_entrypoints(image_name=docker_image_name)
            sh_contents.append(f'source {original_entrypoints[0]} {sdk_args} {pipe_params}')
            write_text(custom_shell_file_local, '\n'.join(sh_contents))

            bash_cmd = f'source /tmp/{custom_shell_file}'

        repo_basename = 'vortex-plugins-services'
        if self.type_config.get('rename_repo') == False:
            repo_basename = path.basename(self.base_path)

        commands = [
                'docker run -t --network="host" --rm',
                f'-v {self.base_path}:/home/grepsr/vortex-plugins/{repo_basename}',
                f'-v {self.tmp_path}:/tmp',
                f'-e APP_ENV={self.config["app_env"]}',
                " ".join(env_vars),
                f'--entrypoint=""' if not only_service else '',
                docker_image_name,
                f'bash -ci "{bash_cmd}"' if not only_service else sdk_args,
        ]

        command = ' '.join([command for command in commands if command])
        # print(command, flush=True)
        system(command)

    def test_script_php_next(self):
        command = f'''docker run -t -i --network="host" --rm \
                     -v {self.base_path}:/home/grepsr/vortex-backend-next/scraper-plugins \
                     -v {self.tmp_path}:/tmp \
                     -e APP_ENV={self.config['app_env']} \
                     {self.type_config['sdk_image']} -s {self.plugin_name} '''
        system(command)

    def test_script_node(self):
        docker_image_name = self.type_config["sdk_image"]
        original_entrypoint = get_docker_entrypoints(image_name=docker_image_name)[0]
        plugin_dir = path.join(self.base_path, self.plugin_name)
        pkg_path = path.join(plugin_dir, 'package.json')
        pkg: Dict[str, Any] = load_json(read_text(pkg_path))
        
        # find out if all dependencies are installed or not.
        proc_ls = cmd_shell_exec('npm ls', working_dir=plugin_dir)
        if proc_ls.returncode != 0:
            print('[gcli] INSTALLING PACKAGES...', flush=True)
            if self.node_pkg_install() != 0:
                print('[gcli] package installed failed. Exiting..')
                return 

        # if pkg.get('crawler_type') == 'typescript':
        #     print('[gcli] RUNNING TSC...', flush=True)
        #     proc = cmd_shell_exec('tsc', working_dir=plugin_dir)
        #     if proc.returncode != 0:
        #         return print(proc.stdout, proc.stderr, flush=True)
            
        print('[gcli] RUNNING CRAWLER...', flush=True)
        return self.run_command_in_docker(docker_image_name, f'cd /home/grepsr/crawler/ && cd {self.plugin_name}/ && npm start',)

    def node_pkg_install(self, package_name: str = '', install_extra_args = None):
        image_name = self.type_config["sdk_image"]
        entrypoint_path = get_docker_entrypoints(image_name=image_name)[0]
        cont_working_dir = get_docker_working_dir(image_name)
        entrypoint_path_abs = path.abspath(path.join(cont_working_dir, entrypoint_path))

        entry_file_contents, entry_file_original_perms = get_file_from_docker(image_name, container_src_path=entrypoint_path_abs)
        
        new_entry_file_contents = entry_file_contents
        new_entry_file_contents = re.sub(r'\n\s*npm install.*', '', new_entry_file_contents)
        new_entry_file_contents = re.sub(r'\n\s*npm start.*', '', new_entry_file_contents)
        new_entry_file_contents = new_entry_file_contents + '\n' + f'npm install --save-exact {package_name} ' + " ".join(install_extra_args or [])

        proc = self.run_command_in_docker(image_name, entrypoint_path_abs, True)
        container_id_to_run = proc.stdout.rstrip()
        copy_contents_to_docker(container_id_to_run, entrypoint_path_abs, new_entry_file_contents, entry_file_original_perms)
        
        returncode = system(f'docker start -a {container_id_to_run}')
        remove_docker_container(container_id_to_run)
        return returncode

    def run_command_in_docker(self, docker_image_name: str, entrypoint_path: str, create_only = False):
        env_vars = []
        if self.type_config.get('env'):
            env_vars = [
                f'-e {env_var}={self.type_config["env"][env_var]}' for env_var in self.type_config["env"].keys()
            ]

        aws_key = self.config.get('aws_access_key_id', '')
        aws_secret = self.config.get('aws_secret_access_key', '')
        if aws_key and aws_secret:
            env_vars.append(f'-e AWS_ACCESS_KEY_ID={aws_key}')
            env_vars.append(f'-e AWS_SECRET_ACCESS_KEY={aws_secret}')

        bash_cmds = [
            r'trap "echo Received SIGTERM; kill -SIGTERM \$child" SIGTERM;',
            r'trap "echo Received SIGINT; kill -SIGINT \$child" SIGINT;',
            f'{entrypoint_path} &',
            'child=$!;',
            'wait $child'
        ]
        bash_cmd = '\n'.join(bash_cmds)
        commands = [
            'docker create' if create_only else 'docker run',
            '--rm --init -t --network="host"',
            f'-v {self.base_path}:/home/grepsr/crawler/',
            f'-v {self.tmp_path}:/tmp/',
            f'-v {self.supp_file_dir}:/home/grepsr/data/',
            " ".join(env_vars),
            f'-e APP_ENV={self.config["app_env"]}',
            f'-e SERVICE_NAME={self.plugin_name}',
            '--entrypoint=""',
            docker_image_name,
            f"bash -c '{bash_cmd}'",
        ]

        command = ' '.join([command for command in commands if command])
        # print(command, flush=True)
        if create_only:
            # need to return container id
            return cmd_shell_exec(command)
        else:
            return system(command)