<?php

$fichier = basename(__FILE__);//selection du fichier courant
$valeur = file_get_contents($fichier);//lecture de tout le contenu
$separation = explode('[B'.'DD]', $valeur);//separation des deux partie à l'aide du marqueur /!\ne pas le marquer ailleur/!\ (partie code et partie BDD)
$code = $separation[0];//partie code
$bdd = $separation[1];//partie BDD
$logs = $separation[2];
$bdd = json_decode($bdd, true);//JSON vers tableau

if(isset($_POST["action_setting"])){
	$action_setting = $_POST["action_setting"];
}elseif(isset($_GET["action_setting"])){
	$action_setting = $_GET["action_setting"];
}else{
	$action_setting = null;
}

if($action_setting == "change_setting"){
	
	$bdd["server"] = $_POST["server"];
	
	if(strlen($_POST["password_1"]) > 0){
		if($_POST["password_1"] == $_POST["password_2"]){
			$bdd["password"] = hash("sha512",$_POST["password_1"]);
			$info = "Changements validés";
		}else{
			$erreur = "Erreur: les mots de passe ne correspondent pas";
		}
	}
	
	$bdd["otp"] = ($_POST["otp"])?true:false;
	
	file_put_contents($fichier, ($code.'[B'.'DD]'.json_encode($bdd).'[B'.'DD]'.$logs));
	
}elseif($action_setting == "clear_ip"){
	
	$bdd["timestamp"] = "0";
	$bdd["IP"] = array();
	
	file_put_contents($fichier, ($code.'[B'.'DD]'.json_encode($bdd).'[B'.'DD]'.$logs));
	
	$info = "IP effacées";
	
}

?>
<html>
	<head>
		<title><?php echo $titre; ?></title>
		<style>
		body {
			text-align: center;
			background: black;
			font-family: arial;
		}
		
		a {
			text-decoration: none;
		}
		
		.cache {
			display: none;
		}
		
		#title {
			text-align: center;
			color: white;
			font-weight: bold;
			font-size: 30px;
		}
		
		#retour {
			position: fixed;
			top: 5px;
			left: 5px;
			text-decoration: none;
			color: white;
			font-size: 40px;
			font-weight: bold;
		}
		
		#serveur {
			color: white;
			position: fixed;
			top: 10px;
			right: 10px;
			font-size: 20px;
		}
		
		#page {
			width: 90%;
			margin-top: 10%;
		}
		
		input, button {
			width: 350px;
			background: #4f4f4f;
			border: none;
			font-size: 25px;
			color: white;
			padding: 5px;
			border-radius: 5px;
			outline: none;
		}
		
		button {
			margin-top: 20px;
			background: #3b3b3b;
		}
		
		#clear_ip {
			color: red;
			position: fixed;
			bottom: 0;
			right: 0;
			padding: 20px;
			font-weight: bold;
			cursor: pointer;
		}
		
		.onoffswitch {
			position: relative; width: 60px;
			-webkit-user-select:none; -moz-user-select:none; -ms-user-select: none;
		}
		.onoffswitch-checkbox {
			display: none;
		}
		.onoffswitch-label {
			display: block; overflow: hidden; cursor: pointer;
			border: 2px solid #E3E3E3; border-radius: 36px;
		}
		.onoffswitch-inner {
			display: block; width: 200%; margin-left: -100%;
			transition: margin 0.3s ease-in 0s;
		}
		.onoffswitch-inner:before, .onoffswitch-inner:after {
			display: block; float: left; width: 50%; height: 36px; padding: 0; line-height: 36px;
			font-size: 16px; color: white; font-family: Trebuchet, Arial, sans-serif; font-weight: bold;
			box-sizing: border-box;
		}
		.onoffswitch-inner:before {
			content: "";
			padding-left: 10px;
			background-color: #3BBEFF; color: #FFFFFF;
		}
		.onoffswitch-inner:after {
			content: "";
			padding-right: 10px;
			background-color: #000000; color: #666666;
			text-align: right;
		}
		.onoffswitch-switch {
			display: block; width: 36px; margin: 0px;
			background: #FFFFFF;
			position: absolute; top: 0; bottom: 0;
			right: 20px;
			border: 2px solid #E3E3E3; border-radius: 36px;
			transition: all 0.3s ease-in 0s; 
		}
		.onoffswitch-checkbox:checked + .onoffswitch-label .onoffswitch-inner {
			margin-left: 0;
		}
		.onoffswitch-checkbox:checked + .onoffswitch-label .onoffswitch-switch {
			right: 0px; 
		}
		</style>
		<script>
		function password_change_activation(){
			document.getElementById('password_change').className = 'cache';
			document.getElementById('password_inputs').className = '';
		}
		</script>
	</head>
	<body>
		<center>
			<div id="title">Paramètres</div>
			<a id="retour" href="<?php echo basename(__FILE__); ?>"><</a>
			<div id="serveur">Serveur : <?php echo $bdd["server"]; ?></div>
			<div id="page">
				<form method="POST" action="<?php echo basename(__FILE__); ?>?action=settings">
					<input type="hidden" name="action_setting" value="change_setting" />
					<input type="text" name="server" placeholder="Nom du serveur" value="<?php echo $bdd["server"]; ?>" /><br/>
					<button type="button" id="password_change" onClick="password_change_activation()" >Changer de mot de passe</div>
					<div id="password_inputs" class="cache">
						<input type="password" name="password_1" placeholder="Mot de passe" /><br/>
						<input type="password" name="password_2" placeholder="Confirmation" /><br/>
					</div>
					
					<div class="onoffswitch">
						<input type="checkbox" name="otp" class="onoffswitch-checkbox" id="myonoffswitch" <?php if($bdd["otp"]){echo "checked";} ?>>
						<label class="onoffswitch-label" for="myonoffswitch">
							<span class="onoffswitch-inner"></span>
							<span class="onoffswitch-switch"></span>
						</label>
					</div>
					
					<button type="submit">Enregistrer</button>
				</form>
			</div>
			<a id="clear_ip" href="<?php echo basename(__FILE__); ?>?action=settings&action_setting=clear_ip">Effacer la liste des IP</a>
		</center>
	</body>
</html>