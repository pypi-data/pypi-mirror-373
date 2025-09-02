#!/bin/sh

# JAVA_HOME
# PATH

{% if component.admin_password %}
export KEYCLOAK_ADMIN=admin
export KEYCLOAK_ADMIN_PASSWORD={{component.admin_password}}
{% endif %}

exec {{component.basedir}}/bin/kc.sh start --proxy-headers xforwarded
