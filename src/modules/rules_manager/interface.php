<?php

$fichier = basename(__FILE__);//selection du fichier courant
$valeur = file_get_contents($fichier);//lecture de tout le contenu
$separation = explode('[B'.'DD]', $valeur);//separation des deux partie à l'aide du marqueur /!\ne pas le marquer ailleur/!\ (partie code et partie BDD)
$code = $separation[0];//partie code
$bdd = $separation[1];//partie BDD
$logs = $separation[2];
$bdd = json_decode($bdd, true);//JSON vers tableau

if(isset($_POST["action_rules"])){
	$action_rules = $_POST["action_rules"];
}elseif(isset($_GET["action_rules"])){
	$action_rules = $_GET["action_rules"];
}else{
	$action_rules = null;
}

$fichier = basename(__FILE__);
$valeur = file_get_contents($fichier);
$separation = explode("\n#STATIC_"."RULES#\n", $valeur);
$rules = $separation[1];


if($action_rules == "save_rules"){
	
	$new_rules = str_replace("\r", '', $_POST["rules"]);
	
	file_put_contents($fichier, ($separation[0]."\n#STATIC_"."RULES#\n".$new_rules.chr(10)."#STATIC_"."RULES#\n".$separation[2]));
	
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
		
		input, button, textarea {
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
		
		td {
			padding: 10px;
		}
		
		table {
			 border-collapse: collapse;
			 font-size: 15px;
			 box-shadow: 1px 1px 10px #555;
			 margin-bottom: 150px;
		}
		
		table tbody:nth-child(2n+1) {
			background: #d1d1d1;
		}
		
		table tbody:first-child {
			color: white;
			background: black;
		}
		
		textarea {
			width: 70%;
			height: 50%;
			font-size: 15px;
		}
		</style>
	</head>
	<body>
		<center>
			<div id="title">Regles Fixes</div>
			<a id="retour" href="<?php echo basename(__FILE__); ?>"><</a>
			<div id="serveur">Serveur : <?php echo $serveur; ?></div>
			<div id="page">
				<form method="POST" action="<?php echo basename(__FILE__); ?>?action=rules_manager">
					
					<input type="hidden" name="action_rules" value="save_rules" />
					
					<textarea name="rules" spellcheck="false"><?php echo $rules; ?></textarea>
					<br/><br/>
					<button type="submit">Enregistrer</button>
				</form>
			</div>
		</center>
	</body>
</html>