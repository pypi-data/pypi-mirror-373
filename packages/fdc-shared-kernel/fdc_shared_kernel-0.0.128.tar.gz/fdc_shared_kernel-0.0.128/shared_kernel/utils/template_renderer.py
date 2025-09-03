from jinja2 import Environment, FileSystemLoader, select_autoescape

class TemplateRenderer:
    """
    A class for rendering templates from a specified directory using Jinja2.

    This class provides a way to render HTML or XML templates without relying 
    on the Flask framework's built-in rendering functions. It is useful for 
    standalone scripts, microservices, or any scenario where you need custom 
    rendering logic.

    Attributes:
        env (jinja2.Environment): The Jinja2 environment for loading and 
        rendering templates.

    Methods:
        render(template_name: str, **context) -> str:
            Renders the specified template with the provided context variables.

    Example Usage:
        >>> renderer = TemplateRenderer('path/to/your/templates')
        >>> rendered_html = renderer.render('example.html', title="My Page", content="Hello, World!")
        >>> print(rendered_html)
    """
    _instance = None
    _initialized = False

    def __new__(cls, templates_dir):
        """
        Ensures that only one instance of the TemplateRenderer class is created.
        
        Args:
            templates_dir (str): The path to the directory containing template files.

        Returns:
            TemplateRenderer: The single instance of the TemplateRenderer class.
        """
        if cls._instance is None:
            cls._instance = super(TemplateRenderer, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, templates_dir):
        """
        Initializes the Jinja2 environment if it hasn't been initialized yet.
        
        Args:
            templates_dir (str): The path to the directory containing template files.
        """
        if not self._initialized:
            self.env = Environment(
                loader=FileSystemLoader(templates_dir),
                autoescape=select_autoescape(['html', 'xml'])
            )
            self._initialized = True
    
    def render(self, template_name, **context):
        """
        Renders a template with the provided context.

        Args:
            template_name (str): The name of the template file to render.
            **context: Arbitrary keyword arguments representing variables to be 
                       passed to the template.

        Returns:
            str: The rendered template as a string.

        Raises:
            jinja2.exceptions.TemplateNotFound: If the specified template is not found.
            jinja2.exceptions.TemplateSyntaxError: If there is an error in the template's syntax.
        """
        template = self.env.get_template(template_name)
        return template.render(**context)