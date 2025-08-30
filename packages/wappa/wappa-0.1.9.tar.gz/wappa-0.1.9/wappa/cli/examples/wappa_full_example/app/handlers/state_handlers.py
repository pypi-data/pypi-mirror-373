"""
State handlers for interactive features in the Wappa Full Example application.

This module provides handlers for managing interactive states like button and list
selections, including state validation, response processing, and cleanup.
"""

import time
from typing import Dict

from wappa.webhooks import IncomingMessageWebhook

from ..models.state_models import ButtonState, ListState, StateType
from ..models.user_models import UserProfile
from ..utils.cache_utils import CacheHelper
from ..utils.media_handler import send_local_media_file
from ..utils.metadata_extractor import MetadataExtractor


class StateHandlers:
    """Collection of handlers for interactive state management."""
    
    def __init__(self, messenger, cache_factory, logger):
        """
        Initialize state handlers.
        
        Args:
            messenger: IMessenger instance for sending messages
            cache_factory: Cache factory for data persistence
            logger: Logger instance
        """
        self.messenger = messenger
        self.cache_helper = CacheHelper(cache_factory)
        self.logger = logger
    
    async def handle_button_state_response(self, webhook: IncomingMessageWebhook, 
                                          user_profile: UserProfile,
                                          button_state: ButtonState) -> Dict[str, any]:
        """
        Handle response when user is in button state.
        
        Args:
            webhook: IncomingMessageWebhook with user input
            user_profile: User profile for tracking
            button_state: Active button state
            
        Returns:
            Result dictionary with operation status
        """
        try:
            start_time = time.time()
            
            user_id = webhook.user.user_id
            message_id = webhook.message.message_id
            message_type = webhook.get_message_type_name()
            
            self.logger.info(f"🔘 Processing button state response from {user_id}")
            
            # Check if this is an interactive button selection
            if message_type == "interactive":
                selection_id = webhook.get_interactive_selection()
                
                if button_state.is_valid_selection(selection_id):
                    # Valid button selection - process it
                    return await self._process_button_selection(
                        webhook, user_profile, button_state, selection_id, start_time
                    )
                else:
                    # Invalid selection
                    await self._send_invalid_button_selection_message(user_id, message_id, selection_id)
                    button_state.increment_attempts()
                    await self.cache_helper.save_user_state(button_state)
                    
                    return {
                        "success": False,
                        "error": "Invalid button selection",
                        "selection_id": selection_id,
                        "attempts": button_state.attempts
                    }
            else:
                # Non-interactive message while in button state - send reminder
                await self._send_button_state_reminder(user_id, message_id, button_state)
                button_state.increment_attempts()
                await self.cache_helper.save_user_state(button_state)
                
                return {
                    "success": False,
                    "error": "Expected button selection",
                    "message_type": message_type,
                    "reminder_sent": True,
                    "attempts": button_state.attempts
                }
        
        except Exception as e:
            self.logger.error(f"❌ Error handling button state response: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def handle_list_state_response(self, webhook: IncomingMessageWebhook, 
                                        user_profile: UserProfile,
                                        list_state: ListState) -> Dict[str, any]:
        """
        Handle response when user is in list state.
        
        Args:
            webhook: IncomingMessageWebhook with user input
            user_profile: User profile for tracking
            list_state: Active list state
            
        Returns:
            Result dictionary with operation status
        """
        try:
            start_time = time.time()
            
            user_id = webhook.user.user_id
            message_id = webhook.message.message_id
            message_type = webhook.get_message_type_name()
            
            self.logger.info(f"📋 Processing list state response from {user_id}")
            
            # Check if this is an interactive list selection
            if message_type == "interactive":
                selection_id = webhook.get_interactive_selection()
                
                if list_state.is_valid_selection(selection_id):
                    # Valid list selection - process it
                    return await self._process_list_selection(
                        webhook, user_profile, list_state, selection_id, start_time
                    )
                else:
                    # Invalid selection
                    await self._send_invalid_list_selection_message(user_id, message_id, selection_id)
                    list_state.increment_attempts()
                    await self.cache_helper.save_user_state(list_state)
                    
                    return {
                        "success": False,
                        "error": "Invalid list selection",
                        "selection_id": selection_id,
                        "attempts": list_state.attempts
                    }
            else:
                # Non-interactive message while in list state - send reminder
                await self._send_list_state_reminder(user_id, message_id, list_state)
                list_state.increment_attempts()
                await self.cache_helper.save_user_state(list_state)
                
                return {
                    "success": False,
                    "error": "Expected list selection",
                    "message_type": message_type,
                    "reminder_sent": True,
                    "attempts": list_state.attempts
                }
        
        except Exception as e:
            self.logger.error(f"❌ Error handling list state response: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def _process_button_selection(self, webhook: IncomingMessageWebhook,
                                       user_profile: UserProfile, button_state: ButtonState,
                                       selection_id: str, start_time: float) -> Dict[str, any]:
        """Process valid button selection."""
        user_id = webhook.user.user_id
        message_id = webhook.message.message_id
        
        # Handle the selection in the state
        button_state.handle_selection(selection_id)
        selected_button = button_state.get_selected_button()
        
        # Remove state from cache
        await self.cache_helper.remove_user_state(user_id, StateType.BUTTON)
        
        # Extract and format metadata
        metadata = MetadataExtractor.extract_metadata(webhook, start_time)
        metadata_text = MetadataExtractor.format_metadata_for_user(metadata)
        
        # Send metadata response
        await self.messenger.send_text(
            recipient=user_id,
            text=metadata_text,
            reply_to_message_id=message_id
        )
        
        # Send corresponding media file based on selection
        media_sent = False
        media_file = None
        
        if selection_id == "kitty":
            media_file = "kitty.png"
        elif selection_id == "puppy":
            media_file = "puppy.png"
        
        if media_file:
            media_result = await send_local_media_file(
                messenger=self.messenger,
                recipient=user_id,
                filename=media_file,
                media_subdir="buttons",
                caption=f"Here's your {selection_id}! 🎉"
            )
            media_sent = media_result["success"]
            
            if not media_sent:
                # Send fallback text if media fails
                fallback_text = f"🎉 You selected: *{selected_button['title']}*\n\n(Media file not found: {media_file})"
                await self.messenger.send_text(
                    recipient=user_id,
                    text=fallback_text
                )
        
        # Send completion message
        completion_text = (
            f"✅ *Button Selection Complete!*\n\n"
            f"🎯 *Your choice*: {selected_button['title']}\n"
            f"🆔 *Selection ID*: `{selection_id}`\n"
            f"⏱️ *Response time*: {int((time.time() - start_time) * 1000)}ms\n"
            f"🗑️ *State cleaned up*: Button state removed\n\n"
            f"💡 *What happened*: You successfully clicked a button, received metadata, "
            f"and got your chosen animal {'image' if media_sent else '(image failed to load)'}!"
        )
        
        await self.messenger.send_text(
            recipient=user_id,
            text=completion_text
        )
        
        # Update user activity
        await self.cache_helper.update_user_activity(user_id, "interactive", interaction_type="button")
        
        processing_time = int((time.time() - start_time) * 1000)
        self.logger.info(f"✅ Button selection processed in {processing_time}ms")
        
        return {
            "success": True,
            "selection_type": "button",
            "selection_id": selection_id,
            "selected_button": selected_button,
            "metadata_sent": True,
            "media_sent": media_sent,
            "media_file": media_file,
            "state_cleaned": True,
            "processing_time_ms": processing_time
        }
    
    async def _process_list_selection(self, webhook: IncomingMessageWebhook,
                                     user_profile: UserProfile, list_state: ListState,
                                     selection_id: str, start_time: float) -> Dict[str, any]:
        """Process valid list selection."""
        user_id = webhook.user.user_id
        message_id = webhook.message.message_id
        
        # Handle the selection in the state
        list_state.handle_selection(selection_id)
        selected_item = list_state.get_selected_item()
        
        # Remove state from cache
        await self.cache_helper.remove_user_state(user_id, StateType.LIST)
        
        # Extract and format metadata
        metadata = MetadataExtractor.extract_metadata(webhook, start_time)
        metadata_text = MetadataExtractor.format_metadata_for_user(metadata)
        
        # Send metadata response
        await self.messenger.send_text(
            recipient=user_id,
            text=metadata_text,
            reply_to_message_id=message_id
        )
        
        # Send corresponding media file based on selection
        media_sent = False
        media_file = None
        media_type = None
        
        # Map selection to media file
        if selection_id == "image_file":
            media_file = "image.png"
            media_type = "image"
        elif selection_id == "video_file":
            media_file = "video.mp4"
            media_type = "video"
        elif selection_id == "audio_file":
            media_file = "audio.mp3"
            media_type = "audio"
        elif selection_id == "document_file":
            media_file = "document.pdf"
            media_type = "document"
        
        if media_file and media_type:
            media_result = await send_local_media_file(
                messenger=self.messenger,
                recipient=user_id,
                filename=media_file,
                media_subdir="list",
                caption=f"Here's your {media_type} file! 🎉"
            )
            media_sent = media_result["success"]
            
            if not media_sent:
                # Send fallback text if media fails
                fallback_text = f"🎉 You selected: *{selected_item['title']}*\n\n(Media file not found: {media_file})"
                await self.messenger.send_text(
                    recipient=user_id,
                    text=fallback_text
                )
        
        # Send completion message
        completion_text = (
            f"✅ *List Selection Complete!*\n\n"
            f"🎯 *Your choice*: {selected_item['title']}\n"
            f"📝 *Description*: {selected_item.get('description', 'N/A')}\n"
            f"🆔 *Selection ID*: `{selection_id}`\n"
            f"📁 *Media type*: {media_type}\n"
            f"⏱️ *Response time*: {int((time.time() - start_time) * 1000)}ms\n"
            f"🗑️ *State cleaned up*: List state removed\n\n"
            f"💡 *What happened*: You successfully selected from a list, received metadata, "
            f"and got your chosen {media_type} {'file' if media_sent else '(file failed to load)'}!"
        )
        
        await self.messenger.send_text(
            recipient=user_id,
            text=completion_text
        )
        
        # Update user activity
        await self.cache_helper.update_user_activity(user_id, "interactive", interaction_type="list")
        
        processing_time = int((time.time() - start_time) * 1000)
        self.logger.info(f"✅ List selection processed in {processing_time}ms")
        
        return {
            "success": True,
            "selection_type": "list",
            "selection_id": selection_id,
            "selected_item": selected_item,
            "metadata_sent": True,
            "media_sent": media_sent,
            "media_file": media_file,
            "media_type": media_type,
            "state_cleaned": True,
            "processing_time_ms": processing_time
        }
    
    async def _send_button_state_reminder(self, user_id: str, message_id: str, 
                                         button_state: ButtonState) -> None:
        """Send reminder message when user is in button state."""
        time_remaining = button_state.time_remaining_minutes()
        
        reminder_text = (
            f"🔘 *Hey Wappa! We love your enthusiasm, but please press a button!*\n\n"
            f"⚠️ *You're currently in Button Demo mode*\n"
            f"📋 *Expected action*: Click one of the buttons above\n"
            f"⏰ *Time remaining*: {time_remaining} minutes\n"
            f"🔢 *Attempt*: {button_state.attempts + 1}/{button_state.max_attempts}\n\n"
            f"💡 *Tip*: Look for the message with 🐱 Kitty and 🐶 Puppy buttons above!"
        )
        
        await self.messenger.send_text(
            recipient=user_id,
            text=reminder_text,
            reply_to_message_id=message_id
        )
    
    async def _send_list_state_reminder(self, user_id: str, message_id: str, 
                                       list_state: ListState) -> None:
        """Send reminder message when user is in list state."""
        time_remaining = list_state.time_remaining_minutes()
        
        reminder_text = (
            f"📋 *Hey Wappa! We love your enthusiasm, but please make a list selection!*\n\n"
            f"⚠️ *You're currently in List Demo mode*\n"
            f"📋 *Expected action*: Tap 'Choose Media' and select an option\n"
            f"⏰ *Time remaining*: {time_remaining} minutes\n"
            f"🔢 *Attempt*: {list_state.attempts + 1}/{list_state.max_attempts}\n\n"
            f"💡 *Tip*: Look for the message with the 'Choose Media' button above!"
        )
        
        await self.messenger.send_text(
            recipient=user_id,
            text=reminder_text,
            reply_to_message_id=message_id
        )
    
    async def _send_invalid_button_selection_message(self, user_id: str, message_id: str, 
                                                   selection_id: str) -> None:
        """Send message for invalid button selection."""
        error_text = (
            f"❌ *Invalid Button Selection*\n\n"
            f"🆔 *You selected*: `{selection_id}`\n"
            f"✅ *Valid options*: `kitty`, `puppy`\n\n"
            f"💡 *Please try again*: Click one of the valid buttons above!"
        )
        
        await self.messenger.send_text(
            recipient=user_id,
            text=error_text,
            reply_to_message_id=message_id
        )
    
    async def _send_invalid_list_selection_message(self, user_id: str, message_id: str, 
                                                  selection_id: str) -> None:
        """Send message for invalid list selection."""
        error_text = (
            f"❌ *Invalid List Selection*\n\n"
            f"🆔 *You selected*: `{selection_id}`\n"
            f"✅ *Valid options*: `image_file`, `video_file`, `audio_file`, `document_file`\n\n"
            f"💡 *Please try again*: Use the list above to make a valid selection!"
        )
        
        await self.messenger.send_text(
            recipient=user_id,
            text=error_text,
            reply_to_message_id=message_id
        )


