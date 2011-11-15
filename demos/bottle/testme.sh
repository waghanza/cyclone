#!/bin/bash

curl localhost:8080
echo
curl localhost:8080/sqlite
echo
curl localhost:8080/redis
echo
curl -d "foo=bar" localhost:8080/redis
echo
curl localhost:8080/redis
echo
