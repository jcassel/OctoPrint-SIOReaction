# OctoPrint-SIOReaction
Sub PlugIn to OctoPrint-SIOControl. Create reactions to changes in IO, GCode, and more.


#### The Companion plugIn for the SIO Control 

A simple but powerful addition to the SIO Control PlugIn. With this Sub PlugIn you can make full use of inputs and outputs available though SIO Control PlugIn + hardware. 

Reactions are what happen when an IO point changes. What should happen is up to you. 

Do things like:
- Use a physical button to tell your machine to home or start to heat up for the print you will be sending soon. 
- Push a physical button and have a connected relay turn on, off or toggle state.  
- Push a physical button and send GCode to the OctoPrint GCode queue.  
- Have a relay turn on when specific GCode is seen. 
- If a limit switch is hit, send some GCode to the GCode queue. 

## Install

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/jcassel/OctoPrint-SIOReaction/archive/main.zip

You must have the [SIO Control PlugIn](https://plugins.octoprint.org/plugins/siocontrol/) installed for this to work.

## Configuration / Setup

Setting up a Reaction is simple. Follow these steps.

- Add a new Reaction row to the settings dialog. Push the Blue [+] button.
- Name your Reaction. 
- Select the configured SIO point to react to (ignored for GCode Command Reaction types).
- Select the type of Reaction __React To__ 
    - __NONE__ Effectivly disables the Reaction 
    - __In Change__ React when this IO Input point changes state
    - __In Active__ React when this IO Input point changes from Not Active to Active
    - __In Not Active__ React when this IO Input point Changes from Active to Not Active
    - __Out Change__ React when this IO Output point changes state
    - __Out Active__ React when this IO Output point changes from Not Active to Active
    - __Out Not Active__ React when this IO Output point changes from Active to Not Active
    - __GCode Command__ React when a specific GCode command is detected.

Note that when creating a reaction the format must follow a few rules. 
- All key words are case sensitive.
  - on, off, toggle, IO, GC, WT are all key words used when creating a reaction.
  - When identifying an IO Point, it must be 2 characters in length. Example: IO point 1 is "01"

## UI Samples
![Settings](/assets/img/SettingsExample.png)

![Help](/assets/img/HelpScrn.png)
