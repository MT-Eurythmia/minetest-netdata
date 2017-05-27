# Minetest Plugin for NetData

Displays the following informations:
* Number of players (note: this information will not be true until the server has no player while NetData is running)
* Number of chat messages per second
* Number of placed nodes per second
* Number of digged nodes per second
* Total number of actions per second

[Live example](http://netdata.langg.net/#menu_minetest_Mynetest_submenu_players)

## Installation

Edit `minetest.conf` so it corresponds to your system.

Then, run the following commands as root:
```
git clone https://github.com/Mynetest/minetest-netdata.git
cd minetest-netdata
cp minetest.chart.py /usr/libexec/netdata/python.d/
cp minetest.conf /etc/netdata/python.d/
```

And restart netdata (try `systemctl restart netdata` or `service netdata restart` or `killall netdata && netdata`).
