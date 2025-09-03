try:
    import readline # just importing changes the behavior of input() function
except ImportError:
    pass # no pkg on windows.
import json
import subprocess
import tarfile
import io
import os
import sys
import re
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any, Union
import urllib.parse
import time
from datetime import datetime, timezone
from jinja2 import Template, Environment, FileSystemLoader
from importlib.metadata import version as pkg_version

from .config import load_config
from .message_log import Log

from ..core.constants import (
    PLATFORMS,
    CLASS_DECLARATION_PATTERN,
    COMMENT_BLOCK_PATTERN
)

def get_plugin_path(plugin_name, type='php', all_types=False):
    """ returns the path of the plugin if plugin name exist

    Args:
        plugin_name (str): name of the service plugin .
        type (str, optional): php|py|node. Defaults to 'php'.
        all_types: retuns the path regardless the plugin types i.e php, py and node
    """
    config = load_config('config.yml')
    if all_types == False:
        if type == 'php':
            if _generate_plugin_path(plugin_name, config['php']['paths']):
                return _generate_plugin_path(plugin_name, config['php']['paths'])
            else:
                return False
        elif type == 'node':
            if _generate_plugin_path(plugin_name, config['node']['paths']):
                return _generate_plugin_path(plugin_name, config['node']['paths'])
            else:
                return False
        elif type == 'py':
            if _generate_plugin_path(plugin_name, config['python']['paths']):
                return _generate_plugin_path(plugin_name, config['python']['paths'])
            else:
                return False
        elif type == 'php_next':
            if _generate_plugin_path(plugin_name, config['php_next']['paths']):
                return _generate_plugin_path(plugin_name, config['php_next']['paths'])
            else:
                return False
        elif type == 'node_next':
            if _generate_plugin_path(plugin_name, config['node_next']['paths']):
                return _generate_plugin_path(plugin_name, config['node_next']['paths'])
            else:
                return False
        else:
            Log.error("Invalid params for type.")
            return False
    else:
        # todo: do not hardcode this
        base_paths_list = [
            config['php']['paths'] if 'php' in config else None,
            config['node']['paths'] if 'node' in config else None,
            config['python']['paths'] if 'python' in config else None,
            config['php_next']['paths'] if 'php_next' in config else None,
            config['node_next']['paths'] if 'node_next' in config else None
        ]

        for base_paths in base_paths_list:
            if base_paths is not None and _generate_plugin_path(plugin_name, base_paths):
                return _generate_plugin_path(plugin_name, base_paths)
        Log.error("Plugin name not found.")
        return False

def extract_plugin_properties(plugin_name):
    config = load_config('config.yml')
    plugin_properties = {
        'path': '',
        'type': '',
    }
    
    for platform in PLATFORMS:
        base_paths = config.get(platform, {}).get('paths', [])            
        abs_plugin_path = _generate_plugin_path(plugin_name, base_paths)
        if abs_plugin_path:
            plugin_properties['path'] = abs_plugin_path
            plugin_properties['type'] = platform
            break

    return plugin_properties

def get_extension(code_type='php'):
    if code_type == 'php':
        return 'php'
    elif code_type == 'node':
        return 'js'
    elif code_type == 'py':
        return 'py'
    elif code_type == 'php_next':
        return 'php'
    elif code_type == 'node_next':
        return 'js'
    else:
        Log.error("No extension for this type")
        return ''


def create_boilerplate(folder_path, boilerplate, data, extension, file_name = None):
    """ to create boilerplate for a given path

    Args:
        folder_path (str): the destination path
        boilerplate (str): the name of the boilerplate
        data (dict): the data to be rendered
    """
    if file_name is None:
        file_name = os.path.basename(folder_path)
    try:
        os.mkdir(folder_path)
    except OSError as err:
        Log.error(err)
        return

    dest_path = '{}/{}.{}'.format(folder_path, file_name, extension)

    render_boilerplate(boilerplate=boilerplate, data=data,
                       destination_path=dest_path)

    Log.info('Plugin created at {}'.format(dest_path))


