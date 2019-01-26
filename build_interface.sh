#!/bin/bash

path=$(readlink -f $0)
path=${path%/*}

if [ ! -d $path/tmp_build ]
then
	mkdir $path/tmp_build
fi

if [ -e $path/tmp_build/modules.php ]
then
	rm -f $path/tmp_build/modules.php
fi

if [ -e $path/tmp_build/modules.css ]
then
	rm -f $path/tmp_build/modules.css
fi

if [ -e $path/tmp_build/modules.html ]
then
	rm -f $path/tmp_build/modules.html
fi

echo "<?php" >> $path/tmp_build/modules.php
first_module=true
for core_module in $path/src/php_core_modules/*.php; do

	file_name=$(basename $core_module)
	module_name=${file_name%.*}
	
	if [ "$first_module" = true ]
	then
		echo "if(\$action == \"$module_name\"){" >> $path/tmp_build/modules.php
	else
		echo "}elseif(\$action == \"$module_name\"){" >> $path/tmp_build/modules.php
	fi
	
	echo "" >> $path/tmp_build/modules.php
	echo "?>" >> $path/tmp_build/modules.php
	cat $core_module >> $path/tmp_build/modules.php
	echo "<?php" >> $path/tmp_build/modules.php
	echo "" >> $path/tmp_build/modules.php
	
	first_module=false
	
done

for additional_module in $path/src/modules/*; do

	module_name=$(basename $additional_module)
	
	if [ -e $additional_module/interface.php ]
	then
		
		if [ "$first_module" = true ]
		then
			echo "if(\$action == \"$module_name\"){" >> $path/tmp_build/modules.php
		else
			echo "}elseif(\$action == \"$module_name\"){" >> $path/tmp_build/modules.php
		fi
		
		echo "" >> $path/tmp_build/modules.php
		echo "?>" >> $path/tmp_build/modules.php
		cat $additional_module/interface.php >> $path/tmp_build/modules.php
		echo "<?php" >> $path/tmp_build/modules.php
		echo "" >> $path/tmp_build/modules.php
		
		if [ -e $additional_module/icon.png ]
		then
			echo "#$module_name {" >> $path/tmp_build/modules.css
			
			img=$(openssl base64 -nopad -in $additional_module/icon.png | tr -d '\n')
			echo "background: url('data:image/png;base64,$img');" >> $path/tmp_build/modules.css
			echo "background-size: cover;" >> $path/tmp_build/modules.css
			
			echo "}" >> $path/tmp_build/modules.css
			echo "" >> $path/tmp_build/modules.css
			
			echo "<a href='<?php echo basename(__FILE__); ?>?action=$module_name'><div id='$module_name' class='icon'></div></a>" >> $path/tmp_build/modules.html
		fi
		
		first_module=false
		
	fi
	
done

sed "/-icons-/{
    s/-icons-//g
    r $path/tmp_build/modules.css
}" $path/src/home.php |
sed "/-links-/{
    s/-links-//g
    r $path/tmp_build/modules.html
}" > $path/tmp_build/home.php

echo "}else{" >> $path/tmp_build/modules.php
echo "?>" >> $path/tmp_build/modules.php
cat $path/tmp_build/home.php >> $path/tmp_build/modules.php
echo "<?php" >> $path/tmp_build/modules.php
echo "}" >> $path/tmp_build/modules.php
echo "?>" >> $path/tmp_build/modules.php
echo "" >> $path/tmp_build/modules.php


if [ -e $path/tmp_build/interface.php ]
then
	rm -f $path/tmp_build/interface.php
fi

sed "/-header-/{
    s/-header-//g
    r $path/src/header.php
}" $path/src/interface.php |
sed "/-modules-/{
    s/-modules-//g
    r $path/tmp_build/modules.php
}" |
sed "/-connexion-/{
    s/-connexion-//g
    r $path/src/connexion.php
}" > $path/tmp_build/interface.php

