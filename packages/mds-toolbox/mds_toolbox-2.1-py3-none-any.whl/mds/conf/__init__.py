from mds.conf import global_settings

# List of modules to load settings from
TO_LOAD = [global_settings]


class Settings:
    def __init__(self, *modules):
        """
        Initialize the Settings instance with the provided modules.

        Args:
            *modules: Variable length argument list of modules to load settings from.
        """
        for module in modules:
            for setting in dir(module):
                if setting.isupper():
                    setattr(self, setting, getattr(module, setting))

    def configure(self, **ext_settings):
        """
        Configure the settings instance by setting new values or overriding existing ones.

        Args:
            **ext_settings: Arbitrary keyword arguments representing settings to be configured.
                            Only capital keywords are considered.
        """
        for key, value in ext_settings.items():
            if key.isupper():
                setattr(self, key, value)


# Create a Settings instance as unique entry point to the app settings
settings = Settings(*TO_LOAD)
