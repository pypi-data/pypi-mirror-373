import os

from jinja2 import Template

from pixBoards.log_utils import setup_logger

from . import __version__

logger = setup_logger(__name__)

from pixBoards.classes import board

imageBlock = """
<div class="masonry-item">
    <a href="{{ media_path }}" onclick="copyToClipboard('{{ hash }}'); event.preventDefault();">
        <img src="{{ media_path }}" alt="{{ hash }}" loading="lazy">
    </a>
</div>
"""

videoBlock = """
<div class="masonry-item">
    <video controls>
        <source src="{{ media_path }}" type="video/mp4" loading="lazy">
        Your browser does not support the video tag. {{ hash }}
    </video>
</div>
"""

from datetime import datetime

now = datetime.now()

timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

from pixBoards.config_loader import config

padding = config["padding"]
masterDir = config["masterDir"]

imgTemplate = Template(imageBlock)
vidTemplate = Template(videoBlock)


templates_folder_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "templates"
)

with open(os.path.join(templates_folder_path, "index_template.html")) as f:
    idxTempl = f.read()

indexTemplate = Template(idxTempl)


def create_css_file(
    target_directory,
    css_template_path=os.path.join(templates_folder_path, "template.css"),
):
    logger.debug(f"creating css file at {target_directory}")
    with open(css_template_path, "r", encoding="utf-8") as template_file:
        template = Template(template_file.read())
        rendered_css = template.render(config)
    with open(
        os.path.join(target_directory, "styles.css"), "w", encoding="utf-8"
    ) as output_file:
        output_file.write(rendered_css)


def create_js_file(
    target_directory,
    js_template_path=os.path.join(templates_folder_path, "template.js"),
):
    logger.debug(f"creating js file at {target_directory}")
    with open(js_template_path, "r", encoding="utf-8") as template:
        js_content = template.read()
    with open(os.path.join(target_directory, "script.js"), "w", encoding="utf-8") as f:
        f.write(js_content)


def build_breadcrumb(b):
    parts = b.name.split("_~")
    breadcrumb = ['<a href="index.html">index</a>']  # root always first

    path = []
    for i, part in enumerate(parts):
        path.append(part)
        link = "_~".join(path) + f"_{1:0{padding}d}" + ".html"
        if i == len(parts) - 1:
            # last one: no link, just text
            breadcrumb.append(part)
        else:
            breadcrumb.append(f'<a href="{link}">{part}</a>')

    # join with separators
    return " &raquo; ".join(breadcrumb)


