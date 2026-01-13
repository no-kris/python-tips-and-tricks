# Python Tips & Tricks Blog

A modern, lightweight blog application built with FastAPI and Jinja2 templates. This platform is designed to share valuable Python programming skills, tips, and tricks.

## 🚀 Features

- **Dynamic Content**: Posts are served from a JSON-based data store.
- **Custom Jinja2 Filters**: Includes a custom `format_date` filter for flexible date presentation.
- **Mobile Responsive**: Built with a custom CSS utility system and resets for a premium feel.
- **Performance Focused**: Optimized style loading with separate utility, variable, and reset sheets.
- **Themable**: Centralized design tokens using CSS variables for easy customization.

## 🛠️ Technology Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.8+)
- **Templating**: [Jinja2](https://jinja.palletsprojects.com/)
- **Styling**: Vanilla CSS with a custom utility-first approach
- **Icons/Fonts**: Google Fonts (Montserrat & Nunito)

## 📁 Project Structure

```text
fastapi_blog/
├── main.py           # Application entry point & route definitions
├── utils.py          # Helper functions & Jinja2 filters
├── snippets.json     # Data store for blog posts
├── static/           # Static assets
│   ├── css/          # Modular CSS (variables, utils, main)
│   └── js/           # Client-side logic
└── templates/        # Jinja2 HTML templates
```

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) (recommended for package management)

### Running Locally

1. **Install dependencies**:

   ```bash
   uv sync
   ```

2. **Start the development server**:

   ```bash
   uv run fastapi dev main.py
   ```

3. **Access the application**:
   Open your browser and navigate to `http://127.0.0.1:8000`.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