def show_schema(base_path):    
    """ this method will show the schema of a plugin if it has schema.json

    Args:
        base_path (str): the base path of the plugin  eg: /home/vtx-services/aaa_com/
    """

    try:
        from terminaltables import SingleTable

        schema_path = base_path + '/schema.json'
        if os.path.exists(schema_path):
            try:
                with open(schema_path, 'r') as f:
                    schema = f.read()
                    schema = json.loads(schema)
                    for page in schema.keys():
                        Log.standout(f"Schema for Page: {page}")
                        schema_heading = ['field', 'type', 'pattern']
                        table_data = [
                            schema_heading
                        ]

                        for th, td in schema[page]['schema']['properties'].items():
                            if 'pattern' in td:
                                row = [th, td['type'], td['pattern']]
                            else:
                                row = [th, td['type'], '']

                            table_data.append(row)

                        print(SingleTable(table_data).table)
                    return True
            except:
                Log.warn("Schema Structured Incorrectly")
        else:
            Log.warn("Schema Not Found")
            return False
    
    except (ModuleNotFoundError, ImportError):
        return

def ask_user_input_YN(msg, default='Y'):
    while True:
        choice = input(msg + (' [Y/n]: ' if default == 'Y' else ' [y/N]: ')).upper()
        if choice == 'N':
            return 'N'
        elif choice == 'Y':
            return 'Y'
        elif choice == '':
            return default

def ask_user_input(msg, allow_empty=False, raw_input=False, msg_after_first=''):
    user_input = ''
    raw_inputs: List[str] = []
    successful_iter_count = 0
    while True:
        try:
            if successful_iter_count > 0 and msg_after_first:
                msg = msg_after_first
            if raw_input:
                user_input = input(msg).strip()
                if not user_input and allow_empty:
                    break
                raw_inputs.append(user_input)
            else:
                user_input = input(msg).strip()
                if user_input or allow_empty:
                    break
            successful_iter_count += 1
        except EOFError:
            break
    if raw_input:
        user_input = '\n'.join(raw_inputs)
    return user_input

def normalize_plugin_text(text):
    plugin_standard_replacements = {
        r'\W+': '_',
    }
    for pattern, repl in plugin_standard_replacements.items():
        text = re.sub(pattern, repl, text)

    return text

def generate_plugin_name(client_name, site_link, scrape_category = ''):
    client_name_standardized = re.sub(r'^[\s\.]*(.*)[\s\.]*$', '\\1', client_name)
    client_name_standardized = normalize_plugin_text(client_name_standardized)

    only_host = extract_host_from_url(site_link) or ''
    only_host = normalize_plugin_text(only_host)
    
    plugin_name_generated = [client_name_standardized, only_host, scrape_category]
    return '_'.join([e.lower() for e in plugin_name_generated if e])
    
def return_parsed_url(url) -> Optional[urllib.parse.ParseResult]:
    url = url.strip()
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url
    try:
        return urllib.parse.urlparse(url)
    except ValueError:
        return None

def extract_host_from_url(url):
    parsed = return_parsed_url(url)
    if not parsed:
        return None
    hostname = parsed.netloc
    if hostname.startswith('www.'):
        hostname = hostname[4:]
    return hostname

def string_to_list(string) -> List[str]:
    parsed_list: List[str] = []
    if '\n' in string:
        parsed_list = string.split('\n')
    elif ',' in string:
        parsed_list = string.split(',')
    parsed_list = [e.strip() for e in parsed_list]
    return parsed_list

def list_dependencies(plugin_name):
    """list dependencies by listing all base_class"""

    dependencies = set()
    while True:
        plugin_dir_path = get_plugin_path(plugin_name)
        if not plugin_dir_path:
            break
        plugin_path = os.path.join(plugin_dir_path, plugin_name + '.php')
        contents = read_text(plugin_path)
        match = CLASS_DECLARATION_PATTERN.search(contents)
        if not match:
            break
        base_class = match.group(1)
        if base_class.startswith('Vtx_Service_Plugin'):
            break
        plugin_name = base_class
        dependencies.add(plugin_name)
    return list(dependencies)

