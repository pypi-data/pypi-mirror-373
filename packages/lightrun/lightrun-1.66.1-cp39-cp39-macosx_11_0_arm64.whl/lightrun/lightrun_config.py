import json
import os
import sys

config = None

BASE_PATH = os.path.dirname(os.path.realpath(__file__))

LIMITS = (
    (("max_snapshot_buffer_size_in_bytes", "max_snapshot_buffer_size"), lambda: GetMaxSnapshotBufferSize(), 65536, 2097152),
    (("max_variable_size_in_bytes", "max_variable_size"), lambda: GetMaxVariableSize(), 32, 2048),
    (
        ("max_watch_expression_size_in_bytes", "max_watchlist_variable_size"),
        lambda: GetMaxWatchExpressionSize(),
        256,
        lambda: int(GetMaxSnapshotBufferSize() * 0.7),
    ),
    (("max_collection_size",), lambda: GetMaxCollectionSize(), 1, 2048),
    (("max_watchlist_collection_size",), lambda: GetMaxWatchlistCollectionSize(), 100, lambda: int(GetMaxSnapshotBufferSize() * 0.7)),
    (("max_frames_with_vars",), lambda: GetMaxFramesWithVars(), 1, 10),
    (("max_object_members",), lambda: GetMaxObjectMembers(), 1, 2048),
)

DEFAULT_CONFIG = {
    # Lightrun Config
    "com.lightrun.secret": None,
    "company_key": None,
    "com.lightrun.server": None,
    "server_url": "https://app.lightrun.com",
    "breakpoint_expiration_sec": "3600",
    "transmission_bulk_max_size": "10",
    "ignore_quota": False,
    "metadata_registration_tags": '[{"name": "Production"}]',
    "collect_log_cooldown_ms": "60000",
    "agent_log_max_file_size_mb": "10",
    "alsologtostderr": False,
    "agent_log_target_dir": "",
    "pinned_certs": "515a630cfd1fb908e30087bcc20b7413ad146b9bf2b23d3aaa72c28e45b24fb2,ee80811b38e7e6c2dc4cc372cbea86bd86b446b012e427f2e19bf094afba5d12",
    "default_certificate_pinning_enabled": "true",
    "dynamic_log_is_colored_console": sys.platform != "win32",
    "dynamic_log_console_handler_format": "%(levelname)s: %(message)s",
    "dynamic_log_file_handler_file_pattern": "",
    "dynamic_log_file_handler_format": "%(levelname)s: %(message)s",
    "enable_pii_redaction": "false",
    "lightrun_wait_for_init": "false",
    "lightrun_init_wait_time_seconds": 2,
    "ignore_pyc_files": True,
    "base_dir": sys.path[0],
    "should_allow_forked_agents": True,
    "is_serverless": False,
    "agent_log_level": "info",
    "agent_log_max_file_count": 5,
    # Google Cloud Debugger Config
    "max_expression_lines": 10000,
    "max_condition_lines_rate": 5000,
    "max_dynamic_log_rate": 30,
    "max_dynamic_log_bytes_rate": 20480,
    "max_snapshot_buffer_size": 768000,
    "max_variable_size": 256,
    "max_watchlist_variable_size": 524288,
    "max_collection_size": 100,
    "max_watchlist_collection_size": 1024,
    "max_frames_with_vars": 4,
    "max_object_members": 100,
    "transmission_bulk_max_network_size_in_bytes": 2097152,
    "transmission_hard_max_network_size_limit_in_bytes": 20971520,
    "proxy_host": None,
    "proxy_port": None,
    "proxy_username": "",
    "proxy_password": "",
    # TODO(yaniv): Implement the usage for the following agent config keys
    # 'max_dynamic_log_rate': '60',
    # 'max_dynamic_log_bytes_rate': '204800',
    # 'max_condition_cost': '1',
    # 'max_log_cpu_cost': '1',
    # 'max_snapshot_buffer_size': '655360',
    # 'max_snapshot_frame_count': '5',
    # 'log_stats_time_micros': '30000000',
    # 'dynamic_log_quota_recovery_ms': '500',
    # 'utility_thread_frequency_ms': '1000',
    # 'exit_after_report_all': '0'
}


def InitializeConfig(config_file_path, cmdline_flags):
    global config

    config = DEFAULT_CONFIG.copy()
    if config_file_path is not None:
        if os.path.exists(config_file_path):
            # Specified configuration options in file override default configuration
            config.update(_ReadConfig(config_file_path))
        else:
            sys.stderr.write(f"Current pid: {os.getpid()} | The provided config file is not found: {config_file_path}\n")

    # Env values override configuration values
    config.update(_GetConfigFromEnvVariables())

    # Flag values override configuration values and env values
    config.update(cmdline_flags)

    ApplyLimits(config, LIMITS)

    # Assert mandatory configuration properties for agent exist
    if GetServerURL() is None:
        raise AssertionError("Lightrun server url must be supplied via 'com_lightrun_server' parameter")
    if GetCompanySecret() is None:
        raise AssertionError("Lightrun company secret must be supplied via 'company_key' parameter")


