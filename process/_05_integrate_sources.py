"""
This part of the script attempts to reattach links to sources where relevant.

It takes the generated response of the websearch enabled AI assistant
and a list of sources (urls) that were used to provide contextual inforamtion for the response.
The script tries to match the urls with the relevant segments of the output.

*Note*: This approach is chose to avoid hallucinations in the generation 
of links to source material.
"""

