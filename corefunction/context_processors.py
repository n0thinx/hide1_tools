def dynamic_breadcrumbs(request):
    path_parts = request.path.strip('/').split('/')
    
    breadcrumbs = []

    # Add "Dashboard" for the homepage
    if not path_parts or request.path == '/':
        breadcrumbs.append({'name': 'Dashboard', 'url': '/'})
    else:
        # Always start with the Dashboard
        breadcrumbs.append({'name': 'Dashboard', 'url': '/'})
        
        for index, part in enumerate(path_parts):
            display_name = part.replace('_', ' ').title()
            url = '/' + '/'.join(path_parts[:index + 1]) + '/'
            breadcrumbs.append({'name': display_name, 'url': url})
    
    return {'breadcrumbs': breadcrumbs}