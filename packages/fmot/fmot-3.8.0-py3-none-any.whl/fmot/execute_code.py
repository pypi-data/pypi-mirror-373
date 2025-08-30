import sys
from os.path import basename
from io import StringIO
from docutils.parsers.rst import Directive
from docutils import nodes


class ExecDirective(Directive):
    """Execute the specified python code and insert the output into the document"""

    has_content = True

    def run(self):
        oldStdout, sys.stdout = sys.stdout, StringIO()
        try:
            exec("\n".join(self.content))
            block = nodes.literal_block(text=sys.stdout.getvalue())
            return [block]
        except Exception as e:
            return [
                nodes.error(
                    None,
                    nodes.literal_block(
                        text=f"Unable to execute python code {self.content}"
                    ),
                    nodes.paragraph(text=str(e)),
                )
            ]
        finally:
            sys.stdout = oldStdout


class ExecAsBulletsDirective(Directive):
    """Execute the specified python code. Each output line is inserted as a bullet point"""

    has_content = True

    def run(self):
        oldStdout, sys.stdout = sys.stdout, StringIO()
        try:
            exec("\n".join(self.content))

            bullets = nodes.bullet_list()
            output = sys.stdout.getvalue()

            for item in output.split("\n"):
                if len(item) != 0:
                    litem = nodes.list_item()
                    litem.append(nodes.literal(text=item))
                    bullets.append(litem)
            return [bullets]

        except Exception as e:
            return [
                nodes.error(
                    None,
                    nodes.literal_block(
                        text=f"Unable to execute python code {self.content}"
                    ),
                    nodes.paragraph(text=str(e)),
                )
            ]
        finally:
            sys.stdout = oldStdout


def setup(app):
    app.add_directive("exec", ExecDirective)
    app.add_directive("exec_as_bullets", ExecAsBulletsDirective)
