# ------ poke the server.py mcp tools to see if it's working ------
import asyncio, inspect
from smolagents import ToolCollection
from mcp import StdioServerParameters

def pick_tool(tc: ToolCollection, name: str):
    return next(t for t in tc.tools if t.name == name)

async def call_tool(tool, payload: dict):
    # Try common async/sync entrypoints across smolagents versions
    if hasattr(tool, "arun"):
        return await tool.arun(payload)
    if hasattr(tool, "ainvoke"):
        return await tool.ainvoke(payload)
    if hasattr(tool, "acall"):
        return await tool.acall(payload)
    if hasattr(tool, "__call__"):
        res = tool(payload)
        return await res if inspect.isawaitable(res) else res
    if hasattr(tool, "run"):
        return tool.run(payload)
    raise TypeError(f"Don't know how to call tool {getattr(tool,'name',tool)}; methods: {dir(tool)}")

async def main():
    params = StdioServerParameters(command="python3", args=["server.py"])

    # In your version, from_mcp returns a *sync* context manager
    with ToolCollection.from_mcp(params, trust_remote_code=True) as tc:
        print("TOOLS:", [t.name for t in tc.tools])

        get_user_profile = pick_tool(tc, "get_user_profile")
        profile = await call_tool(get_user_profile, {"user_id": "USER_001"})
        print("PROFILE:", profile)

        list_matching_jobs = pick_tool(tc, "list_matching_jobs")
        matches = await call_tool(list_matching_jobs, {"user_id": "USER_001", "limit": 3})
        print("MATCHES:", matches)

        # Example: auto-apply (will succeed only if USER_001 is pro)
        # auto_apply = pick_tool(tc, "auto_apply_five")
        # applied = await call_tool(auto_apply, {"user_id": "USER_001", "min_score": 70})
        # print("AUTO_APPLY:", applied)

if __name__ == "__main__":
    asyncio.run(main())
