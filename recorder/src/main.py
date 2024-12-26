import time
import logging
import json

import pandas as pd
from kafka import KafkaConsumer, TopicPartition

import config


def consume_and_compile():
    consumer = KafkaConsumer(
        max_poll_records=config.kafka_max_poll_records,
        max_poll_interval_ms=config.kafka_max_poll_interval_ms,
        auto_offset_reset='earliest',
        bootstrap_servers=config.kafka_brokers,
        group_id=config.kafka_group_id,
        client_id=config.kafka_client_id,
    )

    partition = TopicPartition(config.kafka_topic, 0)
    
    consumer.assign([partition])
    
    start = consumer.position(partition)
    end = consumer.end_offsets([partition])[partition]
    total = end - start
    
    events = []

    for i in range(0, total, 100):
        new_events = consumer.poll(timeout_ms=5000, max_records=100, update_offsets=True)[partition]

        if not new_events:
            break
        
        events.extend(new_events)
    
    df = []

    for event in events:
        data = json.loads(event.value)

        df.append({
            'offset': event.offset,
            'type': data['context']['type'],
            'timestamp': data['context']['timestamp'],
            'package': data['data']
        })

    df = pd.DataFrame(df)

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.floor('H')

    # remove the last hour of rows. This hour may not be complete
    df = df[df['hour'] < df['hour'].max()]

    max_offset = df['offset'].max()
    
    # commit to the max offset and close the consumer
    consumer.commit({partition: max_offset})
    consumer.close()
    
    return df


def aggregate_into_events(df):
    # aggregate per 1 minute and count the number of events
    counts_df = df.resample('1T', on='timestamp').count().drop(columns=['type'])

    # remove any that have no events
    counts_df = counts_df[counts_df['package'] > 0]

    # total up the number of events if the timestamps are back to back (i.e. no gaps)
    record_events = []
    record_event = None
    previous_row = None

    counts_df = counts_df.reset_index()
    counts_df = counts_df.sort_values('timestamp')

    for _, row in counts_df.iterrows():
        if previous_row is not None:
            if (row.timestamp - previous_row.timestamp).total_seconds() == 60:
                if record_event is None:
                    record_event = {
                        'start': previous_row.timestamp,
                        'end': row.timestamp,
                        'count': previous_row.package + row.package
                    }
                else:
                    record_event['end'] = row.timestamp
                    record_event['count'] += row.package
                
            elif record_event is not None:
                record_events.append(record_event)
                record_event = None
        
        previous_row = row

    record_df = pd.DataFrame(record_events)

    # filter if the count is less than the threshold
    record_df = record_df[record_df['count'] > config.event_count_threshold]
    
    # each row now represents an event that needs to be compiled into a video
    return record_df


if __name__ == "__main__":
    '''
    core logic:
    
    consume events from kafka until the end of the stream.
    
    compile the events into a dataframe, and look at the volume of objects detected and tracked, and motion detected.
    
    Determine the intervals of time during events that should be considered as a single event.
    
    Call the server to download the video clips ranging from the start to end of each event.
    
    Compile the video clips into a single video file for each event.
    
    Store the video files in a directory.
    
    Delete the video clips from the server.
    '''
    
    config.initialize()

    events_df = consume_and_compile()

    record_df = aggregate_into_events(events_df)
    
    for row in record_df.itertuples():
        start, end = row['start'], row['end']

        # get the video clips from the server!