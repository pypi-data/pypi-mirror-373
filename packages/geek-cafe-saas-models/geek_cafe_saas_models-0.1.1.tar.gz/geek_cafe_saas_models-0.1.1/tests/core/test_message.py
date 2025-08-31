import pytest
from datetime import datetime
from geek_cafe_saas_models.core.messages.message import Message
from geek_cafe_saas_models.core.messages.channel import MessageChannel


class TestMessage:
    def test_message_creation(self):
        """Test basic message creation with new fields"""
        message = Message()
        
        # Test basic fields
        message.content = "Hello, world!"
        message.sender_id = "user123"
        message.channel_id = "channel456"
        message.message_type = "text"
        
        assert message.content == "Hello, world!"
        assert message.sender_id == "user123"
        assert message.channel_id == "channel456"
        assert message.message_type == "text"
        assert message.is_deleted is False
        assert message.reply_to_message_id is None
        assert message.thread_id is None
        assert message.edited_at is None

    def test_message_threading(self):
        """Test message threading functionality"""
        parent_message = Message()
        parent_message.content = "Original message"
        parent_message.sender_id = "user123"
        parent_message.channel_id = "channel456"
        
        reply_message = Message()
        reply_message.content = "Reply to original"
        reply_message.sender_id = "user789"
        reply_message.channel_id = "channel456"
        reply_message.reply_to_message_id = parent_message.id
        reply_message.thread_id = parent_message.id
        
        assert reply_message.reply_to_message_id == parent_message.id
        assert reply_message.thread_id == parent_message.id

    def test_message_editing(self):
        """Test message editing functionality"""
        message = Message()
        message.content = "Original content"
        message.sender_id = "user123"
        
        # Simulate editing
        edit_time = datetime.now()
        message.content = "Edited content"
        message.edited_at = edit_time
        
        assert message.content == "Edited content"
        assert message.edited_at == edit_time

    def test_message_types(self):
        """Test different message types"""
        text_message = Message()
        text_message.message_type = "text"
        text_message.content = "Hello"
        
        file_message = Message()
        file_message.message_type = "file"
        file_message.content = "file_url_here"
        
        system_message = Message()
        system_message.message_type = "system"
        system_message.content = "User joined the channel"
        
        assert text_message.message_type == "text"
        assert file_message.message_type == "file"
        assert system_message.message_type == "system"


class TestMessageChannel:
    def test_channel_creation(self):
        """Test message channel creation with new fields"""
        channel = MessageChannel()
        
        channel.name = "Property Discussion"
        channel.owner_id = "user123"
        channel.description = "Discussion about 123 Main St"
        channel.channel_type = "property"
        channel.is_private = True
        
        assert channel.name == "Property Discussion"
        assert channel.owner_id == "user123"
        assert channel.description == "Discussion about 123 Main St"
        assert channel.channel_type == "property"
        assert channel.is_private is True

    def test_channel_types(self):
        """Test different channel types"""
        discussion_channel = MessageChannel()
        discussion_channel.channel_type = "discussion"
        
        property_channel = MessageChannel()
        property_channel.channel_type = "property"
        
        project_channel = MessageChannel()
        project_channel.channel_type = "project"
        
        assert discussion_channel.channel_type == "discussion"
        assert property_channel.channel_type == "property"
        assert project_channel.channel_type == "project"

    def test_channel_privacy(self):
        """Test channel privacy settings"""
        public_channel = MessageChannel()
        public_channel.is_private = False
        
        private_channel = MessageChannel()
        private_channel.is_private = True
        
        assert public_channel.is_private is False
        assert private_channel.is_private is True
