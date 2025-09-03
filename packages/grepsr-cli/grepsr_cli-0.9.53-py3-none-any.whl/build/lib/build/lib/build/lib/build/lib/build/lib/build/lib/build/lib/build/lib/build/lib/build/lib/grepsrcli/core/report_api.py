from ..core.config import load_config
import requests as req
import json


config = load_config('config.yml')


def get_report_from_pid(pid, report_name):
    """[summary]

    Args:
        pid ([type]): [description]
        report_id ([type]): [description]
    """

    res = req.get(
        'https://api.grepsr.com/v1/report/list?project_id={}&x-api-key={}'.format(pid, config['api_key']))

    res_json = json.loads(res.text)
    reports = res_json['payload']
    for report in reports:
        if report['name'].strip() == report_name.strip():
            return report['report_id']

    return False


def run_report_by_rid(rid):
    """[summary]

    Args:
        rid ([type]): [description]
    """

    run_api = req.get(
        'https://api.grep.sr/v1/report/run?report_id={}&x-api-key={}'.format(rid, config['api_key']))

    return json.loads(run_api.text)['message']
