import testinfra.utils.ansible_runner
import pytest
import os

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
        os.environ["MOLECULE_INVENTORY_FILE"]).get_hosts("all")


@pytest.mark.parametrize("dirs", [
    "/opt/consul/",
    "/opt/consul/config.d/",
    "/var/lib/consul/"
])
def test_directories_creation(host, dirs):
    d = host.file(dirs)
    assert d.is_directory
    assert d.exists


@pytest.mark.parametrize("files", [
    "/opt/consul/consul.json",
    "/opt/consul/service.d/example.json",
    "/opt/consul/config.d/log_level.json"
])
def test_file_creation(host, files):
    f = host.file(files)
    assert f.exists
    assert f.is_file


@pytest.mark.parametrize("files", [
    "/opt/consul/service.d/dummy.json",
    "/opt/consul/config.d/dummy.json",
    "/opt/consul/script.d/dummy.sh"
])
def test_file_sync(host, files):
    f = host.file(files)
    assert not f.exists


def test_user(host):
    assert host.group("consul").exists
    assert host.user("consul").exists


@pytest.mark.parametrize("service", [
    "consul"
])
def test_service_is_running(host, service):
    service = host.service(service)

    assert service.is_running
    assert service.is_enabled


@pytest.mark.parametrize("domain", [
    "consul",
    "example",
    "google.com"
])
def test_dns_resolution(host, domain):
    domain = host.addr(domain)

    assert domain.is_resolvable


@pytest.mark.parametrize("port", [
    "8500",
    "8600"
])
def test_socket(host, port):
    s = host.socket("tcp://127.0.0.1:{}".format(port))
    assert s.is_listening
