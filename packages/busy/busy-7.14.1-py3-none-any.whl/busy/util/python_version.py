from sys import version_info

MESSAGE = "This application requires Python version %i.%i.%i or higher"


def confirm_python_version(version):
    if version_info < version:
        raise RuntimeError(MESSAGE % version)
