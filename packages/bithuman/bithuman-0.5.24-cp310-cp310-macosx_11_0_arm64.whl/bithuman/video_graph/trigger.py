from __future__ import annotations

import json
from typing import List, Literal, Optional

from loguru import logger
from pydantic import BaseModel, Field


class TriggerData(BaseModel):
    """Data to be sent when a trigger is activated"""

    target_video: Optional[str] = None
    actions: List[str] | str = Field(default_factory=list)
    description: str = ""


class VideoActionTrigger(BaseModel):
    """Base class for video action triggers"""

    trigger_data: TriggerData = Field(
        description="Data to be sent when trigger conditions are met"
    )

    def check_trigger(self, condition: any) -> Optional[TriggerData]:
        """
        Base method to check if trigger conditions are met
        Args:
            condition: The condition to check against (type varies by trigger type)
        Returns:
            TriggerData if triggered, None otherwise
        """
        return None

    @classmethod
    def from_json(cls, json_str: str) -> List["VideoActionTrigger"]:
        """
        Create KeywordTrigger instances from JSON string using Pydantic validation
        Args:
            json_str: JSON string containing trigger configurations
        Returns:
            List of validated KeywordTrigger instances
        """
        if not json_str:
            return []
        try:
            triggers_data = json.loads(json_str)
            return [
                cls.model_validate_json(json.dumps(trigger))
                for trigger in triggers_data
            ]
        except Exception as e:
            logger.exception(f"Error parsing KeywordTrigger: {e}")
            return []


class KeywordTrigger(VideoActionTrigger):
    """Trigger that activates when specific keywords are detected"""

    keywords: List[str] = Field(
        description="List of keywords that can trigger this action"
    )
    trigger_source: Literal["user", "agent", "both"] = Field(
        default="both", description="Who can trigger this action - user, agent, or both"
    )

    def check_trigger(
        self, text: str, source: Literal["user", "agent"]
    ) -> Optional[TriggerData]:
        """
        Check if the given text and source triggers this keyword
        Args:
            text: The text to check
            source: The source of the text - either "user" or "agent"
        Returns:
            TriggerData if triggered, None otherwise
        """
        if self.trigger_source != "both" and source != self.trigger_source:
            return None

        if any(keyword.lower() in text.lower() for keyword in self.keywords):
            return self.trigger_data
        return None


if __name__ == "__main__":
    triggers = KeywordTrigger.from_json(
        '[{"keywords": ["goodbye", "bye"], "trigger_source": "user", "trigger_data": {"target_video": null, "actions": "wave", "description": "Wave animation"}}]',  # noqa: E501
    )
    print(triggers)
