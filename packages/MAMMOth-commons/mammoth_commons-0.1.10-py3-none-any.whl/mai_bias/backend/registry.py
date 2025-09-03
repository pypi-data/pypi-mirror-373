import inspect
from typing import get_type_hints
import markdown2
from mammoth_commons.externals import format_description, format_name


class Registry:
    def __init__(self, desktopmode=True):
        self.dataset_loaders = dict()
        self.model_loaders = dict()
        self.analysis_methods = dict()
        self.name_to_runnable = dict()
        self.parameters_to_class = dict()
        self.desktopmode = desktopmode

    def data(self, component, compatible=None):
        self._register(self.dataset_loaders, component, compatible)

    def model(self, component, compatible=None):
        self._register(self.model_loaders, component, compatible)

    def analysis(self, component, compatible=None):
        self._register(self.analysis_methods, component, compatible)

    def _register(self, catalogue: dict, component, compatible=None):
        component = component.python_func.__mammoth_wrapped__
        signature = inspect.signature(component)
        type_hints = get_type_hints(component)
        doc, args_desc, args_options = format_description(
            component.__doc__, desktopmode=self.desktopmode
        )
        # args_desc = {k: markdown2.markdown(v) for k,v in args_desc.items()}

        doc = markdown2.markdown(doc)
        args = list()
        args_to_classes = dict()
        for pname, parameter in signature.parameters.items():
            arg_type = type_hints.get(pname, parameter.annotation)
            assert pname != "return"
            args_to_classes[pname] = arg_type
            arg_type = arg_type.__name__
            if arg_type == "str" and (
                "path" in pname.lower() or "url" in pname.lower()
            ):
                arg_type = "url"
            if parameter.default is not inspect.Parameter.empty:  # ignore kwargs
                args.append(
                    [
                        pname,
                        arg_type,
                        "None" if parameter.default is None else parameter.default,
                        args_desc.get(pname, format_name(pname)),
                    ]
                )
            else:
                args.append(
                    [pname, arg_type, "None", args_desc.get(pname, format_name(pname))]
                )

        name = format_name(component.__name__)
        assert name not in self.name_to_runnable
        self.name_to_runnable[name] = component
        catalogue[name] = {
            "description": doc,
            "parameters": args,
            "parameter_options": args_options,
            "name": component.__name__,
            "compatible": (
                []
                if compatible is None
                else [
                    format_name(c.python_func.__mammoth_wrapped__.__name__)
                    for c in compatible
                ]
            ),
            "return": signature.return_annotation.__name__,
        }
        args_to_classes["return"] = signature.return_annotation
        self.parameters_to_class[name] = args_to_classes
