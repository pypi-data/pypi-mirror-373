import json
from datetime import datetime
import os
import requests
from dotenv import load_dotenv  
from .tracing import setup_tracing 
from .decorator import setup_decorator, anosys_logger 

# Load environment variables from .env file
load_dotenv()
_tracing_initialized = False  # Global flag to ensure tracing setup is only run once

__all__ = [
    "AnosysOpenAILogger",
    "anosys_logger",
]

def _to_timestamp(dt_str):
    if not dt_str:
        return None
    try:
        return int(datetime.fromisoformat(dt_str).timestamp() )
    except ValueError:
        return None

def span2json(span):
    data = span.get("data", {})
    span_data = data.get("span_data", {})
    source = data.get("source")
    timestamp = span.get("timestamp")
    user_context = json.dumps(span.get("user_context", {}))

    def to_str(value):
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        return str(value)

    def clean_dict(d):
        return {k: v for k, v in d.items() if v is not None}

    base = {
        "cvs50": to_str(source),
        "cvs51": to_str(timestamp),
        "g1": _to_timestamp(timestamp),
        "cvs52": to_str(user_context),
        "cvs53": to_str(data.get("object")),
        "cvs54": to_str(data.get("id")),
        "cvs55": to_str(data.get("trace_id")),
        "cvs56": to_str(data.get("parent_id")),
        "cvs57": to_str(data.get("started_at")),
        "cvi1": _to_timestamp(data.get("started_at")),
        "cvs58": to_str(data.get("ended_at")),
        "cvi2": _to_timestamp(data.get("ended_at")),
        "cvs59": to_str(data.get("error")),
    }

    type_ = span_data.get("type")

    extended = {
        "agent": lambda: {
            "cvs61": to_str(span_data.get("name")),
            "cvs62": to_str(", ".join(span_data.get("handoffs") or [])),
            "cvs63": to_str(", ".join(span_data.get("tools") or [])),
            "cvs64": to_str(span_data.get("output_type")),
        },
        "function": lambda: {
            "cvs61": to_str(span_data.get("name")),
            "cvs65": to_str(span_data.get("input")),
            "cvs66": to_str(span_data.get("output")),
            "cvs67": to_str(span_data.get("mcp_data")),
        },
        "guardrail": lambda: {
            "cvs61": to_str(span_data.get("name")),
            "cvs68": to_str(span_data.get("triggered")),
        },
        "generation": lambda: {
            "cvs65": to_str(span_data.get("input")),
            "cvs66": to_str(span_data.get("output")),
            "cvs69": to_str(span_data.get("model")),
            "cvs70": to_str(span_data.get("model_config")),
            "cvs71": to_str(span_data.get("usage")),
        },
        "custom": lambda: {
            "cvs61": to_str(span_data.get("name")),
            "cvs72": to_str(span_data.get("data")),
        },
        "transcription": lambda: {
            "cvs72": to_str(span_data.get("input", {}).get("data")),
            "cvs73": to_str(span_data.get("input", {}).get("format")),
            "cvs66": to_str(span_data.get("output")),
            "cvs69": to_str(span_data.get("model")),
            "cvs70": to_str(span_data.get("model_config")),
        },
        "speech": lambda: {
            "cvs65": to_str(span_data.get("input")),
            "cvs72": to_str(span_data.get("output", {}).get("data")),
            "cvs73": to_str(span_data.get("output", {}).get("format")),
            "cvs69": to_str(span_data.get("model")),
            "cvs70": to_str(span_data.get("model_config")),
            "cvs74": to_str(span_data.get("first_content_at")),
        },
        "speechgroup": lambda: {
            "cvs65": to_str(span_data.get("input")),
        },
        "MCPListTools": lambda: {
            "cvs75": to_str(span_data.get("server")),
            "cvs76": to_str(span_data.get("result")),
        },
        "response": lambda: {
            "cvs77": to_str(span_data.get("response_id")),
        },
        "handoff": lambda: {
            "cvs78": to_str(span_data.get("from_agent")),
            "cvs79": to_str(span_data.get("to_agent")),
        },
    }

    result = {**base, "cvs60": to_str(type_), "cvs200": "openAI_Agents_Traces"}

    if type_ in extended:
        result.update(extended[type_]() )
    elif type_ is not None:
        raise ValueError(f"Unknown span_data type: {type_}")

    cleaned_result = clean_dict(result)
    # print(cleaned_result)
    return cleaned_result

