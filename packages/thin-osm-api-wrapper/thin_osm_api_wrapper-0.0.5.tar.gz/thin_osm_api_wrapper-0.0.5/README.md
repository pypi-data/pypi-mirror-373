# Replaced
See [osm_easy_api](https://github.com/docentYT/osm_easy_api)

# Original readme

This is intended as a minimal wrapper over [OSM Editing API](https://wiki.openstreetmap.org/wiki/API), to make easy to understand what is going on.

It contains thin wrapper only for parts that I needed so far.

# Run tests

```
python3 -m unittest
```

# Usage examples

## Object history

```
import thin_osm_api_wrapper
import json

object_type = "way"
object_id = 10101010
data = thin_osm_api_wrapper.api.history_json(object_type, object_id)
print(json.dumps(data, indent=3))
```
## List changesets

```
import thin_osm_api_wrapper
import json

data = thin_osm_api_wrapper.api.changeset_list_json()
print(json.dumps(data, indent=3))
closed_after = "2021-12-26"
created_before = "2021-12-27"
data = thin_osm_api_wrapper.api.changeset_list_json(closed_after=closed_after, created_before=created_before)
print(json.dumps(data, indent=3))
```

# Related projects

See also [osm_bot_abstraction_layer](https://github.com/matkoniecz/osm_bot_abstraction_layer) and [osmapi](https://github.com/metaodi/osmapi) for other Python wrappers of OSM editing API.

Sister of [taginfo equivalent](https://github.com/matkoniecz/taginfo_api_wrapper_in_python).

# Contributing

PRs are welcome!

# pypi

See [https://pypi.org/project/thin-osm-api-wrapper/](https://pypi.org/project/thin-osm-api-wrapper/)

