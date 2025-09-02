import importlib.metadata


def get_lock_meta(module):
    name = module.partition(".")[0]
    version = importlib.metadata.version(name)
    return dict(package_lock_name=name, package_lock_version=version)
