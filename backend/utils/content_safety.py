# backend/utils/content_safety.py
"""
Content Safety Utilities for Children's Storybook
Filters inappropriate content and ensures child-safe image generation
"""

import re
from typing import Tuple


class ContentSafetyFilter:
    """Filters and validates content for child safety"""
    
    # Explicit/inappropriate keywords to block
    BLOCKED_KEYWORDS = [
        # Explicit content
        'nude', 'naked', 'nsfw', 'explicit', 'sexual', 'sexy', 'erotic',
        'porn', 'xxx', 'adult', 'mature', 'provocative', 'seductive',
        # Violence
        'blood', 'gore', 'violent', 'brutal', 'murder', 'kill', 'death',
        'weapon', 'gun', 'knife', 'sword', 'fight', 'war', 'battle',
        # Inappropriate themes
        'drug', 'alcohol', 'cigarette', 'smoking', 'drinking',
        'horror', 'scary', 'terrifying', 'nightmare', 'demon', 'evil',
        # Deformity-related
        'deformed', 'mutated', 'grotesque', 'disfigured', 'distorted',
    ]
    
    # Warning keywords (allowed but need stronger negative prompts)
    WARNING_KEYWORDS = [
        'monster', 'creature', 'beast', 'dragon', 'witch', 'ghost',
        'dark', 'shadow', 'night', 'mysterious',
    ]
    
    @staticmethod
    def filter_prompt(prompt: str) -> Tuple[str, bool, str]:
        """
        Filter prompt for inappropriate content
        
        Returns:
            (filtered_prompt, is_safe, warning_message)
        """
        prompt_lower = prompt.lower()
        
        # Check for blocked keywords
        for keyword in ContentSafetyFilter.BLOCKED_KEYWORDS:
            if keyword in prompt_lower:
                return (
                    "",
                    False,
                    f"Prompt contains inappropriate content: '{keyword}'. Please use child-friendly descriptions."
                )
        
        # Check for warning keywords
        needs_extra_safety = False
        for keyword in ContentSafetyFilter.WARNING_KEYWORDS:
            if keyword in prompt_lower:
                needs_extra_safety = True
                break
        
        # Clean up prompt (don't modify it - let IP-Adapter work naturally)
        filtered = prompt.strip()
        
        # Safety is enforced through negative prompts, not by modifying the positive prompt
        # This preserves facial likeness while still blocking inappropriate content
        
        return (filtered, True, "extra_safety" if needs_extra_safety else "")
    
    @staticmethod
    def get_child_safe_negative_prompt(extra_safety: bool = False) -> str:
        """
        Get comprehensive negative prompt for child-safe image generation
        
        Args:
            extra_safety: If True, adds extra negative prompts for darker themes
        """
        base_negative = (
            # Explicit content
            "nsfw, nude, naked, explicit, sexual, adult content, mature, provocative, "
            "inappropriate, suggestive, revealing clothing, "
            # Violence & scary
            "blood, gore, violence, weapon, gun, knife, sword, scary, horror, terrifying, "
            "nightmare, demon, evil, dark magic, "
            # Quality issues
            "deformed, disfigured, mutated, mutation, extra limbs, missing limbs, "
            "extra fingers, missing fingers, fused fingers, too many fingers, "
            "bad anatomy, bad proportions, gross proportions, malformed limbs, "
            "extra arms, extra legs, missing arms, missing legs, "
            "bad hands, poorly drawn hands, poorly drawn face, "
            "ugly, duplicate, morbid, mutilated, "
            "out of frame, extra fingers, mutated hands, "
            "poorly drawn eyes, cloned face, malformed, "
            # Technical issues
            "blurry, bad quality, low quality, worst quality, lowres, "
            "jpeg artifacts, watermark, signature, username, text, error, "
            "cropped, out of frame, "
            # Inappropriate themes
            "drugs, alcohol, smoking, cigarette, beer, wine, "
            "disturbing, creepy, unsettling"
        )
        
        if extra_safety:
            # Add extra negatives for darker themes
            extra_negative = (
                "monster, creature, beast, witch, ghost, zombie, skeleton, "
                "darkness, shadows, night scene, gloomy, ominous, threatening, "
                "sinister, menacing, aggressive"
            )
            return base_negative + ", " + extra_negative
        
        return base_negative
    
    @staticmethod
    def get_child_safe_positive_additions() -> str:
        """Get positive prompt additions to encourage child-friendly content"""
        return (
            "child-friendly, wholesome, innocent, cheerful, happy, bright colors, "
            "safe for children, age-appropriate, family-friendly, cute, adorable, "
            "joyful, playful, colorful, vibrant, clean, pure"
        )
    
    @staticmethod
    def validate_scene_description(description: str) -> Tuple[bool, str]:
        """
        Validate a scene description for child safety
        
        Returns:
            (is_safe, error_message)
        """
        _, is_safe, warning = ContentSafetyFilter.filter_prompt(description)
        
        if not is_safe:
            return False, warning
        
        # Check for overly complex or inappropriate scenarios
        if len(description.split()) > 100:
            return False, "Scene description too complex. Please simplify for better results."
        
        return True, ""


def enhance_prompt_for_children(prompt: str) -> Tuple[str, str, bool]:
    """
    Enhance prompt for child-safe image generation
    
    Returns:
        (enhanced_positive_prompt, negative_prompt, is_safe)
    """
    # Filter prompt
    filtered_prompt, is_safe, warning = ContentSafetyFilter.filter_prompt(prompt)
    
    if not is_safe:
        return "", "", False
    
    # Build enhanced positive prompt
    positive_additions = ContentSafetyFilter.get_child_safe_positive_additions()
    enhanced_positive = f"{positive_additions}, {filtered_prompt}"
    
    # Build negative prompt
    extra_safety = (warning == "extra_safety")
    negative_prompt = ContentSafetyFilter.get_child_safe_negative_prompt(extra_safety)
    
    return enhanced_positive, negative_prompt, True
