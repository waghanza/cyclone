#!/bin/bash

twistd -n cyclone -r $modname.web.Application -c $modname.conf
