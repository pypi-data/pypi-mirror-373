import os
import shutil
import glob
import json
import io
import re
import importlib
import uuid
import sys
import time
from openai import OpenAI
from anthropic import Anthropic
from datetime import datetime
from kywy.client.application.chat.source_code_utils import extract_before_marker_line, extract_between_marker_lines, \
    extract_sections, extract_between_fence

open_ai_client = OpenAI()
anthropic_client = Anthropic()
SCRIPT_DIR = '/Users/emmanuel/dev/kywy/src/kywy/client/application/chat/prompts'
CONTEXT_ROOT = '/Users/emmanuel/data/cobuilder'
CODER_AGENT = 'coder_agent'
SPECS_AGENT = 'specs_agent'
MARKERS = [
    '-- DATA SECTION',
    '-- RELATIONSHIPS SECTION',
    '-- VARIABLES SECTION',
    '-- METRICS SECTION',
    '-- DASHBOARD SECTION'
]


def init(application_id, reset=False):
    path = CONTEXT_ROOT + '/' + application_id

    if reset and os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)

    os.makedirs(_agent_dir(application_id, CODER_AGENT), exist_ok=False)
    os.makedirs(_agent_dir(application_id, SPECS_AGENT), exist_ok=False)


def publish(application_id, step_name=None, num_retries=2, print_output=False, running_on_dev_server=False):
    for try_id in range(0, num_retries):
        print(f'🐢 Now running the publication script (Iteration={try_id + 1}/{num_retries + 1})')
        feedback = _publish(
            application_id=application_id,
            step_name=step_name,
            print_output=print_output,
            running_on_dev_server=running_on_dev_server,
        )
        if feedback:
            print('Generating corrective patch')
            generate_code_patch(
                application_id=application_id,
                user_prompt=feedback,
                step_instructions='Focus on fixing the reported errors',
            )
        else:
            return


def generate_datasets(application_id, special_instructions=""):
    generate_code_patch(
        application_id=application_id,
        user_prompt=special_instructions,
        step_instructions="""
        Only generate the datasets
        """,
    );


def generate_relationships(application_id, special_instructions=""):
    generate_code_patch(
        application_id=application_id,
        user_prompt=special_instructions,
        step_instructions="""
        Add the relationships in the RELATIONSHIPS SECTION.
        """,
    );


def generate_variables(application_id, special_instructions=""):
    generate_code_patch(
        application_id=application_id,
        user_prompt=special_instructions,
        step_instructions="""
        Add the variables in the VARIABLES SECTION.
        """,
    );


def generate_metrics(application_id, special_instructions=""):
    generate_code_patch(
        application_id=application_id,
        user_prompt=special_instructions,
        step_instructions="""
        Add the metrics in the METRICS SECTION.
        """,
    );


def generate_dshboards(application_id, special_instructions=""):
    generate_code_patch(
        application_id=application_id,
        user_prompt=special_instructions,
        step_instructions="""
        Add the widget and pages in the DASHBOARD SECTION.
        """,
    );


def generate_specs(application_id,
                   user_prompt=None,
                   predefined_specs=None,
                   print_output=False):

    if predefined_specs:
        predefined_specs = predefined_specs.strip()

    if user_prompt:
        user_prompt = user_prompt.strip()

    if not user_prompt and not predefined_specs:
        raise Exception('We need at least one of user_prompt or predefined_specs')

    if predefined_specs:
        specs = predefined_specs
    else:
        conversation = _restore_conversation(
            application_id=application_id,
            agent_id=SPECS_AGENT,
        )

        system_prompt = _read_prompt('research', 'research')
        specs = _generate_content_open_ai(
            conversation=conversation,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            print_output=print_output,
        )

        _save_conversation(
            application_id=application_id,
            agent_id=SPECS_AGENT,
            conversation=conversation,
        )

    timestamp = datetime.now().isoformat(timespec="seconds")
    for filename in ['specs.md', f'specs-{timestamp}.md']:
        _persist_output_as_file(
            application_id=application_id,
            agent_id=SPECS_AGENT,
            filename=filename,
            content=specs,
        )


