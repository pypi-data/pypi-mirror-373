## netbox-static-routes

Display static routes in Netbox

### Install the Plugin

To install the Plugin just download it from the pip library:
```
pip install netbox-static-routes-communities
```

### Migrate the database

```
./manage.py migrate
```

### Include Plugin in Netbox

Now you have to include the Plugin to Netbox. Add following to your configuration file:
```
PLUGINS = ['netbox_static_routes_communities']
```

And restart the services:
```
sudo systemctl restart netbox netbox-rq
```