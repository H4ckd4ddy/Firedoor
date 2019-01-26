<?php

$fichier = basename(__FILE__);
$valeur = file_get_contents($fichier);
$valeur = explode("\n", $valeur);
$PID_line = preg_grep('/PROCESS_PID'.':/', $valeur);
$PID_line = implode('',$PID_line);
$PID = explode(":", $PID_line)[1];
$process = ($PID == "#")?false:true;

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
		
		.cache {
			display: none;
		}
		
		#compteur {
			color: green;
		}
		
		#deco {
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
			margin-top: 7%;
		}
		
		.icon {
			display: inline-block;
			margin: 50px;
			height: 150px;
			width: 150px;
			border-radius: 15px;
			background-size: cover;
			cursor: pointer;
		}
		
		#ssh {
			background: url('data:image/png;base64,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');
			background-size: cover;
		}
		
		-icons-
		
		#activation_switch {
			position: fixed;
			bottom: 0;
			left: 0;
			padding: 20px;
			font-weight: bold;
		}
		
		.on {
			color: green;
		}
		
		.off {
			color: red;
		}
		</style>
		<script>
		function action(action){
			
			if((action == "deverouillage") && (document.getElementById("compteur").className == "cache")){
				action = "deverouillage";
			}else{
				action = "verouillage";
			}
			
			var xhr = null; 
			if(window.XMLHttpRequest){ // Firefox et autres
				xhr = new XMLHttpRequest(); 
			}else if(window.ActiveXObject){ // Internet Explorer 
				try {
					xhr = new ActiveXObject('Msxml2.XMLHTTP');
				} catch (e) {
					xhr = new ActiveXObject('Microsoft.XMLHTTP');
				}
			}else{
				alert('Votre navigateur ne supporte pas les objets XMLHTTPRequest...'); 
				xhr = false; 
			}
			
			
			xhr.onreadystatechange = function(){
					
				if( xhr.readyState < 4 ){
					
					
					
				}else if(xhr.readyState == 4 && xhr.status == 200){
					
					if(action == "deverouillage"){
						compteur(xhr.responseText.substring(1));
					}else{
						actualisation(Math.round(Date.now()/1000));
					}
					
				}
				
			}
			
			xhr.open('POST', '<?php echo basename(__FILE__) ?>', true);
			xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
			xhr.send('action='+action);
			
		}
		
		function compteur(duree){
			var date = new Date();
			//var secondes = date.getSeconds();
			//var compte = ((duree-1)*60)+(60-secondes);
			var compte = (duree*60);
			var fin_compteur = Math.round(Date.now()/1000) + compte;
			document.getElementById("compteur").className = "";
			actualisation(fin_compteur);
		}
		
		function actualisation(fin_compteur){
			var compte = fin_compteur - Math.round(Date.now()/1000);
			if(compte > 0){
				var minutes = Math.floor(compte/60);
				var secondes = compte - Math.floor(minutes*60);
				document.getElementById("compteur").innerHTML = "Serveur deverouillé pour "+minutes+"min et "+secondes+"sec";
				setTimeout("actualisation("+fin_compteur+");", 1000);
			}else{
				document.getElementById("compteur").className = "cache";
			}
		}
		</script>
	</head>
	<body>
		<center>
			<div id="compteur" class="cache" onClick="action('verouillage')"></div>
			<a id="deco" href="?action=deco">X</a>
			<div id="serveur">Serveur : <?php echo $serveur; ?></div>
			<div id="page">
				<div id="ssh" class="icon" onClick="action('deverouillage')"></div>
				-links-
			</div>
		</center>
		<span id="activation_switch" class="<?php echo ($process)?"on":"off"; ?>" ><?php echo "Process ".(($process)?"actif":"inactif"); ?></span>
	</body>
</html>
<?php echo $copy; ?>