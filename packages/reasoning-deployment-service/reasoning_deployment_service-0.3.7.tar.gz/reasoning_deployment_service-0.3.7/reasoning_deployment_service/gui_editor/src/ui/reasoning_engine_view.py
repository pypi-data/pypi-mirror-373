"""Reasoning Engine management view."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from ..core.api_client import ApiClient
from .ui_components import async_operation, StatusButton, DeployDialog, EngineDetailsDialog, LoadingDialog, CreateReasoningEngineDialog, CreateReasoningEngineAdvancedDialog


class ReasoningEngineView(ttk.Frame):
    """UI for engine lifecycle."""
    
    def __init__(self, master, api: ApiClient, log: Callable[[str], None], refresh_agents: Callable[[], None]):
        super().__init__(master)
        self.api = api
        self.log = log
        self.refresh_agents = refresh_agents
        self._engines_auto_loaded = False  # Track if engines have been auto-loaded
        
        # Cache authentication state to avoid repeated API calls
        self._cached_auth_state = None
        self._last_auth_check = 0
        self._auth_cache_duration = 30  # 30 seconds
        
        self._setup_ui()

    def _setup_ui(self):
        # Action buttons with prominent CREATE ENGINE NOW button
        actions = ttk.Frame(self)
        actions.pack(fill="x", padx=4, pady=6)

        # Left side - secondary buttons
        left_actions = ttk.Frame(actions)
        left_actions.pack(side="left")
        
        # Right side - prominent CREATE ENGINE NOW button
        right_actions = ttk.Frame(actions)
        right_actions.pack(side="right")
        
        # All Engines section
        engines_frame = ttk.LabelFrame(self, text="All Reasoning Engines", padding=10)
        engines_frame.pack(fill="both", expand=True, padx=4, pady=(16, 6))
        
        # Engines control buttons
        engines_btns = ttk.Frame(engines_frame)
        engines_btns.pack(fill="x", pady=(0, 4))
        
        self.refresh_engines_btn = StatusButton(engines_btns, text="Refresh All Engines", command=self._refresh_engines)
        self.refresh_engines_btn.pack(side="left", padx=4)
        
        self.delete_engines_btn = StatusButton(engines_btns, text="Delete Selected Engines", command=self._delete_selected_engines)
        self.delete_engines_btn.pack(side="left", padx=8)
        
        self.engine_details_btn = StatusButton(engines_btns, text="More Engine Details", command=self.show_engine_details)
        self.engine_details_btn.pack(side="left", padx=8)
        
        self.engines_status = tk.StringVar(value="Ready.")
        ttk.Label(engines_btns, textvariable=self.engines_status).pack(side="right")

        # Engines list
        engines_wrap = ttk.Frame(engines_frame)
        engines_wrap.pack(fill="both", expand=True)
        engines_cols = ("id", "display_name", "create_time")
        self.engines_tree = ttk.Treeview(engines_wrap, columns=engines_cols, show="headings", selectmode="extended")
        
        for c, t, w in [
            ("id", "Engine ID", 250),
            ("display_name", "Display Name", 400),
            ("create_time", "Created", 200),
        ]:
            self.engines_tree.heading(c, text=t)
            self.engines_tree.column(c, width=w, anchor="w")
        
        self.engines_tree.pack(side="left", fill="both", expand=True)
        engines_vsb = ttk.Scrollbar(engines_wrap, orient="vertical", command=self.engines_tree.yview)
        self.engines_tree.configure(yscroll=engines_vsb.set)
        engines_vsb.pack(side="right", fill="y")
        
        # Engines event bindings
        self.engines_tree.bind("<<TreeviewSelect>>", self._on_engines_selection_change)
        self.engines_tree.bind("<Button-3>", self._engines_popup)
        
        # Engines context menu
        self.engines_menu = tk.Menu(self, tearoff=0)
        self.engines_menu.add_command(label="Delete", command=self._delete_selected_engines)
        
        # Debouncing timers
        self._update_timer = None
        self._engines_update_timer = None
        
        # Store full engine data for details popup
        self._engines_data = {}

        # Status
        self.eng_status = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.eng_status).pack(fill="x", padx=4, pady=(8, 0))
        
        # Initialize button states without immediate API calls
        self._update_button_states()
        # Don't auto-refresh on startup - let user click refresh button

    def _get_cached_auth_state(self) -> bool:
        """Get authentication state with local caching to reduce API calls."""
        import time
        now = time.time()
        
        # Use cached result if still fresh
        if (self._cached_auth_state is not None and 
            (now - self._last_auth_check) < self._auth_cache_duration):
            return self._cached_auth_state
        
        # Check authentication and cache result
        self._cached_auth_state = self.api.is_authenticated
        self._last_auth_check = now
        return self._cached_auth_state

    def _status_text(self) -> str:
        return f"Engine: {self.engine_name_var.get()} | Agent: {self.agent_space_id_var.get()}"

    def _update_button_states(self):
        """Update button states based on current conditions."""
        # Use cached authentication state to reduce API calls
        has_auth = self._get_cached_auth_state()
        has_engine = self.api.has_engine
        has_agent = self.api.has_deployed_agent
        
        # Create advanced engine - enabled if authenticated
        # self.create_advanced_btn.set_enabled(
        #     has_auth,
        #     "Authentication required" if not has_auth else ""
        # )
        
        # Engines list buttons
        self.refresh_engines_btn.set_enabled(
            has_auth,
            "Authentication required" if not has_auth else ""
        )
        
        engines_selection = self.engines_tree.selection()
        engines_selection_count = len(engines_selection)
        
        self.delete_engines_btn.set_enabled(
            engines_selection_count > 0,
            "Select engines to delete" if engines_selection_count == 0 else ""
        )
        
        # Deploy - enabled if authenticated and exactly one engine is selected
        single_engine_selected = engines_selection_count == 1
        # self.deploy_btn.set_enabled(
        #     has_auth and single_engine_selected,
        #     "Authentication required" if not has_auth else 
        #     "Select exactly one engine to deploy" if not single_engine_selected else ""
        # )
        
        # Engine details button - enabled only if a single engine is selected
        self.engine_details_btn.set_enabled(
            single_engine_selected,
            "Select a single engine to view details" if not single_engine_selected else ""
        )

    def _on_engines_selection_change(self, event=None):
        """Handle engines tree selection changes - IMMEDIATE update, no debouncing."""
        # Immediate update - no timers or delays
        self._update_button_states()

    def _refresh_engines(self):
        """Refresh the list of all reasoning engines."""
        # Update button states immediately on click
        self._update_button_states()
        
        # Check authentication once at the start using cached state
        if not self._get_cached_auth_state():
            self.log("❌ Authentication required")
            return
        
        # Show loading dialog
        loading_dialog = LoadingDialog(self.winfo_toplevel(), "Loading reasoning engines...")
        self.refresh_engines_btn.set_enabled(False, "Loading...")
        
        def callback(items):
            # Close loading dialog
            loading_dialog.close()
            self.refresh_engines_btn.set_enabled(True)
            
            for i in self.engines_tree.get_children():
                self.engines_tree.delete(i)
            
            # Clear stored data
            self._engines_data.clear()
            
            if isinstance(items, Exception):
                self.log(f"❌ Engines list error: {items}")
                self.engines_status.set("Error")
                return
            
            for it in items:
                # Format create time nicely
                create_time = it.get("create_time", "Unknown")
                if create_time != "Unknown" and "T" in str(create_time):
                    create_time = str(create_time).split("T")[0]  # Just the date part
                
                # Insert into tree with only 3 columns
                item_id = self.engines_tree.insert("", "end", values=(
                    it["id"], 
                    it["display_name"], 
                    create_time
                ))
                
                # Store full data for popup using tree item ID as key
                self._engines_data[item_id] = it
                
            self.engines_status.set(f"{len(items)} engine(s)")
            self._update_button_states()
        
        async_operation(self.api.list_reasoning_engines, callback=callback, ui_widget=self)

    def _delete_selected_engines(self):
        """Delete selected reasoning engines."""
        sel = self.engines_tree.selection()
        if not sel:
            messagebox.showinfo("No selection", "Select one or more engines to delete.")
            return
        
        # Get resource names from stored data
        resource_names = []
        for item_id in sel:
            if item_id in self._engines_data:
                resource_names.append(self._engines_data[item_id]["resource_name"])
        
        if not resource_names:
            messagebox.showerror("Error", "Could not find resource names for selected engines.")
            return
        
        if not messagebox.askyesno("Confirm delete", 
                                  f"Delete {len(resource_names)} selected engine(s)?\n\n"
                                  "⚠️ This will permanently delete the reasoning engines!"):
            return

        self.engines_status.set("Deleting…")
        self.delete_engines_btn.set_enabled(False, "Deleting...")
        
        def ui_log(msg: str):
            """Thread-safe logging - marshal to UI thread."""
            self.after(0, lambda: self.log(msg))
        
        def batch_delete():
            success_count = 0
            for resource_name in resource_names:
                status, msg = self.api.delete_reasoning_engine_by_id(resource_name)
                ui_log(f"{status.upper()}: {msg} — {resource_name}")
                if status == "deleted":
                    success_count += 1
            return success_count == len(resource_names)
        
        def callback(success):
            self.delete_engines_btn.set_enabled(True)
            self._refresh_engines()
            status_msg = "✅ Delete operation completed." if success else "⚠️ Delete completed with issues."
            self.log(status_msg)
        
        async_operation(batch_delete, callback=callback, ui_widget=self)

    def show_engine_details(self):
        """Show details for the selected engine."""
        sel = self.engines_tree.selection()
        if len(sel) != 1:
            messagebox.showinfo("No selection", "Select a single engine to view details.")
            return
        
        item_id = sel[0]
        if item_id not in self._engines_data:
            messagebox.showerror("Error", "Engine data not found.")
            return
        
        engine_data = self._engines_data[item_id]
        try:
            EngineDetailsDialog(self, engine_data)
        except Exception as e:
            print(f"Error opening engine details dialog: {e}")
            messagebox.showerror("Error", f"Failed to open details dialog: {e}")

    def _engines_popup(self, event):
        """Show engines context menu."""
        row = self.engines_tree.identify_row(event.y)
        if row:
            if row not in self.engines_tree.selection():
                self.engines_tree.selection_set(row)
            try:
                self.engines_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.engines_menu.grab_release()

    def _create_engine_advanced(self):
        """Create a new reasoning engine with advanced configuration."""
        if not self.api.is_authenticated:
            self.log("❌ Authentication required")
            return
        
        # Show advanced create engine dialog
        dialog = CreateReasoningEngineAdvancedDialog(self.winfo_toplevel(), self.api)
        self.wait_window(dialog)
        
        if not dialog.result:
            return  # User cancelled
        
        config = dialog.result
        self.log(f"⚙️ Creating advanced reasoning engine '{config['display_name']}'...")
        # self.create_advanced_btn.set_enabled(False, "Creating...")
        
        def callback(res):
            # self.create_advanced_btn.set_enabled(True)
            if isinstance(res, Exception):
                self.log(f"❌ {res}")
                return
            
            status, msg, resource = res
            self.log(f"{status.upper()}: {msg}")
            if resource:
                self.log(f"resource: {resource}")
            
            # Refresh engines list to show the new engine
            self._refresh_engines()
            self._update_button_states()
        
        async_operation(lambda: self.api.create_reasoning_engine_advanced(config), callback=callback, ui_widget=self)

    def update_api(self, api: ApiClient):
        """Update the API client reference."""
        self.api = api
        # Clear cached auth state when API changes
        self._cached_auth_state = None
        self._last_auth_check = 0
        # Reset auto-load flag
        self._engines_auto_loaded = False
        # Update button states immediately
        self._update_button_states()
        
        # Auto-load engines if credentials are available and not loaded yet
        if self._get_cached_auth_state():
            self._engines_auto_loaded = True
            self.log("✅ Auto-loading reasoning engines...")
            # Use a small delay to ensure UI is ready
            self.after(50, self._refresh_engines)

    def on_tab_selected(self):
        """Called when this tab is selected - trigger auto-loading if needed."""
        try:
            if not self._engines_auto_loaded and self._get_cached_auth_state():
                self._engines_auto_loaded = True
                self.log("✅ Auto-loading reasoning engines...")
                self._refresh_engines()
        except Exception as e:
            self.log(f"❌ Error during tab selection: {e}")
            # Don't re-raise to prevent crash
