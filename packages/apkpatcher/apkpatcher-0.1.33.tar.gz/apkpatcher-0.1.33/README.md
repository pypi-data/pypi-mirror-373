# README


## GENERAL INFO


  Project: Library to patch apk (inject frida gadget)  
  Author: MadSquirrel  
  License: GNU General Public License v3.0  
  Version: v1.0  
  Date: 02-06-21  

## GOAL

Library to patch apk (inject frida gadget)
this code is inspired by this project :https://github.com/badadaf/apkpatcher.

The improvements added by this fork are the following:  
- modification of xml files such as AndroidManifest without extracting the resources. Extracting the resources usually prevents to rebuild the apk.
- Use as an API
- Installation as a package

## USAGE

  To use as library you just need to:

```python3
import apkpatcher
patcher = apkpatcher.Patcher(<apk_path>, <version>, <sdktools>)
patcher.patching(<path_gadget>, <arch>, output_file=<output_file>, user_certificate=<true|false>)
```

To use as a program you just need to:
```bash
apkpatcher -a <apk_path> -g <path_gadget> -s <sdktools> -b <version> -r <arch> -o <output_file>
```

You could use it as docker with this command line:

```bash
docker run --rm -v .:/pwd -it madsquirrels/apkpatcher -a base.apk --download_frida_version 16.3.3
```

For more information please visit https://apkpatcher.ci-yow.com/



## EXEMPLE

```python3
import apkpatcher
patcher = apkpatcher.Patcher(<apk_path>, <sdktools>, <version>)
# not mandatory
patcher.add_network_certificate(<custom_certificate>)
patcher.set_arch(<arch>)
patcher.pause = <True|False>
# end not mandatory
patcher.patching(<path_gadget>, <arch>, output_file=<output_file>, user_certificate=<true|false>)
```

## INSTALL

```python3
sudo python3 -m pip install .
```

### Requirement
  setup your sktools as follow:
  - https://asthook.ci-yow.com/how.install.html#setup-sdktools
  install:
  - apktool
  - pip install -r requirements.txt


## CHANGELOG

