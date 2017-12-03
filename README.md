# yeelight_flux_control

Script that controls the color temperature and brightness Yeelight RGB Bulbs based on the color temperature set in f.lux

Requires Python 3
'LAN Mode' must be enableed for your bulbs using the Yeelight Andriod/iOS app

To run:
```
# You must set "http://localhost:42069" as the "Post to this URL when f.lux changes" setting in f.lux
# modify YEELIGHT_IPS yeelight_flux_control.py to include the ip address of the Yeelights
# e.g. YEELIGHT_IPS = ['192.168.1.42']
python yeelight_flux_control.py
```
