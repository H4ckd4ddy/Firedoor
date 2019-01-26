if [ $("whoami") != "root" ]
then
	echo "Vous devez lancer l'installation comme root"
	exit
fi
if [ -e /etc/systemd/system/firedoor.service ]
then
	echo "Firedoor est deja installé"
	exit
fi
echo "[Service]" >> /etc/systemd/system/firedoor.service
echo "Type=oneshot" >> /etc/systemd/system/firedoor.service
echo "RemainAfterExit=yes" >> /etc/systemd/system/firedoor.service
echo "ExecStart=/bin/bash $path startup" >> /etc/systemd/system/firedoor.service
echo "ExecStop=/bin/bash $path clean" >> /etc/systemd/system/firedoor.service
echo "[Install]" >> /etc/systemd/system/firedoor.service
echo "WantedBy=default.target" >> /etc/systemd/system/firedoor.service
chmod 700 /etc/systemd/system/firedoor.service
systemctl enable firedoor
systemctl start firedoor