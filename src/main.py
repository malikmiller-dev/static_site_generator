import os
import shutil
from pathlib import Path
import sys

from src.splitnodes import markdown_to_html_node

if len(sys.argv) < 2:
    basepath = '/'
else:
    basepath = sys.argv[1]


def copy_directory(src, dest):
    if not os.path.exists(dest):
        os.mkdir(dest)

    for name in os.listdir(src):
        src_path = os.path.join(src, name)
        dest_path = os.path.join(dest, name)

        if os.path.isfile(src_path):
            shutil.copy(src_path, dest_path)

        elif os.path.isdir(src_path):
            copy_directory(src_path, dest_path)


def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    static_path = os.path.join(project_root, "static")
    docs_path = os.path.join(project_root, "docs")
    template_path = os.path.join(project_root, 'template.html')

    content_path = os.path.join(project_root, 'content')
    generate_pages_recursive(content_path, template_path, docs_path)
    for items in os.listdir(static_path):
        if items.endswith('.png'):
            abs_images = os.path.join(project_root, f'static//{items}')
            copy_and_rename(abs_images, f'{docs_path}//images', items)


def extract_title(markdown):
    for line in markdown.split('\n'):
        if line.startswith('# '):
            return line.strip()
        else:
            continue
    raise Exception('No H1 Header Found')


def copy_and_rename(src_path, dest_path, new_name):
    try:
        os.makedirs(dest_path, exist_ok=True)
        temp_path = shutil.copy(src_path, dest_path)
        new_path = os.path.join(dest_path, new_name)
        os.rename(temp_path, new_path)
        print(f'Successfully copied and renamed: {src_path} to {new_path}')
    except FileNotFoundError:
        print(f'Error: Source file {src_path} not found')
    except PermissionError:
        print(f'Error: Permission denied when copying {src_path}')
    except Exception as e:
        print(f'Unexpected Error: {e}')


def generate_page(from_path, template_path, dest_path, new_name):
    print(f'Generating page from {from_path} to {dest_path} using {template_path}')
    nw_pth = os.path.join(dest_path, new_name)
    if not os.path.exists(dest_path):
        Path(dest_path).mkdir(parents=True, exist_ok=True)
    if new_name not in os.listdir(dest_path):
        copy_and_rename(template_path, dest_path, new_name)

    with open(from_path, 'r') as out_path:
        file_content = out_path.read()
        file_convert_html = markdown_to_html_node(file_content).to_html()
        h1_extract = extract_title(file_content)
    with open(nw_pth, 'r') as rd_tmp_pth:
        full_tmp = rd_tmp_pth.read()
        tmp_hd = [temp.split('<title>') for temp in full_tmp.split('</title>')]
        tmp_content = [temp.split('<article>') for temp in full_tmp.split('</article>')]
        tmp_hd_repl = tmp_hd[0][1]
        tmp_content_repl = tmp_content[0][1]

    replacements = {
        tmp_hd_repl: h1_extract,
        tmp_content_repl: file_convert_html,
        '<a href="/': f'<a href="{basepath}',
        '<src="/': f'<src="{basepath}"'
    }

    for old, new in replacements.items():
        full_tmp = full_tmp.replace(old, new)

    with open(nw_pth, 'w') as f:
        f.write(full_tmp)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    for items in os.listdir(dir_path_content):
        content_path = os.path.join(project_root, f'{dir_path_content}\\{items}')
        if os.path.isdir(content_path):
            generate_pages_recursive(content_path, template_path, dest_dir_path)
        if items.endswith('.md'):
            p = Path(content_path)
            parent_name = p.parent.name
            if parent_name == 'content':
                generate_page(content_path, template_path, dest_dir_path, 'index.html')
            elif parent_name == 'contact':
                generate_page(content_path, template_path, f'{dest_dir_path}\\contact', 'index.html')
            else:
                generate_page(content_path, template_path, f'{dest_dir_path}\\blog\\{parent_name}',
                              'index.html')


if __name__ == "__main__":
    main()
