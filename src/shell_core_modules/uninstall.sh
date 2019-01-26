if [ $("whoami") != "root" ]
then
	echo "Vous devez lancer la desinstallation comme root"
	exit
fi
$path clean
systemctl stop firedoor
systemctl disable firedoor
rm /etc/systemd/system/firedoor.service
/sbin/iptables -F
/sbin/iptables -X
/sbin/iptables -t nat -F
/sbin/iptables -t nat -X
/sbin/iptables -t mangle -F
/sbin/iptables -t mangle -X
/sbin/iptables -P INPUT ACCEPT
/sbin/iptables -P FORWARD ACCEPT
/sbin/iptables -P OUTPUT ACCEPT
rm -rf /var/log/firedoor
echo "Desinstallation terminée"