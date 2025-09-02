import os
from openai import OpenAI
import sys
import io
import logging
import hashlib
import json
from pathlib import Path
import cloudpickle
import platform

# Initialize cache
CACHE_DIR = Path(".alloai_cache")
CACHE_DIR.mkdir(exist_ok=True)
CACHE_FILE = CACHE_DIR / "execution_cache.pkl"

cache = {}
try:
    with open(CACHE_FILE, 'rb') as f:
        logging.debug("Loading cache from file")
        cache = cloudpickle.load(f)
except FileNotFoundError:
    logging.debug("Cache file not found, will be created")
    pass

if cache:
    logging.debug("Cache loaded")
    if cache.get("version") != platform.python_version():
        logging.warning("Cache version mismatch. Clearing cache.")
        cache = {}
        cache["version"] = platform.python_version()
else:
    cache["version"] = platform.python_version()


def get_hash(*vars):
    """Generate a unique hash for a group of variables"""
    hasher = hashlib.sha256()
    for var in vars:
        if var is None:
            var_str = "None"
        else:
            var_str = json.dumps(var, sort_keys=True, default=str)
        hasher.update(var_str.encode('utf-8'))

    return hasher.hexdigest()


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


def execute_and_capture(code_block, scope, use_cache=True):
    """
    Executes a block of code in a given scope and captures any output
    sent to stdout.

    Args:
        code (str): The Python code to execute.
        scope (dict): The scope (e.g., globals, locals) to execute in.
        use_cache (bool): Whether to use caching for this execution.

    Returns:
        str: The captured stdout content.
    """
    code = code_block['content']
    lang = code_block['language']
    logging.debug(f"Executing code:\n```{lang}\n{code}\n```")

    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    output = ""
    from_cache = False
    hash = get_hash(code, scope)
    try:
        # If the code and it's scope was the same as before, use cached output
        if use_cache and hash in cache:
            cached_result = cache[hash]
            output = cached_result['output']
            # Update the scope with the cached scope
            scope.update(cached_result['scope'])
            from_cache = True
        else:
            exec(code, scope)
            output = redirected_output.getvalue()
    except Exception as e:
        # Print the error to the actual console for debugging
        print(f"Error during execution: {e}")
    finally:
        # Restore stdout
        sys.stdout = old_stdout
    if not from_cache:
        # Cache both output and the resulting scope
        cache[hash] = {
            'output': output,
            'scope': scope.copy()  # Important to copy to avoid reference issues
        }
    else:
        logging.debug("Output from cache")
    return output, scope, from_cache


