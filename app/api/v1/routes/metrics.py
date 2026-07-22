from fastapi import APIRouter, Depends
from app.repositories.stats_repository import StatsRepository
from app.core.dependencies import get_stats_repo

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
async def get_metrics(stats_repo: StatsRepository = Depends(get_stats_repo)):
    stats = await stats_repo.get_all()
    return {"stats": stats}
