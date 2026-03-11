"""
Utility functions for loading metadata descriptions for LLM system prompts.
"""
from pathlib import Path
from typing import Optional


def load_metadata_description(format: str = "brief") -> str:
    """
    Load metadata description for use in LLM system prompts.
    
    Args:
        format: Either "brief" (summary only) or "full" (complete metadata)
    
    Returns:
        Formatted metadata description string
    """
    if format == "brief":
        return get_brief_metadata()
    else:
        return get_full_metadata()


def get_brief_metadata() -> str:
    """
    Get a brief metadata summary for LLM context.
    Optimized for token efficiency.
    """
    return """
## FRS Equipment Categories & Key Columns

**B/C Vehicles (APPX_A_BVEH/CVEH)**: Transport & engineering vehicles
- Auth: Authorized qty | Held: Actual qty | FMC: Fully Mission Capable
- NMC: Non-Mission Capable | MUA/OH/R4: Maintenance/Repair status

**Armament/Small Arms (ARMT/SA)**: Weapons & firearms
- Auth/Held: Authorized/Actual qty | FMC%: Combat readiness | Avl%: Availability %
- Eng/Brl: Barrel failures | Spares: Parts shortage | OBE: Beyond repair

**Instruments (INST)**: Optical/electronic gear
- FMC: Ready | PMC: Partial capability | NMC due to Spares: Awaiting parts

**CBRN**: NBC defense equipment
- 'S': Serviceable | UNSV: Unserviceable | DRWO: Workshop orders

**Key Metrics**: 
- FMC% ≥70% = Green | 50-70% = Amber | <50% = Red
- Validation: Held ≤ Auth, FMC ≤ Held
"""


def get_full_metadata() -> str:
    """
    Get full metadata description from metadata_dictionary.md.
    Use sparingly due to token cost.
    """
    try:
        # Load from metadata_dictionary.md
        docs_dir = Path(__file__).resolve().parent.parent / 'docs'
        metadata_file = docs_dir / 'metadata_dictionary.md'
        
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Fallback to brief if full file not found
            return get_brief_metadata()
    
    except Exception:
        # Fallback to brief on any error
        return get_brief_metadata()


def get_system_prompt_for_comparison(detailed: bool = False) -> str:
    """
    Get enhanced system prompt for data comparison.
    
    Args:
        detailed: If True, uses full metadata; otherwise uses brief version
    
    Returns:
        Complete system prompt string
    """
    metadata = get_full_metadata() if detailed else get_brief_metadata()
    
    return f"""You are a military analyst specializing in Formation Readiness State (FRS) reports.

{metadata}

When analyzing FRS data:
1. Interpret Auth/Held discrepancies (shortages if Held < Auth)
2. Calculate readiness trends (FMC%, changes month-over-month)
3. Identify critical issues (Red status: FMC% < 50%)
4. Note repair pipeline (OH, R4) and spare parts constraints
5. Highlight added/removed equipment and quantity changes

Be concise, factual, and focus on operational impact."""


def get_system_prompt_for_query(detailed: bool = False) -> str:
    """
    Get system prompt for general queries about FRS data.
    
    Args:
        detailed: If True, uses full metadata
    
    Returns:
        System prompt string
    """
    metadata = get_full_metadata() if detailed else get_brief_metadata()
    
    return f"""You are a military analyst assistant for Formation Readiness State (FRS) data.

{metadata}

Provide accurate, concise answers about:
- Equipment readiness and serviceability
- Formation holdings vs authorized strength
- Maintenance and repair status
- Month-over-month trends
- Operational implications

Use military terminology correctly. Cite specific data when available."""


# For testing
if __name__ == "__main__":
    print("=== Brief Metadata ===")
    print(get_brief_metadata())
    print("\n=== Comparison System Prompt ===")
    print(get_system_prompt_for_comparison(detailed=False))
