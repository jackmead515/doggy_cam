import os
import logging

# kafka parameters
kafka_brokers = None
kafka_max_block_ms = 1000
kafka_retries = 5
http_port = 5000
kafka_topic = 'core.events'
kafka_group_id = 'recorder'
kafka_client_id = 'recorder'
kafka_max_poll_records = 5
kafka_max_poll_interval_ms = 300000

event_count_threshold = 10


def required_env(key):
    """
    Gets the provided key from os and if the value
    is None, raises an Exception
    """
    value = os.getenv(key)
    if value is None:
        raise Exception(f'{key} is a required env variable')
    return value



def initialize():
    global kafka_brokers, kafka_max_block_ms, kafka_retries, http_port, kafka_topic
    global kafka_group_id, kafka_client_id, kafka_max_poll_records, kafka_max_poll_interval_ms
    global event_count_threshold

    # setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    kafka_brokers = required_env('KAFKA_BROKERS')
    kafka_brokers = [k.strip() for k in kafka_brokers.split(',')]
    
    kafka_max_block_ms = int(os.getenv('KAFKA_MAX_BLOCK_MS', kafka_max_block_ms))
    kafka_retries = int(os.getenv('KAFKA_RETRIES', kafka_retries))
    http_port = int(os.getenv('HTTP_PORT', http_port))
    kafka_topic = os.getenv('KAFKA_TOPIC', kafka_topic)
    kafka_group_id = os.getenv('KAFKA_GROUP_ID', kafka_group_id)
    kafka_client_id = os.getenv('KAFKA_CLIENT_ID', kafka_client_id)
    kafka_max_poll_records = int(os.getenv('KAFKA_MAX_POLL_RECORDS', kafka_max_poll_records))
    kafka_max_poll_interval_ms = int(os.getenv('KAFKA_MAX_POLL_INTERVAL_MS', kafka_max_poll_interval_ms))
    event_count_threshold = int(os.getenv('EVENT_COUNT_THRESHOLD', event_count_threshold))