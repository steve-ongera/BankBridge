# api/management/commands/seed_data.py

import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction as db_transaction
from api.models import User, Transaction


PREDEFINED_USERS = [
    {"username": "john_doe",       "email": "john@example.com",    "first_name": "John",    "last_name": "Doe",      "phone": "1234567890", "balance": Decimal("5000.00")},
    {"username": "jane_smith",     "email": "jane@example.com",    "first_name": "Jane",    "last_name": "Smith",    "phone": "2345678901", "balance": Decimal("7500.50")},
    {"username": "mike_johnson",   "email": "mike@example.com",    "first_name": "Mike",    "last_name": "Johnson",  "phone": "3456789012", "balance": Decimal("3250.75")},
    {"username": "sarah_williams", "email": "sarah@example.com",   "first_name": "Sarah",   "last_name": "Williams", "phone": "4567890123", "balance": Decimal("10200.00")},
    {"username": "robert_brown",   "email": "robert@example.com",  "first_name": "Robert",  "last_name": "Brown",    "phone": "5678901234", "balance": Decimal("2150.25")},
    {"username": "emily_davis",    "email": "emily@example.com",   "first_name": "Emily",   "last_name": "Davis",    "phone": "6789012345", "balance": Decimal("8900.00")},
    {"username": "david_miller",   "email": "david@example.com",   "first_name": "David",   "last_name": "Miller",   "phone": "7890123456", "balance": Decimal("4320.60")},
    {"username": "lisa_wilson",    "email": "lisa@example.com",    "first_name": "Lisa",    "last_name": "Wilson",   "phone": "8901234567", "balance": Decimal("15750.00")},
    {"username": "james_moore",    "email": "james@example.com",   "first_name": "James",   "last_name": "Moore",    "phone": "9012345678", "balance": Decimal("6100.80")},
    {"username": "anna_taylor",    "email": "anna@example.com",    "first_name": "Anna",    "last_name": "Taylor",   "phone": "0123456789", "balance": Decimal("9450.30")},
]

RANDOM_FIRST_NAMES = [
    "Oliver", "Emma", "Liam", "Sophia", "Noah", "Isabella", "William", "Mia",
    "Benjamin", "Charlotte", "Lucas", "Amelia", "Henry", "Harper", "Alexander",
    "Evelyn", "Mason", "Abigail", "Ethan", "Ella",
]

RANDOM_LAST_NAMES = [
    "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson",
    "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis", "Lee",
    "Walker", "Hall", "Allen", "Young", "Hernandez", "King",
]


class Command(BaseCommand):
    help = "Clear all existing data and seed the database with sample users and transactions."

    def add_arguments(self, parser):
        parser.add_argument(
            "--random-count",
            type=int,
            default=20,
            help="Number of randomly generated users to create (default: 20).",
        )
        parser.add_argument(
            "--skip-transactions",
            action="store_true",
            help="Skip seeding sample transactions.",
        )

    def handle(self, *args, **options):
        # Always clear first
        self._clear_data()

        self.stdout.write("\nSeeding predefined users ...")
        predefined = self._seed_predefined_users()

        self.stdout.write(f"\nSeeding {options['random_count']} random users ...")
        random_users = self._seed_random_users(options["random_count"])

        all_users = predefined + random_users

        if not options["skip_transactions"] and len(all_users) >= 2:
            self.stdout.write("\nSeeding sample transactions ...")
            self._seed_transactions(all_users)

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Created {len(predefined)} predefined and "
            f"{len(random_users)} random users."
        ))
        self._print_summary(predefined)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _clear_data(self):
        self.stdout.write("Clearing existing user and transaction data ...")
        Transaction.objects.all().delete()
        deleted, _ = User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.WARNING(
            f"Cleared {deleted} user(s) and all related transactions."
        ))

    def _create_user(self, username, email, first_name, last_name, phone, balance):
        """
        Create a user only if the username does not already exist.

        The model's save() calls super().save() twice (once to get the PK,
        once to write the account_number). We must never pass force_insert=True
        — which get_or_create does internally — so we check existence manually
        and use create_user() which goes through the normal save() flow.

        Balance is written via update() after creation to avoid recording a
        spurious deposit Transaction for every seeded opening balance.
        """
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"  Skipped : {username} (already exists)")
            return None, False

        user = User.objects.create_user(
            username=username,
            email=email,
            password="password123",
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        )

        User.objects.filter(pk=user.pk).update(balance=balance)
        user.refresh_from_db()

        self.stdout.write(
            f"  Created : {username} "
            f"(acc: {user.account_number}, balance: ${balance:,.2f})"
        )
        return user, True

    def _seed_predefined_users(self):
        created = []
        for data in PREDEFINED_USERS:
            user, was_created = self._create_user(**data)
            if was_created:
                created.append(user)
        return created

    def _seed_random_users(self, count):
        created = []
        attempts = 0
        max_attempts = count * 3

        while len(created) < count and attempts < max_attempts:
            attempts += 1
            first  = random.choice(RANDOM_FIRST_NAMES)
            last   = random.choice(RANDOM_LAST_NAMES)
            suffix = random.randint(1, 9999)
            username = f"{first.lower()}_{last.lower()}_{suffix}"
            email    = f"{username}@example.com"
            phone    = "".join(str(random.randint(0, 9)) for _ in range(10))
            balance  = Decimal(str(round(random.uniform(100, 50000), 2)))

            user, was_created = self._create_user(
                username=username,
                email=email,
                first_name=first,
                last_name=last,
                phone=phone,
                balance=balance,
            )
            if was_created:
                created.append(user)

        if len(created) < count:
            self.stdout.write(self.style.WARNING(
                f"  Could only create {len(created)} of {count} random users "
                f"(too many username collisions)."
            ))
        return created

    @db_transaction.atomic
    def _seed_transactions(self, users):
        count = 0

        # Deposits
        for user in random.sample(users, min(5, len(users))):
            amount = Decimal(str(round(random.uniform(100, 2000), 2)))
            try:
                user.deposit(amount)
                count += 1
            except ValueError:
                pass

        # Withdrawals
        for user in random.sample(users, min(5, len(users))):
            user.refresh_from_db()
            if user.balance > Decimal("50"):
                amount = Decimal(str(round(random.uniform(10, float(user.balance) * 0.3), 2)))
                try:
                    user.withdraw(amount)
                    count += 1
                except ValueError:
                    pass

        # Transfers between random pairs
        pool = random.sample(users, min(10, len(users)))
        for i in range(0, len(pool) - 1, 2):
            sender, receiver = pool[i], pool[i + 1]
            sender.refresh_from_db()
            if sender.balance > Decimal("20"):
                amount = Decimal(str(round(random.uniform(10, float(sender.balance) * 0.2), 2)))
                try:
                    sender.transfer(receiver, amount)
                    count += 1
                except ValueError:
                    pass

        self.stdout.write(f"  Created {count} sample transaction(s).")

    def _print_summary(self, users):
        if not users:
            return
        self.stdout.write("\n  Predefined login credentials  (password: password123)\n")
        self.stdout.write(f"  {'Username':<20} {'Account':<14} {'Balance':>12}")
        self.stdout.write("  " + "-" * 48)
        for user in users:
            user.refresh_from_db()
            self.stdout.write(
                f"  {user.username:<20} {user.account_number:<14} ${user.balance:>11,.2f}"
            )
        self.stdout.write("")