def insert_all_chained_dependencies(plugin_name):
    """add dependencies if the dependencies follow service_code/service_code.php pattern, however deep"""

    dependencies = list_dependencies(plugin_name)
    plugin_dir_path = get_plugin_path(plugin_name)
    if not plugin_dir_path:
        return
    plugin_path = os.path.join(plugin_dir_path, plugin_name + '.php')
    contents = read_text(plugin_path)
    mappings = get_comment_block(contents)
    if 'Dependencies' not in mappings:
        mappings['Dependencies'] = ''
        original_deps = []
    else:
        original_deps = mappings['Dependencies'].split(',')
    
    mappings['Dependencies'] = ','.join(list(set(dependencies + original_deps)))
    contents = set_comment_block(contents, mappings)
    write_text(plugin_path, contents)
    return True

def set_comment_block(script, mappings):
    comment_block = ' * ' + '\n * '.join([f'{k}: {v}' for k, v in mappings.items()])
    subbed = COMMENT_BLOCK_PATTERN.sub('\\1' + comment_block + '\\3', script, 1)
    return subbed

def get_comment_block(script):
    match = COMMENT_BLOCK_PATTERN.search(script)
    if not match:
        return {}
    doc = match.group(2)
    lines = doc.splitlines()
    mappings = {}
    for line in lines:
        splitted = line.lstrip(' *').split(':', 1)
        if len(splitted) != 2:
            # TOOD: dont skip this,
            continue
        k, v = splitted
        mappings[k.strip()] = v.strip()
    return mappings

def first_found_numbers(text) -> str:
    match = re.search(r'(\d+)', text)
    if not match:
        return ''
    digit = match.group(1)
    return digit

def get_jira_id(text) -> str:
    match = re.search(r'(DEL\-\d+)', text)
    if not match:
        return ''
    identifier = match.group(1)
    return identifier

def list_dependents(plugin_name):
    plugin_dir_path = get_plugin_path(plugin_name)
    if not plugin_dir_path:
        return []
    repo_path = os.path.dirname(plugin_dir_path)
    dependents = []
    for directory in os.listdir(repo_path):
        plugin_path = os.path.join(repo_path, directory)
        if os.path.isfile(plugin_path):
            continue
        if get_plugin_info(plugin_path).get('base_class') == plugin_name:
            dependents.append(directory)
    return dependents

def get_plugin_info(plugin_path):
    """ get plugin's info like service_name,pid,description from the plugin's base folder.
    It does so by reading the file and looking at the info from plugin which is commented
    at the beginning.

    Args:
        plugin_path (str): the path of the directory where we find the plugin.
    """
    plugin_file_path = os.listdir(plugin_path)

    files = [f for f in plugin_file_path]
    plugin_file = ''
    for file in files:
        if os.path.basename(plugin_path) in file:
            plugin_file = file
            break

    if plugin_file:
        file_path = os.path.join(plugin_path, plugin_file)
        try:
            with open(file_path) as fd:
                script = fd.read()
            
            match = []
            if file_path.endswith('.php'):
                match = CLASS_DECLARATION_PATTERN.search(script)
            base_class = None
            if match:
                base_class = match[1]

            # TODO: use tree-sitter to parse php file.
            mappings = {k.upper(): v for k, v in get_comment_block(script).items()}
            if not mappings:
                return {}
            dependencies_str = mappings.get('DEPENDENCIES', '')
            dependencies = [d.strip() for d in dependencies_str.split(',')]
            pid_line = mappings.get('PID', '')
            ssv = pid_line.split(' ')
            pid = ssv[0].strip()

            pid_forced = False
            if len(ssv) > 1:
                pid_forced = ssv[1].strip() == 'force'
            
            # TODO: to parse php import mechanisms like require_once, include_once, etc. for dependencies 
            return {
                'pid': pid,
                'pid_forced': pid_forced,
                'report_name': mappings.get('NAME'),
                'description': mappings.get('DESCRIPTION'),
                'dependencies': dependencies,
                'base_class': base_class
            }
        except KeyError as e:
            pass
    return {}

