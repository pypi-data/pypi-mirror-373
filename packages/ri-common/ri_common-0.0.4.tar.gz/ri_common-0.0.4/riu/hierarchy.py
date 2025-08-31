import logging

import riu.entity

_LOGGER = logging.getLogger(__name__)


def translate_hierarchy_with_mappings(
        data, mappings, outer_parent_tuple=None, level=0, do_require_all=True,
        do_include_untranslated=True):
    """Translate names in a hierarchy according to a mappings dictionary. Deeper
    elements are represented as tuples (though the top-level ones can be as
    well). the `outer` name is the human name and the `inner` name is the
    internal/storage name [that we're trying to obscure via this functionality].

    Typically we want all attributes to be present if we're using this
    functionality at all. `do_require_all` should be set to False to support any
    preexisting data that is not covered.
    """

    # Allows us to translate lists of blobs
    if isinstance(data, list) is True:

        results = []
        for i, x in enumerate(data):

            y = translate_hierarchy_with_mappings(
                    x,
                    mappings,
                    outer_parent_tuple=outer_parent_tuple,
                    level=level + 1,
                    do_require_all=do_require_all)

            results.append(y)

        return results

    elif isinstance(data, dict) is False:

        # Some scalar (or, less likely, an unsupported type, which wouldn't
        # make sense in this context since we're writing data). Just pass it
        # through.

        return data


    # It's a dictionary

    translated = {}
    for outer_name, value in data.items():

        # This is what we're look for the translation under. It can be a string
        # or a tuple.
        if outer_parent_tuple is None:
            reference_outer_tuple = outer_name
        else:
            reference_outer_tuple = outer_parent_tuple + (outer_name,)

        try:
            inner_name = mappings[reference_outer_tuple]

        except KeyError:

            # If not enforcing then just set into the output dictionary verbatim
            if do_require_all is False:
                if do_include_untranslated is True:
                    translated[outer_name] = value

                continue

            raise


        # Descend

        # This is the parent-tuple that we'll be passing forward. It will
        # always be a tuple.
        if outer_parent_tuple is None:
            outer_parent_tuple2 = (outer_name,)
        else:
            outer_parent_tuple2 = outer_parent_tuple + (outer_name,)


        updated_value = \
            translate_hierarchy_with_mappings(
                value,
                mappings,
                outer_parent_tuple=outer_parent_tuple2,
                level=level + 1,
                do_require_all=do_require_all)

        translated[inner_name] = updated_value


    return translated


def _invert_mappings_tuple(mappings, input_key_tuple, cache):

    # If it's a 1-tuple, then try looking it up as a string. If not found, the
    # mapping is not complete and it's an error.

    if len(input_key_tuple) == 1:
        input_name = input_key_tuple[0]
        output_name = mappings[input_name]
        return (output_name,)


    # Prevent rerecursions

    try:
        return cache[input_key_tuple]
    except KeyError:
        pass


    # We have a tuple that isn't in the mapping. It must be an intermediate
    # form.

    # This retains the tuple type
    prefix_input_key_tuple = input_key_tuple[:-1]

    output_tuple = \
        _invert_mappings_tuple(
            mappings,
            prefix_input_key_tuple,
            cache)

    output_key_name = mappings[input_key_tuple]
    output_key_tuple = output_tuple + (output_key_name,)


    # Memoize so siblings caller contexts can benefit

    cache[input_key_tuple] = output_key_tuple


    return output_key_tuple


def get_reverse_hierarchy_mappings(mappings):
    """Returns a set of reverse mappings that can be provided to
    `translate_hierarchy_with_mappings` alongside already-mapped data in order
    to restore the pre-mapped data.
    """

    rmappings = {}
    cache = {}
    for outer_key, inner_member_name in mappings.items():
        if outer_key.__class__ is str:
            rmappings[inner_member_name] = outer_key

        elif outer_key.__class__ is tuple:
            inner_member_key = _invert_mappings_tuple(mappings, outer_key, cache)
            outer_member_name = outer_key[-1]

            rmappings[inner_member_key] = outer_member_name

        else:
            raise \
                Exception(
                    "We don't handle keys of type [{}]: [{}] [{}]".format(
                    key.__class__.__name__, key, value))


    return rmappings


def get_value_from_hierarchy_with_tuple_reference(record, reference):

# TODO(dustin): Add test

    parts = reference
    ptr = record
    while parts:

        # Allow us to specify nonexistent parts
        if ptr is None:
            ptr = {}

        part, parts = parts[0], parts[1:]

        try:
            if ptr.__class__ is dict:
                # This will raise KeyError if the reference is invalid
                ptr = ptr[part]
            elif ptr.__class__ is list:
                index = int(part)
                ptr = ptr[index]
            else:
                raise \
                    Exception(
                        "Can't pick [{}] from node of type [{}].".format(
                        part, ptr.__class__.__name__))

        except KeyError:
            raise

        except:
            _LOGGER.exception("Error while picking from node of type [{}]:\n"
                              "{}".format(ptr.__class__.__name__, ptr))

            raise


    return ptr


