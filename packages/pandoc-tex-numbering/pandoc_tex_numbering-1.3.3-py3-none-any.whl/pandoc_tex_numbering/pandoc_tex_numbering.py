import logging
import re
import json
import string
import warnings

from panflute import *
from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode, LatexMacroNode

from .docx_list import add_docx_list
from .numbering import NumberingState, Formater, numberings2chunks

logger = logging.getLogger("pandoc-tex-numbering")
hdlr = logging.FileHandler("pandoc-tex-numbering.log")
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


def to_string(elem):
    if isinstance(elem, Str):
        return elem.text
    elif isinstance(elem, Space):
        return " "
    elif isinstance(elem, (LineBreak, SoftBreak)):
        return "\n"
    elif isinstance(elem, ListContainer):
        return "".join([to_string(item) for item in elem])
    elif hasattr(elem, "content"):
        return "".join([to_string(item) for item in elem.content])
    else:
        return ""


def extract_captions_from_refdict(ref_dict, ref_type, doc):
    items = []
    assert ref_type in ["fig", "tab"]
    for label, num_obj in ref_dict.items():
        if num_obj.item_type == ref_type:
            caption_body = (
                num_obj.short_caption
                if not num_obj.short_caption is None
                else num_obj.caption
            )
            caption_ref = num_obj.src
            caption = f"{caption_ref}: {caption_body}" if caption_body else caption_ref
            items.append((caption, label))
    return items


