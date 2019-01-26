<?php
//shell_exec("sudo ".realpath(basename(__FILE__))." firedoor close");//on execute le script page contenu dans la page courante en tant que root (sudo)
shell_exec(realpath(basename(__FILE__))." command_exec ".base64_encode(realpath(basename(__FILE__))." firedoor close" ));
?>