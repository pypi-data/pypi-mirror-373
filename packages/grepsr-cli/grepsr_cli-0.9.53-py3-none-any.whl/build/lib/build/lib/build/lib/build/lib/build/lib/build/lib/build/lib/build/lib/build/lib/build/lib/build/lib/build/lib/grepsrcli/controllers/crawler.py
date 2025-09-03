from os import system, path
import sys
import subprocess
import json
import pathlib
from typing import List, Dict, Any
from cement import Controller, ex
from ..core.config import load_config
from ..core.utils import (
    create_boilerplate,
    is_this_package_installed_locally,
    list_dependents,
    render_boilerplate,
    get_plugin_info,
    get_plugin_path,
    show_schema,
    insert_all_chained_dependencies,
    does_plugin_have_modifications,
    read_text,
    return_cmd_with_progress,
    update_version_file,
    verbosify,
    write_text,
    ask_user_input_YN,
    ask_user_input,
    return_parsed_url,
    insert_all_chained_dependencies,
    generate_plugin_name,
    string_to_list,
    first_found_numbers,
    get_current_branch_name,
    get_latest_commit_info,
    get_current_utc_aware_datetime,
    normalize_plugin_text,
    load_json,
    extract_plugin_properties,
    get_extension,
    try_updating_itself,
    is_env_noninteractive,
    get_jira_id,
    cmd_shell_exec,
    should_pull_again,
    can_rebase,
)
from ..core.constants import (
    PLATFORMS,
    LanguageType,
    NODE_LANGUAGE_TYPES
)
from ..core.test_local import TestLocal
from ..core.message_log import Log
from ..core.aws_s3 import S3

class CrawlerBase(Controller):
    class Meta:
        label = 'crawler_base'


