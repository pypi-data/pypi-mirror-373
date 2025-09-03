from os import path
import os
import shutil
import subprocess
import yaml
from .message_log import Log
from .config import load_config
from .aws_s3 import S3
from .utils import get_docker_id

class SDKSetup:
    config = load_config('config.yml')
    home_path = path.expanduser('~')
    config_path = path.expanduser('~/.grepsr/config.yml')

    def __init__(self, type, dryrun, sdk_image):
        self.type_dict = self.config[type]
        self.type_name = type
        self.dryrun = dryrun
        self.sdk_image = sdk_image

        self.do_setup()

    def check_path(self):
        for service_dir in self.type_dict.get('paths') or []:
            service_dir = path.expanduser(service_dir)
            if not path.exists(service_dir):
                Log.error(
                    f'Directory {service_dir} was not found')
                Log.error(
                    "Please check ~/.grepsr/config.yml to check if paths are correctly added")
                return False
        return True

    def generate_autocomplete_directory(self, container_id, dir_name):
        for service_dir in self.type_dict.get('paths') or []:
            service_dir = path.expanduser(service_dir)
            Log.info(
                f"Adding autocomplete modules in {service_dir}. This could take some time...")
            
            autocomplete_dir = path.join(service_dir, '.autocomplete')
            if os.path.exists(autocomplete_dir):
                shutil.rmtree(autocomplete_dir)
            os.makedirs(autocomplete_dir, exist_ok=True)

            command = f"""docker cp -L {container_id}:/home/grepsr/{dir_name}/lib {autocomplete_dir} && docker cp -L {container_id}:/home/grepsr/{dir_name}/vendor {autocomplete_dir}
            """
            os.system(command)

    def do_setup(self):
        if self.sdk_image is not None:
            with open(self.config_path, 'w') as w:
                self.config[self.type_name]['sdk_image'] = self.sdk_image
                w.write(yaml.dump(self.config))

        if not self.check_path():
            return False
        if not self.dryrun:
            Log.info("Logging in to AWS service")

            s3 = S3(self.config['aws_access_key_id'], self.config['aws_secret_access_key'])
            username, auth_token = s3.get_decoded_auth_creds().split(':')
            sdk_image = self.sdk_image or self.type_dict['sdk_image']
            hostname = sdk_image.split('/', 2)[0]
            out = subprocess.run([
                'docker', 'login', '--username', username, '--password-stdin', hostname
            ], input=auth_token, text=True, stdout=subprocess.PIPE)
            Log.info(out.stdout)

            Log.info("Getting the SDK")
            os.system(f"docker pull {sdk_image}")

        container_id = get_docker_id(self.type_dict['sdk_image'])

        if self.type_name == 'php':
            self.generate_autocomplete_directory(
                container_id, 'vortex-backend')
        elif self.type_name == 'php_next':
            self.generate_autocomplete_directory(
                container_id, 'vortex-backend-next')

        os.system(f'docker rm {container_id}')
        Log.info("SDK has been installed successfully")
