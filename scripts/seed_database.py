import argparse
import asyncio
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import sys

from sqlalchemy import delete, func, or_, select

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.hashing import hash_password
from app.database import SessionLocal, init_db
from app.models.bid import Bid
from app.models.contract import Contract
from app.models.enums import BidStatus, ContractStatus, ProjectStatus, UserRole
from app.models.project import Project
from app.models.review import Review
from app.models.user import User


SEED_USER_PREFIX = "seed_"
SEED_PROJECT_PREFIX = "Seed Project"
DEFAULT_PASSWORD = "seedpass123"
CLIENT_COUNT = 5
FREELANCER_COUNT = 5
PROJECT_COUNT = 20
OPEN_PROJECTS = 8
IN_PROGRESS_PROJECTS = 6
COMPLETED_PROJECTS = 6


CLIENT_PROFILES = [
    ("atlas_agency", "Product-focused client that hires for marketplace features."),
    ("northstar_labs", "Startup team building internal tools and dashboards."),
    ("brightpath_studio", "Creative agency outsourcing backend and automation work."),
    ("summit_commerce", "E-commerce operator improving customer-facing systems."),
    ("harbor_ops", "Operations-heavy business with workflow and reporting needs."),
]

FREELANCER_PROFILES = [
    ("api_architect", "Backend specialist focused on FastAPI and SQLite."),
    ("react_builder", "Full-stack developer shipping polished client portals."),
    ("data_flow_dev", "Engineer who automates data pipelines and integrations."),
    ("qa_guardian", "Developer with strong testing and CI instincts."),
    ("cloud_crafter", "Freelancer experienced in deployment and observability."),
]

PROJECT_BLUEPRINTS = [
    ("Marketplace messaging API", "Build threaded messaging between clients and freelancers with unread state and search support."),
    ("Invoice export dashboard", "Create a reporting dashboard with CSV export and scheduled delivery for accounting."),
    ("Portfolio review workflow", "Implement review queues, approval notes, and notification hooks for submitted portfolios."),
    ("Subscription billing sync", "Connect subscription events to internal records and reconcile failed charge states."),
    ("Admin audit trail", "Track important admin actions with filters by actor, date range, and affected resource."),
    ("Talent search filters", "Expand search with skill tags, availability filters, and ranking improvements."),
    ("Proposal scoring service", "Score bids against project requirements and surface recommendations to clients."),
    ("Client onboarding wizard", "Design a multi-step onboarding flow with validation and resumable progress."),
    ("Freelancer analytics page", "Show earnings, proposal win rate, and contract completion trends."),
    ("Review moderation queue", "Build moderation tools for flagged reviews with status history."),
    ("Escrow release tracker", "Track milestones, release approvals, and payment release history."),
    ("Webhook delivery monitor", "Monitor webhook deliveries with retries, logs, and failure alerts."),
    ("Saved search alerts", "Notify freelancers when new projects match saved filters and budgets."),
    ("Project template library", "Allow clients to save and reuse project briefs and pricing assumptions."),
    ("Availability calendar sync", "Sync freelancer availability from external calendars and manual blocks."),
    ("Dispute intake portal", "Capture contract disputes, attachments, and resolution notes."),
    ("KYC document review", "Manage identity verification submissions and reviewer comments."),
    ("Recommendation feed", "Generate a personalized project feed based on freelancer history."),
    ("Team invitation system", "Let clients invite collaborators and manage project-level permissions."),
    ("SLA breach alerts", "Alert teams when response-time or delivery milestones are at risk."),
]

BID_MESSAGES = [
    "I can deliver this in phases with clear weekly milestones and status updates.",
    "I have shipped similar marketplace workflows and can start immediately.",
    "I would approach this with tests first and keep the implementation easy to extend.",
    "This scope fits well with my FastAPI and SQLite experience.",
    "I can handle both the API layer and the supporting background jobs.",
]

REVIEW_COMMENTS = [
    "Great communication and consistent delivery across the whole contract.",
    "Strong implementation quality and proactive updates throughout the project.",
    "The freelancer was reliable, thoughtful, and easy to collaborate with.",
    "The work landed on time and the handoff was clean and well documented.",
]


@dataclass(frozen=True)
class SeedUser:
    username: str
    email: str
    password: str
    role: UserRole
    bio: str


def build_client_users() -> list[SeedUser]:
    users: list[SeedUser] = []
    for index, (slug, bio) in enumerate(CLIENT_PROFILES, start=1):
        users.append(
            SeedUser(
                username=f"{SEED_USER_PREFIX}client_{index}_{slug}",
                email=f"{SEED_USER_PREFIX}client_{index}@example.com",
                password=DEFAULT_PASSWORD,
                role=UserRole.CLIENT,
                bio=bio,
            )
        )
    return users