def prepare(doc):
    # These are global metadata settings which will be used in the whole document (need to be saved in the doc object)
    # Settings used once will not be saved, thus it only appears in the prepare function
    doc.settings = {
        # Numbering Item Switches
        "num_fig": doc.get_metadata("number-figures", True),
        "num_tab": doc.get_metadata("number-tables", True),
        "num_eq": doc.get_metadata("number-equations", True),
        "num_sec": doc.get_metadata("number-sections", True),
        "num_theorem": doc.get_metadata("number-theorems", True),
        # Multiline Equation Settings
        "multiline_envs": doc.get_metadata(
            "multiline-environments", "cases,align,aligned,gather,gathered,multline,flalign"
        ).split(","),
        # Multiple Reference Settings
        "multiple_ref_suppress": doc.get_metadata("multiple-ref-suppress", True),
        "multiple_ref_separator": doc.get_metadata("multiple-ref-separator", ", "),
        "multiple_ref_last_separator": doc.get_metadata(
            "multiple-ref-last-separator", " and "
        ),
        "multiple_ref_to": doc.get_metadata("multiple-ref-to", "-"),
        "multiple_ref_style": doc.get_metadata(
            "multiple-ref-style", "simple"
        ),  # must be one of "simple", "full". To get Fig. 1, 2 and 3 or Fig.1, Fig.2 and Fig.3
        # Custom List of Figures and Tables
        "custom_lof": doc.get_metadata("custom-lof", False),
        "custom_lot": doc.get_metadata("custom-lot", False),
        "list_leader_type": doc.get_metadata("list-leader-type", "middleDot"),
        "lof_title": doc.get_metadata("lof-title", "List of Figures"),
        "lot_title": doc.get_metadata("lot-title", "List of Tables"),
        # Appendix Settings
        "apx_names": doc.get_metadata("appendix-names", "Appendix").split("/,"),
        # Miscellaneous
        "data_export_path": doc.get_metadata("data-export-path", None),
        "auto_labelling": doc.get_metadata("auto-labelling", True),
    }
    # Run-time global variables
    doc.global_vars = {
        # Equations with labels will be wrapped with div elements, since pandoc does not support adding identifiers to math blocks directly
        "paras2wrap": {"paras": [], "labels": []},
        # Tables with labels will be wrapped with div elements, only in case the table is not labelled in the latex source
        "tabs2wrap": [],
        # We save the links to replace here to avoid searching them in the finalize function
        "links2replace": [],
        "lof_block": None,
        "lot_block": None,
    }
    thm_names = doc.get_metadata("theorem-names", None)
    doc.settings["theorem_names"] = thm_names.split(",") if thm_names else []
    if doc.settings["num_theorem"] and len(doc.settings["theorem_names"]) == 0:
        warnings.warn(
            "The number-theorems is enabled but no theorem names are provided. The numbering of theorems will be disabled.",
            UserWarning,
        )
        logger.warning(
            "The number-theorems is enabled but no theorem names are provided. The numbering of theorems will be disabled."
        )
        doc.settings["num_theorem"] = False

    # Prepare the multiline environment filter pattern for fast checking
    doc.global_vars["multiline_filter_pattern"] = re.compile(
        r"\\begin\{(" + "|".join(doc.settings["multiline_envs"]) + ")}"
    )

    max_levels = int(doc.get_metadata("section-max-levels", 10))
    # From here, we start to build the core formater system for numbering
    aka = {
        "fig": "figure",
        "tab": "table",
        "eq": "equation",
        "sec": "section",
        "subfig": "subfigure",
        "apx": "appendix",
    }
    formaters = {"thm": {}}
    pref_space = doc.get_metadata("prefix-space", True)

    for item in ["fig", "tab", "eq"]:
        fmt_presets = {}
        for preset, default in [
            ["src", None],
            ["ref", "{num}"],
            ["cref", "{prefix}{num}"],
            ["Cref", None],
        ]:
            if item == "eq" and preset == "src":
                default = "\\qquad({num})"
            fmt = doc.get_metadata(f"{aka[item]}-{preset}-format", default)
            fmt_presets[preset] = fmt
        formaters[item] = Formater(
            fmt_presets=fmt_presets,
            item_type=item,
            prefix=doc.get_metadata(f"{aka[item]}-prefix", aka[item].capitalize()),
            pref_space=pref_space,
            num_style=doc.get_metadata(f"{aka[item]}-numstyle", "arabic"),
        )

    for thm_type in doc.settings["theorem_names"]:
        fmt_presets = {}
        item_type = f"thm-{thm_type}"
        for preset, default in [
            ["src", None],
            ["ref", f"{{{item_type}_id}}"],
            ["cref", f"{{prefix}}{{{item_type}_id}}"],
            ["Cref", None],
        ]:
            fmt = doc.get_metadata(f"theorem-{thm_type}-{preset}-format", default)
            fmt_presets[preset] = fmt
        formaters["thm"][thm_type] = Formater(
            fmt_presets=fmt_presets,
            item_type=item_type,
            prefix=doc.get_metadata(
                f"theorem-{thm_type}-prefix", thm_type.capitalize()
            ),
            pref_space=pref_space,
            num_style=doc.get_metadata(f"theorem-{thm_type}-numstyle", "arabic"),
        )

    formaters["subfig"] = Formater(
        fmt_presets={
            "src": doc.get_metadata("subfigure-src-format", "({this_num})"),
            "ref": doc.get_metadata("subfigure-ref-format", "{parent_num}({this_num})"),
            "cref": doc.get_metadata(
                "subfigure-cref-format", "{prefix}{parent_num}({this_num})"
            ),
            "Cref": doc.get_metadata("subfigure-Cref-format", None),
        },
        item_type="subfig",
        prefix=doc.get_metadata("subfigure-prefix", "Figure"),
        pref_space=pref_space,
        num_style=doc.get_metadata("subfigure-numstyle", "latin"),
    )

    formaters["sec"] = []
    formaters["apx"] = []

    for item in ["apx", "sec"]:
        for i in range(1, max_levels + 1):
            fmt_presets = {}
            for preset, default in [
                ["src", None],
                ["ref", "{num}"],
                ["cref", "{prefix}{num}"],
                ["Cref", None],
            ]:
                fmt = doc.get_metadata(f"{aka[item]}-{preset}-format-{i}", default)
                fmt_presets[preset] = fmt
            if item == "apx" and i == 1:
                default_numstyle = "Latin"
            else:
                default_numstyle = "arabic"
            i_th_formater = Formater(
                fmt_presets=fmt_presets,
                item_type=item,
                prefix=doc.get_metadata(f"{aka[item]}-prefix", aka[item].capitalize()),
                pref_space=pref_space,
                num_style=doc.get_metadata(
                    f"{aka[item]}-numstyle-{i}", default_numstyle
                ),
            )
            formaters[item].append(i_th_formater)

    # Offsets
    offsets = {}
    for item in ["fig", "tab", "eq", "subfig"]:
        offset = doc.get_metadata(f"{aka[item]}-offset", 0)
        if offset != 0:
            offsets[item] = offset
    for item in ["sec", "apx"]:
        for i in range(1, max_levels + 1):
            offset = doc.get_metadata(f"{aka[item]}-offset-{i}", 0)
            if offset != 0:
                offsets[f"{item}_{i}"] = offset
    for thm_type in doc.settings["theorem_names"]:
        offset = doc.get_metadata(f"theorem-{thm_type}-offset", 0)
        if offset != 0:
            offsets[f"thm-{thm_type}"] = offset

    # Initialize a numbering state object
    doc.num_state = NumberingState(
        reset_level=int(doc.get_metadata("number-reset-level", 1)),
        max_levels=max_levels,
        formaters=formaters,
        offsets=offsets,
    )

    doc.ref_dict = {}


