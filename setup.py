# coding=utf-8
from setuptools import setup

########################################################################################################################
plugin_identifier = "SIOReaction"
plugin_package = "octoprint_SIOReaction"
plugin_name = "SIO Reaction"
plugin_version = "0.1.7"
plugin_description = "Sub Plugin for SIO Control (v1+). Create reactions to changes in IO, GCode, and more."
plugin_author = "jcassel"
plugin_author_email = "jcassel@softwaresedge.com"
plugin_url = "https://github.com/jcassel/OctoPrint-SIOReaction"
plugin_license = "AGPLv3"
#plugin_requires = []
plugin_requires = ["SIO-Control@https://github.com/jcassel/OctoPrint-Siocontrol/archive/main.zip"]
plugin_additional_data = []
plugin_additional_packages = []
plugin_ignored_packages = []
additional_setup_parameters = {"python_requires": ">=3,<4"}
########################################################################################################################

try:
    import octoprint_setuptools
except Exception:
    print(
        "Could not import OctoPrint's setuptools, are you sure you are running that under "
        "the same python installation that OctoPrint is installed under?"
    )
    import sys

    sys.exit(-1)

setup_parameters = octoprint_setuptools.create_plugin_setup_parameters(
    identifier=plugin_identifier,
    package=plugin_package,
    name=plugin_name,
    version=plugin_version,
    description=plugin_description,
    author=plugin_author,
    mail=plugin_author_email,
    url=plugin_url,
    license=plugin_license,
    requires=plugin_requires,
    additional_packages=plugin_additional_packages,
    ignored_packages=plugin_ignored_packages,
    additional_data=plugin_additional_data,
)

if len(additional_setup_parameters):
    from octoprint.util import dict_merge

    setup_parameters = dict_merge(setup_parameters, additional_setup_parameters)

setup(**setup_parameters)
