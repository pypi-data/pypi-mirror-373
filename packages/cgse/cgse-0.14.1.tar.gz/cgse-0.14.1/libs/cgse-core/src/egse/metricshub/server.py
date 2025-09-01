# async_gateway.py
import asyncio
import time
from datetime import datetime

import zmq
import zmq.asyncio
from influxdb_client_3 import InfluxDBClient3
from influxdb_client_3 import Point


class AsyncMetricsHub:
    def __init__(
        self,
        influx_client,  # FIXME: should be a plugin
        zmq_endpoint="tcp://*:5555",  # FIXME: should also come from a plugin
        batch_size=500,
        flush_interval=2.0,
    ):
        self.influx_client = influx_client
        self.batch_size = batch_size
        self.flush_interval = flush_interval

        # AsyncIO ZeroMQ context
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.bind(zmq_endpoint)

        # Configure socket
        self.socket.setsockopt(zmq.RCVHWM, 10000)

        # AsyncIO queue for data points
        self.data_queue = asyncio.Queue(maxsize=10000)

        # Stats
        self.stats = {"received": 0, "written": 0, "errors": 0, "queue_size": 0}

        print(f"🚀 AsyncIO Gateway listening on {zmq_endpoint}")

    async def start(self):
        """Start the gateway with concurrent tasks"""
        try:
            # Run receiver and batch processor concurrently
            await asyncio.gather(
                self._receive_data(), self._batch_processor(), self._stats_reporter(), return_exceptions=True
            )
        except Exception as e:
            print(f"❌ Gateway error: {e}")
        finally:
            await self._cleanup()

    async def _receive_data(self):
        """Receive data from ZeroMQ and add to queue"""
        print("📡 Starting data receiver...")

        while True:
            try:
                # Receive message (non-blocking with timeout)
                message = await self.socket.recv_json()

                # Process message
                point = await self._process_message(message)
                if point:
                    # Add to queue (non-blocking)
                    try:
                        await asyncio.wait_for(self.data_queue.put(point), timeout=0.1)
                        self.stats["received"] += 1
                    except asyncio.TimeoutError:
                        # Queue full, drop point
                        self.stats["errors"] += 1
                        print("⚠️ Queue full, dropping point")

            except Exception as e:
                print(f"❌ Error receiving data: {e}")
                self.stats["errors"] += 1
                await asyncio.sleep(0.1)

    async def _process_message(self, message):
        """Process incoming message asynchronously"""
        try:
            # Validate message
            if "device_id" not in message or "data" not in message:
                return None

            # Create InfluxDB point
            point = Point("sensor_data")
            point.tag("device_id", message["device_id"])

            # Add timestamp
            if "timestamp" in message:
                point.time(message["timestamp"])

            # Add sensor data
            sensor_data = message["data"]
            for key, value in sensor_data.items():
                if isinstance(value, (int, float)):
                    point.field(key, value)
                else:
                    point.tag(key, str(value))

            return point

        except Exception as e:
            print(f"❌ Error processing message: {e}")
            return None

    async def _batch_processor(self):
        """Batch processor using asyncio"""
        print("📦 Starting batch processor...")

        batch = []
        last_flush = time.time()

        while True:
            try:
                # Try to get data points for batch
                timeout = max(0.1, self.flush_interval - (time.time() - last_flush))

                try:
                    # Get point with timeout
                    point = await asyncio.wait_for(self.data_queue.get(), timeout=timeout)
                    batch.append(point)

                except asyncio.TimeoutError:
                    # No data received, check if we should flush anyway
                    pass

                # Update queue size stat
                self.stats["queue_size"] = self.data_queue.qsize()

                # Check flush conditions
                should_flush = len(batch) >= self.batch_size or (
                    batch and time.time() - last_flush >= self.flush_interval
                )

                if should_flush and batch:
                    await self._flush_batch(batch)
                    batch.clear()
                    last_flush = time.time()

            except Exception as e:
                print(f"❌ Batch processor error: {e}")
                await asyncio.sleep(1)

    async def _flush_batch(self, batch):
        """Flush batch to InfluxDB asynchronously"""
        if not batch:
            return

        try:
            start_time = time.time()

            # Run InfluxDB write in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.influx_client.write, batch)

            write_time = time.time() - start_time
            self.stats["written"] += len(batch)

            points_per_second = len(batch) / write_time if write_time > 0 else 0
            print(f"✅ Wrote {len(batch)} points ({points_per_second:.0f} pts/s)")

        except Exception as e:
            print(f"❌ Failed to write batch: {e}")
            self.stats["errors"] += len(batch)

    async def _stats_reporter(self):
        """Periodic stats reporting"""
        while True:
            await asyncio.sleep(10)  # Report every 10 seconds
            print(
                f"📊 Stats: Received={self.stats['received']}, "
                f"Written={self.stats['written']}, "
                f"Queue={self.stats['queue_size']}, "
                f"Errors={self.stats['errors']}"
            )

    async def _cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up...")

        # Flush remaining data
        remaining_batch = []
        while not self.data_queue.empty():
            try:
                point = await asyncio.wait_for(self.data_queue.get(), timeout=0.1)
                remaining_batch.append(point)
            except asyncio.TimeoutError:
                break

        if remaining_batch:
            await self._flush_batch(remaining_batch)

        self.socket.close()
        self.context.term()
        print("✅ Cleanup complete")


# Device process (also async)
class AsyncDeviceDataSender:
    def __init__(self, gateway_endpoint="tcp://localhost:5555", device_id="device_001"):
        self.device_id = device_id
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.connect(gateway_endpoint)
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.setsockopt(zmq.SNDHWM, 1000)

    async def send_data_point(self, sensor_data):
        """Send data point asynchronously"""
        message = {"device_id": self.device_id, "timestamp": datetime.utcnow().isoformat(), "data": sensor_data}

        try:
            await self.socket.send_json(message, flags=zmq.NOBLOCK)
            return True
        except zmq.Again:
            # Queue full
            return False

    async def close(self):
        self.socket.close()
        self.context.term()


# Usage examples
async def device_data_loop():
    """Example device data collection loop"""
    sender = AsyncDeviceDataSender(device_id="sensor_001")

    try:
        while True:
            # Your sensor reading logic here
            sensor_data = {
                "temperature": 23.5 + (time.time() % 10),  # Mock data
                "humidity": 45.0 + (time.time() % 5),
                "pressure": 1013.25,
            }

            success = await sender.send_data_point(sensor_data)
            if not success:
                print("⚠️ Failed to send data point")

            await asyncio.sleep(0.1)  # 10Hz

    except KeyboardInterrupt:
        print("🛑 Stopping device loop...")
    finally:
        await sender.close()


async def run_gateway():
    """Run the gateway service"""
    # Initialize InfluxDB client
    influx_client = InfluxDBClient3(host="your-influxdb-host", token="your-token", database="your-database")

    gateway = AsyncInfluxGateway(influx_client=influx_client, batch_size=250, flush_interval=1.0)

    await gateway.start()


# Main execution
if __name__ == "__main__":
    try:
        # Run gateway
        asyncio.run(run_gateway())

        # Or run device simulator
        # asyncio.run(device_data_loop())

    except KeyboardInterrupt:
        print("👋 Goodbye!")