def finalize(doc):
    # Add labels for equations by wrapping them with div elements, since pandoc does not support adding identifiers to math blocks directly
    paras2wrap = doc.global_vars["paras2wrap"]
    paras, labels_list = paras2wrap["paras"], paras2wrap["labels"]
    assert len(paras) == len(labels_list)
    for para, labels in zip(paras, labels_list):
        if labels:
            try:
                parent = para.parent
                idx = parent.content.index(para)
                del parent.content[idx]
                div = Div(para, identifier=labels[0])
                for label in labels[1:]:
                    div = Div(div, identifier=label)
                parent.content.insert(idx, div)
            except Exception as e:
                logger.warning(
                    f"Failed to add identifier to paragraph because of {e}. Pleas check: \n The paragraph: {para}. Parent of the paragraph: {parent}"
                )

    # Add labels for tables by wrapping them with div elements. This is necessary because if a table is not labelled in the latex source, pandoc will not generate a div element for it.
    for tab, label in doc.global_vars["tabs2wrap"]:
        if label:
            parent = tab.parent
            idx = parent.content.index(tab)
            del parent.content[idx]
            div = Div(tab, identifier=label)
            parent.content.insert(idx, div)

    for link, items in doc.global_vars["links2replace"]:
        parent = link.parent
        idx = parent.content.index(link)
        del parent.content[idx]
        for item in items[::-1]:
            parent.content.insert(idx, item)

    if doc.settings["custom_lot"]:
        doc.content.insert(0, RawBlock("\\listoftables", format="latex"))
        doc.global_vars["lot_block"] = doc.content[0]
        table_items = extract_captions_from_refdict(doc.ref_dict, "tab", doc)
        add_docx_list(
            doc.global_vars["lot_block"],
            table_items,
            doc.settings["lot_title"],
            leader_type=doc.settings["list_leader_type"],
        )

    if doc.settings["custom_lof"]:
        doc.content.insert(0, RawBlock("\\listoffigures", format="latex"))
        doc.global_vars["lof_block"] = doc.content[0]
        figure_items = extract_captions_from_refdict(doc.ref_dict, "fig", doc)
        add_docx_list(
            doc.global_vars["lof_block"],
            figure_items,
            doc.settings["lof_title"],
            leader_type=doc.settings["list_leader_type"],
        )

    # Export the reference dictionary to a json file
    if doc.settings["data_export_path"]:
        with open(doc.settings["data_export_path"], "w") as f:
            ref_dict_data = {
                label: num_obj.to_dict() for label, num_obj in doc.ref_dict.items()
            }
            json.dump(ref_dict_data, f, indent=2, ensure_ascii=False)

    # Clean up the global variables
    del doc.settings
    del doc.global_vars
    del doc.num_state
    del doc.ref_dict

    logger.info("Finished pandoc-tex-numbering")


