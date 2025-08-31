#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ozi_build import schema


def render_doc(fields_desc: str, option: str, desc: dict[str, str]):
    fields_desc += "### `%s`" % option
    if desc.get("optional"):
        fields_desc += " (Optional)"
    fields_desc += "\n\n"
    fields_desc += desc['description']
    fields_desc += "\n\n"
    return fields_desc


def generate_doc():
    project_desc = ''
    for option, desc in schema.VALID_PROJECT.items():
        project_desc = render_doc(project_desc, option, desc)
    build_desc = ''
    for option, desc in schema.VALID_BUILD_OPTIONS.items():
        build_desc = render_doc(build_desc, option, desc)
    extra_fields_desc = ""
    for option, desc in schema.VALID_EXTRA_METADATA.items():
        if '{deprecated}' in desc['description']:
            continue
        extra_fields_desc = render_doc(extra_fields_desc, option, desc)
    pyc_wheel_desc = ''
    for option, desc in schema.VALID_PYC_WHEEL_OPTIONS.items():
        pyc_wheel_desc = render_doc(pyc_wheel_desc, option, desc)
    with open(sys.argv[1], 'r') as i:
        with open(sys.argv[2], 'w') as o:
            o.write(
                i.read().format(
                    extra_fields_desc=extra_fields_desc,
                    pyc_wheel_desc=pyc_wheel_desc,
                    project_desc=project_desc,
                    build_desc=build_desc,
                )
            )


if __name__ == "__main__":
    generate_doc()
