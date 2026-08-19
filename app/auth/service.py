"""
Auth business logic.

AuthService depends on five abstractions: UserRepository,
InviteTokenRepository, OrganizationRepository, PasswordHasher, and
TokenIssuer. It has no idea whether users live in MySQL, whether
passwords are hashed with bcrypt or argon2, or whether sessions are JWTs
or something else — every one of those is injected. This is the same
dependency-inversion pattern as FormService/VoiceService in Phase 1,
applied to a new domain.

There is no public "register" method here by design — Phase 2's auth
model is invite-only. The very first org+admin is created by
scripts/seed_org.py, which talks to the repositories directly.
"""

from app.auth.jwt_handler import TokenIssuer, TokenPayload
from app.auth.models import InviteToken, Role, User, Organization
from app.auth.password_hasher import PasswordHasher
from app.auth.repository import InviteTokenRepository, OrganizationRepository, UserRepository
from app.auth.schemas import InviteCreate, InviteStats, InviteTokenDetails, UserRead, UserFullDetails
from app.core.exceptions import NotFoundError, ValidationError


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        invite_repository: InviteTokenRepository,
        org_repository: OrganizationRepository,
        password_hasher: PasswordHasher,
        token_issuer: TokenIssuer,
    ) -> None:
        self._users = user_repository
        self._invites = invite_repository
        self._orgs = org_repository
        self._hasher = password_hasher
        self._tokens = token_issuer

    # --- Login --------------------------------------------------------

    def login(self, email: str, password: str) -> str:
        """Returns a signed session token if credentials are valid."""
        user = self._users.get_by_email(email)
        if user is None or not user.is_active:
            raise ValidationError("Invalid email or password")
        if not self._hasher.verify(password, user.hashed_password):
            raise ValidationError("Invalid email or password")

        return self._tokens.issue(TokenPayload(user_id=user.id, org_id=user.org_id, role=user.role))
    
    
    def signup(self, full_name: str, org_name: str, email: str, password: str) -> User:
        """Creates a new user."""
        
        if self._users.get_by_email(email) is not None:
            raise ValidationError(f"User with {email} - email already exists!")
        
        ## Creating a NEW ORGANISATION:
        organization = self._orgs.create(Organization(name=org_name))
        
        ## Creating a User object for insertion in User Table.
        admin = User(
            org_id=organization.id,
            email=email,
            hashed_password=self._hasher.hash(password),
            full_name=full_name,
            role=Role.ORG_ADMIN,
        )
        user = self._users.create(admin)
        
        return user


    def get_current_user(self, token: str) -> UserRead:
        ## Just verify the JWT Cookie; On match return the basic details
        payload: TokenPayload = self._tokens.verify(token)
        
        return UserRead(id=payload.user_id,
                        org_id=payload.org_id,
                        role=payload.role)
    
    
    
    def get_user_full_details(self, user_id: str) -> dict:
        ## Get user deatils by User ID:
        user = self._users.get_by_id(user_id)
        if user is not None:
            ## Add Organozation details to user details:
            org = self._orgs.get_by_id(user.org_id)          # Get Organisation details by Org ID
                    
            return UserFullDetails(id=user.id,
                                org_id=org.id, 
                                org_name=org.name, 
                                email=user.email, 
                                full_name=user.full_name, 
                                role=user.role)
        else:
            raise ValidationError(f"User with {user_id} does not exists!")


    # --- Invites --------------------------------------------------------

    def create_invite(self, org_id: str, inviter: dict, payload: InviteCreate) -> InviteToken:
        if inviter.role != Role.ORG_ADMIN:
            raise ValidationError("Only an org admin can invite new users")
        if self._users.get_by_email(payload.email) is not None:
            raise ValidationError(f"A user with email '{payload.email}' already exists")

        invite = InviteToken(org_id=org_id, 
                             email=payload.email, 
                             full_name=payload.full_name, 
                             role=payload.role)
        
        return self._invites.create(invite)
    
    
    def get_token_details(self, token: str) -> InviteTokenDetails:
        invite = self._invites.get_by_token(token)
        if invite is None:
            raise NotFoundError("Invite not found.")
        if invite.is_accepted:
            raise ValidationError("This invite has already been used.")
        if invite.is_expired:
            raise ValidationError("This invite has already expired.")
        if self._users.get_by_email(invite.email) is not None:
            raise ValidationError(f"A user with email '{invite.email}' already exists")
        
        org = self._orgs.get_by_id(invite.org_id)
        
        if org is None:
            raise NotFoundError("Organization for this invite no longer exists")
        
        return InviteTokenDetails(full_name = invite.full_name,
                                  org_name = org.name,
                                  role = invite.role)
        
        
        

    def accept_invite(self, token: str, password: str) -> str:
        """Consumes an invite token, creates the User, and returns a session token."""
        invite = self._invites.get_by_token(token)

        ## Validation is already done, just make a new USER:
        user = User(
            org_id=invite.org_id,
            email=invite.email,
            hashed_password=self._hasher.hash(password),
            full_name=invite.full_name,
            role=invite.role,
        )
        created_user = self._users.create(user)
        self._invites.mark_accepted(invite)

        return self._tokens.issue(
            TokenPayload(user_id=created_user.id, org_id=created_user.org_id, role=created_user.role)
        )

    
    
    def list_org_users(self, org_id: str) -> list[User]:
        return self._users.list_for_org(org_id)



    def total_invites(self, org_id: str) -> InviteStats:
            return self._invites.all_invites(org_id)
