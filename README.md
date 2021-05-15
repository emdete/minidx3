# MiniDX3

Bought a minidx3 card reader. Pretty nice reader - cheap, tiny, and battery
powered.

Sadly, the software is Windows only and made by a sketchy company based in
China. I refuse to run it on anything but a VM with no network...as it opens
network connections...for seemingly unknwon reasons. I'm also a pretty paranoid
person, so it might be nothing.

So I reversed engineered the USB Serial protocol it uses and created a partially
implemented Python library that does the following:

- Login to the device.
- Set the date on the device (without it does nothing).
- Get the number of entries from the device.
- Get an entry from the device.
- Get product version from the device.
- Get firmware date from the device.
- Get any sort of register from the device.
- Logout of the device.

This is a complete rewrite of the original software written by mrmoss. I used
the [manual](minidx3_user_manual.pdf) which describes the protocol a bit (so no
real reverse engineering necesary).

