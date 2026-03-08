import sys
import os
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import customtkinter as ctk
from tkinter.colorchooser import askcolor

from src.chromaleague.config_manager import ConfigManager, AppConfig

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ConfiguratorGUI(ctk.CTk):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.config_manager = app.config_manager
        self.app_config = self.config_manager.load()

        self.title("ChromaLeague Configurator")
        self.geometry("800x650")

        # Tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        self.tab_general = self.tabview.add("General")
        self.tab_health = self.tabview.add("Health/Resource")
        self.tab_events = self.tabview.add("Events")
        self.tab_advanced = self.tabview.add("Advanced Trackers")

        from typing import Dict, Any
        self.color_buttons: Dict[str, Any] = {}
        self.checkboxes: Dict[str, ctk.BooleanVar] = {}

        self._build_general_tab()
        self._build_health_tab()
        self._build_events_tab()
        self._build_advanced_tab()

        # Bottom Buttons Frame
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(pady=10)

        # Save Button
        self.save_btn = ctk.CTkButton(self.bottom_frame, text="Save Configuration", command=self.save_config)
        self.save_btn.pack(side="left", padx=10)

        # Restore Defaults Button
        self.restore_btn = ctk.CTkButton(self.bottom_frame, text="Restore Defaults", command=self.restore_defaults, fg_color="#8B0000", hover_color="#A52A2A")
        self.restore_btn.pack(side="left", padx=10)
        
        # Status Label
        self.status_lbl = ctk.CTkLabel(self, text="League API: Waiting...", font=("Arial", 14, "bold"), text_color="orange")
        self.status_lbl.pack(pady=5)
        
        self.update_status()

    def update_status(self):
        if hasattr(self, 'app') and hasattr(self.app, 'league'):
            if self.app.league.active_port is not None:
                self.status_lbl.configure(text=f"League API: Connected (Port {self.app.league.active_port})", text_color="green")
            else:
                self.status_lbl.configure(text="League API: Waiting for Match...", text_color="orange")
        self.after(1000, self.update_status)

    def _build_general_tab(self):
        f = self.app_config.hud.features
        self._create_checkbox(self.tab_general, "Enable Animations", "enable_animations", f.enable_animations)
        self._create_checkbox(self.tab_general, "Enable Gold Module", "enable_gold_module", f.enable_gold_module)
        self._create_checkbox(self.tab_general, "Enable Spell Module", "enable_spell_module", f.enable_spell_module)
        
        c = self.app_config.hud.colors
        self._create_color_picker(self.tab_general, "Background Color (Dead)", "c_dead_bg", c.c_dead_bg)
        self._create_color_picker(self.tab_general, "Off Color", "c_off", c.c_off)

    def _build_health_tab(self):
        c = self.app_config.hud.colors
        self._create_color_picker(self.tab_health, "Health Color", "c_health", c.c_health)
        self._create_color_picker(self.tab_health, "Health Color (Dead)", "c_health_dead", c.c_health_dead)
        self._create_color_picker(self.tab_health, "Mana Color", "c_mana", c.c_mana)
        self._create_color_picker(self.tab_health, "Energy Color", "c_energy", c.c_energy)
        self._create_color_picker(self.tab_health, "Fury/Rage Color", "c_fury", c.c_fury)
        self._create_color_picker(self.tab_health, "Shield Color", "c_shield", c.c_shield)
        self._create_color_picker(self.tab_health, "No Resource Color", "c_no_resource", c.c_no_resource)
        self._create_color_picker(self.tab_health, "Ally Alive Color", "c_ally_alive", c.c_ally_alive)
        self._create_color_picker(self.tab_health, "Ally Dead Color", "c_ally_dead", c.c_ally_dead)

    def _build_events_tab(self):
        f = self.app_config.hud.features
        self._create_checkbox(self.tab_events, "Enable Kill Flash", "enable_kill_flash", f.enable_kill_flash)
        self._create_checkbox(self.tab_events, "Enable Epic Monster Flash", "enable_epic_monster_flash", f.enable_epic_monster_flash)
        self._create_checkbox(self.tab_events, "Enable Level Up Flash", "enable_level_up_flash", f.enable_level_up_flash)
        self._create_checkbox(self.tab_events, "Enable Multikill Animations", "enable_multikill_animations", f.enable_multikill_animations)
        
        c = self.app_config.hud.colors
        self._create_color_picker(self.tab_events, "Kill Flash Color", "c_kill_flash", c.c_kill_flash)
        self._create_color_picker(self.tab_events, "Epic Monster Flash Color", "c_epic_monster_flash", c.c_epic_monster_flash)
        self._create_color_picker(self.tab_events, "Double Kill Color", "c_double_kill", c.c_double_kill)
        self._create_color_picker(self.tab_events, "Triple Kill Color", "c_triple_kill", c.c_triple_kill)
        self._create_color_picker(self.tab_events, "Quadra Kill Color", "c_quadra_kill", c.c_quadra_kill)
        self._create_color_picker(self.tab_events, "Penta Kill Color", "c_penta_kill", c.c_penta_kill)

    def _build_advanced_tab(self):
        f = self.app_config.hud.features
        self._create_checkbox(self.tab_advanced, "Enable Respawn Timer", "enable_respawn_timer", f.enable_respawn_timer)
        self._create_checkbox(self.tab_advanced, "Enable Ally Status Indicator", "enable_ally_status", f.enable_ally_status)
        self._create_checkbox(self.tab_advanced, "Enable Active Item Indicator", "enable_item_indicator", f.enable_item_indicator)
        self._create_checkbox(self.tab_advanced, "Enable Burst Damage Warning", "enable_burst_warning", f.enable_burst_warning)
        self._create_checkbox(self.tab_advanced, "Enable CS/min Metronome", "enable_cs_metronome", f.enable_cs_metronome)
        self._create_checkbox(self.tab_advanced, "Enable Vision Score Tracker", "enable_vision_tracker", f.enable_vision_tracker)

        c = self.app_config.hud.colors
        self._create_color_picker(self.tab_advanced, "Burst Damage Flash Color", "c_burst_damage", c.c_burst_damage)
        self._create_color_picker(self.tab_advanced, "Active Item Ready Color", "c_item_ready", c.c_item_ready)
        self._create_color_picker(self.tab_advanced, "CS/min Poor Color (Red)", "c_cs_poor", c.c_cs_poor)
        self._create_color_picker(self.tab_advanced, "CS/min Good Color (Green)", "c_cs_good", c.c_cs_good)
        self._create_color_picker(self.tab_advanced, "Vision Score Color", "c_vision_score", c.c_vision_score)

    def _create_checkbox(self, parent, text, config_key, default_val):
        var = ctk.BooleanVar(value=default_val)
        chk = ctk.CTkCheckBox(parent, text=text, variable=var)
        chk.pack(anchor="w", pady=5, padx=20)
        self.checkboxes[config_key] = var

    def _create_color_picker(self, parent, text, config_key, default_rgb):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=5, padx=20)
        
        lbl = ctk.CTkLabel(frame, text=text, width=200, anchor="w")
        lbl.pack(side="left", padx=10)
        
        hex_color = "#{:02x}{:02x}{:02x}".format(*default_rgb)
        
        btn = ctk.CTkButton(frame, text="Pick Color", fg_color=hex_color, hover_color=hex_color)
        btn.configure(command=lambda k=config_key, b=btn: self._pick_color(k, b))
        btn.pack(side="left", padx=10)
        
        # Store current color for saving
        self.color_buttons[config_key] = {"rgb": list(default_rgb), "btn": btn}

    def _pick_color(self, config_key, btn):
        current_rgb = self.color_buttons[config_key]["rgb"]
        initial_color = "#{:02x}{:02x}{:02x}".format(*current_rgb)
        # Using standard tkinter color chooser
        color = askcolor(color=initial_color, title="Choose Color")
        if color[0]:
            rgb = [int(c) for c in color[0]]
            hex_color = color[1]
            self.color_buttons[config_key]["rgb"] = rgb
            # Change text color if background is too light to maintain readability
            text_col = "black" if (rgb[0]*0.299 + rgb[1]*0.587 + rgb[2]*0.114) > 186 else "white"
            btn.configure(fg_color=hex_color, hover_color=hex_color, text_color=text_col)

    def restore_defaults(self):
        default_config = AppConfig()
        
        f_default = default_config.hud.features
        for key, var in self.checkboxes.items():
            if hasattr(f_default, key):
                var.set(getattr(f_default, key))
                
        c_default = default_config.hud.colors
        for key, data in self.color_buttons.items():
            if hasattr(c_default, key):
                default_rgb = getattr(c_default, key)
                data["rgb"] = list(default_rgb)
                hex_color = "#{:02x}{:02x}{:02x}".format(*default_rgb)
                text_col = "black" if (default_rgb[0]*0.299 + default_rgb[1]*0.587 + default_rgb[2]*0.114) > 186 else "white"
                data["btn"].configure(fg_color=hex_color, hover_color=hex_color, text_color=text_col)
                
        self.save_config()

    def save_config(self):
        # Update app_config from UI
        f = self.app_config.hud.features
        for key, var in self.checkboxes.items():
            if hasattr(f, key):
                setattr(f, key, var.get())
                
        c = self.app_config.hud.colors
        for key, data in self.color_buttons.items():
            if hasattr(c, key):
                setattr(c, key, data["rgb"])
                
        # Save to disk using the manager
        self.config_manager.config = self.app_config
        self.config_manager.save()
        
        # We also need to reload explicitly here so the GUI stays synchronized
        self.app_config = self.config_manager.load()
        print("Config saved and flushed to disk!")

if __name__ == "__main__":
    class MockLeague:
        active_port = None
    class MockApp:
        def __init__(self):
            self.config_manager = ConfigManager("config.json")
            self.league = MockLeague()
            
    app_mock = MockApp()
    app = ConfiguratorGUI(app_mock)
    app.mainloop()
