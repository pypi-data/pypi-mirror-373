#!/bin/bash

USER=`whoami`

# -----------  jsut checking number of parameters.
# --- this script is called from py wrapper
# --- and paramters are passed using sys.argv
# --- and compatible with uv uvx
#
echo "Parameters: $@"
if [ "$#" -lt 1 ]; then
    echo "no parameter."
elif  [ "$#" -lt 2 ]; then
  echo "one parameter."
fi

function enablesmart(){

    disks=($(lsblk -dno NAME,TYPE | awk '$2=="disk" {print "/dev/"$1}'))
for disk in "${disks[@]}"; do
    sudo smartctl --smart=on --offlineauto=on --saveauto=on  /dev/sdd
done
    }





function showdisks(){

blkid | grep -v squashfs | awk '{
    dev=$1
    label="N/A"
    type="N/A"
    for (i=2; i<=NF; i++) {
        if ($i ~ /LABEL=/) {
            sub("LABEL=", "", $i)
            sub("\"", "", $i)
            label=$i
        }
        if ($i ~ /TYPE=/) {
            sub("TYPE=", "", $i)
            sub("\"", "", $i)
            sub("\"", "", $i)
            type=$i
        }
    }
    print dev," \t", "LABEL=" label, "\t", "TYPE=" type
}'
echo ________________________________
df --output='source','fstype','size','pcent','target' --block-size=1000000k -l | grep -v tmpfs | tail -n +2
echo ________________________________
if [ "$USER" != "root" ]; then
    echo X...  ... USE AS ROOT... sudo btrfs fi show
else
    echo i...  ...  AS ROOT...
    sudo btrfs fi show
fi
}

echo __________________________________ showdisks only _____
showdisks
echo _______________________________________________________

which smartctl >/dev/null
if [ "$?" != "0" ]; then
    echo X... apt install smartmontools
    echo .... apt install gsmartcontrol
    exit 1
fi


disks=($(lsblk -dno NAME,TYPE | awk '$2=="disk" {print "/dev/"$1}'))



if [ "$1" = "mountall" ]; then
    parts=($(lsblk -ln -o NAME,TYPE,FSTYPE | awk '$2=="part" && $3 != "ntfs" && $3 != "swap" && $3 != "" {print "/dev/"$1}'))
    echo i... mounting all
    for disk in "${parts[@]}"; do
	body=$(basename  "$disk")
	if findmnt -rn -S "$disk" > /dev/null; then
	    echo -e "\e[90m  o... $disk is already mounted \e[0m"
	else
	    echo i.. mounting /mnt/${body}
	    sudo  mkdir -p /mnt/${body}
	    sudo mount $disk  /mnt/${body}
	fi
	# fstyp=`blkid -o value -s TYPE $disk`
	# if [ "$fstyp" = "btrfs" ]; then
	#     echo -en  "i... BTRFS detected on $disk "
	#     sudo btrfs check --force --progress ${disk} 2>/dev/null| grep "no error found"
	#     if [ "$?" != "0" ]; then
	# 	echo -e "\e[31mX... CHECKERROR on $disk \e[0m"
	#     fi
	#     sudo btrfs scrub status ${disk} 2>/dev/null| grep "no errors found"
	#     if [ "$?" != "0" ]; then
	# 	echo -e "\e[31mX... SCRUBERROR on $disk \e[0m"
	#     fi
	# fi
    done
    #echo 'for dir in /mnt/*; do echo $dir;  dd if=/dev/zero of="${dir}/zerofile" bs=1M count=102400 ;done'
    exit 0
else
  echo "i... not mounting brutaly all disks..."
  echo H... for BRUTAL mount all disks ... ... ... ... ... say ... smartnow mountall
  #echo .
fi

echo _______________________________________________________


