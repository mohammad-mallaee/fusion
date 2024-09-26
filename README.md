## **What is Fusion ?**

Fusion is a command-line tool designed to streamline the process of keeping your computer and Android device in sync. It offers a user-friendly interface and efficient functionality to make file transfers and synchronization a breeze.


<img style="width:100%; max-width:560px; margin:auto; display:block;" src="https://pouch.jumpshare.com/preview/PK_XqPg8M8wxveGjUUUDzvBlslM2sTlu_t9kIS7CLemNINL2qU_YArePEzdCDbqXFPfdt6yr_MkMmbheFtb9flyhhbS57cMnQUacDTfu-hQ">
</img>


### **Requirements**

- **Python:** Ensure you have the latest Python installed on your system, you can download it from [python.org](https://www.python.org) .
- **Android Debug Bridge (ADB):** fusion uses ADB under the hood to communicate with your device. You can find the latest ADB releases and download instructions on the [Google Developer website](https://developer.android.com/tools/adb) .

### **Connecting your device**

You have varous options to connect your device and all of them are written on the [Google Developer website](https://developer.android.com/tools/adb#Enabling) :

- **USB:** Connect your device to your computer using a USB cable after [enabling USB debugging](https://developer.android.com/tools/adb#Enabling) on your device.
- **WiFi:** Connect your device to your computer [using the same WiFi network](https://developer.android.com/tools/adb#wireless-android11-command-line).
- **Hotspot:** the wifi connection is not supported on Android 10 and lower or with a hotspot connection so you have to use a USB connection at first then use the app. Read along the [Google Developer website](https://developer.android.com/tools/adb#wireless) for more information.

### **Installation**

Use pip (Python Package Index) to install fusion:

```bash
pip install fusion-sync
```

The reason that the package is named `fusion-sync` is because `fusion` is already taken by a different package.

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
fusion sync --delete ./Documents /sdcard/Documents
```

To push all documents from your computer to your device and change its name to `MyDocs` :

```bash
fusion push --content ./Documents /sdcard/MyDocs
```