def get_code_from_llm(instruction_block, last_execution_code, last_execution_output, variable_state_string,
                      full_markdown_content, parsed_markdown, current_part_index, use_cache):
    """Get code from LLM prompt"""
    instruction = instruction_block['content']
    logging.debug(f"LLM Instruction:\n```markdown\n{instruction}\n```\n")
    hash = get_hash(instruction_block, last_execution_code, last_execution_output, variable_state_string,
                    full_markdown_content, parsed_markdown, current_part_index)
    from_cache = False
    # LLM may not generate code for informational statements
    llm_response = {"code": "", "commentary": ""}
    # If the instruction and associated context variables are same then use cached response
    if use_cache and hash in cache:
        logging.debug("Cache hit for Instruction + context variables")
        llm_response = cache[hash]
        from_cache = True
    else:
        logging.debug("Cache miss for Instruction + context variables")
        # Construct the dynamic prompt for the LLM
        if last_execution_code and isinstance(last_execution_code, dict) and last_execution_code.get('content'):
            # There was previous code execution
            previous_code_section = (
                f"--- CODE EXECUTED JUST BEFORE ---\n"
                f"```python\n{last_execution_code['content']}```\n\n"
                f"--- CONSOLE OUTPUT OF THE PREVIOUS CODE ---\n"
                f"{last_execution_output}\n"
            )
            context_intro = "The script has been running and has the following state:\n\n"
        else:
            # No previous code execution
            previous_code_section = "--- NO CODE HAS BEEN EXECUTED YET ---\n"
            context_intro = "You are starting a new Python script execution. "

        # Build context about execution progress
        execution_progress = get_execution_progress_context(parsed_markdown, current_part_index)

        llm_prompt = (
            f"You are an AI assistant that can execute Python code. "
            f"{context_intro}"
            f"--- FULL MARKDOWN FILE CONTENT ---\n"
            f"```markdown\n{full_markdown_content}\n```\n\n"
            f"--- EXECUTION PROGRESS ---\n"
            f"{execution_progress}\n\n"
            f"--- CURRENT INSTRUCTION ---\n"
            f"You are now processing part #{current_part_index + 1}: '{instruction}'\n\n"
            f"{previous_code_section}"
            f"--- CURRENT VARIABLE STATE ---\n"
            f"{variable_state_string if variable_state_string else 'No variables defined yet'}\n\n"
            f"Based on the full file context, execution progress, and current state, "
            f"determine what action (if any) is needed for this instruction: "
            f"'{instruction}'\n\n"
            f"Your response must be in one of these formats:\n"
            f"1. A single code block if you have code to execute:\n"
            f"```python\ncode here\n```\n\n"
            f"2. A blockquote followed by a code block if you have both commentary and code:\n"
            f"> Your commentary here\n```python\ncode here\n```\n\n"
            f"3. Nothing if you have none of the above\n"
            f"Do not include any text after the code block."
        )
        # Get or create the OpenAI client
        try:
            client = get_openai_client()

            # Get the model from environment or use default
            model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

            # Call the LLM
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates python code "
                                                  "based on the current script state."},
                    {"role": "user", "content": llm_prompt}
                ]
            )
            llm_raw_response = response.choices[0].message.content or ''

            # Parse the LLM response to extract code and commentary
            try:
                llm_response = parse_llm_response(llm_raw_response)
            except Exception as parse_error:
                logging.warning(f"Failed to parse LLM response: {parse_error}")
                # Fallback: treat entire response as code if it looks like code, otherwise as commentary
                stripped_response = llm_raw_response.strip()
                keywords = ['def ', 'import ', 'print(', 'for ', 'if ', 'while ', '=']
                if stripped_response and any(keyword in stripped_response.lower() for keyword in keywords):
                    llm_response = {"code": stripped_response, "commentary": ""}
                else:
                    llm_response = {"code": "", "commentary": stripped_response}
        except ValueError as e:
            logging.fatal(f"{e}")
            llm_response = {"code": "", "commentary": ""}
        except Exception as e:
            logging.error(f"LLM API call failed: {e}")
            llm_response = {"code": "", "commentary": f"Error: {str(e)}"}
    if not from_cache:
        cache[hash] = llm_response
    return llm_response, from_cache


def get_execution_progress_context(parsed_markdown, current_part_index):
    """
    Generate context about what has been executed and what's coming next.

    Args:
        parsed_markdown: List of parsed markdown parts
        current_part_index: Index of the current part being processed

    Returns:
        str: Context string about execution progress
    """
    total_parts = len(parsed_markdown)
    executed_parts = []
    upcoming_parts = []

    for i, part in enumerate(parsed_markdown):
        part_desc = f"Part {i+1}: "
        if part['type'] == 'code':
            part_desc += (f"[CODE BLOCK] {part.get('language', 'unknown')} - "
                          f"{part['content'][:30].replace(chr(10), ' ')}...")
        else:
            part_desc += f"[TEXT] {part['content'][:50].replace(chr(10), ' ')}..."

        if i < current_part_index:
            executed_parts.append(f"✓ {part_desc}")
        elif i > current_part_index:
            upcoming_parts.append(f"  {part_desc}")

    context = f"Progress: Processing part {current_part_index + 1} of {total_parts}\n"

    if executed_parts:
        context += "\nAlready executed:\n" + "\n".join(executed_parts[-3:])  # Show last 3
        if len(executed_parts) > 3:
            context += f"\n... and {len(executed_parts) - 3} earlier parts"

    if upcoming_parts:
        context += "\n\nComing next:\n" + "\n".join(upcoming_parts[:3])  # Show next 3
        if len(upcoming_parts) > 3:
            context += f"\n... and {len(upcoming_parts) - 3} more parts"

    return context


