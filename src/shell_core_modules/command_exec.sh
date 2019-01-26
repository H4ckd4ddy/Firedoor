if [ -p /tmp/firedoor_pipe_in ]
then
	cmd=$(echo $2 | base64 -d)
	echo $cmd > /tmp/firedoor_pipe_in
	cat < /tmp/firedoor_pipe_out
else
	echo "Erreur : executeur inactif"
fi