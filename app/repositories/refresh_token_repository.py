from datetime import datetime, timezone

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_refresh_token(
        self, jti: str, user_id: str, expires_at: datetime
    ) -> RefreshToken:
        token = RefreshToken(
            jti=jti,
            user_id=user_id,
            expires_at=expires_at,
        )
        self.db.add(token)
        await self.db.flush()
        return token

    async def get_by_jti(self, jti: str) -> RefreshToken | None:
        query = select(RefreshToken).where(RefreshToken.jti == jti)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_for_update_by_jti(self, jti: str) -> RefreshToken | None:
        query = select(RefreshToken).where(RefreshToken.jti == jti).with_for_update()
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def revoke_by_jti(self, jti: str) -> None:
        query = (
            update(RefreshToken)
            .where(RefreshToken.jti == jti, RefreshToken.revoked.is_(False))
            .values(revoked=True)
        )
        await self.db.execute(query)

    async def revoke_all_for_user(self, user_id: str) -> None:
        query = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked.is_(False),
            )
            .values(revoked=True)
        )
        await self.db.execute(query)

    async def delete_expired(self) -> None:
        await self.db.execute(
            delete(RefreshToken).where(
                RefreshToken.expires_at < datetime.now(timezone.utc)
            )
        )
