# wizard/ui_builder.py

from concurrent.futures import ThreadPoolExecutor
from nicegui import ui
from wizard.wizard_controller import WizardController
from file_manager import open_directory_picker, flush_directory, list_subfolders
from openai_client import OpenAIClient
from logging_utils import log_message, ConsoleColor, trace

from wizard.steps.modules import add_module
import threading

import asyncio

@trace
async def populate_modules_in_parallel(wizard_controller, openai_client):
    """Trigger parallel OpenAI API calls for each module in Step 3."""
    async def call_module_api(module):
        prompt_text = module["prompt"].value
        size = module["size"].value
        prompt_with_size = f"{prompt_text} Size: {size}."
        response = await openai_client.get_response(prompt_with_size, max_tokens=150)
        module["execution_output"].set_text(response)
        log_message(f"Module {module['id']} populated.", session_id=f"MODULE_{module['id']}", color=ConsoleColor.GREEN)
        return response

    tasks = [call_module_api(module) for module in wizard_controller.dynamic_modules]
    await asyncio.gather(*tasks)


@trace
def setup_wizard_ui():
    wizard_controller = WizardController()
    openai_client = OpenAIClient()
    wizard_controller.openai_client = openai_client  # Save the instance in the controller

    # Add custom CSS and Topbar
    ui.add_head_html("""
    <style>
    body { background-color: white; margin: 0; text-align: center; }
    .topbar { background-color: #FFEB3B; color: black; padding: 20px 0; width: 100%; text-align: center; position: fixed; top: 0; z-index: 1000; }
    .topbar .container { width: 94%; max-width: 1440px; margin: auto; display: flex; align-items: center; justify-content: center; }
    .topbar a { color: black; text-decoration: none; }
    .topbar a:hover { text-decoration: underline; }
    .col-centered { flex: 1; margin: 0 10px; display: flex; flex-direction: column; align-items: flex-start; text-align: left; }
    .four-col-row { text-align: left; margin-bottom: 100px; display: flex; flex-direction: row; justify-content: space-around; align-items: flex-start; padding-top: 100px; padding-left: 20px; padding-right: 20px; width: 100%; }
    .col-centered { flex: 1; margin: 0 10px; display: flex; flex-direction: column; align-items: center; }
    .my-button { background-color: #1174e6 !important; color: white !important; border: none; padding: 10px 20px; cursor: pointer; margin: 8px; }
    .my-button-purple { background-color: purple !important; color: white !important; border: none; padding: 10px 20px; cursor: pointer; margin: 8px; }
    .footer { background-color: black; color: white; padding: 20px 0; width: 100%; position: absolute; left: 0; bottom: 0; letter-spacing: 0.81px; padding-bottom: 25px; text-align: center; }
    .cool-footer { font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; font-size: 1.3em; font-weight: bold; text-shadow: 1px 1px 2px #666; }
    input, .nicegui-input {height: 40px !important;font-size: 1.1em;}
    textarea, .nicegui-textarea {min-height: 150px !important; font-size: 1.1em;}
    </style>
    """)

    ui.html("""
    <div class="topbar">
      <div class="container">
        <div class="brand">
          <a href="#">A+ Content Generator</a>
        </div>
      </div>
    </div>
    """)
    wizard_ui = ui.stepper().props('horizontal').classes('w-full p-8 lg:p-16 max-w-[1600px] mx-auto')

    with wizard_ui:
        # ─────────────────────────────────────────────────────────
        # STEP 1: BASIC SETUP
        # ─────────────────────────────────────────────────────────
        with ui.step('Step 1: Basic Setup'):
            ui.label("Step 1: Basic Setup").classes("text-h5 font-bold mb-4")
            ui.label("Select your project folder:").classes("text-h6 mt-4")
            with ui.row().classes("items-center"):
                wizard_controller.root_directory_input = ui.input(
                    placeholder="No directory selected"
                ).props('readonly').classes("w-full")
                ui.button("Select Directory", on_click=lambda:
                          open_directory_picker(wizard_controller.root_directory_input)
                          ).classes("ml-2 bg-blue text-white px-4 py-2 rounded")
                ui.button("Flush Directory", on_click=lambda:
                          flush_directory(wizard_controller)
                          ).classes("ml-2 bg-red text-white px-4 py-2 rounded")
                ui.button("List Subfolders", on_click=lambda:
                          list_subfolders(wizard_controller)
                          ).classes("ml-2 bg-blue text-white px-4 py-2 rounded")
            wizard_controller.subfolder_selection_container = ui.column().classes("mt-2")
            
            ui.label("Enter OpenAI API Key:").classes("text-h6 mt-4")
            api_key_input = ui.input(placeholder="Enter your OpenAI API key").props('type="password"').classes("w-full")
            ui.button("Set API Key", on_click=lambda:
                      openai_client.set_api_key(api_key_input.value)
                      ).classes("mt-2 bg-blue text-white px-4 py-2 rounded")
            
            ui.label("Select Book Genre:").classes("text-h6 mt-4")
            genres = ["Self-Help", "Fiction", "Non-Fiction", "Mystery", "Sci-Fi"]
            wizard_controller.book_type_input = ui.select(genres, value="Self-Help").classes("w-full")
            
            with ui.stepper_navigation():
                def validate_basic_setup():
                    # Validate that an API key is set
                    if not openai_client.api_key:
                        ui.notify("OpenAI API key is required.", color="red")
                        return
                    # Validate that a folder is selected
                    folder = wizard_controller.root_directory_input.value.strip()
                    if not folder:
                        ui.notify("Please select a folder.", color="red")
                        return
                    # If subfolder checkboxes exist, ensure at least one is ticked
                    if wizard_controller.subfolder_checkboxes:
                        if not any(cb[1].value for cb in wizard_controller.subfolder_checkboxes):
                            ui.notify("Please tick at least one subfolder.", color="red")
                            return

                    # All validations passed → move to Step 2
                    wizard_ui.next()
                ui.button("Next", on_click=validate_basic_setup).classes("bg-blue text-white px-4 py-2 rounded")

        # ─────────────────────────────────────────────────────────
        # STEP 2: MODULE STRUCTURE & TYPE
        # ─────────────────────────────────────────────────────────
        with ui.step('Step 2: Module Structure & Type'):
            ui.label("Step 2: Module Structure & Type").classes("text-h5")
            ui.label("Choose how you want to build your modules:").classes("text-body1")
            # For example, a selection between different methods:
            wizard_controller.structure_type = ui.select(["Generate", "Select", "Manual"], value="Generate").classes("w-full")
            with ui.stepper_navigation():
                ui.button("Back", on_click=wizard_ui.previous).classes("bg-blue text-white px-4 py-2 rounded")
                ui.button("Next", on_click=wizard_ui.next).classes("bg-blue text-white px-4 py-2 rounded")

        # ─────────────────────────────────────────────────────────
        # STEP 3: MODULE CONTENTS
        # ─────────────────────────────────────────────────────────
        with ui.step('Step 3: Module Contents'):
            ui.label("Step 3: Module Contents").classes("text-h5")
            ui.label("Customize the content for each module:").classes("text-body1")
            wizard_controller.module_customization_container = ui.row().classes("flex-wrap gap-4 items-start")
            # Pre-create 4 modules
            for _ in range(4):
                add_module(wizard_controller)
            ui.button("Add Module", on_click=lambda: add_module(wizard_controller)).classes("bg-green text-white m-2")
            
            # Bonus Modules (if structure_type is "Generate" and bonus is enabled)
            with ui.column():
                ui.label("Bonus Module Customization (optional)").classes("text-h6 mt-4")
                wizard_controller.bonus_customization_container = ui.column()
                def add_bonus_module_field():
                    with wizard_controller.bonus_customization_container:
                        with ui.row().classes('items-center'):
                            bonus_title = ui.input(label="Bonus Module Title")
                            bonus_desc = ui.input(label="Bonus Module Description")
                            bonus_prompt = ui.textarea(
                                label="Prompt/Instructions",
                                value="Enter your prompt here..."
                            ).style("height: 150px")
                            wizard_controller.bonus_inputs.append({
                                "bonus_title": bonus_title,
                                "bonus_desc": bonus_desc,
                                "bonus_prompt": bonus_prompt
                            })
                    ui.notify("Bonus module field added", color="green", position="top")
                    log_message("Bonus module field added.", session_id=wizard_controller.session_id)
                ui.button("Add Bonus Module", on_click=add_bonus_module_field).classes("m-2 bg-green text-white")
            
            with ui.stepper_navigation():
                ui.button("Back", on_click=wizard_ui.previous).classes("bg-blue text-white px-4 py-2 rounded")
                # When moving from Step 3, trigger population of modules in parallel.
                def next_step3():
                    wizard_ui.next()
                    ui.timer(1, lambda: populate_modules_in_parallel(wizard_controller, openai_client), once=True)
                ui.button("Next", on_click=next_step3).classes("bg-blue text-white px-4 py-2 rounded")

        # ─────────────────────────────────────────────────────────
        # STEP 4: CONTENT GENERATION & REFINING
        # ─────────────────────────────────────────────────────────
        with ui.step('Step 4: Content Generation & Refining'):
            ui.label("Step 4: Content Generation & Refining").classes("text-h5")
            # Example: Propose Headlines
            def propose_headlines():
                prompt = "Generate 3 compelling, distinct headlines for the book based on its modules and style."
                def call_api():
                    headlines_text = openai_client.get_response(prompt, max_tokens=150)
                    headlines = [line.strip() for line in headlines_text.split("\n") if line.strip()]
                    wizard_controller.proposed_headlines = headlines
                    wizard_controller.headline_output.content = "\n".join(f"- {h}" for h in headlines)
                    ui.notify("Headlines proposed", color="green", position="top")
                    log_message("Headlines generated.", session_id=wizard_controller.session_id)
                threading.Thread(target=call_api).start()
            ui.button("Propose Headlines", on_click=propose_headlines).classes("m-2 bg-blue text-white")
            wizard_controller.headline_output = ui.markdown("Proposed headlines will appear here")
            ui.textarea(
                label="Refinement Prompt",
                placeholder="Enter refinement prompt here...",
                on_change=lambda e: setattr(wizard_controller, 'refinement_prompt', e.value)
            ).classes("m-2").style("min-height: 100px;")
            ui.button("Refine Content", on_click=lambda: ui.notify("Content refining triggered", color="green", position="top")).classes("m-2 bg-blue text-white")
            with ui.stepper_navigation():
                ui.button("Back", on_click=wizard_ui.previous).classes("bg-blue text-white px-4 py-2 rounded")
                ui.button("Next", on_click=wizard_ui.next).classes("bg-blue text-white px-4 py-2 rounded")

        # ─────────────────────────────────────────────────────────
        # STEP 5: FINAL OUTPUT
        # ─────────────────────────────────────────────────────────
        with ui.step('Step 5: Final Output'):
            ui.label("Step 5: Final Output").classes("text-h5")
            wizard_controller.final_output_display = ui.markdown("Final plan will appear here...")
            with ui.stepper_navigation():
                ui.button("Back", on_click=wizard_ui.previous).classes("bg-blue text-white px-4 py-2 rounded")
                def finalize_plan():
                    module_data = []
                    for mod in wizard_controller.dynamic_modules:
                        module_data.append({
                            "module_title": mod["title"].value,
                            "headline": mod["headline"].value,
                            "subheadline": mod["subheadline"].value,
                            "mockup_style": mod["mockup_select"].value,
                            "testimonials": mod["testimonials"].value,
                            "prompt": mod["prompt"].value,
                            "size": mod["size"].value,
                        })
                    final_plan = f"Plan created with {len(module_data)} modules:\n" + "\n".join(str(module) for module in module_data)
                    wizard_controller.final_output_display.content = final_plan
                    ui.notify("Final plan generated.", color="green", position="top")
                    log_message(f"Plan created with {len(module_data)} modules.", session_id=wizard_controller.session_id)
                ui.button("Finish", on_click=finalize_plan).classes("bg-green text-white px-4 py-2 rounded")

    # Footer
    ui.html("""
    <div class="footer">
      <div class="container cool-footer">
        🚀 Made by Ravenyr
      </div>
    </div>
    """)

    ui.run(title="A+ Content Plan Generator")

if __name__ in {"__main__", "__mp_main__"}:
    setup_wizard_ui()