def _parse_multiline_environment(root_node, doc):
    labels = {}
    environment_body = ""
    # Multiple equations
    label_of_this_line = None
    is_label_this_line = True
    for node in root_node.nodelist:
        if isinstance(node, LatexMacroNode):
            if node.macroname == "label":
                # If the label contains special characters, the argument will be parsed into multiple nodes. Therefore we get the label from the raw latex string rather than the parsed node.
                # label = node.nodeargd.argnlist[0].nodelist[0].chars
                arg1 = node.nodeargd.argnlist[0]
                label = arg1.latex_verbatim()[1:-1]
                label_of_this_line = label
            if node.macroname == "nonumber":
                is_label_this_line = False
            if node.macroname == "\\":
                if is_label_this_line:
                    doc.num_state.next_eq()
                    num_obj = doc.num_state.current_eq()
                    environment_body += f"{{{num_obj.src}}}"
                    if label_of_this_line:
                        labels[label_of_this_line] = num_obj
                label_of_this_line = None
                is_label_this_line = True
        environment_body += node.latex_verbatim()

    if is_label_this_line:
        doc.num_state.next_eq()
        num_obj = doc.num_state.current_eq()
        environment_body += f"{{{num_obj.src}}}"
        if label_of_this_line:
            labels[label_of_this_line] = num_obj
    modified_math_str = f"\\begin{{{root_node.environmentname}}}{environment_body}\\end{{{root_node.environmentname}}}"
    return modified_math_str, labels


def _parse_plain_math(math_str: str, doc):
    labels = {}
    doc.num_state.next_eq()
    num_obj = doc.num_state.current_eq()
    modified_math_str = f"{math_str}{{{num_obj.src}}}"
    label_strings = re.findall(r"\\label\{(.*?)\}", math_str)
    if len(label_strings) >= 2:
        logger.warning(f"Multiple label_strings in one math block: {label_strings}")
    for label in label_strings:
        labels[label] = num_obj
    return modified_math_str, labels


def parse_latex_math(math_str: str, doc):
    math_str = math_str.strip()
    # Add numbering to every line of the math block when and only when:
    # 1. The top level environment is a multiline environment
    # 2. The math block contains at least a label
    # Otherwise, add numbering to the whole math block

    # Fast check if it is a multiline environment
    if re.match(doc.global_vars["multiline_filter_pattern"], math_str):
        walker = LatexWalker(math_str)
        nodelist, _, _ = walker.get_latex_nodes(pos=0)
        if len(nodelist) == 1:
            root_node = nodelist[0]
            if (
                isinstance(root_node, LatexEnvironmentNode)
                and root_node.environmentname in doc.settings["multiline_envs"]
            ):
                return _parse_multiline_environment(root_node, doc)
    # Otherwise, add numbering to the whole math block
    return _parse_plain_math(math_str, doc)


def add_label_to_caption(num_obj, label: str, elem):
    url = f"#{label}" if label else ""
    label_items = [
        Link(Str(num_obj.src), url=url),
    ]
    has_caption = True
    if not elem.caption:
        elem.caption = Caption(Plain(Str("")), short_caption=ListContainer([Str("")]))
        has_caption = False
    if not elem.caption.content:
        elem.caption.content = [Plain(Str(""))]
        has_caption = False
    if has_caption:
        # If there's no caption text, we shouldnot add a colon
        label_items.extend([Str(":"), Space()])
    for item in label_items[::-1]:
        elem.caption.content[0].content.insert(0, item)


def find_labels_header(elem, doc):
    this_level = elem.level
    if this_level == 1:
        header_txt = to_string(elem)
        doc.num_state.isin_apx = header_txt in doc.settings["apx_names"]

    # Skip numbering if level exceeds max_levels
    max_levels = int(doc.get_metadata("section-max-levels", 10))
    if this_level > max_levels:
        return

    doc.num_state.next_sec(level=this_level)
    num_obj = doc.num_state.current_sec(level=this_level)

    # Check for identifier
    if elem.identifier:
        label = elem.identifier
        doc.ref_dict[label] = num_obj

    for child in elem.content:
        if isinstance(child, Span) and "label" in child.attributes:
            label = child.attributes["label"]
            doc.ref_dict[label] = num_obj
    if doc.settings["num_sec"]:
        elem.content.insert(0, Space())
        elem.content.insert(0, Str(num_obj.src))


