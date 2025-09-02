
import subprocess
import re
import os
import sys
import importlib
import time
import pyperclip
import pyautogui
from pathlib import Path
import venv
from dotenv import load_dotenv
import logging


logger = logging.getLogger(__name__)


class PackageManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PackageManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "initialized"):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.envDir   = None
        self.sitePath = None
        self.fileName = None

    def setEnvDir(self, envDir: str = None) -> None:
        if envDir is None:
            envDir = self._getDir("SkillsEnv")
        self.envDir = envDir
        self.createVirtualEnv()
        self.sitePath = self._getSitePackages()

    def _getSitePackages(self) -> str:
        try:
            return next(Path(self.envDir).rglob("site-packages"))
        except StopIteration:
            raise FileNotFoundError(f"No 'site-packages' found in virtual environment '{self.envDir}'")

    def importFromVenv(self, package: str) -> str:
        if str(self.sitePath) not in sys.path:
            sys.path.insert(0, str(self.sitePath))
        try:
            return importlib.import_module(package)
        except Exception as e:
            raise ImportError(f"Could not import '{package}' from virtual environment: {e}")

    def _getDir(self, *paths: str) -> str:
        return str(Path(*paths).resolve())

    def saveCode(self, code: str, codeDir: str) -> None:
        if not os.path.exists(codeDir):
            os.makedirs(codeDir)

        match = re.search(r"class (.+):", code)
        if not match:
            # print("No match found in the code.")
            # return
            raise ValueError("No class declaration found in the provided code.")

        name = match.group(1).lower()
        self.fileName = f"{name}.py"
        lines = code.splitlines()

        importLines = []
        bodyLines = []
        insideDocstring = False

        for line in lines:
            stripped = line.strip()

            # Handle multi-line docstring content
            if stripped.startswith("'''") or stripped.startswith('"""'):
                insideDocstring = not insideDocstring
                bodyLines.append(line)
                continue

            if not insideDocstring and (stripped.startswith("import ") or stripped.startswith("from ")):
                importLines.append(stripped)
            else:
                bodyLines.append(line)

        # Remove blank lines and sort imports (optional sorting)
        importLines = [line for line in importLines if line]

        # Build final output: blank line at top, grouped imports, two blank lines, then rest
        formattedCode = "\n" + "\n".join(importLines) + "\n\n\n" + "\n".join(bodyLines).lstrip()
        formattedCode = self.fixDocstringIndentation(formattedCode)

        with open(rf"{codeDir}\{name}.py", "w", encoding="utf-8") as file:
            file.write(formattedCode)
        return self.fileName

    def extractSegments(self, codeBlock: str, pipInstalls: bool = False) -> str:
        try:
            pattern_backticks = r"```(?:python|bash)?\n(.*?)```"
            pattern_python_code = r"(^(?:from|import|class|def)\b[\s\S]+?(?=^(?:from|import|class|def)\b|\Z))"
            pip_install_pattern = r"pip install ([\w\s,-]+)"

            matches_backticks = re.findall(pattern_backticks, codeBlock, re.DOTALL)
            matches_python_code = re.findall(pattern_python_code, codeBlock, re.MULTILINE)

            extracted_segments = matches_backticks + matches_python_code

            if pipInstalls:
                pip_installs = re.findall(pip_install_pattern, codeBlock)
                for install_line in pip_installs:
                    if install_line.strip().lower() == "none":
                        continue
                    packages = [pkg.strip() for pkg in install_line.split(',') if pkg.strip().lower() != "none"]
                    for package in packages:
                        if package:
                            self.pipInstall(package)

            return '\n\n'.join(extracted_segments)

        except Exception as e:
            logger.error(f"Error extracting segments:", exc_info=True)
            return ""

    def fixDocstringIndentation(self, codeBlock: str) -> str:
        pattern = re.compile(r"(Args:\n(?:\s+.+?: .+?\n)+)", re.MULTILINE)

        def reindent(match):
            section = match.group(1)
            lines = section.strip().splitlines()
            fixed = []

            for line in lines:
                if ":" in line:
                    fixed.append(line)
                else:
                    # Continuation line
                    fixed.append(" " * 22 + line.strip())
            return "\n".join(fixed) + "\n"

        return pattern.sub(reindent, codeBlock)

    def pipInstall(self, package: str) -> None:
        packageName = package.strip().split()[-1]
        try:
            self.importFromVenv(packageName)
            print(f"Package '{packageName}' is already installed in venv.")
        except ImportError:
            print(f"Installing '{packageName}' to virtual environment...")
            self.installPackage(packageName)

    def createVirtualEnv(self):
        if not os.path.exists(self.envDir):
            print(f"Creating virtual environment at:\n'{self.envDir}'.")
            my_env = os.environ.copy()
            subprocess.check_call(
                ["uv", "venv", self.envDir],
                env=my_env,
                stdout=subprocess.DEVNULL,   # Suppress normal output
                stderr=subprocess.STDOUT     # Suppress errors as well, optional
            )

    def installPackage(self, package: str) -> bool:
        my_env = os.environ.copy()
        my_env["VIRTUAL_ENV"] = self.envDir  # Ensures uv installs to your venv

        try:
            subprocess.check_call(["uv", "pip", "install", package], env=my_env)
            print(f"Package '{package}' installed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install package '{package}': {e}")
            return False

    def enterCode(self, code: str) -> None:
        # Method to enter code into Notepad
        subprocess.Popen(['notepad.exe'])
        time.sleep(1)
        pyperclip.copy(code)
        pyautogui.hotkey('ctrl', 'v')
