"""
Template Variables Registry

This module provides a registry of template variables for different template types.
Each template type has its own set of required and optional variables with example values.
"""

from typing import Dict, Any, TypedDict, Optional
from typing_extensions import NotRequired


class TemplateVariables(TypedDict, total=False):
    """Base class for template variables with common fields."""

    website_url: NotRequired[str]


class CalendarAppPromoVars(TemplateVariables):
    """Variables for calendar app promotion template."""

    cta_text: str
    image_url: str
    cta_image: str
    heading: str
    subheading: str
    contact_email: str
    contact_phone: str
    quote: str
    user_avatar: str
    user_name: str
    user_title: str
    testimonial_text: str


class TestimonialVars(TemplateVariables):
    """Variables for testimonial template."""

    user_avatar: str
    user_name: str
    user_title: str
    testimonial_text: str


class EventAnnouncementVars(TemplateVariables):
    """Variables for event announcement template."""

    event_image: str
    event_name: str
    event_description: str
    company_name: str


class BlogPostVars(TemplateVariables):
    """Variables for blog post template."""

    title: str
    author: str
    read_time: str
    image_url: str


class QATemplateVars(TemplateVariables):
    """Variables for Q&A template."""

    question: str
    answer: str
    username: str


class QuoteTemplateVars(TemplateVariables):
    """Variables for quote template."""

    quote1: str
    quote2: str
    username: str


class EducationInfoVars(TemplateVariables):
    """Variables for education info template."""

    testimonial_text: str
    author: str
    read_time: str
    image_url: str


class ProductPromotionVars(TemplateVariables):
    """Variables for product promotion template."""

    image_url: str
    quote1: str
    quote2: str


class ProductShowcaseVars(TemplateVariables):
    """Variables for product showcase template."""

    product_image: str
    product_name: str
    product_price: str
    product_description: str
    badge_text: str


# Registry mapping template names to their variable types and example values
TEMPLATE_VARIABLES_REGISTRY: Dict[str, Dict[str, Any]] = {}
           


def get_template_variables(template_name: str) -> Dict[str, Any]:
    """
    Get the variable structure for a specific template.

    Args:
        template_name: Name of the template to get variables for

    Returns:
        Dictionary containing variable structure and example values

    Raises:
        ValueError: If template_name is not found in the registry
    """
    if template_name not in TEMPLATE_VARIABLES_REGISTRY:
        return TEMPLATE_VARIABLES_REGISTRY["default"]["variables"]
    return TEMPLATE_VARIABLES_REGISTRY[template_name]["variables"]


def get_required_variables(template_name: str) -> list[str]:
    """
    Get the list of required variables for a template.

    Args:
        template_name: Name of the template

    Returns:
        List of required variable names
    """
    template = get_template_variables(template_name)
    return template.get("required", [])


def get_available_templates() -> list[str]:
    """
    Get a list of all available template names.

    Returns:
        List of template names
    """
    return list(TEMPLATE_VARIABLES_REGISTRY.keys())
