import re

from pydantic import BaseModel
from typing import Optional
from .anthropic_component import get_sonnet35_response, get_haiku35_response
from .perplexity_component import get_sonar_pro_response, get_sonar_response, PerplexityResponse

class PitchDeckSection(BaseModel):
    raw_content: str
    analysis: Optional[PerplexityResponse] = None

class PitchDeckAnalysis(BaseModel):
    problem_statement: PitchDeckSection
    market_opportunity: PitchDeckSection
    technical_approach: PitchDeckSection
    team: PitchDeckSection
    financials: PitchDeckSection
    competition: PitchDeckSection
    roadmap: PitchDeckSection


    
def extract_tag_content(tag: str, response: str) -> str:
    pattern = f"<{tag}>(.*?)</{tag}>"
    match = re.search(pattern, response, re.DOTALL)
    return match.group(1).strip() if match else ""

def extract_sections(markdown_content: str) -> PitchDeckAnalysis:
    """Extract sections from pitch deck using Claude 3.5 Sonnet/Haiku."""
    prompt = f"""Analyze the following pitch deck content and extract these sections:
    1. Problem Statement
    2. Market Opportunity
    3. Technical Approach
    4. Team
    5. Financials
    6. Competition
    7. Roadmap

    Output ONLY valid XML tags for each section. Use these exact tags:
    <problem_statement>...</problem_statement>
    <market_opportunity>...</market_opportunity>
    <technical_approach>...</technical_approach>
    <team>...</team>
    <financials>...</financials>
    <competition>...</competition>
    <roadmap>...</roadmap>

    Here's the pitch deck content:
    <pitch_deck>
    {markdown_content}
    </pitch_deck>
    """
    
    response = get_haiku35_response(prompt)
    if not response:
        raise ValueError("Failed to extract sections from the pitch deck")

    return PitchDeckAnalysis(
        problem_statement=PitchDeckSection(raw_content=extract_tag_content("problem_statement", response)),
        market_opportunity=PitchDeckSection(raw_content=extract_tag_content("market_opportunity", response)),
        technical_approach=PitchDeckSection(raw_content=extract_tag_content("technical_approach", response)),
        team=PitchDeckSection(raw_content=extract_tag_content("team", response)),
        financials=PitchDeckSection(raw_content=extract_tag_content("financials", response)),
        competition=PitchDeckSection(raw_content=extract_tag_content("competition", response)),
        roadmap=PitchDeckSection(raw_content=extract_tag_content("roadmap", response))
    )

def analyze_section(section_content: str, section_name: str, custom_prompt: str) -> PerplexityResponse:
    """Analyze a specific section using Perplexity AI."""
    prompt = f"{custom_prompt}\n\nHere's the {section_name} section content:\n<{section_name}>\n{section_content}\n</{section_name}>"
    return get_sonar_response(prompt)

def analyze_pitch_deck(markdown_content: str, custom_prompts: dict[str, str]) -> PitchDeckAnalysis:
    """Main function to analyze the pitch deck."""
    # First extract all sections
    analysis = extract_sections(markdown_content)
    
    # Then analyze each section with Perplexity
    for field, prompt in custom_prompts.items():
        section = getattr(analysis, field)
        if section.raw_content:
            section.analysis = analyze_section(section.raw_content, field, prompt)
    
    return analysis 