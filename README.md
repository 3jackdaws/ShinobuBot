#ShinobuBot
Shinobu is a Discord bot written in Python.  It uses the wonderful discord.py framework and is inspired by NadekoBot, another Discord bot written in C#.

#Features
Shinobu is built to be extensible and modular.  Features are added by creating new modules and placing them in the ```modules``` directory.  From here, Shinobu can load these modules at runtime.  Modules can be autoloaded by placing the name of the modules in the ```shinobu_config.json``` file.

#Installation
##Docker
`docker pull 3jackdaws/shinobu`

Mount a volume at /etc/shinobu if you want to change config or add modules.

#Linux
View the Dockerfile to see what commands to run.  Any RUN directive needs to be done on the host system.
