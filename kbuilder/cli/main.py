"""Kernel Builder main application entry point."""

from cement.core.exc import CaughtSignal, FrameworkError
from kbuilder.cli.config_parser import parse_kernel_config
from kbuilder.cli.app import App
from kbuilder.core import exc


# Define the applicaiton object outside of main, as some libraries might wish
# to import it as a global (rather than passing it into another class/func)
app = App()


def main():
    with app:
        try:
            app.hook.register('pre_run', parse_kernel_config)
            app.run()

        except exc.KbuilderError as e:
            # Catch our application errors and exit 1 (error)
            print('KbuilderError > %s' % e)
            app.exit_code = 1

        except FrameworkError as e:
            # Catch framework errors and exit 1 (error)
            print('FrameworkError > %s' % e)
            app.exit_code = 1

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('CaughtSignal > %s' % e)
            app.exit_code = 0


if __name__ == '__main__':
    main()
