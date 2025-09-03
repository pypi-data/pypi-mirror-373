from grepsrcli.core.message_log import Log
from cement import Controller, ex
from grepsrcli.core.sdk_setup import SDKSetup
from grepsrcli.core.config import save_config
from ..core.utils import is_this_package_beta, pip_update_this_package, get_this_version

VERSION = ''
try:
    VERSION = get_this_version()
except Exception:
    pass

VERSION_BANNER = """
gcli: cli tool for grepsr developers version: %s
""" % (VERSION)


class Base(Controller):

    class Meta:
        label = 'base'

        arguments = [
            (['-v', '--version'],
             {'action': 'version',
                'version': VERSION_BANNER}),
        ]

    def _default(self):
        Log.heading(VERSION_BANNER)
        self.app.args.print_help()

    @ex(help="setup SDKs for crawling",
        arguments=[
            (['-t', '--type'], {'action': 'store', 'dest': 'type'}),
            (['--dryrun'], {'action': 'store_true',  'dest': 'dryrun'}),
            (['--sdk'], {'action': 'store',  'dest': 'sdk'}),
        ]
        )
    def setup_sdk(self):
        if self.app.pargs.type is not None:
            SDKSetup(self.app.pargs.type,
                     self.app.pargs.dryrun, self.app.pargs.sdk)
        else:
            Log.error(
                "Please select the platform to setup the sdk.\nExample: gcli setup-sdk -t php|php_next")

    @ex(help="Update configuration for gcli",
        arguments=[
            (['--update'], {'action': 'store_true',  'dest': 'update'}),
        ]
        )
    def configure(self):
        if(self.app.pargs.update == True):
            save_config(update=True)
        else:
            save_config(update=False)

    @ex(help="Updates gcli to the latest version",
        arguments=[
            (['--unstable'], {'action': 'store_true',  'dest': 'unstable'}),
        ]
        )
    def update(self):
        is_in_beta_version = bool(is_this_package_beta())
        pip_update_this_package(ask_force_update=True, use_test_pypi=self.app.pargs.unstable or is_in_beta_version)