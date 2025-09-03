"""Common UI components and utilities."""
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
import threading
import os
import json
from typing import Callable, Optional, Dict, Any


def async_operation(func: Callable, *args, callback: Optional[Callable] = None, ui_widget=None):
    """Execute function asynchronously and call callback with result on UI thread."""
    def run():
        try:
            result = func(*args)
        except Exception as e:
            result = e
        if callback and ui_widget:
            try:
                ui_widget.after(0, lambda: callback(result))
            except RuntimeError:
                # Handle case where widget is destroyed or not in main loop
                pass
    
    threading.Thread(target=run, daemon=True).start()


class LogConsole(ttk.Frame):
    """Scrollable text console for logging messages with automatic trimming."""
    
    def __init__(self, master, max_lines=1000):
        super().__init__(master)
        self.max_lines = max_lines
        self.text = ScrolledText(self, wrap="word", height=10)
        self.text.pack(fill="both", expand=True)

    def log(self, msg: str):
        """Add a message to the console with automatic trimming to prevent memory bloat."""
        self.text.insert("end", msg + "\n")
        
        # Trim if we exceed max_lines to prevent performance degradation
        current_lines = int(self.text.index("end-1c").split('.')[0])
        if current_lines > self.max_lines:
            # Delete from beginning until we're back to max_lines
            lines_to_delete = current_lines - self.max_lines
            self.text.delete("1.0", f"{lines_to_delete + 1}.0")
        
        self.text.see("end")

    def clear(self):
        """Clear the console."""
        self.text.delete("1.0", "end")


class CreateReasoningEngineDialog(tk.Toplevel):
    """Dialog for creating a new reasoning engine with metadata."""
    
    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.title("Create Reasoning Engine")
        self.resizable(False, False)
        self.attributes('-topmost', True)
        self.result = None
        self.api = api_client

        frm = ttk.Frame(self, padding=15)
        frm.pack(fill="both", expand=True)

        # Auto-populate from config/profile
        try:
            profile = getattr(self.api, '_profile', {})
            config_display_name = profile.get("display_name", "Your Agent")
            config_description = profile.get("description", "Live Agent")
            config_requirements = profile.get("requirements", [])
            config_extra_packages = profile.get("extra_packages", [])
            config_tool_description = profile.get("tool_description", "Tooling")
        except Exception:
            # Fallback values if profile access fails
            config_display_name = "Your Agent"
            config_description = "Live Agent"
            config_requirements = []
            config_extra_packages = []
            config_tool_description = "Tooling"

        # Display Name
        ttk.Label(frm, text="Display Name:", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky="nw", pady=(0, 5))
        self.display_name_var = tk.StringVar(value=config_display_name)
        ttk.Entry(frm, textvariable=self.display_name_var, width=50).grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=(0, 5))

        # Description
        ttk.Label(frm, text="Description:", font=("TkDefaultFont", 10, "bold")).grid(row=1, column=0, sticky="nw", pady=(0, 5))
        self.description_var = tk.StringVar(value=config_description)
        ttk.Entry(frm, textvariable=self.description_var, width=50).grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(0, 5))

        # Tool Description
        ttk.Label(frm, text="Tool Description:", font=("TkDefaultFont", 10, "bold")).grid(row=2, column=0, sticky="nw", pady=(0, 5))
        self.tool_description_var = tk.StringVar(value=config_tool_description)
        ttk.Entry(frm, textvariable=self.tool_description_var, width=50).grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=(0, 5))

        # Requirements (one per line)
        ttk.Label(frm, text="Requirements:", font=("TkDefaultFont", 10, "bold")).grid(row=3, column=0, sticky="nw", pady=(0, 5))
        requirements_frame = ttk.Frame(frm)
        requirements_frame.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=(0, 5))
        
        self.requirements_text = tk.Text(requirements_frame, height=4, width=50, wrap="word")
        self.requirements_text.pack(side="left", fill="both", expand=True)
        
        req_scroll = ttk.Scrollbar(requirements_frame, orient="vertical", command=self.requirements_text.yview)
        self.requirements_text.configure(yscrollcommand=req_scroll.set)
        req_scroll.pack(side="right", fill="y")
        
        # Pre-populate requirements
        if config_requirements:
            self.requirements_text.insert("1.0", "\n".join(config_requirements))

        # Extra Packages (one per line)
        ttk.Label(frm, text="Extra Packages:", font=("TkDefaultFont", 10, "bold")).grid(row=4, column=0, sticky="nw", pady=(0, 5))
        packages_frame = ttk.Frame(frm)
        packages_frame.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=(0, 5))
        
        self.packages_text = tk.Text(packages_frame, height=4, width=50, wrap="word")
        self.packages_text.pack(side="left", fill="both", expand=True)
        
        pkg_scroll = ttk.Scrollbar(packages_frame, orient="vertical", command=self.packages_text.yview)
        self.packages_text.configure(yscrollcommand=pkg_scroll.set)
        pkg_scroll.pack(side="right", fill="y")
        
        # Pre-populate extra packages
        if config_extra_packages:
            self.packages_text.insert("1.0", "\n".join(config_extra_packages))

        # Agent Import (only for live mode)
        agent_import_value = getattr(self.api, 'agent_import', '') or ''
        if self.api.is_live:
            ttk.Label(frm, text="Agent Import:", font=("TkDefaultFont", 10, "bold")).grid(row=5, column=0, sticky="nw", pady=(0, 5))
            self.agent_import_var = tk.StringVar(value=agent_import_value)
            ttk.Entry(frm, textvariable=self.agent_import_var, width=50).grid(row=5, column=1, sticky="ew", padx=(10, 0), pady=(0, 5))
            
            # Help text for agent import
            help_label = ttk.Label(frm, text="Format: module:attribute (e.g., my_agent:agent)", 
                                 font=("TkDefaultFont", 8), foreground="gray")
            help_label.grid(row=6, column=1, sticky="w", padx=(10, 0), pady=(0, 10))
            current_row = 7
        else:
            current_row = 5

        # Buttons
        btns = ttk.Frame(frm)
        btns.grid(row=current_row, column=0, columnspan=2, pady=(15, 0), sticky="e")
        ttk.Button(btns, text="Cancel", command=self._cancel).pack(side="right", padx=(4, 0))
        ttk.Button(btns, text="Create Engine", command=self._ok).pack(side="right")

        frm.grid_columnconfigure(1, weight=1)
        
        # Keyboard shortcuts
        self.bind("<Return>", lambda _: self._ok())
        self.bind("<Escape>", lambda _: self._cancel())
        
        # Focus the display name field
        self.display_name_var.trace_add("write", lambda *_: None)  # Ensure field is editable
        self.after(100, lambda: frm.focus_set())

    def _ok(self):
        """Validate and save the engine configuration."""
        display_name = self.display_name_var.get().strip()
        description = self.description_var.get().strip()
        tool_description = self.tool_description_var.get().strip()
        
        if not display_name:
            messagebox.showerror("Missing Display Name", "Display name is required.", parent=self)
            return
        
        if not description:
            messagebox.showerror("Missing Description", "Description is required.", parent=self)
            return

        # Parse requirements and extra packages
        requirements_text = self.requirements_text.get("1.0", "end-1c").strip()
        requirements = [line.strip() for line in requirements_text.split("\n") if line.strip()]
        
        packages_text = self.packages_text.get("1.0", "end-1c").strip()
        extra_packages = [line.strip() for line in packages_text.split("\n") if line.strip()]

        # Agent import (live mode only)
        agent_import = ""
        if self.api.is_live:
            agent_import = self.agent_import_var.get().strip()
            if not agent_import:
                messagebox.showerror("Missing Agent Import", 
                                   "Agent import is required for live mode (format: module:attribute).", 
                                   parent=self)
                return

        self.result = {
            "display_name": display_name,
            "description": description,
            "tool_description": tool_description,
            "requirements": requirements,
            "extra_packages": extra_packages,
            "agent_import": agent_import
        }
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