def create_index_file(
    root_boards,
    target_directory,
    index_name="",
    sub_index=False,
    template_path=os.path.join(templates_folder_path, "index_template.html"),
):
    if not sub_index:
        index_file = os.path.join(target_directory, "index.html")
    else:
        index_file = os.path.join(
            target_directory, f"{index_name}_{1:0{padding}d}.html"
        )

    with open(template_path, "r", encoding="utf-8") as template:
        index_template = template.read()

    # back_href = "index.html"
    def board_tree_to_html(boards, depth=0):
        html_parts = ["<ul>\n"]
        for b in boards:
            # if b.parent:
            # back_href = f"{b.parent}_{1:0{padding}d}.html"

            link = f"{b.name}_{1:0{padding}d}.html"
            img_no = b.no_of_imgs
            html_parts.append(
                f'<li><span style="white-space: pre; color:#5b2c5b; font-family:\'Lucida Console\', monospace;">[{img_no:<3}] </span><a class="link" href="{link}"> {b.clean_name}</a>\n'
            )

            if b.nested_boards:
                html_parts.append(board_tree_to_html(b.nested_boards, depth + 1))
            html_parts.append("</li>\n")
        html_parts.append("</ul>\n")
        return "".join(html_parts)

    nested_html = board_tree_to_html(root_boards)

    # create a dummy board with all the root boards.
    if not sub_index:
        # create a dummy board for the root index
        dummy = board("", output_file_loc="", image_paths=[])
        breadcrumb = build_breadcrumb(dummy)
    else:
        # use the actual board (name passed in)
        dummy = board(index_name, output_file_loc="", image_paths=[])
        breadcrumb = build_breadcrumb(dummy)

    back_button = f'<nav class="breadcrumbs">{breadcrumb}</nav>'

    html_content = indexTemplate.render(
        index_links=nested_html,
        back_button=back_button,
        version=__version__,
        timestamp=timestamp,
    )

    with open(index_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    logger.debug(f"index file created, location is - {index_file}")


with open(os.path.join(templates_folder_path, "template.html"), encoding="utf-8") as f:
    base_template = Template(f.read())


def create_html_file(p):
    media_blocks = []
    # output_file = p.file_location
    os.makedirs(os.path.dirname(p.file_location), exist_ok=True)
    no_of_imgs = len(p.images)
    no_of_imgs_board = len(p.bname.image_paths)

    # back_href = "index.html" # this will be changed
    reverse_map = {}
    if getattr(p.bname, "hashmap", None):
        reverse_map = {link: h for h, link in p.bname.hashmap.items()}

    for idx, media_path in enumerate(p.images):
        ext = os.path.splitext(media_path)[1].lower()
        hash = reverse_map.get(media_path, media_path)

        if ext in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".heic"):
            block = imgTemplate.render(media_path=media_path, hash=hash)
        elif ext in (".mp4", ".avi", ".mov", ".webm"):
            block = vidTemplate.render(media_path=media_path, hash=hash)
        else:
            block = imgTemplate.render(media_path=media_path, hash=hash)

        media_blocks.append(block)

    pagination_html = ""
    if p.total_pages > 1:
        pagination_html += '<div class="pagination">\n'

        # First page link
        if p.page_number > 6:
            pagination_html += f'<a href="{os.path.basename(p.file_location).replace(f"_{p.page_number:0{padding}}", f"_001")}">First</a> '

        pagination_html += "&nbsp;"  # add space cuz too conjusted

        # Page links around current page
        start_page = max(1, p.page_number - 5)
        end_page = min(p.total_pages, p.page_number + 5)

        for i in range(start_page, end_page + 1):
            page_file = os.path.basename(p.file_location).replace(
                f"_{p.page_number:0{padding}}", f"_{i:0{padding}}"
            )
            if i == p.page_number:
                pagination_html += f"<strong>{i}</strong> "
            else:
                pagination_html += f'<a href="{page_file}">{i}</a> '

        pagination_html += "&nbsp;"  # add space cuz too conjusted

        # Last page link
        if p.page_number < p.total_pages - 2:
            last_page_file = os.path.basename(p.file_location).replace(
                f"_{p.page_number:0{padding}}", f"_{p.total_pages:0{padding}}"
            )
            pagination_html += f'<a href="{last_page_file}">Last</a> '

        # Jump-to-page input
        pagination_html += """
        <form method="get" style="display:inline;" onsubmit="window.location.href=this.action.replace('PAGE', this.page.value); return false;">
            <input type="number" name="page" min="1" max="{total}" style="width:50px;">
            <input type="submit" value="Go">
        </form>
        """.format(
            total=p.total_pages
        )

        pagination_html += f"""
        <button type="button" onclick="
            const total={p.total_pages};
            const randPage = Math.floor(Math.random() * total) + 1;
            const newFile = '{os.path.basename(p.file_location).replace(f'_{p.page_number:0{padding}}', '_PAGE')}';
            window.location.href = newFile.replace('PAGE', randPage.toString().padStart({padding}, '0'));
        ">
            Random Page
        </button>
        """
        pagination_html += "</div>"

        # if p.bname.parent:
        #     back_href = f"{p.bname.parent}_{1:0{padding}d}.html"

    breadcrumb = build_breadcrumb(p.bname)
    back_button = f'<nav class="breadcrumbs">{breadcrumb}</nav>'

    final_html = base_template.render(
        title=f"Page {p.page_number} of {p.total_pages}",
        media_content="\n".join(media_blocks),
        pagination=pagination_html,
        back_button=back_button,
        version=__version__,
        timestamp=timestamp,
        no_of_imgs=no_of_imgs,
        no_of_imgs_board=no_of_imgs_board,
        col_count=config["col_count"],
    )

    logger.debug("Writing file at: " + p.file_location)
    with open(p.file_location, "w", encoding="utf-8") as f:
        f.write(final_html)
