# Inara plugin for EDMC
A simple plugin that links your [Inara](http://inara.cz) account to [EDMC](https://github.com/Marginal/EDMarketConnector).

Once logged in, the plugin will:
* Update your credit balance (you should set your assets once manually)
* Update your Combat, Trade, Exploration, Empire, Federation & CQC Rank at startup. EDMC must be started before you start Open Play, Private group or Solo play in order to detect them.
* Add an achievement entry for various events, currently only destroying a Capital Ship and dying.
* Update your system location as you travel

The only limitations are the Journal entries and the commander data retrieved by the Companion API.

# Installation
Download the [latest release](https://gitlab.com/mrsheepsheep/EDMC-Inara/repository/archive.zip?ref=master), open the archive (zip) and extract the folder (yup, the weird folder name, feel free to rename) to your EDMC plugin folder.

* Windows: `%LOCALAPPDATA%\EDMarketConnector\plugins` (usually `C:\Users\you\AppData\Local\EDMarketConnector\plugins`).
* Mac: `~/Library/Application Support/EDMarketConnector/plugins` (in Finder hold ⌥ and choose Go &rarr; Library to open your `~/Library` folder).
* Linux: `$XDG_DATA_HOME/EDMarketConnector/plugins`, or `~/.local/share/EDMarketConnector/plugins` if `$XDG_DATA_HOME` is unset.

You will need to re-start EDMC for it to notice the plugin.

# Use with caution
Inara creditentials are saved in a raw format. They are NOT encrypted.

This plugin is not affiliated with Inara and therefore may break at any time.

# Personnal notes
[Companion data sample](http://www.jsoneditoronline.org/?id=c4be6a3d246713af75207a877c6c3f4e)

[Journal Manual](http://hosting.zaonce.net/community/journal/v11/Journal_Manual_v11.pdf)