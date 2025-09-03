from primus_lens_workload_exporter.gpu.gpu_metrics import get_rocm_smi_info
from primus_lens_workload_exporter.rdma.rdma import get_rdma_statistics
from primus_lens_workload_exporter.metric.collector import OTelMetric


def gpu_collector():
    info = get_rocm_smi_info()
    metrics = []
    for card, values in info.items():
        labels = {"gpu": card}
        if "Temperature (Sensor junction) (C)" in values:
            metrics.append(OTelMetric("gpu_temperature_celsius", "GPU junction temp",
                                      float(values["Temperature (Sensor junction) (C)"]), labels))
        if "Current Socket Graphics Package Power (W)" in values:
            metrics.append(OTelMetric("gpu_power_watts", "GPU package power",
                                      float(values["Current Socket Graphics Package Power (W)"]), labels))
        if "GPU use (%)" in values:
            metrics.append(OTelMetric("gpu_utilization", "GPU utilization",
                                      float(values["GPU use (%)"]), labels))
        if "GPU Memory Allocated (VRAM%)" in values:
            metrics.append(OTelMetric("gpu_memory_usage_percent", "GPU VRAM usage",
                                      float(values["GPU Memory Allocated (VRAM%)"]), labels))
    return metrics


def rdma_collector():
    stats = get_rdma_statistics()
    metrics = []
    for link, counters in stats.items():
        labels = {"rdma_link": link}
        for key, value in counters.items():
            # key 直接作为 metric 名字
            metrics.append(
                OTelMetric(
                    name=f"rdma_{key}",  # 建议加 rdma_ 前缀，避免和其他采集器冲突
                    description=f"RDMA counter {key}",
                    value=float(value),
                    labels=labels
                )
            )
    return metrics

