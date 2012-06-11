#!/bin/bash

export PYTHONPATH=`dirname $0`
twistd -n cyclone -r $modname.web.Application -c $modname.conf
