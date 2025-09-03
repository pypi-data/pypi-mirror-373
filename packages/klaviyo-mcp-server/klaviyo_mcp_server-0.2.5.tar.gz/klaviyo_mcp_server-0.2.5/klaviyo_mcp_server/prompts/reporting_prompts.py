from typing import Annotated

from fastmcp.prompts.prompt import PromptMessage, TextContent
from klaviyo_mcp_server.server import mcp
from pydantic import Field


@mcp.prompt
def analyze_campaign_or_flow_anomalies(
    report_type: Annotated[
        str,
        Field(description="Report types include: [campaign, flow]"),
    ],
    timeframe: Annotated[str, Field(description="The timeframe to analyze")],
    refine_prompt: Annotated[
        str,
        Field(
            description="Ask for specific channels, tags, or other details for analysis"
        ),
    ] = "",
) -> PromptMessage:
    """Prompt for analyzing spikes, dips, and other anomalies in campaign or flow performance data."""

    return PromptMessage(
        role="user",
        content=TextContent(
            type="text",
            text=f"""You are a marketing analytics expert analyzing Klaviyo {report_type} performance data.

Analyze {report_type} data over the timeframe: {timeframe}.

{refine_prompt}

When analyzing {report_type} reports, follow this structured approach. If any prior information is unclear, ask the user for clarification.

IMPORTANT EXTRA DETAILS:

--------------------------------

# Important Details
- **ALWAYS** use {report_type} names in final output; IDs only for internal tool calls. This is crucial for understanding.
- Prioritize actionable insights over descriptive statistics
- Include the timeframe in the request always, prioritize using preset timeframes over custom timeframes if possible.
- If possible, visualize the data in a chart or graph.
- Use emojis in headers to make the output more engaging

# Tool calls
- Start with get_metrics to identify available metrics for the timeframe
    - Apply channel filters (email/SMS) only when user specifies channel preference
- Use get_campaign_report_by_id to get the name for a specific campaign
- Use get_flow_report_by_id to get the name for a specific flow
- **Map {report_type} IDs to names**: After retrieving data, ensure that all {report_type} IDs are mapped to their corresponding names before presenting the analysis.

# Analysis Structure
## Header: {report_type} Performance Analysis for {timeframe}

## 1. Performance Overview
- Start with key metrics: delivery rate, open rate, click rate, conversion rate
- Look for rates or metrics from the {report_type}s which differ from the rest of the data substantially.
- Identify top 3 performers and bottom 3 performers with specific percentage differences

## 2. Event Analysis
- Identify spikes and dips in the data
- Provide a detailed analysis of the events that caused the spikes or drops, list the specific {report_type} names that experienced the spike or drop, and which metric was experiencing the spike or drop.
- Provide recommendations for optimizing the {report_type}s to address the drop or build on the spike
- Put it into larger context of the timeframe it is in

## 3. Conclusion
- Summarize the findings
- Provide recommendations for optimizing the data
""",
        ),
    )
