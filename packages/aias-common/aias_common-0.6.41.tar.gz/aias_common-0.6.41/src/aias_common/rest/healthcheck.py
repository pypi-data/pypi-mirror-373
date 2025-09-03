from fastapi import APIRouter, status
from fastapi.responses import Response

ROUTER = APIRouter()


@ROUTER.get("/healthcheck")
async def healthcheck():
    return Response(content="OK", status_code=status.HTTP_200_OK)
