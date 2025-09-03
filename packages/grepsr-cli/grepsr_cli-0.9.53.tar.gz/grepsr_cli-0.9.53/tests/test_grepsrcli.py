
from pytest import raises
from grepsrcli.main import GrepsrCliTest

# def test_grepsrcli():
#     # test grepsrcli without any subcommands or arguments
#     with GrepsrCliTest() as app:
#         app.run()
#         assert app.exit_code == 0


# def test_grepsrcli_debug():
#     # test that debug mode is functional
#     argv = ['--debug']
#     with GrepsrCliTest(argv=argv) as app:
#         app.run()
#         assert app.debug is True


def test_crawler_create_init():
    # test command1 with arguments
    argv = ['crawler', 'create', '--init']
    with GrepsrCliTest(argv=argv) as app:
        app.run()
