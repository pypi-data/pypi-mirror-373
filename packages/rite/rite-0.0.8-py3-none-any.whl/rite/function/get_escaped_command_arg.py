from shlex import quote


def get_escaped_command_arg(arg) -> str:
    return quote(arg)
