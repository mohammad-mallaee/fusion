## **What is Fusion ?**

Fusion is a command-line tool designed to streamline the process of keeping your computer and Android device in sync. It offers a user-friendly interface and efficient functionality to make file transfers and synchronization a breeze.

### **Requirements**

- **Python:** Ensure you have the latest Python installed on your system, you can download it from [python.org](https://www.python.org) .
- **Android Debug Bridge (ADB):** fusion uses ADB under the hood to communicate with your device. You can find the latest ADB releases and download instructions on the [Google Developer website](https://developer.android.com/tools/adb) .

### **Connecting your device**

You have various options to connect your device and all of them are written on the [Google Developer website](https://developer.android.com/tools/adb#Enabling) :

- **USB:** Connect your device to your computer using a USB cable after [enabling USB debugging](https://developer.android.com/tools/adb#Enabling) on your device.
- **WiFi:** Connect your device to your computer [using the same WiFi network](https://developer.android.com/tools/adb#wireless-android11-command-line).
- **Hotspot:** the wifi connection is not supported on Android 10 and lower or with a hotspot connection so you have to use a USB connection at first then use the app. Read along the [Google Developer website](https://developer.android.com/tools/adb#wireless) for more information.

### **Installation**

Use pip (Python Package Index) to install fusion:

```bash
pip install fusion-sync
```

The reason that the package is named `fusion-sync` is because `fusion` was unavailable so, nothing to worry.

### **Usage**

Pull files from your device to your computer :

```bash
fusion pull <source> <destination>
```

Push files from your computer to your device :

```bash
fusion push <source> <destination>
```

Synchronize files between your computer and device :

```bash
fusion sync <source> <destination>
```

#### **Flags**

- **`--dryrun,--dry`:** Perform a dry run without actually transferring files.
- **`--content,-c`:** Transfer content of the directory without the directory itself.
- **`--skip,-p`:** Skip files that exist on both sides.
- **`--sync,-s`:** Synchronize files, overwriting existing ones.
- **`--force,-f`:** Force transfer, ignoring conflicts.
- **`--reverse,-r`:** Reverse the direction of the synchronization.
- **`--delete,-d`:** Delete files that don't exist on the other side.

**P.S**: You can only use one of sync, force or skip flags at a time as they are mutually exclusive.

**P.S 2**: reverse and delete flags are only for sync command.

### **Examples**

To pull all documents from your device to a folder named "Documents" on your computer :

```bash
fusion pull /sdcard/Documents ./Docuemnts
```

Sync two directories and delete files that don't exist on your phone anymore :

```bash
fusion sync --delete /sdcard/Documents ./Documents
```

To push all documents from your computer to your device and change its name to `MyDocs` :

```bash
fusion push --content ./Documents /sdcard/MyDocs
```

### Path Completion
*Fusion* uses argcomplete to provide path completion when pressing  `<Tab>`. According to argcomplete [documentation](https://kislyuk.github.io/argcomplete/index.html#argcomplete-bash-zsh-tab-completion-for-argparse)  you need to register the *Fusion* executable binary to enable this feature. To do so, add the following line to your shell startup file:
```bash
eval "$(register-python-argcomplete fusion)"
```

### Configuration

Fusion allows you to customize its behavior through a configuration file. You can manage your configuration using the following commands:

- **View or Edit current configuration:**
  ```bash
  fusion config <show|edit>
  ```
  edit will open the configuration file in the default editor
- **Set, Add or Remove a configuration value:**
  ```bash
  fusion config <set|add|remove> <key> <value>
  ```

- **Reset configuration to default:**
  ```bash
  fusion config reset
  ```

**Common configuration keys:**
- `excluded_paths`: List of paths to exclude from sync/transfer.
- `hidden_files`: A switch to skip hidden files (files that start with ".")
- `editor`: Editor used for editing configuration and logs (e.g., `vi`, `notepad`).
- `conflict_resolution`: How to handle file conflicts (`sync`, `force`, or `skip`).

The configuration file is stored in Fusion’s config directory. You can also edit it directly if needed.

### Logs

Fusion keeps a log of its operations for troubleshooting and auditing purposes. You can manage logs with the following commands:

- **Open the log file in your configured editor:**
  ```bash
  fusion log open
  ```

- **Copy the log file to a specific directory:**
  ```bash
  fusion log copy <destination_path>
  ```

The log file (`fusion.log`) contains detailed information about transfers, errors, and other events. This can be helpful for debugging or support.