def render_boilerplate(boilerplate, data, destination_path):
    """parse boilerplate from template directory to start a project

    Args:
        boilerplate (str): name of boilerplate template
        data (dict): input for the boilerplate
        destination_path: the final path where the final content needs to be saved
    """

    template_dir = Path(__file__).parent.parent.absolute()
    template_file = '{}/templates/{}'.format(template_dir, boilerplate)

    if os.path.isdir(template_file):
        os.makedirs(destination_path, exist_ok=True)
        render_templates(template_file, destination_path, data)
    else:
        template_dir, template_filename = os.path.split(template_file)
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_filename)
        with open(destination_path, 'w') as dest_file:
            dest_file.write(template.render(data))

def render_templates(input_dir, output_dir, context):
    template_dir = Path(__file__).parent.parent.absolute()
    template_dir = '{}/templates/'.format(template_dir)

    env = Environment(loader=FileSystemLoader(template_dir))
    jinja_file_ext = '.jinja2'
    dynamic_part = re.compile(r'\[(.*)\]')

    for root, dirs, files in os.walk(input_dir):
        # Create corresponding output directories
        for dir in dirs:
            os.makedirs(os.path.join(output_dir, os.path.relpath(os.path.join(root, dir), input_dir)), exist_ok=True)

        # Process template files
        for file in files:
            
            template_path = os.path.relpath(os.path.join(root, file), input_dir)
            template = env.get_template(os.path.join(os.path.basename(input_dir), template_path))
            rendered_content = template.render(context)

            output_path = os.path.join(output_dir, template_path)
            
            match = dynamic_part.search(output_path)
            if match:
                dynamic_filename = match.group(1)
                output_path = dynamic_part.sub(context.get(dynamic_filename, ''), output_path)

            if output_path.endswith(jinja_file_ext):
                output_path = output_path[:-len(jinja_file_ext)]
                
            with open(output_path, 'w') as f:
                f.write(rendered_content)


def _generate_plugin_path(plugin_name, paths) -> Optional[str]:
    for service_path in paths:
        plugin_path = os.path.join(service_path, plugin_name)
        plugin_path = os.path.expanduser(plugin_path)
        if os.path.exists(plugin_path):
            return plugin_path

def get_docker_id(image_name):
    """ after calling this function be sure to remove the id with `docker rm $container_id` """
    container_id = cmd_shell_exec('docker create ' + image_name).stdout.rstrip()
    return container_id

def remove_docker_container(container_id):
    proc = cmd_shell_exec(f'docker rm {container_id}')
    return proc.returncode == 0

def get_docker_image_config(image_name):
    o = subprocess.run(f'docker inspect {image_name}', shell=True, capture_output=True, text=True)
    return json.loads(o.stdout)

def get_docker_entrypoints(image_name):
    try:
        image_info = get_docker_image_config(image_name)
    except json.JSONDecodeError:
        raise Exception('Running docker inspect failed. Is SDK image correct?')
    try:
        return image_info[0]['Config']['Entrypoint']
    except IndexError:
        raise Exception('Docker inspect failed. Is Docker Running? Is SDK image available?')

def get_docker_working_dir(image_name):
    image_info = get_docker_image_config(image_name)
    return image_info[0]['Config']['WorkingDir']

def run_cmd_inside_docker(cmd, image_name, docker_args):
    proc = cmd_shell_exec(f'docker run {docker_args} --entrypoint="" {image_name} bash -c \'{cmd}\'')
    return proc

def copy_from_docker(container_id, container_src_path, local_dest_path, quiet = True):
    """ specify `-` in destination path to stream file to stdout """
    args = '-L'
    if quiet:
        args += 'q'
    cmd = f'docker cp {args} {container_id}:{container_src_path} {local_dest_path}'
    proc = cmd_shell_exec(cmd)
    return proc

