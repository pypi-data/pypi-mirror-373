import asyncio
import logging
import random
import time
import uuid

import pytest

from .services import ServiceMessaging


class UserService:
    def __init__(self):
        # Compose with messaging capability
        self.messaging = ServiceMessaging("user-service")
        self.users = {}  # Simple in-memory store
        self.logger = logging.getLogger("egse.user-service")

    async def create_user(self, email: str, name: str) -> str:
        """Create a user and publish event"""
        user_id = str(uuid.uuid4())

        # Business logic
        user_data = {"id": user_id, "email": email, "name": name, "created_at": time.time()}
        self.users[user_id] = user_data

        self.logger.info(f"Created user: {name} ({email})")

        # Publish event
        await self.messaging.publish_event("user_created", {"user_id": user_id, "email": email, "name": name})

        return user_id

    async def update_user(self, user_id: str, updates: dict):
        """Update user and publish event"""
        if user_id not in self.users:
            raise ValueError("User not found")

        # Business logic
        self.users[user_id].update(updates)

        # Publish event
        await self.messaging.publish_event("user_updated", {"user_id": user_id, "updates": updates})

    async def close(self):
        await self.messaging.disconnect()


class EmailService:
    def __init__(self):
        # Compose with messaging capability - subscribe to events we care about
        self.messaging = ServiceMessaging(
            "email-service", subscriptions=["user_created", "user_updated", "order_placed"]
        )

        # Register handlers
        self.messaging.register_handler("user_created", self.handle_user_created)
        self.messaging.register_handler("user_updated", self.handle_user_updated)
        self.messaging.register_handler("order_placed", self.handle_order_placed)

        self.logger = logging.getLogger("egse.email-service")

    async def handle_user_created(self, event_data: dict):
        """Handle new user creation"""
        user_data = event_data["data"]
        email = user_data["email"]
        name = user_data["name"]

        self.logger.info(f"Sending welcome email to {name}")

        # Simulate email sending
        await self._send_email(to=email, subject="Welcome!", template="welcome", data={"name": name})

    async def handle_user_updated(self, event_data: dict):
        """Handle user updates"""
        user_data = event_data["data"]
        user_id = user_data["user_id"]

        self.logger.info(f"User {user_id} was updated")
        # Could send update notification email

    async def handle_order_placed(self, event_data: dict):
        """Handle order placement"""
        order_data = event_data["data"]
        customer_email = order_data["customer_email"]
        order_id = order_data["order_id"]

        await self._send_email(
            to=customer_email, subject="Order Confirmation", template="order_confirmation", data={"order_id": order_id}
        )

    async def _send_email(self, to: str, subject: str, template: str, data: dict):
        """Simulate sending email"""
        await asyncio.sleep(0.1)  # Simulate network delay
        self.logger.info(f"✉️  Sent '{subject}' to {to}")

    async def start(self):
        """Start listening for events"""
        await self.messaging.start_listening()

    async def close(self):
        await self.messaging.disconnect()


# Order Service - both publishes and subscribes
class OrderService:
    def __init__(self):
        # This service both publishes and subscribes
        self.messaging = ServiceMessaging(
            "order-service",
            subscriptions=["user_created"],  # Maybe we want to track new users
        )

        # Register handlers
        self.messaging.register_handler("user_created", self.handle_new_user)

        self.orders = {}
        self.user_orders = {}  # Track orders per user
        self.logger = logging.getLogger("egse.order-service")

    async def handle_new_user(self, event_data: dict):
        """Handle new user - could send promo code"""
        user_data = event_data["data"]
        user_id = user_data["user_id"]

        self.user_orders[user_id] = []
        self.logger.info(f"Tracking new user: {user_id}")

    async def place_order(self, user_id: str, items: list[dict], customer_email: str):
        """Place an order and publish event"""
        order_id = str(uuid.uuid4())

        # Business logic
        order_data = {
            "id": order_id,
            "user_id": user_id,
            "items": items,
            "customer_email": customer_email,
            "total": sum(item["price"] * item["quantity"] for item in items),
            "created_at": time.time(),
        }

        self.orders[order_id] = order_data

        if user_id in self.user_orders:
            self.user_orders[user_id].append(order_id)

        self.logger.info(f"Order placed: {order_id} for user {user_id}")

        # Publish event
        await self.messaging.publish_event(
            "order_placed",
            {"order_id": order_id, "user_id": user_id, "customer_email": customer_email, "total": order_data["total"]},
        )

        return order_id

    async def start(self):
        """Start listening for events"""
        await self.messaging.start_listening()

    async def close(self):
        await self.messaging.disconnect()


