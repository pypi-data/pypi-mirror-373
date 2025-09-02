{ lib, pkgs, ... }:
{
  services.filebeat = {
    enable = true;
    package = pkgs.filebeat7-oss;
    # ensure there is a `modules` subdirectory in the package, to check
    # whether an error message is actually an issue
    settings.setup.ilm.rollover_alias = "{{ component.filebeat_app }}-{{ component.filebeat_stage }}";
    settings.cloud.id = "{{ component.filebeat_cloud_id }}";
    settings.cloud.auth = "{{ component.filebeat_cloud_auth }}";
    settings.output.elasticsearch = {
      hosts = [ "{{component.filebeat_host}}" ];
    };
{% for data in component.data %}
    inputs.{{data.name}} = {
      type = "filestream";
      id = "{{data.name}}";
      enabled = true;
      paths = [ "{{data.path}}" ];
      {% if data.multiline %}
      multiline = {
        pattern = "{{data.multiline}}";
        negate = true;
        match = "after";
      };
      {% endif %}
      {% if data.exclude_lines %}
      exclude_lines = "{{data.exclude_lines}}";
      {% endif %}
      fields = {
        log_type = "{{data.type}}";
        environment = "{{ component.filebeat_stage }}";
        app = "{{ component.filebeat_app }}";
      };
      {% if data.processors %}
      processors = "{{data.processors}}";
      {% endif %}
    };
{% endfor %}
  };
}