def build_freelancer_users() -> list[SeedUser]:
    users: list[SeedUser] = []
    for index, (slug, bio) in enumerate(FREELANCER_PROFILES, start=1):
        users.append(
            SeedUser(
                username=f"{SEED_USER_PREFIX}freelancer_{index}_{slug}",
                email=f"{SEED_USER_PREFIX}freelancer_{index}@example.com",
                password=DEFAULT_PASSWORD,
                role=UserRole.FREELANCER,
                bio=bio,
            )
        )
    return users


def project_status_for(index: int) -> ProjectStatus:
    if index < OPEN_PROJECTS:
        return ProjectStatus.OPEN
    if index < OPEN_PROJECTS + IN_PROGRESS_PROJECTS:
        return ProjectStatus.IN_PROGRESS
    return ProjectStatus.COMPLETED


def make_project_created_at(now: datetime, index: int) -> datetime:
    return now - timedelta(days=(PROJECT_COUNT - index) * 2)


def make_project_deadline(today: date, index: int, status: ProjectStatus) -> date:
    if status == ProjectStatus.COMPLETED:
        return today - timedelta(days=10 - (index % 4))
    if status == ProjectStatus.IN_PROGRESS:
        return today + timedelta(days=10 + index)
    return today + timedelta(days=20 + index)


async def reset_seed_data(db) -> None:
    seed_user_ids = list(
        (
            await db.scalars(
                select(User.id).where(User.username.like(f"{SEED_USER_PREFIX}%"))
            )
        ).all()
    )
    if not seed_user_ids:
        return

    seed_project_ids = list(
        (
            await db.scalars(
                select(Project.id).where(Project.client_id.in_(seed_user_ids))
            )
        ).all()
    )

    seed_contract_ids: set[int] = set()
    if seed_project_ids:
        seed_contract_ids.update(
            (
                await db.scalars(
                    select(Contract.id).where(Contract.project_id.in_(seed_project_ids))
                )
            ).all()
        )

    seed_contract_ids.update(
        (
            await db.scalars(
                select(Contract.id).where(
                    or_(
                        Contract.client_id.in_(seed_user_ids),
                        Contract.freelancer_id.in_(seed_user_ids),
                    )
                )
            )
        ).all()
    )

    if seed_contract_ids:
        await db.execute(delete(Review).where(Review.contract_id.in_(seed_contract_ids)))
        await db.execute(delete(Contract).where(Contract.id.in_(seed_contract_ids)))

    bid_filters = []
    if seed_project_ids:
        bid_filters.append(Bid.project_id.in_(seed_project_ids))
    if seed_user_ids:
        bid_filters.append(Bid.freelancer_id.in_(seed_user_ids))
    if bid_filters:
        await db.execute(delete(Bid).where(or_(*bid_filters)))

    if seed_project_ids:
        await db.execute(delete(Project).where(Project.id.in_(seed_project_ids)))

    await db.execute(delete(User).where(User.id.in_(seed_user_ids)))
    await db.commit()


async def seed_users(db) -> tuple[list[User], list[User]]:
    clients: list[User] = []
    freelancers: list[User] = []

    for spec in build_client_users() + build_freelancer_users():
        user = User(
            username=spec.username,
            email=spec.email,
            hashed_password=hash_password(spec.password),
            role=spec.role,
            bio=spec.bio,
        )
        db.add(user)
        if spec.role == UserRole.CLIENT:
            clients.append(user)
        else:
            freelancers.append(user)

    await db.flush()
    return clients, freelancers


