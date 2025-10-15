# pylint: disable = invalid-name
import uuid
import streamlit as st
from langchain_core.messages import HumanMessage
from agents.agent import Agent


def send_email(sender_email, receiver_email, subject, thread_id, travel_info):
    try:
        config = {'configurable': {'thread_id': thread_id}}
        # Pass email details and messages to the graph
        state = {
            'messages': [HumanMessage(content=travel_info)],
            'from_email': sender_email,
            'to_email': receiver_email,
            'email_subject': subject
        }
        st.session_state.agent.graph.invoke(state, config=config)
        st.success('✅ Email sent successfully!')
        # Clear session state
        for key in ['travel_info', 'thread_id']:
            st.session_state.pop(key, None)
    except Exception as e:
        st.error(f'❌ Error sending email: {e}')


def initialize_agent():
    if 'agent' not in st.session_state:
        st.session_state.agent = Agent()


def render_custom_css():
    st.markdown(
        '''
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        <style>
        .main-title {
            font-size: 3rem;
            font-weight: 900;
            background: linear-gradient(90deg, #3B82F6, #10B981);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 0.5rem;
            animation: fadeIn 1s ease-in-out;
        }
        .tagline {
            font-size: 1.25rem;
            color: #6B7280;
            text-align: center;
            margin-bottom: 2rem;
            font-style: italic;
        }
        .query-box textarea {
            border-radius: 0.75rem !important;
            border: 2px solid #D1D5DB !important;
            font-size: 1.125rem !important;
            padding: 1rem !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }
        .query-box textarea:focus {
            border-color: #3B82F6 !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3) !important;
        }
        .stButton>button {
            background: linear-gradient(90deg, #3B82F6, #10B981);
            color: white;
            border: none;
            padding: 0.75rem 2rem;
            border-radius: 0.75rem;
            font-size: 1.125rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #2563EB, #059669);
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        .result-box {
            background: #FFFFFF;
            border-radius: 1rem;
            padding: 2rem;
            margin-top: 2rem;
            border: 1px solid #E5E7EB;
            box-shadow: 0 10px 15px rgba(0, 0, 0, 0.05);
            animation: slideUp 0.5s ease-in-out;
        }
        .email-form {
            background: #F9FAFB;
            border-radius: 1rem;
            padding: 1.5rem;
            margin-top: 1.5rem;
            border: 1px solid #E5E7EB;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes slideUp {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        </style>
        ''', unsafe_allow_html=True)


def render_ui():
    st.markdown('<div class="main-title">✈️ AI Travel Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">Your dream vacation, planned in seconds with flights & hotels</div>', unsafe_allow_html=True)

    user_input = st.text_area(
        'Tell us about your travel plans',
        height=200,
        key='query',
        placeholder='e.g., Find flights from Kochi to Delhi next weekend with a 3-star hotel near Connaught Place',
        label_visibility="collapsed"
    )
    return user_input


def process_query(user_input):
    if user_input:
        try:
            thread_id = str(uuid.uuid4())
            st.session_state.thread_id = thread_id
            messages = [HumanMessage(content=user_input)]
            config = {'configurable': {'thread_id': thread_id}}
            state = {'messages': messages}
            result = st.session_state.agent.graph.invoke(state, config=config)

            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown('### 📍 Your Travel Plan')
            st.markdown(result['messages'][-1].content)
            st.markdown('</div>', unsafe_allow_html=True)

            st.session_state.travel_info = result['messages'][-1].content
        except Exception as e:
            st.error(f'❌ Error: {e}')
    else:
        st.warning('⚠️ Please enter a travel query.')


def render_email_form():
    st.markdown('<div class="email-form">', unsafe_allow_html=True)
    st.markdown('### 📧 Share Your Travel Plan')
    send_email_option = st.radio('Would you like to email this itinerary?', ('No', 'Yes'), horizontal=True)
    if send_email_option == 'Yes':
        with st.form(key='email_form'):
            col1, col2 = st.columns(2)
            with col1:
                sender_email = st.text_input('Your Email', placeholder='sender@example.com')
            with col2:
                receiver_email = st.text_input('Recipient Email', placeholder='receiver@example.com')
            subject = st.text_input('Email Subject', 'Your Travel Itinerary')
            submit_button = st.form_submit_button(label='🚀 Send Email')
        if submit_button:
            if sender_email and receiver_email and subject:
                send_email(sender_email, receiver_email, subject, st.session_state.thread_id, st.session_state.travel_info)
            else:
                st.error('⚠️ Please fill out all email fields.')
    st.markdown('</div>', unsafe_allow_html=True)


def main():
    initialize_agent()
    render_custom_css()
    user_input = render_ui()
    st.button('🔍 Plan My Trip', use_container_width=True)
    if st.session_state.get('query'):
        process_query(user_input)
    if 'travel_info' in st.session_state:
        render_email_form()


if __name__ == '__main__':
    main()