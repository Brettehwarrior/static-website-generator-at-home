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

def get_component(name:str) -> str:
    file_path = f'{name}.yaml'
    try:
        component = get_yaml_object(file_path)
    except:
        print(f'Couldn\'t find/parse yaml script at {file_path}')
        return f'<!-- Couldn\'t handle component {name} -->'

    return generate_component_text(component)

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

def parse_content(content_list:list) -> str:
    content_elements = []
    for element in content_list:
        if isinstance(element, str): # Ordinary paragraph
            content_elements.append(f'<p>{element}</p>')
        else: # Special object
            if element['type'] == 'component':
                component_html = get_component(f'component/{element["component"]}')
                content_elements.append(component_html)
            elif element['type'] == 'img':
                content_elements.append(make_figure_html(element, f'<img src="{element['src']}" alt="{element['alt']}">'))
            elif element['type'] == 'iframe':
                iframe_html = '<div class="iframe-embed-wrapper">\n'
                iframe_html += f'<iframe src="{element['src']}" frameborder="0" allowfullscreen></iframe>'
                iframe_html += '\n</div>'
                content_elements.append(make_figure_html(element, iframe_html))
            elif element['type'] == 'video':
                video_html = '<video controls>'
                for source in element['sources']:
                    video_html += f'<source src="{source['src']}" type="{source['type']}">'
                video_html += 'Your browser does not support video playback.</video>'
                content_elements.append(make_figure_html(element, video_html))
            elif element['type'][0] == 'h' and len(element['type']) == 2: # Headings h1, h2, etc.
                content_elements.append(f'<{element['type']}>{element['text']}</{element['type']}>')
            else:
                print(f'Warning: Unrecognized element type "{element['type']}"')
    return '\n'.join(content_elements)


def generate_component_text(page:dict) -> str:
    text = get_file_text(f"template/{page['template']}.html")
    output_text = ""
    split_text = text.split(ARG_ESCAPE_STR)
    for i, s in enumerate(split_text):
        if i % 2 == 1: # every other is an arg (assuming file doesn't start with arg)
            if s.startswith("component/"):
                output_text += get_component(s)
            elif s == 'content':
                output_text += parse_content(page[s])
            elif s not in page:
                output_text += f'<!-- Undefined page key {s} -->'
            else:
                output_text += page[s] # Assuming all vars are strings
        else:
            output_text += s
    return output_text

def generate_page_html(page:dict, output_path:str) -> None:
    final_page_text = generate_component_text(page)
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
    
    for item in target.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

def generate_website(pages: dict) -> None:
    empty_directory('output')
    copy_directory_contents('include', 'output')
    for page_name in pages:
        page_object = get_yaml_object(f'component/{pages[page_name]}.yaml')
        page_output_directory = "output"
        generate_page_html(page_object, f'{page_output_directory}/{page_name}.html')
    

if __name__ == '__main__':
    pages = get_yaml_object('pages.yaml')
    generate_website(pages)