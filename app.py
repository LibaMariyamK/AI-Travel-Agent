import uuid
import streamlit as st
from langchain_core.messages import HumanMessage
from agents.agent import Agent

def send_email(sender_email, receiver_email, subject, thread_id, travel_info):
    try:
        config = {'configurable': {'thread_id': thread_id}}
        input_data = {
            'from_email': sender_email,
            'to_email': receiver_email,
            'email_subject': subject
        }
        with st.spinner('Sending email...'):
            st.session_state.agent.graph.invoke(input_data, config=config)
        st.success('Email sent successfully!')
        for key in ['travel_info', 'thread_id']:
            st.session_state.pop(key, None)
    except Exception as e:
        st.error(f'Error sending email: {e}')
        print(f"Email sending error: {e}")

def initialize_agent():
    if 'agent' not in st.session_state:
        st.session_state.agent = Agent()

def render_custom_css():
    st.markdown(
        '''
        <style>
        .main-title {
            font-size: 2.5em;
            color: #D3D3D3;
            text-align: center;
            margin-bottom: 0.5em;
            font-weight: bold;
        }
        .sub-title {
            font-size: 1.2em;
            color: #333;
            text-align: left;
            margin-bottom: 0.5em;
        }
        .center-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
        }
        .query-box {
            width: 80%;
            max-width: 600px;
            margin-top: 0.5em;
            margin-bottom: 1em;
        }
        .query-container {
            width: 80%;
            max-width: 600px;
            margin: 0 auto;
        }
        </style>
        ''', unsafe_allow_html=True)

def render_ui():
    st.markdown('<div class="center-container">', unsafe_allow_html=True)
    st.markdown('<div class="main-title">✈️🌍 AI Travel Agent 🏨🗺️</div>', unsafe_allow_html=True)
    st.markdown('<div class="query-container">', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Enter your travel query and get flight and hotel information:</div>', unsafe_allow_html=True)
    user_input = st.text_area(
        'Travel Query',
        height=200,
        key='query',
        placeholder='Type your travel query here...',
    )
    st.markdown('</div>', unsafe_allow_html=True)
    return user_input

def process_query(user_input):
    if user_input:
        with st.spinner('Processing your travel query...'):
            try:
                thread_id = str(uuid.uuid4())
                st.session_state.thread_id = thread_id
                messages = [HumanMessage(content=user_input)]
                config = {'configurable': {'thread_id': thread_id}}
                state = {'messages': messages}
                result = st.session_state.agent.graph.invoke(state, config=config)
                print(f"LLM Response: {result['messages'][-1].content}")
                st.subheader('Travel Information')
                st.markdown(result['messages'][-1].content)
                st.session_state.travel_info = result['messages'][-1].content
            except Exception as e:
                st.error(f'Error: {e}')
                print(f"Error details: {e}")
    else:
        st.error('Please enter a travel query.')

def render_email_form():
    send_email_option = st.radio('Do you want to send this information via email?', ('No', 'Yes'))
    if send_email_option == 'Yes':
        with st.form(key='email_form'):
            sender_email = st.text_input('Sender Email')
            receiver_email = st.text_input('Receiver Email')
            subject = st.text_input('Email Subject', 'Travel Information')
            submit_button = st.form_submit_button(label='Send Email')
        if submit_button:
            if sender_email and receiver_email and subject:
                send_email(sender_email, receiver_email, subject, st.session_state.thread_id, st.session_state.travel_info)
            else:
                st.error('Please fill out all email fields.')

def main():
    initialize_agent()
    render_custom_css()
    user_input = render_ui()
    if st.button('Get Travel Information'):
        process_query(user_input)
    if 'travel_info' in st.session_state:
        render_email_form()

if __name__ == '__main__':
    main()  
# Find 4-star hotels in Alapuzha,Kerala with check-in on November 10, 2025, and check-out on November 15, 2025.