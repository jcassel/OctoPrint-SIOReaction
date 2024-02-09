/*
 * View model for OctoPrint-SIOReaction
 *
 * Author: John Cassel
 * License: MIT
 */
$(function() {
    function SioreactionViewModel(parameters) {
        var self = this;
        
        // assign the injected parameters, e.g.:
        self.loginStateViewModel = parameters[0];
        self.settingsViewModel = parameters[1];
        self.accessViewModel = parameters[2];
        self.controlViewModel = parameters[3];
        self.settings = undefined;
        self.vmsioreactions = ko.observableArray();
        self.vmsioconfiguration = ko.observableArray();
        
        // TODO: Implement your plugin's view model here.
        self.onBeforeBinding = function () {
            self.settings = self.settingsViewModel.settings;
            self.vmsioreactions(self.settingsViewModel.settings.plugins.SIOReaction.sioreactions.slice(0));
            self.vmsioconfiguration(self.settings.plugins.siocontrol.sio_configurations.slice(0));
            //self.vmsioconfiguration(self.settingsViewModel.settings.plugins.SIOReaction.sioconfiguration.slice(0));
        };

        self.onSettingsBeforeSave = function () {
            self.settingsViewModel.settings.plugins.SIOReaction.sioreactions(self.vmsioreactions.slice(0));
        };
        
        self.onSettingsShown = function () {
            self.vmsioreactions(self.settingsViewModel.settings.plugins.SIOReaction.sioreactions.slice(0));
            self.vmsioconfiguration(self.settings.plugins.siocontrol.sio_configurations.slice(0));
        };
        
        self.onSettingsHidden = function () {
            self.vmsioreactions(self.settingsViewModel.settings.plugins.SIOReaction.sioreactions.slice(0));
            self.vmsioconfiguration(self.settings.plugins.siocontrol.sio_configurations.slice(0));
        };

        self.addReaction = function () {
            self.vmsioreactions.push({Name:"",Pin:"",RType:"",Commands:""});
        };

        self.removeReaction = function (reaction) {
            self.vmsioreactions.remove(reaction);
        };

        self.getConfiguredIO = function(){
            self.vmsioconfiguration(self.settingsViewModel.settings.plugins.siocontrol.sio_configurations.slice(0));
            return self.vmsioconfiguration;
        }

    }


    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: SioreactionViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: ["loginStateViewModel","settingsViewModel","accessViewModel", "controlViewModel"],
        // Elements to bind to, e.g. #settings_plugin_SIOReaction, #tab_plugin_SIOReaction, ...
        elements: ["#settings_plugin_SIOReaction"]
    });
});
