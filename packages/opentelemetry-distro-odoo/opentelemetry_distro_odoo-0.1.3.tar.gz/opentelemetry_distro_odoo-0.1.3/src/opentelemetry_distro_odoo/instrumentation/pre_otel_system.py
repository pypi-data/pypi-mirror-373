import copy

try:
    from opentelemetry.instrumentation.system_metrics import _DEFAULT_CONFIG, SystemMetricsInstrumentor
except ImportError:
    SystemMetricsInstrumentor = None


def pre_instrument_system():
    if SystemMetricsInstrumentor is None:
        return

    conf = copy.deepcopy(_DEFAULT_CONFIG)

    def _add(*values, key):
        conf[key] = list(set(conf[key]) | set(values))

    _add("iowait", key="system.cpu.time")
    _add("total", "available", key="system.memory.usage")
    _add("total", "available", key="system.swap.usage")

    _add("iowait", key="process.cpu.time")

    conf["system.cpu.utilization"] = conf["system.cpu.time"]
    conf["system.memory.utilization"] = conf["system.memory.usage"]
    conf["system.swap.utilization"] = conf["system.swap.usage"]
    conf["process.cpu.utilization"] = conf["process.cpu.time"]
    conf["process.runtime.cpu.time"] = conf["process.cpu.time"]
    SystemMetricsInstrumentor(config=conf)
