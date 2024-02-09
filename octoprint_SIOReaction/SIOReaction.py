# import sys
#import threading
#import time

#import octoprint.plugin
#from octoprint.settings import settings
from octoprint.util import fqfn

from . import SIOReactionType


class SIOReaction:
    def __init__(self, plugin,name,pin,rtype):
        self.Name = name
        self.Pin = pin
        self.RType = SIOReactionType.SIOReactionType[rtype]
        #self.RType = rtype  # SIOReactionType.SIOReactionType.INPUT_CHANGE
        self.Commands = []

        self._logger = plugin._logger
        self._printer = plugin._printer
        self._printer_profile_manager = plugin._printer_profile_manager
        self._plugin_manager = plugin._plugin_manager
        self._identifier = plugin._identifier
        self._settings = plugin._settings
        self.plugin = plugin

    def AddCommand(self,command):
        self.Commands.append(command)
        self._logger.debug("Added Command{} to Reaction{}".format(command,self.Name))

    def React(self):
        # do the thing or things in reaction Command
        # really would have wanted to do a match here but comparibily is not good enough yet.
        if self.RType == SIOReactionType.SIOReactionType.INPUT_ACTIVE:
            self._logger.debug("Executing Reaction to INPUT_ACTIVE {}".format(self.Pin))
        elif self.RType == SIOReactionType.SIOReactionType.INPUT_NOT_ACTIVE:
            self._logger.debug("Executing Reaction to INPUT_NOT_ACTIVE {}".format(self.Pin))
        elif self.RType == SIOReactionType.SIOReactionType.INPUT_CHANGE:
            self._logger.debug("Executing Reaction to INPUT_CHANGE {}".format(self.Pin))
        elif self.RType == SIOReactionType.SIOReactionType.OUTPUT_ACTIVE:
            self._logger.debug("Executing Reaction to OUTPUT_ACTIVE {}".format(self.Pin))
        elif self.RType == SIOReactionType.SIOReactionType.OUTPUT_NOT_ACTIVE:
            self._logger.debug("Executing Reaction to OUTPUT_NOT_ACTIVE {}".format(self.Pin))
        elif self.RType == SIOReactionType.SIOReactionType.OUTPUT_CHANGE:
            self._logger.debug("Executing Reaction to OUTPUT_CHANGE {}".format(self.Pin))
        else:
            self._logger.debug("Executing Reaction to something unexpected? {}".format(self.Pin))

        for command in self.Commands:
            if command[:2] == "IO":  # change an IO point (outputs)
                if "set_sio_digital_state" in self.plugin.siocontrol_helper.keys():
                    self._logger.debug("Executing Command \"{}\" for Reaction <{}>".format(command,self.Name))
                    callback = self.plugin.siocontrol_helper["set_sio_digital_state"]
                    try:
                        action = command[4:][2:]
                        pin = int(command[3:][:2])
                        if action == "toggle":
                            if int(self.plugin.IOState[pin]) == 1:
                                action = "off"
                            else:
                                action = "on"

                        self.plugin.IOState = callback(pin,action)

                    except Exception:
                        self._logger.exception("Error while executing callback {}".format(callback),extra={"callback": fqfn(callback)},)

                else:
                    self._logger.debug("Can't find the proper method in siocontrol_helper \"set_sio_digital_state\" for Reaction{},Command{}".format(self.Name,command))
                    self._logger.debug("Executing Command \"{}\" for Reaction <{}>".format(command,self.Name))

            elif command[:2] == "GC":   # inject some gcode into the flow
                self._logger.debug("Executing Command \"{}\" for Reaction <{}>".format(command,self.Name))
                self._printer.commands(command[3:])
            else:
                if self.RType != SIOReactionType.SIOReactionType.GCODE and command.index == 0:  # ignore the first command when a GCode reaction type
                    self._logger.debug("Invalid Command \"{}\" for Reaction <{}>".format(command,self.Name))
