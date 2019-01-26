-header-

<?php
if($auth){
	?>
	
	-modules-
	
	<?php
}elseif($action == "command"){
	echo "Acces interdit";
}else{
	?>
	
	-connexion-
	
	<?php
}
?>