class CreateReasoningEngineAdvancedDialog(tk.Toplevel):
    """Advanced dialog for creating reasoning engines with flexible project support."""
    
    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.title("Create Reasoning Engine - Advanced")
        self.resizable(True, True)
        self.geometry("750x725")  # Increased from 700x800 for better visibility
        self.attributes('-topmost', True)
        self.result = None
        self.api = api_client

        # Create main scrollable frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel to canvas (bind to canvas only, not globally)
        def _on_mousewheel(event):
            try:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                # Canvas destroyed, ignore
                pass
        canvas.bind("<MouseWheel>", _on_mousewheel)
        self._canvas = canvas  # Store reference for cleanup

        frm = scrollable_frame
        current_row = 0

        # === ENGINE METADATA ===
        meta_frame = ttk.LabelFrame(frm, text="Engine Configuration", padding=15)
        meta_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 15))
        meta_frame.grid_columnconfigure(1, weight=1)
        current_row += 1

        # Auto-populate staging bucket from config
        try:
            config_bucket = getattr(self.api, 'staging_bucket', 'gs://my-staging-bucket')
        except Exception:
            config_bucket = 'gs://my-staging-bucket'

        # Staging Bucket
        ttk.Label(meta_frame, text="Staging Bucket:", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky="nw", pady=(0, 5))
        self.bucket_var = tk.StringVar(value=config_bucket)
        bucket_frame = ttk.Frame(meta_frame)
        bucket_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=(0, 5))
        ttk.Entry(bucket_frame, textvariable=self.bucket_var, width=35).pack(side="left", fill="x", expand=True)
        ttk.Label(bucket_frame, text="(gs:// prefix optional)", font=("TkDefaultFont", 8), foreground="gray").pack(side="right", padx=(5, 0))

        # Display Name
        ttk.Label(meta_frame, text="Display Name:", font=("TkDefaultFont", 10, "bold")).grid(row=1, column=0, sticky="nw", pady=(0, 5))
        self.display_name_var = tk.StringVar(value="Meeting Follow-Up Assistant")
        ttk.Entry(meta_frame, textvariable=self.display_name_var, width=40).grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(0, 5))

        # Description
        ttk.Label(meta_frame, text="Description:", font=("TkDefaultFont", 10, "bold")).grid(row=2, column=0, sticky="nw", pady=(0, 5))
        self.description_var = tk.StringVar(value="AI-powered assistant with Gmail + Calendar")
        ttk.Entry(meta_frame, textvariable=self.description_var, width=40).grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=(0, 5))

        # === AGENT SOURCE CONFIGURATION ===
        source_frame = ttk.LabelFrame(frm, text="Agent Source Configuration", padding=15)
        source_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 15))
        source_frame.grid_columnconfigure(1, weight=1)
        current_row += 1

        # Agent File - simplified to just file picker
        ttk.Label(source_frame, text="Agent File:", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky="nw", pady=(0, 5))
        file_frame = ttk.Frame(source_frame)
        file_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=(0, 5))
        self.agent_file_var = tk.StringVar(value="/Users/me/projects/my_agent_project/agent.py")
        ttk.Entry(file_frame, textvariable=self.agent_file_var, width=40).pack(side="left", fill="x", expand=True)
        ttk.Button(file_frame, text="Browse", command=self._browse_agent_file).pack(side="right", padx=(5, 0))
        
        # Help text
        ttk.Label(source_frame, text="Select the Python file containing your 'root_agent' definition", 
                 font=("TkDefaultFont", 8), foreground="gray").grid(row=1, column=1, sticky="w", padx=(10, 0))

        # === REQUIREMENTS CONFIGURATION ===
        req_frame = ttk.LabelFrame(frm, text="Requirements Configuration", padding=15)
        req_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 15))
        req_frame.grid_columnconfigure(1, weight=1)
        current_row += 1

        # Requirements source (Radio buttons)
        ttk.Label(req_frame, text="Requirements Source:", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky="nw", pady=(0, 5))
        
        req_source_frame = ttk.Frame(req_frame)
        req_source_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=(0, 5))
        
        self.req_source_var = tk.StringVar(value="file")
        
        # Requirements file option
        req_file_frame = ttk.Frame(req_source_frame)
        req_file_frame.pack(fill="x", pady=(0, 5))
        ttk.Radiobutton(req_file_frame, text="requirements.txt file:", variable=self.req_source_var, 
                       value="file", command=self._toggle_req_source).pack(side="left")
        self.req_file_var = tk.StringVar(value="requirements.txt")
        self.req_file_entry = ttk.Entry(req_file_frame, textvariable=self.req_file_var, width=25)
        self.req_file_entry.pack(side="left", padx=(10, 0), fill="x", expand=True)
        self.req_file_button = ttk.Button(req_file_frame, text="Browse", command=self._browse_req_file)
        self.req_file_button.pack(side="right", padx=(5, 0))
        
        # Paste requirements option
        req_text_frame = ttk.Frame(req_source_frame)
        req_text_frame.pack(fill="x", pady=(0, 5))
        ttk.Radiobutton(req_text_frame, text="Paste here:", variable=self.req_source_var, 
                       value="text", command=self._toggle_req_source).pack(side="left")
        
        # Requirements text area
        self.req_text_frame = ttk.Frame(req_frame)
        self.req_text_frame.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(5, 0))
        
        self.req_text = tk.Text(self.req_text_frame, height=6, width=50, wrap="word", state="disabled")
        self.req_text.pack(side="left", fill="both", expand=True)
        
        req_text_scroll = ttk.Scrollbar(self.req_text_frame, orient="vertical", command=self.req_text.yview)
        self.req_text.configure(yscrollcommand=req_text_scroll.set)
        req_text_scroll.pack(side="right", fill="y")
        
        # Default requirements text
        default_reqs = """pydantic>=2.0.0
google-auth>=2.23.0
google-adk>=1.0.0
google-cloud-aiplatform[adk,agent-engines]>=1.93.0
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.1.0
google-api-python-client>=2.86.0"""
        self.req_text.config(state="normal")
        self.req_text.insert("1.0", default_reqs)
        self.req_text.config(state="disabled")

        # === OPTIONS ===
        options_frame = ttk.LabelFrame(frm, text="Deployment Options", padding=15)
        options_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 15))
        current_row += 1

        # Exclude dev files checkbox
        self.exclude_dev_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Exclude dev files (.env, __pycache__, .git, tests, etc.)", 
                       variable=self.exclude_dev_var).pack(anchor="w")

        # Enable tracing checkbox
        self.enable_tracing_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Enable tracing for debugging", 
                       variable=self.enable_tracing_var).pack(anchor="w", pady=(5, 0))

        # === BUTTONS ===
        button_frame = ttk.Frame(frm)
        button_frame.grid(row=current_row, column=0, sticky="ew", pady=(20, 0))
        
        # Left side buttons (utility functions)
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side="left")
        ttk.Button(left_buttons, text="Populate with JSON", command=self._populate_from_json).pack(side="left", padx=(0, 4))
        ttk.Button(left_buttons, text="Export to JSON", command=self._export_to_json).pack(side="left")
        ttk.Button(left_buttons, text="Cancel", command=self._cancel).pack(side="right", padx=(4, 0))
        
        # Right side buttons (main actions)
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side="right")
        ttk.Button(right_buttons, text="Finalize Reasoning Engine", command=self._ok).pack(side="right")

        # Configure column weights
        frm.grid_columnconfigure(0, weight=1)

        # Initialize UI state
        self._toggle_req_source()
        
        # Keyboard shortcuts
        self.bind("<Return>", lambda _: self._ok())
        self.bind("<Escape>", lambda _: self._cancel())
        
        # Ensure proper cleanup on window close
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        
        # Focus
        self.focus_set()

    def _cleanup(self):
        """Clean up resources to prevent memory leaks."""
        # Cleanup is handled automatically since we bind to canvas, not globally
        pass

    def _browse_directory(self):
        """Browse for agent directory."""
        directory = filedialog.askdirectory(title="Select Agent Project Directory")
        if directory:
            self.agent_dir_var.set(directory)

    def _browse_agent_file(self):
        """Browse for agent Python file and automatically set directory."""
        file_path = filedialog.askopenfilename(
            title="Select Agent Python File (containing root_agent)",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if file_path:
            self.agent_file_var.set(file_path)
            # Automatically infer and set the directory from the file path
            agent_directory = os.path.dirname(file_path)
            print(f"🔍 Auto-detected agent directory: {agent_directory}")

    def _browse_req_file(self):
        """Browse for requirements file."""
        file_path = filedialog.askopenfilename(
            title="Select Requirements File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.req_file_var.set(file_path)

    def _toggle_agent_source(self):
        """No longer needed - simplified to just file picker."""
        pass

    def _toggle_req_source(self):
        """Toggle requirements source input fields."""
        if self.req_source_var.get() == "file":
            self.req_file_entry.config(state="normal")
            self.req_file_button.config(state="normal")
            self.req_text.config(state="disabled")
        else:
            self.req_file_entry.config(state="disabled")
            self.req_file_button.config(state="disabled")
            self.req_text.config(state="normal")

    def _validate(self):
        """Validate the current configuration."""
        errors = []
        
        # Validate staging bucket
        if not self.bucket_var.get().strip():
            errors.append("Staging bucket is required")
        
        # Validate agent file
        agent_file_path = self.agent_file_var.get().strip()
        if not agent_file_path:
            errors.append("Agent file path is required")
        elif not os.path.exists(agent_file_path):
            errors.append(f"Agent file does not exist: {agent_file_path}")
        
        # Validate requirements source
        if self.req_source_var.get() == "file":
            req_file = self.req_file_var.get().strip()
            if req_file and not os.path.exists(req_file):
                errors.append(f"Requirements file does not exist: {req_file}")
        else:
            req_text = self.req_text.get("1.0", "end-1c").strip()
            if not req_text:
                errors.append("Requirements text is empty")
        
        # Validate metadata
        if not self.display_name_var.get().strip():
            errors.append("Display name is required")
        
        # Show results
        if errors:
            messagebox.showerror("Validation Errors", "\n".join(f"• {err}" for err in errors), parent=self)
        else:
            messagebox.showinfo("Validation Success", "✅ Configuration is valid!", parent=self)

    def _populate_from_json(self):
        """Populate dialog fields from a JSON file."""
        file_path = filedialog.askopenfilename(
            title="Select Configuration JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            parent=self
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r') as f:
                config = json.load(f)
            
            # Populate basic fields
            if "staging_bucket" in config:
                self.bucket_var.set(config["staging_bucket"])
            if "display_name" in config:
                self.display_name_var.set(config["display_name"])
            if "description" in config:
                self.description_var.set(config["description"])
            
            # Populate agent file path
            if "agent_file_path" in config:
                self.agent_file_var.set(config["agent_file_path"])
            
            # Populate requirements
            if "requirements_source_type" in config:
                self.req_source_var.set(config["requirements_source_type"])
                self._toggle_req_source()  # Update UI state
                
                if config["requirements_source_type"] == "file" and "requirements_file" in config:
                    self.req_file_var.set(config["requirements_file"])
                elif config["requirements_source_type"] == "text" and "requirements_text" in config:
                    self.req_text.config(state="normal")
                    self.req_text.delete("1.0", "end")
                    self.req_text.insert("1.0", config["requirements_text"])
                    # Note: req_text state is managed by _toggle_req_source
            
            # Populate options
            if "exclude_dev_files" in config:
                self.exclude_dev_var.set(bool(config["exclude_dev_files"]))
            if "enable_tracing" in config:
                self.enable_tracing_var.set(bool(config["enable_tracing"]))
            
            messagebox.showinfo("Configuration Loaded", 
                              f"✅ Configuration successfully loaded from:\n{os.path.basename(file_path)}", 
                              parent=self)
            
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON Error", 
                               f"Invalid JSON file:\n{str(e)}", 
                               parent=self)
        except Exception as e:
            messagebox.showerror("Load Error", 
                               f"Failed to load configuration:\n{str(e)}", 
                               parent=self)

    def _export_to_json(self):
        """Export current dialog configuration to a JSON file."""
        # Get project info from API client
        try:
            project_id = getattr(self.api, 'project_id', 'unknown-project')
            location = getattr(self.api, 'location', 'us-central1')
        except Exception:
            project_id = 'unknown-project'
            location = 'us-central1'
        
        # Collect current configuration
        config = {
            "project_id": project_id,
            "location": location,
            "staging_bucket": self.bucket_var.get().strip(),
            "agent_file_path": self.agent_file_var.get().strip(),
            "requirements_source_type": self.req_source_var.get(),
            "requirements_file": self.req_file_var.get().strip() if self.req_source_var.get() == "file" else None,
            "requirements_text": self.req_text.get("1.0", "end-1c").strip() if self.req_source_var.get() == "text" else None,
            "display_name": self.display_name_var.get().strip(),
            "description": self.description_var.get().strip(),
            "exclude_dev_files": self.exclude_dev_var.get(),
            "enable_tracing": self.enable_tracing_var.get(),
            "_metadata": {
                "exported_from": "AgentSpaceDeploymentService",
                "dialog_version": "1.0",
                "export_timestamp": str(__import__('datetime').datetime.now())
            }
        }
        
        # Remove None values for cleaner JSON
        config = {k: v for k, v in config.items() if v is not None}
        
        # Default filename based on display name
        default_name = self.display_name_var.get().strip()
        if default_name:
            default_filename = f"{default_name.lower().replace(' ', '_')}_config.json"
        else:
            default_filename = "reasoning_engine_config.json"
        
        file_path = filedialog.asksaveasfilename(
            title="Save Configuration as JSON",
            defaultextension=".json",
            initialfile=default_filename,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            parent=self
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            messagebox.showinfo("Configuration Exported", 
                              f"✅ Configuration successfully exported to:\n{os.path.basename(file_path)}", 
                              parent=self)
            
        except Exception as e:
            messagebox.showerror("Export Error", 
                               f"Failed to export configuration:\n{str(e)}", 
                               parent=self)

    def _ok(self):
        import os
        """Validate and save the configuration."""
        # Run validation first
        errors = []
        
        # Validate staging bucket
        if not self.bucket_var.get().strip():
            errors.append("Staging bucket is required")
        
        # Validate agent file
        agent_file = self.agent_file_var.get().strip()
        if not agent_file:
            errors.append("Agent file is required")
        elif not os.path.exists(agent_file):
            errors.append(f"Agent file does not exist: {agent_file}")
        
        # Validate requirements source
        if self.req_source_var.get() == "file":
            req_file = self.req_file_var.get().strip()
            if req_file and not os.path.exists(req_file):
                errors.append(f"Requirements file does not exist: {req_file}")
        else:
            req_text = self.req_text.get("1.0", "end-1c").strip()
            if not req_text:
                errors.append("Requirements text is empty")
        
        # Validate metadata
        if not self.display_name_var.get().strip():
            errors.append("Display name is required")
        
        # Show validation errors if any
        if errors:
            messagebox.showerror("Validation Errors", "\n".join(f"• {err}" for err in errors), parent=self)
            return
        
        # Get project info from API client
        try:
            project_id = getattr(self.api, 'project_id', 'unknown-project')
            location = getattr(self.api, 'location', 'us-central1')
        except Exception:
            project_id = 'unknown-project'
            location = 'us-central1'
        
        # Collect all configuration
        import os
        agent_file_path = self.agent_file_var.get().strip()
        agent_directory = os.path.dirname(agent_file_path) if agent_file_path else ""
        
        config = {
            "project_id": project_id,
            "location": location,
            "staging_bucket": self.bucket_var.get().strip(),
            "agent_directory": agent_directory,  # Auto-inferred from file path
            "agent_file_path": agent_file_path,
            "requirements_source_type": self.req_source_var.get(),
            "requirements_file": self.req_file_var.get().strip() if self.req_source_var.get() == "file" else None,
            "requirements_text": self.req_text.get("1.0", "end-1c").strip() if self.req_source_var.get() == "text" else None,
            "display_name": self.display_name_var.get().strip(),
            "description": self.description_var.get().strip(),
            "exclude_dev_files": self.exclude_dev_var.get(),
            "enable_tracing": self.enable_tracing_var.get()
        }
        
        self.result = config
        self._cleanup()
        self.destroy()

    def _cancel(self):
        """Cancel dialog."""
        self.result = None
        self._cleanup()
        self.destroy()


class DeployToAgentSpaceDialog(tk.Toplevel):
    """Dialog for deploying reasoning engine to Agent Space with full configuration."""
    
    def __init__(self, parent, api_client, engine_resource_name: str = ""):
        super().__init__(parent)
        self.title("Deploy to Agent Space")
        self.resizable(False, False)
        self.attributes('-topmost', True)
        self.result = None
        self.api = api_client
        self.engine_resource_name = engine_resource_name

        frm = ttk.Frame(self, padding=15)
        frm.pack(fill="both", expand=True)

        # Auto-populate from config/profile
        try:
            profile = getattr(self.api, '_profile', {})
            config_display_name = profile.get("display_name", "Your Agent")
            config_description = profile.get("description", "Live Agent")
            config_tool_description = profile.get("tool_description", "Tooling")
        except Exception:
            # Fallback values if profile access fails
            config_display_name = "Your Agent"
            config_description = "Live Agent"
            config_tool_description = "Tooling"

        # Engine Info (read-only)
        ttk.Label(frm, text="Reasoning Engine:", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky="nw", pady=(0, 5))
        engine_display = engine_resource_name if engine_resource_name else "Current Engine"
        ttk.Label(frm, text=engine_display, wraplength=400, foreground="gray").grid(row=0, column=1, sticky="nw", padx=(10, 0), pady=(0, 5))

        # Agent Display Name
        ttk.Label(frm, text="Agent Display Name:", font=("TkDefaultFont", 10, "bold")).grid(row=1, column=0, sticky="nw", pady=(0, 5))
        self.agent_display_name_var = tk.StringVar(value=config_display_name)
        ttk.Entry(frm, textvariable=self.agent_display_name_var, width=50).grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(0, 5))

        # Agent Description
        ttk.Label(frm, text="Agent Description:", font=("TkDefaultFont", 10, "bold")).grid(row=2, column=0, sticky="nw", pady=(0, 5))
        self.agent_description_var = tk.StringVar(value=config_description)
        ttk.Entry(frm, textvariable=self.agent_description_var, width=50).grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=(0, 5))

        # Tool Description
        ttk.Label(frm, text="Tool Description:", font=("TkDefaultFont", 10, "bold")).grid(row=3, column=0, sticky="nw", pady=(0, 5))
        self.tool_description_var = tk.StringVar(value=config_tool_description)
        ttk.Entry(frm, textvariable=self.tool_description_var, width=50).grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=(0, 5))

        # Authorization section
        auth_frame = ttk.LabelFrame(frm, text="Authorization Settings", padding=10)
        auth_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(15, 0))
        auth_frame.grid_columnconfigure(1, weight=1)

        # Enable Authorization checkbox
        self.with_auth_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(auth_frame, text="Configure OAuth Authorization", 
                       variable=self.with_auth_var, command=self._toggle_auth).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))

        # Authorization Name
        ttk.Label(auth_frame, text="Authorization Name:").grid(row=1, column=0, sticky="nw", pady=(0, 5))
        self.auth_name_var = tk.StringVar(value="default-auth")
        self.auth_entry = ttk.Entry(auth_frame, textvariable=self.auth_name_var, width=40)
        self.auth_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(0, 5))

        # Help text for authorization
        self.auth_help = ttk.Label(auth_frame, text="Authorization will be created/attached for OAuth access", 
                                 font=("TkDefaultFont", 8), foreground="gray")
        self.auth_help.grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 5))

        # Advanced section (collapsible)
        self.show_advanced_var = tk.BooleanVar(value=False)
        advanced_check = ttk.Checkbutton(frm, text="Show Advanced Settings", 
                                       variable=self.show_advanced_var, command=self._toggle_advanced)
        advanced_check.grid(row=5, column=0, columnspan=2, sticky="w", pady=(15, 5))

        # Advanced frame (initially hidden)
        self.advanced_frame = ttk.LabelFrame(frm, text="Advanced Settings", padding=10)
        
        # Project details (read-only, for reference)
        ttk.Label(self.advanced_frame, text="Project ID:", font=("TkDefaultFont", 9)).grid(row=0, column=0, sticky="nw", pady=(0, 3))
        ttk.Label(self.advanced_frame, text=getattr(self.api, 'project_id', 'N/A'), 
                 font=("TkDefaultFont", 9), foreground="gray").grid(row=0, column=1, sticky="nw", padx=(10, 0), pady=(0, 3))

        ttk.Label(self.advanced_frame, text="Project Number:", font=("TkDefaultFont", 9)).grid(row=1, column=0, sticky="nw", pady=(0, 3))
        ttk.Label(self.advanced_frame, text=getattr(self.api, 'project_number', 'N/A'), 
                 font=("TkDefaultFont", 9), foreground="gray").grid(row=1, column=1, sticky="nw", padx=(10, 0), pady=(0, 3))

        ttk.Label(self.advanced_frame, text="Location:", font=("TkDefaultFont", 9)).grid(row=2, column=0, sticky="nw", pady=(0, 3))
        ttk.Label(self.advanced_frame, text=getattr(self.api, 'location', 'N/A'), 
                 font=("TkDefaultFont", 9), foreground="gray").grid(row=2, column=1, sticky="nw", padx=(10, 0), pady=(0, 3))

        ttk.Label(self.advanced_frame, text="Engine Name:", font=("TkDefaultFont", 9)).grid(row=3, column=0, sticky="nw", pady=(0, 3))
        ttk.Label(self.advanced_frame, text=getattr(self.api, 'engine_name', 'N/A'), 
                 font=("TkDefaultFont", 9), foreground="gray").grid(row=3, column=1, sticky="nw", padx=(10, 0), pady=(0, 3))

        self.advanced_frame.grid_columnconfigure(1, weight=1)

        # Buttons
        btns = ttk.Frame(frm)
        btns.grid(row=7, column=0, columnspan=2, pady=(20, 0), sticky="e")
        ttk.Button(btns, text="Cancel", command=self._cancel).pack(side="right", padx=(4, 0))
        ttk.Button(btns, text="Deploy to Agent Space", command=self._ok).pack(side="right")

        frm.grid_columnconfigure(1, weight=1)
        
        # Keyboard shortcuts
        self.bind("<Return>", lambda _: self._ok())
        self.bind("<Escape>", lambda _: self._cancel())
        
        # Initialize UI state
        self._toggle_auth()
        self._toggle_advanced()
        
        # Focus the agent display name field
        self.after(100, lambda: self.agent_display_name_var.get() and None)

    def _toggle_auth(self):
        """Toggle authorization fields based on checkbox."""
        enabled = self.with_auth_var.get()
        state = "normal" if enabled else "disabled"
        self.auth_entry.config(state=state)
        self.auth_help.config(foreground="black" if enabled else "gray")

    def _toggle_advanced(self):
        """Toggle advanced settings visibility."""
        if self.show_advanced_var.get():
            self.advanced_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        else:
            self.advanced_frame.grid_remove()

    def _ok(self):
        """Validate and save the deployment configuration."""
        agent_display_name = self.agent_display_name_var.get().strip()
        agent_description = self.agent_description_var.get().strip()
        tool_description = self.tool_description_var.get().strip()
        with_authorization = self.with_auth_var.get()
        auth_name = self.auth_name_var.get().strip()
        
        if not agent_display_name:
            messagebox.showerror("Missing Agent Display Name", "Agent display name is required.", parent=self)
            return
        
        if not agent_description:
            messagebox.showerror("Missing Agent Description", "Agent description is required.", parent=self)
            return

        if with_authorization and not auth_name:
            messagebox.showerror("Missing Authorization Name", 
                               "Authorization name is required when OAuth is enabled.", parent=self)
            return

        self.result = {
            "agent_display_name": agent_display_name,
            "agent_description": agent_description,
            "tool_description": tool_description,
            "with_authorization": with_authorization,
            "authorization_name": auth_name
        }
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


