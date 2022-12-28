# NAD Amplier remote control for Home Assistant

This repository contains a Home Assistant integration NAD Amplifiers. Much of this is a fork of the core integration and this work may be merged back into core in the future depending upon how it develops. Goals for this custom integration are:

* auto-discovery of telnet-capable NAD amplifiers (**DONE**)
* zone 2 selection
* switches for DSP programs
* volume controls for all speakers

**THE INTEGRATION SHOULD BE CONSIDERED NON-FUNCTIONAL UNTIL FURTHER NOTICE. PLEASE DO NOT RAISE ISSUES.**

##  Installation

Right now, the integration must be installed as a custom repository from HACS. Follow the instructions for adding custom repositories [in the HACS documentation](https://hacs.xyz/docs/faq/custom_repositories/) then download the repository to your Home Assistant instance and add the integration to your instance. The repository to use is:

<https://github.com/masaccio/ha-nad2>
