import argparse


class OptionalSecondArgFormatter(argparse.HelpFormatter):
    def _format_args(self, action, default_metavar):
        if getattr(action, "optsecond", False):
            return f"{default_metavar} [{action.optsecond}]"
        return super()._format_args(action, default_metavar)


class OptionalSecondArgAction(argparse.Action):
    # Custom action to set a flag for selective formatting
    def __init__(self, *args, **kwargs):
        self.optsecond = kwargs.pop("optsecond", False)
        super().__init__(*args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        # Implement the logic for handling the argument
        if getattr(namespace, self.dest, None) is None:
            setattr(namespace, self.dest, [])
        current_values = getattr(namespace, self.dest)
        current_values.append(values)
        setattr(namespace, self.dest, current_values)
