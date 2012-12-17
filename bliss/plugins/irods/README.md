NOTES ON THE IRODS PLUGIN:

This was all tested on gw68 using the OSG iRODS access.  Get in touch with Tanya if you would like access.

imv does NOT work.  As per Tanya,
>Hi Ashley,
>move is not implemented yet. The only commands that should be working are listed in tutorial.
Said tutorial can be found at: https://twiki.grid.iu.edu/bin/view/VirtualOrganizations/IRODSOSG#Brief_Tutorial

I implemented it anyways, but it is COMPLETELY UNTESTED.

The server part of the URL is completely ignored.  As it is now, the plugin will just use the 
icommands found locally.

TODO ITEMS:
We don't check for flags such as overwrite/etc right now.
Various TODO items sprinkled throughout the code

GENERAL NOTES ON SAGA REPLICA/ETC: 
Some oddness with regards to naming of logical file functions, is the package implemented 100% correctly?

Parsing parameters from the query part of the URL ie ?resource= is kind of funky,
should this be standardized across SAGA?