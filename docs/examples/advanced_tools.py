"""
Advanced Tool Development Example

This example demonstrates how to create sophisticated custom tools
with proper type validation, error handling, and advanced features.
"""

from unisonai.tools.tool import BaseTool, Field
from unisonai.tools.types import ToolParameterType
import json
import requests
from typing import Dict, List, Optional
import statistics

class WeatherTool(BaseTool):
    """Advanced weather tool with comprehensive features."""

    def __init__(self):
        self.name = "weather_tool"
        self.description = "Get detailed weather information for any location"
        self.params = [
            Field(
                name="location",
                description="City name or coordinates (e.g., 'New York' or '40.7128,-74.0060')",
                field_type=ToolParameterType.STRING,
                required=True
            ),
            Field(
                name="units",
                description="Temperature units ('celsius', 'fahrenheit')",
                field_type=ToolParameterType.STRING,
                default_value="celsius",
                required=False
            ),
            Field(
                name="include_forecast",
                description="Include 5-day weather forecast",
                field_type=ToolParameterType.BOOLEAN,
                default_value=False,
                required=False
            ),
            Field(
                name="details",
                description="Level of detail ('basic', 'detailed', 'comprehensive')",
                field_type=ToolParameterType.STRING,
                default_value="basic",
                required=False
            )
        ]
        super().__init__()

    def _run(self, location: str, units: str = "celsius",
             include_forecast: bool = False, details: str = "basic") -> Dict:
        """Get weather information for the specified location."""

        # Simulate API call (replace with actual weather API)
        weather_data = self._get_weather_data(location)

        if details == "basic":
            result = {
                "location": location,
                "temperature": weather_data["current"]["temp"],
                "condition": weather_data["current"]["condition"],
                "humidity": weather_data["current"]["humidity"]
            }
        elif details == "detailed":
            result = weather_data["current"]
            result["location"] = location
        else:  # comprehensive
            result = weather_data

        if include_forecast and "forecast" in weather_data:
            result["forecast"] = weather_data["forecast"]

        return result

    def _get_weather_data(self, location: str) -> Dict:
        """Simulate weather API call."""
        # In a real implementation, this would call a weather API
        return {
            "current": {
                "temp": 22.5,
                "condition": "Partly Cloudy",
                "humidity": 65,
                "wind_speed": 12,
                "pressure": 1013
            },
            "forecast": [
                {"day": "Monday", "high": 25, "low": 18, "condition": "Sunny"},
                {"day": "Tuesday", "high": 23, "low": 16, "condition": "Cloudy"},
                {"day": "Wednesday", "high": 26, "low": 19, "condition": "Rainy"}
            ]
        }

