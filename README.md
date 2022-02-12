# Consul

Install, configure and maintain [Consul](https://www.consul.io) - a service mesh
from HashiCorp.

## Role Philosophy

Instead of duplicating every single configuration option as an Ansible variable Consul
configuration is stored in Ansible inventory in `yaml` format:

```yml
consul_config:
  data_dir: "/var/lib/consul/"

  enable_syslog: true
  # "trace", "debug", "info", "warn", "err"
  log_level: "info"
  syslog_facility: "LOCAL5"

  rejoin_after_leave: true

  bind_addr: !unsafe '{{ GetInterfaceIP "eth0" }}'

  telemetry:
    disable_compat_1.9: true
    disable_hostname: true
    prometheus_retention_time: "30s"

  server: false
```

And then copied to host using `no_nice_json` filter:

```yml
- name: copy consul config
  copy:
    content: "{{ consul_config | to_nice_json }}"
    dest: "/opt/consul/consul.json"
    validate: "consul validate -config-format=json %s"
```

When variable is a map (`consul_services` for example) every key of a map will
be copied as file with value as a content.

The following map

```yml
consul_services:
  consul:
    service:
      id: "consul-api"
      name: "consul-api"
      port: 8500
      tags:
        - "traefik.enable=true"
        - "traefik.http.routers.consul.entrypoints=https"
        - "traefik.http.routers.consul.rule=Host(`consul.example.com`)"
      meta:
        external-source: "consul"
      check:
        id: "consul-api-health"
        name: "consul-api-health"
        http: "http://localhost:8500/v1/agent/self"
        interval: "20s"
        timeout: "2s"

  telegraf:
    service:
      id: "telegraf-exporter"
      name: "telegraf-exporter"
      port: 9271
      meta:
        external-source: "consul"
      check:
        id: "telegraf-exporter-health"
        name: "telegraf-exporter-health"
        http: "http://localhost:9270"
        interval: "20s"
        timeout: "2s"
```

will produce files `consul.json` and `telegraf.json` in
`/opt/consul/service.d/`.

Files that are not present in the map will be deleted, thus allowing to maintain
a state with Ansible inventory.

## Role Variables

See [defaults/](https://github.com/nahsi/ansible-consul/blob/master/defaults/)
for details and examples.

#### `consul_version`

- version to use

#### `consul_dirs`

- a map of directories to create
- default:

```yml
consul_dir: "/opt/consul"
consul_dirs:
  main:
    path: "{{ consul_dir }}"
  configs:
    path: "{{ consul_dir }}/config.d"
  services:
    path: "{{ consul_dir }}/service.d"
  certs:
    path: "{{ consul_dir }}/certs"
    mode: "u=rwX,g=rX,o="
  scripts:
    path: "{{ consul_dir }}/script.d"
  logs:
    path: "/var/log/consul"
  data:
    path: "/var/lib/consul"
    mode: "u=rwX,g=rX,o="
```

#### `consul_config`

- main [configuration](https://www.consul.io/docs/agent/options) file
- example: please see
  [defaults/example.yml](https://github.com/nahsi/ansible-consul/blob/master/defaults/example.yml)

#### `consul_configs`

- map of configuration files to create in `config.d` directory. Restart on
  changes

#### `consul_services`

- map of [service](https://www.consul.io/docs/discovery/services) files to
  create in `service.d` directory. Reload on changes

#### `consul_scripts`

- map of scripts to create in `scripts.d` directory

#### `consul_user`

- owner of Consul process and files
- default: `consul`

#### `consul_group`

- group of `consul_user`
- default: `consul`

#### `consul_download_url`

- url to get Consul archive from
- default: `https://releases.hashicorp.com`

#### `consul_service`

- openrc service file
- default: see
  [defaults/main.yml](https://github.com/nahsi/ansible-consul/blob/master/defaults/main.yml)

#### `consul_unitfile`

- systemd unit file
- default: see
  [defaults/main.yml](https://github.com/nahsi/ansible-consul/blob/master/defaults/main.yml)

#### `skip_handlers`

- skipt consul restart/reload - useful when building images with packer
- default: `false`

## Tags

- `config` - update Consul unit/service file and sync configuration files
- `services` - sync Consul services
- `scripts` - sync Consul scripts

## Author

- **Anatoly Laskaris** - [nahsi](https://github.com/nahsi)
