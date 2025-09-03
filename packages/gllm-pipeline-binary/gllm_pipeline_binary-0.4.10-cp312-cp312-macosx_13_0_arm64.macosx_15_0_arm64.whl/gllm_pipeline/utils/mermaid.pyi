from gllm_pipeline.steps.pipeline_step import BasePipelineStep as BasePipelineStep

MERMAID_HEADER: str

def extract_step_diagrams(steps: list[BasePipelineStep]) -> list[str]:
    """Extract and format Mermaid diagram content from a list of steps.

    This function is used to extract the diagram content from each step in the pipeline.
    It will remove the mermaid header and return the remaining lines.

    Args:
        steps (list[BasePipelineStep]): A list of pipeline steps that may have get_mermaid_diagram methods

    Returns:
        list[str]: A list of Mermaid diagram lines from the steps
    """
def combine_mermaid_diagrams(base_diagram: str, step_diagrams: str) -> str:
    """Combine a base Mermaid diagram with step diagrams if they exist.

    This is a common utility for Pipeline and various step classes that follow the same
    pattern of combining a base diagram with nested step diagrams.

    Args:
        base_diagram (str): The base Mermaid diagram representation.
        step_diagrams (str): The combined step diagrams content.

    Returns:
        str: The complete Mermaid diagram representation.
    """
