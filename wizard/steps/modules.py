import json
import asyncio
from nicegui import ui
from logging_utils import log_message, ConsoleColor, trace
from rag_integration import run_rag_system
from openai_client import OpenAIClient

@trace
def add_module(wizard, prefill_data: dict = None):
    # Use prefill_data for restored modules; otherwise assign new id
    module_id = prefill_data.get('module_id', len(wizard.dynamic_modules) + 1) if prefill_data else len(wizard.dynamic_modules) + 1

    # Create a module container as a flex row (side-by-side columns) 
    with ui.row().classes("flex flex-row gap-8 items-start").style("width: 100%; margin-bottom: 16px;") as module_row:
        ## Left Column: Input Fields (60% width)
        with ui.column().style("flex: 0 0 60%;"):
            #ui.label(f"Module {module_id}").classes("text-h5 font-bold mb-4 text-blue-700")
            # Module header with title and spinner in a row:
            with ui.row().classes("items-center gap-2 mb-4"):
                header_label = ui.label(f"Module {module_id}").classes("text-h5 font-bold text-blue-700")
                loading_spinner = ui.spinner("dots", size="sm").classes("ml-2").style("display: none;")

            # Title, Headline, Subheadline
            with ui.row().classes("items-center gap-4 mb-3"):
                title_input = ui.input(label="Title", placeholder="e.g. 'Introduction'")\
                                .classes("w-full")\
                                .style("background-color: #f0f8ff;")
                title_validation_label = ui.label().style("color: red; margin-left: 8px;")
    
            with ui.row().classes("items-center gap-4 mb-3"):
                headline_input = ui.input(label="Headline", placeholder="Short, catchy phrase")\
                                   .classes("w-full")\
                                   .style("background-color: #f0f8ff;")
                headline_char_count = ui.label("0 / 100").style("margin-left: 8px;")
    
            subheadline_input = ui.input(
                label="Subheadline",
                placeholder="Expand on the headline..."
            ).classes("w-full mb-3").style("background-color: #f0f8ff;")
    
            # Mockup Style Dropdown
            chosen_mockup_style = [prefill_data['chosen_mockup_style']] if prefill_data and 'chosen_mockup_style' in prefill_data else ["(choose style)"]
    
            def set_mockup_style(style):
                chosen_mockup_style[0] = style
                update_preview()      # update any additional text preview if needed
    
            with ui.row().classes("items-center gap-4 mb-3"):
                ui.label("Mockup Style:")
                mockup_dropdown = ui.dropdown_button("Choose style", auto_close=True).classes("w-40")
                with mockup_dropdown:
                    ui.item("Open Book", on_click=lambda: set_mockup_style("Open Book"))
                    ui.item("Closed Book", on_click=lambda: set_mockup_style("Closed Book"))
                    ui.item("3D Book", on_click=lambda: set_mockup_style("3D Book"))
    
            # Testimonials
            testimonials_input = ui.input(
                label="Testimonials",
                placeholder="Enter testimonials"
            ).classes("w-full mb-3").style("background-color: #f0f8ff;")
    
            # Prompt/Instructions
            prompt_textarea = ui.textarea(
                label="Prompt/Instructions",
                value="Improve this part"
            ).classes("w-full mb-3").style("height: 150px; background-color: #f0f8ff;")
    
            # Default Size
            default_size = ""
            if module_id == 1:
                default_size = "970x600px Standard Image Header With Text"
            elif module_id == 2:
                default_size = "970x300px Standard Image & Light Text Overlay"
            elif module_id == 3:
                default_size = "4x220x220px Standard Four Images & Text"
            elif module_id == 4:
                default_size = "970x300px Standard Image & Light Text Overlay"
            size_input = ui.input(label="Size", value=prefill_data.get('size', default_size) if prefill_data else default_size)\
                           .classes("w-full mb-3").style("background-color: #f0f8ff;")
    
            # Color Palette Inputs with Swatches next to them
            with ui.row().classes("items-center gap-4 mb-3"):
                # Left sub-column: Color Inputs
                with ui.column().style("flex: 0 0 50%;"):
                    ui.label("Color Palette:").classes("text-body1 font-semibold")
                    color_primary = ui.color_input(label="Primary", value=prefill_data.get('color_primary', "#3D5A80") if prefill_data else "#3D5A80").classes("w-36")
                    color_secondary = ui.color_input(label="Secondary", value=prefill_data.get('color_secondary', "#98C1D9") if prefill_data else "#98C1D9").classes("w-36")
                    color_accent = ui.color_input(label="Accent", value=prefill_data.get('color_accent', "#EE6C4D") if prefill_data else "#EE6C4D").classes("w-36")
    
                # Right sub-column: Color Palette Swatches
                with ui.column().style("flex: 0 0 50%;"):
                    ui.label("Swatches:").classes("text-body1 font-semibold")
                    with ui.row().classes("gap-2"):
                        primary_swatch = ui.label().style(
                            "background-color: #3D5A80; width: 40px; height: 40px; border-radius: 4px;"
                        )
                        secondary_swatch = ui.label().style(
                            "background-color: #98C1D9; width: 40px; height: 40px; border-radius: 4px;"
                        )
                        accent_swatch = ui.label().style(
                            "background-color: #EE6C4D; width: 40px; height: 40px; border-radius: 4px;"
                        )
    
                    def update_color_swatches(_=None):
                        primary_swatch.style(f"background-color: {color_primary.value}; width: 40px; height: 40px; border-radius: 4px;")
                        secondary_swatch.style(f"background-color: {color_secondary.value}; width: 40px; height: 40px; border-radius: 4px;")
                        accent_swatch.style(f"background-color: {color_accent.value}; width: 40px; height: 40px; border-radius: 4px;")
    
                    color_primary.on('input', update_color_swatches)
                    color_secondary.on('input', update_color_swatches)
                    color_accent.on('input', update_color_swatches)
    
            # Fonts Inputs
            with ui.row().classes("items-center gap-4 mb-3"):
                ui.label("Fonts:").classes("text-body1 font-semibold")
                font_primary = ui.input(label="Primary", value=prefill_data.get('font_primary', "Roboto") if prefill_data else "Roboto")\
                                  .classes("w-36").style("background-color: #f0f8ff;")
                font_secondary = ui.input(label="Secondary", value=prefill_data.get('font_secondary', "Lato") if prefill_data else "Lato")\
                                  .classes("w-36").style("background-color: #f0f8ff;")
    
            layout_input = ui.input(
                label="Layout",
                value=prefill_data.get('layout', "Grid-based, two-column layout") if prefill_data else "Grid-based, two-column layout"
            ).classes("w-full mb-3").style("background-color: #f0f8ff;")
    
            with ui.column().classes("mb-3"):
                ui.label("Image Descriptions:").classes("text-body1 font-semibold mb-1")
                image_desc_primary = ui.input(label="Primary", value=prefill_data.get('image_desc_primary', "cover shot") if prefill_data else "cover shot")\
                                       .classes("w-full mb-2").style("background-color: #f0f8ff;")
                image_desc_secondary = ui.input(label="Secondary", value=prefill_data.get('image_desc_secondary', "interior shot") if prefill_data else "interior shot")\
                                         .classes("w-full mb-2").style("background-color: #f0f8ff;")
    
            with ui.row().classes("items-center gap-4 mb-3"):
                ui.label("Tags:").classes("text-body1 font-semibold")
                tags_textarea = ui.textarea(value=prefill_data.get('tags', "C++, Programming") if prefill_data else "C++, Programming")\
                                  .classes("w-full").style("background-color: #f0f8ff;")
    
            alignment_input = ui.input(
                label="Alignment",
                value=prefill_data.get('alignment', "centered") if prefill_data else "centered"
            ).classes("w-full mb-3").style("background-color: #f0f8ff;")
    
            # Execution Output
            execution_output = ui.label("").classes("mt-2")
    
            # Basic Validations and Live Updates
            def validate_title(_):
                val = title_input.value.strip()
                title_validation_label.text = "Title cannot be empty." if not val else ""
    
            def update_headline_char_count(_):
                text = headline_input.value
                length = len(text)
                if length > 100:
                    headline_char_count.text = f"{length}/100 (Too long!)"
                    headline_char_count.style("color: red")
                else:
                    headline_char_count.text = f"{length} / 100"
                    headline_char_count.style("color: black")
    
            def update_preview(_=None):
                # Extend to update any additional text preview as needed.
                pass
    
            title_input.on('change', validate_title)
            headline_input.on('change', update_headline_char_count)
            title_input.on('change', update_preview)
            headline_input.on('change', update_preview)
            subheadline_input.on('change', update_preview)
            testimonials_input.on('change', update_preview)
            prompt_textarea.on('change', update_preview)
    
            # JSON parsing helper (unchanged)
            def parse_and_fill_ui(resp_str: str):
                try:
                    data = json.loads(resp_str)
                    mod_data = data["modules"][0]  # assume first module
    
                    if "title" in mod_data:
                        title_input.value = mod_data["title"]
                        title_input.update()
                    if "headline" in mod_data:
                        headline_input.value = mod_data["headline"]
                        headline_input.update()
                    if "subheadline" in mod_data:
                        subheadline_input.value = mod_data["subheadline"]
                        subheadline_input.update()
                    if "mockup_style" in mod_data:
                        chosen_mockup_style[0] = mod_data["mockup_style"]
                    if "testimonials" in mod_data:
                        testimonials_input.value = mod_data["testimonials"]
                        testimonials_input.update()
                    if "size" in mod_data:
                        size_input.value = mod_data["size"]
                        size_input.update()
    
                    da = mod_data.get("design_attributes", {})
                    if isinstance(da, dict):
                        cp = da.get("color_palette", {})
                        if "primary" in cp:
                            color_primary.value = cp["primary"]
                            color_primary.update()
                        if "secondary" in cp:
                            color_secondary.value = cp["secondary"]
                            color_secondary.update()
                        if "accent" in cp:
                            color_accent.value = cp["accent"]
                            color_accent.update()
    
                        fn = da.get("fonts", {})
                        if "primary" in fn:
                            font_primary.value = fn["primary"]
                            font_primary.update()
                        if "secondary" in fn:
                            font_secondary.value = fn["secondary"]
                            font_secondary.update()
    
                        if "layout" in da:
                            layout_input.value = da["layout"]
                            layout_input.update()
    
                        idesc = da.get("image_descriptions", {})
                        if "primary" in idesc:
                            image_desc_primary.value = idesc["primary"]
                            image_desc_primary.update()
                        if "secondary" in idesc:
                            image_desc_secondary.value = idesc["secondary"]
                            image_desc_secondary.update()
    
                        if "tags" in da and isinstance(da["tags"], list):
                            tags_textarea.value = ", ".join(str(t) for t in da["tags"])
                            tags_textarea.update()
    
                        if "alignment" in da:
                            alignment_input.value = da["alignment"]
                            alignment_input.update()
    
                except Exception as e:
                    log_message(f"Error parsing JSON: {e}", level="error", color=ConsoleColor.RED)
    
            async def execute_api():
                spinner = None
                def create_spinner():
                    nonlocal spinner
                    loading_spinner.style("display: inline-block;")
                ui.timer(0, create_spinner, once=True)
    
                try:
                    api_key = wizard.openai_client.api_key
                    if not api_key:
                        execution_output.set_text("No API key set. Please go back and set your OpenAI API key.")
                        return
    
                    data_dir = wizard.root_directory_input.value.strip()
                    if not data_dir:
                        execution_output.set_text("No directory selected. Please go back to Step 1 and select a folder.")
                        return
    
                    persist_dir = "./client_books"
                    loop = asyncio.get_event_loop()
                    rag_result = await loop.run_in_executor(
                        None,
                        lambda: run_rag_system(api_key=api_key, persist_dir=persist_dir, data_dir=data_dir)
                    )
    
                    final_data = {
                        "structure_type": wizard.structure_type.value if wizard.structure_type else None,
                        "modules": [
                            {
                                "module_id": module_id,
                                "title": title_input.value,
                                "headline": headline_input.value,
                                "subheadline": subheadline_input.value,
                                "mockup_style": chosen_mockup_style[0],
                                "testimonials": testimonials_input.value,
                                "size": size_input.value,
                                "book_of_interest": rag_result,
                                "design_attributes": {
                                    "color_palette": {
                                        "primary": color_primary.value,
                                        "secondary": color_secondary.value,
                                        "accent": color_accent.value
                                    },
                                    "fonts": {
                                        "primary": font_primary.value,
                                        "secondary": font_secondary.value
                                    },
                                    "layout": layout_input.value,
                                    "image_descriptions": {
                                        "primary": image_desc_primary.value,
                                        "secondary": image_desc_secondary.value
                                    },
                                    "tags": [tag.strip() for tag in tags_textarea.value.split(",")],
                                    "alignment": alignment_input.value
                                }
                            }
                        ]
                    }
    
                    # Updated module prompt with new text
                    module_prompt = f"""
                    Take a deep breath and generate only one comprehensive module description for a book of interest. ACT as a holywood movie poster creator 
                    that is preparing a book marketing campaign in strict JSON format, incorporating all provided details exactly as given.
                    <Requirements>
                    Golden Rule:
                    Treat the book as more than just pages with words—it's a gateway to an experience. Every element of the campaign should convey the journey the reader will embark upon.
                    Understand the Book's Core Essence
                        Read or thoroughly research the book to grasp its central theme, narrative, and value proposition.
                        Identify the core message and the author's intent—what transformation does the reader experience after engaging with this book?
                        Summarize the book in one compelling sentence to clarify its essence for the campaign.
                    Define the Target Audience with Precision
                        Identify the book's primary and secondary audiences based on genre, themes, and style.
                        Build audience personas that detail demographics, motivations, and reading behaviors.
                        Understand emotional drivers: What does the audience seek—entertainment, education, inspiration, or transformation?
                    Craft Messaging that Resonates
                        Develop a clear value proposition: Why should someone read this book over others in the same genre?
                        Craft headlines that evoke curiosity and emotion. Lead with the book's most intriguing aspect or boldest claim.
                        Ensure subheadlines provide clarity, context, and compelling reasons to continue reading.
                        Avoid generic language like “must-read” or “unputdownable.” Instead, focus on the book's unique impact on the reader's life.
                    Visual Storytelling and Branding
                        Identify visual themes that align with the book's genre and mood (e.g., soft pastels for romance, bold contrasts for thrillers, minimalism for non-fiction).
                        Create mood boards that capture the book's essence—characters, settings, and core ideas should be visually represented.
                        Choose color schemes that evoke the desired emotional response: warm tones for comfort, cool tones for intellectual themes, vibrant accents for excitement.
                        Ensure all visual materials maintain a consistent style across platforms to reinforce brand recognition.
                    Master Tone and Voice
                        Adjust the tone to suit the genre:
                            Fiction: Imaginative, emotionally evocative.
                            Non-fiction: Authoritative yet relatable.
                            Self-help: Motivational and solution-oriented.
                            Memoir: Authentic and deeply personal.
                        Develop brand guidelines that define the campaign's voice, ensuring consistency across all materials.
                    <Good Example>
                    "structure_type": "Module",
                    "modules": 
                        "title": "The Society of Mind: Exploring the Architecture of Thought",
                        "headline": "Embark on a Journey into the Mind's Inner Workings",
                        "subheadline": "Marvin Minsky unveils a groundbreaking perspective on how simple components collaborate to create the tapestry of human thought.",
                        "mockup_style": "Open Book Display",
                        "testimonials": "A profound and fascinating book that lays down the foundations for the solution of one of the last great problems of modern science.",
                        "size": "970x600px Standard Image Header with Text",
                        "book_of_interest": "The Society of Mind by Marvin Minsky",
                        "design_attributes": 
                            "color_palette": 
                            "primary": "#2C3E50",
                            "secondary": "#8E44AD",
                            "accent": "#3498DB",
                            "fonts": 
                            "primary": "Arial",
                            "secondary": "Times New Roman",
                            "layout": "Balanced, single-column layout",
                            "image_descriptions":
                            "primary": "Cover art depicting a stylized sphere composed of interlocking geometric shapes, symbolizing the complexity and unity of the mind.",
                            "secondary": "Interior illustrations featuring interconnected diagrams and conceptual imagery that bring the book's theories to life.",
                            "tags": 
                            "cognitive science",
                            "artificial intelligence",
                            "Marvin Minsky",
                            "human cognition",
                            "alignment": "centered"
                    <Bad Example>
                    Visual: A 3D mockup of the book cover.
                    Headline: A vague, clichéd headline with overused phrases.
                    Example: "Delve into the world of endless possibilities and unleash the power of transformation."
                    Subheadline: A generic subheadline that fails to highlight specific benefits.
                    Example: "Learn everything you need to know about success and growth."
    
                    [TARGET] ALWAYS Strictly output a JSON containing all necessary information like so:
                    {json.dumps(final_data, indent=2)}
                    """
    
                    response = await loop.run_in_executor(
                        None,
                        lambda: wizard.openai_client.get_response(module_prompt, max_tokens=1050)
                    )
    
                    execution_output.set_text(response)
                    log_message("Module API call executed with RAG data included.",
                                session_id=f"MODULE_{module_id}", color=ConsoleColor.GREEN)
    
                    def parse_later():
                        parse_and_fill_ui(response)
    
                    ui.timer(0, parse_later, once=True)
    
                except Exception as e:
                    error_msg = f"Error in execute_api: {e}"
                    execution_output.set_text(error_msg)
                    log_message(error_msg, level="error", color=ConsoleColor.RED)
                finally:
                    ui.timer(0, lambda: loading_spinner.style("display: none;"), once=True)
    
            ui.button("Execute", on_click=execute_api).classes("bg-blue text-white px-4 py-2 rounded m-2")
            ui.button("Remove This Module", on_click=lambda: remove_module(wizard, module_id, module_row))\
              .classes("bg-red text-white px-4 py-2 rounded m-2")
        ui.separator().classes("my-4")
    # Save references for later use (for removal/undo)
    wizard.dynamic_modules.append({
        "id": module_id,
        "container": module_row,
        "title": title_input,
        "headline": headline_input,
        "subheadline": subheadline_input,
        "testimonials": testimonials_input,
        "prompt": prompt_textarea,
        "size": size_input,
        "color_primary": color_primary,
        "color_secondary": color_secondary,
        "color_accent": color_accent,
        "font_primary": font_primary,
        "font_secondary": font_secondary,
        "layout_input": layout_input,
        "image_desc_primary": image_desc_primary,
        "image_desc_secondary": image_desc_secondary,
        "tags_textarea": tags_textarea,
        "alignment_input": alignment_input,
        "chosen_mockup_style": chosen_mockup_style,
        "execution_output": execution_output
    })

