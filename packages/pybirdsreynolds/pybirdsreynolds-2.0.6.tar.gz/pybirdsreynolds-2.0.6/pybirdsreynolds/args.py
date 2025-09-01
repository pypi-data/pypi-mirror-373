# args.py
import argparse
import importlib
import pybirdsreynolds.params as params


def get_description() -> str:
    return (
        importlib.resources.files("pybirdsreynolds")
        .joinpath("DESCRIPTION.txt")
        .read_text(encoding="utf-8")
        .strip()
    )


def get_epilog() -> str:
    return (
        importlib.resources.files("pybirdsreynolds")
        .joinpath("EPILOG.txt")
        .read_text(encoding="utf-8")
        .strip()
    )


def display_range(prefix):
    """
    Return a readable description of valid values for a parameter,
    including ranges, free-mode limits, and default value.
    """
    value_default = getattr(params, f"{prefix}_DEFAULT")

    # Case: integer parameter with range constraints
    if not isinstance(value_default, bool) and isinstance(value_default, int):
        value_min = getattr(params, f"{prefix}_MIN")
        value_max = getattr(params, f"{prefix}_MAX")
        value_free_min = getattr(params, f"{prefix}_FREE_MIN")
        value_free_max = getattr(params, f"{prefix}_FREE_MAX")
        parts = []

        if value_min is not None and value_max is not None:
            parts.append(f"between {value_min} and {value_max}")
        elif value_min is not None:
            parts.append(f">= {value_min}")
        elif value_max is not None:
            parts.append(f"<= {value_max}")
        else:
            parts.append(f"with no limit")

        if value_free_min is not None and value_free_max is not None:
            parts.append(f"if --free between {value_free_min} and {value_free_max}")
        elif value_free_min is not None:
            parts.append(f"if --free >= {value_free_min}")
        elif value_free_max is not None:
            parts.append(f"if --free <= {value_free_max}")
        else:
            parts.append(f"if --free with no limit")

        if value_default is not None:
            parts.append(f"default: {value_default}")

        return f"{' , '.join(parts)}" if parts else ""

    # Case: boolean parameter
    elif isinstance(value_default, bool):
        return f"boolean value, default: {value_default}"

    # Case: string (or other types)
    else:
        return f"string value, default: {value_default}"


def check_values(prefix, free, value, parser):
    """
    Validate a parameter value against defined min/max ranges,
    using free-mode limits if `free` is True.
    """
    value_min = getattr(params, f"{prefix}_MIN")
    value_max = getattr(params, f"{prefix}_MAX")
    value_free_min = getattr(params, f"{prefix}_FREE_MIN")
    value_free_max = getattr(params, f"{prefix}_FREE_MAX")

    # Case: no free
    if not free:
        if (
            value_min is not None
            and value_max is not None
            and (value < value_min or value > value_max)
        ):
            parser.error(
                f"{prefix.lower()} must be between {value_min} and {value_max}"
            )
        elif value_min is None and value_max is not None and value > value_max:
            parser.error(f"{prefix.lower()} must <= {value_max}")
        elif value_min is not None and value_max is None and value < value_min:
            parser.error(f"{prefix.lower()} must >= {value_min}")
    # Case: free
    else:
        if (
            value_free_min is not None
            and value_free_max is not None
            and (value < value_free_min or value > value_free_max)
        ):
            parser.error(
                f"{prefix.lower()} must be between {value_free_min} and {value_free_max}"
            )
        elif (
            value_free_min is None
            and value_free_max is not None
            and value > value_free_max
        ):
            parser.error(f"{prefix.lower()} must <= {value_free_max}")
        elif (
            value_free_min is not None
            and value_free_max is None
            and value < value_free_min
        ):
            parser.error(f"{prefix.lower()} must >= {value_free_min}")


def create_parser():
    controls_text = "\n".join(
        f"  [{getattr(params, name.replace('_TEXT', '_COMMAND'))}] : {getattr(params, name)}"
        for name, value in params.__dict__.items()
        if name.endswith("_TEXT") and getattr(params, f"{name[:-5]}_ACTIVATED") > 0
    )

    parser = argparse.ArgumentParser(
        description=get_description() + "\n\n" + f"controls:\n{controls_text}",
        epilog=get_epilog(),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    for name in dir(params):
        if not name.endswith("_DOC"):
            continue

        prefix = name[:-4]
        activated = getattr(params, f"{prefix}_ACTIVATED")
        if activated == 0:
            continue

        default_name = f"{prefix}_DEFAULT"
        if not hasattr(params, default_name):
            continue

        default_value = getattr(params, default_name)
        arg_name = "--" + prefix.lower()
        if isinstance(default_value, bool):
            parser.add_argument(
                arg_name,
                action="store_true",
                default=default_value,
                help=getattr(params, name) + " (" + display_range(prefix) + ")",
            )
        elif isinstance(default_value, int):
            parser.add_argument(
                arg_name,
                type=int,
                default=default_value,
                help=getattr(params, name) + " (" + display_range(prefix) + ")",
            )
        elif isinstance(default_value, str):
            parser.add_argument(
                arg_name,
                type=str,
                default=default_value,
                help=getattr(params, name) + " (" + display_range(prefix) + ")",
            )
    return parser


def compute_args():
    parser = create_parser()
    args = parser.parse_args()

    for name in dir(params):
        if not name.endswith("_DOC"):
            continue

        prefix = name[:-4]
        hide = getattr(params, f"{prefix}_ACTIVATED")
        if hide == 2:
            continue

        default_name = f"{prefix}_DEFAULT"
        if not hasattr(params, default_name):
            continue

        default_value = getattr(params, default_name)
        if not isinstance(default_value, int) or isinstance(default_value, bool):
            continue

        arg_value = getattr(args, prefix.lower(), None)
        check_values(prefix, args.free, arg_value, parser)

    return args


def get_help_text():
    parser = create_parser()
    return parser.format_help()
