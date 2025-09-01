"""Reasoning Engine creation with robust venv lifecycle and safe imports.

This module provides a `ReasoningEngineCreator` that:
- Creates an isolated virtual environment per engine build
- Installs dependencies using the *venv's* interpreter (`python -m pip`)
- Temporarily exposes the venv's site-packages to the current process for imports
- Emulates activation for subprocesses via PATH/VIRTUAL_ENV
- Stages a clean copy of the agent directory as an extra package
- Cleans up the venv after completion

Pass a config dict to `create_advanced_engine` with keys:
- display_name (str)
- description (str, optional)
- enable_tracing (bool, optional)
- requirements_source_type ("file" | "text")
- requirements_file (str, optional when source_type == "file")
- requirements_text (str, optional when source_type == "text")
- agent_file_path (str, path to the python file exporting `root_agent`)
- project_id, location, staging_bucket should be supplied to the constructor
"""
from __future__ import annotations

import importlib
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import venv
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vertexai import init as vertexai_init
from vertexai.preview.reasoning_engines import AdkApp
from vertexai import agent_engines

# --- helpers for clean packaging ---
EXCLUDES = [
    ".env",
    ".env.*",
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".DS_Store",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".venv",
    "venv",
    "tests",
    "docs",
]


class ReasoningEngineCreator:
    """
    Dedicated class for creating reasoning engines with advanced virtual environment management.
    Handles all the complex logic for venv creation, dependency installation, and deployment.
    """

    def __init__(self, project_id: str, location: str, staging_bucket: str, debug: bool = False):
        self.project_id = project_id
        self.location = location
        self.staging_bucket = staging_bucket
        self.debug = debug

        # Ensure staging bucket has gs:// prefix
        if not self.staging_bucket.startswith("gs://"):
            self.staging_bucket = f"gs://{self.staging_bucket}"

    # ---------------- Vertex init ----------------
    def _ensure_vertex_inited(self) -> None:
        """Initialize Vertex AI once and reuse."""
        if not getattr(self, "_vertex_inited", False):
            vertexai_init(project=self.project_id, location=self.location, staging_bucket=self.staging_bucket)
            self._vertex_inited = True

    # ---------------- Virtual Environment Management ----------------
    def _create_venv_name(self, engine_name: str) -> str:
        """Generate a unique virtual environment name with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Clean engine name for filesystem safety
        clean_name = "".join(c for c in engine_name if c.isalnum() or c in "_-").lower()
        return f"venv_{timestamp}_{clean_name}"

    def _deactivate_current_venv(self) -> bool:
        """Deactivate any currently active virtual environment."""
        if not os.environ.get("VIRTUAL_ENV"):
            if self.debug:
                print("📍 No virtual environment currently active.")
            return True
        if self.debug:
            print(f"📍 Deactivating current virtual environment: {os.environ.get('VIRTUAL_ENV')}")
        # No-op for current process; we'll spawn new processes with the target venv
        return True

    def _create_and_activate_venv(self, venv_name: str, project_dir: str) -> Tuple[bool, str, str]:
        """
        Create a new virtual environment.
        Returns: (success, venv_path, python_executable)
        """
        try:
            venv_base = os.path.join(os.path.expanduser("~"), ".agent_venvs")
            os.makedirs(venv_base, exist_ok=True)
            venv_path = os.path.join(venv_base, venv_name)

            print(f"🔧 Creating virtual environment: {venv_path}")
            venv.create(venv_path, with_pip=True, clear=True)

            if platform.system() == "Windows":
                python_exe = os.path.join(venv_path, "Scripts", "python.exe")
            else:
                python_exe = os.path.join(venv_path, "bin", "python")

            if not os.path.exists(python_exe):
                raise RuntimeError(f"Python executable not found at: {python_exe}")

            print("✅ Virtual environment created successfully")
            print(f"📍 Python executable: {python_exe}")
            return True, venv_path, python_exe
        except Exception as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False, "", ""

    def _install_requirements_in_venv(self, python_exe: str, requirements: List[str]) -> bool:
        """Install requirements in the specified virtual environment using interpreter-correct pip."""
        if not requirements:
            print("📍 No requirements to install.")
            return True
        try:
            print(f"📦 Installing {len(requirements)} requirements...")
            for req in requirements:
                print(f"  📦 Installing: {req}")
                cmd = [python_exe, "-m", "pip", "install", req]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    print(f"❌ Failed to install {req}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
                    return False
            print("✅ All requirements installed successfully!")
            return True
        except subprocess.TimeoutExpired:
            print("❌ Package installation timed out")
            return False
        except Exception as e:
            print(f"❌ Error installing requirements: {e}")
            return False

    def _cleanup_venv(self, venv_path: str) -> bool:
        """Remove the virtual environment directory."""
        if not venv_path or not os.path.exists(venv_path):
            if self.debug:
                print("📍 Virtual environment path doesn't exist, nothing to clean up.")
            return True
        try:
            print(f"🧹 Cleaning up virtual environment: {venv_path}")
            shutil.rmtree(venv_path)
            print("✅ Virtual environment cleaned up successfully!")
            return True
        except Exception as e:
            print(f"⚠️ Warning: Failed to clean up virtual environment: {e}")
            return False

    def _add_venv_to_sys_path(self, python_exe: str) -> Optional[str]:
        """Add the virtual environment's site-packages to sys.path for imports."""
        try:
            code = "import sysconfig, json; print(json.dumps(sysconfig.get_paths()))"
            result = subprocess.check_output([python_exe, "-c", code], text=True)
            paths = json.loads(result.strip())
            site_pkgs = paths.get("purelib") or paths.get("platlib")
            if site_pkgs and site_pkgs not in sys.path:
                print(f"📍 Adding venv site-packages to sys.path: {site_pkgs}")
                sys.path.insert(0, site_pkgs)
                return site_pkgs
            return site_pkgs
        except Exception as e:
            print(f"⚠️ Warning: Could not add venv to sys.path: {e}")
            return None

    def _remove_venv_from_sys_path(self, site_pkgs_path: Optional[str]) -> None:
        """Remove the virtual environment's site-packages from sys.path."""
        if site_pkgs_path and site_pkgs_path in sys.path:
            sys.path.remove(site_pkgs_path)
            print(f"📍 Removed venv site-packages from sys.path: {site_pkgs_path}")

    def _push_venv_envvars(self, venv_path: str) -> None:
        """Temporarily emulate activation for subprocesses/tools."""
        self._old_env = {
            "PATH": os.environ.get("PATH", ""),
            "VIRTUAL_ENV": os.environ.get("VIRTUAL_ENV"),
        }
        bin_dir = os.path.join(venv_path, "Scripts" if platform.system() == "Windows" else "bin")
        os.environ["VIRTUAL_ENV"] = venv_path
        os.environ["PATH"] = bin_dir + os.pathsep + self._old_env["PATH"]

    def _pop_venv_envvars(self) -> None:
        if hasattr(self, "_old_env"):
            os.environ["PATH"] = self._old_env["PATH"]
            if self._old_env["VIRTUAL_ENV"] is None:
                os.environ.pop("VIRTUAL_ENV", None)
            else:
                os.environ["VIRTUAL_ENV"] = self._old_env["VIRTUAL_ENV"]
            del self._old_env

    # ---------------- Validation ----------------
    def _assert_no_google_shadow(self, agent_dir: str) -> None:
        """Ensure no local package named 'google' shadows site-packages."""
        local_google = os.path.join(agent_dir, "google")
        if os.path.isdir(local_google) or os.path.isfile(local_google + ".py"):
            raise RuntimeError(
                f"Found local '{local_google}'. This will shadow 'google.adk'. "
                "Rename/remove it or move agent code under a different package."
            )

    # ---------------- Agent Loading and Staging ----------------
    def _stage_clean_copy(self, src_dir: str) -> str:
        """Copy agent directory to temp dir, excluding dev files and secrets."""
        src = Path(src_dir).resolve()
        dst_root = Path(tempfile.mkdtemp(prefix="agent_stage_"))
        dst = dst_root / src.name

        if self.debug:
            print("📦 Staging agent directory...")
            print(f"📁 Source: {src}")
            print(f"📁 Destination: {dst}")
            print(f"🚫 Excluding: {EXCLUDES}")
            if src.exists():
                print("📋 Source contents:")
                for item in sorted(src.iterdir()):
                    print(f"  {'📁' if item.is_dir() else '📄'} {item.name}{'/' if item.is_dir() else ''}")

        shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*EXCLUDES), dirs_exist_ok=True)

        if self.debug:
            print("📋 Staged contents:")
            for item in sorted(dst.iterdir()):
                print(f"  {'📁' if item.is_dir() else '📄'} {item.name}{'/' if item.is_dir() else ''}")

        # Clean up .env files
        for p in dst.rglob(".env*"):
            try:
                p.unlink()
                if self.debug:
                    print(f"🗑️  Removed: {p}")
            except Exception:
                pass

        if self.debug:
            print(f"✅ Staging complete: {dst}")
        return str(dst)

    def _load_agent_from_file(self, agent_file_path: str):
        """Load root_agent from a Python file, handling relative imports properly."""
        agent_file = Path(agent_file_path).resolve()
        if not agent_file.exists():
            raise RuntimeError(f"Agent file not found: {agent_file}")

        agent_dir = agent_file.parent
        package_name = agent_dir.name
        module_name = f"{package_name}.{agent_file.stem}"

        parent_dir = str(agent_dir.parent)
        agent_dir_str = str(agent_dir)

        print(f"🤖 Loading {agent_file.stem} from: {agent_file}")
        print(f"📁 Agent directory: {agent_dir}")
        print(f"📦 Package name: {package_name}")
        print(f"🔧 Module name: {module_name}")
        if self.debug:
            print(f"🛤️  Adding to sys.path: {parent_dir} (for package imports)")
            print(f"🛤️  Adding to sys.path: {agent_dir_str} (for absolute imports like 'tools')")

        # Add both parent directory and agent directory
        paths_added: List[str] = []
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
            paths_added.append(parent_dir)
        if agent_dir_str not in sys.path:
            sys.path.insert(0, agent_dir_str)
            paths_added.append(agent_dir_str)

        try:
            # Optionally create a package for proper relative import resolution
            init_py = agent_dir / "__init__.py"
            package_spec = importlib.util.spec_from_file_location(package_name, init_py if init_py.exists() else None)
            if package_spec:
                package_module = importlib.util.module_from_spec(package_spec)
                sys.modules[package_name] = package_module
                if package_spec.loader and init_py.exists():
                    package_spec.loader.exec_module(package_module)

            spec = importlib.util.spec_from_file_location(module_name, agent_file)
            if spec is None or spec.loader is None:
                raise RuntimeError(f"Could not load module spec from {agent_file}")

            module = importlib.util.module_from_spec(spec)
            module.__package__ = package_name  # help relative imports
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            if not hasattr(module, "root_agent"):
                raise RuntimeError(f"Module '{agent_file}' does not define `root_agent`.")
            print(f"✅ Successfully loaded root_agent from {agent_file}")
            return getattr(module, "root_agent")
        except Exception as e:
            print(f"❌ Failed to load agent: {e}")
            raise RuntimeError(f"Failed to execute agent module {agent_file}: {e}") from e
        finally:
            for path in reversed(paths_added):
                while path in sys.path:
                    sys.path.remove(path)
            # clean any submodules from this package
            mods_to_remove = [name for name in list(sys.modules.keys()) if name.startswith(package_name)]
            for name in mods_to_remove:
                sys.modules.pop(name, None)

    # ---------------- Utilities ----------------
    @staticmethod
    def _merge_requirements(baseline: List[str], user: List[str]) -> List[str]:
        seen = set()
        out: List[str] = []
        for seq in (baseline, user):
            for item in seq:
                key = item.strip().lower()
                if not key or key in seen:
                    continue
                seen.add(key)
                out.append(item.strip())
        return out

    # ---------------- Main Creation Method ----------------
    def create_advanced_engine(self, config: Dict[str, Any]) -> Tuple[str, str, Optional[str]]:
        """Create a reasoning engine with advanced configuration options."""
        print("🚀 Starting advanced reasoning engine creation...")
        if self.debug:
            print("📋 Configuration:")
            try:
                print(json.dumps(config, indent=2))
            except Exception:
                print(str(config))

        try:
            display_name = config["display_name"]
            description = config.get("description", "")
            enable_tracing = config.get("enable_tracing", True)

            # Requirements
            requirements: List[str] = []
            if config["requirements_source_type"] == "file":
                req_file = config.get("requirements_file")
                if req_file and os.path.exists(req_file):
                    with open(req_file, "r", encoding="utf-8") as f:
                        requirements = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
            elif config["requirements_source_type"] == "text":
                requirements_text = config.get("requirements_text", "").strip()
                requirements = [line.strip() for line in requirements_text.splitlines() if line.strip() and not line.strip().startswith("#")]

            # Ensure baseline ADK deps exist in the build venv (idempotent)
            baseline = [
                "google-adk>=1.0.0",
                "google-cloud-aiplatform[agent_engines]>=1.93.0,<2.0.0",
                "google-genai>=1.16.1,<2.0.0",
            ]
            requirements = self._merge_requirements(baseline, requirements)

            # Paths
            agent_file_path = config["agent_file_path"]
            agent_dir = os.path.dirname(agent_file_path)

            # venv lifecycle
            print("🌐 Setting up isolated virtual environment...")
            self._deactivate_current_venv()
            venv_name = self._create_venv_name(display_name)
            v_success, venv_path, python_exe = self._create_and_activate_venv(venv_name, agent_dir)
            if not v_success:
                raise RuntimeError("Failed to create virtual environment")

            # installs
            if requirements:
                if not self._install_requirements_in_venv(python_exe, requirements):
                    self._cleanup_venv(venv_path)
                    raise RuntimeError("Failed to install requirements in virtual environment")

            # make imports & subprocesses behave like activated
            self._push_venv_envvars(venv_path)
            venv_site_pkgs = self._add_venv_to_sys_path(python_exe)

            try:
                # quick guard against local google/ package
                self._assert_no_google_shadow(agent_dir)

                print("🔍 Checking agent directory structure...")
                agent_path = Path(agent_dir)
                tools_path = agent_path / "tools"
                if tools_path.exists() and self.debug:
                    tool_files = [p.name for p in tools_path.glob("*.py")]
                    print(f"✅ Found tools directory with files: {tool_files}")
                elif not tools_path.exists():
                    print(f"❌ WARNING: tools directory not found at {tools_path}")

                staged_dir = self._stage_clean_copy(agent_dir)
                staged_tools = Path(staged_dir) / "tools"
                if not staged_tools.exists():
                    print("❌ ERROR: Tools directory missing from staged copy!")
                    raise RuntimeError("Tools directory was not properly staged")

                # load agent
                print(f"🤖 Loading root_agent from: {agent_file_path}")
                root_agent = self._load_agent_from_file(agent_file_path)

                # vertex init + create
                self._ensure_vertex_inited()
                print("🚀 Creating reasoning engine with venv dependencies…")
                app = AdkApp(agent=root_agent, enable_tracing=enable_tracing)
                remote = agent_engines.create(
                    app,
                    display_name=display_name,
                    description=description,
                    requirements=requirements,
                    extra_packages=[staged_dir],
                )

                print("✅ Engine creation successful!")
                return (
                    "created",
                    f"Advanced engine '{display_name}' created successfully",
                    remote.resource_name,
                )

            except Exception as e:
                print(f"❌ Deployment failed: {e}")
                raise
            finally:
                # undo import/env tweaks, then remove the venv
                if venv_site_pkgs:
                    self._remove_venv_from_sys_path(venv_site_pkgs)
                self._pop_venv_envvars()
                print("🧹 Cleaning up virtual environment...")
                self._cleanup_venv(venv_path)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return ("failed", f"Creation failed: {str(e)}", None)
