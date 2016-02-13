#!/sbin/sh
echo \#!/sbin/sh > /tmp/createnewboot.sh
echo /tmp/mkbootimg --kernel /tmp/Image.gz-dtb --ramdisk /tmp/boot.img-ramdisk.gz --cmdline \"$(cat /tmp/cmdline.cfg)\" --pagesize 2048 --ramdisk_offset 0x11000000 --tags_offset 0x10000100 --output /tmp/newboot.img >> /tmp/createnewboot.sh
chmod 777 /tmp/createnewboot.sh
/tmp/createnewboot.sh
return $?
