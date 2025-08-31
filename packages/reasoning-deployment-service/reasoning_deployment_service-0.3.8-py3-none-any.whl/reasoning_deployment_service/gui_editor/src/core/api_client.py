"""API client for Google Cloud Agent Space and Reasoning Engine operations."""
import json
import uuid
import time
import subprocess
import sys, importlib, importlib.util
from typing import Optional, Dict, Any, List, Tuple
from pprint import pprint
from pathlib import Path

from .google_deps import (
    HAS_GOOGLE, google, GoogleAuthRequest, 
    vertexai, agent_engines
)
from .reasoning_engine_creator import ReasoningEngineCreator

BASE_URL = "https://discoveryengine.googleapis.com/v1alpha"


# --- helpers for clean packaging ---
EXCLUDES = [
        ".env", ".env.*", ".git", "__pycache__", ".pytest_cache", ".mypy_cache",
        ".DS_Store", "*.pyc", "*.pyo", "*.pyd", ".venv", "venv", "tests", "docs"
    ]


class ApiClient:
    def drop_agent_authorizations(self, agent_id: str) -> dict:
        """Drop all authorizations for an agent space agent by PATCHing with all attributes except authorizations (fully omitted)."""
        if not self.is_live:
            return {
                "id": agent_id,
                "authorizations": [],
                "status": "mock-dropped"
            }
        headers = {
            "Authorization": f"Bearer {self._access_token()}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self.project_id,
        }
        url = (f"{BASE_URL}/projects/{self.project_id}/locations/global/collections/default_collection/"
               f"engines/{self.engine_name}/assistants/default_assistant/agents/{agent_id}")
        # GET the current agent definition
        get_resp = self._http.get(url, headers=headers, timeout=60)
        get_resp.raise_for_status()
        agent_data = get_resp.json()
        # Build PATCH payload: copy all attributes except authorizations
        patch_payload = {}
        for key in ["displayName", "description"]:
            if key in agent_data:
                patch_payload[key] = agent_data[key]
        adk_def = agent_data.get("adkAgentDefinition", {})
        patch_adk_def = {}
        # Copy all adkAgentDefinition fields except 'authorizations'
        for k, v in adk_def.items():
            if k != "authorizations":
                patch_adk_def[k] = v
        if patch_adk_def:
            patch_payload["adk_agent_definition"] = patch_adk_def
        # PATCH with the new payload
        patch_resp = self._http.patch(url, headers=headers, json=patch_payload, timeout=60)
        patch_resp.raise_for_status()
        return patch_resp.json()
    def update_authorization_scopes(self, auth_id: str, scopes: list, oauth_client_id: str) -> dict:
        """Patch the scopes for a specific authorization by ID, updating the authorizationUri as well."""
        if not self.is_live:
            return {
                "id": auth_id,
                "scopes": scopes,
                "status": "mock-patched"
            }
        import requests
        scopes_str = " ".join(scopes)
        authorization_uri = (
            "https://accounts.google.com/o/oauth2/auth"
            "?response_type=code"
            f"&client_id={oauth_client_id}"
            f"&scope={scopes_str}"
            "&access_type=offline&prompt=consent"
        )
        payload = {
            "serverSideOauth2": {
                "authorizationUri": authorization_uri
            }
        }
        url = f"{BASE_URL}/projects/{self.project_id}/locations/global/authorizations/{auth_id}?update_mask=server_side_oauth2.authorization_uri"
        headers = {
            "Authorization": f"Bearer {self._access_token()}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self.project_id,
        }
        r = self._http.patch(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()
    def get_authorization_info(self, auth_id: str) -> dict:
        """Get details for a specific authorization by ID."""
        if not self.is_live:
            # Return mock info for testing
            return {
                "id": auth_id,
                "scopes": [
                    "https://www.googleapis.com/auth/cloud-platform",
                    "https://www.googleapis.com/auth/userinfo.email"
                ],
                "status": "mock"
            }
        headers = {
            "Authorization": f"Bearer {self._access_token()}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self.project_id,
        }
        url = f"{BASE_URL}/projects/{self.project_id}/locations/global/authorizations/{auth_id}"
        r = self._http.get(url, headers=headers, timeout=60)
        r.raise_for_status()
        return r.json()
    """
    Single responsibility: hold configuration & credentials and expose API calls.
    This class has both 'live' and 'mock' modes; the public surface is identical.
    """
    
    def __init__(
        self,
        project_id: str,
        project_number: str,
        location: str,
        engine_name: str,
        staging_bucket: str = "",
        oauth_client_id: str = "",
        oauth_client_secret: str = "",
        agent_import: Optional[str] = None,
        mode: str = "mock",  # "live" or "mock"
        profile_path: str = "agent_profile.json",
    ):
        self.project_id = project_id
        self.project_number = project_number
        self.location = location
        self.engine_name = engine_name
        self.staging_bucket = staging_bucket
        self.oauth_client_id = oauth_client_id
        self.oauth_client_secret = oauth_client_secret
        self.agent_import = agent_import
        self.mode = mode
        self.profile_path = profile_path

        # Local state persisted between runs
        self._profile: Dict[str, Any] = {
            "display_name": "Demo Agent" if mode == "mock" else "Your Agent",
            "description": "Prototype only" if mode == "mock" else "Live Agent",
            "name": None,  # reasoning engine resource
            "agent_space_agent_id": None,
            "requirements": [],
            "extra_packages": [],
            "tool_description": "Tooling",
        }
        self._agents_cache: List[Dict[str, str]] = []  # mock-only
        self._loaded_agent = None  # live-only
        
        # Authentication caching for performance ("live enough")
        self._auth_cache = None
        self._auth_cache_time = 0
        self._auth_cache_duration = 30  # Cache for 30 seconds
        
        # Performance optimizations
        self._vertex_inited = False  # Cache Vertex AI initialization
        self.debug = False  # Set True only when debugging needed
        
        # Reuse HTTP session to avoid repeated TLS handshakes
        import requests as _requests
        self._http = _requests.Session()
        self._http.headers.update({"Content-Type": "application/json"})

        self._load_profile()

        if self.is_live:
            if not HAS_GOOGLE:
                raise RuntimeError("Live mode requested but Google libs not installed.")
            # Lazy-load actual agent code if provided
            self._loaded_agent = self._maybe_import_agent(self.agent_import)

    # ---------------- Properties ----------------
    @property
    def is_live(self) -> bool:
        return self.mode == "live"

    @property
    def profile(self) -> Dict[str, Any]:
        return self._profile
    
    @property
    def is_authenticated(self) -> bool:
        """Check if we have valid authentication (cached for performance)."""
        if not self.is_live:
            return True
        
        # Use cached result if still fresh (30 seconds)
        now = time.time()
        if (self._auth_cache is not None and 
            (now - self._auth_cache_time) < self._auth_cache_duration):
            return self._auth_cache
        
        # Check authentication and cache result
        try:
            _ = self._access_token()
            self._auth_cache = True
        except Exception:
            self._auth_cache = False
        
        self._auth_cache_time = now
        return self._auth_cache
    
    def refresh_auth_cache(self):
        """Force refresh of authentication cache."""
        self._auth_cache = None
        self._auth_cache_time = 0
    
    def _ensure_vertex_inited(self):
        """Initialize Vertex AI once and reuse to avoid repeated heavy init calls."""
        if not self._vertex_inited:
            vertexai.init(project=self.project_id, location=self.location, staging_bucket=self.staging_bucket)
            self._vertex_inited = True
    
    @property
    def has_engine(self) -> bool:
        """Check if we have a reasoning engine."""
        return bool(self._profile.get("name"))
    
    @property
    def has_deployed_agent(self) -> bool:
        """Check if we have a deployed agent."""
        return bool(self._profile.get("agent_space_agent_id"))

    # ---------------- Profile Management ----------------
    def set_auth_name(self, name: str):
        self._profile["working_auth_name"] = name
        self._save_profile()

    def _save_profile(self):
        try:
            with open(self.profile_path, "w") as f:
                json.dump(self._profile, f, indent=2)
        except Exception:
            pass

    def _load_profile(self):
        try:
            with open(self.profile_path, "r") as f:
                saved = json.load(f)
                # shallow update only known keys
                for k in self._profile.keys():
                    if k in saved:
                        self._profile[k] = saved[k]
                # also pick up working_auth_name if present
                if "working_auth_name" in saved:
                    self._profile["working_auth_name"] = saved["working_auth_name"]
        except Exception:
            pass

    def _maybe_import_agent(self, mod_attr: Optional[str]):
        if not mod_attr:
            return None
        parts = mod_attr.split(":")
        if len(parts) != 2:
            return None
        mod, attr = parts
        try:
            imported = __import__(mod, fromlist=[attr])
            return getattr(imported, attr, None)
        except Exception:
            return None

    # ---------------- Authentication ----------------
    def _access_token(self) -> str:
        """Live: fetch ADC access token; raises if not available."""
        creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        # Only refresh if needed - avoid network hit on every call
        if not creds.valid or (creds.expired and creds.refresh_token):
            creds.refresh(GoogleAuthRequest())
        return creds.token

    def authenticate(self) -> bool:
        """
        For Live: ensure ADC is configured (runs gcloud flow if needed).
        For Mock: fast True.
        """
        if not self.is_live:
            # Minimal delay to simulate network without causing UI lag
            time.sleep(0.02)
            return True
        
        # If token works, we're good
        try:
            _ = self._access_token()
            return True
        except Exception:
            pass

        # Launch gcloud browser flow
        try:
            subprocess.run(["gcloud", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except Exception:
            raise RuntimeError("'gcloud' not found on PATH. Install Google Cloud SDK.")

        proc = subprocess.run(
            ["gcloud", "auth", "application-default", "login"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        if proc.returncode != 0:
            raise RuntimeError(f"ADC auth failed:\n{proc.stdout}")

        # Validate we can fetch a token now
        _ = self._access_token()
        return True

    # ---------------- Agent Space APIs ----------------
    def list_agent_space_agents(self) -> List[Dict[str, str]]:
        if not self.is_live:
            time.sleep(0.02)
            return list(self._agents_cache)  # Return empty list initially

        headers = {
            "Authorization": f"Bearer {self._access_token()}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self.project_id,
        }
        url = (f"{BASE_URL}/projects/{self.project_id}/locations/global/collections/default_collection/"
               f"engines/{self.engine_name}/assistants/default_assistant/agents")
        r = self._http.get(url, headers=headers, timeout=60)
        r.raise_for_status()
        data = r.json()
        out = []

        for a in data.get("agents", []):
            try:
                authorization_full = a.get('adkAgentDefinition', {}).get('authorizations', [])
                authorization_id = "N/A"
                authorization_path = "N/A"
                
                if authorization_full and len(authorization_full) > 0:
                    authorization_path = authorization_full[0]
                    # Extract just the authorization ID from the full path
                    if "/" in authorization_path:
                        authorization_id = authorization_path.split("/")[-1]
                    else:
                        authorization_id = authorization_path

                # Extract engine ID from reasoning engine path
                engine_full = a.get('adkAgentDefinition', {}).get('provisionedReasoningEngine', {}).get('reasoningEngine', '')
                engine_id = "N/A"
                
                if engine_full and "/" in engine_full:
                    engine_id = engine_full.split("/")[-1]
                elif engine_full:
                    engine_id = engine_full

            except Exception:
                authorization_id = "N/A"
                authorization_path = "N/A"
                engine_id = "N/A"
                engine_full = "N/A"

            full = a.get("name", "")
            out.append({
                "id": full.split("/")[-1] if full else "",
                "display_name": a.get("displayName", "N/A"),
                "authorization_id": authorization_id,
                "engine_id": engine_id,
                "full_name": full,
                # Store full paths for popup
                "authorization_full": authorization_path,
                "engine_full": engine_full,
            })
        return out

    def delete_agent_from_space(self, full_name: str) -> Tuple[str, str]:
        if not self.is_live:
            time.sleep(0.02)
            before = len(self._agents_cache)
            self._agents_cache = [a for a in self._agents_cache if a["full_name"] != full_name]
            if before != len(self._agents_cache) and self._profile.get("agent_space_agent_id") == full_name:
                self._profile["agent_space_agent_id"] = None
            return ("deleted", "Removed (mock)")
        
        headers = {
            "Authorization": f"Bearer {self._access_token()}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self.project_id,
        }
        url = f"{BASE_URL}/{full_name}"
        r = self._http.delete(url, headers=headers, timeout=60)
        # Treat any 2xx status as success (many APIs return 204 No Content)
        if 200 <= r.status_code < 300:
            if self._profile.get("agent_space_agent_id") == full_name:
                self._profile["agent_space_agent_id"] = None
                self._save_profile()
            return ("deleted", "Deleted")
        elif r.status_code == 404:
            return ("not_found", "Not found")
        else:
            return ("failed", f"{r.status_code} {r.text}")

    # ---------------- Reasoning Engine APIs ----------------
    def list_reasoning_engines(self) -> List[Dict[str, str]]:
        """List all reasoning engines in the project."""
        if not self.is_live:
            time.sleep(0.02)
            # Return empty list initially - no mock data by default
            return []
        
        # Use the Vertex AI SDK to list reasoning engines
        try:
            self._ensure_vertex_inited()  # Use cached initialization
            engines = agent_engines.list()
            
            out = []
            for engine in engines:
                try:
                    resource_name = str(engine.resource_name) if engine.resource_name else ""
                    engine_id = resource_name.split("/")[-1] if resource_name else ""
                    
                    # Handle datetime objects safely
                    create_time = "Unknown"
                    if hasattr(engine, 'create_time') and engine.create_time:
                        try:
                            # Convert datetime to string
                            create_time = str(engine.create_time)
                        except Exception:
                            create_time = "Unknown"
                    
                    # Safely get display name
                    display_name = str(engine.display_name) if hasattr(engine, 'display_name') and engine.display_name else "Unnamed Engine"
                    
                    out.append({
                        "id": engine_id,
                        "display_name": display_name,
                        "resource_name": resource_name,
                        "create_time": create_time
                    })
                except Exception as e:
                    # Skip engines that cause issues but continue processing
                    print(f"⚠️ Skipped engine due to error: {str(e)}")
                    continue
            
            return out
        except Exception as e:
            # Handle API registration and other Vertex AI errors gracefully
            error_msg = str(e)
            if "api_mode" in error_msg:
                print(f"⚠️ Vertex AI API registration warning: {error_msg}")
                # Return empty list but don't crash the app
                return []
            else:
                raise RuntimeError(f"Failed to list reasoning engines: {error_msg}")

    def delete_reasoning_engine_by_id(self, resource_name: str) -> Tuple[str, str]:
        """Delete a reasoning engine by resource name."""
        if not self.is_live:
            time.sleep(0.02)
            return ("deleted", f"Engine {resource_name} deleted (mock)")
        
        try:
            engine = agent_engines.get(resource_name)
            engine.delete(force=True)
            return ("deleted", "Reasoning engine deleted")
        except Exception as e:
            return ("failed", f"Delete failed: {str(e)}")

    def _load_agent_from_file(self, agent_file_path: str):
        """Load root_agent from a Python file, handling relative imports properly."""
        agent_file = Path(agent_file_path).resolve()
        if not agent_file.exists():
            raise RuntimeError(f"Agent file not found: {agent_file}")
        
        agent_dir = agent_file.parent
        package_name = agent_dir.name
        module_name = f"{package_name}.{agent_file.stem}"
        
        # Define paths before using them in print statements
        parent_dir = str(agent_dir.parent)
        agent_dir_str = str(agent_dir)
        
        print(f"🤖 Loading {agent_file.stem} from: {agent_file}")
        print(f"📁 Agent directory: {agent_dir}")
        print(f"📦 Package name: {package_name}")
        print(f"🔧 Module name: {module_name}")
        if self.debug:
            print(f"🛤️  Adding to sys.path: {parent_dir} (for package imports)")
            print(f"🛤️  Adding to sys.path: {agent_dir_str} (for absolute imports like 'tools')")
        
        # Add both the parent directory (for package imports) and the agent directory (for absolute imports like 'tools')
        paths_added = []
        
        # Add parent directory for package imports (e.g., 'executive_summary_builder.agent')
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
            paths_added.append(parent_dir)
        
        # Add agent directory for absolute imports within the package (e.g., 'tools.gmail_search_supporter')
        if agent_dir_str not in sys.path:
            sys.path.insert(0, agent_dir_str)
            paths_added.append(agent_dir_str)
        
        try:
            # Create package spec for proper relative import handling
            package_spec = importlib.util.spec_from_file_location(
                package_name, 
                agent_dir / "__init__.py" if (agent_dir / "__init__.py").exists() else None
            )
            
            if package_spec:
                # Load the package first
                package_module = importlib.util.module_from_spec(package_spec)
                sys.modules[package_name] = package_module
                if package_spec.loader and (agent_dir / "__init__.py").exists():
                    package_spec.loader.exec_module(package_module)
            
            # Now load the agent module as part of the package
            spec = importlib.util.spec_from_file_location(module_name, agent_file)
            if spec is None or spec.loader is None:
                raise RuntimeError(f"Could not load module spec from {agent_file}")
            
            module = importlib.util.module_from_spec(spec)
            # Set the package for relative imports
            module.__package__ = package_name
            
            # Add to sys.modules for relative imports to work
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
            # Clean up sys.path - remove all paths we added
            for path in reversed(paths_added):  # Remove in reverse order
                while path in sys.path:
                    sys.path.remove(path)
            
            # Clean up sys.modules
            modules_to_remove = [name for name in sys.modules.keys() 
                               if name.startswith(package_name)]
            for name in modules_to_remove:
                if name in sys.modules:
                    del sys.modules[name]

    def create_reasoning_engine_advanced(self, config: Dict[str, Any]) -> Tuple[str, str, Optional[str]]:
        """Create a reasoning engine with advanced configuration options."""
        creator = ReasoningEngineCreator(
            project_id=self.project_id,
            location=self.location,
            staging_bucket=self.staging_bucket,
            debug=self.debug,
        )

        return creator.create_advanced_engine(config)

    def delete_reasoning_engine(self) -> Tuple[str, str]:
        if not self._profile.get("name"):
            return ("not_found", "No engine")
        if not self.is_live:
            time.sleep(0.02)
            self._profile["name"] = None
            self._save_profile()
            return ("deleted", "Engine deleted (mock)")
        try:
            agent_engines.delete(self._profile["name"])
            self._profile["name"] = None
            self._save_profile()
            return ("deleted", "Engine deleted")
        except Exception as e:
            return ("failed", str(e))

    # ---------------- Deploy APIs ----------------
    def list_authorizations(self) -> List[Dict[str, str]]:
        """List all authorizations in the project."""
        if not self.is_live:
            time.sleep(0.02)
            # Mock some authorizations for testing
            return [
                {"id": "demo-auth", "name": f"projects/{self.project_id}/locations/global/authorizations/demo-auth"},
                {"id": "google-drive-auth", "name": f"projects/{self.project_id}/locations/global/authorizations/google-drive-auth"}
            ]
        
        headers = {
            "Authorization": f"Bearer {self._access_token()}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self.project_id,
        }
        url = f"{BASE_URL}/projects/{self.project_id}/locations/global/authorizations"
        r = self._http.get(url, headers=headers, timeout=60)
        r.raise_for_status()
        data = r.json()
        
        out = []
        for auth in data.get("authorizations", []):
            full_name = auth.get("name", "")
            out.append({
                "id": full_name.split("/")[-1] if full_name else "",
                "name": full_name,
            })
        return out

    def delete_authorization(self, auth_id: str) -> Tuple[str, str]:
        """Delete an authorization by ID."""
        if not self.is_live:
            time.sleep(0.02)
            return ("deleted", f"Authorization {auth_id} deleted (mock)")
        
        headers = {
            "Authorization": f"Bearer {self._access_token()}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self.project_id,
        }
        url = f"{BASE_URL}/projects/{self.project_id}/locations/global/authorizations/{auth_id}"
        r = self._http.delete(url, headers=headers, timeout=60)
        
        # Treat any 2xx status as success (many APIs return 204 No Content)
        if 200 <= r.status_code < 300:
            return ("deleted", "Authorization deleted")
        elif r.status_code == 404:
            return ("not_found", "Authorization not found")
        else:
            return ("failed", f"{r.status_code} {r.text}")

    def _ensure_authorization(self, auth_name: str) -> Tuple[bool, str]:
        if not self.is_live:
            time.sleep(0.02)
            return True, "mock"
        
        headers = {
            "Authorization": f"Bearer {self._access_token()}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self.project_number,
        }
        payload = {
            "name": f"projects/{self.project_number}/locations/global/authorizations/{auth_name}",
            "serverSideOauth2": {
                "clientId": self.oauth_client_id or "your-client-id",
                "clientSecret": self.oauth_client_secret or "your-client-secret",
                "authorizationUri": (
                    "https://accounts.google.com/o/oauth2/auth"
                    "?response_type=code"
                    f"&client_id={(self.oauth_client_id or 'your-client-id')}"
                    "&scope=openid"
                    "%20https://www.googleapis.com/auth/userinfo.email"
                    "%20https://www.googleapis.com/auth/calendar"
                    "%20https://www.googleapis.com/auth/gmail.send"
                    "%20https://www.googleapis.com/auth/gmail.compose"
                    "%20https://www.googleapis.com/auth/drive"
                    "%20https://www.googleapis.com/auth/presentations"
                    "%20https://www.googleapis.com/auth/cloud-platform"
                    "%20https://mail.google.com/"
                    "&access_type=offline&prompt=consent"
                ),
                "tokenUri": "https://oauth2.googleapis.com/token"
            }
        }
        url = f"{BASE_URL}/projects/{self.project_id}/locations/global/authorizations?authorizationId={auth_name}"
        r = self._http.post(url, headers=headers, json=payload, timeout=60)

        if self.debug:
            from pprint import pprint
            pprint(r.json())  # Debugging output
        if r.status_code < 400:
            return True, "created"
        if r.status_code == 409:
            return True, "exists"
        return False, f"{r.status_code} {r.text}"

    def deploy_to_agent_space(self, with_authorization: bool, auth_name: str) -> Tuple[str, str, Optional[Dict[str, str]]]:
        if not self._profile.get("name"):
            return ("failed", "Reasoning engine required before deploy", None)

        if not self.is_live:
            time.sleep(0.02)
            aid = f"agent_{uuid.uuid4().hex[:6]}"
            full = (f"projects/{self.project_id}/locations/global/collections/default_collection/"
                    f"engines/{self.engine_name}/assistants/default_assistant/agents/{aid}")
            item = {"id": aid, "display_name": self._profile.get("display_name", "Demo Agent"), "full_name": full}
            self._agents_cache.append(item)
            self._profile["agent_space_agent_id"] = full
            self._save_profile()
            return ("created", f"Deployed (mock, oauth={with_authorization})", item)

        if with_authorization:
            ok, msg = self._ensure_authorization(auth_name)
            if not ok:
                return ("failed", f"Authorization failed: {msg}", None)

        headers = {
            "Authorization": f"Bearer {self._access_token()}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self.project_number,
        }
        payload = {
            "displayName": self._profile.get("display_name", "Live Agent"),
            "description": self._profile.get("description", "Live Agent"),
            "adk_agent_definition": {
                "tool_settings": {"tool_description": self._profile.get("tool_description", "Tooling")},
                "provisioned_reasoning_engine": {"reasoning_engine": self._profile["name"]},
            },
        }
        if with_authorization:
            payload["adk_agent_definition"]["authorizations"] = [
                f"projects/{self.project_number}/locations/global/authorizations/{auth_name}"
            ]

        url = (f"{BASE_URL}/projects/{self.project_number}/locations/global/collections/default_collection/"
               f"engines/{self.engine_name}/assistants/default_assistant/agents")
        if self.debug:
            pprint(payload)
            pprint(url)
        r = self._http.post(url, headers=headers, json=payload, timeout=90)

        if self.debug:
            pprint(r.json())  # Debugging output
        if not r.ok:
            return ("failed", f"Deploy failed: {r.status_code} {r.text}", None)

        info = r.json()
        full = info.get("name", "")
        item = {
            "id": full.split("/")[-1] if full else "",
            "display_name": info.get("displayName", self._profile.get("display_name", "")),
            "full_name": full,
        }
        self._profile["agent_space_agent_id"] = full
        self._save_profile()
        return ("created", "Deployed", item)
