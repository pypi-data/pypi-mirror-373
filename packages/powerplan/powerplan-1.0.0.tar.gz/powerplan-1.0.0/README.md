# powerplan (v1.0.0) - UPDATE 2025
## Get windows power plan information

powerplan is a Python package to get information about your current windows power plan using subprocess module and to change your current power plan to a different one.
## Features

- Get GUID of your current windows power plan
- Get name of your current windows power plan
- Change power plan to Power saver, Balanced or high performance.

## Installation

powerplan requires [Python](https://www.python.org/) Version 3+ to run.

## Usage

```py
import powerplan
name = powerplan.get_current_scheme_name()
guid = powerplan.get_current_scheme_guid()
print(name, guid)
powerplan.change_current_scheme_to_powersaver()
powerplan.change_current_scheme_to_balanced()
powerplan.change_current_scheme_to_high()
```
## License

MIT

**Made by Temal in Germany**
[www.colinm.de](https://colinm.de/)
