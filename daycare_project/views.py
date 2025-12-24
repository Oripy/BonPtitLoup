from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from admin_panel.models import WelcomePage
import markdown


def home(request):
    welcome_page_obj = WelcomePage.get_instance()
    # Convert Markdown to HTML
    html_content = markdown.markdown(
        welcome_page_obj.content,
        extensions=['extra', 'codehilite', 'nl2br']
    )
    
    context = {
        'welcome_page': welcome_page_obj,
        'html_content': html_content,
    }
    return render(request, 'admin_panel/welcome_page.html', context)

