

import inspect
import json
import threading
import logging
import re
from pathlib import Path
from google.genai import types
from HoloSync import HoloSync

from .HLLoader.Loader import Loader
from .HLParsers.ArgumentParser.ArgumentParser import ArgumentParser
from .HLParsers.ActionParser.ActionParser import ActionParser
from .HLParsers.SkillParser.SkillParser import SkillParser
from .HLParsers.ToolParser.ToolParser import ToolParser
#from .HLPackageManager.PackageManager import PackageManager
from HoloViro import HoloViro
from .HLSkillMover.SkillMover import SkillMover
from .HLUtils.Utils import *

logger = logging.getLogger(__name__)


class HoloLink:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(HoloLink, cls).__new__(cls)
        return cls._instance

    def __init__(self, autoReload=False, cycleInterval=60): # test as False normally set to True
        if getattr(self, 'initialized', False):
            return
        self._initComponents(autoReload, cycleInterval)
        self.initialized = True

    def _initComponents(self, autoReload, cycleInterval):
        self.loader               = Loader()
        self.actionParser         = ActionParser()
        self.argParser            = ArgumentParser()
        self.skillsMover          = SkillMover()
        self.autoReload           = autoReload
        self.cycleInterval        = cycleInterval
        self.useThreading         = False
        self.timer                = None
        self.skillExamples        = None
        self.reloadableComponents = []
        if self.autoReload:
            self.reloadTimer()

    def setThreading(self, useThreading: bool=False) -> None:
        """
        Set whether to use threading for loading skills.
        If useThreading is True, skills will be loaded in a separate thread.
        If False, skills will be loaded in the main thread.
        WARNING: In most cases, threading will not speed up skill loading and may slow it down! also, it can cause issues with skills that rely on synchronous execution.
        """
        self.useThreading = useThreading

    def getDir(self, *paths):
        """
        Returns the absolute path of the given paths.
        """
        return str(Path(*paths).resolve())

    def setAutoReload(self, autoReload: bool=False, cycleInterval: int=None) -> None:
        """
        Set whether to automatically reload skills after a certain interval.
        If autoReload is True, starts the timer for reloading skills.
        If False, stops the timer if it is running.
        """
        self.cycleInterval = cycleInterval if cycleInterval is not None else self.cycleInterval
        self.autoReload = autoReload
        if self.autoReload:
            self.reloadTimer()
        elif self.timer:
            self.timer.cancel()
            self.timer = None

    def setEnvDir(self, envDir: str=None) -> None:
        """
        Set the directory for the virtual environment.
        This is used to load skills from a specific environment.
        """
        HoloViro().setEnvDir(envDir)

    def loadComponents(self, paths: list=None, components: list=None, reloadable: list=None, useThreading: bool=None, cycleInterval: int=None):
        """
        Load multiple component groups by passing parallel lists:
        - paths:       list of path lists
        - components:  list of component lists
        - reloadable:  list of bools (optional, defaults to all False)
        - useThreading: bool, whether to use threading for loading (optional, defaults to self.useThreading=False)
        - cycleInterval: int, interval in seconds for auto-reloading (optional, defaults to self.cycleInterval=60)
        WARNING: In most cases, threading will not speed up skill loading and may slow it down! also, it can cause issues with skills that rely on synchronous execution.
        """
        if not paths or not components:
            raise ValueError("Both 'paths' and 'components' are required.")
        if len(paths) != len(components):
            raise ValueError("'paths' and 'components' must be the same length.")
        reloadable = reloadable or [False] * len(paths)
        if len(reloadable) != len(paths):
            raise ValueError("'reloadable' must be the same length as 'paths' and 'components'.")
        #ut = useThreading or self.useThreading
        ut = self.useThreading if useThreading is None else useThreading
        for p, c, r in zip(paths, components, reloadable):
            for path in p or []:
                self.loadSkills(path, c, ut)
            if r and (c, p) not in self.reloadableComponents:
                self.reloadableComponents.append((c, p))
        #cycleInterval = cycleInterval or self.cycleInterval
        cycleInterval = self.cycleInterval if cycleInterval is None else cycleInterval
        self.setAutoReload(bool(self.reloadableComponents), cycleInterval)

    def loadSkills(self, source, component=None, useThreading: bool=None):
        ut = self.useThreading if useThreading is None else useThreading
        return self.loader.loadSkills(source, component, ut)

    def reloadTimer(self):
        """
        Starts or restarts the timer for auto-reloading skills.
        If a timer is already running, it cancels it first.
        """
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(self.cycleInterval, self.reloadSkills)
        self.timer.start()

    def reloadSkills(self):
        """
        Reload all registered reloadable skill components,
        update metadata, and restart the timer.
        """
        # if not self.reloadableComponents:
        #     return
        # Reload all registered reloadable skill components
        if self.reloadableComponents:
            for component, paths in self.reloadableComponents:
                component.clear()
                for path in paths or []:
                    self.loadSkills(path, component)

        if self.autoReload:
            self.reloadTimer()

    def getComponents(self, skills, content= None):
        """
        Returns actions or executes an action depending on the arguments.
        - If content is provided, executes actions on the skills with that content.
        - If content is None, returns a dict of all available actions.
        """
        if content is not None:
            return self.getUserActions(skills, content)
        return self.getSelfActions(skills)

    def getUserActions(self, skills, content):
        """
        Runs executeAction(content) on the first skill that returns a result.
        'skills' must be a list of skill objects to check.
        """
        # Flatten skills in case someone passes a list of lists/tuples
        flat_skills = []
        for group in skills:
            if isinstance(group, (list, tuple)):
                flat_skills.extend(group)
            else:
                flat_skills.append(group)
        for executor in flat_skills:
            action = executor.executeAction(content)
            if action is not None:
                return action
        return None

    def getSelfActions(self, skills):
        """
        Returns a dict of action methods from the given skill(s).
        Accepts a single skill instance or a list/tuple of skills.
        """
        if not isinstance(skills, (list, tuple)):
            skills = [skills]

        graph = {}
        for skill in skills:
            for name, method in inspect.getmembers(
                skill,
                predicate=lambda m: inspect.ismethod(m) or inspect.isfunction(m)
            ):
                if name.startswith("_"):
                    continue
                graph[name] = method
        return graph

    def getMetaData(self, skillGroups=None, printMetaData=False):
        """
        Returns a list of metadata dictionaries for the given skill groups.
        If skillGroups is None, defaults to all skills ending with 'Skills' in the class.
        If printMetaData is True, prints the metadata to the console.
        """
        if skillGroups is None:
            skillGroups = [
                getattr(self, name) for name in dir(self)
                if name.endswith('Skills') and isinstance(getattr(self, name), list)
            ]
        # Flatten if list of lists
        if isinstance(skillGroups, (list, tuple)):
            skills = []
            for group in skillGroups:
                if isinstance(group, (list, tuple)):
                    skills.extend(group)
                else:
                    skills.append(group)
        else:
            skills = [skillGroups]

        metaList = []
        for comp in skills:
            # Try both _metaData and _metadata (case-insensitive)
            metaMethod = next(
                (getattr(comp, methodName) for methodName in ['_metaData', '_metadata']
                 if hasattr(comp, methodName) and callable(getattr(comp, methodName))),
                None
            )
            if metaMethod:
                md = metaMethod()
                metaList.append({
                    "className": md.get("className", "Unknown"),
                    "description": f"Allows me to {md.get('description','').lower()}"
                })

        if printMetaData:
            self.printMetaDataInfo(metaList)
        return metaList

    def parseCapabilities(self, skills, description = True):
        """
        Parses the capabilities of the given skills and returns a list of capabilities.
        If skills is a single skill, it will be wrapped in a list.
        If description is True, it get information about the capabilities from the docstring.
        """
        return SkillParser.parseCapabilities(skills, description)

    def checkActions(self, action: str) -> str:
        """
        Checks if the given action string matches any of the available actions.
        If the action string is empty, it returns a message indicating that no action was provided.
        If the action string matches an available action, it returns the action string.
        If the action string does not match any available actions, it returns None.
        """
        return self.actionParser.checkActions(action)

    def getActions(self, action: str) -> list:
        """
        Returns a list of actions that match the given action string.
        If the action string is empty, it returns all available actions.
        """
        return self.actionParser.getActions(action)

    def calledActions(self, caller: str, localVars: dict) -> None:
        """
        Prints the actions called by the given caller with the provided local variables.
        This is useful for debugging and understanding the flow of actions in the code.
        Args:
            caller (str): The name of the caller (usually the class or function name).
            localVars (dict): The local variables available in the caller's scope.
        """
        return self.argParser.calledActions(caller, localVars)

    def executeAction(self, actions, action):
        """
        Executes a single action from the list of actions.
        If the action is not found, it returns None.
        """
        return self.actionParser.executeAction(actions, action)

    def executeActions(self, actions, action):
        """
        Executes a single action or multiple actions from the list of actions.
        It will execute each action in the list in a for loop, if the action is a list.
        If the action is not found, it returns None.
        """
        return self.actionParser.executeActions(actions, action)

    # def executeSkill(self, name, *args):
    #     """
    #     Executes a skill action based on the provided name and arguments.
    #     Args:
    #         name (str): The name of who the skill/action is executed by (e.g., 'agent', 'assistant', 'system', 'user').
    #         *args: Variable length argument list for the skill action.
    #     Returns:
    #         The result of the skill action execution.
    #     Raises:
    #         ValueError: If the skill action name is unknown.
    #     """
    #     dispatchers = {
    #         "self":      self.systemDispatcher,
    #         "system":    self.systemDispatcher,
    #         "agent":     self.systemDispatcher,
    #         "assistant": self.systemDispatcher,
    #         "user":      self.userDispatcher
    #     }
    #     try:
    #         return dispatchers[name.lower()](*args)
    #     except KeyError:
    #         publicNames = [k for k in dispatchers if k != "self"]
    #         raise ValueError(f"Unknown dispatcher name: {name}. Must be one of: {publicNames}")
    def executeSkill(self, name, *args):
        """
        Executes a skill action based on the provided name and arguments.
        Args:
            name (str): The role or executor ('agent', 'assistant', 'system', 'user').
            *args: Arguments for the skill/action.
        Returns:
            The result of the skill action execution.
        Raises:
            ValueError: If the skill action name is unknown.
        """
        dispatchers = {
            "system": self.systemDispatcher,
            "user": self.userDispatcher
        }
        # All aliases point to canonical dispatcher keys
        aliases = {
            "self": "system",
            "agent": "system",
            "assistant": "system"
        }
        # Compose list of all accepted names for error/help (excluding "self")
        validNames = list(dispatchers.keys()) + [k for k in aliases if k != "self"]

        key = name.lower()
        key = aliases.get(key, key)
        try:
            return dispatchers[key](*args)
        except KeyError:
            raise ValueError(f"Unknown dispatcher name: {name}. Must be one of: {validNames}")

    def systemDispatcher(self, name, actionMap, action: str, *args):
        """
        Description: Executes the requested action for system management based on the actionMap.
        """
        try:
            actionKey = actionMap.get(action.lower())
            if not actionKey:
                return f"Invalid {name} Action: {action}"

            # pull out the real skill instance
            skillObj = getattr(actionKey, "__self__", actionKey)
            func_name = actionKey.__name__
            sig       = inspect.signature(actionKey)

            listSig = self.argParser.getListSig(skillObj, func_name) or []
            dictSig = self.argParser.getDictSig(skillObj, func_name) or {}

            # LIST dispatch (with fragmented‐JSON recovery)
            if listSig:
                _args = list(args)
                if len(_args) > 1 and _args[0].startswith("[") and _args[-1].endswith("]"):
                    try:
                        joined   = '","'.join(_args)
                        possible = json.loads(joined)
                        if isinstance(possible, list):
                            _args = possible
                    except:
                        pass
                elif len(_args) == 1 and isinstance(_args[0], str):
                    try:
                        possible = json.loads(_args[0])
                        if isinstance(possible, list):
                            _args = possible
                    except:
                        pass
                return actionKey(_args)

            # DICT dispatch (with fragmented‐JSON recovery)
            if dictSig:
                keys  = list(dictSig.keys())
                _args = list(args)

                # 1) fragmented JSON dict?
                if len(_args) > 1 and _args[0].startswith("{") and _args[-1].endswith("}"):
                    try:
                        joined   = '","'.join(_args)
                        possible = json.loads(joined)
                        if isinstance(possible, dict):
                            _args = [possible.get(k) for k in keys]
                    except:
                        pass

                # 2) single JSON string?
                elif len(_args) == 1 and isinstance(_args[0], str):
                    try:
                        possible = json.loads(_args[0])
                        if isinstance(possible, dict):
                            _args = [possible.get(k) for k in keys]
                    except:
                        pass

                info = dict(zip(keys, _args))
                return actionKey(info)

            # positional fallback
            return actionKey(*args[:len(sig.parameters)])

        except Exception as e:
            logger.error(f"Error executing {name} with: {action}", exc_info=True)
            return f"Error: {e}"

    def userDispatcher(self, name, actionMap, ctx: str) -> str:
        """
        Description: Executes the requested action for date/time management based on context.
        """
        try:
            action = ctx.lower()
            actionKey = next((key for key in actionMap if key in action), None)
            if not actionKey:
                return None
            args = action.replace(actionKey, "", 1).strip()
            return actionMap[actionKey](args)
        except Exception as e:
            logger.error(f"Error executing {name} with: {ctx}", exc_info=True)
            return f"Error: {e}"

    def getSkills(self, skillList: list, printSkills: bool = False, description: bool = False):
        """
        Returns a human-readable list of skills for the given skill(s).
        If skillList is a single skill, it will be wrapped in a list.
        If printSkills is True, it will print the skills to the console.
        If description is True, it will parse the skills docstrings for more information.
        """
        return self.getCapabilities(skillList, printSkills, description)

    def getCapabilities(self, skillList: list, printSkills: bool = False, description: bool = False):
        """
        Returns a human-readable list of capabilities for the given skill(s).
        If skillList is a single skill, it will be wrapped in a list.
        If printSkills is True, it will print the capabilities to the console.
        If description is True, it will parse the capabilities docstrings for more information.
        """
        skills = skillList if isinstance(skillList, list) else [skillList]
        caps = self.parseCapabilities(skills, description)
        if printSkills:
            self.printSkillInfo(caps)
        self.skillExamples = "\n\n".join(caps)
        return "\n\n".join(caps)



    # Skill Mover methods
    def setMoveDirs(self, primarySkillDir=None, primaryDynamicDir=None, primaryStaticDir=None,
                secondarySkillDir=None, secondaryDynamicDir=None, secondaryStaticDir=None):
        """
        Configure directory pairs for file moving operations.
        Only the pairs you want to use need to be set (both source and destination).
        """
        self.skillsMover.setMoveDirs(primarySkillDir, primaryDynamicDir, primaryStaticDir,
                                     secondarySkillDir, secondaryDynamicDir, secondaryStaticDir)

    def setMoveSettings(self, storageUnit="days", storageValue=7, 
                    checkInterval=10, noMoveLimit=3):
        """
        Set storage/move timing and check parameters.
        """
        self.skillsMover.setMoveSettings(storageUnit, storageValue, checkInterval, noMoveLimit)

    def manualMove(self, sourceDir, destinationDir, minAge=None):
        """
        Immediately move eligible files from sourceDir to destinationDir.
        
        Args:
            sourceDir (str): Directory to move files from.
            destinationDir (str): Directory to move files to.
            minAge (timedelta, optional): Only move files older than this age.
                                          If None, move all files.
        Returns:
            int: Number of files moved.
        """
        return self.skillsMover.manualMove(sourceDir, destinationDir, minAge)

    def autoMove(self):
        """
        Start all monitor threads for file moves.
        """
        self.skillsMover.autoMove()



    # Action and Skill Examples
    def actionInstructions(self, capabilities: list, examples: str = None, limit: int=None, verbose: bool=False):
        if examples is None:
            examples = self.generateExamples(self.skillExamples, limit=limit, verbose=False)
        instructions = (
            f"You determine the best course of action. "
            f"Select the most logical action(s) from the list below:\n\n{capabilities}\n\n"
            "If more than one action is required, list them in the exact order of execution, separated by commas. "
            "For actions requiring context or content, use what the user said. "
            "If no action is necessary, respond only with 'None'. "
            "Respond only with the exact name(s) or 'None'. No extra text or explanation is allowed.\n\n"

            "Examples:\n"
            "No Action Needed Example:\n"
            "- If no action is needed, respond with: None\n"
            f"{examples}\n"
        )
        if verbose:
            print(instructions)
        return instructions

    def skillInstructions(self, capabilities: list, examples: str = None, limit: int=None, verbose: bool=False):
        if examples is None:
            examples = self.generateExamples(self.skillExamples, limit=limit, verbose=False)
        instructions = (
            f"You determine the best course of action. "
            f"Select the most logical skill(s) or action(s) from the list below:\n\n{capabilities}\n\n"
            "If more than one skill or action is required, list them in the exact order of execution, separated by commas. "
            "For actions requiring context or content, use what the user said. "
            "If no action is necessary, respond only with 'None'. "
            "Respond only with the exact name(s) or 'None'. No extra text or explanation is allowed.\n\n"

            "Examples:\n"
            "No Skill or Action Needed Example:\n"
            "- If no skill or action is needed, respond with: None\n"
            f"{examples}\n"
        )
        if verbose:
            print(instructions)
        return instructions

    def generateExamples(self, capabilities: str, limit: int=None, verbose: bool=False):
        capabilities_str = capabilities.strip()
        typeExampleMap = {
            'int':   '1',
            'float': '1.23',
            'list':  '["item1", "item2"]',
            'dict':  '{"key": "value"}',
            'bool':  'True or False',
        }

        singles, subactions, multis = [], [], []
        seen_skills_no_param = set()
        seen_skills_with_param = set()
        seen_multis = set()

        blocks = re.split(r'(?=^[a-zA-Z_][a-zA-Z0-9_]*\s*\()', capabilities_str, flags=re.MULTILINE)
        for block in blocks:
            block = block.strip()
            if not block:
                continue

            # Standalone function (not skill)
            func_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\(([^)]*)\):', block)
            skill_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\(action: str, \*args\):', block)
            if func_match and not skill_match:
                func = func_match.group(1)
                params_str = func_match.group(2)
                params = []
                if params_str:
                    for param_decl in params_str.split(','):
                        param_decl = param_decl.strip()
                        if not param_decl:
                            continue
                        param_parts = re.match(r'(\w+):\s*(\w+)', param_decl)
                        if param_parts:
                            param, param_type = param_parts.groups()
                            if param_type == 'str':
                                params.append(f'\\"{param}\\"')
                            elif param_type in typeExampleMap:
                                params.append(typeExampleMap[param_type])
                            else:
                                params.append(f'{param} ({param_type})')
                call = f"{func}(" + ", ".join(params) + ")"
                singles.append(f"['{call}']")
                continue

            # Skill+action block
            if skill_match:
                skill = skill_match.group(1)
                action_matches = list(re.finditer(
                    r'- ([\w-]+):\n((?:\s{2,}(?:Required|Optional):.*(?:\n(?!\s{2,}-(?: [\w-]+):))*)*)',
                    block
                ))
                action_calls = []
                for match in action_matches:
                    action = match.group(1)
                    params_block = match.group(2)
                    params = []
                    required_lines = re.findall(r'Required:\s*([^\n]+)', params_block)
                    for line in required_lines:
                        for param, param_type in re.findall(r'(\w+)\s*\((\w+)\)', line):
                            if param_type == "dict":
                                dict_match = re.search(
                                    rf'{param} \(dict\)\n\s+Dict Signature:\n((?:\s+\w+: \w+\n)+)', params_block)
                                if dict_match:
                                    dict_fields = re.findall(r'\s+(\w+): (\w+)', dict_match.group(1))
                                    dict_param = '{' + ', '.join(
                                        f'{k}: {typeExampleMap.get(t, f"{k} ({t})")}' for k, t in dict_fields
                                    ) + '}'
                                    params.append(dict_param)
                                else:
                                    params.append(typeExampleMap['dict'])
                            elif param_type == 'str':
                                params.append(f'\\"{param}\\"')
                            elif param_type in typeExampleMap:
                                params.append(typeExampleMap[param_type])
                            else:
                                params.append(f'{param} ({param_type})')
                    call = f'{skill}(\\"{action}\\"' + (", " + ", ".join(params) if params else "") + ")"
                    action_calls.append((call, len(params) > 0))
                # Add first NO-param action for this skill
                for call, has_param in action_calls:
                    if not has_param and skill not in seen_skills_no_param:
                        subactions.append(f"['{call}']")
                        seen_skills_no_param.add(skill)
                        break  # Only one no-param per skill
                # Add first WITH-param action for this skill
                for call, has_param in action_calls:
                    if has_param and skill not in seen_skills_with_param:
                        subactions.append(f"['{call}']")
                        seen_skills_with_param.add(skill)
                        break  # Only one with-param per skill
                # Multi examples: from all actions with params, but only first unique pair
                param_calls = [call for call, has_param in action_calls if has_param]
                if len(param_calls) >= 2:
                    multi_key = tuple(param_calls[:2])
                    if multi_key not in seen_multis:
                        multis.append(f"[{', '.join(f'\'{x}\'' for x in param_calls[:2])}]")
                        seen_multis.add(multi_key)

        # Truncate if limit is set
        if limit is not None:
            singles = singles[:limit]
            subactions = subactions[:limit]
            multis = multis[:limit]

        # Format output
        out = "Single Action Examples:\n"
        if not singles:
            out += "- ['funcName()'], ['func_name()']\n"
        else:
            for ex in singles:
                out += f"- {ex}\n"
        out += "Skill With Sub-Action Examples:\n"
        if not subactions:
            out += "\n"
        else:
            for ex in subactions:
                out += f"- {ex}\n"
        out += "Skill With Multi Sub-Action Examples:\n"
        if not multis:
            out += "\n"
        else:
            for ex in multis:
                out += f"- {ex}\n"

        if verbose:
            print(out)
        return out

    # Can be used with both skills and tools
    def isStructured(self, *args):
        """
        Check if any of the arguments is a list of dictionaries.
        This indicates structured input (multi-message format).
        """
        return isStructured(*args)

    def handleTypedFormat(self, role: str = "user", content: str = ""):
        """
        Format content for Google GenAI APIs.
        """
        return handleTypedFormat(role, content)

    def handleJsonFormat(self, role: str = "user", content: str = ""):
        """
        Format content for OpenAI APIs and similar JSON-based APIs.
        """
        return handleJsonFormat(role, content)

    def formatTypedExamples(self, items):
        """
        Format a list of items into a Google GenAI compatible format.
        Each item should be a dictionary with 'role' and 'content' keys.
        """
        return formatTypedExamples(items)

    def formatJsonExamples(self, items):
        """
        Format a list of items into a JSON-compatible format.
        Each item should be a dictionary with 'role' and 'content' keys.
        """
        return formatJsonExamples(items)

    def formatExamples(self, items, formatFunc):
        """
        Format a list of items using the provided format function.
        Each item should be a dictionary with 'role' and 'content' keys.
        """
        return formatExamples(items, formatFunc)

    def handleTypedExamples(self, items):
        """
        Format a list of items into a Google GenAI compatible format.
        Each item should be a dictionary with 'role' and 'content' keys.
        """
        return handleTypedExamples(items)

    def handleJsonExamples(self, items):
        """
        Format a list of items into a JSON-compatible format.
        Each item should be a dictionary with 'role' and 'content' keys.
        """
        return handleJsonExamples(items)

    def handleExamples(self, items, formatFunc):
        """
        Format a list of items using the provided format function.
        Each item should be a dictionary with 'role' and 'content' keys.
        """
        return handleExamples(items, formatFunc)
        

    def buildGoogleSafetySettings(self, harassment="BLOCK_NONE", hateSpeech="BLOCK_NONE", sexuallyExplicit="BLOCK_NONE", dangerousContent="BLOCK_NONE"):
        """
        Construct a list of Google GenAI SafetySetting objects.
        """
        return buildGoogleSafetySettings(harassment, hateSpeech, sexuallyExplicit, dangerousContent)



    # Everything below this point is related to tools
    def getTools(self, toolList: list, printTools: bool = False, schemaType: str = None) -> dict:
        """
        Parses a list of tools (modules, functions, or classes) to extract callable tools.
        Returns a dictionary of tool names to their callable objects.
        If a skill is a module, it extracts all functions defined in that module.
        """
        tools = ToolParser.getTools(toolList)

        if printTools:
            self.printTools(tools, schemaType)
            
        return tools

    def parseTools(self, docstring):
        """
        Parses a docstring to extract tool metadata, including name, description, and parameters.
        """
        return ToolParser.parseToolDocstring(docstring)

    def extractJson(self, text):
        """
        Extract the first JSON array or object from a string, even if wrapped in markdown or extra commentary.
        """
        return ToolParser.extractJson(text)

    def getTypedSchema(self, func):
        """
        Build a Google GenAI function declaration for a given function based on its signature and docstring metadata.
        Returns a FunctionDeclaration object.
        """
        return ToolParser.parseTypedSchema(func)

    def getJsonSchema(self, func, schemaType="responses"):
        """
        Build a JSON schema for a function based on its signature and docstring metadata.
        The schemaType can be either 'chat_completions' or 'responses'.

        Returns a dictionary representing the schema.
        """
        return ToolParser.parseJsonSchema(func, schemaType)

    def executeTool(self, name, tools, args, threshold=80, retry=False):
        """
        Call a tool by its name, auto-fixing missing argument names using fuzzy matching if needed.
        - threshold: Minimum match score for fuzzy correction.
        - retry: Whether to retry the tool call with corrected args.
        """
        return self.actionParser.executeTool(name, tools, args, threshold, retry)

    def getJsonTools(self, toolList, schemaType="responses"):
        """
        Returns a list of JSON schemas for the given toolList.
        If schemaType is 'chat_completions', it returns the OpenAI chat_completions schema.
        If schemaType is 'responses', it returns the OpenAI responses schema.
        If schemaType is None, it defaults to 'responses'.
        """
        tools = [self.getJsonSchema(f, schemaType) for f in toolList.values()]
        return tools, toolList

    # Will be implemented in the skillgraph package before moving to here
    def getTypedTools(self, toolList):
        """
        Returns a list of Google GenAI typed schemas for the given toolList.
        Each tool in the list is converted to a FunctionDeclaration object.
        """
        declarations = [self.getTypedSchema(f) for f in toolList.values()]
        tools = [types.Tool(function_declarations=declarations)]
        return tools, toolList


    # Print methods for debugging and information display
    def printSkillInfo(self, graph):
        print("Human-readable Format:")
        for item in graph:
            print("\n=== Capability ===\n")
            print(item)
            print("\n" + "=" * 50 + "\n")

        print("My-readable Format:")
        print(graph)

    def printMetaDataInfo(self, metaList):
        print("Human-readable Format:")
        for m in metaList:
            print(f"\n=== MetaData ===\n")
            print(f"Class: {m['className']} | Description: {m['description']}")
            print("\n" + "=" * 50 + "\n")

        print("My-readable Format:")
        print(metaList)

    def printTools(self, toolList: list, schemaType: str = None):
        """
        For each function in toolList, print:
          OpenAI completions schema
          OpenAI responses schema
          Google GenAI typed schema
        schemaType can be 'completions', 'responses', 'typed', or None (all)
        """
        schemaType = schemaType.lower() if schemaType else None
        if schemaType == "chat_completions":
            schemaType = "completions"
        SCHEMA_PRINTERS = {
            "completions": lambda name, fn: (
                print("completions schema:"),
                print(json.dumps(self.getJsonSchema(fn, "completions"), indent=2)),
                print("\n" + "-"*40)
            ),
            "responses": lambda name, fn: (
                print("responses schema:"),
                print(json.dumps(self.getJsonSchema(fn, "responses"), indent=2)),
                print("\n" + "-"*40)
            ),
            "typed": lambda name, fn: (
                print("typed schema:"),
                print(json.dumps(self._getTypedDict(self.getTypedSchema(fn)), indent=2)),
                print("\n" + "-"*40)
            ),
        }

        print("\n=== Tool Schemas ===")
        for name, fn in toolList.items():
            if schemaType in SCHEMA_PRINTERS:
                SCHEMA_PRINTERS[schemaType](name, fn)
            elif schemaType is None:
                SCHEMA_PRINTERS["completions"](name, fn)
                SCHEMA_PRINTERS["responses"](name, fn)
                SCHEMA_PRINTERS["typed"](name, fn)


    def _getTypedDict(self, typed):
        """
        Convert a Google GenAI typed schema into a dictionary format.
        This is used to convert FunctionDeclaration objects into a JSON‐serializable format.
        """
        if isinstance(typed, dict):
            return typed

        if isinstance(typed, types.FunctionDeclaration):
            params = typed.parameters
            props = {}
            for name, schema in params.properties.items():
                entry = {"type": schema.type.name}
                if schema.type == types.Type.ARRAY and getattr(schema, "items", None):
                    entry["items"] = {"type": schema.items.type.name}

                if schema.type == types.Type.OBJECT and getattr(schema, "properties", None):
                    nested = {}
                    for k, v in schema.properties.items():
                        nested[k] = {"type": v.type.name}
                    entry["properties"] = nested
                    if getattr(schema, "required", None):
                        entry["required"] = list(schema.required)

                props[name] = entry

            return {
                "name":        typed.name,
                "description": typed.description,
                "parameters": {
                    "type":       params.type.name,
                    "properties": props,
                    "required":   list(params.required)
                }
            }

        # fallback to pydantic/proto dumps
        if hasattr(typed, "model_dump"):
            return typed.model_dump(exclude_none=True, exclude_defaults=True, exclude_unset=True)
        if hasattr(typed, "dict"):
            return typed.dict(exclude_none=True, exclude_defaults=True, exclude_unset=True)

        # generic fallback
        return {
            "name":        typed.name,
            "description": typed.description,
            "parameters": {
                "type": "object",
                "properties": {
                    k: {"type": v.type.name.lower()}
                    for k, v in (typed.parameters.properties or {}).items()
                },
                "required": getattr(typed.parameters, "required", []) or []
            }
        }

