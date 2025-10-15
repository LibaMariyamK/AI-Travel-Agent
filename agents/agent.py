import datetime
import operator
import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from agents.tools.flights_finder import flights_finder
from agents.tools.hotels_finder import hotels_finder

_ = load_dotenv()

CURRENT_YEAR = datetime.datetime.now().year

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    from_email: str
    to_email: str
    email_subject: str

TOOLS_SYSTEM_PROMPT = f"""You are a smart travel agency. Use the tools to look up information.
Always return your final response in well-formatted Markdown with the following structure:
## Flights from [Origin] to [Destination]
1. **Airline Name**
   - ![Airline Logo](logo_url)
   - Departure: [details]
   - Arrival: [details]
   - Duration: [time]
   - Price: $[amount] USD
   - [Book Flight](flight_link)
## Hotels in [Location]
1. **Hotel Name**
   - ![Hotel Image](image_url)
   - Description: [brief desc]
   - Rate: $[rate] per night
   - Total: $[total]
   - Rating: [stars]/5
   - [Visit Website](hotel_website)
If no data is found, return: 'No results found for the given query.'
The current year is {CURRENT_YEAR}.
Use the tools to look up information when needed. You are allowed to make multiple calls.
Only look up information when you are sure of what you want.
Include links to hotels and flights websites and logos if possible.
Include prices and currency (USD) for flights and hotels.
"""

TOOLS = [flights_finder, hotels_finder]

EMAILS_SYSTEM_PROMPT = """Your task is to convert structured markdown-like text into a valid HTML email body.
- Do not include a ```html preamble in your response.
- The output should be in proper HTML format, ready to be used as the body of an email.
Convert markdown elements to HTML:
- ## Heading -> <h2>Heading</h2>
- **Bold** -> <strong>Bold</strong>
- 1. List -> <ol><li>...</li></ol>
- ![alt](url) -> <img src="url" alt="alt">
- [text](url) -> <a href="url">text</a>
Keep the structure clean and ensure images are displayed properly.
"""

class Agent:
    def __init__(self):
        self._tools = {t.name: t for t in TOOLS}
        self._tools_llm = ChatOllama(model='llama3.1:8b', timeout=30).bind_tools(TOOLS)

        builder = StateGraph(AgentState)
        builder.add_node('call_tools_llm', self.call_tools_llm)
        builder.add_node('invoke_tools', self.invoke_tools)
        builder.add_node('email_sender', self.email_sender)
        builder.set_entry_point('call_tools_llm')
        builder.add_conditional_edges('call_tools_llm', self.exists_action, {'more_tools': 'invoke_tools', 'email_sender': 'email_sender'})
        builder.add_edge('invoke_tools', 'call_tools_llm')
        builder.add_edge('email_sender', END)
        memory = MemorySaver()
        self.graph = builder.compile(checkpointer=memory, interrupt_before=['email_sender'])
        print(self.graph.get_graph().draw_mermaid())

    @staticmethod
    def exists_action(state: AgentState):
        result = state['messages'][-1]
        print(f"Tool calls: {result.tool_calls}")
        if len(result.tool_calls) == 0:
            return 'email_sender'
        return 'more_tools'

    def email_sender(self, state: AgentState):
        print('Sending email')
        email_llm = ChatOllama(model='llama3.1:8b', temperature=0.1)
        email_message = [SystemMessage(content=EMAILS_SYSTEM_PROMPT), HumanMessage(content=state['messages'][-1].content)]
        try:
            email_response = email_llm.invoke(email_message)
            print(f'Email content: {email_response.content}')
            html_content = email_response.content
            message = Mail(
                from_email=state['from_email'],
                to_emails=state['to_email'],
                subject=state['email_subject'],
                html_content=html_content
            )
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(f"SendGrid response: {response.status_code}")
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            html_content = f"Error sending email: {str(e)}"
        return {'messages': [HumanMessage(content=html_content)]}

    def call_tools_llm(self, state: AgentState):
        messages = state['messages']
        messages = [SystemMessage(content=TOOLS_SYSTEM_PROMPT)] + messages
        from langchain_core.runnables import RunnableConfig  # Add this import at the top if missing
        config = RunnableConfig(recursion_limit=5)  # Limit to 5 iterations
        message = self._tools_llm.invoke(messages, config=config)
        return {'messages': [message]}

    def invoke_tools(self, state: AgentState):
        tool_calls = state['messages'][-1].tool_calls
        results = []
        for t in tool_calls:
            print(f'Calling tool: {t["name"]} with args: {t["args"]}')
            if t['name'] not in self._tools:
                print(f'Invalid tool name: {t["name"]}')
                result = 'Invalid tool name, retry'
            else:
                try:
                    result = self._tools[t['name']].invoke(t['args'])
                except Exception as e:
                    result = f"Tool {t['name']} failed: {str(e)}"
                print(f"Tool result: {result}")
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
        return {'messages': results}