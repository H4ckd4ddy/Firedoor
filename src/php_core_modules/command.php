<?php
echo nl2br(htmlentities(shell_exec(realpath(basename(__FILE__))." command_exec ".base64_encode($_POST['command']))));//on execute le script page contenu dans la page courante en tant que root (sudo) avec le parametre "command" pour signaler que c'est un commande
//echo nl2br(htmlentities(shell_exec('echo "'.realpath(basename(__FILE__)).' command '.base64_encode($_POST['commande']).'" > /tmp/firedoor_pipe_in')));
?>