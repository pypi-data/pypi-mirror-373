from cement import Controller, ex
from webbrowser import open_new_tab
from ..core.config import load_config
from ..core.utils import get_plugin_path, get_plugin_info
from ..core.report_api import get_report_from_pid, run_report_by_rid


class ReportBase(Controller):
    class Meta:
        label = 'report_base'


class Report(Controller):
    config = load_config('config.yml')

    class Meta:
        label = 'report'
        stacked_on = 'report_base'
        stacked_type = 'nested'

    @ex(
        help="run report to live",
        arguments=[
            (['-rid', '--report-id'], {
                "action": "store",
                "dest": "report_id"
            }),
            (['-s', '--service'], {
                "action": "store",
                "dest": "service_code"
            })
        ]
    )
    def run(self):

        if(self.app.pargs.service_code is not None):
            service_code = self.app.pargs.service_code
            plugin_info = get_plugin_info(
                get_plugin_path(service_code, all_types=True))

            rid = get_report_from_pid(
                plugin_info['pid'], plugin_info['report_name'])

            if(rid):
                run_api_message = run_report_by_rid(rid)
                self.app.log.info("Report: {}, message: {}".format(
                    service_code, run_api_message))
                open_new_tab(
                    f'https://appnext.grepsr.com/projects/{plugin_info["pid"]}')
            else:
                self.app.log.warning(
                    "We couldn't run report via report name, please try running it manually via the url")

                self.app.log.info(
                    f'App Url: https://appnext.grepsr.com/projects/{plugin_info["pid"]}')

        elif (self.app.pargs.report_id is not None):
            report_id = self.app.pargs.report_id
            run_api_message = run_report_by_rid(report_id)
            self.app.log.info("Report ID: {}, message: {}".format(
                report_id, run_api_message))
        else:
            self.app.log.error("please use a valid syntax")
