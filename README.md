## **What is Shift ?**

Shift is a command-line tool designed to streamline the process of keeping your computer and Android device in sync. It offers a user-friendly interface and efficient functionality to make file transfers and synchronization a breeze.

### **Requirements**

* **Python:** Ensure you have the latest Python installed on your system, you can download it from [python.org](https://www.python.org) .
* **Android Debug Bridge (ADB):** shift uses ADB under the hood to communicate with your device. You can find the latest ADB releases and download instructions on the [Google Developer website](https://developer.android.com/tools/adb) .

**Connecting your device:**
1. Enable USB debugging on your Android device:
   * Go to Settings > Developer options > USB debugging.
2. Connect your device to your computer using a USB cable.
3. Open a terminal or command prompt and type `adb devices`. If your device is listed, it's connected correctly.

### **Usage**
Pull files from your device to your computer :
```bash
shift pull <source> <destination>
```
Push files from your computer to your device :
```bash
shift push <source> <destination>
```
Synchronize files between your computer and device :
```bash
shift sync <source> <destination>
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

### **Example**
To pull all documents from your device to a folder named "Documents" on your computer:
```bash
shift pull /sdcard/Documents ./Docuemnts
```

To push all documents from your computer to your device and change its name to `MyDocs`:
```bash
shift push --content ./Documents /sdcard/MyDocs
```