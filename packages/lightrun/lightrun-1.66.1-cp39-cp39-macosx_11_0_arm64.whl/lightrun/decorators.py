import json
import os
import time

try:
    import lightrun
except ImportError as e:
    print("Error importing Lightrun: ", e)


def lightrun_serverless(company_key=None, lightrun_tags=None, **decorator_kwargs):
    """
    A decorator used to wrap serverless functions which we want to make sure that we activate and deactivate lightrun
    on each function call

    For example -

    @lightrun_serverless(company_key, lightrun_tags, ...)
    def foo():
        # Do something
        pass

    """
    if lightrun_tags is None:
        lightrun_tags = []

    def inner_function(func):
        def wrapper(*args, **kwargs):
            try:
                if os.getenv("LIGHTRUN_KEY"):
                    key = os.getenv("LIGHTRUN_KEY")
                else:
                    key = company_key

                if os.getenv("LIGHTRUN_TAGS"):
                    tags = list(set(lightrun_tags) | set(os.getenv("LIGHTRUN_TAGS").split(",")))
                else:
                    tags = lightrun_tags
                tags = [{"name": tag} for tag in tags]

                lightrun.enable(company_key=key, metadata_registration_tags=json.dumps(tags), is_serverless=True, **decorator_kwargs)

                result = func(*args, **kwargs)

                lightrun.disable()

                return result
            except Exception as e:
                raise RuntimeError("Failed to run serverless function with lightrun. Exception: %s" % e)

        return wrapper

    return inner_function


def lightrun_airflow_task(company_key=None, config_path=None, initial_sleep_ms=3000, com_lightrun_server=None):
    """
    A decorator used to wrap functions which are used as PythonOperator for airflow tasks.

    For example -

    @lightrun_airflow_task(secret="1111-2222-3333")
    def foo():
        # Do something
        pass

    ...

    foo_task = PythonOperator(task_id='foo', python_callable=foo)

    :param company_key: The secret api key of the company. Must be supplied either via this parameter or
                        indirectly via the 'LIGHTRUN_KEY' environmental variable.
    :param config_path: The filesystem path of a configuration for the lightrun agent. Optional.
                        It can be also supplied indirectly via the 'LIGHTRUN_AGENT_CONFIG' environmental variable.
    :param initial_sleep_ms: The amount of time, in milliseconds, to sleep after initializing the agent.
                             In case it is set to a low value, the agent might not have enough time to initialize
                              before the actual task starts execution, which will mean it won't be able to hit
                              breakpoints inserted to lines which will be executed before it finishes initialization.
    :param com_lightrun_server: Custom Lightrun server url. Optional.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            display_name = "_".join(filter(None, [os.getenv("AIRFLOW_CTX_TASK_ID"), os.getenv("AIRFLOW_CTX_DAG_RUN_ID")])) or None
            tags_string = (
                '[{"name": "airflow"}' + ((', {"name": "' + os.getenv("AIRFLOW_CTX_TASK_ID") + '"}') if os.getenv("AIRFLOW_CTX_TASK_ID") else "") + "]"
            )
            lightrun.enable(
                company_key=company_key or os.getenv("LIGHTRUN_KEY"),
                agent_config=config_path or os.getenv("LIGHTRUN_AGENT_CONFIG"),
                metadata_registration_tags=tags_string,
                metadata_registration_displayName=display_name,
                com_lightrun_server=com_lightrun_server,
            )

            # Sleep for a short while to let the agent initialize and query the backend
            time.sleep(initial_sleep_ms / 1000.0)
            parameter_names = func.__code__.co_varnames
            new_args = [a for a in args if a in parameter_names]
            new_kwargs = {k: v for k, v in kwargs.items() if k in parameter_names}
            result = func(*new_args, **new_kwargs)
            return result

        with lightrun.GoogleCloudDebuggerInitializer(lightrun.MAIN_PROCESS_NAME) as debugger:
            # the agent must be initialized only once
            return func if debugger.is_enabled() else wrapper

    return decorator
