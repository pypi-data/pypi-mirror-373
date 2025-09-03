from typing import Annotated

from pydantic import Field

from klaviyo_mcp_server.utils.utils import get_klaviyo_client, clean_result
from klaviyo_mcp_server.utils.tool_decorator import mcp_tool

HTML_PARAM_DESCRIPTION = """
The complete HTML of the template. Should include <html> and <body> tags.
To include an image, first upload the image using the upload_image_from_file or upload_image_from_url tool, then use the returned image URL.
Always include an unsubscribe link. Do this by inserting the template string "{% unsubscribe 'Unsubscribe' %}". You can replace 'Unsubscribe' with custom text.

To add an editable region to the template, ensure the has_editable_regions param is true and add the following:
<td align="center" data-klaviyo-region="true" data-klaviyo-region-width-pixels="600"></td>

To add an editable text block, add the following within that region:
<div class="klaviyo-block klaviyo-text-block">Hello world!</div>

To add an editable image block, add the following within that region:
<div class="klaviyo-block klaviyo-image-block"></div>

To add a universal content block, add the following within that region, replacing block_id with the ID of the universal content block:
<div data-klaviyo-universal-block="block_id">&nbsp;<div>
"""


@mcp_tool(has_writes=True)
def create_email_template(
    name: Annotated[str, Field(description="The name of the template")],
    html: Annotated[str, Field(description=HTML_PARAM_DESCRIPTION)],
    has_editable_regions: Annotated[
        bool,
        Field(
            description="Whether the template HTML contains editable regions. Should be false unless they explicitly request an editable/drag-and-drop/hybrid template."
        ),
    ] = False,
) -> dict:
    """Create a new email template from the given HTML. Returns the ID of the template.

    You can view and edit a template in the Klaviyo UI at https://www.klaviyo.com/email-editor/{TEMPLATE_ID}/edit."""
    body = {
        "data": {
            "type": "template",
            "attributes": {
                "name": name,
                "editor_type": "USER_DRAGGABLE" if has_editable_regions else "CODE",
                "html": html,
            },
        }
    }
    response = get_klaviyo_client().Templates.create_template(body)
    template_id = response["data"]["id"]
    return {
        "id": template_id,
    }


@mcp_tool(has_writes=False)
def get_email_template(
    template_id: Annotated[str, Field(description="The ID of the template return")],
) -> dict:
    """Get an email template with the given data. Returns attributes including the html or amp.

    You can view and edit a template in the Klaviyo UI at https://www.klaviyo.com/email-editor/{TEMPLATE_ID}/edit."""
    response = get_klaviyo_client().Templates.get_template(template_id)
    clean_result(response["data"])
    return response["data"]