def get_file_from_docker(image_name, container_src_path):
    container_id = get_docker_id(image_name)
    try:
        proc = copy_from_docker(container_id, container_src_path, local_dest_path='-')
    finally:
        remove_docker_container(container_id)

    entry_file_tar_stream = proc.stdout
    return extract_from_tar(entry_file_tar_stream)

def copy_to_docker(container_id, container_dest_path, local_src_path, stdin: Optional[bytes] = None, quiet = True):
    """ specify `-` in local path to stream file from stdin """
    args = '-L'
    if quiet:
        args += 'q'
    cmd = f'docker cp {args} {local_src_path} {container_id}:{container_dest_path}'
    proc = subprocess.run(cmd, shell=True, timeout=100, input=stdin)
    return proc

def copy_contents_to_docker(container_id, container_dest_path, file_contents, file_perms = None):
    file_name = os.path.basename(container_dest_path)
    new_entry_file = make_tar_stream(file_name, file_contents, file_perms)
    
    copy_to_docker(container_id, os.path.dirname(container_dest_path), local_src_path='-', stdin=new_entry_file)

def make_tar_stream(file_name, contents: str, file_mode: Optional[int]) -> bytes:
    file_content = contents.encode('UTF-8')
    tar_buffer = io.BytesIO()
    if file_mode is None:
        file_mode = 777

    with tarfile.open(fileobj=tar_buffer, mode='w') as tar:
        tarinfo = tarfile.TarInfo(name=file_name)
        tarinfo.size = len(file_content)
        tarinfo.mode = file_mode  # Use the original file permissions
        tar.addfile(tarinfo, io.BytesIO(file_content))

    tar_buffer.seek(0)
    return tar_buffer.getvalue()

def extract_from_tar(tar_contents: str) -> Tuple[str, int]:
    tar_stream = io.BytesIO(tar_contents.encode('UTF-8'))
    with tarfile.open(fileobj=tar_stream) as tar:
        member = tar.next()  # Get the first member (since we're dealing with a single file)
        file_content = tar.extractfile(member).read().decode('UTF-8')
        file_perms = member.mode  # Store the original file permissions
        
    return file_content, file_perms

def write_text(file_path, contents):
    "helper function to write text to file with compatible encoding and no newline magic"

    # turn off universal-newline mode for less surprises.
    with open(file_path, 'w', encoding='UTF-8', newline='') as fd:
        fd.write(contents)

def read_text(file_path, return_empty_on_error=False):
    "helper function to read text from file with compatible encoding and no newline magic"

    try:
        # turn off universal-newline mode for less surprises.
        with open(file_path, 'r', encoding='UTF-8', newline='') as fd:
            contents = fd.read()
    except FileNotFoundError as exc:
        if return_empty_on_error:
            return ''
        raise exc

    return contents

def update_version_file(plugin_dir_path, major_flag, minor_flag, crawler_type = 'php'):
    from semver import VersionInfo

    # create .version file or update .version file
    version_path = '{}/.version'.format(plugin_dir_path)
    pkg_path = os.path.join(plugin_dir_path, 'package.json')
    
    if os.path.exists(version_path) or (crawler_type == 'node' and os.path.exists(pkg_path)):
        if (crawler_type == 'node'):
            pkg: Dict[str, Any] = load_json(read_text(pkg_path))
            version_info = VersionInfo.parse(pkg['version'])        
        else:
            version_info = VersionInfo.parse(read_text(version_path))
        if major_flag:
            version_info = version_info.next_version(
                part='major')
        elif minor_flag:
            version_info = version_info.next_version(
                part='minor')
        else:
            version_info = version_info.bump_patch()
        version_info = str(version_info)
    else:
        if major_flag:
            version_info = "1.0.0"
        elif minor_flag:
            version_info = "0.1.0"
        else:
            version_info = "0.0.1"

    if crawler_type != 'node':
        write_text(version_path, version_info)

    return version_info

