from grepsrcli.core import utils

def test_list_dependents():
    dependents = utils.list_dependents('gi_service_main')
    expected_dependents = [
        'nordstorm_web_desktop',
        'gi_connection_com',
        'gi_neiman_marcus_com',
        'gi_lowes_products',
        'gi_pcnation_com',
        'gi_bissell_com',
        'gi_homedepot_pdp',
        'gi_costco_com_new',
        'gi_walmart_com_zip',
        'gi_conns_com',
        'gi_pcrichard_com',
        'gi_target_com',
        'gi_nordstorm_com',
        'bestbuy_pdp',
        'gi_dell_com',
        'gi_intelligence_QVC',
        'gi_samsclub_com',
        'gi_ajmadison_com',
        'gi_abt_com',
        'gi_insight_com',
        'gi_bhpPhotoVideo_com',
        'gi_wayfair_com'
    ]
    assert len(dependents) == len(expected_dependents)
    for dependent in dependents:
        assert dependent in expected_dependents

def test_get_plugin_path():
    pass