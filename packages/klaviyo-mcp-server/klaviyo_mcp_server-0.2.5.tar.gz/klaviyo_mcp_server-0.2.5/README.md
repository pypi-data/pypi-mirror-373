# Klaviyo MCP Server (Beta)

The Klaviyo [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) server integrates with [Klaviyo's APIs](https://developers.klaviyo.com/en/reference/api_overview), allowing you to interact with your Klaviyo data using a variety of MCP clients. For a detailed guide on how to set up and use this server, see our [Klaviyo MCP server guide](https://developers.klaviyo.com/en/docs/klaviyo_mcp_server).

> [!WARNING]
> The Klaviyo MCP server is currently in beta and is subject to change. Please provide any feedback using [this form](https://docs.google.com/forms/d/e/1FAIpQLSday2sqDvxfoRxjLrhROYZtxivRfHF151tcXV7o-ZYGF2SipQ/viewform?usp=header).

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- A compatible MCP client (e.g., Cursor). Note: This server runs locally, so web-based clients such as ChatGPT are not supported at this time.

## Quickstart

### Create a Klaviyo private API key<a id="create-a-klaviyo-private-key"></a>

To utilize all [available tools](#available-tools), create a [Klaviyo private API key](https://developers.klaviyo.com/en/docs/authenticate_#create-a-private-key) with the following permissions:

| Scope         | Access |
| ------------- | ------ |
| Accounts      | Read   |
| Campaigns     | Full   |
| Catalogs      | Read   |
| Events        | Full   |
| Flows         | Read   |
| Images        | Full   |
| List          | Read   |
| Metrics       | Read   |
| Profiles      | Full   |
| Segments      | Full   |
| Subscriptions | Full   |
| Tags          | Read   |
| Templates     | Full   |

### Install [uv](https://docs.astral.sh/uv/getting-started/installation/)<a id="install-uv"></a>

For macOS and Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For Windows:

```bat
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Add the server to your MCP client<a id="add-the-server-to-your-mcp-client"></a>

For guidance on securely configuring your MCP client, refer to our [Klaviyo MCP server guide](https://developers.klaviyo.com/en/docs/klaviyo_mcp_server).

## Available tools<a id="available-tools"></a>

| Category  | Tool name                             | Description                                                        |
| --------- | ------------------------------------- | ------------------------------------------------------------------ |
| Accounts  | `get_account_details`                 | Get details of your account.                                       |
| Campaigns | `get_campaigns`                       | List your campaigns.                                               |
| Campaigns | `get_campaign`                        | Get details of a campaign.                                         |
| Campaigns | `create_campaign`                     | Create a campaign.                                                 |
| Campaigns | `assign_template_to_campaign_message` | Assign an email template to a campaign message.                    |
| Catalogs  | `get_catalog_items`                   | List your catalog items.                                           |
| Events    | `get_events`                          | List events.                                                       |
| Events    | `create_event`                        | Create an event for a profile.                                     |
| Events    | `get_metrics`                         | List event metrics.                                                |
| Events    | `get_metric`                          | Get details of an event metric.                                    |
| Flows     | `get_flows`                           | List your flows.                                                   |
| Flows     | `get_flow`                            | Get details of a flow.                                             |
| Groups    | `get_lists`                           | List your lists.                                                   |
| Groups    | `get_list`                            | Get details of a list.                                             |
| Groups    | `get_segments`                        | List your segments.                                                |
| Groups    | `get_segment`                         | Get details of a segment.                                          |
| Images    | `upload_image_from_file`              | Upload image from a local file.                                    |
| Images    | `upload_image_from_url`               | Upload image from a URL.                                           |
| Profiles  | `get_profiles`                        | List your profiles.                                                |
| Profiles  | `get_profile`                         | Get details of a profile.                                          |
| Profiles  | `create_profile`                      | Create a profile.                                                  |
| Profiles  | `update_profile`                      | Update a profile.                                                  |
| Profiles  | `subscribe_profile_to_marketing`      | Subscribe a profile to marketing for a given channel and list.     |
| Profiles  | `unsubscribe_profile_from_marketing`  | Unsubscribe a profile from marketing for a given channel and list. |
| Reporting | `get_campaign_report`                 | Get a report of your campaign performance.                         |
| Reporting | `get_flow_report`                     | Get a report of your flow performance.                             |
| Templates | `create_email_template`               | Create an HTML email template.                                     |
| Templates | `get_email_template`                  | Get the details of an email template.                              |
