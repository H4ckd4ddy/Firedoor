#!/bin/bash

path=$(readlink -f $0)
path=${path%/*}

if [ ! -d $path/tmp_build ]
then
	mkdir $path/tmp_build
fi

if [ -e $path/tmp_build/script.sh ]
then
	rm -f $path/tmp_build/script.sh
fi

cp $path/src/script.sh $path/tmp_build/

first_module=true
for core_module in $path/src/shell_core_modules/*.sh; do

	file_name=$(basename $core_module)
	module_name=${file_name%.*}
	
	if [ "$first_module" = true ]
	then
		echo "if [ \$module = \"$module_name\" ]" >> $path/tmp_build/script.sh
	else
		echo "elif [ \$module = \"$module_name\" ]" >> $path/tmp_build/script.sh
	fi
	
	echo "then" >> $path/tmp_build/script.sh
	cat $core_module >> $path/tmp_build/script.sh
	echo "" >> $path/tmp_build/script.sh
	
	first_module=false
	
done

for additional_module in $path/src/modules/*; do

	module_name=$(basename $additional_module)
	
	if [ -e $additional_module/script.sh ]
	then
		
		if [ "$first_module" = true ]
		then
			echo "if [ \$module = \"$module_name\" ]" >> $path/tmp_build/script.sh
		else
			echo "elif [ \$module = \"$module_name\" ]" >> $path/tmp_build/script.sh
		fi
		
		echo "then" >> $path/tmp_build/script.sh
		cat $additional_module/script.sh >> $path/tmp_build/script.sh
		echo "" >> $path/tmp_build/script.sh
		
		first_module=false
		
	fi
	
done

echo "else" >> $path/tmp_build/script.sh
echo "echo \"No module named : \$module\"" >> $path/tmp_build/script.sh
echo "fi" >> $path/tmp_build/script.sh
echo "exit" >> $path/tmp_build/script.sh