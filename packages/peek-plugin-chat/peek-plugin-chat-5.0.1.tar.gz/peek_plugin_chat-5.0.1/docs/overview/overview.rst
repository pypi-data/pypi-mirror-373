.. _overview:


========
Overview
========

Plugin Objective
----------------

The Peek Chat plugin provides simple chat functionality between users in the Peek
system and integrations in external systems.

Integrations with external systems are handled by other plugins, which can use
the API for this chat plugin.

Originally this plugin was designed to send messages between the power grid control
room and field engineers.

Plugin Uses
-----------

Simple communications with external systems.


How It Works
------------

Here is an overview of the architecture of the plugin.

.. image:: ChatPluginArchitectureDiagram.png


Administration
--------------

Requirements
````````````

This plugin requires the following peek plugins :

*   peek-plugin-active-task
*   peek-core-user

These dependencies are set in the python package.