class DeployDialog(tk.Toplevel):
    """Dialog for configuring deployment to Agent Space."""
    
    def __init__(self, parent, default_auth_name: str = "", default_with_auth: bool = True):
        super().__init__(parent)
        self.title("Deploy to Agent Space")
        self.resizable(False, False)
        self.attributes('-topmost', True)
        self.result = None

        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Authorization name").grid(row=0, column=0, sticky="w")
        self.auth_var = tk.StringVar(value=default_auth_name)
        ttk.Entry(frm, textvariable=self.auth_var, width=40).grid(row=0, column=1, padx=(8, 0), sticky="we")

        self.chk_var = tk.BooleanVar(value=default_with_auth)
        ttk.Checkbutton(frm, text="Configure OAuth (create/attach authorization)", variable=self.chk_var)\
            .grid(row=1, column=0, columnspan=2, pady=(8, 0), sticky="w")

        btns = ttk.Frame(frm)
        btns.grid(row=2, column=0, columnspan=2, pady=(12, 0), sticky="e")
        ttk.Button(btns, text="Cancel", command=self._cancel).pack(side="right", padx=4)
        ttk.Button(btns, text="Deploy", command=self._ok).pack(side="right")

        frm.grid_columnconfigure(1, weight=1)
        self.bind("<Return>", lambda _: self._ok())
        self.bind("<Escape>", lambda _: self._cancel())

    def _ok(self):
        name = self.auth_var.get().strip()
        with_auth = self.chk_var.get()
        if with_auth and not name:
            messagebox.showerror("Missing authorization name", "Provide an authorization name or uncheck OAuth.")
            return
        self.result = {"authorization_name": name, "with_authorization": with_auth}
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


