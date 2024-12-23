# coding=utf-8
from __future__ import absolute_import


import octoprint.plugin
from octoprint.util import fqfn

# import flask
from . import SIOReaction, SIOReactionType


import threading

# *** old way (using Octoprint RepeatedTimer)***
# from octoprint.util import RepeatedTimer

# import time


class SioreactionPlugin(
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.SimpleApiPlugin,
):
    def __init__(self):
        self.has_SIOC = False
        self.available_plugins = dict()
        self.IOState = ""
        self.IOStatus = []
        self.Reactions = []
        self.GCReactions = []  # Special list for reactions that look at the GCode stream.
        self.RTReactions = []  # Special list for reactions that run on a repeted timer interval.
        self.SIOConfiguration = []
        self.siocontrol_helper = None

    def get_settings_defaults(self):
        return dict(
            sioreactions=[],
        )

    def reload_settings(self):
        for k, v in self.get_settings_defaults().items():
            if type(v) is str:
                v = self._settings.get([k])
            elif type(v) is int:
                v = self._settings.get_int([k])
            elif type(v) is float:
                v = self._settings.get_float([k])
            elif type(v) is bool:
                v = self._settings.get_boolean([k])

    def get_template_configs(self):
        return [dict(type="settings", custom_bindings=True, template="sioreaction_settings.jinja2",),]

    def get_template_vars(self):
        return {
            "SIOReactions": self._settings.get(["sioreactions"]),
        }

    def on_settings_initialized(self):
        self.updateReactions()
        return super().on_settings_initialized()

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.updateReactions()
        self.startRectionTimers()
        return super().on_settings_save(data)

    def updateReactions(self):
        # synctronize/replaces the server side list of reactions from any changes made by browser client.
        self.Reactions.clear()
        self.GCReactions.clear()
        for r in self.RTReactions:
            if r.RType == SIOReactionType.SIOReactionType.TIMER:
                # r.Timer.cancel()  #old way (using Octoprint RepeatedTimer)
                r.StopTimer()  # new way (using threading.Timer)
                self._logger.debug("Stopping Repeat Timer for Reaction <{}>".format(r.Name))

        self.RTReactions.clear()

        for r in self._settings.get(["sioreactions"]):
            reaction = SIOReaction.SIOReaction(self, r["Name"], int(r["Pin"]), r["RType"])
            commands = r["Commands"].splitlines()
            for cmd in commands:
                reaction.AddCommand(cmd)

            # Check if this reaction is a GCode reaction. If it is,add it to a special list.
            if reaction.RType == SIOReactionType.SIOReactionType.GCODE:
                self.GCReactions.append(reaction)

            # if reaction is Repeat timer reaction, add it to a special list.
            if reaction.RType == SIOReactionType.SIOReactionType.TIMER:
                self.RTReactions.append(reaction)

            self.Reactions.append(reaction)

        return

    def on_after_startup(self):
        try:
            self.siocontrol_helper = self._plugin_manager.get_helpers("siocontrol")
            if not self.siocontrol_helper:
                self._logger.warning("siocontrol Plugin not found.")
            elif "register_plugin" not in self.siocontrol_helper.keys():
                self._logger.warning("The version of siocontrol that is installed does not support plugin registration. Version 1.0.0 or higher is required.")
            else:
                self.siocontrol_helper["register_plugin"](self)
                self._logger.info("Regester as Sub Plugin to siocontrol")
                self.getIOState()
                self.startRectionTimers()

        except Exception as err:
            self._logger.exception("Exception: {}, {}".format(err, type(err)))

        return super().on_after_startup()

    def startRectionTimers(self):
        # start repeat timer for reactions RTReactions
        for r in self.RTReactions:
            if r.RType == SIOReactionType.SIOReactionType.TIMER:
                self._logger.debug("Starting Repeat Timer for Reaction <{}>".format(r.Name))
                # *** new way (using threading.Timer) ***
                r.timer = threading.Thread(target=r.StartTimer, daemon=True)
                r.timer.start()  # start the timer thread

                # *** old way (using Octoprint RepeatedTimer)***
                # r.Timer = RepeatedTimer(timedelay, r.React)
                # r.Timer.start()

    def getIOState(self):
        callback = self.siocontrol_helper["get_sio_digital_state"]
        try:
            self.IOState = callback()

        except Exception:
            self._logger.exception("Error while executing callback {}".format(callback), extra={"callback": fqfn(callback)},)

    def getPINStatus(self, pin):
        callback = self.siocontrol_helper["get_sio_digital_status"]
        try:
            self.IOStatus = callback()
            pinStatus = self.IOStatus[pin]
        except Exception:
            self._logger.exception("Error while executing callback {}".format(callback), extra={"callback": fqfn(callback)},)
            pinStatus = -1  # error status

        return pinStatus

    #  events
    # def hook_sio_serial_stream(self,line):
    #   self._logger.info("SIOReaction hook_sio_serial_Stream: {}".format(line))

    def sioStateChanged(self, newIOstate, newIOStatus):
        previousIOState = self.IOState
        # previousIOStatus = self.IOStatus
        self.IOState = newIOstate
        self.IOStatus = newIOStatus
        if previousIOState is not None:
            self._logger.debug("sioStateChanged: {}".format(newIOstate))
            for r in self.Reactions:
                if r.RType != SIOReactionType.SIOReactionType.GCODE:  # skip this type it does not react to IO changes.
                    curPinState = self.IOState[r.Pin]
                    prePinState = previousIOState[r.Pin]
                    if curPinState != prePinState:
                        if r.RType == SIOReactionType.SIOReactionType.INPUT_CHANGE or r.RType == SIOReactionType.SIOReactionType.OUTPUT_CHANGE:
                            self._logger.debug("Reacting to IO State(in or out) Change")
                            r.React()

                        if r.RType == SIOReactionType.SIOReactionType.INPUT_ACTIVE and self.IOStatus[r.Pin] == "on":
                            self._logger.debug("Reacting to IO Pin{} changed to Active".format(r.Pin))
                            r.React()

                        if r.RType == SIOReactionType.SIOReactionType.INPUT_NOT_ACTIVE and self.IOStatus[r.Pin] == "off":
                            self._logger.debug("Reacting to IO Pin{} changed to NOT_Active".format(r.Pin))
                            r.React()

                        if r.RType == SIOReactionType.SIOReactionType.OUTPUT_ACTIVE and self.IOStatus[r.Pin] == "on":
                            self._logger.debug("Reacting to IO Pin{} changed to Active".format(r.Pin))
                            r.React()

                        if r.RType == SIOReactionType.SIOReactionType.OUTPUT_NOT_ACTIVE and self.IOStatus[r.Pin] == "off":
                            self._logger.debug("Reacting to IO Pin{} changed to NOT_Active".format(r.Pin))
                            r.React()

    def hook_gcode_queuing(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
        skipQueuing = False
        if len(self.GCReactions) == 0:
            return

        if not gcode:
            gcode = cmd.split(' ', 1)[0]

        for r in self.GCReactions:
            if gcode == r.Commands[0]:
                self._logger.debug("Reacting to GCODE{}".format(r.Commands[0]))
                r.React()

        if skipQueuing:
            return (None,)

    # #~~ AssetPlugin mixin
    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": ["js/SIOReaction.js"],
            "css": ["css/SIOReaction.css"],
            "less": ["less/SIOReaction.less"]
        }

    # #~~ Softwareupdate hook
    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "SIOReaction": {
                "displayName": "SIO Reaction Sub Plugin",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "jcassel",
                "repo": "OctoPrint-SIOReaction",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/jcassel/OctoPrint-SIOReaction/archive/{target_version}.zip",
            }
        }


__plugin_name__ = "SIO Reaction"
__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = SioreactionPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.comm.protocol.gcode.queuing": __plugin_implementation__.hook_gcode_queuing,
    }
