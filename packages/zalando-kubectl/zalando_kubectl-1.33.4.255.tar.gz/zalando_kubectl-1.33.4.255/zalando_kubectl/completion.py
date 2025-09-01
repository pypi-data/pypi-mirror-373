import click


def extend(lines: list, click_cli, ctx):
    """Extends kubectl completion script with zkubectl commands"""
    commands = []
    functions = []
    for c in click_cli.list_commands(ctx):
        if c != "completion":
            commands.append('    commands+=("' + c + '")')
            functions.extend(_make_completion_functions(ctx, click_cli.get_command(ctx, c), ""))

    result = lines
    try:
        p = result.index("_zkubectl_root_command()")
        result = result[:p] + functions + result[p:]

        p = result.index('    commands+=("completion")')
        result = result[:p] + commands + result[p:]
    except ValueError:
        return lines

    return result


def _make_completion_functions(ctx, command, prefix):
    """Returns completion functions for command and its subcommands as list of lines"""
    functions, subcommands, flags = [], [], []

    if isinstance(command, click.Group):
        for c in command.list_commands(ctx):
            subcommands.append(c)
            functions.extend(_make_completion_functions(ctx, command.get_command(ctx, c), command.name + "_"))

    for param in command.params:
        if isinstance(param, click.Option) and not param.hidden:
            flags.extend(param.opts)

    functions.extend(_make_completion_function(prefix + command.name, subcommands, flags))
    return functions


def _make_completion_function(name: str, subcommands: list, flags: list):
    """Returns completion function as list of lines"""
    return """_zkubectl_{name}() {{
    last_command="zkubectl_{name}"

    commands=()
    {subcommands}
    flags=()
    {flags}
    two_word_flags=()
    local_nonpersistent_flags=()
    flags_with_completion=()
    flags_completion=()
    must_have_one_flag=()
    must_have_one_noun=()
    noun_aliases=()
}}
""".format(
        subcommands="    ".join('commands+=("' + c + '")\n' for c in subcommands),
        flags="    ".join('flags+=("' + c + '")\n' for c in flags),
        name=name,
    ).split(
        "\n"
    )
