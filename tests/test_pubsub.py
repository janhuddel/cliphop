from cliphop.pubsub import Broadcaster


def test_publish_reaches_subscriber():
    broadcaster = Broadcaster()
    queue = broadcaster.subscribe()
    broadcaster.publish("<div>neu</div>")
    assert queue.get_nowait() == "<div>neu</div>"


def test_unsubscribe_stops_delivery():
    broadcaster = Broadcaster()
    queue = broadcaster.subscribe()
    broadcaster.unsubscribe(queue)
    assert broadcaster.subscriber_count == 0
    broadcaster.publish("x")
    assert queue.empty()