def generate_code_patch(application_id,
                        user_prompt,
                        step_instructions,
                        print_output=False):
    conversation = _restore_conversation(
        application_id=application_id,
        agent_id=CODER_AGENT,
    )

    action = 'create' if not conversation else 'edit'

    system_prompt = _code_generation_prompt(action)

    specs = _load_file(
        application_id=application_id,
        agent_id=SPECS_AGENT,
        filename='specs.md'
    )

    patch = _generate_content_anthropic(
        print_output=print_output,
        conversation=conversation,
        system_prompt=system_prompt,
        user_prompt=f"""

        {step_instructions}

        User prompt: {user_prompt}

        Specs: {specs}

        """,
    )

    patch = extract_between_fence(patch)

    _save_conversation(
        application_id=application_id,
        agent_id=CODER_AGENT,
        conversation=conversation,
    )

    timestamp = datetime.now().isoformat(timespec="seconds")

    filename = 'base.py' if action == 'create' else f'patch-{timestamp}.py'

    _persist_output_as_file(
        application_id=application_id,
        agent_id=CODER_AGENT,
        filename=filename,
        content=patch,
    )

    final_script = _merge_patches(
        application_id=application_id
    )

    _persist_output_as_file(
        application_id=application_id,
        agent_id=CODER_AGENT,
        filename='merged.py',
        content=final_script,
    )

    return patch


def _code_generation_prompt(create_or_edit):
    main_task = _read_prompt(create_or_edit, 'main-task')
    kawa_sdk_documentation = _read_prompt('common', 'sdk-documentation')
    mistakes_to_avoid = _read_prompt('common', 'mistakes-to-avoid')
    example = _read_prompt(create_or_edit, 'examples')
    guidelines = _read_prompt('common', 'additional-guidelines')

    system_prompt = f'''

        # Main task

        {main_task}


        # Kawa SDK Documentation

        {kawa_sdk_documentation}


        # Additional guidelines

        {guidelines}


        # Mistakes to avoid

        {mistakes_to_avoid}


        # Full working example

        {example}
        '''

    return system_prompt


def _read_prompt(directory, name):
    full_path = f'{SCRIPT_DIR}/{directory}/{name}.md'
    with open(full_path, "r", encoding="utf-8") as file:
        prompt = file.read()

    if not prompt:
        raise Exception('Could not load ' + full_path)

    return prompt


def _merge_patches(application_id):
    base_script = _load_file(application_id, CODER_AGENT, 'base.py')

    # Init the sections with the base file
    sections = extract_sections(source=base_script, markers=MARKERS)
    for marker in MARKERS:
        if marker not in sections:
            raise Exception(f'The initial script is missing this section: {marker}')

    # Go through all the files in order and apply the patches, updating the "sections" dict
    patch_filenames = _list_files_in_dir(
        application_id=application_id,
        agent_id=CODER_AGENT,
        pattern='patch-*.py',
    )

    for patch_filename in patch_filenames:
        patch_content = _load_file(
            application_id=application_id,
            agent_id=CODER_AGENT,
            filename=patch_filename,
        )

        sections_in_patch = extract_sections(
            source=patch_content,
            markers=MARKERS,
            patch_name=patch_filename,
        )

        sections.update(sections_in_patch)

    return _build_script_from_sections(
        base_script=base_script,
        sections=sections,
    )


def _build_script_from_sections(base_script, sections):
    script_header = extract_before_marker_line(
        source=base_script,
        marker=MARKERS[0]
    )
    final_script = script_header

    for marker in MARKERS:
        content = sections[marker]['content']
        patch_name = sections[marker]['patch']
        final_script += f'## 📝 Applied from patch "{patch_name}"'
        final_script += '\n'
        final_script += content
        final_script += '\n'

    final_script += '\n\napp.publish()\n'
    return final_script


