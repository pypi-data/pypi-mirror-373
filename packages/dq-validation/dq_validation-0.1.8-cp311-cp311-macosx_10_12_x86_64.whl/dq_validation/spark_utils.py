import tempfile
from typing import Optional, Tuple, Any
from contextlib import contextmanager
import multiprocessing
import math
import os
import psutil
from .logger import logger

import pyarrow.parquet as pq
from pyspark.sql import SparkSession


_DEFAULT_HEAP_SIZE_EXTRA_ROOM_PER_CORE = 268435456


def _get_cgroup_memory() -> int:
    max_memory_str = None
    if os.path.isfile("/sys/fs/cgroup/memory.max"):
        with open("/sys/fs/cgroup/memory.max", "r") as f:
            max_memory_str = f.read().strip()
    elif os.path.isfile("/sys/fs/cgroup/memory/memory.limit_in_bytes"):
        with open("/sys/fs/cgroup/memory/memory.limit_in_bytes", "r") as f:
            max_memory_str = f.read().strip()

    max_memory = None
    if max_memory_str == "max":
        # Fallback to available virtual memory size
        max_memory = psutil.virtual_memory().available
    elif max_memory_str is not None:
        try:
            max_memory = int(max_memory_str)
        except ValueError:
            pass

    if max_memory is not None:
        return max_memory
    else:
        logger.info("Unable to determine available memory from cgroup, assuming 5G")
        return 5 * 1024 * 1024 * 1024


# There are a couple of dimensions to look at when it comes to memory management:
# 1. CGroup available memory. This is the docker memory limit with already-used memory accounted for. If RSS
#    reaches this limit, the kernel OOM killer is triggered on the container.
# 2. Spark JVM heap. This corresponds to the -Xmx JVM argument and determines the size of the the GC-d heap.
# 3. RSS usage. This is the *actual* resident memory used by the running process. When it comes to operating
#    at capacity, we need to configure the settings such that RSS doesn't hit the CGroup limit.
# 4. spark.memory.fraction. This is the fraction of the JVM heap that's meant to be "used" by Spark. This is
#    not actually the case, in reality it is a number informing a limit on certain allocations, in particular
#    RDDs kept in memory.
#
# The 2 main sources of OOMs are large garbage churn and the CGroup limit hit. These OOMs manifest differently,
# and sometimes they trigger pathological behaviour (like extreme CPU usage), for example when RSS is very close
# to hitting the limit, but doesn't quite hit it.
#
# To address large garbage churn we set spark.memory.fraction to 0.4, down from the default 0.6. When computing at
# capacity, the rate of garbage churn seems to get higher than the rate of garbage collection. By setting the ratio
# lower we make GC cycles free more memory at once, which increases the GC rate to an extent that the OOM conditions
# stop happening.
#
# To address RSS vs CGroup limit we set the JVM heap to account for the empirically higher real RSS. Based on tests it
# seems that with fixed parallelism difference between RSS and the JVM heap size is close to a constant 1.0-1.5G.
# However this also seems to be environment dependent.
# Although from tests we don't see the extra RSS overhead affected by the size of inputs or amount of JVM heap, we still
# scale unused memory linearly with the cgroup memory as well, to account for other considerations like kernel memory usage.
#
# The final allocated JVM heap is thus set based on spark_memory = 0.95 * (cgroup_memory - 2.0G)
def _determine_optimal_spark_settings(parallelism: int) -> list[Tuple[str, str]]:
    # The SPARK_MEMORY env variable may be used to precisely set the spark memory.
    if "SPARK_MEMORY" in os.environ:
        spark_memory = int(os.environ["SPARK_MEMORY"])
    else:
        cgroup_memory = _get_cgroup_memory()
        spark_memory = int(0.95 * (cgroup_memory - 2 * 1024 * 1024 * 1024))

    # Align memory
    spark_memory_4096 = (spark_memory // 4096) * 4096
    if spark_memory_4096 < 2 * 1024 * 1024 * 1024:
        raise Exception(f"Not enough memory for the JVM (requested {spark_memory_4096}, but minimum is 2G)")

    settings = [
        ("spark.sql.files.maxPartitionBytes", 64 * 1024 * 1024),
        ("spark.driver.cores", str(parallelism)),
        ("spark.driver.memory", str(spark_memory_4096)),
        ("spark.memory.fraction", "0.4"),
        # See https://spark.apache.org/docs/latest/sql-performance-tuning.html#coalescing-post-shuffle-partitions
        ("spark.sql.adaptive.coalescePartitions.parallelismFirst", "false"),
    ]

    return settings


def _create_spark_session(
    parallelism: int,
    name: str = "local_spark_session",
    config: list[Tuple[str, Any]] = [],
    java_temp_dir: str = "/scratch",
    java_user_home_dir: str = "/scratch",
) -> SparkSession:
    """
    :param name: The name of the spark session.
    :param parallelism: The size of the executor pool computing internal spark tasks.
    :param config: Additional config settings to set on the spark config.
    :param java_temp_dir: Location for the JVM to store temp files.
    :param java_user_home_dir: Location for the user home directory as seen by the JVM.
    :return: The spark session.
    """
    os.environ["SPARK_EXECUTOR_POOL_SIZE"] = str(parallelism)
    os.environ["JDK_JAVA_OPTIONS"] = f'-Duser.home="{java_user_home_dir}" -Djava.io.tmpdir="{java_temp_dir}"'

    ss = (
        SparkSession.builder
        .appName(name)
        .master(f"local[{parallelism}]")
    )
    for (key, value) in config:
        ss = ss.config(key, value)

    logger.info("Spark settings:\n" + f"\n".join([str(x) for x in config]))

    return ss.getOrCreate()


@contextmanager
def spark_session(
        temp_dir: str = "/scratch",
        name: str = "Spark",
        config: list[Tuple[str, str]] = [],
        parallelism: int = 8,
):
    """
    Create a spark session and configure it according to the enclave environment.

    **Parameters**:
    - `temp_dir`: Where to store temporary data such as persisted data frames
      or shuffle data.
    - `name`: An optional name for this spark session.
    - `config`: Extra settings to pass to the Spark session builder.

    **Example**:

    ```python
    import decentriq_util as dq

    # Path to a potentially very large file
    input_csv_path = "/input/my_file.csv"

    # Automatically create and configure a spark session and
    # make sure it's being stopped at the end.
    with dq.spark.spark_session() as ss:
        # Read from a CSV file
        df = ss.read.csv(input_csv_path, header=False).cache()

        # Perform any pyspark transformations
        print(f"Original number of rows: {df.count()}")
        result_df = df.limit(100)

        # Write the result to an output file
        result_df.write.parquet("/output/my_file.parquet")
    ```
    """
    with tempfile.TemporaryDirectory(dir=temp_dir, prefix="java-") as java_tmp:
        with tempfile.TemporaryDirectory(dir=temp_dir, prefix="spark-") as spark_tmp:
            config_dict = dict(config)
            optimal_settings = _determine_optimal_spark_settings(
                parallelism=parallelism,
            )
            for key, value in optimal_settings:
                if key not in config_dict:
                    config.append((key, value))
            if "spark.local.dir" not in config_dict:
                config.append(
                    ("spark.local.dir", spark_tmp)
                )
            ss = _create_spark_session(parallelism=parallelism, name=name, java_temp_dir=java_tmp, java_user_home_dir=java_tmp, config=config)
            try:
                yield ss
            finally:
                try:
                    ss.stop()
                except:
                    pass
