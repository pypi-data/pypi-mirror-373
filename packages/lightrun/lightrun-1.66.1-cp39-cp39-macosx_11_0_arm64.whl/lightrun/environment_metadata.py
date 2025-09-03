import os
import platform
import socket
import sys

import psutil

from .lightrun_native import native

LINUX = "linux"
WINDOWS = "windows"
MACOS = "mac"


class CachedEnvironmentMetadataProperty(object):
    """The property stores a name value. It's also cached, i.e. it's calculated only once"""

    def __init__(self, name):
        if not name:
            raise ValueError("name must be defined")
        self.name = name
        self.value = None

    def __call__(self, fget):
        self._fget = fget
        return self

    def __get__(self, inst, owner):
        try:
            self.value = inst._cache[self.name]
        except (KeyError, AttributeError):
            try:
                self.value = self._fget(inst)
            except Exception as e:
                native.LogWarning('Failed to get the environment property "%s": %s' % (self.name, e))
                self.value = None
            try:
                cache = inst._cache
            except AttributeError:
                cache = inst._cache = {}
            cache[self.name] = self.value
        return self.value


class EnvironmentMetadata:
    """The class represents different parameters of the agent environment"""

    def __init__(self):
        self._cached_os_release = None

    @CachedEnvironmentMetadataProperty(name="runtimeEnvironment")
    def runtime_environment(self):
        return "Python"

    @CachedEnvironmentMetadataProperty(name="pid")
    def pid(self):
        return os.getpid()

    @CachedEnvironmentMetadataProperty(name="procArch")
    def proc_arch(self):
        # platform.machine() values vary greatly between platforms
        arch = platform.machine().lower()
        if arch in ["x86_64", "amd64", "x64"]:
            return "x64"
        if arch in ["i386", "i686", "x86", "x86_32"]:
            return "x32"
        if arch in ["arm", "aarch", "arm32", "aarch32"]:
            return "arm"
        if arch.startswith("arm") or arch.startswith("aarch"):
            # 32-bit arm is handled above, so it can only be arm64
            return "arm64"
        return arch

    @CachedEnvironmentMetadataProperty(name="cpuCoreCount")
    def cpu_core_count(self):
        return psutil.cpu_count()

    @CachedEnvironmentMetadataProperty(name="systemTotalMemoryBytes")
    def system_total_memory_bytes(self):
        return psutil.virtual_memory().total

    @CachedEnvironmentMetadataProperty(name="host")
    def host(self):
        return socket.gethostname()

    @CachedEnvironmentMetadataProperty(name="agentOS")
    def os_name(self):
        os_name = sys.platform.lower()
        if os_name.startswith("linux"):
            return LINUX
        if os_name.startswith("win"):
            return WINDOWS
        if os_name == "darwin":
            return MACOS
        return os_name

    @CachedEnvironmentMetadataProperty(name="osVersion")
    def os_version(self):
        if self.os_name == LINUX:
            return self._os_release.get("VERSION_ID", "") or platform.release()
        return platform.release()

    @CachedEnvironmentMetadataProperty(name="linuxDistroName")
    def linux_distro_name(self):
        if self.os_name == LINUX:
            return self._os_release.get("ID", "")
        return ""

    @CachedEnvironmentMetadataProperty(name="runtimeEnvironmentVersion")
    def runtime_environment_version(self):
        info = sys.version_info
        return "%d.%d.%d" % (info.major, info.minor, info.micro)

    @CachedEnvironmentMetadataProperty(name="runtimeEnvironmentInfo")
    def runtime_environment_info(self):
        info = "Python %s, %s" % (sys.version, platform.platform())
        return info.replace("\r", "").replace("\n", "")[:250]

    @CachedEnvironmentMetadataProperty(name="isInDocker")
    def is_in_docker(self):
        if self.os_name == LINUX:
            return os.path.exists("/.dockerenv")
        else:
            # TODO: check whether this is a Windows base OS in Docker
            return False

    @CachedEnvironmentMetadataProperty(name="isInK8s")
    def is_in_k8s(self):
        return os.getenv("KUBERNETES_SERVICE_HOST") is not None

    @property
    def _os_release(self):
        if self._cached_os_release is None:
            self._cached_os_release = {}
            if self.os_name == LINUX:
                try:
                    with open("/etc/os-release", "r") as f:
                        for line in f:
                            k, v = line.rstrip().split("=")
                            self._cached_os_release[k] = v.strip('"')
                except Exception as e:
                    native.LogWarning("Failed to open and parse /etc/os-release: %s" % e)
        return self._cached_os_release

    def get_props(self):
        """Collect all non-empty CachedEnvironmentMetadataProperty fields into the dictionary"""

        props = {
            v.name: v.__get__(self, EnvironmentMetadata)  # enforce calling a getter to init the property
            for k, v in EnvironmentMetadata.__dict__.items()
            if not k.startswith("_") and isinstance(v, CachedEnvironmentMetadataProperty)
        }
        non_empty_props = {k: v for k, v in props.items() if v is not None and v != ""}
        return non_empty_props
