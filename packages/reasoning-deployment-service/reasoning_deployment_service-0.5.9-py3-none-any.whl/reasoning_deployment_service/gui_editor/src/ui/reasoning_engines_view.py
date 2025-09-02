"""Reasoning Engines listing and management view."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from ..core.api_client import ApiClient
from .ui_components import async_operation, StatusButton


class ReasoningEnginesView(ttk.Frame):
    """UI for listing and managing reasoning engines."""
    
    def __init__(self, master, api: ApiClient, log: Callable[[str], None]):
        super().__init__(master)
        self.api = api
        self.log = log
        
        # Cache authentication state to avoid repeated API calls
        self._cached_auth_state = None
        self._last_auth_check = 0
        self._auth_cache_duration = 30  # 30 seconds
        
        self._setup_ui()

    def _setup_ui(self):
        # Control buttons
        btns = ttk.Frame(self)
        btns.pack(fill="x", pady=(6, 4))
        
        self.refresh_btn = StatusButton(btns, text="Refresh Engines", command=self.refresh)
        self.refresh_btn.pack(side="left", padx=4)
        
        self.delete_btn = StatusButton(btns, text="Delete Selected", command=self.delete_selected)
        self.delete_btn.pack(side="left", padx=8)
        
        self.status = tk.StringVar(value="Ready.")
        ttk.Label(btns, textvariable=self.status).pack(side="right")

        # Info label
        info_frame = ttk.Frame(self)
        info_frame.pack(fill="x", padx=4, pady=4)
        ttk.Label(info_frame, text="💡 Reasoning Engines are the core compute units that power your agents.", 
                 foreground="gray").pack(anchor="w")

        # Engines list
        wrap = ttk.Frame(self)
        wrap.pack(fill="both", expand=True)
        cols = ("id", "display_name", "create_time", "resource_name")
        self.tree = ttk.Treeview(wrap, columns=cols, show="headings", selectmode="extended")
        
        for c, t, w in [
            ("id", "Engine ID", 200),
            ("display_name", "Display Name", 300),
            ("create_time", "Created", 180),
            ("resource_name", "Full Resource Name", 500),
        ]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="w")
        
        self.tree.pack(side="left", fill="both", expand=True)
        vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.pack(side="right", fill="y")
        
        # Event bindings
        self.tree.bind("<<TreeviewSelect>>", self._on_selection_change)
        self.tree.bind("<Button-3>", self._popup)
        
        # Context menu
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Delete", command=self.delete_selected)
        
        self._update_button_states()

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

    def _update_button_states(self):
        """Update button states based on current conditions."""
        # Use cached authentication state to reduce API calls
        is_auth = self._get_cached_auth_state()
        self.refresh_btn.set_enabled(
            is_auth,
            "Authentication required" if not is_auth else ""
        )
        
        # Delete button - enabled only if engines are selected
        has_selection = bool(self.tree.selection())
        self.delete_btn.set_enabled(
            has_selection,
            "Select engines to delete" if not has_selection else ""
        )

    def _on_selection_change(self, event=None):
        """Handle tree selection changes - IMMEDIATE update, no debouncing."""
        # Immediate update - no timers or delays
        self._update_button_states()

    def refresh(self):
        """Refresh the list of reasoning engines."""
        # Use cached authentication state
        if not self._get_cached_auth_state():
            self.log("❌ Authentication required")
            return
            
        self.status.set("Loading…")
        self.refresh_btn.set_enabled(False, "Loading...")
        
        def callback(items):
            self.refresh_btn.set_enabled(True)
            for i in self.tree.get_children():
                self.tree.delete(i)
            
            if isinstance(items, Exception):
                self.log(f"❌ List error: {items}")
                self.status.set("Error")
                return
            
            for it in items:
                # Format create time nicely
                create_time = it.get("create_time", "Unknown")
                if create_time != "Unknown" and "T" in create_time:
                    create_time = create_time.split("T")[0]  # Just the date part
                
                self.tree.insert("", "end", values=(
                    it["id"], 
                    it["display_name"], 
                    create_time,
                    it["resource_name"]
                ))
            self.status.set(f"{len(items)} engine(s)")
            self._update_button_states()
        
        async_operation(self.api.list_reasoning_engines, callback=callback, ui_widget=self)

    def delete_selected(self):
        """Delete selected reasoning engines."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("No selection", "Select one or more engines to delete.")
            return
        
        rows = [self.tree.item(i, "values") for i in sel]
        resource_names = [r[3] for r in rows]  # resource_name is column 3
        
        if not messagebox.askyesno("Confirm delete", 
                                  f"Delete {len(resource_names)} selected engine(s)?\n\n"
                                  "⚠️ This will permanently delete the reasoning engines!"):
            return

        self.status.set("Deleting…")
        self.delete_btn.set_enabled(False, "Deleting...")
        
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
            self.delete_btn.set_enabled(True)
            self.refresh()
            status_msg = "✅ Delete operation completed." if success else "⚠️ Delete completed with issues."
            self.log(status_msg)
        
        async_operation(batch_delete, callback=callback, ui_widget=self)

    def _popup(self, event):
        """Show context menu."""
        row = self.tree.identify_row(event.y)
        if row:
            if row not in self.tree.selection():
                self.tree.selection_set(row)
            try:
                self.menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.menu.grab_release()

    def update_api(self, api: ApiClient):
        """Update the API client reference."""
        self.api = api
        # Clear cached auth state when API changes
        self._cached_auth_state = None
        self._last_auth_check = 0
        self._update_button_states()
