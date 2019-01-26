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
			color: white;
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
			<div id="title">VHost</div>
			<a id="retour" href="<?php echo basename(__FILE__); ?>"><</a>
			<div id="serveur">Serveur : <?php echo $serveur; ?></div>
			<div id="page">
				<?php
				$available_path = "/etc/apache2/sites-available";
				$enable_path = "/etc/apache2/sites-enabled";
				$avaible = scandir($available_path);
				$enable = scandir($enable_path);
				unset($avaible[0],$avaible[1],$enable[0],$enable[1]);
				natcasesort($avaible);
				natcasesort($enable);
				
				foreach($avaible as $vhost){
					
					$server_name = shell_exec("grep -v '#' ".$available_path.'/'.$vhost." | grep ServerName");
					$server_name = end(explode(' ', $server_name));
					echo $server_name."<br/>";
					
				}
				
				?>
			</div>
		</center>
	</body>
</html>