from pathlib import Path
from smali import SmaliReader, SmaliWriter, MethodWriter
from smali.visitor import MethodVisitor, AnnotationVisitor
from smali.base import AccessType, Token

from dataclasses import dataclass


@dataclass
class Method:
    """Method class
    """
    prototype: str
    content: str


def get_smali_file_from_class(directory : str | Path, classname : str) -> Path:
    """
    Get the path of apk entrypoint on the smali files.
    """
    if isinstance(directory, str):
        directory = Path(directory)
    files_at_path = directory.iterdir()

    for file in files_at_path:
        if file.name.startswith("smali") and file.is_dir():
            tmp = file / (classname.replace(".", "/") + ".smali")
            if tmp.is_file():
                return tmp
    return None


class SmaliMethodRemover(MethodWriter):
    """SmaliMethodRemover
    """

    def __init__(self, delegate: "MethodVisitor" = None, indent=0) -> None:
        super().__init__(delegate)

    def visit_annotation(self, access_flags: int, signature: str) -> AnnotationVisitor:
        return None

    def visit_block(self, name: str) -> None:
        pass

    def visit_line(self, number: int) -> None:
        pass

    def visit_goto(self, block_name: str) -> None:
        pass

    def visit_instruction(self, ins_name: str, args: list) -> None:
        pass

    def visit_param(self, register: str, name: str) -> None:
        pass

    def visit_comment(self, text: str) -> None:
        pass

    def visit_restart(self, register: str) -> None:
        pass

    def visit_locals(self, local_count: int) -> None:
        pass

    def visit_local(self, register: str, name: str, descriptor: str, full_descriptor: str) -> None:
        pass

    def visit_prologue(self) -> None:
        pass

    def visit_catch(self, exc_name: str, blocks: tuple) -> None:
        pass

    def visit_catchall(self, exc_name: str, blocks: tuple) -> None:
        pass

    def visit_registers(self, registers: int) -> None:
        pass

    def visit_return(self, ret_type: str, args: list) -> None:
        pass

    def visit_invoke(self, inv_type: str, args: list, owner: str, method: str) -> None:
        pass

    def visit_array_data(self, length: str, value_list: list) -> None:
        pass

    def visit_packed_switch(self, value: str, blocks: list) -> None:
        pass

    def visit_sparse_switch(self, branches: dict) -> None:
        pass

    def visit_eol_comment(self, text: str) -> None:
        pass

    def visit_end(self) -> None:
        """visit_end
        """
        # self.cache.apply_code_cache(True)
        super().visit_end()


class SmaliModifier(SmaliWriter):
    """Public standard implementation of a Smali Source-Code writer."""

    """The code cache to use."""

    def __init__(self, reader: SmaliReader = None, indent=0, methods=None) -> None:
        super().__init__()
        self.methods = methods
        self.method_remove = False

    def visit_method(
        self, name: str, access_flags: int, parameters: list, return_type: str
    ) -> MethodVisitor:
        flags = " ".join(AccessType.get_names(access_flags))
        params = "".join(parameters)
        desc = f".{Token.METHOD} {flags} {name}({params}){return_type}"
        for m in self.methods:
            if m.prototype == desc:
                self.method_remove = True
                # delegate = super().visit_method(name, access_flags, parameters, return_type)
                m_visitor = SmaliMethodRemover(None, self.cache.indent)
                m_visitor.cache.add(desc)
                m_visitor.cache.add(m.content)
                self.cache.add_to_cache(m_visitor)
                return m_visitor
        return super().visit_method(name, access_flags, parameters, return_type)


def replace_methods(methods: list, content: str) -> str:
    """replace method in a smali content

    Args:
        methods (list): list of method to target
        content (str): the smali content

    Returns:
        str: return the new content
    """
    reader = SmaliReader()
    writer = SmaliModifier(methods=methods)
    reader.visit(content, writer)
    text = writer.code
    return text

    # test to hook .method public static getApkContentsSigners(Landroid/content/pm/SigningInfo;)[Landroid/content/pm/Signature;
