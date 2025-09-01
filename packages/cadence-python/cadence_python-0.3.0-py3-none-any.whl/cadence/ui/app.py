"""Cadence AI Streamlit UI Application.

This module provides a Streamlit-based web interface for interacting with the
Cadence AI multi-agent framework. It includes chat functionality, plugin management,
and system monitoring capabilities.
"""

import os
import streamlit as st
from typing import Dict, Any
import time
import uuid

from .client import CadenceApiClient, ChatResult, PluginInfo, SystemStatus


def get_api_base_url() -> str:
    """Get the API base URL from environment variables."""
    return os.environ.get("CADENCE_API_BASE_URL", "http://localhost:8000")


def get_default_user_config() -> Dict[str, str]:
    """Get default user configuration from environment variables."""
    return {
        "user_id": os.environ.get("CADENCE_DEFAULT_USER_ID", "anonymous"),
        "org_id": os.environ.get("CADENCE_DEFAULT_ORG_ID", "public"),
    }


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    if "client" not in st.session_state:
        st.session_state.client = None
    if "system_status" not in st.session_state:
        st.session_state.system_status = None
    if "plugins" not in st.session_state:
        st.session_state.plugins = []


def create_client(api_url: str) -> CadenceApiClient:
    """Create and return a new API client instance."""
    return CadenceApiClient(api_url)


def send_chat_message(client: CadenceApiClient, message: str, user_id: str, org_id: str) -> ChatResult:
    """Send a chat message and return the response."""
    try:
        result = client.chat(
            message=message,
            thread_id=st.session_state.thread_id,
            user_id=user_id,
            org_id=org_id,
            tone="natural"
        )
        return result
    except Exception as e:
        st.error(f"Error sending message: {str(e)}")
        return None


def load_plugins(client: CadenceApiClient) -> list[PluginInfo]:
    """Load available plugins from the API."""
    try:
        return client.get_plugins()
    except Exception as e:
        st.error(f"Error loading plugins: {str(e)}")
        return []


def load_system_status(client: CadenceApiClient) -> SystemStatus:
    """Load system status from the API."""
    try:
        return client.get_system_status()
    except Exception as e:
        st.error(f"Error loading system status: {str(e)}")
        return None


def reload_plugins(client: CadenceApiClient) -> Dict[str, Any]:
    """Reload all plugins."""
    try:
        return client.reload_plugins()
    except Exception as e:
        st.error(f"Error reloading plugins: {str(e)}")
        return {}


def main():
    """Main Streamlit application entry point."""
    st.set_page_config(
        page_title="Cadence AI Framework",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    st.title("🤖 Cadence AI Framework")
    st.markdown("A plugin-based multi-agent conversational AI framework")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        
        # API configuration
        api_url = st.text_input(
            "API Base URL",
            value=get_api_base_url(),
            help="Base URL for the Cadence API"
        )
        
        # User configuration
        user_config = get_default_user_config()
        user_id = st.text_input("User ID", value=user_config["user_id"])
        org_id = st.text_input("Organization ID", value=user_config["org_id"])
        
        # Create client when API URL changes
        if st.session_state.client is None or st.session_state.client.base_url != api_url:
            st.session_state.client = create_client(api_url)
        
        # Plugin management
        st.header("Plugins")
        if st.button("🔄 Refresh Plugins"):
            with st.spinner("Refreshing plugins..."):
                result = reload_plugins(st.session_state.client)
                if result:
                    st.success("Plugins reloaded successfully!")
                    st.session_state.plugins = load_plugins(st.session_state.client)
                else:
                    st.error("Failed to reload plugins")
        
        # Load plugins on first load
        if not st.session_state.plugins:
            with st.spinner("Loading plugins..."):
                st.session_state.plugins = load_plugins(st.session_state.client)
        
        # Display plugins in sidebar
        if st.session_state.plugins:
            st.subheader("Available Plugins")
            for plugin in st.session_state.plugins:
                status_color = "🟢" if plugin.status == "healthy" else "🔴"
                st.write(f"{status_color} {plugin.name} ({plugin.status})")
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "🔌 Plugins", "📊 System"])
    
    with tab1:
        st.header("Chat Interface")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Type your message here..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Display assistant response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                with st.spinner("Thinking..."):
                    # Send message to API
                    result = send_chat_message(st.session_state.client, prompt, user_id, org_id)
                    
                    if result:
                        # Update session state with thread and conversation IDs
                        if result.thread_id:
                            st.session_state.thread_id = result.thread_id
                        if result.conversation_id:
                            st.session_state.conversation_id = result.conversation_id
                        
                        # Add assistant response to chat history
                        st.session_state.messages.append({"role": "assistant", "content": result.response})
                        
                        # Display the response
                        message_placeholder.markdown(result.response)
                        
                        # Show metadata if available
                        if result.metadata:
                            with st.expander("Response Metadata"):
                                st.json(result.metadata)
                    else:
                        message_placeholder.error("Failed to get response from the API")
    
    with tab2:
        st.header("Plugin Management")
        
        if st.session_state.plugins:
            # Plugin list
            st.subheader("Available Plugins")
            
            for plugin in st.session_state.plugins:
                with st.expander(f"{plugin.name} v{plugin.version} - {plugin.status}"):
                    st.write(f"**Description:** {plugin.description}")
                    st.write(f"**Status:** {plugin.status}")
                    st.write(f"**Capabilities:** {', '.join(plugin.capabilities)}")
                    
                    # Status indicator
                    if plugin.status == "healthy":
                        st.success("✅ Plugin is running")
                    else:
                        st.error("❌ Plugin has issues")
        else:
            st.info("No plugins available. Try refreshing the plugins.")
    
    with tab3:
        st.header("System Status")
        
        # Load system status
        if st.button("🔄 Refresh Status"):
            with st.spinner("Loading system status..."):
                st.session_state.system_status = load_system_status(st.session_state.client)
        
        # Load status on first load
        if st.session_state.system_status is None:
            with st.spinner("Loading system status..."):
                st.session_state.system_status = load_system_status(st.session_state.client)
        
        if st.session_state.system_status:
            # System status metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                status_icon = "🟢" if st.session_state.system_status.status == "operational" else "🔴"
                st.metric("System Status", f"{status_icon} {st.session_state.system_status.status}")
            
            with col2:
                st.metric("Available Plugins", len(st.session_state.system_status.available_plugins))
            
            with col3:
                st.metric("Healthy Plugins", len(st.session_state.system_status.healthy_plugins))
            
            with col4:
                st.metric("Failed Plugins", len(st.session_state.system_status.failed_plugins))
            
            # Detailed status
            st.subheader("Plugin Status Details")
            
            # Available plugins
            if st.session_state.system_status.available_plugins:
                st.write("**Available Plugins:**")
                for plugin in st.session_state.system_status.available_plugins:
                    if plugin in st.session_state.system_status.healthy_plugins:
                        st.write(f"✅ {plugin}")
                    elif plugin in st.session_state.system_status.failed_plugins:
                        st.write(f"❌ {plugin}")
                    else:
                        st.write(f"⚠️ {plugin}")
            
            # Session information
            st.subheader("Session Information")
            st.metric("Total Sessions", st.session_state.system_status.total_sessions)
            
            if st.session_state.thread_id:
                st.write(f"**Current Thread ID:** {st.session_state.thread_id}")
            if st.session_state.conversation_id:
                st.write(f"**Current Conversation ID:** {st.session_state.conversation_id}")
        else:
            st.error("Failed to load system status")


if __name__ == "__main__":
    main()
