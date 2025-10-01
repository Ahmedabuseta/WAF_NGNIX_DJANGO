from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def metric_card(title, value, subtitle=None, color='blue', icon=None, trend=None):
    """Render a metric card component"""
    icon_html = ""
    if icon:
        icon_html = f'<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">{icon}</svg>'
    else:
        icon_html = '''<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
        </svg>'''
    
    trend_html = ""
    if trend:
        direction_icon = ""
        if trend.get('direction') == 'up':
            direction_icon = '''<svg class="h-4 w-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 17l9.2-9.2M17 17V7H7"></path>
            </svg>'''
            trend_class = "text-green-500"
        elif trend.get('direction') == 'down':
            direction_icon = '''<svg class="h-4 w-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 7l-9.2 9.2M7 7v10h10"></path>
            </svg>'''
            trend_class = "text-red-500"
        else:
            direction_icon = '''<svg class="h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path>
            </svg>'''
            trend_class = "text-gray-500"
        
        trend_html = f'''
        <div class="mt-4">
            <div class="flex items-center">
                {direction_icon}
                <span class="{trend_class} text-sm font-medium ml-1">{trend.get("value", 0)}%</span>
                <span class="text-gray-500 dark:text-gray-400 text-sm ml-2">{trend.get("period", "")}</span>
            </div>
        </div>'''
    
    return mark_safe(f'''
    <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div class="flex items-center justify-between">
            <div>
                <h3 class="text-gray-500 dark:text-gray-400 text-sm font-medium uppercase leading-tight">{title}</h3>
                <p class="text-3xl font-bold text-gray-900 dark:text-white mt-1">{value}</p>
                {f'<p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{subtitle}</p>' if subtitle else ''}
            </div>
            <div class="text-{color}-500 dark:text-{color}-400">
                {icon_html}
            </div>
        </div>
        {trend_html}
    </div>''')


@register.simple_tag
def status_badge(text, status='default'):
    """Render a status badge component"""
    status_classes = {
        'active': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
        'success': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
        'inactive': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
        'error': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
        'danger': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
        'warning': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
        'pending': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
        'info': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
        'default': 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
    }
    
    class_name = status_classes.get(status, status_classes['default'])
    
    return mark_safe(f'''
    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {class_name}">
        {text}
    </span>''')


@register.simple_tag
def progress_bar(percentage, color='blue', height='h-2'):
    """Render a progress bar component"""
    return mark_safe(f'''
    <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full {height}">
        <div class="bg-{color}-600 {height} rounded-full transition-all duration-300" style="width: {percentage}%"></div>
    </div>''')


@register.simple_tag
def icon(name, size='w-5 h-5', class_name=''):
    """Render an icon component"""
    icons = {
        'dashboard': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5a2 2 0 012-2h4a2 2 0 012 2v6H8V5z"></path>''',
        'sites': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"></path>''',
        'rules': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>''',
        'analytics': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>''',
        'logs': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>''',
        'waf': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>''',
        'plus': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>''',
        'edit': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>''',
        'delete': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-2-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>''',
        'view': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>''',
        'search': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>''',
        'filter': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path>''',
        'sort': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"></path>''',
        'chevron-up': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"></path>''',
        'chevron-down': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>''',
        'chevron-left': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>''',
        'chevron-right': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>''',
        'menu': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>''',
        'close': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>''',
        'check': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>''',
        'alert': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>''',
        'info': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>''',
        'warning': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>''',
        'error': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>''',
        'success': '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>''',
    }
    
    icon_path = icons.get(name, '')
    
    return mark_safe(f'''
    <svg class="{size} {class_name}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        {icon_path}
    </svg>''')


@register.simple_tag
def breadcrumb(items):
    """Render a breadcrumb navigation component"""
    breadcrumb_html = '<nav class="flex" aria-label="Breadcrumb">'
    breadcrumb_html += '<ol class="inline-flex items-center space-x-1 md:space-x-3">'
    
    for i, item in enumerate(items):
        if i == 0:
            breadcrumb_html += f'''
            <li class="inline-flex items-center">
                <a href="{item.url}" class="inline-flex items-center text-sm font-medium text-gray-700 hover:text-blue-600 dark:text-gray-400 dark:hover:text-white">
                    <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"></path>
                    </svg>
                    {item.name}
                </a>
            </li>'''
        else:
            breadcrumb_html += f'''
            <li>
                <div class="flex items-center">
                    <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
                    </svg>
                    <a href="{item.url}" class="ml-1 text-sm font-medium text-gray-700 hover:text-blue-600 md:ml-2 dark:text-gray-400 dark:hover:text-white">{item.name}</a>
                </div>
            </li>'''
    
    breadcrumb_html += '</ol>'
    breadcrumb_html += '</nav>'
    
    return mark_safe(breadcrumb_html)
