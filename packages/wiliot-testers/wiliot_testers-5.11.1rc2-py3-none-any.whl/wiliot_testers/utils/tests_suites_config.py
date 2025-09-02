#  """
#    Copyright (c) 2016- 2025, Wiliot Ltd. All rights reserved.
#
#    Redistribution and use of the Software in source and binary forms, with or without modification,
#     are permitted provided that the following conditions are met:
#
#       1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#       2. Redistributions in binary form, except as used in conjunction with
#       Wiliot's Pixel in a product or a Software update for such product, must reproduce
#       the above copyright notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the distribution.
#
#       3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
#       may be used to endorse or promote products or services derived from this Software,
#       without specific prior written permission.
#
#       4. This Software, with or without modification, must only be used in conjunction
#       with Wiliot's Pixel or with Wiliot's cloud service.
#
#       5. If any Software is provided in binary form under this license, you must not
#       do any of the following:
#       (a) modify, adapt, translate, or create a derivative work of the Software; or
#       (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
#       discover the source code or non-literal aspects (such as the underlying structure,
#       sequence, organization, ideas, or algorithms) of the Software.
#
#       6. If you create a derivative work and/or improvement of any Software, you hereby
#       irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
#       royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
#       right and license to reproduce, use, make, have made, import, distribute, sell,
#       offer for sale, create derivative works of, modify, translate, publicly perform
#       and display, and otherwise commercially exploit such derivative works and improvements
#       (as applicable) in conjunction with Wiliot's products and services.
#
#       7. You represent and warrant that you are not a resident of (and will not use the
#       Software in) a country that the U.S. government has embargoed for use of the Software,
#       nor are you named on the U.S. Treasury Department’s list of Specially Designated
#       Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
#       You must not transfer, export, re-export, import, re-import or divert the Software
#       in violation of any export or re-export control laws and regulations (such as the
#       United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
#       and use restrictions, all as then in effect
#
#     THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
#     OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
#     WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
#     QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
#     IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
#     ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
#     OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
#     FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
#     (SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
#     (A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
#     CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
#     (B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
#     (C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
#  """
import re
import sys
import json
import os.path
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, simpledialog
except Exception as e:
    print(f'could not import tkinter: {e}')
from wiliot_core.local_gateway.local_gateway_core import valid_output_power_vals
from enum import Enum
from wiliot_core.local_gateway.utils.gw_commands import CommandDetails
from wiliot_core.packet_data.data_schema.stat_data_info import get_stat_params_names_and_types


class GwPatterns(Enum):
    ENERGY_18 = 'Beacon 37, 38, 39 Energy at 2480'
    ENERGY_51 = 'Beacon 37, 38, 39 Energy at 915'


BLE_ENERGY = ['neg20dBm', 'neg16dBm', 'neg12dBm', 'neg4dBm', 'neg8dBm', 'neg12dBm', 'pos8dBm', 'pos7dBm', 'pos6dBm',
              'pos7dBm', 'pos6dBm', 'pos5dBm', 'pos4dBm', 'neg16dBm', 'neg20dBm', 'pos4dBm', 'neg16dBm', 'neg20dBm']

LORA_POWER = ['0dBm', '9dBm', '14dBm', '17dBm', '20dBm', '23dBm', '26dBm', '29dBm', '32dBm']

CRITERIA_KEYS = sorted(list(get_stat_params_names_and_types().keys()))

FIELD_NAMES = {"plDelay": "Production Line Delay",
               "rssiThresholdHW": "RSSI Threshold HW",
               "rssiThresholdSW": "RSSI Threshold SW",
               "maxTtfp": "Max TTFP",
               "ignore_test_mode": "Ignore Test Mode Packets",
               "devMode": "Decryption",
               "run_all": "Run all stages even if fail",
               "name": "Name",
               "rxChannel": "RX Channel",
               "energizingPattern": "Energizing Pattern",
               "timeProfile": "Time Profile (msec)",
               "absGwTxPowerIndex": "Power Index/Name",
               "sub1gGwTxPower": "LoRa Power",
               "maxTime": "Test Time (sec)",
               "delayBeforeNextTest": "Stage Delay (sec)"}

DEFAULT_VALUES = {
    "plDelay": 100,
    "rssiThresholdHW": 85,
    "rssiThresholdSW": 70,
    "maxTtfp": 5,
    "ignore_test_mode": True,
    "devMode": False,
    "run_all": False,
    "tests": [{
        "name": "",
        "rxChannel": 37,
        "energizingPattern": 18,
        "timeProfile": [5, 10],
        "absGwTxPowerIndex": len(valid_output_power_vals) - 1,
        "sub1gGwTxPower": LORA_POWER[0],
        "maxTime": 5,
        "delayBeforeNextTest": 0,
        "stop_criteria": {},
        "quality_param": {}
    }]
}


