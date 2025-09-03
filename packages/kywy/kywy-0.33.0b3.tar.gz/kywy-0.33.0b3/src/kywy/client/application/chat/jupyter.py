import os
import tempfile
import importlib
import uuid
import requests
from kywy.client.application.chat.chat import NotebookChat
from anthropic import Anthropic
import ipywidgets as widgets
from IPython.display import display

version = 20


# To run un Jupyter:
# from kywy.client.application.chat.jupyter import chat_app
# chat_app()

def chat_app():
    chat = NotebookChat()

    def reset(b):
        chat.reset()
        generation_output.clear_output()
        execution_output.clear_output()
        prompt_input.value = ''
        specs_input.value = ''

    def on_submit_research_click(b):
        research_button.description = "Processing…"
        research_button.disabled = True
        current_prompt = prompt_input.value
        chat.log('Start writing the specs...')
        try:

            specs = chat.generate_application_specs(current_prompt)
            specs_input.value = specs
            chat.log('Generated specs: \n' + specs)

        finally:
            research_button.description = "📚Write Specs"
            research_button.disabled = False
            submit_button.disabled = False

    def on_submit_button_click(b):
        submit_button.description = "Processing…"
        submit_button.disabled = True
        research_button.disabled = True
        chat.log('Start generating code...')
        current_prompt = prompt_input.value
        current_specs = specs_input.value
        try:
            for iteration in range(3):
                generation_output.clear_output()
                execution_output.clear_output()

                chat.log(f'Running iteration {iteration}')

                iteration_text = '' if iteration == 0 else f'(retry {iteration}) '

                with generation_output:
                    submit_button.description = f'🤖 {iteration_text}Generating…'
                    prompt = f'''
                    User original prompt: {current_prompt}
                    Application specs: {current_specs}
                    '''
                    generated_code = chat.generate_code(prompt=prompt)
                with execution_output:
                    submit_button.description = f'⚙️ {iteration_text}Publishing…'
                    error = chat.execute_code()
                    if not error:
                        m = '✅ Generation and Publication complete'
                        print(m)
                        chat.log(m)
                        break
                    else:
                        m = '❌ There were errors, starting again.'
                        print(m)
                        chat.log(m)
                        chat.log(error)
                        current_prompt = error

                chat.log('Generated code: \n' + generated_code)

        finally:
            submit_button.description = "🤖 Submit"
            submit_button.disabled = False
            research_button.disabled = False

    #
    # Build the app
    #
    logo_url = "https://learn.kawa.ai/logo.png"
    resp = requests.get(logo_url)
    logo_bytes = resp.content
    logo_img = widgets.Image(
        value=logo_bytes,
        format='png',  # or 'jpg' etc. matching your image
        layout=widgets.Layout(width='120px', height='30px')
    )
    title = widgets.HTML(
        value="<h1 style='margin:0; padding-left:10px;'>Experimental App Co builder</h1>",
    )

    header = widgets.HBox(
        [logo_img, title],
        layout=widgets.Layout(align_items='center', padding='10px 0')
    )

    prompt_input = widgets.Textarea(
        value='',
        placeholder=f'(V{version}) Type your prompt here...',
        layout=widgets.Layout(width='calc(100% - 2px)', height='100px')
    )

    specs_input = widgets.Textarea(
        value='',
        placeholder=f'... Your specs will be generated here ....',
        layout=widgets.Layout(width='calc(100% - 2px)')
    )

    research_button = widgets.Button(description="📚Write Specs", button_style='info', disabled=False)
    submit_button = widgets.Button(description="🤖 Submit", button_style='info', disabled=True)
    reset_button = widgets.Button(description="Reset", button_style='danger', disabled=False)
    buttons = widgets.HBox([research_button, submit_button, reset_button])

    output_layout = {'padding': '10px', 'border': '1px solid gray'}

    generation_output = widgets.Output(layout=output_layout)
    execution_output = widgets.Output(layout=output_layout)

    research_button.on_click(on_submit_research_click)
    submit_button.on_click(on_submit_button_click)
    reset_button.on_click(reset)
    display(
        header,
        buttons,
        prompt_input,
        specs_input,
        generation_output,
        execution_output,
    )