class AgentDetailsDialog(tk.Toplevel):
    """Dialog for displaying detailed agent information."""
    
    def __init__(self, parent, agent_data: dict):
        super().__init__(parent)
        self.title(f"Agent Details - {agent_data.get('display_name', 'Unknown')}")
        self.resizable(True, True)
        self.geometry("700x450")
        
        # Improved dialog setup for reliability
        self.transient(parent)
        
        # Defer grab_set to avoid blocking issues
        self.after(1, self._setup_modal)
        
        # Store variables as instance attributes to avoid garbage collection
        self.resource_var = tk.StringVar(value=agent_data.get("full_name", "N/A"))
        auth_full = agent_data.get("authorization_full", "")
        engine_full = agent_data.get("engine_full", "")
        
        if auth_full and auth_full != "N/A":
            self.auth_var = tk.StringVar(value=auth_full)
        else:
            self.auth_var = None
            
        if engine_full and engine_full != "N/A":
            self.engine_var = tk.StringVar(value=engine_full)
        else:
            self.engine_var = None

        frm = ttk.Frame(self, padding=15)
        frm.pack(fill="both", expand=True)

        # Agent details
        ttk.Label(frm, text="Agent ID:", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky="nw", pady=(0, 5))
        ttk.Label(frm, text=agent_data.get("id", "N/A"), wraplength=400).grid(row=0, column=1, sticky="nw", padx=(10, 0), pady=(0, 5))

        ttk.Label(frm, text="Display Name:", font=("TkDefaultFont", 10, "bold")).grid(row=1, column=0, sticky="nw", pady=(0, 5))
        ttk.Label(frm, text=agent_data.get("display_name", "N/A"), wraplength=400).grid(row=1, column=1, sticky="nw", padx=(10, 0), pady=(0, 5))

        # Authorization ID (short name)
        ttk.Label(frm, text="Authorization ID:", font=("TkDefaultFont", 10, "bold")).grid(row=2, column=0, sticky="nw", pady=(0, 5))
        auth_id = agent_data.get("authorization_id", "N/A")
        ttk.Label(frm, text=auth_id, wraplength=400).grid(row=2, column=1, sticky="nw", padx=(10, 0), pady=(0, 5))

        # Engine ID (short name)
        ttk.Label(frm, text="Engine ID:", font=("TkDefaultFont", 10, "bold")).grid(row=3, column=0, sticky="nw", pady=(0, 5))
        engine_id = agent_data.get("engine_id", "N/A")
        ttk.Label(frm, text=engine_id, wraplength=400).grid(row=3, column=1, sticky="nw", padx=(10, 0), pady=(0, 5))

        # Full Resource Name with copy button
        ttk.Label(frm, text="Full Resource Name:", font=("TkDefaultFont", 10, "bold")).grid(row=4, column=0, sticky="nw", pady=(0, 10))
        
        resource_frame = ttk.Frame(frm)
        resource_frame.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=(0, 10))
        
        resource_entry = ttk.Entry(resource_frame, textvariable=self.resource_var, state="readonly", width=50)
        resource_entry.pack(side="left", fill="x", expand=True)
        
        copy_resource_btn = ttk.Button(resource_frame, text="Copy", command=self._copy_resource_name)
        copy_resource_btn.pack(side="right", padx=(5, 0))

        current_row = 5

        # Full Authorization Path with copy button (if available)
        if self.auth_var:
            ttk.Label(frm, text="Full Authorization Path:", font=("TkDefaultFont", 10, "bold")).grid(row=current_row, column=0, sticky="nw", pady=(0, 10))
            
            auth_frame = ttk.Frame(frm)
            auth_frame.grid(row=current_row, column=1, sticky="ew", padx=(10, 0), pady=(0, 10))
            
            auth_entry = ttk.Entry(auth_frame, textvariable=self.auth_var, state="readonly", width=50)
            auth_entry.pack(side="left", fill="x", expand=True)
            
            copy_auth_btn = ttk.Button(auth_frame, text="Copy", command=self._copy_auth_path)
            copy_auth_btn.pack(side="right", padx=(5, 0))
            current_row += 1

        # Full Engine Path with copy button (if available)
        if self.engine_var:
            ttk.Label(frm, text="Full Engine Path:", font=("TkDefaultFont", 10, "bold")).grid(row=current_row, column=0, sticky="nw", pady=(0, 10))
            
            engine_frame = ttk.Frame(frm)
            engine_frame.grid(row=current_row, column=1, sticky="ew", padx=(10, 0), pady=(0, 10))
            
            engine_entry = ttk.Entry(engine_frame, textvariable=self.engine_var, state="readonly", width=50)
            engine_entry.pack(side="left", fill="x", expand=True)
            
            copy_engine_btn = ttk.Button(engine_frame, text="Copy", command=self._copy_engine_path)
            copy_engine_btn.pack(side="right", padx=(5, 0))
            current_row += 1

        # Close button
        close_btn = ttk.Button(frm, text="Close", command=self._close_dialog)
        close_btn.grid(row=current_row, column=0, columnspan=2, pady=(20, 0))

        frm.grid_columnconfigure(1, weight=1)
        self.bind("<Escape>", lambda _: self._close_dialog())
        
        # Ensure dialog is visible and focused
        self.lift()
        self.focus_set()
    
    def _setup_modal(self):
        """Set up modal behavior after dialog is fully created."""
        try:
            self.attributes('-topmost', True)
        except tk.TclError:
            # If attributes fails, dialog is still functional
            pass

    def _close_dialog(self):
        """Properly close the dialog."""
        self.destroy()

    def _copy_resource_name(self):
        """Copy resource name to clipboard."""
        try:
            self.clipboard_clear()
            self.clipboard_append(self.resource_var.get())
            messagebox.showinfo("Copied", "Resource name copied to clipboard!", parent=self)
        except Exception:
            messagebox.showerror("Error", "Failed to copy to clipboard.", parent=self)

    def _copy_auth_path(self):
        """Copy authorization path to clipboard."""
        if not self.auth_var:
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(self.auth_var.get())
            messagebox.showinfo("Copied", "Authorization path copied to clipboard!", parent=self)
        except Exception:
            messagebox.showerror("Error", "Failed to copy to clipboard.", parent=self)

    def _copy_engine_path(self):
        """Copy engine path to clipboard."""
        if not self.engine_var:
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(self.engine_var.get())
            messagebox.showinfo("Copied", "Engine path copied to clipboard!", parent=self)
        except Exception:
            messagebox.showerror("Error", "Failed to copy to clipboard.", parent=self)


