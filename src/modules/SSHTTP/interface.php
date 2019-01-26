<?php

$prefix = "SSHTTP ".$version." - ".$serveur." # ";//declaration du prefixe de l'invite de commande

?>

<html>
	<head>
		<title>SSHTTP <?php echo $version." - ".$serveur; ?></title>
		<style>
		
		body {
			background: black;
			color: white;
			text-align: left;
			font-family: Courier;
		}
		
		.prefix {
			color: green;
		}
		
		.command {
			color: white;
			background: none;
			border: none;
			outline: none;
			font-family: Courier;
			width: 80%;
		}
		
		::selection {  
			background: white;
			color: black;
		}
		
		::-moz-selection {  
			background: white;
			color: black;
		}
		
		</style>
		<script>
			
			document.addEventListener("keydown", function(e) {
				if(e.ctrlKey){
					e.preventDefault();
					switch(e.keyCode){
						case 67: add_line();break;//c
						case 68: quit();break;//d
					}
				}else{
					switch(e.keyCode){
						case 13: send_command();break;//return
						case 38: parse_history("up");break;//up
						case 40: parse_history("down");break;//down
					}
				}
			}, false);
			
			document.addEventListener("click", function(e) {
				document.getElementById(current_line).focus();
			}, false);
			
			var number_of_line = 0;
			var current_line = 0;
			var current_history_line = 0;
			
			function initialisation(){
				document.body.innerHTML = document.body.innerHTML.substr(1);
				add_line();
			}
			
			function add_line(command){
				
				if(number_of_line > 0){
					document.getElementById("command_span_"+number_of_line).innerHTML = (command?command:"");
				}
				
				number_of_line++;
				current_line = number_of_line;
				current_history_line = current_line;
				
				var prefix = document.createElement("span");
				prefix.className = "prefix";
				prefix.innerHTML = "<?php echo $prefix; ?>";
				
				var command_span = document.createElement("span");
				command_span.id = "command_span_"+number_of_line;
				
				var command_input = document.createElement("input");
				command_input.id = current_line;
				command_input.className = "command";
				
				document.body.appendChild(prefix);
				command_span.appendChild(command_input);
				document.body.appendChild(command_span);
				document.body.appendChild(document.createElement("br"));
				
				window.scrollTo(0,document.body.scrollHeight);
				document.getElementById(current_line).focus();
				
			}
			
			function quit(){
				window.location = window.location.href.split("?")[0];
			}
			
			function parse_history(direction){
				if((direction == "up")&&(current_history_line > 1)){
					current_history_line--;
				}else if((direction == "down")&&(current_history_line < (number_of_line-1))){
					current_history_line++;
				}
				
				document.getElementById(current_line).value = document.getElementById("command_span_"+current_history_line).innerHTML;
				
			}
			
			function send_command(){
				
				var command = document.getElementById(current_line).value;
				
				if(command == "clear"){
					
					location.reload();
					
				}else if(command == "exit"){
					
					quit();
					
				}else{
					
					document.body.innerHTML += "<span id='resultat-"+current_line+"'></span><br/>";
					
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
							
							document.getElementById('resultat-'+current_line).innerHTML = '...';
							
						}else if(xhr.readyState == 4 && xhr.status == 200){
							
							document.getElementById('resultat-'+current_line).innerHTML = xhr.responseText.substring(1);
							
							add_line(command);
							
						}
						
					}
					
					xhr.open('POST', '<?php echo basename(__FILE__); ?>', true);
					xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
					xhr.send('action=command&command='+command);
					
				}
				
			}
		</script>
	</head>
	<body onload="initialisation()">
		
	</body>
</html>