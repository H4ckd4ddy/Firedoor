/sbin/iptables -t filter -F
/sbin/iptables -t filter -X

/sbin/iptables -t filter -P INPUT DROP
/sbin/iptables -t filter -P FORWARD DROP
/sbin/iptables -t filter -P OUTPUT DROP

/sbin/iptables -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
/sbin/iptables -A OUTPUT -m state --state RELATED,ESTABLISHED -j ACCEPT

/sbin/iptables -t filter -A INPUT -i lo -j ACCEPT
/sbin/iptables -t filter -A OUTPUT -o lo -j ACCEPT
	
#STATIC_RULES#
iptables -t filter -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -t filter -A OUTPUT -p tcp --dport 80 -j ACCEPT
iptables -t filter -A INPUT -p tcp --dport 873 -j ACCEPT
iptables -t filter -A OUTPUT -p tcp --dport 873 -j ACCEPT
iptables -t filter -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -t filter -A OUTPUT -p tcp --dport 443 -j ACCEPT
iptables -t filter -A INPUT -p udp --dport 53 -j ACCEPT
iptables -t filter -A OUTPUT -p udp --dport 53 -j ACCEPT
iptables -t filter -A INPUT -p tcp --dport 53 -j ACCEPT
iptables -t filter -A OUTPUT -p tcp --dport 53 -j ACCEPT
iptables -t filter -A OUTPUT -p tcp --dport 5000 -j ACCEPT
iptables -I OUTPUT -p udp --dport 67:68 --sport \ 67:68 -j ACCEPT
#STATIC_RULES#

if [ $2 == "open" ]
then
	if [ ! -z "$3" ]
	then
		
		action="ACCEPT"
		ip=$3
		/sbin/iptables -t filter -A INPUT -p tcp --dport 22 -s $ip -j $action
		/sbin/iptables -t filter -A OUTPUT -p tcp --dport 22 -d $ip -j $action
		
		/sbin/iptables -t filter -A INPUT -p icmp -s $ip -j $action
		/sbin/iptables -t filter -A OUTPUT -p icmp -d $ip -j $action
		
	else
		
		action="ACCEPT"
		/sbin/iptables -t filter -A INPUT -p tcp --dport 22 -j $action
		/sbin/iptables -t filter -A OUTPUT -p tcp --dport 22 -j $action
		
		/sbin/iptables -t filter -A INPUT -p icmp -j $action
		/sbin/iptables -t filter -A OUTPUT -p icmp -j $action
		
	fi
	echo 1
	echo "$path firedoor close" | at now +2 minute
else
	echo Close
fi