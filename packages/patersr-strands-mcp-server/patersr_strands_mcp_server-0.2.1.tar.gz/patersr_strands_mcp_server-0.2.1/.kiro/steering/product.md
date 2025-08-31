# Product Overview

This project is for creating a Python MCP Server (https://github.com/modelcontextprotocol and https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#overview) compatible with Amazon Q Developer or Kiro Agentic IDE for assisting in the development of LLM agents with the Strands Agent SDK framework (https://github.com/strands-agents/samples and https://github.com/strands-agents/sdk-python and https://github.com/strands-agents/docs/tree/main).

I want the MCP Server to be able to search an indexed set of the latest Strands SDK documents. You need to trade off currency of the documents with efficiency of not having to check for changes on every single call. Checking periodically such as nightly, the first time the server is started on a day or even weekly should do.

The MCP Server should be able to set up a brand new Strands project upon request. It should be able to detect if Strands is installed, if it's the latest version that is installed, it should be able to configure a directory for basic Strands operations, it should request information such as the preferred AWS region and model ID string. If these information aren't displayed it should prompt the user with the information of what defaults are going to be used. When a Model ID string is supplied you should use awscli to check for that model's availability with the currently available AWS credentials, and you should lookup and inform the user of the currently active inference requests per second quota limits for the proposed Model ID string.

The MCP Server should be able to determine from the users requests the most appropriate starting sample code to implement. For example, the MCP Server should understand the various Multi Agent patterns available (these should be determined from the documentation's Multi Agent section). 

The agent should understand the Strands SDK Observability and Evaluation techniques and be able to guide querying of these tools to help resolve problems with a Strands SDK project. 

The MCP server should also understand the considerations and requirements for deployment of a Strands SDK into various production environments (as determined from the "Deploy" section of the Strands SDK documentation.)


## Key Principles
- Maintain clean, readable code
- Follow established conventions consistently
- Prioritize security and best practices
- Document important decisions and architecture choices

## Development Approach
- This project will use `uv` for dependency management.
- Start with minimal viable implementations
- Iterate based on requirements
- Keep dependencies lean and purposeful