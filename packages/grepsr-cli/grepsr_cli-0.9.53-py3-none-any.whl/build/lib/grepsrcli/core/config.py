import yaml
from os import path, remove, system
from pathlib import Path
from .message_log import Log
from jinja2 import Template
import platform


config_path = path.expanduser('~/.grepsr')


def load_config(file_name, file_path=None):
    """Loads yml config file for user configuration

    Args:
        file_name (str): the name of file in the path gcli/config
    """

    if file_path is None:
        file_path = config_path
    try:
        file = f'{file_path}/{file_name}'
        with open(file, 'r') as f:
            file_content = f.read()
            return yaml.full_load(file_content)
    except:
        Log.error("{} not found in Path {}".format(file_name, file_path))
        return {}


def save_config(update=False):

    if update == False:
        setup_config = {}
    else:
        setup_config = load_config('config.yml')

    platforms = ['php', 'node', 'python', 'php_next']
    crawler_paths = []

    for plat in platforms:
        if yes_no_prompt(f"\nProcess configuration for {Log.OKCYAN + plat + Log.ENDC} platform?"):
            if update == False:
                setup_config[plat] = {}
                setup_config[plat]['paths'] = []

                if(plat == 'php'):
                    setup_config[plat]['sdk_image'] = '486559570021.dkr.ecr.eu-central-1.amazonaws.com/vortex/sdk:stable'
                elif(plat == 'php_next'):
                    setup_config[plat]['sdk_image'] = '486559570021.dkr.ecr.eu-central-1.amazonaws.com/vortex/backend-next:latest'
                else:
                    setup_config[plat]['sdk_image'] = ''

            setup_config[plat]['env'] = {}
            Log.heading("\nStep 1: Path Configuration")

            if update == True:
                if yes_no_prompt("Do you want to update crawler paths?") == True:
                    setup_config[plat]['paths'] = []
                    while True:
                        base_path = prompt_for(
                            prompt="Enter path for your plugin directory: ")
                        base_path = path.expanduser(base_path.rstrip('/'))
                        setup_config[plat]['paths'].append(base_path)
                        crawler_paths.append(base_path)
                        if(yes_no_prompt("Do you want to another path?") == False):
                            break
            elif update == False:
                while True:
                    base_path = prompt_for(
                        prompt="Enter path for your plugin directory: ")
                    base_path = path.expanduser(base_path.rstrip('/'))
                    setup_config[plat]['paths'].append(base_path)
                    crawler_paths.append(base_path)
                    if(yes_no_prompt("Do you want to another path?") == False):
                        break
            else:
                pass

            Log.heading("\nStep 2: SDK Configuration")
            if update == True:
                if yes_no_prompt("Do you want to update SDK image ?") == True:
                    if plat == 'php':
                        setup_config[plat]['sdk_image'] = '486559570021.dkr.ecr.eu-central-1.amazonaws.com/vortex/sdk:stable'
                    elif plat == 'php_next':
                        setup_config[plat]['sdk_image'] = '486559570021.dkr.ecr.eu-central-1.amazonaws.com/vortex/backend-next:latest'
                    else:
                        setup_config[plat]['sdk_image'] = ''

                    sdk_image = prompt_for(
                        prompt=f"Enter SDK image for {Log.OKCYAN + plat + Log.ENDC} (defaults to stable sdk if empty): ", empty=True)
                    if sdk_image is not None:
                        setup_config[plat]['sdk_image'] = sdk_image
            elif update == False:
                sdk_image = prompt_for(
                    prompt=f"Enter SDK image for {Log.OKCYAN + plat + Log.ENDC} (defaults to stable sdk if empty): ", empty=True)
                if sdk_image is not None:
                    setup_config[plat]['sdk_image'] = sdk_image
            else:
                pass

            Log.heading("\nStep 3: Environment variable Coniguration")
            if yes_no_prompt("Do you want to add environment variables?") == True:
                while True:
                    env_key_val = prompt_for(
                        f"Enter env variable for {Log.OKCYAN + plat + Log.ENDC} (Eg:- CFG_PARAMS_SELENIUM_HOST: 192.168.90.64) \n")
                    try:
                        env_key_val = env_key_val.split(':')
                        setup_config[plat]['env'][env_key_val[0].strip()
                                                  ] = env_key_val[1].strip()
                    except:
                        Log.error("Please follow the correct format")
                    if yes_no_prompt("Do you want to another env variable?") == False:
                        break

    if update == True:
        if yes_no_prompt("Do you want to update your aws keys?") == True:
            setup_config['aws_access_key_id'] = prompt_for(
                f"Enter aws id \n")
            setup_config['aws_secret_access_key'] = prompt_for(
                f"Enter aws secret key \n")
    else:
        setup_config['aws_access_key_id'] = prompt_for(
            f"Enter aws id \n")
        setup_config['aws_secret_access_key'] = prompt_for(
            f"Enter aws secret key \n")

    setup_config['app_env'] = 'tst'

    with open(config_path + '/config.yml', 'w') as w:
        w.write(yaml.dump(setup_config))

    generate_autocomplete_script(crawler_paths)

def prompt_for(prompt, empty=True):
    while True:
        ans = input(prompt)
        if not empty and ans == '':
            continue
        break
        
    return ans

def yes_no_prompt(ques):
    answer = input(f'{ques} (y/n) ')
    if(answer in ['y', '']):
        return True
    else:
        return False


def generate_autocomplete_script(crawler_paths):
    
    data = {}
    data['paths'] = []
    for p in range(len(crawler_paths)):
        d = {}
        d['ind'] = p
        d['dest_path'] = crawler_paths[p]
        data['paths'].append(d)

    template_dir = Path(__file__).parent.parent.absolute()

    # generate autocomplete file for zsh and bash
    for auto_script in ['autocomplete',  'autocomplete_zsh']:

        if path.exists(config_path + f'/{auto_script}.sh'):
            remove(config_path +
                   f'/{auto_script}.sh')

        template_file = '{}/templates/{}'.format(
            template_dir, f'{auto_script}.jinja2')

        with open(template_file) as file:
            template = Template(file.read())

        with open(config_path + f'/{auto_script}.sh', 'w') as dest_file:
            dest_file.write(template.render(data))
    Log.info(f"Generating Autocomplete Script for {platform.system()}")
    if platform.system() == 'Linux':
        
        with open(path.expanduser('~/.bashrc')) as rc_file:
            rc_file = rc_file.read()
            if ".grepsr/autocomplete.sh" not in rc_file:
                system(
                    '''echo "source $HOME/.grepsr/autocomplete.sh" >>  ~/.bashrc''')
    elif platform.system() == 'Darwin':
        with open(path.expanduser(path.expanduser('~/.zshrc'))) as rc_file:
            rc_file = rc_file.read()
            if ".grepsr/autocomplete_zsh.sh" not in rc_file:
                system(
                    '''echo "source $HOME/.grepsr/autocomplete_zsh.sh" >>  ~/.zshrc''')
