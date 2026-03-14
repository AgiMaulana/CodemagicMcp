from typing import Any

import httpx

from codemagic_mcp.config import settings


class CodemagicClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=settings.codemagic_base_url,
            headers={"x-auth-token": settings.codemagic_api_key},
            timeout=30.0,
        )

    async def __aenter__(self) -> "CodemagicClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._client.aclose()

    async def _get(self, path: str, **kwargs: Any) -> Any:
        response = await self._client.get(path, **kwargs)
        response.raise_for_status()
        return response.json()

    async def _post(self, path: str, **kwargs: Any) -> Any:
        response = await self._client.post(path, **kwargs)
        response.raise_for_status()
        return response.json()

    async def _delete(self, path: str, **kwargs: Any) -> Any:
        response = await self._client.delete(path, **kwargs)
        response.raise_for_status()
        return response.json()

    # Applications

    async def list_apps(self) -> Any:
        return await self._get("/apps")

    async def get_app(self, app_id: str) -> Any:
        return await self._get(f"/apps/{app_id}")

    async def add_app(self, repository_url: str) -> Any:
        return await self._post("/apps", json={"repositoryUrl": repository_url})

    async def add_private_app(
        self,
        repository_url: str,
        ssh_key_data: str,
        ssh_passphrase: str | None = None,
        project_type: str | None = None,
        team_id: str | None = None,
    ) -> Any:
        payload: dict[str, Any] = {
            "repositoryUrl": repository_url,
            "sshKey": {"data": ssh_key_data},
        }
        if ssh_passphrase is not None:
            payload["sshKey"]["passphrase"] = ssh_passphrase
        if project_type is not None:
            payload["projectType"] = project_type
        if team_id is not None:
            payload["teamId"] = team_id
        return await self._post("/apps/new", json=payload)

    # Builds

    async def trigger_build(
        self,
        app_id: str,
        workflow_id: str,
        branch: str | None = None,
        tag: str | None = None,
        environment: dict[str, Any] | None = None,
        instance_type: str | None = None,
    ) -> Any:
        payload: dict[str, Any] = {
            "appId": app_id,
            "workflowId": workflow_id,
        }
        if branch is not None:
            payload["branch"] = branch
        if tag is not None:
            payload["tag"] = tag
        if environment is not None:
            payload["environment"] = environment
        if instance_type is not None:
            payload["instanceType"] = instance_type
        return await self._post("/builds", json=payload)

    async def cancel_build(self, build_id: str) -> Any:
        return await self._post(f"/builds/{build_id}/cancel")

    # Artifacts

    async def get_artifact_url(self, secure_filename: str) -> Any:
        return await self._get(f"/artifacts/{secure_filename}")

    async def create_artifact_public_url(
        self, secure_filename: str, expires_at: int
    ) -> Any:
        return await self._post(
            f"/artifacts/{secure_filename}/public-url",
            json={"expiresAt": expires_at},
        )

    # Caches

    async def list_caches(self, app_id: str) -> Any:
        return await self._get(f"/apps/{app_id}/caches")

    async def delete_all_caches(self, app_id: str) -> Any:
        return await self._delete(f"/apps/{app_id}/caches")

    async def delete_cache(self, app_id: str, cache_id: str) -> Any:
        return await self._delete(f"/apps/{app_id}/caches/{cache_id}")
