"""Cadence AI Streamlit UI Application.

This module provides a Streamlit-based web interface for interacting with the
Cadence AI multi-agent framework. It includes chat functionality, plugin management,
and system monitoring capabilities.
"""

import os
from typing import Any, Dict

import streamlit as st


def get_api_base_url() -> str:
    """Get the API base URL from environment variables."""
    return os.environ.get("CADENCE_API_BASE_URL", "http://localhost:8000")


def get_default_user_config() -> Dict[str, str]:
    """Get default user configuration from environment variables."""
    return {
        "user_id": os.environ.get("CADENCE_DEFAULT_USER_ID", "anonymous"),
        "org_id": os.environ.get("CADENCE_DEFAULT_ORG_ID", "public"),
    }


def main():
    """Main Streamlit application entry point."""
    st.set_page_config(
        page_title="Cadence AI Framework", page_icon="🤖", layout="wide", initial_sidebar_state="expanded"
    )

    st.title("🤖 Cadence AI Framework")
    st.markdown("A plugin-based multi-agent conversational AI framework")

    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")

        # API configuration
        api_url = st.text_input("API Base URL", value=get_api_base_url(), help="Base URL for the Cadence API")

        # User configuration
        user_config = get_default_user_config()
        user_id = st.text_input("User ID", value=user_config["user_id"])
        org_id = st.text_input("Organization ID", value=user_config["org_id"])

        # Plugin management
        st.header("Plugins")
        if st.button("Refresh Plugins"):
            st.info("Plugin refresh functionality coming soon!")

    # Main content area
    tab1, tab2, tab3 = st.tabs(["Chat", "Plugins", "System"])

    with tab1:
        st.header("Chat Interface")
        st.info("Chat functionality coming soon!")

        # Chat input
        user_input = st.text_area("Your message:", height=100)
        if st.button("Send"):
            if user_input:
                st.success(f"Message sent: {user_input}")
            else:
                st.warning("Please enter a message")

    with tab2:
        st.header("Plugin Management")
        st.info("Plugin management interface coming soon!")

        # Plugin list placeholder
        st.subheader("Available Plugins")
        plugins = [
            {"name": "Math Agent", "status": "Active", "description": "Mathematical calculations"},
            {"name": "Search Agent", "status": "Active", "description": "Web search capabilities"},
            {"name": "Info Agent", "status": "Inactive", "description": "General information"},
        ]

        for plugin in plugins:
            with st.expander(f"{plugin['name']} - {plugin['status']}"):
                st.write(plugin["description"])
                if plugin["status"] == "Active":
                    st.success("Plugin is running")
                else:
                    st.error("Plugin is not running")

    with tab3:
        st.header("System Status")
        st.info("System monitoring coming soon!")

        # System status
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("API Status", "🟢 Online")
            st.metric("Active Plugins", "2")

        with col2:
            st.metric("Memory Usage", "45%")
            st.metric("CPU Usage", "12%")

        with col3:
            st.metric("Active Sessions", "5")
            st.metric("Total Requests", "1,234")


if __name__ == "__main__":
    main()
