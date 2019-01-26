if [ $2 = "start" ]
then
	
	separator_part_A='MONITORING'
	separator_part_B='_PID:'
	separator="$separator_part_A$separator_part_B"
	
	pid_line=$(grep $separator $path)
	
	if [[ "$pid_line" == *"#"* ]]
	then
		$path monitoring start_process > /dev/null 2>&1 &
		new_PID=$!
		new_pid_line=${pid_line/"#"/$new_PID}
		sed -i -e "s/$pid_line/$new_pid_line/g" $path
		echo "Activation du monitoring"
	else
		echo "Monitoring deja en fonctionnnement"
	fi
	
elif [ $2 = "start_process" ]
then
	while true
	do
		sleep 1m
		
		if [ ! -d $logs_path ]
		then
			mkdir -p $logs_path
		fi
		
		date=$(date +%Y-%m-%d)
		
		if [ ! -d $logs_path/$date ]
		then
			mkdir $logs_path/$date
		fi
		
		time=$(date +%Y/%m/%d" "%H:%M:%S)
		
		total_ram=$(($(cat /proc/meminfo | grep "MemTotal" | cut -d: -f2 | awk '{ print $1 }') * 1000 ))
		ram_libre=$(($(cat /proc/meminfo | grep "MemFree" | cut -d: -f2 | awk '{ print $1 }') * 1000 ))
		ram_utilise=$(($total_ram-$ram_libre))
		
		echo "$time , $total_ram , $ram_utilise" >> $logs_path/$date/RAM.log
		#echo "$time , $total_ram , $ram_utilise #RAM" >> $path
		
		
		
		double_mesure=$(top -n 2 -b | grep "%Cpu(s)" | cut -d, -f7 | awk '{ print $1 "+" }')
		
		pourcentage_cpu_libre=$(echo $double_mesure | cut -d+ -f2 | awk '{ print $1 }')
		
		cpu=$((100 - $pourcentage_cpu_libre))
		
		echo "$time , $cpu" >> $logs_path/$date/CPU.log
		#echo "$time , $cpu #CPU" >> $path
		
		
		
		mesure=$(df | grep "^/dev")
		
		nom_disque=$(echo $mesure | awk '{ print $1 }')
		total_disque=$(($(echo $mesure | awk '{ print $2 }') * 1000 ))
		disque_utilise=$(($(echo $mesure | awk '{ print $3 }') * 1000 ))
		disque_libre=$(echo $mesure | awk '{ print $4 }')
		pourcentage=$(echo $mesure | awk '{ print $5 }')
		
		echo "$time , $total_disque , $disque_utilise" >> $logs_path/$date/DISK.log
		
		#echo "$time , $total_disque , $disque_utilise #DISK" >> $path
		#echo "$time , $pourcentage #DISKPOUR" >> ./index.php
		
		current_download_count=$(/sbin/ifconfig eth0 | grep "RX bytes" | cut -d: -f2 | awk '{ print $1 }')
		current_upload_count=$(/sbin/ifconfig eth0 | grep "TX bytes" | cut -d: -f3 | awk '{ print $1 }')
		
		if [ -n "$last_mesure" ]
		then
			delay=$(( $(date +"%s") - $last_mesure ))
			download=$(((($current_download_count - $download_count)) / $delay))
			upload=$(((($current_upload_count - $upload_count)) / $delay))
		else
			sleep 1
			tmp_download_count=$(/sbin/ifconfig eth0 | grep "RX bytes" | cut -d: -f2 | awk '{ print $1 }')
			tmp_upload_count=$(/sbin/ifconfig eth0 | grep "TX bytes" | cut -d: -f3 | awk '{ print $1 }')
			
			download=$(($tmp_download_count - $current_download_count))
			upload=$(($tmp_upload_count - $current_upload_count))
		fi
		
		last_mesure=$(date +"%s")
		
		download_count=$current_download_count
		upload_count=$current_upload_count
		
		echo "$time , $upload , $download" >> $logs_path/$date/NET.log
		
	done
elif [ $2 = "stop" ]
then
	
	separator_part_A='MONITORING'
	separator_part_B='_PID:'
	separator="$separator_part_A$separator_part_B"
	
	pid_line=$(grep "$separator" $path)
	
	if [[ "$pid_line" != *"#"* ]]
	then
		pid=$(echo $pid_line | cut -f2 -d:)
		kill $pid
		new_pid_line_part_A='MONITORING_PID'
		new_pid_line_part_B=':#'
		new_pid_line="$new_pid_line_part_A$new_pid_line_part_B"
		sed -i -e "s/$pid_line/$new_pid_line/g" $path
		echo "Desactivation du monitoring"
	else
		echo "Monitoring non actif"
	fi
	
elif [ $2 = "status" ]
then
	separator_part_A='MONITORING'
	separator_part_B='_PID:'
	separator="$separator_part_A$separator_part_B"
	
	pid_line=$(grep $separator $path)
	
	if [[ "$pid_line" == *"#"* ]]
	then
		status="stopped"
	else
		status="running"
	fi
	echo $status
else
	echo "Erreur: wrong action"
fi