def parse_llm_response(raw_response):
    """
    Parse LLM response to extract commentary and code blocks.

    Expected formats:
    1. Just code: ```python\ncode\n```
    2. Just commentary: > commentary
    3. Commentary + code: > commentary\n```python\ncode\n```

    Returns:
        dict: {"code": str, "commentary": str}
    """
    response = {"code": "", "commentary": ""}

    try:
        if not raw_response or not raw_response.strip():
            return response

        lines = raw_response.strip().split('\n')

        # Extract blockquote commentary (lines starting with >)
        commentary_lines = []
        code_start_idx = -1

        for i, line in enumerate(lines):
            try:
                if line.strip().startswith('>'):
                    # Remove > and any leading space after it
                    comment_text = line.strip()[1:].lstrip()
                    commentary_lines.append(comment_text)
                elif line.strip().startswith('```python'):
                    code_start_idx = i
                    break
            except Exception as e:
                logging.debug(f"Error processing line {i}: {e}")
                continue

        response["commentary"] = '\n'.join(commentary_lines) if commentary_lines else ""

        # Extract code block
        if code_start_idx >= 0:
            code_lines = []
            try:
                for i in range(code_start_idx + 1, len(lines)):
                    if lines[i].strip() == '```':
                        break
                    code_lines.append(lines[i])
                response["code"] = '\n'.join(code_lines).strip()
            except Exception as e:
                logging.warning(f"Error extracting code block: {e}")
        else:
            # Check if the response is just code without markdown formatting
            potential_code = raw_response.strip()
            if potential_code and not potential_code.startswith('>'):
                # Assume it's code if it doesn't start with blockquote
                response["code"] = potential_code

    except Exception as e:
        logging.error(f"Error in parse_llm_response: {e}")
        # Return the raw response as commentary if parsing fails completely
        response["commentary"] = raw_response.strip()

    return response


