<?php
//echo shell_exec("sudo ".realpath(basename(__FILE__))." firedoor open ".(($_SERVER['HTTP_X_FORWARDED_FOR']) ? $_SERVER['HTTP_X_FORWARDED_FOR'] : $_SERVER['REMOTE_ADDR']));//on execute le script page contenu dans la page courante en tant que root (sudo)
echo shell_exec(realpath(basename(__FILE__))." command_exec ".base64_encode(realpath(basename(__FILE__))." firedoor open ".(($_SERVER['HTTP_X_FORWARDED_FOR']) ? $_SERVER['HTTP_X_FORWARDED_FOR'] : $_SERVER['REMOTE_ADDR'])) );
?>