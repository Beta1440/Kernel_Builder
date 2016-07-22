from cement.core.foundation import CementApp
from cement.utils.misc import init_defaults

# Application default.  Should update config/kbuilder.conf to reflect any
# changes, or additions here.
defaults = init_defaults('kbuilder')

# All internal/external plugin configurations are loaded from here
defaults['kbuilder']['plugin_config_dir'] = '/etc/kbuilder/plugins.d'

# External plugins (generally, do not ship with application code)
defaults['kbuilder']['plugin_dir'] = '/var/lib/kbuilder/plugins'

# External templates (generally, do not ship with application code)
defaults['kbuilder']['template_dir'] = '/var/lib/kbuilder/templates'


class KbuilderApp(CementApp):
    class Meta:
        label = 'kbuilder'
        config_defaults = defaults

        # All built-in application bootstrapping (always run)
        bootstrap = 'kbuilder.cli.bootstrap'

        # Internal plugins (ship with application code)
        plugin_bootstrap = 'kbuilder.cli.plugins'

        # Internal templates (ship with application code)
        template_module = 'kbuilder.cli.templates'