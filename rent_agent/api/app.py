"""REST API for Rent Prediction Agent with FastAPI and fallback HTTP server."""

import json
from typing import Dict, Any, Optional
from rent_agent.agent.core import RentPredictionAgent
from rent_agent.config import CITY_METRICS

agent_instance = RentPredictionAgent()

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field

    app = FastAPI(
        title="ApexRent AI - Rent Prediction Agent API",
        description="Machine learning valuation engine and autonomous rental market advisory agent.",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class PropertyInput(BaseModel):
        city: str = Field(default="Chicago", description="Metropolitan city name")
        neighborhood: Optional[str] = Field(default=None, description="Neighborhood name")
        property_type: str = Field(default="Apartment", description="Apartment, Condo, Townhouse, etc.")
        bedrooms: int = Field(default=2, ge=0, le=10)
        bathrooms: float = Field(default=1.5, ge=1.0, le=10.0)
        sqft: int = Field(default=950, ge=200, le=15000)
        year_built: int = Field(default=2015, ge=1850, le=2026)
        condition: str = Field(default="Standard / Well Maintained")
        amenities: Dict[str, bool] = Field(default_factory=dict)
        walk_score: int = Field(default=75, ge=0, le=100)
        transit_score: int = Field(default=70, ge=0, le=100)

    class ChatInput(BaseModel):
        message: str = Field(..., description="User question or prompt for the AI agent")

    class RoiInput(BaseModel):
        purchase_price: float = Field(..., ge=10000)
        monthly_rent: float = Field(..., ge=100)
        down_payment_pct: float = Field(default=0.20, ge=0.0, le=1.0)
        monthly_hoa: float = Field(default=250.0, ge=0.0)
        interest_rate: float = Field(default=0.065, ge=0.0, le=0.25)

    @app.get("/")
    def health_check():
        return {
            "status": "online",
            "service": "ApexRent AI Agent",
            "version": "1.0.0",
            "supported_cities": list(CITY_METRICS.keys()),
        }

    @app.post("/predict")
    def predict_rent(property_data: PropertyInput):
        specs = property_data.dict()
        result = agent_instance.tools.predict_rent(specs)
        return result

    @app.post("/agent/chat")
    def agent_chat(chat_data: ChatInput):
        reply = agent_instance.chat(chat_data.message)
        return {"response": reply}

    @app.post("/comps")
    def find_comps(property_data: PropertyInput, top_k: int = 5):
        specs = property_data.dict()
        comps = agent_instance.tools.find_comparables(specs, top_k=top_k)
        return {"comparables": comps}

    @app.post("/roi")
    def calculate_roi(roi_data: RoiInput):
        return agent_instance.tools.calculate_roi(
            purchase_price=roi_data.purchase_price,
            monthly_rent=roi_data.monthly_rent,
            down_payment_pct=roi_data.down_payment_pct,
            monthly_hoa=roi_data.monthly_hoa,
            interest_rate=roi_data.interest_rate,
        )

    @app.get("/trends/{city}")
    def get_trends(city: str):
        summary = agent_instance.tools.get_market_trends(city)
        if "error" in summary:
            raise HTTPException(status_code=404, detail=summary["error"])
        return summary

except ImportError:
    # Lightweight standard library HTTP server fallback
    app = None


def run_simple_server(port: int = 8000):
    """Run built-in zero-dependency HTTP server if FastAPI is not installed."""
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class SimpleHandler(BaseHTTPRequestHandler):
        def _set_headers(self, status=200):
            self.send_response(status)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def do_OPTIONS(self):
            self._set_headers(200)

        def do_GET(self):
            if self.path == "/" or self.path == "/health":
                self._set_headers(200)
                resp = {
                    "status": "online",
                    "mode": "standalone_simple_http",
                    "supported_cities": list(CITY_METRICS.keys()),
                }
                self.wfile.write(json.dumps(resp).encode())
            elif self.path.startswith("/trends/"):
                city = self.path.split("/")[-1].replace("%20", " ")
                summary = agent_instance.tools.get_market_trends(city)
                self._set_headers(200 if "error" not in summary else 404)
                self.wfile.write(json.dumps(summary).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Not Found"}).encode())

        def do_POST(self):
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len).decode()
            try:
                data = json.loads(post_body) if post_body else {}
            except Exception:
                data = {}

            if self.path == "/predict":
                result = agent_instance.tools.predict_rent(data)
                self._set_headers(200)
                self.wfile.write(json.dumps(result).encode())
            elif self.path == "/agent/chat":
                msg = data.get("message", "")
                reply = agent_instance.chat(msg)
                self._set_headers(200)
                self.wfile.write(json.dumps({"response": reply}).encode())
            elif self.path == "/comps":
                comps = agent_instance.tools.find_comparables(data, top_k=5)
                self._set_headers(200)
                self.wfile.write(json.dumps({"comparables": comps}).encode())
            elif self.path == "/roi":
                res = agent_instance.tools.calculate_roi(
                    purchase_price=float(data.get("purchase_price", 350000)),
                    monthly_rent=float(data.get("monthly_rent", 2200)),
                )
                self._set_headers(200)
                self.wfile.write(json.dumps(res).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())

    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    print(f"ApexRent AI HTTP Server running at http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    if app:
        import uvicorn
        uvicorn.run("rent_agent.api.app:app", host="0.0.0.0", port=8000, reload=True)
    else:
        run_simple_server(8000)
