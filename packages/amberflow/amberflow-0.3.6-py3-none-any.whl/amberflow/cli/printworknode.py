import inspect
import textwrap

from amberflow.worknodes import templateworknode

__all__ = ("printworknode",)


def printworknode():
    """
    Prints the source code of the TemplateWorkNode class.
    """
    source_code = inspect.getsource(templateworknode)

    source_code = source_code.replace("# from ", """from """, 1)
    source_code = source_code.replace(
        "class TemplateWorkNode(object):",
        """@worknodehelper(file_exists=True, input_artifact_types=(BaseArtifact,), output_artifact_types=(BaseArtifact,))
class TemplateWorkNode(BaseSingleWorkNode):""",
        1,
    )
    print(textwrap.dedent(source_code))


if __name__ == "__main__":
    printworknode()
