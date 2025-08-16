import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import sys

class RepairTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ITSYS")
        self.root.geometry("900x600")
        self.root.configure(bg="#d4d0c8")
        
        if getattr(sys, 'frozen', False):
            self.data_dir = Path(sys.executable).parent / "ITRepairData"
        else:
            self.data_dir = Path.home() / "Documents" / "ITRepairTracker"
        
        self.data_file = self.data_dir / "repair_data.json"
        
        try:
            os.makedirs(self.data_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Could not create data directory:\n{str(e)}")
            self.root.destroy()
            return
        
        self.devices = []
        try:
            self.devices = self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load data:\n{str(e)}")
            self.root.destroy()
            return
        
        self.create_widgets()
        self.schedule_cleanup()

    def load_data(self):
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            return []
        except json.JSONDecodeError:
            messagebox.showwarning("Warning", "Data file is corrupted. Starting with empty data.")
            return []
        except Exception as e:
            raise Exception(f"Failed to load data: {str(e)}")

    def save_data(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.devices, f, indent=2)
        except Exception as e:
            raise Exception(f"Failed to save data: {str(e)}")

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bd=1, relief="sunken", bg="#d4d0c8")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        title_label = tk.Label(main_frame, text="ITSYS 1.0", font=("Arial", 16, "bold"), bg="#d4d0c8")
        title_label.pack(pady=(10, 20))
        
        form_frame = tk.Frame(main_frame, bg="#d4d0c8")
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Row 0
        tk.Label(form_frame, text="Device Name:", bg="#d4d0c8").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.device_entry = tk.Entry(form_frame, width=30, relief="sunken")
        self.device_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="Serial Number:", bg="#d4d0c8").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.serial_entry = tk.Entry(form_frame, width=20, relief="sunken")
        self.serial_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Row 1
        tk.Label(form_frame, text="Issue Description:", bg="#d4d0c8").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.issue_entry = tk.Entry(form_frame, width=30, relief="sunken")
        self.issue_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="Submitted By:", bg="#d4d0c8").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.submitted_entry = tk.Entry(form_frame, width=20, relief="sunken")
        self.submitted_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # Row 2 - Contact Field
        tk.Label(form_frame, text="Contact Info:", bg="#d4d0c8").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.contact_entry = tk.Entry(form_frame, width=30, relief="sunken")
        self.contact_entry.grid(row=2, column=1, padx=5, pady=5, columnspan=3, sticky="ew")
        
        button_frame = tk.Frame(main_frame, bg="#d4d0c8")
        button_frame.pack(pady=10)
        
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="raised", background="#d4d0c8")
        
        self.add_button = ttk.Button(button_frame, text="Add New Device", command=self.add_device)
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        self.repair_button = ttk.Button(button_frame, text="Mark as Repaired", command=self.mark_repaired)
        self.repair_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel Repair", command=self.cancel_repair)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = ttk.Button(button_frame, text="Delete Selected", command=self.delete_device)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        tree_frame = tk.Frame(main_frame, bg="#d4d0c8")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ("id", "device", "serial", "issue", "submitted", "contact", "status", "date_repaired")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("device", text="Device Name")
        self.tree.heading("serial", text="Serial Number")
        self.tree.heading("issue", text="Issue Description")
        self.tree.heading("submitted", text="Submitted By")
        self.tree.heading("contact", text="Contact Info")
        self.tree.heading("status", text="Status")
        self.tree.heading("date_repaired", text="Date Repaired")
        
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("device", width=120)
        self.tree.column("serial", width=100)
        self.tree.column("issue", width=150)
        self.tree.column("submitted", width=100)
        self.tree.column("contact", width=120)
        self.tree.column("status", width=100, anchor="center")
        self.tree.column("date_repaired", width=100)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.load_treeview()
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief="sunken", anchor="w")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def add_device(self):
        device = self.device_entry.get().strip()
        serial = self.serial_entry.get().strip()
        issue = self.issue_entry.get().strip()
        submitted = self.submitted_entry.get().strip()
        contact = self.contact_entry.get().strip()
        
        if not device or not issue:
            messagebox.showwarning("Input Error", "Device name and issue description are required!")
            return
            
        new_id = max([d['id'] for d in self.devices], default=0) + 1
        new_device = {
            "id": new_id,
            "device": device,
            "serial": serial,
            "issue": issue,
            "submitted": submitted,
            "contact": contact,
            "status": "Pending",
            "date_submitted": datetime.now().strftime("%Y-%m-%d"),
            "date_repaired": ""
        }
        
        self.devices.append(new_device)
        try:
            self.save_data()
            self.load_treeview()
            
            self.device_entry.delete(0, tk.END)
            self.serial_entry.delete(0, tk.END)
            self.issue_entry.delete(0, tk.END)
            self.submitted_entry.delete(0, tk.END)
            self.contact_entry.delete(0, tk.END)
            
            self.status_var.set(f"Device '{device}' added for repair")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save device: {str(e)}")
            self.devices.remove(new_device)

    def mark_repaired(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a device to mark as repaired")
            return
            
        item = self.tree.item(selected[0])
        device_id = item['values'][0]
        
        for device in self.devices:
            if device['id'] == device_id:
                if device['status'] == "Repaired":
                    messagebox.showinfo("Info", "This device is already marked as repaired")
                    return
                    
                device['status'] = "Repaired"
                device['date_repaired'] = datetime.now().strftime("%Y-%m-%d")
                try:
                    self.save_data()
                    self.load_treeview()
                    self.status_var.set(f"Device '{device['device']}' marked as repaired")
                except Exception as e:
                    messagebox.showerror("Save Error", f"Failed to save changes: {str(e)}")
                    device['status'] = "Pending"
                    device['date_repaired'] = ""
                return

    def cancel_repair(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a device to cancel repair")
            return
            
        item = self.tree.item(selected[0])
        device_id = item['values'][0]
        
        for device in self.devices:
            if device['id'] == device_id:
                if device['status'] == "Canceled":
                    messagebox.showinfo("Info", "This repair is already canceled")
                    return
                    
                device['status'] = "Canceled"
                device['date_repaired'] = datetime.now().strftime("%Y-%m-%d")
                try:
                    self.save_data()
                    self.load_treeview()
                    self.status_var.set(f"Repair for '{device['device']}' has been canceled")
                except Exception as e:
                    messagebox.showerror("Save Error", f"Failed to save changes: {str(e)}")
                    device['status'] = "Pending"
                    device['date_repaired'] = ""
                return

    def delete_device(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a device to delete")
            return
            
        item = self.tree.item(selected[0])
        device_id = item['values'][0]
        device_name = item['values'][1]
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{device_name}'?"):
            return
        
        for device in self.devices:
            if device['id'] == device_id:
                self.devices.remove(device)
                try:
                    self.save_data()
                    self.load_treeview()
                    self.status_var.set(f"Device '{device_name}' has been deleted")
                except Exception as e:
                    messagebox.showerror("Delete Error", f"Failed to save after deletion: {str(e)}")
                    self.devices.append(device)
                return

    def load_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for device in self.devices:
            values = (
                device['id'],
                device['device'],
                device['serial'],
                device['issue'],
                device['submitted'],
                device['contact'],
                device['status'],
                device['date_repaired']
            )
            self.tree.insert("", "end", values=values)
            
            if device['status'] == "Repaired":
                self.tree.item(self.tree.get_children()[-1], tags=('repaired',))
            elif device['status'] == "Canceled":
                self.tree.item(self.tree.get_children()[-1], tags=('canceled',))
                
        self.tree.tag_configure('repaired', background='#d0f0d0')
        self.tree.tag_configure('canceled', background='#f0d0d0')

    def schedule_cleanup(self):
        self.cleanup_old_repaired()
        self.root.after(86400000, self.schedule_cleanup)

    def cleanup_old_repaired(self):
        today = datetime.now()
        removed = False
        
        devices_copy = self.devices.copy()
        
        for device in devices_copy:
            if device['status'] == "Repaired" and device['date_repaired']:
                repair_date = datetime.strptime(device['date_repaired'], "%Y-%m-%d")
                if (today - repair_date).days >= 10:
                    self.devices.remove(device)
                    removed = True
        
        if removed:
            try:
                self.save_data()
                self.load_treeview()
                self.status_var.set("Old repaired devices have been removed")
            except Exception as e:
                messagebox.showerror("Cleanup Error", f"Failed to save after cleanup: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = RepairTrackerApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application failed to start:\n{str(e)}")