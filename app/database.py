import httpx
from typing import Optional, Any
from app.config import get_settings

settings = get_settings()


class SupabaseResponse:
    """Response wrapper"""
    def __init__(self, data: list, count: Optional[int] = None):
        self.data = data
        self.count = count


class TableQuery:
    """Query builder for Supabase REST API"""
    
    def __init__(self, base_url: str, headers: dict, table: str):
        self.base_url = f"{base_url}/{table}"
        self.headers = headers.copy()
        self.query_params = {}
        self._method = "GET"
        self._body = None
    
    def select(self, columns: str = "*", count: str = None):
        self.query_params["select"] = columns
        if count:
            self.headers["Prefer"] = f"count={count}"
        return self
    
    def eq(self, column: str, value: Any):
        self.query_params[column] = f"eq.{value}"
        return self
    
    def neq(self, column: str, value: Any):
        self.query_params[column] = f"neq.{value}"
        return self
    
    def ilike(self, column: str, pattern: str):
        self.query_params[column] = f"ilike.{pattern}"
        return self
    
    def or_(self, conditions: str):
        self.query_params["or"] = f"({conditions})"
        return self
    
    def order(self, column: str, desc: bool = False):
        direction = "desc" if desc else "asc"
        self.query_params["order"] = f"{column}.{direction}"
        return self
    
    def limit(self, count: int):
        self.query_params["limit"] = str(count)
        return self
    
    def range(self, start: int, end: int):
        self.headers["Range"] = f"{start}-{end}"
        return self
    
    def insert(self, data: dict):
        self._method = "POST"
        self._body = data
        self.headers["Prefer"] = "return=representation"
        return self
    
    def update(self, data: dict):
        self._method = "PATCH"
        self._body = data
        self.headers["Prefer"] = "return=representation"
        return self
    
    def delete(self):
        self._method = "DELETE"
        self.headers["Prefer"] = "return=representation"
        return self
    
    def execute(self) -> SupabaseResponse:
        """Execute the query"""
        with httpx.Client(timeout=30.0) as client:
            if self._method == "GET":
                response = client.get(
                    self.base_url,
                    headers=self.headers,
                    params=self.query_params
                )
            elif self._method == "POST":
                response = client.post(
                    self.base_url,
                    headers=self.headers,
                    params=self.query_params,
                    json=self._body
                )
            elif self._method == "PATCH":
                response = client.patch(
                    self.base_url,
                    headers=self.headers,
                    params=self.query_params,
                    json=self._body
                )
            elif self._method == "DELETE":
                response = client.delete(
                    self.base_url,
                    headers=self.headers,
                    params=self.query_params
                )
            
            # Error handling
            if response.status_code >= 400:
                error_detail = response.text
                raise Exception(f"Database error: {response.status_code} - {error_detail}")
            
            # Parse response
            data = response.json() if response.text else []
            
            # Get count from header if available
            count = None
            content_range = response.headers.get("content-range")
            if content_range:
                try:
                    count = int(content_range.split("/")[-1])
                except:
                    count = len(data)
            
            return SupabaseResponse(data=data, count=count)


class SupabaseClient:
    """Simple Supabase client using REST API"""
    
    def __init__(self):
        self.base_url = f"{settings.supabase_url}/rest/v1"
        self.headers = {
            "apikey": settings.supabase_key,
            "Authorization": f"Bearer {settings.supabase_key}",
            "Content-Type": "application/json"
        }
    
    def from_(self, table: str) -> TableQuery:
        return TableQuery(self.base_url, self.headers, table)
    
    def table(self, table: str) -> TableQuery:
        """Alias for from_"""
        return self.from_(table)


# Global client instance
db_client = SupabaseClient()