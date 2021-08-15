* Use `gdown` to download the [dataset](https://drive.google.com/uc?id=1T0txOBPRN_PhaYTpQBkUvuIXKVgpKqnE)
* Decompress it to the current directory
* Run `python3 generator.py`
	* Options
		* `-a`,	The IP address of the MQTT broker. 
		* `-p`, Port number of the MQTT broker
		* `-n`, Number of days(rooms)
		* `-s`, Fast-forward. The default is 1(Normal speed), but the intervals between events is surprising long(More than 1000 seconds)
		* `-h`, Send via HTTP instead of MQTT. If `INGRESS_HOST` and `INGRESS_PORT` are set, those values will be used instead of the address and the port for the broker
