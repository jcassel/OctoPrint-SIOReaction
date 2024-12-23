# import sys
# import threading
# import time

# import octoprint.plugin
# from octoprint.settings import settings
import threading
import time
from octoprint.util import fqfn

from . import SIOReactionType


class SIOReaction:
    def __init__(self, plugin, name, pin, rtype):
        self.Name = name
        self.Pin = pin
        self.RType = SIOReactionType.SIOReactionType[rtype]
        self.Commands = []
        self.Timer = None  # used to store the timer object if this is a timer reaction
        self.TimerThreadStop = False  # used to stop the timer thread
        self._logger = plugin._logger
        self._printer = plugin._printer
        self._printer_profile_manager = plugin._printer_profile_manager
        self._plugin_manager = plugin._plugin_manager
        self._identifier = plugin._identifier
        self._settings = plugin._settings
        self.plugin = plugin

    def AddCommand(self, command):
        self.Commands.append(command)
        self._logger.debug("Added Command{} to Reaction{}".format(command, self.Name))

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

        thread = threading.Thread(target=self.CommadExecution_thread, daemon=True)
        thread.start()

    def StartTimer(self):
        self.TimerThreadStop = False
        while True:
            self._logger.debug("Executing Timer Reaction for Reaction <{}>".format(self.Name))
            if (self.TimerThreadStop is True):
                self._logger.debug("Timer Reaction <{}> Stopped".format(self.Name))
                break  # stop the timer thread

            self.React()
            timedelay = int(self.Commands[0])  # the first command is the delay time
            time.sleep(timedelay)  # sleep for the delay time

    def StopTimer(self):
        self.TimerThreadStop = True
        if self.Timer and threading.current_thread() != self.TimerThreadStop:
            try:
                self.Timer.join()
            except Exception:
                pass

        self.Timer = None

    def CommadExecution_thread(self):
        self._logger.debug("Executing Commands for Reaction <{}>".format(self.Name))
        for command in self.Commands:
            if command[:2] == "IO":  # change an IO point (outputs)
                if "set_sio_digital_state" in self.plugin.siocontrol_helper.keys():
                    self._logger.debug("Executing Command \"{}\" for Reaction <{}>".format(command, self.Name))
                    callback = self.plugin.siocontrol_helper["set_sio_digital_state"]
                    try:
                        action = command[4:][2:]
                        pin = int(command[3:][:2])
                        if (self.plugin.IOState is not None):
                            if action == "toggle":
                                if int(self.plugin.IOState[pin]) == 1:
                                    action = "off"
                                else:
                                    action = "on"

                            self.plugin.IOState = callback(pin, action)

                    except Exception:
                        self._logger.exception("Error while executing callback {}".format(callback), extra={"callback": fqfn(callback)},)
                        pass
                else:
                    self._logger.debug("Can't find the proper method in siocontrol_helper \"set_sio_digital_state\" for Reaction{},Command{}"
                                       .format(self.Name, command))
                    self._logger.debug("Executing Command \"{}\" for Reaction <{}>".format(command, self.Name))

            elif command[:2] == "GC":   # inject some gcode into the flow
                self._logger.debug("Executing Command \"{}\" for Reaction <{}>".format(command, self.Name))
                self._printer.commands(command[3:])

            elif command[:2] == "WT":  # wait command
                self._logger.debug("Executing Command \"{}\" for Reaction <{}>".format(command, self.Name))
                sleep_time = command[3:]
                if not sleep_time.isnumeric() or isinstance(sleep_time, float) or (isinstance(sleep_time, int) and int(sleep_time) < 1):
                    self._logger.info("Invalid Wait Time \"{}\" for Reaction <{}>, value must be a whole number greater than 0".format(command, self.Name))
                else:
                    time.sleep(int(sleep_time))
                    
            elif command[:2] == "TD":  # DS18B20 temperature control
                self._logger.debug("Executing Command \"{}\" for Reaction <{}>".format(command, self.Name))
                # get extra parameters from the command line. "TD PIN:# OnAt:# OffAt:# OUTIO:#"
                pin = int(command.split(" ")[1].split(":")[1])
                onAt = int(command.split(" ")[2].split(":")[1].split(".")[0])  # remove any decimal points
                offAt = int(command.split(" ")[3].split(":")[1].split(".")[0])  # remove any decimal points
                outIO = int(command.split(" ")[4].split(":")[1])
                if "get_sio_ds18b20_data" in self.plugin.siocontrol_helper.keys():
                    callback = self.plugin.siocontrol_helper["get_sio_ds18b20_data"]
                    try:
                        ds18b20 = callback(pin)
                        if ds18b20 is not None:
                            temp = ds18b20["temp"]
                            if temp <= onAt:
                                self.plugin.IOState = self.plugin.siocontrol_helper["set_sio_digital_state"](outIO, "on")
                            elif temp >= offAt:
                                self.plugin.IOState = self.plugin.siocontrol_helper["set_sio_digital_state"](outIO, "off")
                    except Exception:
                        self._logger.exception("Error while executing callback {}".format(callback), extra={"callback": fqfn(callback)},)

            elif command[:2] == "TH":  # temperature control
                self._logger.debug("Executing Command \"{}\" for Reaction <{}>".format(command, self.Name))
                # get extra parameters from the command line. "TC PIN:# OnAt:# OffAt:# OUTIO:#"
                pin = int(command.split(" ")[1].split(":")[1])
                onAt = int(command.split(" ")[2].split(":")[1].split(".")[0])  # remove any decimal points
                offAt = int(command.split(" ")[3].split(":")[1].split(".")[0])  # remove any decimal points
                outIO = int(command.split(" ")[4].split(":")[1])
                if "get_sio_dht_data" in self.plugin.siocontrol_helper.keys():
                    callback = self.plugin.siocontrol_helper["get_sio_dht_data"]
                    try:
                        dht = callback(pin)
                        if dht is not None:
                            temp = dht["temp"]
                            if temp <= onAt:
                                self.plugin.IOState = self.plugin.siocontrol_helper["set_sio_digital_state"](outIO, "on")
                            elif temp >= offAt:
                                self.plugin.IOState = self.plugin.siocontrol_helper["set_sio_digital_state"](outIO, "off")
                    except Exception:
                        self._logger.exception("Error while executing callback {}".format(callback), extra={"callback": fqfn(callback)},)

            elif command[:2] == "MU":  # send a message to the user (future feature)
                # "MU {"msg":"a message", "type":"success", "title":"thetile", "persist":false, "timeout":0,"close":true, "sound":false}"
                # msg_types = ['notice','error','info','success']                
                self._logger.debug("Executing Command \"{}\" for Reaction <{}>".format(command, self.Name))
                # try:
                #    self.plugin._plugin_manager.send_plugin_message(self._identifier, dict(type ="popup", msg=command[3:]))
                # except Exception:
                #    self._logger.exception("Error while sending plugin message", extra={"callback": fqfn(self.plugin._plugin_manager.send_plugin_message)},)

            else:
                # ignore the first command when a GCode and TIMER reaction type or report an error for other reaction types
                if (self.RType != SIOReactionType.SIOReactionType.GCODE or self.RType != SIOReactionType.SIOReactionType.TIMER) and command.index == 0:
                    self._logger.info("Invalid Command \"{}\" for Reaction <{}>".format(command, self.Name))