class EngineDetailsDialog(tk.Toplevel):
    """Dialog for displaying detailed engine information."""
    
    def __init__(self, parent, engine_data: dict):
        super().__init__(parent)
        self.title(f"Engine Details - {engine_data.get('display_name', 'Unknown')}")
        self.resizable(True, True)
        self.geometry("600x400")
        
        # Center the dialog
        self.transient(parent)
        self.attributes('-topmost', True)
        
        # Store variable as instance attribute to avoid garbage collection
        self.resource_var = tk.StringVar(value=engine_data.get("resource_name", "N/A"))

        frm = ttk.Frame(self, padding=15)
        frm.pack(fill="both", expand=True)

        # Engine details
        ttk.Label(frm, text="Engine ID:", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky="nw", pady=(0, 5))
        ttk.Label(frm, text=engine_data.get("id", "N/A"), wraplength=400).grid(row=0, column=1, sticky="nw", padx=(10, 0), pady=(0, 5))

        ttk.Label(frm, text="Display Name:", font=("TkDefaultFont", 10, "bold")).grid(row=1, column=0, sticky="nw", pady=(0, 5))
        ttk.Label(frm, text=engine_data.get("display_name", "N/A"), wraplength=400).grid(row=1, column=1, sticky="nw", padx=(10, 0), pady=(0, 5))

        ttk.Label(frm, text="Created:", font=("TkDefaultFont", 10, "bold")).grid(row=2, column=0, sticky="nw", pady=(0, 5))
        ttk.Label(frm, text=engine_data.get("create_time", "N/A"), wraplength=400).grid(row=2, column=1, sticky="nw", padx=(10, 0), pady=(0, 5))

        ttk.Label(frm, text="Resource Name:", font=("TkDefaultFont", 10, "bold")).grid(row=3, column=0, sticky="nw", pady=(0, 10))
        
        # Resource name with copy button
        resource_frame = ttk.Frame(frm)
        resource_frame.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=(0, 10))
        
        resource_entry = ttk.Entry(resource_frame, textvariable=self.resource_var, state="readonly", width=50)
        resource_entry.pack(side="left", fill="x", expand=True)
        
        copy_btn = ttk.Button(resource_frame, text="Copy", command=self._copy_resource_name)
        copy_btn.pack(side="right", padx=(5, 0))

        # Close button
        close_btn = ttk.Button(frm, text="Close", command=self._close_dialog)
        close_btn.grid(row=4, column=0, columnspan=2, pady=(20, 0))

        frm.grid_columnconfigure(1, weight=1)
        self.bind("<Escape>", lambda _: self._close_dialog())
        
        # Focus the dialog
        self.focus_set()

    def _close_dialog(self):
        """Properly close the dialog."""
        self.destroy()

    def _copy_resource_name(self):
        """Copy resource name to clipboard."""
        try:
            self.clipboard_clear()
            self.clipboard_append(self.resource_var.get())
            messagebox.showinfo("Copied", "Resource name copied to clipboard!", parent=self)
        except Exception:
            messagebox.showerror("Error", "Failed to copy to clipboard.", parent=self)


