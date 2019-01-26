<?php

$version = "v3.0";

$path = realpath(basename(__FILE__));
$logs_path = "/var/log/firedoor";

$serveur = json_decode(explode('[B'.'DD]', file_get_contents(basename(__FILE__)))[1], true)["server"];//recuperation du nmo du serveur dans la BDD

if($serveur == "Default"){
	$serveur = shell_exec('hostname');
	$serveur = str_replace (array("\r\n", "\n", "\r"), '', $serveur);
}

$titre = "Firedoor ".$version." - ".$serveur;
$copy = "<center style='position:fixed;bottom:5px;left:0;width:100%;'><a style='font-weight:bold;color:grey;text-decoration:none;' href='http://contact.sellan.fr' target='_blank' >Firedoor ".$version." Etienne SELLAN - 2016 - 2019</a></center>";

session_start();//demarage de session PHP

if(isset($_POST['action'])){
	$action = $_POST['action'];
}elseif(isset($_GET['action'])){
	$action = $_GET['action'];
}else{
	$action = null;
}

if($action == 'deco'){//si dans l'url, la variable action = deco
	$_SESSION = array();//destruction du tableau de session
	session_regenerate_id();//regeneration des identifiants de session PHP pour eviter les fixations de session
	session_unset();//suppression des sessions courantes
}

if((isset($_SESSION['acces']))&&($_SESSION['acces'] == sha1(md5(date('FMmntLoYy'))))&&($_SESSION['ip'] == ($_SERVER['HTTP_X_FORWARDED_FOR']) ? $_SERVER['HTTP_X_FORWARDED_FOR'] : $_SERVER['REMOTE_ADDR'])&&($_SESSION['navigateur'] == $_SERVER["HTTP_USER_AGENT"])){//si toutes les infos de session correspondes
	$auth = true;
}else{
	$auth = false;
}

?>