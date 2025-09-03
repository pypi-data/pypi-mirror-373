import os
import json
import httpx
from typing import Any, Dict
from .models import MemoryCreate, SearchQuery

class SovantError(Exception):
    def __init__(self, message: str, code: str, status: int | None = None, details: Any | None = None):
        super().__init__(message)
        self.code = code
        self.status = status
        self.details = details

class Sovant:
    def __init__(self, api_key: str | None = None, base_url: str | None = None, timeout: float = 30.0):
        self.api_key = api_key or os.getenv("SOVANT_API_KEY")
        if not self.api_key:
            raise ValueError("Missing api_key")
        self.base_url = (base_url or os.getenv("SOVANT_BASE_URL") or "https://sovant.ai").rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(
            timeout=self.timeout,
            headers={
                "authorization": f"Bearer {self.api_key}",
                "content-type": "application/json"
            }
        )

    def _handle(self, r: httpx.Response):
        if r.status_code >= 400:
            try:
                body = r.json()
            except Exception:
                body = {"message": r.text}
            msg = body.get("message") or r.reason_phrase
            code = body.get("code") or f"HTTP_{r.status_code}"
            raise SovantError(msg, code, r.status_code, body)
        if not r.text:
            return None
        try:
            return r.json()
        except Exception:
            return r.text

    def memory_create(self, create: MemoryCreate):
        # Convert data field to content field for API
        body = create.model_dump()
        if 'data' in body:
            body['content'] = json.dumps(body.pop('data')) if not isinstance(body.get('data'), str) else body.pop('data')
        
        # Ensure type has a default
        if 'type' not in body or body['type'] is None:
            body['type'] = 'journal'
            
        r = self._client.post(f"{self.base_url}/api/v1/memory", content=json.dumps(body))
        return self._handle(r)

    def memory_get(self, id: str):
        r = self._client.get(f"{self.base_url}/api/v1/memories/{id}")
        return self._handle(r)

    def memory_search(self, q: SearchQuery):
        params = {}
        if q.query:
            params['query'] = q.query
        if q.type:
            params['type'] = q.type
        if q.tags:
            params['tags'] = ','.join(q.tags)
        if q.thread_id:
            params['thread_id'] = q.thread_id
        if q.limit:
            params['limit'] = str(q.limit)
        if q.from_date:
            params['from_date'] = q.from_date
        if q.to_date:
            params['to_date'] = q.to_date
        r = self._client.get(f"{self.base_url}/api/v1/memory/search", params=params)
        return self._handle(r)

    def memory_update(self, id: str, patch: Dict[str, Any]):
        # Convert data field to content field if present
        if 'data' in patch:
            patch['content'] = json.dumps(patch.pop('data')) if not isinstance(patch.get('data'), str) else patch.pop('data')
        r = self._client.patch(f"{self.base_url}/api/v1/memories/{id}", content=json.dumps(patch))
        return self._handle(r)

    def memory_delete(self, id: str):
        r = self._client.delete(f"{self.base_url}/api/v1/memories/{id}")
        return self._handle(r)