def return_cmd_with_progress(cmds, toolbar_width):
    try:
        multiplier = toolbar_width // len(cmds)
    except ZeroDivisionError:
        multiplier = 0
    # just echo some dashes after each command for progress. lol.
    echoer = 'echo -n ' + '-' * multiplier
    # .join() only does n-1 additions. Hence add a echoer at last. And then echo remaining to fill the bar (caused by floor division)
    cmd = f' && {echoer} &&'.join(cmds) + f' && {echoer}' + f' && echo -n {"-" * (toolbar_width - (len(cmds) * multiplier))}'
    return cmd

def is_path_tracked_by_git(relative_path, root_repo_dir):
    proc = cmd_shell_exec(f'git ls-files --error-unmatch {relative_path}', root_repo_dir)
    if proc.returncode == 0:
        return True
    return False

def does_plugin_have_modifications(plugin_name, root_repo_dir, crawler_type):
    """check if plugin has any modification in the code
    """
    if not is_path_tracked_by_git(f'{plugin_name}/', root_repo_dir):
        # is untracked file. meaning plugin was just created. it does have modifications.
        return True
    proc = cmd_shell_exec(f'git diff -s --exit-code {plugin_name}/{plugin_name}.{get_extension(crawler_type)}', root_repo_dir)
    if proc.returncode == 0:
        return False
    elif proc.returncode == 1:
        return True
    return None

def is_env_noninteractive():
    return os.environ.get('FRONTEND') == 'noninteractive'

def verbosify(cmds: List[str]) -> str:
    return ' && '.join([f'echo {cmd} && {cmd}' for cmd in cmds])

def cmd_shell_exec(cmd, working_dir=None, timeout=100, check=False):
    return subprocess.run(cmd, shell=True, timeout=timeout, cwd=working_dir or None, capture_output=True, text=True, check=check)

def get_current_utc_aware_datetime() -> datetime:
    """Get the current UTC aware datetime."""
    return datetime.now(timezone.utc)

def get_latest_commit_info(root_repo_dir: str):
    try:
        # Run git log command to get the latest commit info
        proc = cmd_shell_exec('git log -1 --pretty=%an,%ae,%ad --date=iso', root_repo_dir)
        # Split the output: author name, author email, date
        author_name, author_email, commit_date_str = proc.stdout.strip().split(',', 2)
        commit_date = None
        try:
            commit_date = datetime.fromisoformat(commit_date_str)
        except ValueError:
            pass
        return {
            'author_name': author_name,
            'author_email': author_email,
            'commit_date': commit_date
        }
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def get_latest_commit_date(root_repo_dir: str) -> Optional[datetime]:
    """Get the latest commit date in the repository."""
    # proc = cmd_shell_exec('git log -1 --format=%cd --date=iso', root_repo_dir)
    # if proc.returncode != 0:
    #     return None
    # commit_date_str = proc.stdout.strip()
    # try:
    #     commit_date = datetime.fromisoformat(commit_date_str)
    #     return commit_date
    # except ValueError:
    #     return None

def get_current_branch_name(root_repo_dir: str) -> str:
    git_cmds = [
        'git branch --show-current',
        'git rev-parse --abbrev-ref HEAD',
        'git symbolic-ref --short HEAD',
    ]
    
    branch_name = ''
    for git_cmd in git_cmds:
        proc = cmd_shell_exec(git_cmd, root_repo_dir)
        if proc.returncode == 0:
            branch_name = proc.stdout.strip()
            break
    
    return branch_name

def should_pull_again(proc):
    if proc.returncode == 1 and re.search(r'\[rejected\]', proc.stdout) and re.search(r'failed\s+to\s+push\s+some\s+refs.+git pull', proc.stderr):
        return True
    return False

def load_json(json_str: str) -> Union[Dict[Any, Any], List[Any]]:
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {}
    
def can_rebase(proc):
    if proc.returncode == 128 and re.search(r'Cannot fast\-forward to multiple branches|Not possible to fast\-forward', proc.stderr):
        return True
    return False