def safe_serialize(obj):
    try:
        if isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        elif isinstance(obj, list):
            return [safe_serialize(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: safe_serialize(v) for k, v in obj.items()}
        elif hasattr(obj, "dict"):
            return safe_serialize(obj.dict())
        elif hasattr(obj, "export"):
            return safe_serialize(obj.export())
        elif hasattr(obj, "__dict__"):
            return safe_serialize(vars(obj))
        return str(obj)
    except Exception as e:
        return f"[Unserializable: {e}]"


class AnosysOpenAIAgentsLogger:
    """
    Logging utility that captures traces and spans, transforms them,
    and sends them to the Anosys API endpoint for ingestion/logging.
    """

    def __init__(self, get_user_context=None):
        global _tracing_initialized
        _tracing_initialized = False
        api_key = os.getenv('ANOSYS_API_KEY')
        if not api_key:
            print("[ERROR] ANOSYS_API_KEY not found. Please obtain your API key from https://console.anosys.ai/collect/integrationoptions")

        # retrive AnoSys url from API key and build the logging endpoint URL
        try:
            response = requests.get(f"https://api.anosys.ai/api/resolveapikeys?apikey={api_key or 'AnoSys_mock_api_key'}", timeout=30)
            response.raise_for_status()  # Raises HTTPError for bad responses (e.g., 4xx/5xx)
            data = response.json()
            self.log_api_url = data.get("url", "https://www.anosys.ai")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to resolve API key: {e}")
            self.log_api_url = "https://www.anosys.ai"

        # Optional function to provide user context (e.g., session_id, token)
        self.get_user_context = get_user_context or (lambda: None)

    def _get_session_id(self):
        """Safely retrieves the current session ID from user context."""
        try:
            user_context = self.get_user_context()
            return getattr(user_context, "session_id", "unknown_session")
        except Exception:
            return "unknown_session"

    def _get_token(self):
        """Safely retrieves the current token from user context."""
        try:
            user_context = self.get_user_context()
            return getattr(user_context, "token", None)
        except Exception:
            return None

    def _log_summary(self, data):
        """
        Logs serialized trace or span data.
        Optionally includes user context metadata.
        """
        try:
            formatted_data = json.loads(json.dumps(data, default=str))
            payload = {
                "timestamp": datetime.utcnow().isoformat(),
                "data": formatted_data,
            }

            user_context = self.get_user_context()
            if user_context:
                payload["user_context"] = {
                    "session_id": getattr(user_context, "session_id", "unknown_session"),
                    "token": getattr(user_context, "token", None),
                    "metadata": None,
                }

            # Debug print (replace with POST request in production)
            # print(self.log_api_url)
            # print(span2json(payload))
            requests.post(self.log_api_url, json=span2json(payload), timeout=5)

        except Exception as e:
            print(f"[Logger] Error logging full trace: {e}")
            print(data)

    def on_trace_start(self, trace):
        """
        Called when a trace begins. Initializes tracing if not already set up.
        """
        global _tracing_initialized
        if not _tracing_initialized:
            # print("[ANOSYS] Not initialized yet — setting up tracing")
            setup_decorator(self.log_api_url)
            setup_tracing(self.log_api_url)
            _tracing_initialized = True
        # else:
        #     print("[ANOSYS] Already initialized — skipping setup")

        serialized_data = safe_serialize(trace)
        self._log_summary({**serialized_data, "source": "on_trace_start"})

    def on_trace_end(self, trace):
        """Called when a trace ends. Logs final trace state."""
        serialized_data = safe_serialize(trace)
        self._log_summary({**serialized_data, "source": "on_trace_end"})

    def on_span_start(self, span):
        """Called when a span starts. Logs initial span data."""
        serialized_data = safe_serialize(span)
        self._log_summary({**serialized_data, "source": "on_span_start"})

    def on_span_end(self, span):
        """Called when a span ends. Logs completed span data."""
        serialized_data = safe_serialize(span)
        self._log_summary({**serialized_data, "source": "on_span_end"})

    def force_flush(self) -> None:
        """Forces flush of all queued spans and traces (no-op)."""
        pass

    def shutdown(self) -> None:
        """Graceful shutdown hook (no-op)."""
        pass
