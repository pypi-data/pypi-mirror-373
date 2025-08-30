from jinja2 import Environment, FileSystemLoader

templates_dir = "app/templates"

file_loader = FileSystemLoader(templates_dir)
tpl_env = Environment(loader=file_loader, enable_async=True)