class LoadingDialog(tk.Toplevel):
    """Loading dialog with spinner animation."""
    
    def __init__(self, parent, message="Loading..."):
        super().__init__(parent)
        
        # Initialize animation control first
        self._animation_active = True
        
        self.title("Loading")
        self.resizable(False, False)
        self.geometry("300x120")
        
        # Center the dialog
        self.transient(parent)
        self.attributes('-topmost', True)
        
        # Try to remove window decorations, but handle errors gracefully
        try:
            self.overrideredirect(True)
        except tk.TclError:
            # Fall back to normal window if overrideredirect fails
            pass
        
        # Center on parent (deferred to avoid blocking)
        self.after(0, self._center_on_parent, parent)
        
        # Create frame with border
        main_frame = ttk.Frame(self, relief="solid", borderwidth=2, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Loading message
        ttk.Label(main_frame, text=message, font=("TkDefaultFont", 11)).pack(pady=(0, 10))
        
        # Simple text-based spinner instead of progress bar (macOS compatibility)
        self.spinner_label = ttk.Label(main_frame, text="●●●", font=("TkDefaultFont", 12))
        self.spinner_label.pack(pady=(0, 10))
        
        # Start text animation
        self.spinner_states = ["●  ", " ● ", "  ●", " ● "]
        self.spinner_index = 0
        self._animate_spinner()
        
        # Cancel button (optional)
        ttk.Button(main_frame, text="Cancel", command=self.destroy).pack()
        
        # Make sure it's on top
        self.focus_set()
        self.lift()
    
    def _center_on_parent(self, parent):
        """Center dialog on parent without blocking the UI."""
        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - 150
            y = parent.winfo_y() + (parent.winfo_height() // 2) - 60
            self.geometry(f"300x120+{x}+{y}")
        except tk.TclError:
            # Fall back to default position if centering fails
            pass
        
    def _animate_spinner(self):
        """Animate the text spinner."""
        if not self._animation_active:
            return
        
        try:
            self.spinner_label.config(text=self.spinner_states[self.spinner_index])
            self.spinner_index = (self.spinner_index + 1) % len(self.spinner_states)
            self.after(300, self._animate_spinner)  # Update every 300ms
        except tk.TclError:
            # Widget destroyed, stop animation
            self._animation_active = False
        
    def close(self):
        """Properly close the loading dialog."""
        self._animation_active = False
        self.destroy()


class StatusButton(ttk.Button):
    """Button that can be enabled/disabled based on conditions with status text."""
    
    def __init__(self, master, text: str, command: Callable, **kwargs):
        super().__init__(master, text=text, command=self._wrapped_command, **kwargs)
        self._original_text = text
        self._original_command = command
        self._is_enabled = True
    
    def _wrapped_command(self):
        """Wrapped command that provides immediate visual feedback."""
        if self._is_enabled and self._original_command:
            # Provide immediate visual feedback without blocking UI
            self.config(state="active")
            # Remove blocking update_idletasks() call
            
            # Execute the actual command
            try:
                self._original_command()
            finally:
                # Restore normal state with ultra-minimal delay (5ms for immediate feel)
                self.after(5, lambda: self.config(state="normal" if self._is_enabled else "disabled"))
    
    def set_enabled(self, enabled: bool, reason: str = ""):
        """Enable/disable button with optional reason tooltip."""
        self._is_enabled = enabled
        if enabled:
            self.config(state="normal")
            self.config(text=self._original_text)
        else:
            self.config(state="disabled")
            if reason:
                # You could add tooltip here if needed
                pass
    
    @property
    def is_enabled(self) -> bool:
        return self._is_enabled
