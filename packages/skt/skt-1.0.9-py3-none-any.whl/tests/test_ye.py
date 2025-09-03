def test_get_spark():
    from pyspark import SparkConf

    from skt.ye import get_spark

    conf = SparkConf(loadDefaults=False)

    spark = get_spark(scale=5, conf=conf)
    assert "8g" == spark.conf.get("spark.driver.memory")
    assert "32" == spark.conf.get("spark.executor.instances")
    assert "32g" == spark.conf.get("spark.executor.memory")
    assert "8g" == spark.conf.get("spark.driver.maxResultSize")

    spark.stop()
