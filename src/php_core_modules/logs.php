<?php

if(isset($_GET["graph"]) && preg_match("/[a-zA-Z]+/",$_GET["graph"])){
	$file = $_GET["graph"];
	if(isset($_GET["date"]) && preg_match('/^\d+(\-\d+)*$/',$_GET["date"])){
		$date = $_GET["date"];
	}else{
		$scan = scandir($logs_path);
		unset($scan[0], $scan[1]);
		natcasesort($scan);
		$scan = array_reverse($scan);
		$date = $scan[0];
	}
	$path = $logs_path."/".$date."/".$file.".log";
	echo file_get_contents($path);
}

?>