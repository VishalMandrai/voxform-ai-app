"""
Seed script — the ONLY way a new Organization + its first admin user
get created. There is no public signup route by design (Auth
model is invite-only within an existing org); someone with shell/DB
access has to run this once per new tenant.

Usage:
    python -m scripts.seed_org --org-name "Org XYZ" \\
        --admin-email orgXYZ@gmail.com --admin-name "Admin ABC" --admin-password "ChangeMe123"

This script talks to the repositories directly — the same
MySQLOrganizationRepository / MySQLUserRepository / BcryptPasswordHasher
the rest of the app uses, so the data it creates is identical in shape
to anything created through normal application flow.
"""

import argparse
import sys

from app.auth.models import Organization, Role, User
from app.auth.password_hasher import BcryptPasswordHasher
from app.auth.repository import MySQLOrganizationRepository, MySQLUserRepository
from app.core.db import Base, SessionLocal, engine


def seed_org(org_name: str, admin_email: str, admin_name: str, admin_password: str) -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user_repo = MySQLUserRepository(db)
        org_repo = MySQLOrganizationRepository(db)
        hasher = BcryptPasswordHasher()

        if user_repo.get_by_email(admin_email) is not None:
            print(f"A user with email '{admin_email}' already exists — aborting.", file=sys.stderr)
            sys.exit(1)

        ## Creating a NEW ORGANISATION:
        organization = org_repo.create(Organization(name=org_name))
        
        ## Creating a User object for insertion in User Table.
        admin = User(
            org_id=organization.id,
            email=admin_email,
            hashed_password=hasher.hash(admin_password),
            full_name=admin_name,
            role=Role.ORG_ADMIN,
        )
        user_repo.create(admin)

        print(f"Created organization '{org_name}' (id={organization.id})")
        print(f"Created admin user '{admin_email}' (id={admin.id})")
        print("They can now log in at /login and invite teammates from /team.")
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed a new organization and its first admin user.")
    parser.add_argument("--org-name", required=True, help="Display name for the new organization")
    parser.add_argument("--admin-email", required=True, help="Email for the first admin user")
    parser.add_argument("--admin-name", required=True, help="Full name for the first admin user")
    parser.add_argument("--admin-password", required=True, help="Initial password (min 8 chars)")
    args = parser.parse_args()

    if len(args.admin_password) < 8:
        print("Password must be at least 8 characters.", file=sys.stderr)
        sys.exit(1)

    seed_org(args.org_name, args.admin_email, args.admin_name, args.admin_password)


if __name__ == "__main__":
    main()
