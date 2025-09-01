import pyspark
from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession

from freeds.config import get_config


def get_spark_session(app_name: str, use_local: bool = False) -> SparkSession:
    """Get spark client for s3."""

    s3_cfg = get_config("s3")

    conf = (
        pyspark.conf.SparkConf()
        .setAppName(app_name)
        # s3 secrets
        .set("spark.hadoop.fs.s3a.access.key", s3_cfg["access_key"])
        .set("spark.hadoop.fs.s3a.secret.key", s3_cfg["secret_key"])
        .set("spark.task.maxFailures", "1")
    )
    if use_local:
        conf = conf.setMaster("local[*]")

    builder = pyspark.sql.SparkSession.builder.config(conf=conf)
    spark_session = configure_spark_with_delta_pip(builder).getOrCreate()

    return spark_session


def show_cfg(spark_session: SparkSession) -> None:
    """Print the entire spark config."""
    cfg = spark_session.sparkContext.getConf().getAll()
    for key, value in cfg:
        if key in (
            "spark.submit.pyFiles",
            "spark.driver.extraJavaOptions",
            "park.app.initial.jar.urls",
            "spark.files",
            "spark.repl.local.jars",
            "spark.app.initial.file.urls" "spark.executor.extraJavaOption",
            "spark.app.initial.jar.urls" "spark.app.initial.file.urls",
        ):
            print(key)
            for csv in value.split(","):
                print("    " + str(csv))
        else:
            print(f"{key} = {value}")


def show_spark_info(sc: SparkSession) -> None:
    """Print some spark info."""
    cfg: pyspark.SparkConf = sc.sparkContext.getConf()
    print(f'==== spark app: {cfg.get("spark.app.name")} ====')
    print(f'Spark master: {cfg.get("spark.master")}')
    print(f'Delta lake location: {cfg.get("spark.sql.warehouse.dir")}')
    print(f'S3 endpoint: {cfg.get("spark.hadoop.fs.s3a.endpoint")}')


def show_dbs(sc: SparkSession) -> None:
    """Print all databases and tables."""
    dbs = sc.catalog.listDatabases()
    print("Databases and tables:")
    for db in dbs:
        print(db.name)
        tables = sc.catalog.listTables(db.name)
        for tbl in tables:
            print(f"    {tbl.name}")