# Convenience functions for direct use
async def handle_user_in_state(webhook: IncomingMessageWebhook, user_profile: UserProfile,
                              messenger, cache_factory, logger) -> Dict[str, any]:
    """
    Handle user response when they are in an active state (convenience function).
    
    Args:
        webhook: IncomingMessageWebhook with user response
        user_profile: User profile for tracking
        messenger: IMessenger instance
        cache_factory: Cache factory
        logger: Logger instance
        
    Returns:
        Result dictionary or None if no active state
    """
    handlers = StateHandlers(messenger, cache_factory, logger)
    cache_helper = CacheHelper(cache_factory)
    user_id = webhook.user.user_id
    
    # Check for active button state
    button_state = await cache_helper.get_user_state(user_id, StateType.BUTTON)
    if button_state and button_state.is_active():
        # Ensure we have the correct type
        if isinstance(button_state, ButtonState):
            return await handlers.handle_button_state_response(webhook, user_profile, button_state)
        else:
            logger.warning(f"Button state returned wrong type: {type(button_state)}")
    
    # Check for active list state
    list_state = await cache_helper.get_user_state(user_id, StateType.LIST)
    if list_state and list_state.is_active():
        # Ensure we have the correct type
        if isinstance(list_state, ListState):
            return await handlers.handle_list_state_response(webhook, user_profile, list_state)
        else:
            logger.warning(f"List state returned wrong type: {type(list_state)}")
    
    # No active state found
    return None


async def cleanup_expired_user_states(cache_factory, logger, user_id: str = None) -> int:
    """
    Cleanup expired states for a specific user or all users (convenience function).
    
    Args:
        cache_factory: Cache factory
        logger: Logger instance
        user_id: Optional specific user ID to clean up
        
    Returns:
        Number of states cleaned up
    """
    cache_helper = CacheHelper(cache_factory)
    
    try:
        # This is a simplified cleanup - in a real implementation you would
        # scan Redis keys and clean up expired states
        cleanup_count = 0
        
        if user_id:
            # Clean up specific user's states
            for state_type in [StateType.BUTTON, StateType.LIST]:
                state = await cache_helper.get_user_state(user_id, state_type)
                if state and state.is_expired():
                    await cache_helper.remove_user_state(user_id, state_type)
                    cleanup_count += 1
                    logger.info(f"🧹 Cleaned up expired {state_type.value} state for user {user_id}")
        
        return cleanup_count
    
    except Exception as e:
        logger.error(f"❌ Error during state cleanup: {e}")
        return 0