def get_value_from_hierarchy_with_string_reference(
        record, reference, separator='.'):

# TODO(dustin): Add test

    parts = reference.split(separator)
    value = get_value_from_hierarchy_with_tuple_reference(record, parts)

    return value


def pick_from_hierarchical_record(
        record, attribute_mappings, default_comma_separate_lists=False):

# TODO(dustin): Add test

    assert \
        attribute_mappings.__class__ is dict, \
        "Attribute mappings must be a dictionary: [{}]".format(
            attribute_mappings.__class__.__name__)

    assert \
        attribute_mappings, \
        "Attribute mappings is empty."


    assembled = {}
    for from_, to in attribute_mappings.items():

        try:
            ptr = get_value_from_hierarchy_with_string_reference(record, from_)

        except KeyError:

            # Supports nonexistent parts
            ptr = None


        # If None, we couldn't find this attribute
        if ptr is None:
            ptr = ''

        if ptr.__class__ is list and default_comma_separate_lists is True:
            ptr = ','.join([str(x) for x in ptr])

        assembled[to] = ptr


    return assembled


def pick_from_hierarchical_records_gen(records, attribute_mappings, **kwargs):
    """Given an iterable and a dictionayr of mappings (the keys of which can be
    hierarchical), yield a dictionary of mapped values for each record.
    """

    for record in records:
        assembled = \
            pick_from_hierarchical_record(
                record,
                attribute_mappings,
                **kwargs)

        yield assembled


class BaseTreeNode(riu.entity.BaseEntity):
    @property
    def children(self):
        raise NotImplementedError()


def _build_tree_node(
        record_index, out_node_index, child_attribute, node_id,
        node_factory_fn=None):

    record = record_index[node_id]
    child_ids = record.get(child_attribute, [])


    # Build children

    children = \
        map(
            lambda child_id: \
                _build_tree_node(
                    record_index,
                    out_node_index,
                    child_attribute,
                    child_id,
                    node_factory_fn=node_factory_fn),

            child_ids)

    children = list(children)


    # Construct node

    if node_factory_fn is None:
        node = record.copy()
        node['children'] = children

    else:
        node = node_factory_fn(record, children)

        assert \
            issubclass(node.__class__, BaseTreeNode) is True, \
            "Node factory is expected to return an instance of " \
                "`BaseTreeNode`: [{}] {}".format(node.__class__.__name__, node)


    # Set into node lookup

    out_node_index[node_id] = node


    return node


def tree_build_down(
        records, id_attribute, child_attribute, node_factory_fn=None):
    """Build a tree of `BaseTreeNode` objects. `node_factory_fn` should take a
    record and a list of child nodes and return a `BaseTreeNode`.
    """

    # Index all nodes

    record_index = {
        record[id_attribute]: record
        for record
        in records
    }


    # Find root

    leaf_ids = []
    parent_ids_s = set(record_index.keys())
    for record in record_index.values():
        id_ = record[id_attribute]
        child_ids = record.get(child_attribute, [])

        if not child_ids:
            leaf_ids.append(id_)

        else:
            for child_id in child_ids:
                parent_ids_s.discard(child_id)


    assert \
        len(parent_ids_s) == 1, \
        "There wasn't exactly one root node: {}".format(list(parent_ids_s))

    parent_ids = list(parent_ids_s)
    root_id = parent_ids[0]


    # Build tree

    node_index = {}

    root_node = \
        _build_tree_node(
            record_index,
            node_index,
            child_attribute,
            root_id,
            node_factory_fn=node_factory_fn)


    return node_index, root_id, leaf_ids


def scalar_tree_build_down(
        node, name_extractor_fn, flat_node_factory_fn=None,
        new_index_current_level=None):
    """Transform a tree from complex nodes to scalar nodes. Expects nodes to
    inherit from `BaseTreeNode`. One possible use-case would be to create
    multilevel string-lookup dictionaries, for example:

    string1 -> string2 -> string3 -> [None] -> value
    """

    if new_index_current_level is None:
        new_index_current_level = {}

    if flat_node_factory_fn is None:
        def flat_node_factory_fn(value, children_index):
            children_index[None] = value
            return children_index


    children_index = {}

    for child in node.children:
        scalar_tree_build_down(
            child,
            name_extractor_fn,
            flat_node_factory_fn=flat_node_factory_fn,
            new_index_current_level=children_index)

    new_flat_node = \
        flat_node_factory_fn(
            node.id,
            children_index)

    name = name_extractor_fn(node)

    new_index_current_level[name] = new_flat_node

    return new_index_current_level
