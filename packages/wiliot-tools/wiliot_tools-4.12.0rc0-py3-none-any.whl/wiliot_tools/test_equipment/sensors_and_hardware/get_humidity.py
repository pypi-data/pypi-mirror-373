import time

from wiliot_core import set_logger
from wiliot_tools.test_equipment.test_equipment import YoctoSensor

TIME_BTWN_MEASURE = 1  # seconds
path, logger = set_logger(app_name='GetHumidity', dir_name='humidity_sensor', file_name='get_humidity')

sensor = YoctoSensor(logger)

while True:
    humidity = sensor.get_humidity()
    logger.info(humidity)
    time.sleep(TIME_BTWN_MEASURE)