async def seed_projects(db, clients: list[User], freelancers: list[User]) -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    today = now.date()

    for index, (title, description) in enumerate(PROJECT_BLUEPRINTS):
        status = project_status_for(index)
        client = clients[index % len(clients)]
        budget = round(800 + (index * 185), 2)
        created_at = make_project_created_at(now, index)
        deadline = make_project_deadline(today, index, status)
        project = Project(
            title=f"{SEED_PROJECT_PREFIX} {index + 1:02d}: {title}",
            description=description,
            budget=budget,
            deadline=deadline,
            status=status,
            client_id=client.id,
            created_at=created_at,
        )
        db.add(project)
        await db.flush()

        bidder_count = 3 if index % 2 == 0 else 4
        bidders = [
            freelancers[(index + offset) % len(freelancers)]
            for offset in range(bidder_count)
        ]
        accepted_bid = None
        accepted_index = index % bidder_count

        for bid_index, freelancer in enumerate(bidders):
            if status == ProjectStatus.OPEN:
                bid_status = BidStatus.PENDING
            else:
                bid_status = (
                    BidStatus.ACCEPTED if bid_index == accepted_index else BidStatus.REJECTED
                )

            bid = Bid(
                project_id=project.id,
                freelancer_id=freelancer.id,
                price=round(budget * (0.78 + bid_index * 0.06), 2),
                message=BID_MESSAGES[(index + bid_index) % len(BID_MESSAGES)],
                status=bid_status,
                created_at=created_at + timedelta(hours=bid_index + 2),
            )
            db.add(bid)
            await db.flush()

            if bid_status == BidStatus.ACCEPTED:
                accepted_bid = bid

        if accepted_bid is None:
            continue

        contract_created_at = accepted_bid.created_at + timedelta(days=1)
        contract = Contract(
            project_id=project.id,
            client_id=client.id,
            freelancer_id=accepted_bid.freelancer_id,
            agreed_price=accepted_bid.price,
            status=(
                ContractStatus.ACTIVE
                if status == ProjectStatus.IN_PROGRESS
                else ContractStatus.FINISHED
            ),
            created_at=contract_created_at,
            finished_at=(
                contract_created_at + timedelta(days=14)
                if status == ProjectStatus.COMPLETED
                else None
            ),
        )
        db.add(contract)
        await db.flush()

        completed_offset = index - (OPEN_PROJECTS + IN_PROGRESS_PROJECTS)
        if status == ProjectStatus.COMPLETED and completed_offset < 4:
            review = Review(
                contract_id=contract.id,
                rating=5 if completed_offset % 2 == 0 else 4,
                comment=REVIEW_COMMENTS[completed_offset % len(REVIEW_COMMENTS)],
                created_at=contract.finished_at + timedelta(hours=6),
            )
            db.add(review)


async def get_seed_counts(db) -> dict[str, int]:
    project_ids = list(
        (
            await db.scalars(
                select(Project.id).where(Project.title.like(f"{SEED_PROJECT_PREFIX}%"))
            )
        ).all()
    )
    contract_ids = list(
        (
            await db.scalars(
                select(Contract.id).where(
                    Contract.project_id.in_(project_ids) if project_ids else False
                )
            )
        ).all()
    )

    return {
        "users": int(
            await db.scalar(
                select(func.count()).select_from(User).where(
                    User.username.like(f"{SEED_USER_PREFIX}%")
                )
            )
            or 0
        ),
        "projects": len(project_ids),
        "bids": int(
            await db.scalar(
                select(func.count()).select_from(Bid).where(
                    Bid.project_id.in_(project_ids) if project_ids else False
                )
            )
            or 0
        ),
        "contracts": len(contract_ids),
        "reviews": int(
            await db.scalar(
                select(func.count()).select_from(Review).where(
                    Review.contract_id.in_(contract_ids) if contract_ids else False
                )
            )
            or 0
        ),
        "open_projects": int(
            await db.scalar(
                select(func.count()).select_from(Project).where(
                    Project.title.like(f"{SEED_PROJECT_PREFIX}%"),
                    Project.status == ProjectStatus.OPEN,
                )
            )
            or 0
        ),
        "in_progress_projects": int(
            await db.scalar(
                select(func.count()).select_from(Project).where(
                    Project.title.like(f"{SEED_PROJECT_PREFIX}%"),
                    Project.status == ProjectStatus.IN_PROGRESS,
                )
            )
            or 0
        ),
        "completed_projects": int(
            await db.scalar(
                select(func.count()).select_from(Project).where(
                    Project.title.like(f"{SEED_PROJECT_PREFIX}%"),
                    Project.status == ProjectStatus.COMPLETED,
                )
            )
            or 0
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed the database with demo freelance marketplace data."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing seed_* demo data before inserting a fresh dataset.",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    await init_db()

    async with SessionLocal() as db:
        existing_seed_users = int(
            await db.scalar(
                select(func.count()).select_from(User).where(
                    User.username.like(f"{SEED_USER_PREFIX}%")
                )
            )
            or 0
        )

        if existing_seed_users and not args.reset:
            raise SystemExit(
                "Seed data already exists. Re-run with --reset to replace the existing seed_* dataset."
            )

        if args.reset:
            await reset_seed_data(db)

        clients, freelancers = await seed_users(db)
        await seed_projects(db, clients, freelancers)
        await db.commit()

        counts = await get_seed_counts(db)

    print("Seed data created successfully.")
    print(f"Users: {counts['users']} (clients: {CLIENT_COUNT}, freelancers: {FREELANCER_COUNT})")
    print(
        "Projects: "
        f"{counts['projects']} "
        f"(open: {counts['open_projects']}, in_progress: {counts['in_progress_projects']}, completed: {counts['completed_projects']})"
    )
    print(
        f"Bids: {counts['bids']}, Contracts: {counts['contracts']}, Reviews: {counts['reviews']}"
    )
    print("Login password for all seed users: seedpass123")
    print("Example usernames:")
    print("  - seed_client_1_atlas_agency")
    print("  - seed_freelancer_1_api_architect")


if __name__ == "__main__":
    asyncio.run(main())
