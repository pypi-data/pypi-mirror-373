# The 3Di command line client

The 3Di command line client allows for 

 - Defining and running 3Di scenarios from the command line. 
 - Assembling different scenarios as a "suite" that will be run in batch.    
 - Management commands, for instance to list currently running simulations. 
 
## Entry points
 
There are different entry points for the 3Di command line client. The main one being

```shell script
$ 3Di_cmd --help

Usage: 3Di_cmd [OPTIONS] COMMAND [ARGS]...

Options:
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.

  --help                          Show this message and exit.

Commands:
  api        Interact with with the 3Di API
  live       Get real time updates of running simulations
  scenarios  Manage your local scenarios

```
The output above shows the three sub-commands `api`, `live` and `scenarios`. Those are all commands from 
the main client. Whenever you install plugins this list can be appended. You can even append this list yourself 
by writing your own plugin! How to go about doing that, explains the plugins section. 


You can invoke the sub-commands also directly, e.g. 

```shell script
$ api --help
Usage: api [OPTIONS] COMMAND [ARGS]...

Options:
  --endpoint [localhost|staging|production]
                                  [default: production]
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.

  --help                          Show this message and exit.

Commands:
  models         List available threedimodels
  organisations  List available organisations
  results        Download results of a simulation
  run-scenario   Run a scenario
  settings       Set default settings
  simulations    List simulations
 ```


## Dependencies

`python >= 3.10`


## Installation


```
pip install --user threedi-cmd
```

## Plugins

The 3Di command client has it's own plugin ecosystem. The commands described above are the client core that can 
be extended by installing 3Di command client packages into the same environment. 

An example: You have a virtual environment `/home/you/.virtualenvs/3di/bin/python` and you install the 3Di command client
using pip

```shell script
pip install threedi-cmd
```    


If you want to add the statistics commands, you'll install the threedi-cmd-statistics package 

```shell script
pip install threedi-cmd-statistics
```    

Now run `3Di_cmd api` again. Notice the `statistics` and `customers` commands that has been added to the commands 
overview; they have added through the plugin you just installed.

```shell script
Usage: 3Di_cmd api [OPTIONS] COMMAND [ARGS]...

  Interact with with the 3Di API

Options:
  --endpoint [localhost|staging|production]
                                  [default: production]
  --help                          Show this message and exit.

Commands:
  customers      List 3Di customers
  models         List available threedimodels
  organisations  List available organisations
  results        Download results of a simulation
  run-scenario   Run a scenario
  settings       Set default settings
  simulations    List simulations
  statistics     3Di API statistics, like session counts etc
```


### Available plugins

  - https://github.com/nens/threedi-cmd-statistics/


### Writing your own plugin 

The first thing to know is that the plugin discovering mechanism is [based on a naming convention](https://packaging.python.org/guides/creating-and-discovering-plugins/).
All plugin packages must start with **threedi_cmd_**, otherwise the main programme will not be able to discover the 
package and add the commands to the client.


The commands of the plugin package itself must be [typer](https://typer.tiangolo.com/) apps. 

The threedi-cmd packages ships with two objects that are used to define and register the plugin apps.  

```python
@dataclass
class AppMeta:
    app: typer.Typer
    name: str
    help: str
    add_to: Optional[str] = ""


@dataclass
class AppRegistry:
    apps: Dict[str, AppMeta]
  ```

So let's say you have an plugin package that is called `threedi-cmd-queue` that implements a single app called `queue_app`. 
You would need to the following for the threedi-cmd client to pick the command up.

#### AppMeta

```python
"""threedi_cmd_queue/app_definitions.py"""

# these classes are shiped with the threedi-cmd package
from threedi_cmd.plugins.models import AppMeta, AppRegistry
# import your won app
from threedi_cmd_queue.commands.apps import queue_app


queues_meta = AppMeta(
    app=queue_app,
    name="queues",
    help="3Di API queues",
    add_to="api"
)

# fill the registry; we use the name "queues" for the registry as well 
registry = AppRegistry(
    apps={queues_meta.name : queues_meta}
)

```

Lastly, make sure the registry is available through your **top level** `__init__.py`. Following our example the 
method would reside in  `threedi-cmd-queue/threedi_cmd_queue/__init__.py`
 
```python
"""Top-level package for threedi_cmd_queue."""

from threedi_cmd_queue.app_definitions import registry

````


That's it. Publish your package to [pypi](https://pypi.org/) so that is pip installable. 