class Crawler(Controller):
    config = load_config('config.yml')

    class Meta:
        label = 'crawler'
        stacked_on = 'crawler_base'
        stacked_type = 'nested'

    @ex(
        help="test a plugin locally",
        aliases=['tst'],
        arguments=[
            (['-s', '--service'], {
                'action': 'store',
                'dest': 'plugin_name',
                'required': True,
                'help': "The name of the service/plugin to run locally"
            }),
            (['-p', '--params'], {
                'action': 'store',
                'dest': 'params',
                'help': 'Parameters (as JSON) to pass to the arguments of the main function',
            }),
            (['-m', '--multiprocess'], {
                'action': 'store',
                'dest': 'multi_proc_mode',
                'help': 'Multiprocess mode',
            }),
            (['--params-file'], {
                'action': 'store',
                'dest': 'params_file',
                'help': 'JSON file location containing parameters to pass to the arguments of the main function'
            }),
            (['-t', '--type'], {
                'action': 'store',
                'required': False,
                'dest': 'crawler_type',
                'help': "the crawler type",
                'choices': PLATFORMS,
            }),
        ]
    )
    def test(self):
        plugin_name = self.app.pargs.plugin_name
        main_fn_params = self.app.pargs.params
        main_fn_params_file = self.app.pargs.params_file
        is_multi_proc = self.app.pargs.multi_proc_mode
        crawler_type = self.app.pargs.crawler_type

        platforms = PLATFORMS
        if crawler_type:
            platforms = [p for p in platforms if p == crawler_type]

        for platform in platforms:
            if platform in self.config:
                plugin_path = get_plugin_path(plugin_name, type=platform)
                if plugin_path:
                    base_path = pathlib.Path(plugin_path).parent
                    try:
                        test = TestLocal(type=platform, base_path=base_path, plugin_name=plugin_name, params=main_fn_params, params_file=main_fn_params_file, is_multi_proc=is_multi_proc)
                        test.test_script()
                    except json.JSONDecodeError as e:
                        self.app.log.error(f"Error decoding params as JSON. {e}")
                        self.app.exit_code = 10
                    except FileNotFoundError as e:
                        self.app.log.error(f"Params file: `{main_fn_params_file}` not found. {e}")
                        self.app.exit_code = 20
                    break
        else:
            self.app.log.error(f"plugin: {plugin_name} not found for crawler type: {crawler_type}")
            self.app.exit_code = 127

    @ex(
        help="performs git pull to update the codebase",
        arguments=[
            (['-t', '--type'], {
                'action': 'store',
                'dest': 'type',
                'help': "the crawler type",
                'choices': PLATFORMS,
            })
        ]
    )
    def sync(self):
        if self.app.pargs.type:
            type = self.app.pargs.type
            crawler_paths = self.config[type]['paths']

            for crawler_path in crawler_paths:
                Log.info(f"Syncing: {crawler_path}")
                crawler_path = path.expanduser(crawler_path)
                curr_branch_name = get_current_branch_name(crawler_path)
                system(f"cd {crawler_path} && git pull origin {curr_branch_name} --ff-only")
        else:
            Log.warn("Please enter a valid type")

    @ex(
        help="create basic boilerplate for plugins ",
        arguments=[
            (
                ['-s', '--service'], {
                    "action": "store",
                    "dest": "plugin_name",
                    "help": "the name of the plugin to be created"
            }), (
                ['--init', '-i'], {
                    "action": "store_true",
                    "dest": 'init',
                    "help": "create a crawler step by step"
            }), (
                ['-t', '--template'], {
                    "action": "store",
                    "dest": 'template',
                    "help": "choose a template to boilerplate php|node|py|vc defaults to php"
                }
            ), (
                ['--path'], {
                    'action': "store",
                    'dest': 'folder_path',
                    'help': 'the path of the folder where the plugin will reside'
                }
            )
        ]
    )
    def create(self):

        template = self.app.pargs.template

        if self.app.pargs.folder_path is not None:
            folder_path = self.app.pargs.folder_path
            folder_path = folder_path.rstrip('/')
            folder_path = path.expanduser(folder_path)
        else:
            folder_path = pathlib.Path().resolve()
            folder_path = str(folder_path)

        context = {}
        pid = ''
        jira_id = ''
        site_link = ''
        col_headers: List[str] = []
        scrape_category = ''
        
        if self.app.pargs.init:
            if template:
                return self.app.log.error('setting both --init and -t ' + template + ' is not allowed')

            lang_type_index = ask_user_input('Choose Language Type:\n' + '\n'.join([f'[{lang.value}] {lang.name}' for lang in LanguageType]) + '\n> ')
            client_name = ask_user_input('Enter Client Name: ')
            site_link = ask_user_input('Enter Website Link: ', allow_empty=True)
            scrape_category = normalize_plugin_text(ask_user_input('Enter Scrape Category Type if any: ', allow_empty=True))
            pid = ask_user_input('Enter Project ID/URL: ', allow_empty=True)
            pid = first_found_numbers(pid)
            jira_id = ask_user_input('Enter Jira Ticket ID/URL: ', allow_empty=False)
            jira_id = get_jira_id(jira_id)
            col_headers_input: str = ask_user_input('Enter column headers if any (comma/newline seperated): ', allow_empty=True, raw_input=True, msg_after_first='Enter any more column headers: ')
            col_headers = string_to_list(col_headers_input.strip())
            col_headers = [h for h in col_headers if h]
            plugin_name = generate_plugin_name(client_name, site_link, scrape_category)

            if not pid:
                pid = '***'

            origin = ''
            parsed_url = return_parsed_url(site_link)
            if parsed_url:
                origin = f"{parsed_url.scheme}://{parsed_url.hostname}"
                if parsed_url.port:
                    origin += f":{parsed_url.port}"

            context = {
                'plugin_name': plugin_name,
                'pid': pid,
                'jid': jira_id,
                'base_url': site_link,
                'domain_url': origin,
                'scrape_category': scrape_category,
                'host_name': parsed_url.hostname if parsed_url else None,
                'plugin_dirname': path.basename(folder_path.rstrip('/')),
                'col_headers': json.dumps(col_headers),
                'dependencies': [], # TODO:
            }

            lang_type = LanguageType(lang_type_index)
            template = lang_type.template_name

            if lang_type in NODE_LANGUAGE_TYPES:
                recommended_packages = [
                    '@vortex-ts-sdk/http-crawler',
                    '@vortex-ts-sdk/cache-handler',
                    '@vortex-ts-registry/p-queue',
                    '@vortex-ts-registry/crawler-utils',
                ]
                packages_to_install = []
                plugin_path = path.join(folder_path, plugin_name)
                
                for package_name in recommended_packages:
                    if ask_user_input_YN('Install Recommended Package `' + package_name + '`: ') == 'Y':
                        packages_to_install.append(package_name)
                context['packages_to_install'] = packages_to_install

                if lang_type == LanguageType.JAVASCRIPT:
                    create_boilerplate(plugin_path, "node_boilerplate.jinja2", context, 'js')
                    render_boilerplate(path.join("node_ts", "package.json.jinja2"), context, path.join(plugin_path, 'package.json'))
                
                if lang_type == LanguageType.TYPESCRIPT:
                    context['language_type'] = 'typescript'
                    context['enable_source_map'] = ask_user_input_YN('Enable source maps for easier debugging?') == 'Y'
                    render_boilerplate("node_ts", context, plugin_path)
                
                base_path = pathlib.Path(plugin_path).parent
                test = TestLocal(type=template, base_path=base_path, plugin_name=plugin_name)
                if packages_to_install:
                    self.app.log.info(f'Installing packages: `{", ".join(packages_to_install)}`')
                    test.node_pkg_install(' '.join(packages_to_install))
                if lang_type == LanguageType.TYPESCRIPT:
                    self.app.log.info(f'Installing package: `typescript` as devdependency')
                    test.node_pkg_install('typescript', ['--save-dev'])

                Log.info('Plugin created at {}'.format(plugin_path))
                return
                
        else:
            if self.app.pargs.plugin_name is None:
                self.app.log.error("cannot create boilerplate file without plugin's name")
                return
            else:
                plugin_name = self.app.pargs.plugin_name
        
        
        data = {
            'plugin_name': plugin_name,
            **context
        }

        plugin_path = folder_path + '/' + plugin_name
        if template == 'vc':
            create_boilerplate(plugin_path, "php_vc_boilerplate.jinja2", data, 'php')
        elif template == 'py':
            create_boilerplate(plugin_path, "py_boilerplate.jinja2", data, 'py')
        elif template == 'brp':
            create_boilerplate(plugin_path, "php_brp_boilerplate.jinja2", data, 'php')
        else:
            create_boilerplate(plugin_path, "php_boilerplate.jinja2", data, 'php')

    @ex(
        help="deploy a specific plugin to live with versioning",
        arguments=[
            (['-s', '--service'], {
                "action": "store",
                'required': True,
                "dest": 'plugin_name',
            }), (['-m', '--message'], {
                "action": "store",
                'required': True,
                "dest": "message"
            }), (['-st', '--stable'], {
                "action": "store_true",
                "dest": "stable_flag"
            }), (['--patch'], {
                "action": "store_true",
                "dest": "patch_flag"
            }), (['--minor'], {
                "action": "store_true",
                "dest": "minor_flag",
                "help": "set major of a version"
            }), (['--major'], {
                "action": "store_true",
                "dest": "major_flag"
            }),
            (['--verbose'], {
                "action": 'store_true',
                "dest": "verbose"
            })
        ]
    )
    def deploy(self):

        toolbar_width = 50
        verbose_mode = False

        if (self.config.get('verbose') == True) or (self.app.pargs.verbose == True):
            verbose_mode = True

        input_plugin_name = self.app.pargs.plugin_name
        deploy_message = self.app.pargs.message

        if input_plugin_name is None:
            self.app.log.error("cannot deploy without service code")
            return False
        if deploy_message is None:
            self.app.log.error("cannot deploy without deploy message")
            return False

        if self.app.pargs.stable_flag:
            deploy_type = "DEPLOY-STABLE"
        else:
            deploy_type = "DEPLOY"

        major_flag = self.app.pargs.major_flag
        minor_flag = self.app.pargs.minor_flag

        plugin_names = False
        if ',' in input_plugin_name:
            plugin_names = input_plugin_name.split(',')

        if plugin_names == False:
            plugin_names = []
            plugin_names.append(input_plugin_name)

        for plugin_name in plugin_names:
            plugin_name = plugin_name.strip()
            plugin_props = extract_plugin_properties(plugin_name)
            plugin_dir_path = plugin_props['path']
            crawler_type = plugin_props['type']

            if not plugin_dir_path:
                self.app.log.error(f'Could not find plugin: {plugin_name}')
                continue

            plugin_info = get_plugin_info(plugin_dir_path)
            if plugin_info:
                base_class = plugin_info['base_class']
                if base_class and not base_class.startswith('Vtx_Service_Plugin'):
                    if base_class not in plugin_info['dependencies'] and (not is_env_noninteractive()):
                        msg = f'Plugin extends {base_class} but does not declare it as a dependency.'
                        self.app.log.warning(msg)
                        if ask_user_input_YN(f'[Experimental] Do you want to automatically add dependencies?') == 'Y':
                            insert_all_chained_dependencies(plugin_name)
                        go_fwd = ask_user_input_YN(f'Do you want to continue?')
                        if go_fwd == 'N':
                            continue

            root_repo_dir = path.dirname(plugin_dir_path)
            if verbose_mode:
                sys.stdout.write('Syncing Repo: ' + root_repo_dir + '\n')
                sys.stdout.flush()
            quiet_mode = "" if verbose_mode else "--quiet"
            curr_branch_name = get_current_branch_name(root_repo_dir)
            git_sync_cmds = [
                f'git pull origin {curr_branch_name} {quiet_mode} --ff-only',
            ]

            mixed_rebase_cmd = 'git reset --mixed HEAD~1'

            if verbose_mode:
                git_sync_cmd = verbosify(git_sync_cmds)
            else:
                git_sync_cmd = return_cmd_with_progress(git_sync_cmds, toolbar_width)
            try:
                try:
                    proc = cmd_shell_exec(git_sync_cmd, working_dir=root_repo_dir, check=False) # check=false so that we can show the exact error to the user.
                except subprocess.TimeoutExpired:
                    self.app.log.error(f'timed out on syncing repo for {plugin_name}')
                    continue
                if proc.returncode != 0:
                    self.app.log.error(f'syncing repo for {plugin_name}. The command(s) that failed was `{",".join(git_sync_cmds)}`')
                    self.app.log.error(proc.stderr)
                    if can_rebase(proc):
                        self.app.log.error(f'Can probably fix this error with `{mixed_rebase_cmd}`')
                    continue
                
                # if crawler_type == 'node' and ('vortex-ts-crawler' == path.basename(root_repo_dir)):
                #     latest_commit_info = get_latest_commit_info(root_repo_dir)
                #     if latest_commit_info is not None:
                #         latest_commit_date = latest_commit_info.get('commit_date')
                #         if latest_commit_date:
                #             diff_minutes = (get_current_utc_aware_datetime().timestamp() - latest_commit_date.timestamp()) / 60
                #             MIN_TIME_PERIOD_BTN_2_COMMITS = 2.5
                #             if is_this_package_installed_locally():
                #                 # MIN_TIME_PERIOD_BTN_2_COMMITS = 200000
                #                 self.app.log.warning(f'Last commit was made {diff_minutes:.2f} minutes ago (by `{latest_commit_info.get("author_name")}`)')

                #             if diff_minutes <= MIN_TIME_PERIOD_BTN_2_COMMITS:
                #                 self.app.log.warning(f'Last commit was made {diff_minutes:.2f} minutes ago (by `{latest_commit_info.get("author_name")}`).\nPipeline for `vortex-ts-crawler` will likely fail if multiple deploys are made within ~{MIN_TIME_PERIOD_BTN_2_COMMITS} minutes.')
                #                 if not is_env_noninteractive():
                #                     if ask_user_input_YN('Do you want to continue?') == 'N':
                #                         self.app.exit_code = 1
                #                         return
                            
                if not verbose_mode:
                    sys.stdout.write(
                        "Deploying: [%s]" % (" " * toolbar_width))
                    sys.stdout.write("\b" * (toolbar_width + 1))
                    sys.stdout.flush()
                
                plugin_abs_path = path.join(plugin_dir_path, plugin_name + '.' + get_extension(crawler_type))
                if path.exists(plugin_abs_path):
                    if not does_plugin_have_modifications(plugin_name, root_repo_dir, crawler_type):
                        self.app.log.warning(f'No changes detected for {plugin_name}. Adding newline')
                        write_text(plugin_abs_path, read_text(plugin_abs_path) + "\n")
                
                version_info = update_version_file(plugin_dir_path, major_flag, minor_flag, crawler_type)
                if crawler_type == 'node':
                    pkg_path = path.join(plugin_dir_path, 'package.json')
                    pkg: Dict[str, Any] = load_json(read_text(pkg_path))
                    pkg['version'] = version_info
                    write_text(pkg_path, json.dumps(pkg, indent=4))

                if plugin_info and version_info == '0.0.1':
                    # if its already deployed then the service probabily works fine.
                    # if its the first deploy, we annoy the user.
                    if not plugin_info.get('pid_forced'):
                        self.app.log.warning("PID was not forced. This may cause issues.")

                commit_msg = f'[{deploy_type}] [{version_info}] {deploy_message}'
                # self.app.log.info(commit_msg)
                main_git_cmds = [
                    f'git restore --staged .', # unstage all stage files. this is done if the users system has weird settings that stages files when merge/pull conflcit.
                    f'git add {plugin_name}/',
                    f'git commit -m "{commit_msg}" {quiet_mode}',
                ]
                push_cmds = [
                    f'git push origin {curr_branch_name} {quiet_mode} --porcelain' + (' --dry-run' if self.config.get('dry_run') else ''),
                ]

                for _ in range(5):
                    # git add + commit
                    if verbose_mode:
                        git_commit_cmds = verbosify(main_git_cmds)
                    else:
                        git_commit_cmds = return_cmd_with_progress(main_git_cmds, toolbar_width)
                    proc = cmd_shell_exec(git_commit_cmds, working_dir=root_repo_dir, check=True)
                    
                    # git push portion
                    push_successful = False
                    should_try_with_rebase = False
                    if verbose_mode:
                        git_push_cmds = verbosify(push_cmds)
                    else:
                        git_push_cmds = return_cmd_with_progress(push_cmds, toolbar_width)
                    try:
                        proc = cmd_shell_exec(git_push_cmds, working_dir=root_repo_dir, timeout=300, check=False)
                        push_successful = True
                        if should_pull_again(proc):
                            push_successful = False
                            should_try_with_rebase = True
                    except subprocess.TimeoutExpired:
                        self.app.log.error(f'git push timeout occured when deploying {plugin_name}')
                    
                    if not push_successful and should_try_with_rebase:
                        user_approves_of_rebase = ask_user_input_YN(f'Push was not successful. Should try with rebase ({mixed_rebase_cmd})? [Experimental]') == 'Y'
                        if user_approves_of_rebase:
                            proc = cmd_shell_exec(mixed_rebase_cmd, working_dir=root_repo_dir)
                            if proc.returncode == 0:
                                continue   # try commit and push again
                    elif proc.returncode != 0:
                        raise subprocess.CalledProcessError(proc.returncode, git_push_cmds, proc.stdout, proc.stderr)
                    break

            except subprocess.CalledProcessError as e:
                if verbose_mode:
                    self.app.log.error(e)

                self.app.log.error(f'There was a problem deploying {plugin_name}')
                continue

            if verbose_mode is False:
                sys.stdout.flush()
                sys.stdout.write("\n")

            show_schema(plugin_dir_path)

            try:
                app_url = f'https://platform.grepsr.com/projects/{plugin_info["pid"]}'
                if plugin_info.get('rid'):
                    app_url += f'/reports/{plugin_info["rid"]}'
                self.app.log.info(f"App Url: {app_url}")
            except KeyError:
                self.app.log.warning(f"Cannot find pid in plugin, please find the project's url manually")

            self.app.log.info(
                f"Plugin: {plugin_name} [{version_info}] deployed successfully")
            
        try_updating_itself()

    @ex(
        help="use a base plugin from: https://bitbucket.org/grepsr/vortex-plugins-services-base",
        arguments=[
            (['-s', '--service'], {
                "help": "name of the base crawler you want to use",
                "action": "store",
                "dest": "base_plugin_name"
            }),
            (['-t'], {
                "help": "name of target crawler that you want to use",
                "action": "store",
                "dest": "plugin_name"
            })
        ]
    )
    def use_basecrawler(self):

        s3 = S3(aws_id=self.config['aws_access_key_id'],
                aws_sec_key=self.config['aws_secret_access_key'])

        version = None
        base_plugin_name = self.app.pargs.base_plugin_name
        target_plugin_name = self.app.pargs.plugin_name

        if(base_plugin_name is None or target_plugin_name is None):
            Log.error(
                "Please Enter base crawler and target cralwers.\nUse gcli crawler use-basecrawler -h for more information")
            return

        if('-' in base_plugin_name):
            version = base_plugin_name.split('-')[1]
            base_plugin_name = base_plugin_name.split('-')[0]

        # to check if there is a base-plugin in thier gcli settings ...
        base_plugin_dir_path = get_plugin_path(
            base_plugin_name, type='php')

        target_plugin_path = get_plugin_path(
            target_plugin_name, type='php'
        )

        if(version is None and base_plugin_dir_path):
            f = open(f"{base_plugin_dir_path}/.version", mode='r')
            version = f.read()
            f.close()

        if(version is None):
            Log.error(
                "Please Specify the version of base crawler that you want to use")
            return

        if(target_plugin_path):
            Log.info(
                f'Getting Secure Url of target plugin: {base_plugin_name}, {version}')

            presigned_url = s3.get_secure_url(bucket='crawler-plugins',
                                              filename=f'php/vortex-plugins-services-base/{base_plugin_name}/{base_plugin_name}-{version}.tar.gz')

            data = {
                'presigned_url': presigned_url,
                'plugin_name': base_plugin_name,
                'version': version
            }

            render_boilerplate(boilerplate='composer.jinja2', data=data,
                               destination_path=target_plugin_path + '/composer.json')
            system(
                f""" cd {target_plugin_path} &&  composer install""")
        else:
            Log.error(f"Target plugin: {target_plugin_name} not found")


    @ex(
        help="list all the dependents of this given plugin",
        arguments=[
            (['-s', '--service'], {
                "action": "store",
                'required': True,
                "dest": 'plugin_name'
            })
        ]
    )
    def list_dependents(self):
        plugin_name = self.app.pargs.plugin_name
    
        if plugin_name is None:
            self.app.log.error("no service code provided")
            return False
        plugin_dir_path = get_plugin_path(plugin_name, all_types=True)

        if not plugin_dir_path:
            self.app.log.error(f'Could not find plugin: {plugin_name}')
            return
        
        for dependents in list_dependents(plugin_name):
            print(dependents)

    @ex(
        help="install a package for plugin",
        arguments=[
            (['-s', '--service'], {
                'action': 'store',
                'required': True,
                'dest': 'plugin_name',
                'help': "The name of the service/plugin to run locally"
            }),
            (['-p', '--package'], {
                'action': 'store',
                'required': True,
                'dest': 'package_name',
                'help': "The name of the package to install"
            }),
            (['-D', '--save-dev'], {
                'action': 'store_true',
                'required': False,
                'dest': 'dev_dep',
                'help': "if this should be installed as devDependencies"
            }),
            (['-t', '--type'], {
                'action': 'store',
                'required': True,
                'dest': 'crawler_type',
                'help': "the crawler type",
                'choices': PLATFORMS,
            }),
        ]
    )
    def package_install(self):
        plugin_name = self.app.pargs.plugin_name
        package_name_csv = self.app.pargs.package_name
        crawler_type = self.app.pargs.crawler_type
        is_dev_dependency = self.app.pargs.dev_dep

        package_names = package_name_csv.split(',')
        final_packages = []
        for package_name in package_names:
            package_name = package_name.strip()
            if not package_name:
                self.app.log.error(f"package name is empty")
                continue
            final_packages.append(package_name)
        
        plugin_path = get_plugin_path(plugin_name, type=crawler_type)
        if plugin_path:
            base_path = pathlib.Path(plugin_path).parent
            test = TestLocal(type=crawler_type, base_path=base_path, plugin_name=plugin_name)
            self.app.log.info(f'Installing package: `{", ".join(final_packages)}` {"as devdependency" if is_dev_dependency else ""}')
            test.node_pkg_install(' '.join(final_packages), ['--save-dev'] if is_dev_dependency else None)
        else:
            self.app.log.error(f"plugin: {plugin_name} not found for crawler type: {crawler_type}")
            self.app.exit_code = 127

    @ex(
        help="uninstall a package for plugin",
        arguments=[
            (['-s', '--service'], {
                'action': 'store',
                'required': True,
                'dest': 'plugin_name',
                'help': "The name of the service/plugin to run locally"
            }),
            (['-p', '--package'], {
                'action': 'store',
                'required': True,
                'dest': 'package_name',
                'help': "The name of the package to install"
            }),
            (['-t', '--type'], {
                'action': 'store',
                'required': True,
                'dest': 'crawler_type',
                'help': "the crawler type",
                'choices': PLATFORMS,
            }),
        ]
    )
    def package_uninstall(self):
        plugin_name = self.app.pargs.plugin_name
        package_name_csv = self.app.pargs.package_name
        crawler_type = self.app.pargs.crawler_type

        package_names = package_name_csv.split(',')
        final_packages = []
        for package_name in package_names:
            package_name = package_name.strip()
            if not package_name:
                self.app.log.error(f"package name is empty")
                continue
            final_packages.append(package_name)
        
        plugin_path = get_plugin_path(plugin_name, type=crawler_type)
        if plugin_path:
            base_path = pathlib.Path(plugin_path).parent
            test = TestLocal(type=crawler_type, base_path=base_path, plugin_name=plugin_name)
            docker_image_name = test.type_config["sdk_image"]
            self.app.log.info(f'Uninstalling package: `{", ".join(final_packages)}`')
            test.run_command_in_docker(docker_image_name, f'cd {plugin_name} && npm uninstall ' + ' '.join(final_packages))
        else:
            self.app.log.error(f"plugin: {plugin_name} not found for crawler type: {crawler_type}")
            self.app.exit_code = 127

    