import asyncio
import gtm_agent

async def main():
    await (gtm_agent.start("/Users/rosamii1/opllm-generic-agents/sample/sample.csv"))

if __name__ == "__main__":
    asyncio.run(main())