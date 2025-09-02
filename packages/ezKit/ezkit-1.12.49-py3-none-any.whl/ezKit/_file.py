from loguru import logger

from . import utils


def markdown_to_html(markdown_file: str, html_file: str, header_file: str = "markdown.html") -> bool:
    """Markdown to HTML"""

    # Markdown to HTML
    # 使用 MacDown 生成 HTML, 然后提取样式到 markdown.html
    # pandoc 生成的 HTML 默认 max-width: 36em, 如果表格内容很长, 会导致表格样式难看
    # 所以在 markdown.html 的 body{...} 中添加配置 max-width: unset, 解决内容过长的样式问题
    # 所有 a 标签添加 text-decoration: none; 去除链接下划线
    # pandoc --no-highlight -s --quiet -f markdown -t html -H markdown.html -o data.html data.md

    info: str = "markdown to html"

    logger.info(f"{info} ......")

    try:

        result = utils.shell(
            f"pandoc --no-highlight -s --quiet -f markdown -t html -H {header_file} -o {html_file} {markdown_file}"
        )

        if result is None or result.returncode != 0:
            logger.error(f"{info} [failure]")
            return False

        logger.success(f"{info} [success]")
        return True

    except Exception as e:
        logger.error(f"{info} [failure]")
        logger.exception(e)
        return False
