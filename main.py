import yaml
from pathlib import Path
import shutil

ARG_ESCAPE_STR = '%'

def get_yaml_object(path : str) -> dict:
    y = None
    with open(path, 'r') as f:
        y = yaml.safe_load(f)
    return y

def write_text_to_file(text:str, path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w+') as f:
        f.write(text)

def get_file_text(path:str) -> str:
    text : str = ""
    with open(path, 'r') as f:
        text = f.read()
    return text

def get_component(name:str, input_directory:str, variable_overrides:dict = {}) -> str:
    file_path = f'{input_directory}/{name}.yaml' # TODO: Don't include component/ in name
    try:
        component = get_yaml_object(file_path)
    except:
        print(f'Couldn\'t find/parse yaml script at {file_path}')
        return f'<!-- Couldn\'t handle component {name} -->'

    for var in variable_overrides:
        component[var] = variable_overrides[var]

    return generate_component_text(component, input_directory)

def make_figure_html(element, figure_html):
    output = ''
    output += '<figure>'
    output += '<div class="figure-content-wrapper">'
    output += figure_html
    output += '</div>'
    if 'caption' in element:
        output += f'<figcaption>{element['caption']}</figcaption>'
    output += '</figure>'
    return output

def parse_object(object:any, html_tag_for_raw_string:str=None) -> str:
    if isinstance(object, str): # Just text
        if html_tag_for_raw_string:
            return f'<{html_tag_for_raw_string}>{object}</{html_tag_for_raw_string}>'
        return object
    
    if object['type'] == 'component':
        variable_overrides = object['variables']
        component_html = get_component(f'component/{object["component"]}', input_directory, variable_overrides)
        return (component_html)
    
    if object['type'] == 'img':
        return (make_figure_html(object, f'<img src="{object['src']}" alt="{element['alt']}">'))
    
    if object['type'] == 'iframe':
        iframe_html = '<div class="iframe-embed-wrapper">\n'
        iframe_html += f'<iframe src="{object['src']}" frameborder="0" allowfullscreen></iframe>'
        iframe_html += '\n</div>'
        return (make_figure_html(object, iframe_html))
    
    if object['type'] == 'video':
        video_html = '<video controls>'
        for source in object['sources']:
            video_html += f'<source src="{source['src']}" type="{source['type']}">'
        video_html += 'Your browser does not support video playback.</video>'
        return (make_figure_html(object, video_html))
    
    if object['type'][0] == 'h' and len(object['type']) == 2: # Headings h1, h2, etc.
        return (f'<{object['type']}>{object['text']}</{object['type']}>')
    
    print(f'Warning: Unrecognized object type "{object['type']}"')
    return f"<!-- Couldn't parse type {object['type']} -->"

def parse_object_list(content_list:list) -> str:
    content_elements = []
    for element in content_list:
        content_elements.append(parse_object(element, 'p')) # Strings in lists are paragraphs
    return '\n'.join(content_elements)


def generate_component_text(page:dict, input_directory:str) -> str:
    text = get_file_text(f"{input_directory}/template/{page['template']}.html")
    output_text = ""
    split_text = text.split(ARG_ESCAPE_STR)
    for i, s in enumerate(split_text):
        if i % 2 == 1: # every other is an arg (assuming file doesn't start with arg)
            if s.startswith("component/"):
                output_text += get_component(s, input_directory)
            elif s == 'content':
                output_text += parse_object_list(page[s])
            elif s not in page:
                output_text += f'<!-- Undefined page key {s} -->'
            else:
                output_text += parse_object(page[s])
        else:
            output_text += s
    return output_text

def generate_page_html(page:dict, input_directory:str, output_path:str) -> None:
    final_page_text = generate_component_text(page, input_directory)
    write_text_to_file(final_page_text, output_path)

def copy_directory_contents(src_path:str, dest_path:str) -> None:
    src = Path(src_path)
    dest = Path(dest_path)
    dest.mkdir(parents=True, exist_ok=True)
    
    for item in src.iterdir():
        if item.is_dir():
            shutil.copytree(item, dest / item.name, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest / item.name)


def empty_directory(path: str) -> None:
    """Remove all files and folders in a directory."""
    target = Path(path)
    if not target.exists():
        return
    
    for item in target.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

def generate_website(input_directory: str, output_directory) -> None:
    pages = get_yaml_object(f'{input_directory}/pages.yaml')
    empty_directory(output_directory)
    copy_directory_contents(f'{input_directory}/include', output_directory)
    for page_name in pages:
        page_object = get_yaml_object(f'{input_directory}/component/{pages[page_name]}.yaml')
        generate_page_html(page_object, input_directory, f'{output_directory}/{page_name}.html')
    

if __name__ == '__main__':
    input_directory = 'input'
    output_directory = 'output'
    generate_website(input_directory, output_directory)