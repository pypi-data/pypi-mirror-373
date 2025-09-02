# HESTIA Schema

Data uploaded to [HESTIA](http://hestia.earth/) are stored in
[JSON-LD](https://json-ld.org/) files which each represent unique elements of food
production systems e.g. farms or fields. This repository contains the specification of
the JSON-LD based data exchange format. It was broadly based on the [openLCA schema](https://github.com/GreenDelta/olca-schema).

The schema is defined in [YAML](http://yaml.org/), with a file for each element in
the [yaml folder](./yaml). HTML documentation is generated via the `scripts/yaml_to_html.py` script. The script uses [PyYAML](https://pypi.org/project/PyYAML/) which needs to be
installed before running it (e.g. via `pip install PyYAML`).

## License

This project is in the worldwide public domain, released under the [CC0 1.0 Universal Public Domain Dedication](https://creativecommons.org/publicdomain/zero/1.0/).

![Public Domain Dedication](https://licensebuttons.net/p/zero/1.0/88x31.png)
