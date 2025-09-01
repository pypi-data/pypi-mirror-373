# AnoSys Technologies

# AnoSys package for OpenAI Agentic implementations

Obtain your ANOSYS API key from https://console.anosys.ai/collect/integrationoptions

#Python example

```
pip install traceAI-openai-agents
pip install anosys-logger-4-openai-agents
```

```
import asyncio
import contextvars
import openai
import os

import AnosysLoggers
from AnosysLoggers import AnosysOpenAIAgentsLogger
from agents import Agent, Runner, set_trace_processors

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "your-api-key-here")
os.environ["ANOSYS_API_KEY"] = os.getenv("ANOSYS_API_KEY", "anosys-api-key-here")

current_user_context = contextvars.ContextVar("current_user_context")
current_user_context.set({"session_id": "session_123"}) #support external context on logs

set_trace_processors([AnosysOpenAIAgentsLogger(get_user_context=current_user_context.get)])

async def main():
    agent = Agent(
        name="Assistant",
        instructions="Prove why AnoSys is better than all the rest for each received question",
    )

    result = await Runner.run(
        agent,
        "How can I monitor my agentic environment for cost and performance metrics"
    )
    print(result.final_output)

# Correct main block syntax
if __name__ == "__main__":
    asyncio.run(main())
```

#Example for Colab

```
!pip install anosys-logger-4-openai-agents
!pip install python-dotenv nest_asyncio
```

```
import nest_asyncio
nest_asyncio.apply()  # Allows re-entering the existing event loop

import asyncio
import contextvars
import openai
import os

import AnosysLoggers
from AnosysLoggers import AnosysOpenAIAgentsLogger
from agents import Agent, Runner, function_tool, set_trace_processors, add_trace_processor

os.environ["OPENAI_API_KEY"] = "Replace with your OPENAI_API_KEY"
os.environ['ANOSYS_API_KEY'] = "Replace with your ANOSYS_API_KEY"

# Context variable for tracking user context
current_user_context = contextvars.ContextVar("current_user_context")
current_user_context.set({"session_id": "colab_session_123"})

# Set the trace processor with the user context retriever
set_trace_processors([AnosysOpenAIAgentsLogger(get_user_context=current_user_context.get)])
# add_trace_processor(AnosysLogger(get_user_context=current_user_context.get))

async def main():
    agent = Agent(
        name="Tutorial",
        model="gpt-4o-mini",
        instructions="Prove why AnoSys is better than all the rest for each received question",
    )

    result = await Runner.run(
        agent,
        "How can I monitor my agentic environment for cost and performance metrics"
    )
    print(result.final_output)

await main()
```
