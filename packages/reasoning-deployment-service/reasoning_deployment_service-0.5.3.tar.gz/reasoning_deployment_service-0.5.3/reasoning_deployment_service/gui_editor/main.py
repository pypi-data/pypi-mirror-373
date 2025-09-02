"""Main application window and orchestration."""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

try:
    # Try package-level imports first (when installed as package)
    from reasoning_deployment_service.gui_editor.src.core.config import Config, loadenv
    from reasoning_deployment_service.gui_editor.src.core.api_client import ApiClient
    from reasoning_deployment_service.gui_editor.src.core.google_deps import HAS_GOOGLE
    from reasoning_deployment_service.gui_editor.src.ui.ui_components import LogConsole, async_operation
    from reasoning_deployment_service.gui_editor.src.ui.agent_space_view import AgentSpaceView
    from reasoning_deployment_service.gui_editor.src.ui.reasoning_engine_view import ReasoningEngineView
    from reasoning_deployment_service.gui_editor.src.ui.authorization_view import AuthorizationView
except ImportError:
    try:
        # Try relative imports (when running from within the package)
        from .src.core.config import Config, loadenv
        from .src.core.api_client import ApiClient
        from .src.core.google_deps import HAS_GOOGLE
        from .src.ui.ui_components import LogConsole, async_operation
        from .src.ui.agent_space_view import AgentSpaceView
        from .src.ui.reasoning_engine_view import ReasoningEngineView
        from .src.ui.authorization_view import AuthorizationView
    except ImportError:
        # Fall back to absolute imports (when running directly)
        from src.core.config import Config, loadenv
        from src.core.api_client import ApiClient
        from src.core.google_deps import HAS_GOOGLE
        from src.ui.ui_components import LogConsole, async_operation
        from src.ui.agent_space_view import AgentSpaceView
        from src.ui.reasoning_engine_view import ReasoningEngineView
        from src.ui.authorization_view import AuthorizationView