def _publish(application_id, step_name=None, print_output=False, running_on_dev_server=True):
    agant_dir = _agent_dir(application_id=application_id, agent_id=CODER_AGENT, )
    script_path = f'{agant_dir}/merged.py'
    stdout_buffer = io.StringIO()
    original_stdout = sys.stdout

    if print_output:
        sys.stdout = StreamDuplicator(original_stdout, stdout_buffer)
    else:
        sys.stdout = stdout_buffer

    error = None
    try:
        module_name = f"mod_{uuid.uuid4().hex}"
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

    except Exception as e:
        error = f'An error was detected: {e}'
        print(error)

    finally:
        sys.stdout = original_stdout
        captured_output = stdout_buffer.getvalue()
        error_section = extract_between_marker_lines(
            captured_output,
            marker='# ERROR SECTION'
        ).strip()

        if error:
            return f"""
            There was a global error, please regenerate the appropriate sections to fix it.
            {error}
            """

        elif error_section:
            return f"""
            Here is the output of the script - notice that it stopped in the middle of its execution.
            This means that the last element has an error to fix (indicated below).
            Please generate ONLY the impacted section with your fix.
            {captured_output}
            """
        else:
            for line in captured_output.splitlines():
                if 'Publication Complete:' in line:
                    if running_on_dev_server:
                        updated_string = line.replace("8080", "4200")
                        print(updated_string)
                    else:
                        print(line)

                # If a step name was specified, we will extract the report for that step
                # and print it out
                elif step_name and 'Report file here' in line:
                    path = re.findall(r'\[(.*?)\]', line)[0]
                    with open(path, "r") as report_file:
                        report = json.loads(report_file.read())
                    if report:
                        created_entities = report.get('report', {}).get(step_name, [])
                        print(f'\nThe following {step_name}s were created:')
                        for created_entity in created_entities:
                            print(' - ' + created_entity.get('name'))

            return ''


## 🤖 LLM calls

def _generate_content_open_ai(conversation,
                              system_prompt,
                              user_prompt,
                              model=None,
                              print_output=True):
    start = time.time()
    conversation.append({"role": "user", "content": user_prompt})
    system_msg = {"role": "system", "content": system_prompt}
    full_conversation = [system_msg] + conversation
    used_model =model or 'gpt-4o'
    stream = open_ai_client.chat.completions.create(
        model=used_model,
        messages=full_conversation,
        stream=True
    )

    agent_message = ''
    counter = 0
    for event in stream:
        if event.choices[0].delta.content is not None:
            delta = event.choices[0].delta.content
            agent_message += delta
            if print_output:
                print(delta, end="")
            else:
                counter += 1
                print(f"\rReceiving content: {counter}", end="")

    conversation.append({"role": "assistant", "content": agent_message})
    elapsed = time.time() - start
    print(f'\n✅ ({used_model}) Generation is complete (it contains: {len(agent_message)} characters in {elapsed:.2f}s)')

    return agent_message


def _generate_content_anthropic(conversation,
                                system_prompt,
                                user_prompt,
                                model=None,
                                print_output=True):
    start = time.time()
    conversation.append({"role": "user", "content": user_prompt})
    agent_message = ''
    counter = 0
    used_model = model or 'claude-sonnet-4-20250514'
    with anthropic_client.messages.stream(
            model=used_model,
            max_tokens=50_000,
            system=system_prompt,
            messages=conversation,
    ) as stream:
        for text in stream.text_stream:
            agent_message += text
            if print_output:
                print(text, end="", flush=True)
            else:
                counter += 1
                print(f"\rReceiving content: {counter}", end="")

    conversation.append({"role": "assistant", "content": agent_message})
    elapsed = time.time() - start
    print(f'\n✅ ({used_model}) Generation is complete (it contains: {len(agent_message)} characters in {elapsed:.2f}s)')

    return agent_message


## 📝 Simple file manipulation

def _agent_dir(application_id, agent_id):
    return CONTEXT_ROOT + '/' + application_id + '/' + agent_id


def _list_files_in_dir(application_id, agent_id, pattern):
    directory = _agent_dir(application_id, agent_id)
    path_pattern = os.path.join(directory, pattern)
    file_paths = glob.glob(path_pattern)
    filenames = [os.path.basename(path) for path in file_paths]
    return sorted(filenames)


def _persist_output_as_file(application_id, agent_id, filename, content):
    path = _agent_dir(application_id, agent_id) + '/' + filename
    with open(path, "w") as f:
        f.write(content)


def _load_file(application_id, agent_id, filename):
    path = _agent_dir(application_id, agent_id) + '/' + filename
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def _save_conversation(application_id, agent_id, conversation):
    path = _agent_dir(application_id, agent_id) + '/' + "messages.json"
    with open(path, "w") as f:
        json.dump(conversation, f)


def _restore_conversation(application_id, agent_id):
    path = _agent_dir(application_id, agent_id) + '/' + "messages.json"
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


class StreamDuplicator:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()