def find_labels_math(elem, doc):
    math_str = elem.text
    modified_math_str, labels = parse_latex_math(math_str, doc)
    elem.text = modified_math_str
    for label, num_obj in labels.items():
        doc.ref_dict[label] = num_obj
    if labels:
        this_elem = elem
        while not isinstance(this_elem, Para):
            this_elem = this_elem.parent
            if isinstance(this_elem, Doc):
                logger.warning(f"Unexpected parent of math block: {this_elem}")
                break
        else:
            if not this_elem in doc.global_vars["paras2wrap"]["paras"]:
                doc.global_vars["paras2wrap"]["paras"].append(this_elem)
                doc.global_vars["paras2wrap"]["labels"].append(list(labels.keys()))
            else:
                idx = doc.global_vars["paras2wrap"]["paras"].index(this_elem)
                doc.global_vars["paras2wrap"]["labels"][idx].extend(labels.keys())


def find_labels_table(elem, doc):
    doc.num_state.next_tab()
    # The label of a table will be added to a div element wrapping the table, if any. And if there is not, the div element will be not created.
    num_obj = doc.num_state.current_tab()
    if isinstance(elem.parent, Div):
        label = elem.parent.identifier
        if not label and doc.settings["auto_labelling"]:
            label = f"tab:{num_obj.ref}"
            elem.parent.identifier = label
    else:
        if doc.settings["auto_labelling"]:
            label = f"tab:{num_obj.ref}"
            doc.global_vars["tabs2wrap"].append([elem, label])
        else:
            label = ""

    num_obj.caption = to_string(elem.caption)
    add_label_to_caption(num_obj, label, elem)
    if label:
        doc.ref_dict[label] = num_obj


def find_labels_figure(elem, doc):
    # We will walk the subfigures in a Figure element manually, therefore we directly skip the subfigures from global walking
    if isinstance(elem.parent, Figure):
        return

    doc.num_state.next_fig()
    _find_labels_figure(elem, doc, subfigure=False)

    for child in elem.content:
        if isinstance(child, Figure):
            doc.num_state.next_subfig()
            _find_labels_figure(child, doc, subfigure=True)


def _find_labels_figure(elem, doc, subfigure=False):
    label = elem.identifier
    num_obj = doc.num_state.current_fig(subfig=subfigure)
    if not label and doc.settings["auto_labelling"]:
        label = f"fig:{num_obj.ref}"
        elem.identifier = label

    num_obj.caption = to_string(elem.caption)
    num_obj.short_caption = to_string(elem.caption.short_caption)
    add_label_to_caption(num_obj, label, elem)
    if label:
        doc.ref_dict[label] = num_obj


def find_labels_theorem(elem, doc):
    thm_type = [cls for cls in elem.classes if cls in doc.settings["theorem_names"]][0]
    doc.num_state.next_thm(thm_type)
    label = elem.identifier
    num_obj = doc.num_state.current_thm(thm_type)
    if not label:
        elem.identifier = f"thm_{thm_type}:{num_obj.ref}"
    doc.ref_dict[label] = num_obj


def action_find_labels(elem, doc):
    # Find labels in headers, math blocks, figures and tables
    if isinstance(elem, Header):
        # We should always find labels in headers since we need the section numbering information
        find_labels_header(elem, doc)
    if (
        isinstance(elem, Math)
        and elem.format == "DisplayMath"
        and doc.settings["num_eq"]
    ):
        find_labels_math(elem, doc)
    if isinstance(elem, Figure) and doc.settings["num_fig"]:
        find_labels_figure(elem, doc)
    if isinstance(elem, Table) and doc.settings["num_tab"]:
        find_labels_table(elem, doc)
    # if isinstance(elem,RawBlock) and (doc.settings["custom_lof"] or doc.settings["custom_lot"]) and elem.format == "latex":
    #     if "listoffigures" in elem.text:
    #         doc.global_vars["lof_block"] = elem
    #     if "listoftables" in elem.text:
    #         doc.global_vars["lot_block"] = elem
    if isinstance(elem, Div):
        if (
            any([cls in doc.settings["theorem_names"] for cls in elem.classes])
            and doc.settings["num_theorem"]
        ):
            find_labels_theorem(elem, doc)