class GuiEditorApp(tk.Tk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.title("Agent Space / Reasoning Engine Manager")
        self.geometry("1120x760")
        
        # Load environment variables from env.agent
        loadenv(".env.agent")
        
        # Show blocking dropdown for environment selection
        self.env_var = tk.StringVar(value="dev")
        self._show_env_selector()
        
        # Load configuration
        self.config = Config()
        
        # Validate environment
        if not self._validate_env():
            self.destroy()
            return

        # Create API client
        self.api_client = self._create_api_client()
        
        # Setup UI
        self._setup_ui()

        # Initial state
        self._check_and_auto_load()

    def _create_api_client(self) -> ApiClient:
        """Create live API client."""
        cfg = self.config.to_dict()

        # Rename 'agent_space' to 'engine_name' for ApiClient compatibility
        cfg["engine_name"] = cfg.pop("agent_space", None)

        try:
            return ApiClient(**cfg, mode="live", profile_path="agent_profile.live.json")
        except Exception as e:
            print(f"[Live mode disabled] {e}")
            raise

    def _setup_ui(self):
        """Setup the user interface."""
        # Top control bar
        self._setup_top_bar()
        
        # Main content tabs
        self._setup_tabs()
        
        # Bottom console
        self._setup_console()

    def _setup_top_bar(self):
        """Setup the top control bar."""
        top = ttk.Frame(self, padding=(10, 8, 10, 0))
        top.pack(fill="x")
        
        # Auth button
        self.auth_btn = ttk.Button(top, text="Authenticate (ADC)", command=self._authenticate)
        self.auth_btn.pack(side="left")
        
        # Configuration status
        config_status = "✅ Configured" if self.config.is_configured else "⚠️ Check environment variables"
        ttk.Label(top, text=f"Config: {config_status}").pack(side="left", padx=(16, 0))

    def _setup_tabs(self):
        """Setup the main content tabs."""
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=10)

        # Create views
        self.agent_space = AgentSpaceView(self.nb, self.api_client, self._log)
        self.engine_view = ReasoningEngineView(
            self.nb, self.api_client, self._log, self.agent_space.refresh
        )
        self.auth_view = AuthorizationView(self.nb, self.api_client, self._log)

        self.nb.add(self.agent_space, text="Agent Space")
        self.nb.add(self.engine_view, text="Reasoning Engines")
        self.nb.add(self.auth_view, text="Authorizations")
        
        # Bind tab selection event to handle auto-loading
        self.nb.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _setup_console(self):
        """Setup the bottom console."""
        self.console = LogConsole(self)
        self.console.pack(fill="both", expand=False, padx=10, pady=(0, 10))
        self._log("Ready. Data will auto-load if credentials are available.")

    def _log(self, message: str):
        """Log a message to the console."""
        self.console.log(message)

    def _on_tab_changed(self, event):
        """Handle tab selection changes to trigger auto-loading."""
        selected_tab = self.nb.select()
        tab_text = self.nb.tab(selected_tab, "text")

        # Auto-load reasoning engines when that tab is first selected
        if tab_text == "Reasoning Engines":
            try:
                self.engine_view.on_tab_selected()
            except Exception as e:
                self._log(f"⚠️ Error loading reasoning engines: {e}")
        elif tab_text == "Authorizations":
            try:
                self.auth_view.on_tab_selected()
            except Exception as e:
                self._log(f"⚠️ Error loading authorizations: {e}")

    def _authenticate(self):
        """Authenticate with Google Cloud."""
        self._log("Authenticating…")

        def callback(res):
            if isinstance(res, Exception):
                self._log(f"❌ Auth error: {res}")
                return
            self._log("✅ Auth complete. Auto-loading data...")
            # Refresh auth cache after successful authentication
            self.api_client.refresh_auth_cache()
            # Auto-refresh data after successful authentication
            self.agent_space.refresh()

        async_operation(self.api_client.authenticate, callback=callback, ui_widget=self)

    def _check_and_auto_load(self):
        """Check authentication and auto-load data if credentials are available."""
        if self.api_client.is_authenticated:
            self._log("✅ Credentials available. Auto-loading data...")
            self.agent_space.refresh()
            self.engine_view._refresh_engines()  # Ensure reasoning engines are loaded
        else:
            self._log("🔐 Click 'Authenticate' to load data, or use Refresh buttons.")

    def _show_env_selector(self):
        """Show a blocking dropdown for selecting environment."""
        # Create a simple dialog without grab_set to avoid crashes
        selector = tk.Toplevel(self)
        selector.title("Select Environment")
        selector.geometry("400x200")
        selector.resizable(False, False)
        
        # Center the dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 200
        y = (self.winfo_screenheight() // 2) - 100
        selector.geometry(f"400x200+{x}+{y}")
        
        # Make it stay on top but don't use grab_set
        selector.attributes('-topmost', True)
        
        # Variables to track dialog state
        self.env_selected = False
        
        frame = ttk.Frame(selector, padding=20)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Select Environment:", font=("TkDefaultFont", 12)).pack(pady=10)
        
        env_frame = ttk.Frame(frame)
        env_frame.pack(pady=10)
        ttk.Label(env_frame, text="Environment:").pack(side="left", padx=(0, 10))
        env_menu = ttk.OptionMenu(env_frame, self.env_var, self.env_var.get(), "dev", "prod")
        env_menu.pack(side="left")

        def on_confirm():
            selected_env = self.env_var.get()
            
            # Load environment variables based on selection
            import os
            env_prefix = selected_env.upper()
            
            # Map environment variables
            os.environ["PROJECT_ID"] = os.getenv(f"{env_prefix}_PROJECT_ID", "")
            os.environ["PROJECT_NUMBER"] = os.getenv(f"{env_prefix}_PROJECT_NUMBER", "")
            os.environ["PROJECT_LOCATION"] = os.getenv(f"{env_prefix}_PROJECT_LOCATION", "")
            os.environ["AGENT_SPACE_ENGINE"] = os.getenv(f"{env_prefix}_AGENT_SPACE_ENGINE", "")
            
            self.config = Config()  # Reload configuration
            
            if self._validate_env():
                self.env_selected = True
                selector.destroy()
            else:
                messagebox.showerror(
                    "Validation Error",
                    f"Missing required fields in {selected_env} environment.\n"
                    f"Please ensure all required fields are set in .env.agent file:\n"
                    f"- {env_prefix}_PROJECT_ID\n"
                    f"- {env_prefix}_PROJECT_NUMBER\n"
                    f"- {env_prefix}_PROJECT_LOCATION\n"
                    f"- {env_prefix}_AGENT_SPACE_ENGINE"
                )

        def on_close():
            selector.destroy()
            self.destroy()
            exit()

        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Confirm", command=on_confirm).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Close App", command=on_close).pack(side="left", padx=10)
        
        # Handle window close event
        selector.protocol("WM_DELETE_WINDOW", on_close)
        
        # Wait for the dialog to be closed
        self.wait_window(selector)
        
        # If environment not selected, exit
        if not hasattr(self, 'env_selected') or not self.env_selected:
            self.destroy()
            exit()

    def _validate_env(self):
        """Validate the selected environment for required fields."""
        required_fields = ["project_id", "project_number", "location", "agent_space"]
        missing_fields = []
        
        for field in required_fields:
            value = getattr(self.config, field, None)
            if not value or value.strip() == "":
                missing_fields.append(field)
        
        return len(missing_fields) == 0

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    GuiEditorApp().run()

