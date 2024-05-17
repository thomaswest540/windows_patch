import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

PSEXEC_PATH = r"C:\pstools\psexec.exe"

def browse_hosts_file():
    hosts_file_path = filedialog.askopenfilename()
    hosts_file_path = os.path.abspath(hosts_file_path)
    hosts_entry.delete(0, tk.END)
    hosts_entry.insert(0, hosts_file_path)

def browse_update_file():
    update_file_path = filedialog.askopenfilename()
    update_file_path = os.path.abspath(update_file_path)
    update_file_entry.delete(0, tk.END)
    update_file_entry.insert(0, update_file_path)

def copy_update_file():
    hosts_file_path = hosts_entry.get()
    update_file_path = update_file_entry.get()

    if not hosts_file_path or not update_file_path:
        messagebox.showwarning("Missing Information", "Please select the hosts file and update file.")
        return

    with open(hosts_file_path, 'r') as file:
        for host in file:
            host = host.strip()
            command = f'copy "{update_file_path}" \\\\{host}\\c$\\updates\\'
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                messagebox.showinfo("File Transfer", f"Copied update file to {host}")
            else:
                messagebox.showwarning("File Transfer Error", f"Failed to copy update file to {host}.\n{result.stderr}")

def check_update_file():
    hosts_file_path = hosts_entry.get()
    update_file_name = os.path.basename(update_file_entry.get())

    if not hosts_file_path or not update_file_entry.get():
        messagebox.showwarning("Missing Information", "Please select the hosts file and update file.")
        return

    with open(hosts_file_path, 'r') as file:
        for host in file:
            host = host.strip()
            command = f'dir \\\\{host}\\c$\\updates\\{update_file_name}'
            subprocess.run(command, shell=True)

def run_update():
    hosts_file_path = hosts_entry.get()
    update_file_name = os.path.basename(update_file_entry.get())

    if not hosts_file_path or not update_file_entry.get():
        messagebox.showwarning("Missing Information", "Please select the hosts file and update file.")
        return

    with open(hosts_file_path, 'r') as file:
        for host in file:
            host = host.strip()
            unblock_command = f'"{PSEXEC_PATH}" \\\\{host} -s -accepteula powershell -command "Unblock-File -Path \\"C:\\updates\\{update_file_name}\\""'
            run_command = f'"{PSEXEC_PATH}" \\\\{host} -s -accepteula cmd.exe /c "C:\\updates\\{update_file_name}"'

            # Unblock the file on the remote computer
            unblock_result = subprocess.run(unblock_command, shell=True, capture_output=True, text=True)
            if unblock_result.returncode != 0:
                messagebox.showwarning("Unblock Error", f"Failed to unblock file on {host}.\n{unblock_result.stderr}")

            # Run the update
            run_result = subprocess.run(run_command, shell=True, capture_output=True, text=True)
            if run_result.returncode == 0:
                messagebox.showinfo("Update Run", f"Update run successfully on {host}")
            else:
                messagebox.showwarning("Update Run Error", f"Failed to run update on {host}.\n{run_result.stderr}")

def enable_smartscreen():
    command = f'"{PSEXEC_PATH}" -s -accepteula powershell -command "Set-ItemProperty -Path \'HKLM:\\Software\\Policies\\Microsoft\\Windows\\System\' -Name \'EnableSmartScreen\' -Value 1"'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        status_label.config(text="SmartScreen enabled. You can now use the Run Update button.")
    else:
        messagebox.showwarning("Enable SmartScreen Error", f"Failed to enable SmartScreen.\n{result.stderr}")

def disable_smartscreen():
    command = f'"{PSEXEC_PATH}" -s -accepteula powershell -command "Set-ItemProperty -Path \'HKLM:\\Software\\Policies\\Microsoft\\Windows\\System\' -Name \'EnableSmartScreen\' -Value 0"'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        status_label.config(text="SmartScreen disabled. You can now copy the update file.")
    else:
        messagebox.showwarning("Disable SmartScreen Error", f"Failed to disable SmartScreen.\n{result.stderr}")

# Create the main window
root = tk.Tk()
root.title("Program Update Tool")

# Create a frame for hosts selection
hosts_frame = tk.Frame(root)
hosts_frame.pack(padx=10, pady=10, fill=tk.X)

hosts_label = tk.Label(hosts_frame, text="Select Hosts File:")
hosts_label.pack(side=tk.LEFT)

hosts_entry = tk.Entry(hosts_frame, width=50)
hosts_entry.pack(side=tk.LEFT, padx=(5, 0))

browse_hosts_button = tk.Button(hosts_frame, text="Browse", command=browse_hosts_file)
browse_hosts_button.pack(side=tk.LEFT, padx=(5, 0))

# Create a frame for update file selection
update_file_frame = tk.Frame(root)
update_file_frame.pack(padx=10, pady=10, fill=tk.X)

update_file_label = tk.Label(update_file_frame, text="Select Update File:")
update_file_label.pack(side=tk.LEFT)

update_file_entry = tk.Entry(update_file_frame, width=50)
update_file_entry.pack(side=tk.LEFT, padx=(5, 0))

browse_update_button = tk.Button(update_file_frame, text="Browse", command=browse_update_file)
browse_update_button.pack(side=tk.LEFT, padx=(5, 0))

# Create buttons for copy, check, and run update
copy_button = tk.Button(root, text="Copy Update File", command=copy_update_file)
copy_button.pack(pady=5)

check_button = tk.Button(root, text="Check Update File", command=check_update_file)
check_button.pack(pady=5)

run_button = tk.Button(root, text="Run Update", command=run_update)
run_button.pack(pady=5)

enable_smartscreen_button = tk.Button(root, text="Enable SmartScreen", command=enable_smartscreen)
enable_smartscreen_button.pack(pady=5)

disable_smartscreen_button = tk.Button(root, text="Disable SmartScreen", command=disable_smartscreen)
disable_smartscreen_button.pack(pady=5)

# Create a label for status messages
status_label = tk.Label(root, text="Please disable SmartScreen before copying the update file.")
status_label.pack(side=tk.BOTTOM, pady=10)

# Start the GUI event loop
root.mainloop()
