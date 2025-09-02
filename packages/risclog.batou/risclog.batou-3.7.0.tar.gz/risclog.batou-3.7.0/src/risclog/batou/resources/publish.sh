#!/usr/bin/env bash
DOCKER_DEFAULT_PLATFORM=linux/amd64 {{component.docker_path}}-compose -p {{component.container_name}} -f {{component.service_file.path}} build --no-cache
{{component.docker_path}} tag {{component.registry_path}}:{{component.version}} {{component.registry_url}}:{{component.registry_port}}/{{component.registry_path}}:{{component.service_version}}
{{component.docker_path}} push {{component.registry_url}}:{{component.registry_port}}/{{component.registry_path}}:{{component.version}}
