import os
from dynaconf.loaders.env_loader import *


def load_from_env(
        obj,
        prefix=False,
        key=None,
        silent=False,
        identifier=IDENTIFIER_PREFIX,
        env=False,  # backwards compatibility bc renamed param
        validate=False,
        environ=None,
):
    if environ is None:
        environ = os.environ
    elif not environ:
        environ = {}

    if prefix is False and env is not False:
        prefix = env

    env_ = ""
    if prefix is not False:
        if not isinstance(prefix, str):
            raise TypeError("`prefix/env` must be str or False")

        prefix = prefix.upper()
        env_ = f"{prefix}_"

    # set source metadata
    source_metadata = SourceMetadata(identifier, prefix, "global")

    # Load a single environment variable explicitly.
    if key:
        key = upperfy(key)
        value = environ.get(f"{env_}{key}")
        if value:
            try:  # obj is a Settings
                obj.set(
                    key,
                    boolean_fix(value),
                    loader_identifier=source_metadata,
                    tomlfy=True,
                    validate=validate,
                )
            except AttributeError:  # obj is a dict
                obj[key] = parse_conf_data(
                    boolean_fix(value), tomlfy=True, box_settings=obj
                )

    # Load environment variables in bulk (when matching).
    else:
        # Only known variables should be loaded from environment?
        ignore_unknown = obj.get("IGNORE_UNKNOWN_ENVVARS_FOR_DYNACONF")

        # prepare data
        trim_len = len(env_)
        data = {
            key[trim_len:]: parse_conf_data(
                boolean_fix(value), tomlfy=True, box_settings=obj
            )
            for key, value in environ.items()
            if key.startswith(env_)
               and not (
                # Ignore environment variables that haven't been
                # pre-defined in settings space.
                    ignore_unknown
                    and obj.get(key[trim_len:], default=missing) is missing
            )
        }
        # Update the settings space based on gathered data from environment.
        if data:
            filter_strategy = obj.get("FILTER_STRATEGY")
            if filter_strategy:
                data = filter_strategy(data)
            obj.update(
                data, loader_identifier=source_metadata, validate=validate
            )
