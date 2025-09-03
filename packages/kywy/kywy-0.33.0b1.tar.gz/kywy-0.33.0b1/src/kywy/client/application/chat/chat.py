from .source_code_utils import extract_sections, extract_between_marker_lines, extract_before_marker_line, \
    extract_between_fence
from anthropic import Anthropic
from openai import OpenAI
import os
import tempfile
import importlib
import uuid
import io
import sys
import traceback
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))

PATH_TO_LOG_FILE = '/tmp/co-builder.log'
MODEL = 'claude-sonnet-4-20250514'
MARKERS = [
    '-- DATA SECTION',
    '-- MODEL SECTION',
    '-- DASHBOARD SECTION'
]
SYSTEM_PROMPT_PATHS = {
    'create': f'{script_dir}/prompts/full-prompt.md',
    'edit': f'{script_dir}/prompts/edit-prompt.md',
}


class NotebookChat:

    def __init__(self):
        self._initial_script = None
        self._conversation = []
        self._patches = []
        self._anthropic_client = Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        self._open_ai_client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        self._qwen_client = OpenAI(
            api_key=os.getenv('QWEN_API_KEY'),
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        )

    @staticmethod
    def log(message):
        with open(PATH_TO_LOG_FILE, "a") as f:
            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{current_time}] {message}\n")

    def reset(self):
        self._initial_script = None
        self._conversation = []
        self._patches = []

    def execute_code(self):
        merged_code = self._merged_code()
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as tmp_file:
            extracted_code = extract_between_fence(merged_code)
            tmp_file.write(extracted_code)
            tmp_path = tmp_file.name

        stdout_buffer = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = StreamDuplicator(original_stdout, stdout_buffer)

        try:
            module_name = f"mod_{uuid.uuid4().hex}"
            spec = importlib.util.spec_from_file_location(module_name, tmp_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

        finally:
            os.remove(tmp_path)
            sys.stdout = original_stdout
            captured_output = stdout_buffer.getvalue()

            error_section = extract_between_marker_lines(
                captured_output,
                marker='# ERROR SECTION'
            ).strip()

            if error_section:
                return error_section

    def generate_code(self, prompt):

        is_first_iteration = self._first_iteration()
        action = 'create' if is_first_iteration else 'edit'
        system_prompt = self._build_system_prompt(action)

        self._conversation.append({
            "role": "user",
            "content": prompt
        })

        generated_content = self._generate_content_claude(system_prompt)

        self._conversation.append({
            "role": "assistant",
            "content": generated_content
        })

        if is_first_iteration:
            self._initial_script = generated_content
        else:
            extractions = extract_sections(
                source=generated_content,
                markers=MARKERS,
                patch_name=prompt
            )
            self._patches.append(extractions)

        return generated_content

    def generate_application_specs(self, prompt):
        instructions = self._load_prompt_file('research', 'research')
        tools = [{"type": "web_search"}]
        response = self._generate_content_open_ai(
            client=self._open_ai_client,
            model="gpt-5-nano",
            system_prompt=instructions
        )
        return response

    def _merged_code(self):
        sections = extract_sections(self._initial_script, markers=MARKERS)
        for marker in MARKERS:
            if marker not in sections:
                raise Exception(f'The initial script is missing this section: {marker}')

        for patch in self._patches:
            sections.update(patch)

        script_header = extract_before_marker_line(self._initial_script, MARKERS[0])
        final_script = script_header

        for marker in MARKERS:
            content = sections[marker]['content']
            patch_name = sections[marker]['patch']

            final_script += f'## 📝 Applied from patch "{patch_name}"'
            final_script += '\n'
            final_script += content
            final_script += '\n'

        final_script += '\n\napp.publish()\n```'
        return final_script

    def _first_iteration(self):
        return len(self._conversation) == 0

    def _build_system_prompt(self, create_or_edit):

        print('Using the prompt to ' + create_or_edit)
        main_task = self._load_prompt_file(create_or_edit, 'main-task')
        kawa_sdk_documentation = self._load_prompt_file('common', 'sdk-documentation')
        mistakes_to_avoid = self._load_prompt_file('common', 'mistakes-to-avoid')
        example = self._load_prompt_file(create_or_edit, 'examples')
        guidelines = self._load_prompt_file('common', 'additional-guidelines')

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

    def _generate_content_open_ai(self, client, model, system_prompt):
        conversation_with_system_prompt = [{"role": "system", "content": system_prompt}] + self._conversation
        generated_chunks = []
        # Stream tokens from Qwen3 (OpenAI-compatible Chat Completions API)
        stream = client.chat.completions.create(
            model=model,
            messages=conversation_with_system_prompt,
            stream=True,
        )

        for chunk in stream:
            # OpenAI-compatible delta structure
            delta = None
            if chunk.choices and chunk.choices[0].delta:
                delta = chunk.choices[0].delta
            if delta and getattr(delta, "content", None):
                text = delta.content
                generated_chunks.append(text)
                print(text, end="", flush=True)

        return "".join(generated_chunks)

    def _generate_content_claude(self, system_prompt):
        generated_content = ''
        with self._anthropic_client.messages.stream(
                model=MODEL,
                max_tokens=50_000,
                system=system_prompt,
                messages=self._conversation,
        ) as stream:
            for text in stream.text_stream:
                generated_content += text
                print(text, end="", flush=True)

        return generated_content

    @staticmethod
    def _load_prompt_file(directory, name):
        full_path = f'{script_dir}/prompts/{directory}/{name}.md'
        print(f'Loading prompt:{name} from {full_path}')

        with open(full_path, "r", encoding="utf-8") as file:
            prompt = file.read()

        if not prompt:
            raise Exception('Could not load ' + full_path)

        return prompt


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