class TestConfigEditorApp(tk.Tk):
    def __init__(self, json_file):
        super().__init__()
        self.tooltip_label = None
        self.json_file = json_file
        self.data = self.load_data()
        self.current_config = None
        self.dynamic_widgets = {}
        self.test_name_label, self.selected_config = None, None
        self.config_dropdown, self.canvas, self.scrollable_frame, self.vsb = None, None, None, None
        self.create_widgets()
        self.style = None
        self.configure_styles()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_data(self):
        try:
            with open(self.json_file, 'r') as file:
                return json.load(file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load JSON data: {e}")
            self.quit()

    def configure_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # General Styles
        self.style.configure('TFrame', background='#f7f7f7')
        self.style.configure('TLabel', background='#f7f7f7', foreground='#333333', font=('Helvetica', 9))
        self.style.configure('TButton', background='#e0e0e0', foreground='#333333', font=('Helvetica', 9, 'bold'))
        self.style.configure('TEntry', background='#ffffff', foreground='#333333', font=('Helvetica', 9), padding=5)
        self.style.configure('TCombobox', background='#ffffff', foreground='#333333', font=('Helvetica', 9))

        # LabelFrame Styles
        self.style.configure('TLabelframe', background='#f7f7f7', foreground='#333333', padding=10)
        self.style.configure('TLabelframe.Label', background='#f7f7f7', foreground='#333333',
                             font=('Helvetica', 10, 'bold'))

        # Scrollable Frame Styles
        self.style.configure('Canvas.TFrame', background='#f7f7f7')

    def create_widgets(self):
        self.geometry("600x800")
        self.title("Test Suite Editor")
        self.configure(background='#f7f7f7')

        selection_frame = ttk.Frame(self, padding=5)
        selection_frame.pack(side=tk.TOP, fill=tk.X)

        self.test_name_label = ttk.Label(selection_frame, text="", font=('Helvetica', 11, 'bold'), background='#d0d0d0')
        self.test_name_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        self.add_tooltip(self.test_name_label, "This label displays the name of the currently selected test.")

        self.selected_config = tk.StringVar()
        self.config_dropdown = ttk.Combobox(selection_frame, textvariable=self.selected_config, state="readonly",
                                            width=30)
        self.config_dropdown['values'] = list(self.data.keys())
        self.config_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=10)
        self.config_dropdown.bind("<<ComboboxSelected>>", self.on_config_selected)

        # Disable mouse wheel
        self.config_dropdown.bind("<MouseWheel>", lambda event: "break")
        self.config_dropdown.bind("<Button-4>", lambda event: "break")
        self.config_dropdown.bind("<Button-5>", lambda event: "break")

        self.add_tooltip(self.config_dropdown, "Select a test configuration from the dropdown list.")

        control_frame = ttk.Frame(self, padding=5)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        save_button = ttk.Button(control_frame, text="Save", command=self.on_save)
        save_button.pack(side=tk.LEFT, padx=5)
        self.add_tooltip(save_button, "Save the current test configuration.")

        clear_button = ttk.Button(control_frame, text="Clear", command=self.load_initial_values)
        clear_button.pack(side=tk.LEFT, padx=5)
        self.add_tooltip(clear_button, "Clear all input fields to their initial values.")

        new_button = ttk.Button(control_frame, text="New", command=self.create_new_test)
        new_button.pack(side=tk.LEFT, padx=5)
        self.add_tooltip(new_button, "Create a new test configuration.")

        delete_button = ttk.Button(control_frame, text="Delete", command=self.delete_current_test)
        delete_button.pack(side=tk.LEFT, padx=5)
        self.add_tooltip(delete_button, "Delete the currently selected test configuration.")

        duplicate_button = ttk.Button(control_frame, text="Duplicate", command=self.duplicate_current_test)
        duplicate_button.pack(side=tk.LEFT, padx=5)
        self.add_tooltip(duplicate_button, "Duplicate the currently selected test configuration.")

        self.canvas = tk.Canvas(self, borderwidth=0, background='#f7f7f7')
        self.scrollable_frame = ttk.Frame(self.canvas, style='Canvas.TFrame')
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.limit_scroll_region()

    def _on_mousewheel(self, event):
        if 'combobox' in str(event.widget):
            return
        if event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.delta > 0 and self.canvas.canvasy(0) > 0:
            self.canvas.yview_scroll(-1, "units")

    def on_frame_configure(self, event=None):
        self.limit_scroll_region()

    def limit_scroll_region(self):
        self.update_idletasks()
        bbox = self.canvas.bbox("all")
        if bbox:
            x1, y1, x2, y2 = bbox
            self.canvas.configure(scrollregion=(x1, 0, x2, y2))

    def on_config_selected(self, event=None):
        config_name = self.selected_config.get()
        if config_name and config_name in self.data:
            self.current_config = config_name
            config_values = self.data[config_name]
            self.clear_display()
            self.generate_fields(config_values)
            self.test_name_label.config(text=f"Current Configuration: {config_name}")
        else:
            self.clear_display()
            self.test_name_label.config(text="No configuration selected.")
        self.limit_scroll_region()

    def add_tooltip(self, widget, text):
        widget.bind("<Enter>", lambda e: self.show_tooltip(e, text))
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event, text):
        if hasattr(self, 'tooltip_label') and self.tooltip_label:
            self.tooltip_label.destroy()
            self.tooltip_label = None

        x = event.x_root - self.winfo_rootx() + 10
        y = event.y_root - self.winfo_rooty() + 10

        self.tooltip_label = tk.Label(self, text=text, background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                                      font=("tahoma", "10", "normal"))
        self.tooltip_label.place(x=x, y=y)

    def hide_tooltip(self, event):
        if hasattr(self, 'tooltip_label') and self.tooltip_label:
            self.tooltip_label.destroy()
            self.tooltip_label = None

    def generate_fields(self, config_values):
        ttk.Label(self.scrollable_frame, text="General Configuration:", style='TLabelframe').pack(
            fill=tk.X, padx=5, pady=5)
        for key in ['plDelay', 'rssiThresholdHW', 'rssiThresholdSW', 'maxTtfp']:
            if key in config_values:
                self.generate_field(key, config_values[key], FIELD_NAMES.get(key, key), int, 0, 1000)
        for key in ['ignore_test_mode', 'devMode', 'run_all']:
            if key in config_values:
                if key == 'ignore_test_mode':
                    self.generate_boolean_field(key, True, FIELD_NAMES.get(key, key))
                else:
                    self.generate_boolean_field(key, config_values[key], FIELD_NAMES.get(key, key))
            else:
                self.generate_boolean_field(key, False, FIELD_NAMES.get(key, key))
        self.generate_test_fields(config_values.get("tests", []))

    def generate_field(self, key, value, display_name, field_type, min_val, max_val):
        frame = ttk.Frame(self.scrollable_frame, style='Canvas.TFrame')
        frame.pack(fill=tk.X, padx=10, pady=5)
        label = ttk.Label(frame, text=f"{display_name}: ", width=25)
        label.pack(side=tk.LEFT)
        self.add_tooltip(label, f"This is a tooltip for {display_name}.")
        var = tk.StringVar(value=str(value))
        entry = ttk.Entry(frame, textvariable=var, width=10)
        entry.pack(side=tk.LEFT, padx=5)
        self.add_tooltip(entry, f"Enter the value for {display_name}.")
        self.dynamic_widgets[key] = (var, field_type)

    def generate_boolean_field(self, key, value, display_name):
        frame = ttk.Frame(self.scrollable_frame, style='Canvas.TFrame')
        frame.pack(fill=tk.X, padx=10, pady=5)
        var = tk.BooleanVar(value=str(value).lower() == 'true')
        check = ttk.Checkbutton(frame, text=display_name, variable=var)
        check.pack(side=tk.LEFT)
        self.add_tooltip(check, f"This is a tooltip for {display_name}.")
        self.dynamic_widgets[key] = var

    def generate_test_fields(self, tests):
        for index, test in enumerate(tests):
            frame = ttk.LabelFrame(self.scrollable_frame, text=f"Stage {index + 1}", style='TLabelframe', padding=10)
            frame.pack(fill=tk.X, expand=True, padx=10, pady=20)
            self.add_tooltip(frame, f"This is Stage {index + 1} of the test configuration.")
            self.create_test_inputs(frame, test, index)
            self.create_gw_commands_fields(test.get('gw_commands', {}), frame, f"{index}_gw_commands")
            delete_button = ttk.Button(frame, text="Delete Stage", command=lambda idx=index: self.delete_test(idx))
            delete_button.pack(side=tk.LEFT, padx=5, pady=5)
            self.add_tooltip(delete_button, f"Delete stage {index + 1} of the test.")
        add_button = ttk.Button(self.scrollable_frame, text="Add New Stage", command=self.add_new_test)
        add_button.pack(pady=10)
        self.add_tooltip(add_button, "Add a new test stage.")

    def create_test_inputs(self, frame, test, index):
        for key in DEFAULT_VALUES["tests"][0].keys():
            if key not in test:
                test[key] = DEFAULT_VALUES["tests"][0][key]

        ordered_keys = ['name', 'rxChannel', 'energizingPattern', 'timeProfile', 'absGwTxPowerIndex', 'sub1gGwTxPower',
                        'maxTime', 'delayBeforeNextTest']

        for key in ordered_keys:
            value = test[key]
            friendly_name = FIELD_NAMES.get(key, key)
            sub_frame = ttk.Frame(frame, style='Canvas.TFrame')
            sub_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)
            self.add_tooltip(sub_frame, f"This section contains input for '{friendly_name}'.")
            if isinstance(value, list) and key == "timeProfile":
                self.create_time_profile_input(sub_frame, value, index, friendly_name)
            elif key == "name":
                self.create_standard_input(sub_frame, key, value, friendly_name, index, l_expand=True)
            elif key == "absGwTxPowerIndex":
                current_index = value if isinstance(value, int) else None
                self.create_power_dropdown(sub_frame, index, current_index, friendly_name)
            elif key == "sub1gGwTxPower":
                current_value = value if isinstance(value, int) else 0
                self.create_lora_power_dropdown(sub_frame, index, current_value, friendly_name)
            elif key not in ["stop_criteria", "quality_param"]:
                self.create_standard_input(sub_frame, key, value, friendly_name, index)

        self.create_criteria_fields(test.get('stop_criteria', {}), frame, f"{index}_stop_criteria", 'Stop Criteria')
        self.create_criteria_fields(test.get('quality_param', {}), frame, f"{index}_quality_param", 'Quality Param')

    def create_gw_commands_fields(self, commands_list, frame, identifier):
        gw_commands_frame = ttk.LabelFrame(frame, text="GW Commands", style='TLabelframe', padding=10)
        gw_commands_frame.pack(fill=tk.X, expand=True, padx=5, pady=10)
        self.add_tooltip(gw_commands_frame, "This section contains GW Commands.")

        test_index = int(identifier.split('_')[0])

        for command_string in commands_list:
            # Parse the command string to extract the command and values
            parts = command_string.split()
            command = parts[0][1:]  # Remove the leading '!' from the command
            values = " ".join(parts[1:])  # Join the rest as the values string

            # Pass the parsed command and values to create the input fields
            self.create_single_gw_command_input(gw_commands_frame, command, values, test_index)

        add_button = ttk.Button(gw_commands_frame, text="Add GW Command",
                                command=lambda: self.add_gw_command(gw_commands_frame, identifier))
        add_button.pack(side=tk.TOP, pady=5)
        self.add_tooltip(add_button, "Add a new GW Command.")

    def create_single_gw_command_input(self, frame, command, value, test_index):
        command = re.sub(r'_\d+$', '', command)
        cmd_frame = ttk.Frame(frame, name=command, style='Canvas.TFrame')
        cmd_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)
        self.add_tooltip(cmd_frame, {CommandDetails[command].value['desc']})

        ttk.Label(cmd_frame, text=f"{command}: ", style='TLabel').pack(side=tk.LEFT, padx=5)

        cmd_var = tk.StringVar(value=value)
        entry = ttk.Entry(cmd_frame, textvariable=cmd_var, width=20)
        entry.pack(side=tk.LEFT, padx=5)
        self.add_tooltip(entry, f"args: {CommandDetails[command].value['args']} for {command}'.")

        self.dynamic_widgets[f"gw_command_{command}_{test_index}"] = cmd_var

        delete_button = ttk.Button(cmd_frame, text="Delete",
                                   command=lambda: self.delete_gw_command(cmd_frame, command, test_index))
        delete_button.pack(side=tk.RIGHT, padx=5)
        self.add_tooltip(delete_button, f"Delete the GW Command '{command}'.")

        # Concatenate the command and value
        concatenated_value = f"!{command} {cmd_var.get()}"

        # Ensure 'gw_commands' is a list
        test_data = self.data[self.current_config]['tests'][test_index]
        if 'gw_commands' not in test_data or not isinstance(test_data['gw_commands'], list):
            test_data['gw_commands'] = []  # Initialize as an empty list if not present or if it's mistakenly a dict

        # Add command if it's not already in the list
        if concatenated_value not in test_data['gw_commands']:
            test_data['gw_commands'].append(concatenated_value)

    def add_gw_command(self, gw_commands_frame, identifier):
        add_frame = ttk.Frame(gw_commands_frame, style='Canvas.TFrame')
        add_frame.pack(fill=tk.X, expand=True, padx=5, pady=5, side=tk.TOP)

        command_var = tk.StringVar()
        options = sorted([cmd.value['cmd'] for cmd in CommandDetails])
        command_dropdown = ttk.Combobox(add_frame, textvariable=command_var, values=options, state="readonly")
        command_dropdown.pack(side=tk.LEFT, padx=5)

        # Disable mouse wheel
        command_dropdown.bind("<MouseWheel>", lambda event: "break")
        command_dropdown.bind("<Button-4>", lambda event: "break")
        command_dropdown.bind("<Button-5>", lambda event: "break")

        ttk.Button(add_frame, text="Add", command=lambda: self.confirm_add_gw_command(
            command_var.get(), gw_commands_frame, identifier, add_frame)).pack(side=tk.LEFT, padx=10)

        ttk.Button(add_frame, text="Cancel", command=add_frame.destroy).pack(side=tk.LEFT, padx=5)

    def confirm_add_gw_command(self, command_key, gw_commands_frame, identifier, add_frame):
        test_index = int(identifier.split('_')[0])
        selected_command = command_key.strip()
        test_data = self.data[self.current_config]['tests'][test_index]

        if 'gw_commands' not in test_data or not isinstance(test_data['gw_commands'], list):
            test_data['gw_commands'] = []

        concatenated_value = f"!{selected_command} "

        if concatenated_value not in test_data['gw_commands']:
            test_data['gw_commands'].append(concatenated_value)

        self.create_single_gw_command_input(gw_commands_frame, selected_command, "", test_index)

        add_frame.destroy()

    def delete_gw_command(self, frame, command, test_index):
        try:
            test_data = self.data[self.current_config]['tests'][test_index]
            if 'gw_commands' in test_data:
                gw_commands = test_data['gw_commands']
                matching_command = next((cmd for cmd in gw_commands if cmd.startswith(f"!{command} ")), None)

                if matching_command:
                    gw_commands.remove(matching_command)
                    dynamic_widget_key = f"gw_command_{command}_{test_index}"
                    if dynamic_widget_key in self.dynamic_widgets:
                        del self.dynamic_widgets[dynamic_widget_key]
                    frame.destroy()
                    if not gw_commands:
                        test_data['gw_commands'] = []
                else:
                    messagebox.showerror("Error", f"GW Command '{command}' not found.")
            else:
                messagebox.showerror("Error", "GW Commands section not found.")
        except KeyError as e:
            messagebox.showerror("Error", f"Failed to delete GW Command: '{command}'")
        except ValueError as e:
            messagebox.showerror("Error", "Invalid operation or data structure issues.")

    def create_lora_power_dropdown(self, frame, index, current_value, friendly_name):
        ttk.Label(frame, text=f"{friendly_name}: ", width=25).pack(side=tk.LEFT)
        options = LORA_POWER
        var = tk.StringVar(frame)
        dropdown = ttk.Combobox(frame, textvariable=var, values=options, state="readonly", width=15)
        dropdown.pack(side=tk.LEFT, padx=5, pady=5)

        # Disable mouse wheel
        dropdown.bind("<MouseWheel>", lambda event: "break")
        dropdown.bind("<Button-4>", lambda event: "break")
        dropdown.bind("<Button-5>", lambda event: "break")

        if f"{current_value}dBm" in options:
            var.set(f"{current_value}dBm")
        else:
            var.set('0dBm')
        self.dynamic_widgets[f"{index}_sub1gGwTxPower"] = var
        self.add_tooltip(dropdown, f"Select the LoRa power level for {friendly_name}.")
        return var

    def create_new_test(self):
        new_name = simpledialog.askstring("New Test", "Enter the name for the new test configuration:")
        if new_name:
            if new_name in self.data:
                messagebox.showerror("Error", "A test with this name already exists.")
                return

            self.data[new_name] = DEFAULT_VALUES.copy()
            self.selected_config.set(new_name)
            self.update_dropdown()

            self.on_config_selected()

    def create_standard_input(self, frame, key, value, friendly_name, index, l_expand=False):
        var = tk.StringVar(value=str(value))
        ttk.Label(frame, text=f"{friendly_name}: ", width=25).pack(side=tk.LEFT)
        entry = ttk.Entry(frame, textvariable=var, width=10)
        if l_expand:
            entry.pack(side=tk.LEFT, expand=l_expand, fill=tk.X)
        else:
            entry.pack(side=tk.LEFT, padx=5)
        self.dynamic_widgets[f"{index}_{key}"] = var
        self.add_tooltip(entry, f"Enter the value for {friendly_name}.")

    def create_time_profile_input(self, frame, values, index, friendly_name):
        ttk.Label(frame, text=f"{friendly_name}: ", width=25).pack(side=tk.LEFT)
        profile_vars = []
        for i, val in enumerate(values):
            var = tk.IntVar(value=val)
            entry = ttk.Entry(frame, textvariable=var, width=5)
            entry.pack(side=tk.LEFT, padx=5)
            profile_vars.append(var)
            self.add_tooltip(entry, f"Enter value {i + 1} for {friendly_name}.")
        self.dynamic_widgets[f"{index}_timeProfile"] = profile_vars

    def create_power_dropdown(self, frame, index, current_index, friendly_name):
        ttk.Label(frame, text=f"{friendly_name}: ", width=25).pack(side=tk.LEFT)
        options = [f"{item['abs_power']} dBm ({item['gw_output_power']}, "
                   f"PA Bypass: {item['bypass_pa']})" for item in valid_output_power_vals]
        var = tk.StringVar(frame)
        dropdown = ttk.Combobox(frame, textvariable=var, values=options, state="readonly", width=30)
        dropdown.pack(side=tk.LEFT, padx=5, pady=5)

        # Disable mouse wheel
        dropdown.bind("<MouseWheel>", lambda event: "break")
        dropdown.bind("<Button-4>", lambda event: "break")
        dropdown.bind("<Button-5>", lambda event: "break")

        if current_index is not None and isinstance(current_index, int) and \
                current_index < len(valid_output_power_vals):
            var.set(options[current_index])
        else:
            var.set(options[-1])
        self.dynamic_widgets[f"{index}_absGwTxPowerIndex"] = var
        self.add_tooltip(dropdown, f"Select the power level for {friendly_name}.")

    def create_criteria_fields(self, criteria_dict, frame, identifier, name):
        criteria_frame = ttk.LabelFrame(frame, text=name, style='TLabelframe', padding=10)
        criteria_frame.pack(fill=tk.X, expand=True, padx=5, pady=10)
        self.add_tooltip(criteria_frame, f"This section contains {name} criteria.")

        test_index = int(identifier.split('_')[0])
        category = "_".join(identifier.split('_')[1:3])

        for criterion, values in criteria_dict.items():
            if values:
                self.create_single_criterion_input(criteria_frame, criterion, values, int(test_index), category)

        add_button = ttk.Button(criteria_frame, text="Add Criterion",
                                command=lambda: self.add_criterion(criteria_frame, identifier))
        add_button.pack(side=tk.TOP, pady=5)
        self.add_tooltip(add_button, f"Add a new criterion to {name}.")

    def add_criterion_button(self, criteria_frame, identifier):
        ttk.Button(criteria_frame, text="Add Criterion",
                   command=lambda: self.add_criterion(criteria_frame, identifier)).pack(side=tk.BOTTOM, pady=5)

    def add_criterion(self, criteria_frame, identifier):
        add_frame = ttk.Frame(criteria_frame, style='Canvas.TFrame')
        add_frame.pack(fill=tk.X, expand=True, padx=5, pady=5, side=tk.TOP)

        criterion_var = tk.StringVar()
        criterion_dropdown = ttk.Combobox(add_frame, textvariable=criterion_var, values=CRITERIA_KEYS, state="readonly")
        criterion_dropdown.pack(side=tk.LEFT, padx=5)

        def disable_mouse_wheel(event):
            return "break"

        criterion_dropdown.bind("<MouseWheel>", disable_mouse_wheel)
        criterion_dropdown.bind("<Button-4>", disable_mouse_wheel)
        criterion_dropdown.bind("<Button-5>", disable_mouse_wheel)

        ttk.Button(add_frame, text="Add", command=lambda: self.confirm_add_criterion(
            criterion_var.get(), criteria_frame, identifier, add_frame)).pack(side=tk.LEFT, padx=10)
        ttk.Button(add_frame, text="Cancel", command=add_frame.destroy).pack(side=tk.LEFT, padx=5)

        for widget in criteria_frame.winfo_children():
            if isinstance(widget, ttk.Button) and 'Add Criterion' in widget.cget('text'):
                widget.pack_forget()
                widget.pack(side=tk.BOTTOM, pady=5)

    def duplicate_current_test(self):
        if not self.current_config:
            messagebox.showwarning("Warning", "No configuration selected to duplicate.")
            return

        new_name = simpledialog.askstring("Duplicate Test", "Enter the name for the duplicated test configuration:")
        old_name = self.current_config
        if not new_name:
            return

        if new_name in self.data:
            messagebox.showerror("Error", "A test with this name already exists.")
            return

        self.data[new_name] = json.loads(json.dumps(self.data[self.current_config]))
        self.update_dropdown()
        self.selected_config.set(new_name)
        self.on_config_selected()

        messagebox.showinfo("Duplicate Successful", f"Configuration '{old_name}' duplicated as '{new_name}'.")

    @staticmethod
    def extract_numeric_index(identifier):
        parts = identifier.split('_')
        if parts and parts[0].isdigit():
            return int(parts[0])
        raise ValueError(f"Invalid identifier {identifier}")

    def confirm_add_criterion(self, criterion_key, criteria_frame, identifier, add_frame):
        test_index, category = identifier.split('_')[:2]
        full_category = "_".join(identifier.split('_')[1:])

        existing_keys = self.data[self.current_config]['tests'][int(test_index)].get(full_category, {})
        if criterion_key in existing_keys:
            messagebox.showerror("Error", f"The criterion '{criterion_key}' already exists in {full_category}.")
            return

        self.data[self.current_config]['tests'][int(test_index)].setdefault(full_category, {})[criterion_key] = [0, 999]
        self.create_single_criterion_input(criteria_frame, criterion_key, [0, 999], int(test_index), full_category)
        add_frame.destroy()

    def create_single_criterion_input(self, frame, criterion, values, test_index, category):
        crit_frame = ttk.Frame(frame, name=criterion, style='Canvas.TFrame')
        crit_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)
        self.add_tooltip(crit_frame, f"This frame contains inputs for the criterion '{criterion}'.")

        min_val, max_val = values
        ttk.Label(crit_frame, text=f"{criterion}: ", style='TLabel').pack(side=tk.LEFT, padx=5)

        min_var = tk.DoubleVar(value=min_val)
        max_var = tk.DoubleVar(value=max_val)

        min_key = f"{test_index}_{category}_{criterion}_min"
        max_key = f"{test_index}_{category}_{criterion}_max"

        self.dynamic_widgets[min_key] = min_var
        self.dynamic_widgets[max_key] = max_var

        min_entry = ttk.Entry(crit_frame, textvariable=min_var, style='TEntry', width=10)
        min_entry.pack(side=tk.LEFT, padx=5)
        self.add_tooltip(min_entry, f"Enter the minimum value for {criterion}.")
        max_entry = ttk.Entry(crit_frame, textvariable=max_var, style='TEntry', width=10)
        max_entry.pack(side=tk.LEFT, padx=5)
        self.add_tooltip(max_entry, f"Enter the maximum value for {criterion}.")

        delete_button = ttk.Button(crit_frame, text="Delete", command=lambda: self.delete_criterion(
            crit_frame, criterion, f"{test_index}_{category}"))
        delete_button.pack(side=tk.RIGHT, padx=5)
        self.add_tooltip(delete_button, f"Delete the criterion '{criterion}'.")

    def delete_current_test(self):
        if self.current_config and messagebox.askyesno("Delete Test",
                                                       f"Are you sure you want to delete '{self.current_config}'?"):
            del self.data[self.current_config]
            self.update_dropdown()

    def delete_criterion(self, frame, criterion, identifier):
        criterion_name = criterion
        try:
            parts = identifier.split('_')
            if len(parts) < 3:
                messagebox.showerror("Error", "Invalid criterion identifier.")
                return

            test_index = int(parts[0])
            category = "_".join(parts[1:3])

            if category in self.data[self.current_config]['tests'][test_index]:
                if criterion_name in self.data[self.current_config]['tests'][test_index][category]:
                    del self.data[self.current_config]['tests'][test_index][category][criterion_name]
                    frame.destroy()

                    if not self.data[self.current_config]['tests'][test_index][category]:
                        self.data[self.current_config]['tests'][test_index][category] = {}

                    self.refresh_criteria_display(test_index, category)
                else:
                    messagebox.showerror("Error", f"Criterion '{criterion_name}' not found in '{category}'.")
            else:
                messagebox.showerror("Error", f"Category '{category}' not found in test index {test_index}.")

        except KeyError as e:
            messagebox.showerror("Error", f"Failed to delete criterion: '{criterion_name}'")
        except ValueError:
            messagebox.showerror("Error", "Invalid operation or data structure issues.")

    @staticmethod
    def output_power_string_to_index(selected_string):
        try:
            abs_power = int(selected_string.split(' ')[0])
        except Exception as e:
            raise Exception(f'could not parse the absolute power from the selected string: '
                            f'{selected_string} due to: {e}')
        for i, item in enumerate(valid_output_power_vals):
            if item['abs_power'] == abs_power:
                return i
        raise Exception(f'could not find the relevant output power index for the specified string: {selected_string}')

    def clear_criteria_section(self, test_index, category):
        try:
            test_frame = next((child for child in self.scrollable_frame.winfo_children()
                               if isinstance(child, ttk.LabelFrame) and
                               f"Stage {test_index + 1}" in child.cget('text')), None)
            if test_frame:
                criteria_frame = next((child for child in test_frame.winfo_children()
                                       if isinstance(child, ttk.LabelFrame) and
                                       category.lower() in child.cget('text').lower()), None)
                if criteria_frame:
                    criteria_frame.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def check_stage_exists(self, test_index):
        return any(isinstance(child, ttk.LabelFrame) and f"Stage {test_index + 1}" in child.cget('text')
                   for child in self.scrollable_frame.winfo_children())

    def update_dropdown(self):
        self.config_dropdown['values'] = list(self.data.keys())
        if self.data:
            if self.selected_config.get() not in self.data:
                self.selected_config.set(next(iter(self.data.keys())))
            self.on_config_selected()
        else:
            self.selected_config.set('')
            self.clear_display()

    def clear_display(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        ttk.Label(self.scrollable_frame, text="No configuration selected or available.", style='TLabelframe').pack()

    def refresh_criteria_display(self, test_index, category):
        try:
            test_frame = next((child for child in self.scrollable_frame.winfo_children()
                               if isinstance(child, ttk.LabelFrame) and
                               f"Stage {test_index + 1}" in child.cget('text')), None)
            if not test_frame:
                raise Exception("Test frame not found.")

            criteria_frame = next((child for child in test_frame.winfo_children()
                                   if isinstance(child, ttk.LabelFrame) and
                                   category.lower() in child.cget('text').lower()), None)
            if not criteria_frame:
                return

            for widget in criteria_frame.winfo_children():
                widget.destroy()

            new_criteria_dict = self.data[self.current_config]['tests'][test_index][category]
            identifier = f"{test_index}_{category}"
            self.create_criteria_fields(new_criteria_dict, criteria_frame, identifier, category.capitalize())
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_new_test(self):
        self.update_current_state()
        new_test = {
            "name": "",
            "rxChannel": 37,
            "energizingPattern": 18,
            "timeProfile": [5, 10],
            "absGwTxPowerIndex": len(valid_output_power_vals) - 1,
            "sub1gGwTxPower": LORA_POWER[0],
            "maxTime": 5,
            "delayBeforeNextTest": 0,
            "stop_criteria": {},
            "quality_param": {}
        }
        self.data[self.current_config]["tests"].append(new_test)
        self.on_config_selected()
        self.limit_scroll_region()

    def delete_test(self, index):
        self.update_current_state()
        del self.data[self.current_config]['tests'][index]
        self.on_config_selected()
        self.limit_scroll_region()

    def update_current_state(self):
        if self.current_config is None:
            return

        config_values = self.data[self.current_config]
        for key in ['plDelay', 'rssiThresholdHW', 'rssiThresholdSW', 'maxTtfp']:
            if key in self.dynamic_widgets:
                var, field_type = self.dynamic_widgets[key]
                config_values[key] = int(var.get()) if key != 'maxTtfp' else float(var.get())

        for key in ['devMode', 'run_all']:
            if key in self.dynamic_widgets:
                config_values[key] = "true" if self.dynamic_widgets[key].get() else "false"

        if self.dynamic_widgets['ignore_test_mode'].get():
            config_values['ignore_test_mode'] = ""
        else:
            if 'ignore_test_mode' in config_values:
                del config_values['ignore_test_mode']

        updated_tests = []
        for index in range(len(config_values['tests'])):
            test = {}
            test_prefix = f"{index}_"
            for key in FIELD_NAMES.keys():
                widget_key = f"{test_prefix}{key}"
                if widget_key in self.dynamic_widgets:
                    widget = self.dynamic_widgets[widget_key]
                    if key == 'absGwTxPowerIndex':
                        selected_text = widget.get()
                        selected_index = self.output_power_string_to_index(selected_text)
                        test[key] = selected_index - len(valid_output_power_vals)
                    elif key == 'sub1gGwTxPower':
                        selected_text = widget.get()
                        if selected_text != '0dBm':
                            selected_value = int(selected_text[:-3])
                            test[key] = selected_value
                        else:
                            if 'sub1gGwTxPower' in test:
                                del test['sub1gGwTxPower']
                    elif key in ['rxChannel', 'energizingPattern']:
                        test[key] = int(widget.get())
                    elif key == 'timeProfile':
                        test[key] = [var.get() for var in widget]
                    elif key in ['maxTime', 'delayBeforeNextTest']:
                        test[key] = int(widget.get())
                    else:
                        test[key] = widget.get()

            stop_criteria = {}
            quality_param = {}
            for criterion in CRITERIA_KEYS:
                if criterion in config_values['tests'][index].get('stop_criteria', {}).keys():
                    min_key = f"{test_prefix}stop_criteria_{criterion}_min"
                    max_key = f"{test_prefix}stop_criteria_{criterion}_max"
                    if min_key in self.dynamic_widgets and max_key in self.dynamic_widgets:
                        min_var = self.dynamic_widgets[min_key]
                        max_var = self.dynamic_widgets[max_key]
                        stop_criteria[criterion] = [min_var.get(), max_var.get()]
                if criterion in config_values['tests'][index].get('quality_param', {}).keys():
                    min_key = f"{test_prefix}quality_param_{criterion}_min"
                    max_key = f"{test_prefix}quality_param_{criterion}_max"
                    if min_key in self.dynamic_widgets and max_key in self.dynamic_widgets:
                        min_var = self.dynamic_widgets[min_key]
                        max_var = self.dynamic_widgets[max_key]
                        quality_param[criterion] = [min_var.get(), max_var.get()]

            for criterion in list(config_values['tests'][index].get('stop_criteria', {}).keys()):
                if f"{test_prefix}stop_criteria_{criterion}_min" not in self.dynamic_widgets:
                    del stop_criteria[criterion]
            for criterion in list(config_values['tests'][index].get('quality_param', {}).keys()):
                if f"{test_prefix}quality_param_{criterion}_min" not in self.dynamic_widgets:
                    del quality_param[criterion]

            test['stop_criteria'] = stop_criteria
            test['quality_param'] = quality_param

            updated_tests.append(test)

        config_values['tests'] = updated_tests

    def store_current_state(self):
        if self.current_config is None:
            return

        config_values = self.data[self.current_config]
        for key in ['plDelay', 'rssiThresholdHW', 'rssiThresholdSW', 'maxTtfp']:
            if key in self.dynamic_widgets:
                var, field_type = self.dynamic_widgets[key]
                config_values[key] = int(var.get()) if key != 'maxTtfp' else float(var.get())

        for key in ['devMode', 'run_all']:
            if key in self.dynamic_widgets:
                config_values[key] = "true" if self.dynamic_widgets[key].get() else "false"

        if self.dynamic_widgets['ignore_test_mode'].get():
            config_values['ignore_test_mode'] = ""
        else:
            if 'ignore_test_mode' in config_values:
                del config_values['ignore_test_mode']

        updated_tests = []
        for index in range(len(config_values['tests'])):
            test = {}
            test_prefix = f"{index}_"
            for key in FIELD_NAMES.keys():
                widget_key = f"{test_prefix}{key}"
                if widget_key in self.dynamic_widgets:
                    widget = self.dynamic_widgets[widget_key]
                    if key == 'absGwTxPowerIndex':
                        selected_text = widget.get()
                        selected_index = self.output_power_string_to_index(selected_text)
                        test[key] = selected_index - len(valid_output_power_vals)
                    elif key == 'sub1gGwTxPower':
                        selected_text = widget.get()
                        if selected_text != '0dBm':
                            selected_value = int(selected_text[:-3])
                            test[key] = selected_value
                        else:
                            if 'sub1gGwTxPower' in test:
                                del test['sub1gGwTxPower']
                    elif key in ['rxChannel', 'energizingPattern']:
                        test[key] = int(widget.get())
                    elif key == 'timeProfile':
                        test[key] = [var.get() for var in widget]
                    elif key in ['maxTime', 'delayBeforeNextTest']:
                        test[key] = float(widget.get())
                    else:
                        test[key] = widget.get()

            stop_criteria = {}
            quality_param = {}
            for criterion in CRITERIA_KEYS:
                if criterion in config_values['tests'][index].get('stop_criteria', {}).keys():
                    min_key = f"{test_prefix}stop_criteria_{criterion}_min"
                    max_key = f"{test_prefix}stop_criteria_{criterion}_max"
                    if min_key in self.dynamic_widgets and max_key in self.dynamic_widgets:
                        min_var = self.dynamic_widgets[min_key]
                        max_var = self.dynamic_widgets[max_key]
                        stop_criteria[criterion] = [min_var.get(), max_var.get()]
                if criterion in config_values['tests'][index].get('quality_param', {}).keys():
                    min_key = f"{test_prefix}quality_param_{criterion}_min"
                    max_key = f"{test_prefix}quality_param_{criterion}_max"
                    if min_key in self.dynamic_widgets and max_key in self.dynamic_widgets:
                        min_var = self.dynamic_widgets[min_key]
                        max_var = self.dynamic_widgets[max_key]
                        quality_param[criterion] = [min_var.get(), max_var.get()]

            gw_commands = []
            for widget_key in self.dynamic_widgets.keys():
                if widget_key.startswith(f"gw_command_") and widget_key.endswith(f"_{index}"):
                    command = widget_key.split('_', 2)[-1].rsplit('_', 1)[0]
                    cmd_var = self.dynamic_widgets[widget_key]
                    gw_command_string = f"!{command} {cmd_var.get()}"
                    gw_commands.append(gw_command_string)

            for criterion in list(config_values['tests'][index].get('stop_criteria', {}).keys()):
                if f"{test_prefix}stop_criteria_{criterion}_min" not in self.dynamic_widgets:
                    del stop_criteria[criterion]
            for criterion in list(config_values['tests'][index].get('quality_param', {}).keys()):
                if f"{test_prefix}quality_param_{criterion}_min" not in self.dynamic_widgets:
                    del quality_param[criterion]

            test['stop_criteria'] = stop_criteria
            test['quality_param'] = quality_param
            test['gw_commands'] = gw_commands

            updated_tests.append(test)

        config_values['tests'] = updated_tests
        self.save_to_json()

    def save_to_json(self):
        try:
            formatted_data = self.format_data(self.data)
            with open(self.json_file, 'w') as file:
                json.dump(formatted_data, file, indent=4, separators=(',', ': '), ensure_ascii=False)
            messagebox.showinfo("Success", "Configuration saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save JSON data: {e}")

    def format_data(self, data):
        formatted_data = {}
        for key, value in data.items():
            if isinstance(value, dict) and 'tests' in value:
                formatted_tests = [self.format_test(test) for test in value['tests']]
                value['tests'] = formatted_tests
            formatted_data[key] = value
        return formatted_data

    def format_test(self, test):
        formatted_test = {}
        ordered_keys = ['name', 'rxChannel', 'energizingPattern', 'timeProfile', 'absGwTxPowerIndex', 'sub1gGwTxPower',
                        'maxTime', 'delayBeforeNextTest']
        for key in ordered_keys:
            if key in test:
                formatted_test[key] = test[key]
        if 'timeProfile' in test:
            formatted_test['timeProfile'] = test['timeProfile']
        if 'stop_criteria' in test:
            formatted_test['stop_criteria'] = {k: v for k, v in test['stop_criteria'].items()}
        if 'quality_param' in test:
            formatted_test['quality_param'] = {k: v for k, v in test['quality_param'].items()}
        if 'gw_commands' in test:
            formatted_test['gw_commands'] = test['gw_commands']

        return formatted_test

    def on_save(self):
        if not self.current_config:
            messagebox.showwarning("Warning", "Please select a configuration.")
            return

        self.store_current_state()

    def on_close(self):
        self.destroy()
        sys.exit()

    def load_initial_values(self):
        self.data = self.load_data()
        if self.current_config:
            self.on_config_selected()


if __name__ == "__main__":
    from pathlib import Path
    
    base_path = Path(__file__).parents[1] / 'offline'/ 'configs'
    if (base_path / 'tests_suites_eng.json').is_file():
        app = TestConfigEditorApp(base_path / 'tests_suites_eng.json')
    else:
        app = TestConfigEditorApp(base_path / 'tests_suites.json')
    app.mainloop()
