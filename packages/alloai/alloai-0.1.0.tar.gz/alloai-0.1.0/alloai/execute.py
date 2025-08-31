import os
from openai import OpenAI
import sys
import io
import logging

def get_openai_client():
    """Get or create OpenAI client with proper configuration."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found in environment variables. "
            "Please set it in your .env file or environment."
        )

    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        return OpenAI(api_key=api_key, base_url=base_url)
    else:
        return OpenAI(api_key=api_key)

def execute_and_capture(code, scope):
    """
    Executes a block of code in a given scope and captures any output
    sent to stdout.

    Args:
        code (str): The Python code to execute.
        scope (dict): The scope (e.g., globals, locals) to execute in.

    Returns:
        str: The captured stdout content.
    """
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    output = ""
    try:
        exec(code, scope)
        output = redirected_output.getvalue()
    except Exception as e:
        # Print the error to the actual console for debugging
        print(f"Error during execution: {e}")
    finally:
        # Restore stdout
        sys.stdout = old_stdout
    return output


def execute_markdown(parsed_markdown):
    """
    Executes list of interleaved Python code blocks and natural
    language instructions for an LLM. The LLM is provided with the
    runtime state (variables and output of the executed code block
    just before it).

    Args:
        parsed_markdown (list[dict[str, str]]): The parsed markdown content.
    """

    # A dictionary to serve as the shared global scope for exec
    shared_scope = {}
    last_execution_output = ""
    last_execution_code = ""
    for part in parsed_markdown:
        # It's a code block
        if part['type'] == 'code':
            code = part['content']
            logging.debug(f"Executing code:\n---\n{code}\n---")
            last_execution_code = code
            output = execute_and_capture(code, shared_scope)

            if output:
                print(output,  end="")
                last_execution_output = output

        # It's a natural language instruction
        elif part['type'] == 'prompt':
            instruction = part['content']
            logging.debug(f"LLM Instruction: {instruction}")

            # Prepare the current variable state for the prompt
            variable_state_lines = []
            for key, value in shared_scope.items():
                if not key.startswith('__'): # Filter out built-ins
                    try:
                        # Use repr() for a developer-friendly representation
                        variable_state_lines.append(f"{key} = {repr(value)}")
                    except Exception:
                        variable_state_lines.append(f"{key} = <unrepresentable object>")
            variable_state_string = "\n".join(variable_state_lines)


            # Construct the dynamic prompt for the LLM
            prompt = (
                f"You are an AI assistant that can execute Python code. "
                f"The script has been running and has the following state:\n\n"
                f"--- CODE EXECUTED JUST BEFORE ---\n"
                f"```python\n{last_execution_code}```\n\n"
                f"--- CONSOLE OUTPUT OF THE PREVIOUS CODE ---\n"
                f"{last_execution_output}\n"
                f"--- CURRENT VARIABLE STATE ---\n"
                f"{variable_state_string}\n\n"
                f"Based on this state, the user wants you to perform the following action: '{instruction}'.\n\n"
                f"Generate ONLY the Python code to accomplish this. Do not add explanations or markdown formatting."
            )

            # Get or create the OpenAI client
            try:
                client = get_openai_client()
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)

            # Get the model from environment or use default
            model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

            # Call the LLM
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that generates python code based on the current script state."},
                        {"role": "user", "content": prompt}
                    ]
                )
            except Exception as e:
                print(f"Error calling LLM: {e}")
                logging.error(f"LLM API call failed: {e}")
                continue
            llm_code = response.choices[0].message.content or ''

            # Clean potential markdown formatting from the LLM's response
            if llm_code.startswith("```python"):
                llm_code = llm_code[9:]  # Remove ```python
            if llm_code.endswith("```"):
                llm_code = llm_code[:-3]  # Remove trailing ```
            llm_code = llm_code.strip()

            logging.debug(f"Executing llm generated code:\n---\n{llm_code}\n---")
            output = execute_and_capture(llm_code, shared_scope)

            if output:
                print(output, end="")