def _num2link(num_obj, fmt_preset):
    return Link(Str(num_obj.format(fmt_preset=fmt_preset)), url=f"#{num_obj.label}")


def join_items(items, doc):
    if len(items) == 1:
        if isinstance(items[0], list):
            return items[0]
        else:
            return items
    results = []
    for i, item in enumerate(items):
        if i != 0:
            if i == len(items) - 1:
                results.append(Str(doc.settings["multiple_ref_last_separator"]))
            else:
                results.append(Str(doc.settings["multiple_ref_separator"]))
        if isinstance(item, list):
            results.extend(item)
        else:
            results.append(item)
    return results


def labels2refs(labels, ref_type, doc):
    # This function handles ONE single citation, most of these codes are dealing with multiple references in one citation.
    assert ref_type in [
        "ref",
        "ref+label",
        "ref+Label",
        "eqref",
    ], f"Unknown reference-type: {ref_type}"
    num_objs = []
    for label in list(set(labels)):
        if label in doc.ref_dict:
            num_obj = doc.ref_dict[label]
            num_obj.label = label
            num_objs.append(num_obj)
        else:
            logger.warning(f"Reference not found: {label}")

    is_suppress = doc.settings["multiple_ref_suppress"]

    # `numberings2chunks` will organize references in one citation into sorted chunks. `chunks` is {item_type(fig, tab, eq, sec, thm): [[num_obj1, num_obj2], ...]} where num_objs are sorted and splited into continuous chunks.
    # our current task is to format these chunks into the desired output.
    chunks = numberings2chunks(num_objs, split_continous=is_suppress)

    # preset that the user defined
    raw_preset = {
        "ref": "ref",
        "eqref": "ref",
        "ref+label": "cref",
        "ref+Label": "Cref",
    }[ref_type]

    # (all_first_preset) Chunk1Ref1 - (plain_preset) Chunk1Refn, (chunk_first_preset) Chunk2Ref1 - (chunk_first_preset) Chunk2Refn, ...
    all_first_preset = raw_preset
    chunk_first_preset = "cref" if raw_preset == "Cref" else raw_preset
    plain_preset = raw_preset if doc.settings["multiple_ref_style"] == "full" else "ref"
    plain_preset = "cref" if plain_preset == "Cref" else plain_preset

    results_list = []
    item_types = list(chunks.keys())
    for i_item_type, item_type in enumerate(item_types):

        chunk_first_preset = chunk_first_preset if i_item_type > 0 else all_first_preset

        chunk_result = []

        ref_list = chunks[item_type]
        for iref, refs in enumerate(ref_list):

            # we now consider should these references be suppressed or not: i.e. Fig. 1-3 or Fig. 1, 2, 3
            if len(refs) == 1:
                ref_result = [_num2link(refs[0], chunk_first_preset)]
            elif is_suppress:
                ref_result = [
                    [
                        _num2link(refs[0], chunk_first_preset),
                        Str(doc.settings["multiple_ref_to"]),
                        _num2link(refs[-1], plain_preset),
                    ]
                ]
            else:
                ref_result = [
                    _num2link(refs[0], chunk_first_preset),
                ]
                for num_obj in refs[1:]:
                    ref_result.append(
                        [
                            _num2link(num_obj, plain_preset),
                        ]
                    )
            chunk_result.append(join_items(ref_result, doc))
        results_list.append(join_items(chunk_result, doc))
    results = join_items(results_list, doc)
    return results


def action_replace_refs(elem, doc):
    if isinstance(elem, Link) and "reference-type" in elem.attributes:
        labels = elem.attributes["reference"].split(",")
        results = labels2refs(labels, elem.attributes["reference-type"], doc)
        doc.global_vars["links2replace"].append((elem, results))


def main(doc=None):
    logger.info("Starting pandoc-tex-numbering")
    return run_filters(
        [action_find_labels, action_replace_refs],
        doc=doc,
        prepare=prepare,
        finalize=finalize,
    )


if __name__ == "__main__":
    main()
