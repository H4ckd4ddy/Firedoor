<?php

if(isset($_POST['mdp'])){//si on a une demande de connexion
	
	//systeme anti-bruteforce
	$ip = ($_SERVER['HTTP_X_FORWARDED_FOR']) ? $_SERVER['HTTP_X_FORWARDED_FOR'] : $_SERVER['REMOTE_ADDR'];
	$fichier = basename(__FILE__);//selection du fichier courant
	$valeur = file_get_contents($fichier);//lecture de tout le contenu
	$separation = explode('[B'.'DD]', $valeur);//separation des deux partie à l'aide du marqueur /!\ne pas le marquer ailleur/!\ (partie code et partie BDD)
	$code = $separation[0];//partie code
	$bdd = $separation[1];//partie BDD
	$logs = $separation[2];
	$bdd = json_decode($bdd, true);//JSON vers tableau
	$restant = (intval($bdd["timestamp"]) + (60*60*24)) - time();//calcul du temps restant à la BDD à partir du timestamp de la BDD et le timestamp courant
	if($restant < 0){//si le temps restant à la BDD est inferieur a 0
		$bdd["timestamp"] = time();//maj du timestamp
		$bdd["IP"] = array();//vidange des IP
		file_put_contents($fichier, ($code.'[B'.'DD]'.json_encode($bdd).'[B'.'DD]'.$logs));//reformation du contenu et reecriture dans le fichier
	}
	
	if(array_count_values($bdd["IP"])[$ip] < 3){//si l'ip du visiteur est contenue moins de 3 fois dans la liste
		
		$validation = false;
		
		if($bdd["otp"]){
			
			$data = array(
				'ID'=>'000001',
				'code'=> $_POST['mdp']
			);
			
			$postdata = http_build_query($data);
			 
			$options = 
			array(
				'http' =>
				array(
					'method' => 'POST',
					'header' => 'Content-type: application/x-www-form-urlencoded',
					'content' => $postdata
				),
				"ssl" =>
				array(
					"verify_peer" => false,
					"verify_peer_name" => false
				)
			);
			 
			$context  = stream_context_create($options);
			$resultat = file_get_contents('https://otp.sellan.fr', false, $context);
			
			if($resultat == "OK"){
				$validation = true;
			}
			
		}elseif(hash("sha512", $_POST['mdp']) == $bdd["password"]){//si le mot de passe est correct
			$validation = true;
		}
		
		if($validation){
			$_SESSION['acces'] = sha1(md5(date('FMmntLoYy')));//la variable d'acces contenant le sha1 du md5 des variables de date est stocke en session
			$_SESSION['ip'] = ($_SERVER['HTTP_X_FORWARDED_FOR']) ? $_SERVER['HTTP_X_FORWARDED_FOR'] : $_SERVER['REMOTE_ADDR'];//l'ip en stocke dans la session
			$_SESSION['navigateur'] = $_SERVER["HTTP_USER_AGENT"];//l'user agent du navigateur est stocke dans la session
			
			session_regenerate_id();//regeneration des identifiants de session PHP pour eviter les fixations de session
			header('Location: '.basename(__FILE__));//rechargement de la page
			exit();//arret de l'execution du script
		}else{
			$fichier = basename(__FILE__);//selection du fichier courant
			$valeur = file_get_contents($fichier);//lecture de tout le contenu
			$separation = explode('[B'.'DD]', $valeur);//separation des deux partie à l'aide du marqueur /!\ne pas le marquer ailleur/!\ (partie code et partie BDD)
			$code = $separation[0];//partie code
			$bdd = $separation[1];//partie BDD
			$logs = $separation[2];
			$bdd = json_decode($bdd, true);//JSON vers tableau
			array_push($bdd["IP"], $ip);//Ajout de l'IP actuelle
			file_put_contents($fichier, ($code.'[B'.'DD]'.json_encode($bdd).'[B'.'DD]'.$logs));//reformation du contenu et reecriture dans le fichier
			fclose($fichier);//fermeture du fichier
			$erreur = "Mot de passe incorrect";//declaration de l'erreur
		}
		
	}else{//si l'ip du visiteur est contenue 3 fois ou plus dans la liste
		
		//$min = floor($restant / 60);//calcul des arrondi des minutes restantes au plus pres
		//$sec =  $restant - (floor($restant / 60) * 60);//calcul des arrondi des secondes restantes
		//$erreur = "Bloquage IP actif : merci d'attendre ".$min." min et ".$sec." sec";//affichage du temps restant avec les secondes
		
		$min = ceil($restant / 60);//calcul des arrondi des minutes restantes a la valeur supperieur
		$heures = 0;
		$jours = 0;
		
		if($min >= 60){//si le bloquage est supperieur à 1 heure
			$heures = floor($min / 60);//on divise et on troncature pour avoir les heures
			$min = $min % 60;//on prend le reste des minute par modulo
		}
		
		if($heures > 24){//si le bloquage est supperieur à 1 journée
			$jours = floor($heures / 24);//on divise et on troncature pour avoir les jours
			$heures = $heures % 24;//on prend le reste des heures par modulo
		}
		
		$temps = ($jours > 0) ? $jours." jour(s) " : '';
		
		$temps .= (($jours+$heures) > 0) ? $heures." heure(s) et " : '';
		
		$temps .= $min." min";
		
		$erreur = "Bloquage actif : merci d'attendre ".$temps;//affichage du temps restant
		
	}
	
}
?>
<html>
	<head>
		<title><?php echo $titre; ?></title>
		<style>
		body {
			text-align: center;
			background-color: black;
			font-family: arial;
		}
		
		.cadena {
			top: -45px;
			left: 30%;
			width: 500px;
			height: 500px;
			position: absolute;
			overflow: hidden;
			display: none;
		}
		
		.cadena .anse {
			width: 40%;
			height: 40%;
			position: absolute;
			left: 50%;
			margin-left: -20%;
			top: 14%;
			background-color: #000;
			border-radius: 40%;
			background-color: #02A7D7;
		}
		
		.cadena .trou-anse {
			width: 24%;
			height: 40%;
			position: absolute;
			left: 50%;
			margin-left: -12%;
			top: 22%;
			background-color: black;
			border-radius: 25%;
		}
		
		.cadena .boitier {
			width: 60%;
			height: 48%;
			position: absolute;
			left: 50%;
			margin-left: -30%;
			bottom: 11%;
			background-color: #000;
			border-radius: 15%;
			background-color: #02A7D7;
		}
		
		.cadena .serrure {
			width: 16%;
			height: 16%;
			position: absolute;
			left: 50%;
			margin-left: -8%;
			top: 51%;
			border-radius: 100%;
			background-color: black;
		}
		
		.cadena .serrure:after {
			content: "";
			width: 43%;
			height: 78%;
			position: absolute;
			left: 50%;
			margin-left: -20%;
			top: 95%;
			background-color: inherit;
		}
		
		form {
			margin-top: 15%;
		}
		
		input {
			background: #606060;
			border: none;
			padding: 5px;
			border-radius: 3px;
			font-size: 25px;
		}
		
		input:focus {
			outline: none;
		}
		
		input:hover {
			cursor: pointer;
		}
		
		#serveur {
			color: white;
			position: fixed;
			top: 10px;
			right: 10px;
			font-size: 20px;
		}
		</style>
	</head>
	<body>
		<?php if(isset($erreur)){echo "<span style='width:100%;position:fixed;top:5px;left:0;color:red;'>".$erreur."</span>";} ?>
		<div id="serveur">Serveur : <?php echo $serveur; ?></div>
		<div class="cadena" style="float: left">
			<div class="anse" style="background-color: #02A7D7"></div>
			<div class="trou-anse"></div>
			<div class="boitier" style="background-color: #02A7D7"></div>
			<div class="serrure"></div>
		</div>
		<form name="auht" method="POST" action="<?php echo basename(__FILE__); ?>">
			<input name="mdp" type="password" placeholder="Mot de passe"/>
			<input id="valider" type="submit" value="→"/>
		</form>
	</body>
</html>
<?php echo $copy; ?>