if [ "$1" = "chkbtrfs" ]; then
    parts=($(lsblk -ln -o NAME,TYPE,FSTYPE | awk '$2=="part" && $3 != "ntfs" && $3 != "swap" && $3 != "" {print "/dev/"$1}'))
    #echo i... mounting all
    for disk in "${parts[@]}"; do
	body=$(basename  "$disk")
	#if findmnt -rn -S "$disk" > /dev/null; then
	#    echo -e "\e[90m  o... $disk is already mounted \e[0m"
	#else
	    #echo i.. mounting /mnt/${body}
	    #sudo  mkdir -p /mnt/${body}
	    #sudo mount $disk  /mnt/${body}
	#fi
	fstyp=`blkid -o value -s TYPE $disk`
	if [ "$fstyp" = "btrfs" ]; then

	    echo -en  "i... BTRFS detected on $disk "
	    sudo btrfs check --force --progress ${disk} 2>/dev/null| grep "no error found"
	    if [ "$?" != "0" ]; then
		echo -e "\e[31mX... CHECKERROR on $disk \e[0m"
	    fi

	    sudo btrfs scrub status ${disk} 2>/dev/null| grep "no error" | grep "found"
	    if [ "$?" != "0" ]; then
		echo -e "\e[31mX... SCRUBERROR on $disk \e[0m"
	    fi


	fi
    done
    echo 'for dir in /mnt/*; do echo $dir;  dd if=/dev/zero of="${dir}/zerofile" bs=1M count=102400 ;done'
    exit 0
    else
    echo "i... not doing brutal checkbtrfs and scrub"
    echo H... for BRUTAL btrsfs --force check and then SCRUB say ... smartnow chkbtrfs
fi


echo _______________________________________________________

for disk in "${disks[@]}"; do
    # Check if the disk has partitions
    partitions=$(lsblk -nlo NAME "$disk" | grep -v "^$(basename $disk)$")
    if [[ -z $partitions && $(lsblk -ndo TRAN "$disk") == "usb" ]]; then
        echo "Skipping USB disk $disk with no partitions."
        continue
    fi


    echo "Checking ...  $disk... "

    if [ "$USER" = "root" ]; then
        echo X...  ... USE AS ROOT... smartctl

    echo -ne "=======: $disk "
    if [[ $disk == *nvme* ]]; then
        sudo smartctl -H -d nvme $disk | grep  "PASSED"
    else
        sudo smartctl -H $disk | grep  "PASSED"
    fi

    if [ $? -ne 0 ]; then
        echo "X... Problem detected with $disk"
    fi

    TEMPRES="/tmp/smartnow.res"

    # Check specific attributes
    if [[ $disk == *nvme* ]]; then
        sudo smartctl -A -d nvme $disk > $TEMPRES
    else
        sudo smartctl -A $disk > $TEMPRES
    fi

    cat $TEMPRES | awk '
        /Percentage Used/ { if ($3 >= 95)       {print "Warning:", disk, " SSD life at", $3"% "; found=1 }}
        /Available Spare:/ { if ($3 <= 10)      {print "Warning:", disk, " Low available spare at", $3"% "; found=1   }}
        /Reallocated_Sector_Ct/ { if ($10 > 0)  {print "Warning:", disk, " Reallocated sectors v=", $10; found=1       }}
        /Current_Pending_Sector/ { if ($10 > 0) {print "Warning:", disk, " Pending sectors v=",$10 ; found=1     }}
        /Offline_Uncorrectable/ { if ($10 > 0)  {print "Warning:", disk, " Uncorrectable sectors v=", $10 ; found=1 }}
        /SSD_Life_Left/ { if ($10 <= 5)         {print "Warning:", disk, " SSD life left at", $10"% " ; found=1    }}
        /Multi_Zone_Error_Rate/ { if ($10 > 0)  {print "Warning:", disk, " Surface or heads damaged v=", $10 ; found=1    }} END {exit found}
        ' disk="$disk"
#        ' disk="$disk" 2>/dev/null

    if [ "$?" != "0" ]; then
	echo "X... ... PROBLEMS ON DISK $disk"
	which notifator >/dev/null
	if [ "$?" = 0 ]; then
	    HO=`hostname`
	    notifator n "$HO: problems on disk $disk"
	fi

    fi

    #echo X...
    #    exit 1
   else
    echo "X... skipping all smartctl tests, root priviledges needed"
  fi
  echo
done
