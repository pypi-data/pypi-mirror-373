from django.template import loader
from django.http import HttpResponse, HttpRequest
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Callable, Any, Optional, Dict


class ViteLoader:
    """
    Class to support Vite SSR (Server-Side Rendering) for Django templates.
    """

    @staticmethod
    def render(
        template_name: str, 
        context: Optional[Dict[str, Any]] = None, 
        request: Optional[HttpRequest] = None, 
        wrapper: Optional[str] = None, 
        vite_path: Optional[Path] = None, 
        render_func: Optional[Callable] = None
    ) -> str:
        """
        Renders a Django template and injects Vite-generated JS and CSS assets into the HTML.
        
        Args:
            template_name (str): The name of the Django template to render. Example: `index.html`.
            context (dict, optional): Context data to pass to the template. Example: `{"name": "Joe", "age": 30}`.
            request (HttpRequest, optional): Django `HttpRequest` object, if available.
            wrapper (str, optional): Optional wrapper HTML to inject around the React root div. 
                If defined, you must describe the `<root/>` in your wrapper. 
                Example: `<div id="root-wrapper"><root/></div>`.
            vite_path (Path, optional): Custom path to the Vite-generated index.html file.
            render_func (Callable, optional): Custom render function to use instead of Django's default.
            
        Returns:
            str: The rendered HTML string with Vite assets and React root div injected.
            
        Raises:
            FileNotFoundError: If the Vite-generated index.html file is not found.
        """
        if context is None:
            context = {}

        base_dir = Path(__file__).resolve().parent.parent
        print('Default basedir: ', base_dir)

        if vite_path:
            vite_index_path = vite_path / "index.html"
        else:
            vite_index_path = base_dir / "static" / "web" / "index.html"

        if not vite_index_path.exists():
            raise FileNotFoundError(f"File index.html at ({vite_index_path}) not found.")

        with open(vite_index_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, "html.parser")
        assets = {
            "js": [script["src"] for script in soup.find_all("script", src=True)],
            "css": [link["href"] for link in soup.find_all("link", rel="stylesheet")],
        }
        
        if render_func:
            rendered_string = render_func(template_name, context, request)
        else:
            rendered_string = loader.render_to_string(template_name, context, request)
        
        asset_injection = ""
        build_time = int(vite_index_path.stat().st_mtime)
        django_context = str(context).replace("'", '"')
        asset_injection += f'<script id="django-context" type="application/json">{django_context}</script>\n'
        
        for css in assets["css"]:
            asset_injection += f'<link rel="stylesheet" href="/static/web{css}?bid={build_time}">\n'
        for js in assets["js"]:
            asset_injection += f'<script type="module" src="/static/web{js}?bid={build_time}"></script>\n'
            
        asset_injection += "</head>"
        
        rendered_string = rendered_string.replace("</head>", asset_injection)

        if wrapper:
            react_root = wrapper.replace("<root/>", '<div id="root"></div>')
        else:
            react_root = '<div id="root"></div>'
        
        react_root += "</body>"
        
        rendered_string = rendered_string.replace("</body>", react_root)

        return rendered_string


def vite_render(
    template_name: str, 
    context: Optional[Dict[str, Any]] = None, 
    request: Optional[HttpRequest] = None,
    **kwargs
) -> str:
    """
    Renders a Django template with Vite SSR (Server-Side Rendering) support.
    
    Args:
        template_name (str): The name of the Django template to render. Example: `index.html`.
        context (dict, optional): Context data to pass to the template. Example: `{"name": "Joe", "age": 30}`.
        request (HttpRequest, optional): Django `HttpRequest` object, if available.
        **kwargs: Additional arguments to pass to ViteLoader.render.
        
    Returns:
        str: The rendered HTML string with Vite assets and React root div injected.
        
    Raises:
        FileNotFoundError: If the Vite-generated index.html file is not found.
    """
    return ViteLoader.render(template_name, context, request, **kwargs)


def vite_response(
    template_name: str, 
    context: Optional[Dict[str, Any]] = None, 
    request: Optional[HttpRequest] = None,
    **kwargs
) -> HttpResponse:
    """
    Return a Django HttpResponse with SSR Vite-rendered content.
    
    Args:
        template_name (str): The name of the Django template to render. Example: `index.html`.
        context (dict, optional): Context data to pass to the template. Example: `{"name": "Joe", "age": 30}`.
        request (HttpRequest, optional): Django `HttpRequest` object, if available.
        **kwargs: Additional arguments to pass to ViteLoader.render.
        
    Returns:
        HttpResponse: The Vite-rendered HTML content wrapped in a Django HttpResponse.
        
    Raises:
        FileNotFoundError: If the Vite-generated index.html file is not found.
    """
    return HttpResponse(vite_render(template_name, context, request, **kwargs))