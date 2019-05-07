# Firedoor
Webserver firewall manager / monitoring / database administration / Web shell


Why use the best practices when you can use the worsts ?

The challenge of this project is to use PHP, Shell script, JS, HTML and CSS to make a fonctionnal and usefull webserver manager in only one file.


<span style="color:red">New version in Python under development</span> : [here](https://github.com/H4ckd4ddy/Firedoor/tree/dev)


## Build
##### Export code in one file :

```
./build.sh
```

## Install

##### Install all dependencies :

* net-tools
* at
* openssl
* iptables
* apache2
* php5

##### Place ```build/firedoor.php```in your webserver directory

##### Install firedoor service with :

```
./firedoor.php install
```

Default password : **firedoor**
