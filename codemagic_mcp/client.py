from typing import Any

import httpx

from codemagic_mcp.config import settings


class CodemagicClient:
    def __init__(self) -> None:
        self.default_app_id: str | None = settings.codemagic_default_app_id
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

    async def _put(self, path: str, **kwargs: Any) -> Any:
        response = await self._client.put(path, **kwargs)
        response.raise_for_status()
        return response.json()

    async def _delete(self, path: str, **kwargs: Any) -> Any:
        response = await self._client.delete(path, **kwargs)
        response.raise_for_status()
        return response.json()

    # Applications

    def _trim_app(self, app: dict) -> dict:
        repo = app.get("repository") or {}
        return {
            "_id": app.get("_id"),
            "appName": app.get("appName"),
            "projectType": app.get("projectType"),
            "archived": app.get("archived"),
            "isConfigured": app.get("isConfigured"),
            "lastBuildId": app.get("lastBuildId"),
            "createdAt": app.get("createdAt"),
            "repository": {
                "url": repo.get("htmlUrl"),
                "provider": repo.get("provider"),
                "defaultBranch": repo.get("defaultBranch"),
                "language": repo.get("language"),
            },
        }

    async def list_apps(self) -> Any:
        data = await self._get("/apps")
        apps = data.get("applications", data) if isinstance(data, dict) else data
        if isinstance(apps, list):
            return [self._trim_app(a) for a in apps]
        return apps

    async def get_app(self, app_id: str) -> Any:
        data = await self._get(f"/apps/{app_id}")
        app = data.get("application", data) if isinstance(data, dict) else data
        return self._trim_app(app)

    async def add_app(self, repository_url: str) -> Any:
        return await self._post("/apps", json={"repositoryUrl": repository_url})

    async def delete_app(self, app_id: str) -> Any:
        return await self._delete(f"/apps/{app_id}")

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

    async def list_builds(
        self,
        app_id: str | None = None,
        branch: str | None = None,
        tag: str | None = None,
        limit: int = 10,
        page: int = 1,
    ) -> Any:
        params: dict[str, Any] = {}
        if app_id is not None:
            params["appId"] = app_id
        if branch is not None:
            params["branch"] = branch
        if tag is not None:
            params["tag"] = tag
        data = await self._get("/builds", params=params)
        all_builds = data.get("builds", [])
        total = len(all_builds)
        start = (page - 1) * limit
        end = start + limit
        page_builds = all_builds[start:end]
        return {
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "totalPages": (total + limit - 1) // limit if total > 0 else 1,
            },
            "builds": [
                {
                    "id": b.get("_id"),
                    "status": b.get("status"),
                    "branch": b.get("branch"),
                    "tag": b.get("tag"),
                    "workflowId": b.get("workflowId"),
                    "workflowName": b.get("workflowName"),
                    "appId": b.get("appId"),
                    "createdAt": b.get("createdAt"),
                    "startedAt": b.get("startedAt"),
                    "finishedAt": b.get("finishedAt"),
                }
                for b in page_builds
            ],
        }

    async def get_build(self, build_id: str, include_steps: bool = False) -> Any:
        data = await self._get(f"/builds/{build_id}")
        app = data.get("application", {})
        build = data.get("build", {})
        commit = build.get("commit", {}) or {}
        pr = build.get("pullRequest")
        actions = build.get("buildActions", [])

        from collections import Counter
        status_counts = Counter(a.get("status") for a in actions)
        steps: Any = {
            "total": len(actions),
            "success": status_counts.get("success", 0),
            "failed": status_counts.get("failed", 0),
            "skipped": status_counts.get("skipped", 0),
        }
        if include_steps:
            steps["items"] = [
                {
                    "id": a.get("_id"),
                    "name": a.get("name"),
                    "status": a.get("status"),
                }
                for a in actions
            ]

        return {
            "appName": app.get("appName"),
            "appId": app.get("_id"),
            "build": {
                "_id": build.get("_id"),
                "index": build.get("index"),
                "status": build.get("status"),
                "branch": build.get("branch"),
                "tag": build.get("tag"),
                "workflow": build.get("fileWorkflowId") or build.get("workflowId"),
                "instanceType": build.get("instanceType"),
                "startedAt": build.get("startedAt"),
                "finishedAt": build.get("finishedAt"),
                "startedBy": build.get("startedBy"),
                "message": build.get("message"),
                "commit": {
                    "author": commit.get("authorName"),
                    "message": commit.get("commitMessage"),
                    "hash": commit.get("hash"),
                },
                "pullRequest": {
                    "number": pr.get("number"),
                    "sourceBranch": pr.get("sourceBranch"),
                    "destinationBranch": pr.get("destinationBranch"),
                    "url": pr.get("url"),
                } if pr else None,
                "steps": steps,
            },
        }

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

    async def get_build_logs(self, build_id: str, statuses: list[str] | None = None) -> str:
        build_data = await self._get(f"/builds/{build_id}")
        actions = build_data.get("build", {}).get("buildActions", [])
        status_emoji = {
            "success": "✅",
            "failed": "❌",
            "skipped": "⏭",
            "canceled": "🚫",
        }
        lines = []
        for action in actions:
            status = action.get("status") or "unknown"
            if statuses and status not in statuses:
                continue
            emoji = status_emoji.get(status, "⏳")
            lines.append(f"{emoji}  {action.get('name')}")
            lines.append(f"    ID: {action.get('_id')}  status: {status}")
        return "\n".join(lines)

    async def get_step_logs(self, build_id: str, step_id: str) -> str:
        response = await self._client.get(f"/builds/{build_id}/step/{step_id}")
        response.raise_for_status()
        return response.text

    async def list_build_artifacts(self, build_id: str) -> Any:
        build = await self._get(f"/builds/{build_id}")
        artifacts = build.get("build", {}).get("artefacts", [])
        return [
            {
                "name": a.get("name"),
                "type": a.get("type"),
                "url": a.get("url"),
                "size": a.get("size"),
                "version": a.get("versionName") or a.get("version"),
                "versionCode": a.get("versionCode"),
                "minOsVersion": a.get("minOsVersion"),
            }
            for a in artifacts
        ]

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

    # Variables

    async def list_variables(self, app_id: str) -> Any:
        return await self._get(f"/apps/{app_id}/variables")

    async def add_variable(
        self,
        app_id: str,
        key: str,
        value: str,
        group: str,
        secure: bool = False,
    ) -> Any:
        return await self._post(
            f"/apps/{app_id}/variables",
            json={"key": key, "value": value, "group": group, "secure": secure},
        )

    async def update_variable(
        self,
        app_id: str,
        variable_id: str,
        key: str,
        value: str,
        group: str,
        secure: bool = False,
    ) -> Any:
        return await self._put(
            f"/apps/{app_id}/variables/{variable_id}",
            json={"key": key, "value": value, "group": group, "secure": secure},
        )

    async def delete_variable(self, app_id: str, variable_id: str) -> Any:
        return await self._delete(f"/apps/{app_id}/variables/{variable_id}")

    # Webhooks

    async def list_webhooks(self, app_id: str) -> Any:
        return await self._get(f"/apps/{app_id}/webhooks")

    async def add_webhook(self, app_id: str, url: str, events: list[str]) -> Any:
        return await self._post(
            f"/apps/{app_id}/webhooks",
            json={"url": url, "events": events},
        )

    async def delete_webhook(self, app_id: str, webhook_id: str) -> Any:
        return await self._delete(f"/apps/{app_id}/webhooks/{webhook_id}")

    # Caches

    async def list_caches(self, app_id: str) -> Any:
        return await self._get(f"/apps/{app_id}/caches")

    async def delete_all_caches(self, app_id: str) -> Any:
        return await self._delete(f"/apps/{app_id}/caches")

    async def delete_cache(self, app_id: str, cache_id: str) -> Any:
        return await self._delete(f"/apps/{app_id}/caches/{cache_id}")
