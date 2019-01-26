if [ $2 = "start" ]
then
	
	if [ $("whoami") != "root" ]
	then
		echo "Vous devez demarrer le process comme root"
		exit
	fi
	
	separator_part_A='PROCESS'
	separator_part_B='_PID:'
	separator="$separator_part_A$separator_part_B"
	
	pid_line=$(grep $separator $path)
	
	if [[ "$pid_line" == *"#"* ]]
	then
		$path process_manager start_process &
		new_PID=$!
		new_pid_line=${pid_line/"#"/$new_PID}
		sed -i -e "s/$pid_line/$new_pid_line/g" $path
		echo "Activation de l executeur"
	else
		echo "Executeur deja en fonctionnnement"
	fi
	
elif [ $2 = "start_process" ]
then
	in=/tmp/firedoor_pipe_in
	out=/tmp/firedoor_pipe_out
	
	trap "rm -f $in $out" EXIT
	
	if [[ ! -p $in ]]; then
	    mkfifo $in -m 777
	fi
	
	if [[ ! -p $out ]]; then
	    mkfifo $out -m 777
	fi
	
	ref_auth=$(cat /var/log/auth.log | grep 'ssh.*Accepted password' | wc -l)
	
	while true
	do
	    if read line <$in; then
	        echo "$($line)" >> $out
	    else
	    	auth=$(cat /var/log/auth.log | grep 'ssh.*Accepted password' | wc -l)
	    	if (( $auth > $ref_auth ))
	    	then
	    		ref_auth=$auth
	    		$path firedoor close
	    	elif (( $auth < $ref_auth ))
	    	then
	    		ref_auth=$auth
	    	fi
	    fi
	done
elif [ $2 = "stop" ]
then
	
	separator_part_A='PROCESS'
	separator_part_B='_PID:'
	separator="$separator_part_A$separator_part_B"
	
	pid_line=$(grep "$separator" $path)
	
	if [[ "$pid_line" != *"#"* ]]
	then
		pid=$(echo $pid_line | cut -f2 -d:)
		kill $pid
		new_pid_line_part_A='PROCESS_PID'
		new_pid_line_part_B=':#'
		new_pid_line="$new_pid_line_part_A$new_pid_line_part_B"
		sed -i -e "s/$pid_line/$new_pid_line/g" $path
		echo "Desactivation de l executeur"
	else
		echo "Executeur non actif"
	fi
	
elif [ $2 = "status" ]
then
	separator_part_A='PROCESS'
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