class DataAnalysisTool(BaseTool):
    """Advanced data analysis tool with statistical operations."""

    def __init__(self):
        self.name = "data_analyzer"
        self.description = "Perform comprehensive statistical analysis on datasets"
        self.params = [
            Field(
                name="data",
                description="List of numerical values to analyze",
                field_type=ToolParameterType.LIST,
                required=True
            ),
            Field(
                name="operations",
                description="Statistical operations to perform",
                field_type=ToolParameterType.LIST,
                default_value=["mean", "median", "std_dev"],
                required=False
            ),
            Field(
                name="precision",
                description="Number of decimal places for results",
                field_type=ToolParameterType.INTEGER,
                default_value=2,
                required=False
            ),
            Field(
                name="include_outliers",
                description="Include outlier detection in analysis",
                field_type=ToolParameterType.BOOLEAN,
                default_value=True,
                required=False
            )
        ]
        super().__init__()

    def _run(self, data: List[float], operations: Optional[List[str]] = None,
             precision: int = 2, include_outliers: bool = True) -> Dict:
        """Perform statistical analysis on the provided data."""

        if operations is None:
            operations = ["mean", "median", "std_dev"]

        results = {}

        try:
            # Basic statistics
            if "mean" in operations:
                results["mean"] = round(statistics.mean(data), precision)

            if "median" in operations:
                results["median"] = round(statistics.median(data), precision)

            if "mode" in operations:
                try:
                    results["mode"] = statistics.mode(data)
                except statistics.StatisticsError:
                    results["mode"] = "No unique mode found"

            if "std_dev" in operations:
                results["standard_deviation"] = round(statistics.stdev(data), precision)

            if "variance" in operations:
                results["variance"] = round(statistics.variance(data), precision)

            # Additional metrics
            results["count"] = len(data)
            results["min"] = min(data)
            results["max"] = max(data)
            results["range"] = max(data) - min(data)
            results["sum"] = sum(data)

            # Outlier detection
            if include_outliers:
                outliers = self._detect_outliers(data)
                results["outliers"] = outliers
                results["outlier_count"] = len(outliers)

        except Exception as e:
            results["error"] = f"Analysis failed: {str(e)}"

        return results

    def _detect_outliers(self, data: List[float]) -> List[float]:
        """Detect outliers using IQR method."""
        if len(data) < 4:
            return []

        sorted_data = sorted(data)
        q1 = statistics.median(sorted_data[:len(sorted_data)//2])
        q3 = statistics.median(sorted_data[-(len(sorted_data)//2):])
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        return [x for x in data if x < lower_bound or x > upper_bound]

class APITool(BaseTool):
    """Tool for making HTTP API calls with proper error handling."""

    def __init__(self):
        self.name = "api_caller"
        self.description = "Make HTTP requests to external APIs"
        self.params = [
            Field(
                name="url",
                description="API endpoint URL",
                field_type=ToolParameterType.STRING,
                required=True
            ),
            Field(
                name="method",
                description="HTTP method (GET, POST, PUT, DELETE)",
                field_type=ToolParameterType.STRING,
                default_value="GET",
                required=False
            ),
            Field(
                name="headers",
                description="HTTP headers as dictionary",
                field_type=ToolParameterType.DICT,
                default_value={},
                required=False
            ),
            Field(
                name="data",
                description="Request body data",
                field_type=ToolParameterType.DICT,
                default_value=None,
                required=False
            )
        ]
        super().__init__()

    def _run(self, url: str, method: str = "GET",
             headers: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to the specified API."""

        if headers is None:
            headers = {}

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text,
                "json": response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            }

        except requests.RequestException as e:
            return {
                "error": f"Request failed: {str(e)}",
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
        except Exception as e:
            return {
                "error": f"Unexpected error: {str(e)}"
            }

# Example usage and testing
def test_advanced_tools():
    """Test the advanced tools."""

    print("🛠️  Advanced Tools Testing")
    print("=" * 50)

    # Test weather tool
    print("\n🌤️  Testing Weather Tool:")
    weather_tool = WeatherTool()

    try:
        result = weather_tool.run(
            location="New York",
            units="fahrenheit",
            include_forecast=True,
            details="comprehensive"
        )
        print(f"✅ Weather result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ Weather tool error: {e}")

    # Test data analysis tool
    print("\n📊 Testing Data Analysis Tool:")
    analysis_tool = DataAnalysisTool()

    test_data = [1, 5, 2, 8, 3, 9, 15, 12, 7, 4, 100]  # Includes outlier

    try:
        result = analysis_tool.run(
            data=test_data,
            operations=["mean", "median", "std_dev", "outliers"],
            precision=3
        )
        print(f"✅ Analysis result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ Analysis tool error: {e}")

    # Test API tool
    print("\n🌐 Testing API Tool:")
    api_tool = APITool()

    try:
        result = api_tool.run(
            url="https://httpbin.org/json",
            method="GET",
            headers={"User-Agent": "UnisonAI-Tool/1.0"}
        )
        print(f"✅ API result: Status {result.get('status_code', 'Unknown')}")
    except Exception as e:
        print(f"❌ API tool error: {e}")

if __name__ == "__main__":
    test_advanced_tools()