def pip_update_package(package_name, ask_force_update=False, force_update=False, use_test_pypi=False):
    previous_version = get_this_version()

    if use_test_pypi:
        print('Using test.pypi.org for update\n')
        
    prefix_cmd = f'{sys.executable} -m'
    extra_args = '' if not use_test_pypi else '--index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple'
    proc = cmd_shell_exec(f'{prefix_cmd} pip install {package_name} --upgrade {extra_args}')
    if proc.returncode != 0:
        if (ask_force_update or force_update) and '--break-system-packages' in proc.stderr:
            if force_update or ask_user_input_YN(f'{package_name} update unsuccessful. Do you want to force update using `--break-system-packages`?') == 'Y':
                proc = cmd_shell_exec(f'{prefix_cmd} pip install {package_name} --break-system-packages --upgrade {extra_args}')
    
    current_version = get_this_version()
    if proc.returncode == 0:
        stdout = proc.stdout
        if f'Successfully installed {package_name}' in stdout:
            print(f'{package_name} updated successfully from {previous_version} to {current_version}', flush=True)
        else:
            print(f'{package_name} is already at the latest version {current_version}', flush=True)
    else:
        print(f'{package_name} update failed. Still at version {current_version}')
        return False
    
    return True

def is_package_installed_locally(package_name: str):
    prefix_cmd = f'{sys.executable} -m'
    proc = cmd_shell_exec(f'{prefix_cmd} pip list --format=json')
    modules = load_json(proc.stdout.strip()) or []
    for module in modules:
        if module.get('name') == package_name:
            if module.get('editable_project_location'):
                return True
            
    return False

def is_pkg_beta(package_name: str):
    """ 
        AFAIK there is no way to know if the package was installed from normal pypi or test pypi.
        So, to check if a package was installed using test pypi, we compare the current locally installed version with
        the latest stable normal pypi version.
        (Assuming that the test-pypi has more recent version than the normal pypi version.)
    """
    from semver import VersionInfo

    proc = cmd_shell_exec(f'pip index versions {package_name}')
    output = proc.stdout

    installed_pattern = r'INSTALLED:\s*([\d\.]+)'
    latest_pattern = r'LATEST:\s*([\d\.]+)'

    installed_match = re.search(installed_pattern, output)
    latest_match = re.search(latest_pattern, output)

    if installed_match and latest_match:
        installed_version_str = installed_match.group(1)
        latest_version_str = latest_match.group(1)

        try:
            installed_version = VersionInfo.parse(installed_version_str)
            latest_version = VersionInfo.parse(latest_version_str)
            # print(installed_version, latest_version)
            if installed_version > latest_version:
                return True
            else:
                return False
        except ValueError:
            pass
    
    return None

PACKAGE_NAME = 'grepsr-cli'

def is_this_package_installed_locally():
    return is_package_installed_locally(PACKAGE_NAME)

def is_this_package_beta():
    return is_pkg_beta(PACKAGE_NAME)

def pip_update_this_package(ask_force_update=False, force_update=False, use_test_pypi=False):
    pip_update_package(PACKAGE_NAME, ask_force_update=ask_force_update, force_update=force_update, use_test_pypi=use_test_pypi)

def try_updating_itself():
    if is_this_package_installed_locally():
        # dont
        return
    
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    time_file = os.path.join(curr_dir, 'time.log')
    
    curr_timestamp = int(time.time())
    file_contents = read_text(time_file, return_empty_on_error=True).strip()
    stored_timestamp = int(file_contents or curr_timestamp)

    is_in_beta_version = bool(is_this_package_beta())
    check_update_duration_secs = 3_600 if is_in_beta_version else 86_400

    if (not file_contents) or curr_timestamp - stored_timestamp > check_update_duration_secs:
        print('\nTrying to update gcli...')
        pip_update_this_package(force_update=True, use_test_pypi=is_in_beta_version)
        write_text(time_file, str(curr_timestamp))

def get_this_version():
    module_name = PACKAGE_NAME
    try:
        return pkg_version(module_name)
        
    except Exception as e:
        return ''

# print(is_pkg_beta('grepsr-cli'))