def GetValueFromConfigOrDefault(name, value_type):
    try:
        return value_type(config.get(name, DEFAULT_CONFIG[name]))
    except (AttributeError, ValueError, TypeError):
        return DEFAULT_CONFIG[name]


def GetTransmissionBulkMaxNetworkSizeInBytes():
    return GetValueFromConfigOrDefault("transmission_bulk_max_network_size_in_bytes", int)


def GetTransmissionHardMaxNetworkSizeLimitInBytes():
    return GetValueFromConfigOrDefault("transmission_hard_max_network_size_limit_in_bytes", int)


def GetMaxObjectMembers():
    return GetValueFromConfigOrDefault("max_object_members", int)


def GetMaxFramesWithVars():
    return GetValueFromConfigOrDefault("max_frames_with_vars", int)


def GetMaxCollectionSize():
    return GetValueFromConfigOrDefault("max_collection_size", int)


def GetMaxWatchlistCollectionSize():
    return GetValueFromConfigOrDefault("max_watchlist_collection_size", int)


def GetMaxSnapshotBufferSize():
    # max_snapshot_buffer_size_in_bytes is for backwards compatibility
    return int(config.get("max_snapshot_buffer_size_in_bytes") or config.get("max_snapshot_buffer_size") or DEFAULT_CONFIG["max_snapshot_buffer_size"])


def GetMaxVariableSize():
    # max_variable_size_in_bytes is for backwards compatibility
    return int(config.get("max_variable_size_in_bytes") or config.get("max_variable_size") or DEFAULT_CONFIG["max_variable_size"])


def GetMaxWatchExpressionSize():
    # max_watch_expression_size_in_bytes is for backwards compatibility
    return int(config.get("max_watch_expression_size_in_bytes") or config.get("max_watchlist_variable_size") or DEFAULT_CONFIG["max_watchlist_variable_size"])


def GetServerURL():
    return config.get("com_lightrun_server") or config.get("com.lightrun.server") or config.get("server_url")


def GetCompanySecret():
    return config.get("com_lightrun_secret") or config.get("com.lightrun.secret") or config.get("company_key")


def ShouldIgnorePyc():
    if not config:
        return DEFAULT_CONFIG["ignore_pyc_files"]
    return GetBooleanConfigValue("ignore_pyc_files")


def GetProxyHost():
    return config.get("proxy_host")


def GetProxyPort():
    return GetValueFromConfigOrDefault("proxy_port", int)


def GetProxyUsername():
    username = config.get("proxy_username")
    return username if username else None


def GetProxyPassword():
    password = config.get("proxy_password")
    return password if password else None


def _ReadConfig(config_file_path):
    file_config = {}
    with open(config_file_path, "r") as f:
        raw_config = f.read()
    config_lines = [line for line in raw_config.split("\n") if line.strip() != "" and not line.strip().startswith("#")]
    for line in config_lines:
        key, val = line.split("=")
        file_config[key] = val
    return file_config


def _GetConfigFromEnvVariables():
    env_config = {}
    if os.getenv("LIGHTRUN_TAGS"):
        registration_tags = [{"name": tag} for tag in os.getenv("LIGHTRUN_TAGS").split(",")]
        env_config["metadata_registration_tags"] = json.dumps(registration_tags)
    for name in ["agent_log_target_dir", "agent_log_max_file_size_mb", "agent_log_level", "agent_log_max_file_count"]:
        if os.getenv(name.upper()):
            env_config[name] = os.getenv(name.upper())

    # all other agents use LIGHTRUN_ prefix for defining proxy server configuration,
    # so the Python agent complies
    if os.getenv("LIGHTRUN_PROXY_HOST"):
        env_config["proxy_host"] = os.getenv("LIGHTRUN_PROXY_HOST")
    if os.getenv("LIGHTRUN_PROXY_PORT"):
        env_config["proxy_port"] = os.getenv("LIGHTRUN_PROXY_PORT")
    if os.getenv("LIGHTRUN_PROXY_USERNAME"):
        env_config["proxy_username"] = os.getenv("LIGHTRUN_PROXY_USERNAME")
    if os.getenv("LIGHTRUN_PROXY_PASSWORD"):
        env_config["proxy_password"] = os.getenv("LIGHTRUN_PROXY_PASSWORD")
    return env_config


def GetBooleanConfigValue(key):
    return config.get(key) in ["true", "True", "1", True]


def ApplyLimits(conf, limits):
    for aliases, getter, min_val, max_val_or_callable in limits:
        max_val = max_val_or_callable() if callable(max_val_or_callable) else max_val_or_callable
        val = getter()
        if not (min_val <= val <= max_val):
            new_val = max(min_val, min(val, max_val))
            for alias in aliases:
                conf[alias] = new_val
                sys.stderr.write(
                    f"Current pid: {os.getpid()} | Config parameter {alias} was updated to fit the limits {(min_val, max_val)}: {val} -> {new_val}\n"
                )
