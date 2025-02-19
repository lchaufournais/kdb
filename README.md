# A+ Content Plan Generator

This project is an A+ Content Plan Generator built using NiceGUI and OpenAI API, designed to streamline the creation of marketing content for books and other materials.

## ✨Features

Multi-step onboarding wizard with modular customization.

Integration with OpenAI API for generating content (headlines, descriptions, etc.).

Parallel API calls to OpenAI for faster content generation.

Modular design with reusable components.

## 🛠️ Requirements

Python 3.12+

NiceGUI

OpenAI Python SDK (v1.0.0 or above)

## 📦 Installation

    pip install -r requirements.txt

## 🚀 Usage

    python wizard/ui_builder.py

The application will run on http://localhost:8080 by default.

## 📝 Steps Overview

Basic Setup: Input files, genre selection, and OpenAI API key.

Module Structure and Type: Choose how to build content modules.

Module Contents: Customize headlines, subheadlines, and visual content.

Content Generation and Refining: Generate content via OpenAI and refine it.

Final Output: Review and finalize the generated content.

## ⚙️ Configuration

OpenAI API Key: Set via the application UI.

Modules: Pre-configured with size, titles, and content templates.

## 📂 Code Structure

    wizard/ui_builder.py: Main UI and workflow logic.

    wizard/modules.py: Module creation and customization logic.

    openai_client.py: OpenAI API integration.

    file_manager.py: File and directory handling utilities.

    logging_utils.py: Logging configurations.

## 🛠️ Troubleshooting

Ensure OpenAI API key is valid and set.

Verify that OpenAI SDK is v1.0.0 or above.

For API issues, refer to OpenAI Migration Guide.

## 📜 License

This project is licensed under the MIT License.

## 🙌 Acknowledgments

NiceGUI Documentation

OpenAI API Documentation

## Made by Ravenyr 🚀