# Analytics Service - subscribes to multiple events
class AnalyticsService:
    def __init__(self):
        self.messaging = ServiceMessaging(
            "analytics-service", subscriptions=["user_created", "order_placed", "user_updated"]
        )

        # Register handlers
        self.messaging.register_handler("user_created", self.track_user_signup)
        self.messaging.register_handler("order_placed", self.track_order)
        self.messaging.register_handler("user_updated", self.track_user_update)

        self.metrics = {"users_created": 0, "orders_placed": 0, "total_revenue": 0.0}
        self.logger = logging.getLogger("egse.analytics-service")

    async def track_user_signup(self, event_data: dict):
        """Track user signup"""
        self.metrics["users_created"] += 1
        self.logger.info(f"📊 Users created: {self.metrics['users_created']}")

    async def track_order(self, event_data: dict):
        """Track order placement"""
        order_data = event_data["data"]
        total = order_data["total"]

        self.metrics["orders_placed"] += 1
        self.metrics["total_revenue"] += total

        self.logger.info(f"📊 Orders: {self.metrics['orders_placed']}, Revenue: ${self.metrics['total_revenue']:.2f}")

    async def track_user_update(self, event_data: dict):
        """Track user updates"""
        self.logger.info("📊 User update tracked")

    async def start(self):
        await self.messaging.start_listening()

    async def close(self):
        await self.messaging.disconnect()


async def run_microservices_demo():
    """Run the complete microservices system"""

    # Create services
    user_service = UserService()
    email_service = EmailService()
    order_service = OrderService()
    analytics_service = AnalyticsService()

    # Start subscriber services
    tasks = [
        asyncio.create_task(email_service.start()),
        asyncio.create_task(order_service.start()),
        asyncio.create_task(analytics_service.start()),
    ]

    # Demo scenario
    async def demo_workflow():
        await asyncio.sleep(1)  # Let services connect

        # Create some users
        user1_id = await user_service.create_user("alice@example.com", "Alice Smith")
        user2_id = await user_service.create_user("bob@example.com", "Bob Jones")

        await asyncio.sleep(0.5)

        # Place some orders
        await order_service.place_order(
            user1_id, [{"name": "Widget", "price": 29.99, "quantity": 2}], "alice@example.com"
        )

        await order_service.place_order(
            user2_id, [{"name": "Gadget", "price": 19.99, "quantity": 1}], "bob@example.com"
        )

        await asyncio.sleep(0.5)

        # Update a user
        await user_service.update_user(user1_id, {"name": "Alice Johnson"})

        await asyncio.sleep(2)

        # Stress test, send hundreds of notifications

        for x in range(100):
            # Place some orders
            await order_service.place_order(
                user1_id,
                [{"name": "Widget", "price": 29.99 + x * 3.14, "quantity": random.choice([1, 2, 3, 4])}],
                "alice@example.com",
            )

            await order_service.place_order(
                user2_id,
                [{"name": "Gadget", "price": 19.99 + x * 1.23, "quantity": random.choice([1, 2, 3, 4])}],
                "bob@example.com",
            )

        # Cleanup
        await user_service.close()
        await email_service.close()
        await order_service.close()
        await analytics_service.close()

    async def _cleanup_running_tasks():
        # Cancel all running tasks
        for task in tasks:
            if not task.done():
                print(f"Cancelling task {task.get_name()}.")
                task.cancel()

        # Wait for tasks to complete their cancellation
        if tasks:
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            except asyncio.CancelledError as exc:
                print(f"Caught {type(exc).__name__}: {exc}.")
                pass

    tasks.append(asyncio.create_task(demo_workflow()))

    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("Shutting down...")

    await _cleanup_running_tasks()


@pytest.mark.asyncio
def test_notify_hub(): ...


if __name__ == "__main__":
    from egse.logger import setup_logging

    asyncio.run(run_microservices_demo())
