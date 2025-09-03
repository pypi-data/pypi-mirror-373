import json
import asyncio
import argparse
import logging
import threading
import sys
from gar import GARClient


async def main(main_args):
    """Sample GAR client to demonstrate subscribe and publish"""
    log_level = getattr(logging, main_args.log_level.upper())
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d – %(message)s",
    )

    endpoint = main_args.url

    gar_client = GARClient(
        endpoint,
        working_namespace=main_args.ns,
        allow_self_signed_certificate=main_args.allow_self_signed_certificate,
    )

    if main_args.user:
        gar_client.user = main_args.user

    if main_args.application:
        gar_client.application = main_args.application

    client_thread = threading.Thread(target=gar_client.start)
    client_thread.daemon = True

    def on_heartbeat_timeout():
        logging.warning("Heartbeat timeout detected. Exiting application.")

    gar_client.register_heartbeat_timeout_handler(on_heartbeat_timeout)

    def on_gar_stopped():
        logging.info("GAR client stopped, exiting application.")

    gar_client.register_stopped_handler(on_gar_stopped)

    # pylint: disable=unused-argument
    def on_gar_error(error_message):
        logging.info("Exiting on error.")

    gar_client.register_error_handler(on_gar_error)

    heartbeat_received = threading.Event()

    def on_heartbeat(ms):
        logging.info("First heartbeat received %dms", ms)
        heartbeat_received.set()
        gar_client.clear_heartbeat_handler()

    gar_client.register_heartbeat_handler(on_heartbeat)

    gar_client.register_record_update_handler(
        lambda key_id, topic_id, value: logging.info(
            "Record update: %s - %s = %s",
            gar_client.server_key_id_to_name.get(key_id),
            gar_client.server_topic_id_to_name.get(topic_id),
            value,
        )
        # , subscription_group=1
    )

    client_thread.start()

    logging.info("Waiting for first heartbeat...")

    if not heartbeat_received.wait(timeout=29):  # seconds
        logging.error("Timed out waiting for first heartbeat")
        sys.exit(1)

    logging.info("Heartbeat received, starting stream.")

    try:
        if main_args.publish:
            key, topic, json_value = main_args.publish
            try:
                parsed_value = json.loads(json_value)  # Renamed from 'value'
                gar_client.publish_record(key, topic, parsed_value)
                # await asyncio.sleep(1) #TO DO - flush writes cleanly
                gar_client.logoff()
            except json.JSONDecodeError as json_exc:  # Renamed from 'e'
                logging.error("Invalid JSON value %s: %s", json_value, json_exc)
                gar_client.logoff()
        elif main_args.send_shutdown:
            gar_client.publish_shutdown()
            gar_client.logoff()
        else:
            subscription_mode = "Streaming" if main_args.streaming else "Snapshot"

            # Validate mutually exclusive parameters
            if main_args.key_name and (
                main_args.key_filter or main_args.exclude_key_filter
            ):
                logging.error(
                    "--key-name cannot be used with --key-filter or --exclude-key-filter"
                )
                sys.exit(1)

            if main_args.topic_name and (
                main_args.topic_filter or main_args.exclude_topic_filter
            ):
                logging.error(
                    "--topic-name cannot be used with --topic-filter or --exclude-topic-filter"
                )
                sys.exit(1)

            # Validate limit parameter usage
            if main_args.limit > 0 and subscription_mode == "Streaming":
                logging.error("--limit cannot be used with streaming subscriptions")
                sys.exit(1)

            gar_client.subscribe(
                "S1",
                subscription_mode=subscription_mode,
                key_name=main_args.key_name,
                topic_name=main_args.topic_name,
                class_name=main_args.__dict__["class"],
                key_filter=main_args.key_filter,
                topic_filter=main_args.topic_filter,
                exclude_key_filter=main_args.exclude_key_filter,
                exclude_topic_filter=main_args.exclude_topic_filter,
                max_history=main_args.max_history,
                include_referenced_keys=main_args.include_referenced_keys,
                include_referencing_keys=main_args.include_referencing_keys,
                include_all_namespace=main_args.include_all_namespace,
                trim_default_values=main_args.trim_default_values,
                working_namespace=main_args.working_namespace,
                density=main_args.density,
                subscription_set=main_args.subscription_set,
                subscription_group=main_args.subscription_group,
                snapshot_size_limit=main_args.snapshot_size_limit,
                nagle_interval=main_args.nagle_interval,
                limit=main_args.limit,
            )

            if subscription_mode == "Snapshot":
                snapshot_received = threading.Event()

                def on_subscription_status(name, status):
                    logging.info(
                        "Snapshot status received for subscription: %s (%s)",
                        name,
                        status,
                    )
                    if status == "NeedsContinue":
                        try:
                            input(
                                "Snapshot size limit reached. Press Enter to continue..."
                            )
                            gar_client.send_subscribe_continue(name)
                            logging.info(
                                "Sent SubscribeContinue for subscription: %s", name
                            )
                        except KeyboardInterrupt:
                            logging.info(
                                "KeyboardInterrupt during input, unsubscribing"
                            )
                            gar_client.publish_unsubscribe(name)
                            snapshot_received.set()
                            gar_client.clear_subscription_status_handler()
                    elif status == "Finished":
                        snapshot_received.set()
                        gar_client.clear_subscription_status_handler()

                gar_client.register_subscription_status_handler(on_subscription_status)
                if not snapshot_received.wait(timeout=60):  # seconds
                    logging.error("Timed out waiting for snapshot")
                    gar_client.exit_code = 1

                gar_client.logoff()
    except KeyboardInterrupt:
        logging.info("Received KeyboardInterrupt, shutting down")
    except Exception as e:
        logging.error("Error in main loop: %s", e)

    client_thread.join()

    logging.info("Exiting with code %d", gar_client.exit_code)
    sys.exit(gar_client.exit_code)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GAR Protocol Client")
    parser.add_argument(
        "--url",
        type=str,
        default="ws://127.0.0.1:6502",
        help="GAR WebSocket URL (default: ws://127.0.0.1:6502)",
    )
    parser.add_argument(
        "--ns",
        type=str,
        default=None,
        help="Working namespace (default: the server's working namespace)",
    )
    parser.add_argument(
        "--allow-self-signed-certificate",
        action="store_true",
        help="Allow self-signed certificates (default: False)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--streaming",
        action="store_true",
        help="Stay running and stream updates. Otherwise exit after snapshot received.",
    )
    parser.add_argument(
        "--key-filter", type=str, default=None, help="Key filter regex pattern"
    )
    parser.add_argument("--class", type=str, default=None, help="Class name")
    parser.add_argument(
        "--key-name",
        type=str,
        default=None,
        help="Key name(s) to filter by (space-separated for multiple, cannot use with --key-filter)",
    )
    parser.add_argument(
        "--topic-name",
        type=str,
        default=None,
        help="Topic name(s) to filter by (space-separated for multiple, cannot use with --topic-filter)",
    )
    parser.add_argument(
        "--topic-filter", type=str, default=None, help="Topic filter regex pattern"
    )
    parser.add_argument(
        "--send-shutdown", action="store_true", help="Shut down the server"
    )
    parser.add_argument(
        "--publish",
        nargs=3,
        metavar=("key", "topic", "value"),
        help="Publish a record with key, topic, and JSON value (e.g., --publish mykey mytopic '{\"data\": 123}')",
    )
    parser.add_argument(
        "--snapshot-size-limit",
        type=int,
        default=0,
        help="Limit the size of snapshot responses (default: 0, no limit)",
    )
    parser.add_argument(
        "--subscription-set",
        type=str,
        default=None,
        help="Subscription set identifier",
    )
    parser.add_argument(
        "--max-history",
        type=str,
        default=None,
        help="Maximum history to include (history_type)",
    )
    parser.add_argument(
        "--nagle-interval",
        type=int,
        default=0,
        help="Nagle interval in milliseconds (default: 0)",
    )
    parser.add_argument(
        "--subscription-group",
        type=int,
        default=0,
        help="Subscription group ID for isolating callbacks (default: 0)",
    )
    parser.add_argument(
        "--density",
        type=str,
        default=None,
        help="Performance tuning density setting",
    )
    parser.add_argument(
        "--include-referenced-keys",
        action="store_true",
        help="Add keys from any key references in matched records",
    )
    parser.add_argument(
        "--include-referencing-keys",
        action="store_true",
        help="Add keys that have one or more records referencing any matched keys",
    )
    parser.add_argument(
        "--include-all-namespace",
        action="store_true",
        help="Include keys and topics from all namespaces",
    )
    parser.add_argument(
        "--trim-default-values",
        action="store_true",
        help="Trim records containing default values from the snapshot",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit the number of records in initial snapshot (0 = all, default: 0)",
    )
    parser.add_argument(
        "--exclude-key-filter",
        type=str,
        default=None,
        help="Exclude keys matching regex pattern (cannot use with --key-name)",
    )
    parser.add_argument(
        "--exclude-topic-filter",
        type=str,
        default=None,
        help="Exclude topics matching regex pattern (cannot use with --topic-name)",
    )
    parser.add_argument(
        "--working-namespace",
        type=str,
        default=None,
        help="Namespace for matching relative paths using topic filters",
    )
    parser.add_argument(
        "--user",
        type=str,
        default=None,
        help="Username (default: OS environment username)",
    )
    parser.add_argument(
        "--application",
        type=str,
        default=None,
        help="Application name (default: trsgar.py)",
    )

    args = parser.parse_args()
    asyncio.run(main(args))