@trace
def remove_module(wizard, module_id, container):
    # Find the module in dynamic_modules
    module = next((m for m in wizard.dynamic_modules if m["id"] == module_id), None)
    if module:
        # Ensure a list to store deleted modules exists
        if not hasattr(wizard, 'deleted_modules'):
            wizard.deleted_modules = []
        # Store current input values for undo
        wizard.deleted_modules.append({
            "module_id": module_id,
            "values": {
                "title": module["title"].value,
                "headline": module["headline"].value,
                "subheadline": module["subheadline"].value,
                "testimonials": module["testimonials"].value,
                "prompt": module["prompt"].value,
                "size": module["size"].value,
                "color_primary": module["color_primary"].value,
                "color_secondary": module["color_secondary"].value,
                "color_accent": module["color_accent"].value,
                "font_primary": module["font_primary"].value,
                "font_secondary": module["font_secondary"].value,
                "layout": module["layout_input"].value,
                "image_desc_primary": module["image_desc_primary"].value,
                "image_desc_secondary": module["image_desc_secondary"].value,
                "tags": module["tags_textarea"].value,
                "alignment": module["alignment_input"].value,
                "chosen_mockup_style": module["chosen_mockup_style"][0],
            }
        })
        container.delete()
        wizard.dynamic_modules = [m for m in wizard.dynamic_modules if m["id"] != module_id]
        ui.notify(f"Module {module_id} removed.", color="yellow")

def undo_last_module(wizard):
    if hasattr(wizard, 'deleted_modules') and wizard.deleted_modules:
        last_deleted = wizard.deleted_modules.pop()
        add_module(wizard, prefill_data=last_deleted["values"])
        ui.notify(f"Module {last_deleted['module_id']} restored.", color="green")
    else:
        ui.notify("No module to undo.", color="orange")

def setup_undo_button(wizard):
    # Create a persistent Undo Delete button if not already present.
    if not hasattr(wizard, 'undo_button'):
        wizard.undo_button = ui.button("Undo Delete", on_click=lambda: undo_last_module(wizard))\
                                .classes("bg-green text-white px-4 py-2 rounded m-2")
