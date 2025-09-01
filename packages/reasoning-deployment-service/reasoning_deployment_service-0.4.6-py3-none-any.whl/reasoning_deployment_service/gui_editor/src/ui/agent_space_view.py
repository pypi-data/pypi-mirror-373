"""Agent Space management view."""
import time
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from ..core.api_client import ApiClient
from .ui_components import async_operation, StatusButton, AgentDetailsDialog, LoadingDialog
from reasoning_deployment_service.gui_editor.agent_checkbox_list import AgentCheckboxList


class AgentSpaceView(ttk.Frame):
    """UI for listing and deleting Agent Space agents."""
    
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
        
        self.refresh_btn = StatusButton(btns, text="Refresh Agents", command=self.refresh)
        self.refresh_btn.pack(side="left", padx=4)
        
        self.delete_btn = StatusButton(btns, text="Delete Selected", command=self.delete_selected)
        self.delete_btn.pack(side="left", padx=8)

        self.drop_auth_btn = StatusButton(btns, text="Drop Authorizations (Selected)", command=self.drop_selected_authorizations)
        self.drop_auth_btn.pack(side="left", padx=8)

        self.details_btn = StatusButton(btns, text="More Agent Details", command=self.show_agent_details)
        self.details_btn.pack(side="left", padx=8)
        
        self.status = tk.StringVar(value="Ready.")
        ttk.Label(btns, textvariable=self.status).pack(side="right")

        # Add dropdown for environment selection
        self.env_var = tk.StringVar(value="dev")
        ttk.Label(btns, text="Environment:").pack(side="left", padx=(10, 0))
        ttk.OptionMenu(btns, self.env_var, "dev", "prod").pack(side="left", padx=(0, 10))

        # Agent list
        wrap = ttk.Frame(self)
        wrap.pack(fill="both", expand=True)
        cols = ("id", "display_name", "authorization_id", "engine_id")
        self.tree = ttk.Treeview(wrap, columns=cols, show="headings", selectmode="extended")
        
        for c, t, w in [
            ("id", "Agent ID", 250),
            ("display_name", "Display Name", 250),
            ("authorization_id", "Authorization", 250),
            ("engine_id", "Engine", 250),
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
        
        # Store full agent data for details popup
        self._agents_data = {}
        
        # Cache selection state to avoid redundant tree.selection() calls
        self._cached_selection = None
        self._selection_is_dirty = True
        
        # Checkbox agent list (initially empty, filled on refresh)
        self.checkbox_list_frame = ttk.LabelFrame(self, text="Mass Select Agents (Checkboxes)")
        self.checkbox_list_frame.pack(fill="x", padx=10, pady=8)
        self.agent_checkbox_list = None
        # Initialize button states without triggering immediate API calls
        self._update_button_states()

    def _get_cached_auth_state(self) -> bool:
        """Get authentication state with local caching to reduce API calls."""
        now = time.time()
        
        # Use cached result if still fresh
        if (self._cached_auth_state is not None and 
            (now - self._last_auth_check) < self._auth_cache_duration):
            return self._cached_auth_state
        
        # Check authentication and cache result
        self._cached_auth_state = self.api.is_authenticated
        self._last_auth_check = now
        return self._cached_auth_state

    def _get_selection(self):
        """Get cached selection to avoid redundant tree.selection() calls."""
        if self._selection_is_dirty or self._cached_selection is None:
            self._cached_selection = self.tree.selection()
            self._selection_is_dirty = False
        return self._cached_selection

    def _update_button_states(self):
        """Update button states based on current conditions - IMMEDIATE, no timers."""
        is_auth = self._get_cached_auth_state()
        self.refresh_btn.set_enabled(
            is_auth,
            "Authentication required" if not is_auth else ""
        )
        selection = self._get_selection()
        has_selection = bool(selection)
        single_selection = len(selection) == 1
        self.delete_btn.set_enabled(
            has_selection,
            "Select agents to delete" if not has_selection else ""
        )
        self.drop_auth_btn.set_enabled(
            has_selection,
            "Select agents to drop authorizations" if not has_selection else ""
        )
        self.details_btn.set_enabled(
            single_selection,
            "Select a single agent to view details" if not single_selection else ""
        )
    def drop_selected_authorizations(self):
        """Drop authorizations for selected agents."""
        selection = self._get_selection()
        if not selection:
            messagebox.showinfo("No selection", "Select agents to drop authorizations.")
            return
        count = len(selection)
        if not messagebox.askyesno("Confirm", f"Drop authorizations for {count} agent{'s' if count != 1 else ''}?"):
            return
        agent_ids = []
        for item in selection:
            values = self.tree.item(item, "values")
            if len(values) >= 1:
                agent_ids.append(values[0])
        self.status.set(f"Dropping authorizations for {count} agent{'s' if count != 1 else ''}...")
        def callback(results):
            if isinstance(results, Exception):
                self.status.set(f"Error: {results}")
                self.log(f"❌ Error dropping authorizations: {results}")
                return
            ok = [k for k, v in results.items() if isinstance(v, dict)]
            bad = {k: v for k, v in results.items() if not isinstance(v, dict)}
            if ok:
                self.log(f"✅ Dropped authorizations for {len(ok)} agent(s): {', '.join(ok[:10])}{'…' if len(ok) > 10 else ''}")
            for k, v in list(bad.items())[:10]:
                self.log(f"⚠️ {k}: {v}")
            if len(bad) > 10:
                self.log(f"…and {len(bad)-10} more failures")
            self.status.set(f"Done. Dropped authorizations for {len(ok)} agent(s).")
            self._update_button_states()
            self.refresh()
        def mass_drop():
            results = {}
            for agent_id in agent_ids:
                try:
                    results[agent_id] = self.api.drop_agent_authorizations(agent_id)
                except Exception as e:
                    results[agent_id] = str(e)
            return results
        async_operation(mass_drop, callback=callback, ui_widget=self)

    def _on_selection_change(self, event=None):
        """Handle tree selection changes - IMMEDIATE update, no debouncing."""
        # Mark selection cache as dirty
        self._selection_is_dirty = True
        # Immediate update - no timers or delays
        self._update_button_states()

    def _fill_tree_chunked(self, rows, start=0, chunk=200):
        """Fill tree in chunks to prevent UI freezing on large datasets."""
        end = min(start + chunk, len(rows))
        for agent in rows[start:end]:
            iid = self.tree.insert("", "end", values=(
                agent["id"],
                agent["display_name"],
                agent["authorization_id"],
                agent["engine_id"]
            ))
            # Store full agent data for details popup
            self._agents_data[iid] = agent
        
        if end < len(rows):
            # Yield to UI thread, then continue with next chunk
            self.after(0, self._fill_tree_chunked, rows, end, chunk)
        else:
            # All done - update final status and button states
            count = len(rows)
            self.status.set(f"Loaded {count} agent{'s' if count != 1 else ''}.")
            self.log(f"✅ Loaded {count} agent space agent{'s' if count != 1 else ''}. Data keys: {len(self._agents_data)}")
            # Update checkbox list
            self._update_checkbox_list(list(self._agents_data.values()))
            self._update_button_states()

    def _update_checkbox_list(self, agents):
        # Remove previous checkbox list if present
        if self.agent_checkbox_list:
            self.agent_checkbox_list.destroy()
        self.agent_checkbox_list = AgentCheckboxList(
            self.checkbox_list_frame,
            agents,
            self._mass_drop_authorizations_from_checkboxes
        )
        self.agent_checkbox_list.pack(fill="x", padx=4, pady=4)

    def _mass_drop_authorizations_from_checkboxes(self, agent_ids):
        if not agent_ids:
            messagebox.showinfo("No agents selected", "Please check agents to drop authorizations.")
            return
        count = len(agent_ids)
        if not messagebox.askyesno("Confirm", f"Drop authorizations for {count} agent{'s' if count != 1 else ''}?"):
            return
        self.status.set(f"Dropping authorizations for {count} agent{'s' if count != 1 else ''}...")
        def callback(results):
            if isinstance(results, Exception):
                self.status.set(f"Error: {results}")
                self.log(f"❌ Error dropping authorizations: {results}")
                return
            ok = [k for k, v in results.items() if isinstance(v, dict)]
            bad = {k: v for k, v in results.items() if not isinstance(v, dict)}
            if ok:
                self.log(f"✅ Dropped authorizations for {len(ok)} agent(s): {', '.join(ok[:10])}{'…' if len(ok) > 10 else ''}")
            for k, v in list(bad.items())[:10]:
                self.log(f"⚠️ {k}: {v}")
            if len(bad) > 10:
                self.log(f"…and {len(bad)-10} more failures")
            self.status.set(f"Done. Dropped authorizations for {len(ok)} agent(s).")
            self._update_button_states()
            self.refresh()
        def mass_drop():
            results = {}
            for agent_id in agent_ids:
                try:
                    results[agent_id] = self.api.drop_agent_authorizations(agent_id)
                except Exception as e:
                    results[agent_id] = str(e)
            return results
        async_operation(mass_drop, callback=callback, ui_widget=self)

    def refresh(self):
        """Refresh the agent list from the API."""
        if not self._get_cached_auth_state():
            self.log("🔐 Authentication required.")
            return

        # Show loading dialog
        loading_dialog = LoadingDialog(self.winfo_toplevel(), "Loading agents...")
        self.refresh_btn.set_enabled(False, "Loading...")
        self.status.set("Loading agents...")
        
        def callback(result):
            # Close loading dialog
            loading_dialog.close()
            self.refresh_btn.set_enabled(True)
            
            if isinstance(result, Exception):
                self.status.set(f"Error: {result}")
                self.log(f"❌ Error loading agents: {result}")
                return
            
            # Bulk delete all existing rows (efficient)
            self.tree.delete(*self.tree.get_children())
            
            # Clear stored data and invalidate selection cache
            self._agents_data.clear()
            self._selection_is_dirty = True
            
            # Fill tree in chunks to prevent UI freezing
            if result:
                self._fill_tree_chunked(result)
            else:
                # No agents
                self.status.set("No agents found.")
                self.log("ℹ️ No agents found.")
                self._update_button_states()
        
        async_operation(self.api.list_agent_space_agents, callback=callback, ui_widget=self)

    def delete_selected(self):
        """Delete selected agents."""
        # Use cached selection to avoid redundant tree.selection() call
        selection = self._get_selection()
        if not selection:
            return

        count = len(selection)
        if not messagebox.askyesno("Confirm", f"Delete {count} agent{'s' if count != 1 else ''}?"):
            return

        # Get all selected agents
        agents_to_delete = []
        for item in selection:
            values = self.tree.item(item, "values")
            if len(values) >= 4:
                agent_id = values[0]
                display_name = values[1]
                # Find full_name from the API data
                full_name = f"projects/{self.api.project_id}/locations/global/collections/default_collection/engines/{self.api.engine_name}/assistants/default_assistant/agents/{agent_id}"
                agents_to_delete.append((item, agent_id, display_name, full_name))

        if not agents_to_delete:
            return

        self.status.set(f"Deleting {count} agent{'s' if count != 1 else ''}...")

        def delete_next(index=0):
            if index >= len(agents_to_delete):
                # All done
                self.status.set(f"Deleted {count} agent{'s' if count != 1 else ''}.")
                self.log(f"✅ Deleted {count} agent{'s' if count != 1 else ''}.")
                # Update button states after deletion
                self._update_button_states()
                return

            item, agent_id, display_name, full_name = agents_to_delete[index]
            
            def callback(result):
                if isinstance(result, Exception):
                    self.log(f"❌ Failed to delete {display_name}: {result}")
                else:
                    status, message = result
                    if status == "deleted":
                        self.tree.delete(item)
                        # Invalidate selection cache since tree changed
                        self._selection_is_dirty = True
                        self.log(f"✅ Deleted agent: {display_name}")
                    else:
                        self.log(f"⚠️ {display_name}: {message}")
                
                # Continue with next deletion
                delete_next(index + 1)

            async_operation(lambda: self.api.delete_agent_from_space(full_name), callback=callback, ui_widget=self)

        delete_next()

    def show_agent_details(self):
        """Show details for the selected agent."""
        # Use cached selection to avoid redundant tree.selection() call
        sel = self._get_selection()
        if len(sel) != 1:
            messagebox.showinfo("No selection", "Select a single agent to view details.")
            return
        
        item_id = sel[0]
        if item_id not in self._agents_data:
            messagebox.showerror("Error", "Agent data not found.")
            return
        
        agent_data = self._agents_data[item_id]
        try:
            AgentDetailsDialog(self, agent_data)
        except Exception as e:
            print(f"Error opening agent details dialog: {e}")
            messagebox.showerror("Error", f"Failed to open details dialog: {e}")

    def _popup(self, event):
        """Show context menu."""
        row = self.tree.identify_row(event.y)
        if not row:
            return
        
        # Always select the right-clicked row for clarity
        # This ensures context menu operates on the visible selection
        self.tree.selection_set(row)
        self._selection_is_dirty = True
        
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
        # Update button states immediately
        self._update_button_states()

    # Add validation for required fields
    def validate_env(self):
        required_fields = ["project_id", "project_number", "location", "agent_space", "engine"]
        missing_fields = [field for field in required_fields if not getattr(self.api, field, None)]
        if missing_fields:
            messagebox.showerror("Validation Error", f"Missing required fields: {', '.join(missing_fields)}")
            return False
        return True
