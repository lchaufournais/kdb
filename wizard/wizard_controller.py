# wizard/wizard_controller.py

import uuid
from logging_utils import log_message, ConsoleColor, trace

@trace
class WizardController:
    def __init__(self):
        self.current_step = 1
        self.session_id = uuid.uuid4().hex
        self.openai_client = None  # Save the instance in the controller

        # Step 1 fields
        self.root_directory_input = None
        self.subfolder_selection_container = None
        self.subfolder_checkboxes = []
        self.book_type_input = None
        self.bonus_checkbox = None

        # Step 2: Dynamic module customization
        self.module_customization_container = None
        self.dynamic_modules = []  # list of module dictionaries

        # Step 3: Bonus modules
        self.bonus_customization_container = None
        self.bonus_inputs = []

        # Step 4: Headlines and layout
        self.headline_output = None
        self.refinement_prompt = ""
        self.proposed_headlines = []
        self.chosen_layout_json = None
        self.final_layout = None

        # UI Step containers (for direct manipulation if needed)
        self.step1 = None
        self.step2 = None
        self.step3 = None
        self.step4 = None

    def next_step(self, wizard_ui):
        """Advance to the next step with conditional logic."""
        try:
            if self.current_step == 1:
                self.current_step = 2
                wizard_ui.next()  # using stepper built-in navigation
                log_message("Proceeding from Step 1 to Step 2.", session_id=self.session_id)
            elif self.current_step == 2:
                if self.bonus_checkbox and self.bonus_checkbox.value:
                    self.current_step = 3
                    wizard_ui.next()
                    log_message("Bonus enabled: Proceeding to Step 3.", session_id=self.session_id)
                else:
                    self.current_step = 4
                    wizard_ui.next()
                    log_message("Bonus disabled: Skipping Step 3 and proceeding to Step 4.", session_id=self.session_id)
            elif self.current_step == 3:
                self.current_step = 4
                wizard_ui.next()
                log_message("Proceeding from Step 3 to Step 4.", session_id=self.session_id)
        except Exception as e:
            log_message(f"Error in next_step: {e}", level="error", session_id=self.session_id)

    def prev_step(self, wizard_ui):
        """Return to the previous step with conditional logic."""
        try:
            if self.current_step == 4:
                if self.bonus_checkbox and self.bonus_checkbox.value:
                    self.current_step = 3
                    wizard_ui.previous()
                    log_message("Going back from Step 4 to Step 3.", session_id=self.session_id)
                else:
                    self.current_step = 2
                    wizard_ui.previous()
                    log_message("Going back from Step 4 to Step 2.", session_id=self.session_id)
            elif self.current_step == 3:
                self.current_step = 2
                wizard_ui.previous()
                log_message("Going back from Step 3 to Step 2.", session_id=self.session_id)
            elif self.current_step == 2:
                self.current_step = 1
                wizard_ui.previous()
                log_message("Going back from Step 2 to Step 1.", session_id=self.session_id)
        except Exception as e:
            log_message(f"Error in prev_step: {e}", level="error", session_id=self.session_id)
