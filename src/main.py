import os
import shutil
from pathlib import Path
import sys

from splitnodes import markdown_to_html_node


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
    if len(sys.argv) > 1:
        basepath = sys.argv[1]
    else:
        basepath = '/'

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    static_path = os.path.join(project_root, "static")
    docs_path = os.path.join(project_root, "docs")
    template_path = os.path.join(project_root, 'template.html')

    content_path = os.path.join(project_root, 'content')
    if os.path.exists(docs_path):
        shutil.rmtree(docs_path)

    os.makedirs(docs_path, exist_ok=True)

    shutil.copy(
        os.path.join(static_path, "index.css"),
        os.path.join(docs_path, "index.css"),
    )

    images_path = os.path.join(docs_path, "images")
    os.makedirs(images_path, exist_ok=True)

    for item in os.listdir(static_path):
        if item.endswith(".png"):
            src_path = os.path.join(static_path, item)
            dest_path = os.path.join(images_path, item)
            shutil.copy(src_path, dest_path)

    generate_pages_recursive(content_path, template_path, docs_path, basepath)


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


def generate_page(from_path, template_path, dest_path, new_name, basepath):
    print(f'Generating page from {from_path} to {dest_path} using {template_path}')
    nw_pth = os.path.join(dest_path, new_name)
    if not os.path.exists(dest_path):
        Path(dest_path).mkdir(parents=True, exist_ok=True)

    with open(from_path, 'r') as out_path:
        file_content = out_path.read()
        file_convert_html = markdown_to_html_node(file_content).to_html()
        h1_extract = extract_title(file_content)
    with open(template_path, 'r') as template_file:
        full_tmp = template_file.read()

    full_tmp = full_tmp.replace("{{ Title }}", h1_extract)
    full_tmp = full_tmp.replace("{{ Content }}", file_convert_html)

    full_tmp = full_tmp.replace('href="/', f'href="{basepath}')
    full_tmp = full_tmp.replace('src="/', f'src="{basepath}')

    with open(nw_pth, 'w') as f:
        f.write(full_tmp)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    for items in os.listdir(dir_path_content):
        content_path = os.path.join(dir_path_content, items)
        if os.path.isdir(content_path):
            generate_pages_recursive(content_path, template_path, dest_dir_path, basepath)
        if items.endswith('.md'):
            p = Path(content_path)
            parent_name = p.parent.name
            if parent_name == 'content':
                generate_page(content_path, template_path, dest_dir_path, 'index.html', basepath)
            elif parent_name == 'contact':
                generate_page(content_path, template_path, os.path.join(dest_dir_path, 'contact'), 'index.html',
                              basepath)
            else:
                generate_page(content_path, template_path, os.path.join(dest_dir_path, 'blog', parent_name),
                              'index.html', basepath)


if __name__ == "__main__":
    main()
