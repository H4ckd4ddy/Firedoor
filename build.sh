#!/bin/bash

path=$(readlink -f $0)
path=${path%/*}

if [ -d $path/tmp_build ]
then
	rm -rf $path/tmp_build
fi
mkdir $path/tmp_build

$path/build_script.sh
$path/build_interface.sh

if [ -d $path/build ]
then
	rm -rf $path/build
fi

mkdir $path/build

echo "#<?php /*" > $path/build/firedoor.php

echo "" >> $path/build/firedoor.php
cat $path/tmp_build/script.sh >> $path/build/firedoor.php
echo "" >> $path/build/firedoor.php

echo "*/ ?>" >> $path/build/firedoor.php

echo "" >> $path/build/firedoor.php
cat $path/tmp_build/interface.php >> $path/build/firedoor.php
echo "" >> $path/build/firedoor.php

echo "" >> $path/build/firedoor.php
cat $path/src/database.php >> $path/build/firedoor.php
echo "" >> $path/build/firedoor.php

chmod 777 $path/build/firedoor.php

rm -rf $path/tmp_build