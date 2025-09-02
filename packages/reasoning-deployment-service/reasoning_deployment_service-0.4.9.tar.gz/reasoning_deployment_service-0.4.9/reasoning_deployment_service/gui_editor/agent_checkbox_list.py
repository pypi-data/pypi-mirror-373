"""
Scrollable agent list with checkboxes for mass selection and actions.
"""
import tkinter as tk
from tkinter import ttk, messagebox

class AgentCheckboxList(tk.Frame):
    def __init__(self, master, agents, on_mass_action):
        super().__init__(master)
        self.agents = agents
        self.on_mass_action = on_mass_action
        self.vars = {}
        self._setup_ui()

    def _setup_ui(self):
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set, height=300)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for agent in self.agents:
            var = tk.BooleanVar()
            self.vars[agent["id"]] = var
            cb = tk.Checkbutton(self.scrollable_frame, text=f"{agent.get('display_name', agent['id'])}", variable=var)
            cb.pack(anchor="w", padx=4, pady=2)

        self.action_btn = ttk.Button(self, text="Drop Authorizations for Checked Agents", command=self._do_mass_action)
        self.action_btn.pack(fill="x", pady=8)

    def get_checked_agent_ids(self):
        return [aid for aid, var in self.vars.items() if var.get()]

    def _do_mass_action(self):
        checked = self.get_checked_agent_ids()
        if not checked:
            messagebox.showinfo("No agents selected", "Please check agents to drop authorizations.")
            return
        self.on_mass_action(checked)
