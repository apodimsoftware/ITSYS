ITSYS is a useful software made for IT professionals note their tasks.

Credits:
- App icon by Google Material Icons


Made by Apodim's Software.


Open source at: https://github.com/apodimsoftware/itsys

VirusTotal flags this code as malicious because (its false-positives):
- Writes data to disk -> This is known for malicious apps, but our app only writes data to the JSON storing the devices
- Was made through Pyinstaller which antiviruses flags it as malicious because of its custom GUI (Pyinstaller from our computer comes directly from Python so its safe)
- Isn't signed -> Because it isn't signed, make sure it comes from this repository


These don't happen with the python file itself. Only because it is packed with Pyinstaller.

We guarantee it doesn't do any damage to your computer, unless you download it from the wrong source.
