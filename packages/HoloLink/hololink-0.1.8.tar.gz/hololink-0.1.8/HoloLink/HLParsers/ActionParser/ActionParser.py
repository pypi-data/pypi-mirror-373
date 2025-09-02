
import ast
import inspect
import types
import re
import logging
from dotenv import load_dotenv
from rapidfuzz import process, fuzz

load_dotenv()
logger = logging.getLogger(__name__)


class ActionParser:
    def __init__(self):
        pass

    def checkActions(self, action: str) -> str:
        """
        Check if the action string is a valid action format.
        Returns the action name if valid, or None if not.
        """
        match = re.search(r"action='([^']*)'", action)
        return match.group(1) if match else None

    # def getActions(self, action: str) -> list:
    #     """
    #     Parse a string of actions, potentially with parameters, into a list of action names.
    #     Handles both single actions and lists of actions in string format.
    #     If the action is a list (e.g., "[action1, action2]"), it will return a list of actions.
    #     If the action is a single action (e.g., "action1(param1, param2)"), it will return a list with that single action.
    #     If the action is None or empty, it returns an empty list.
    #     Raises TypeError if the action is not a string.
    #     """
    #     if action is None:
    #         action = "None"
    #     if not isinstance(action, str):
    #         raise TypeError(f"Expected a string in getActions, got {type(action).__name__}.")
    #     s = action.strip()
    #     if s.startswith("[") and s.endswith("]"):
    #         try:
    #             lit = ast.literal_eval(s)
    #             if isinstance(lit, list):
    #                 return [str(item).strip() for item in lit]
    #         except (ValueError, SyntaxError):
    #             s = s[1:-1].strip()

    #     actions     = []
    #     buf         = []
    #     paren_level = 0
    #     in_quote    = False
    #     quote_char  = None

    #     for ch in s:
    #         if ch in ("'", '"'):
    #             if not in_quote:
    #                 in_quote   = True
    #                 quote_char = ch
    #             elif quote_char == ch:
    #                 in_quote = False

    #         if ch == "," and not in_quote and paren_level == 0:
    #             token = "".join(buf).strip()
    #             if token:
    #                 actions.append(token)
    #             buf = []
    #             continue

    #         buf.append(ch)
    #         if ch == "(" and not in_quote:
    #             paren_level += 1
    #         elif ch == ")" and not in_quote and paren_level > 0:
    #             paren_level -= 1

    #     last = "".join(buf).strip()
    #     if last:
    #         actions.append(last)

    #     return actions
    def getActions(self, action: str) -> list:
        """
        Parse a string of actions, potentially with parameters, into a list of action names.
        Handles both single actions and lists of actions in string format.
        If the action is a string that represents a list
            (e.g., "['action1', 'action2']"), it will return a list of actions.
        If the action is a single action string
            (e.g., "action1(param1, param2)"), it will return a list with that single action.
        If the action is None or empty, it returns an empty list.
        Returns [] on any parsing error.
        """
        try:
            if action is None:
                action = "None"
            # if not isinstance(action, str):
            #     raise TypeError(f"Expected a string in getActions, got {type(action).__name__}. Converting to a string")
            if not isinstance(action, str):
                action = str(action)
            s = action.strip()
            if s.startswith("[") and s.endswith("]"):
                try:
                    lit = ast.literal_eval(s)
                    if isinstance(lit, list):
                        return [str(item).strip() for item in lit]
                except (ValueError, SyntaxError):
                    s = s[1:-1].strip()

            actions     = []
            buf         = []
            paren_level = 0
            in_quote    = False
            quote_char  = None

            for ch in s:
                if ch in ("'", '"'):
                    if not in_quote:
                        in_quote   = True
                        quote_char = ch
                    elif quote_char == ch:
                        in_quote = False

                if ch == "," and not in_quote and paren_level == 0:
                    token = "".join(buf).strip()
                    if token:
                        actions.append(token)
                    buf = []
                    continue

                buf.append(ch)
                if ch == "(" and not in_quote:
                    paren_level += 1
                elif ch == ")" and not in_quote and paren_level > 0:
                    paren_level -= 1

            last = "".join(buf).strip()
            if last:
                actions.append(last)

            return actions
        except Exception as ex:
            logger.error(f"Error parsing actions string '{action}': {ex}", exc_info=True)
            return []


    # def executeAction(self, actions, action):
    #     """
    #     Execute a single action by name, with optional parameters.
    #     Returns the result as a string, or None if the action is not found or an error occurs.
    #     """
    #     try:
    #         if "(" in action and ")" in action:
    #             name, params = action.split("(", 1)
    #             params       = params.rstrip(")").strip()
    #             args, kwargs = self.parseActions(params)
    #         else:
    #             name, args, kwargs = action.strip(), [], {}

    #         func = actions.get(name)
    #         if not func:
    #             return None

    #         result = func(**kwargs) if kwargs else (func(*args) if args else func())
    #         if isinstance(result, list):
    #             return "\n".join(map(str, result))
    #         if isinstance(result, dict):
    #             return str(result)
    #         return result
    #     except Exception as ex:
    #         logger.error(f"Error executing action '{action}'", exc_info=True)
    #         return f"Error executing action '{action}', {ex}" #str(ex)

    # def executeActions(self, actions, actionList):
    #     """
    #     Execute a list of actions, each potentially with parameters.
    #     Returns a list of results, one for each action.
    #     If an action is not found or errors, its result will be None.
    #     """
    #     if isinstance(actionList, str):
    #         actionList = [a.strip() for a in actionList.strip().splitlines() if a.strip()]
    #     results = []
    #     for action in actionList:
    #         try:
    #             if "(" in action and ")" in action:
    #                 name, params = action.split("(", 1)
    #                 params       = params.rstrip(")").strip()
    #                 args, kwargs = self.parseActions(params)
    #             else:
    #                 name, args, kwargs = action.strip(), [], {}
    #             func = actions.get(name)
    #             if not func:
    #                 results.append(None)
    #                 continue
    #             sig = inspect.signature(func)
    #             if kwargs and any(
    #                 p.kind == inspect.Parameter.VAR_KEYWORD or p.name in kwargs
    #                 for p in sig.parameters.values()
    #             ):
    #                 result = func(**kwargs)
    #             elif args:
    #                 result = func(*args)
    #             else:
    #                 result = func()
    #             if isinstance(result, list):
    #                 results.append("\n".join(map(str, result)))
    #             elif isinstance(result, dict):
    #                 results.append(str(result))
    #             else:
    #                 results.append(result)
    #         except Exception as ex:
    #             logger.error(f"Error executing action '{action}'", exc_info=True)
    #             results.append(str(ex))
    #     return results
    def executeAction(self, actions, action):
        """
        Execute a single action by name, with optional parameters.
        Returns the result as a string, or an error string if actions is not a dict or an error occurs.
        """
        if not hasattr(actions, 'get'):
            logger.error(f"Actions must be a dict-like object, got {type(actions).__name__}")
            return f"Error: actions is not a dict, got {type(actions).__name__}"
        try:
            if "(" in action and ")" in action:
                name, params = action.split("(", 1)
                params       = params.rstrip(")").strip()
                args, kwargs = self.parseActions(params)
            else:
                name, args, kwargs = action.strip(), [], {}

            func = actions.get(name)
            if not func:
                return None

            result = func(**kwargs) if kwargs else (func(*args) if args else func())
            if isinstance(result, list):
                return "\n".join(map(str, result))
            if isinstance(result, dict):
                return str(result)
            return result
        except Exception as ex:
            logger.error(f"Error executing action '{action}'", exc_info=True)
            return f"Error executing action '{action}', {ex}"

    def executeActions(self, actions, actionList):
        """
        Execute a list of actions, each potentially with parameters.
        Returns a list of results, one for each action, or error strings if actions is not a dict.
        """
        if not hasattr(actions, 'get'):
            logger.error(f"Actions must be a dict-like object, got {type(actions).__name__}")
            return [f"Error: actions is not a dict, got {type(actions).__name__}"] * (len(actionList) if actionList else 1)
        if isinstance(actionList, str):
            actionList = [a.strip() for a in actionList.strip().splitlines() if a.strip()]
        results = []
        for action in actionList:
            try:
                if "(" in action and ")" in action:
                    name, params = action.split("(", 1)
                    params       = params.rstrip(")").strip()
                    args, kwargs = self.parseActions(params)
                else:
                    name, args, kwargs = action.strip(), [], {}
                func = actions.get(name)
                if not func:
                    results.append(None)
                    continue
                sig = inspect.signature(func)
                if kwargs and any(
                    p.kind == inspect.Parameter.VAR_KEYWORD or p.name in kwargs
                    for p in sig.parameters.values()
                ):
                    result = func(**kwargs)
                elif args:
                    result = func(*args)
                else:
                    result = func()
                if isinstance(result, list):
                    results.append("\n".join(map(str, result)))
                elif isinstance(result, dict):
                    results.append(str(result))
                else:
                    results.append(result)
            except Exception as ex:
                logger.error(f"Error executing action '{action}'", exc_info=True)
                results.append(str(ex))
        return results

    def executeTool(self, name, tools, args, threshold=80, retry=False):
        """
        Call a tool by its name, auto-fixing missing argument names using fuzzy matching if needed.
        - threshold: Minimum match score for fuzzy correction.
        - retry: Whether to retry the tool call with corrected args.
        """
        if name not in tools:
            return f"Function '{name}' not found."
        func = tools[name]
        sig = inspect.signature(func)
        params = sig.parameters
        required = [
            pname for pname, p in params.items()
            if p.default is p.empty and p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)
        ]

        # Step 1: Filter arguments to valid param names
        filtered_args = {k: v for k, v in args.items() if k in params}

        # Step 2: Detect missing required arguments
        missing = [p for p in required if p not in filtered_args]

        # Step 3: Fuzzy-correct missing arguments
        corrections = {}
        for miss in missing:
            matches = process.extractOne(
                miss, args.keys(), scorer=fuzz.ratio, score_cutoff=threshold
            )
            if matches:
                matched_arg, score = matches[0], matches[1]
                corrections[miss] = matched_arg

        # Step 4: If corrections found, auto-fix and retry
        if corrections and retry:
            fixed_args = filtered_args.copy()
            for correct_name, supplied_name in corrections.items():
                fixed_args[correct_name] = args[supplied_name]
            # Remove the fuzzy-matched keys to avoid dupes
            for supplied_name in corrections.values():
                fixed_args.pop(supplied_name, None)
            try:
                result = func(**fixed_args)
                return {
                    "result": result,
                    "fixes": corrections,
                    "info": f"Arguments auto-corrected: {corrections}"
                }
            except Exception as e:
                return {
                    "error": str(e),
                    "fixes": corrections,
                    "info": f"Auto-retry failed after correcting arguments: {corrections}"
                }

        # Step 5: If still missing required, or no corrections, error out
        still_missing = [p for p in required if p not in filtered_args and p not in corrections]
        if still_missing:
            return {
                "error": f"Missing required argument(s): {', '.join(still_missing)}",
                "suggestion": f"Tried correction, fixed: {corrections}" if corrections else None
            }

        # Step 6: Standard call if all good
        try:
            return func(**filtered_args)
        except Exception as e:
            return f"Error running '{name}': {e}"

    def parseActions(self, paramString: str) -> tuple:
        args, kwargs = [], {}
        if not paramString:
            return args, kwargs

        parts = self._splitParameters(paramString)
        for p in parts:
            parsed = self._parseParameters(p)
            if isinstance(parsed, tuple):
                k, v = parsed
                kwargs[k] = v
            else:
                args.append(parsed)
        return args, kwargs

    def _splitParameters(self, s: str) -> list:
        lst = []
        buf = []
        lvl = 0
        for ch in s:
            if ch == ',' and lvl == 0:
                token = ''.join(buf).strip()
                if token: lst.append(token)
                buf = []
            else:
                buf.append(ch)
                if ch == '(': lvl += 1
                elif ch == ')' and lvl > 0: lvl -= 1
        last = ''.join(buf).strip()
        if last: lst.append(last)
        return lst

    def _parseParameters(self, p: str):
        if '=' in p:
            k, v = p.split('=', 1)
            k, v = k.strip(), v.strip()
            try:
                return k, ast.literal_eval(v)
            except:
                return k, v.strip("'\"")
        try:
            return ast.literal_eval(p)
        except:
            return p.strip("'\"")