def execute_markdown(parsed_markdown, output_file=None, use_cache=True, full_markdown_content=""):
    """
    Executes list of interleaved Python code blocks and natural
    language instructions for an LLM. The LLM is provided with the
    runtime state (variables and output of the executed code block
    just before it).

    Args:
        parsed_markdown (list[dict[str, str]]): The parsed markdown content.
        output_file (str, optional): Path to save the generated code to.
        use_cache (bool): Whether to use caching for execution.
        full_markdown_content (str): The full original markdown content for context.

    Returns:
        str: The complete generated code that was executed.
    """

    # A dictionary to serve as the shared global scope for exec
    shared_scope = {}
    last_execution_output = ""
    last_execution_code = None

    # Track all executed code for export
    all_executed_code = []
    for part_index, part in enumerate(parsed_markdown):
        # It's a code block
        if part['type'] == 'code':
            last_execution_code = part

            # Add to collected code
            all_executed_code.append(f"# Predefined code\n{part['content']}")

            output, scope, from_cache = execute_and_capture(part, shared_scope, use_cache)
            if from_cache:
                shared_scope = scope  # Update shared_scope with the cached scope
            if output:
                for op in output.splitlines():
                    print("> " + op)
                last_execution_output = output

        # It's a natural language instruction
        elif part['type'] == 'prompt':
            # Prepare the current variable state for the prompt
            variable_state_lines = []
            for key, value in shared_scope.items():
                if not key.startswith('__'):  # Filter out built-ins
                    try:
                        # Use repr() for a developer-friendly representation
                        variable_state_lines.append(f"{key} = {repr(value)}")
                    except Exception:
                        variable_state_lines.append(f"{key} = <unrepresentable object>")
            variable_state_string = "\n".join(variable_state_lines)

            try:
                # Call the LLM API to generate code with the instruction and variable state
                llm_response, from_cache = get_code_from_llm(
                    part, last_execution_code, last_execution_output, variable_state_string,
                    full_markdown_content, parsed_markdown, part_index, use_cache)
            except Exception as e:
                print(f"Error calling LLM: {e}")
                logging.error(f"LLM API call failed: {e}")
                continue

            if not isinstance(llm_response, dict):
                logging.error(f"Invalid LLM response format: {type(llm_response)}")
                continue

            llm_code = llm_response.get("code", "")
            llm_commentary = llm_response.get("commentary", "")

            # If LLM has commentary, print it
            if llm_commentary:
                print(f"💭 LLM: {llm_commentary}")

            # If there's no code to execute, just continue to next block
            if not llm_code.strip():
                logging.debug("LLM provided no executable code, continuing to next block")
                continue

            # TODO: python is hardcoded here
            logging.debug(f"Executing llm generated code:\n```python\n{llm_code}\n```\n")

            # Build comment for the generated code
            instruction_lines = f"{part['content'][:50]}{'...' if len(part['content']) > 50 else ''}".splitlines()
            modified_instruction_lines = ["# " + line for line in instruction_lines]
            comment_string = "\n".join(modified_instruction_lines)

            # Include LLM commentary if available
            code_comment = f"\n# LLM-generated code for: \n{comment_string}"
            if llm_commentary:
                commentary_lines = [f"# {line}" for line in llm_commentary.splitlines()]
                code_comment += "\n# LLM commentary: \n" + "\n".join(commentary_lines)

            all_executed_code.append(f"{code_comment}\n\n{llm_code}")

            # TODO: language is hardcoded here
            llm_code_block = {
                'content': llm_code,
                'language': 'python'  # Hardcoded for now
            }
            try:
                output, scope, from_cache = execute_and_capture(llm_code_block, shared_scope, use_cache)
                if from_cache:
                    shared_scope = scope  # Update shared_scope with the cached scope
                if output:
                    for op in output.splitlines():
                        print("> " + op)
                    last_execution_output = output  # TODO see if needed
            except Exception as e:
                print(f"Error executing LLM-generated code: {e}")
                logging.error(f"LLM code execution failed: {e}")
                continue

    # Combine all executed code
    complete_code = "\n\n".join(all_executed_code)

    # Save to file if requested
    if output_file:
        save_generated_code(complete_code, output_file)
        print(f"\n\n✓ Generated code saved to: {output_file}")

    with open(CACHE_FILE, 'wb+') as f:
        logging.debug("Saving cache to file")
        cloudpickle.dump(cache, f)
    return complete_code


def save_generated_code(code, filepath):
    """
    Save the generated code to a file.

    Args:
        code (str): The code to save.
        filepath (str): The path where to save the code.
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("#!/usr/bin/env python3\n")
            f.write("# This file was generated by AlloAI\n")
            f.write("# You can run this file directly with: python3 {}\n\n".format(filepath))
            f.write(code)

        # Make the file executable on Unix-like systems
        import stat
        import platform
        if platform.system() != 'Windows':
            current_permissions = os.stat(filepath).st_mode
            os.chmod(filepath, current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except Exception as e:
        logging.error(f"Failed to save generated code: {e}")
        raise


def clear_cache():
    """
    Clear all cached data including in-memory cache and persistent cache file.

    This function removes all cached execution results and LLM responses,
    forcing fresh execution on subsequent runs.
    """
    # Clear in-memory cache
    cache.clear()
    cache["version"] = platform.python_version()

    # Remove persistent cache file
    try:
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
            logging.debug("Cache file removed successfully")
    except Exception as e:
        logging.warning(f"Failed to remove cache file: {e}")

    logging.info("Cache cleared successfully")
