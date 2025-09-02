
import os
import inspect
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class ArgumentParser:
    def __init__(self):
        pass

    def calledActions(self, caller: str, localVars: dict) -> None:
        showOutput = os.getenv("SHOW_CALLED_ACTIONS", 'False') == 'True'
        if not showOutput:
            return

        # Climb up two frames: this function -> calledActions -> true caller
        frame = inspect.currentframe()
        if frame is not None:
            outer_frame = frame.f_back.f_back  # Two frames up
            if outer_frame is not None:
                actionName = outer_frame.f_code.co_name
            else:
                actionName = "<unknown>"
        else:
            actionName = "<unknown>"

        className = caller.__class__.__name__ if hasattr(caller, '__class__') else str(caller)

        # Filter out 'self' and any dunder vars
        args = {k: v for k, v in localVars.items() if k != 'self' and not k.startswith('__')}
        if args:
            print(f"Called {actionName} with arguments:")
            for k, v in args.items():
                print(f"  {k}: {v}\n")
        else:
            print(f"Called {actionName}:")


    def printArgs(self, caller: str, localVars: dict) -> None:
        showOutput = os.getenv("SHOW_CALLED_ACTIONS", 'False') == 'True'
        if not showOutput:
            return

        frame      = inspect.currentframe().f_back
        className  = caller.__class__.__name__ if hasattr(caller, '__class__') else caller.__name__
        actionName = frame.f_code.co_name

        # Filter out 'self' and any dunder vars
        args = {k: v for k, v in localVars.items() if k != 'self' and not k.startswith('__')}
        if args:
            print(f"Called {actionName} with arguments:")
            for k, v in args.items():
                print(f"  {k}: {v}\n")
        else:
            print(f"Called {actionName}:")

    def getListSig(self, obj, func_name):
        for attr in ("listSig", "list_sig", "LIST_SIG"):
            value = getattr(obj, attr, None)
            if isinstance(value, dict) and func_name in value:
                return value[func_name]
        return None

    def getDictSig(self, obj, func_name):
        for attr in ("dictSig", "dict_sig", "DICT_SIG"):
            value = getattr(obj, attr, None)
            if isinstance(value, dict) and func_name in value:
                return value[func_name]
        return None
