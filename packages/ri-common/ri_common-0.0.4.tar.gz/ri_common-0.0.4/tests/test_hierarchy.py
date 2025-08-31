import unittest

import riu.hierarchy


_COMPLEX_MAPPINGS = {
    'a': 'AA',
    'c': 'CC',
    'e': 'EE',
    ('e', 'f'): 'FF',
    ('e', 'h'): 'HH',
    ('e', 'j'): 'JJ',
    ('e', 'j', 'k'): 'KK',
    ('e', 'j', 'm'): 'MM',
}


class _TestNode(riu.hierarchy.BaseTreeNode):
    def __init__(self, data):
        self._data = data

    @property
    def id(self):
        return self._data['id']

    @property
    def children(self):
        return self._data['children']

    @property
    def raw(self):

        exported = {
            'id': self.id,
            'children': [
                child.raw
                for child
                in self.children
            ]
        }

        return exported


def _TEST_NODE_FACTORY(record, children):
    record = record.copy()
    record['children'] = children

    return _TestNode(record)


class Test(unittest.TestCase):
    def test_translate_hierarchy_with_mappings(self):

        data = {
            'a': 'b',
            'c': 'd',
        }

        mappings = {
            'a': 'AA',
            'c': 'CC',
        }

        translated = \
            riu.hierarchy.translate_hierarchy_with_mappings(
                data,
                mappings)

        expected = {
            'AA': 'b',
            'CC': 'd',
        }

        self.assertEqual(translated, expected)


        # Translate with an uncovered attribute (should fail)

        data['e'] = 'f'

        try:
            riu.hierarchy.translate_hierarchy_with_mappings(
                data,
                mappings)

        except KeyError:
            pass

        else:
            raise Exception("Expected KeyError for uncovered attribute.")


        # Translate with an uncovered attribute (not requiring coverage)

        translated = \
            riu.hierarchy.translate_hierarchy_with_mappings(
                data,
                mappings,
                do_require_all=False)

        expected = {
            'AA': 'b',
            'CC': 'd',

            # Just copied verbatim
            'e': 'f',
        }

        self.assertEqual(translated, expected)

    def test_translate_hierarchy_with_mappings__nested(self):

        data4 = [
            {
                'n': 'o',
                'p': 'q',
            },
            {
                'r': 's',
                't': 'u',
            },
        ]

        data3 = {
            'k': 'l',
            'm': data4,
        }

        data2 = {
            'f': 'g',
            'h': 'i',
            'j': data3,
        }

        data1 = {
            'a': 'b',
            'c': 'd',
            'e': data2,
        }

        mappings = {
            'a': 'AA',
            'c': 'CC',
            'e': 'EE',
            ('e', 'f'): 'FF',
            ('e', 'h'): 'HH',
            ('e', 'j'): 'JJ',
            ('e', 'j', 'k'): 'KK',
            ('e', 'j', 'm'): 'MM',

            # These are wrapped into a list, in the source (outer) data
            ('e', 'j', 'm', 'n'): 'NN',
            ('e', 'j', 'm', 'p'): 'PP',
            ('e', 'j', 'm', 'r'): 'RR',
            ('e', 'j', 'm', 't'): 'TT',
        }

        translated = \
            riu.hierarchy.translate_hierarchy_with_mappings(
                data1,
                mappings)

        expected = {
            'AA': 'b',
            'CC': 'd',
            'EE': {
                'FF': 'g',
                'HH': 'i',
                'JJ': {
                    'KK': 'l',
                    'MM': [
                        {
                            'NN': 'o',
                            'PP': 'q',
                        },
                        {
                            'RR': 's',
                            'TT': 'u',
                        },
                    ],
                },
            },
        }

        self.assertEqual(translated, expected)


        # Translate with an uncovered attribute (should fail)

        data3['v'] = 'w'

        try:
            riu.hierarchy.translate_hierarchy_with_mappings(
                data1,
                mappings)

        except KeyError:
            pass

        else:
            raise Exception("Expected KeyError for uncovered attribute.")


        # Translate with an uncovered attribute (not requiring coverage)

        translated = \
            riu.hierarchy.translate_hierarchy_with_mappings(
                data1,
                mappings,
                do_require_all=False)

        expected = {
            'AA': 'b',
            'CC': 'd',
            'EE': {
                'FF': 'g',
                'HH': 'i',
                'JJ': {
                    # Just copied verbatim
                    'v': 'w',

                    'KK': 'l',
                    'MM': [
                        {
                            'NN': 'o',
                            'PP': 'q',
                        },
                        {
                            'RR': 's',
                            'TT': 'u',
                        },
                    ],
                },
            },
        }

        self.assertEqual(translated, expected)

    def test_invert_mappings_tuple(self):

        # Check a depth of 1

        cache = {}

        self.assertEqual(
            riu.hierarchy._invert_mappings_tuple(_COMPLEX_MAPPINGS, ('a',), cache),
            ('AA',))


        expected = {}
        self.assertEqual(cache, expected)


        # Check a depth of 2

        cache = {}

        self.assertEqual(
            riu.hierarchy._invert_mappings_tuple(_COMPLEX_MAPPINGS, ('e', 'f'), cache),
            ('EE', 'FF'))

        expected = {
            ('e', 'f'): ('EE', 'FF')
        }

        self.assertEqual(cache, expected)


        # Check a depth of 3

        cache = {}

        self.assertEqual(
            riu.hierarchy._invert_mappings_tuple(_COMPLEX_MAPPINGS, ('e', 'j', 'k'), cache),
            ('EE', 'JJ', 'KK'))

        expected = {
            ('e', 'j'): ('EE', 'JJ'),
            ('e', 'j', 'k'): ('EE', 'JJ', 'KK'),
        }

        self.assertEqual(cache, expected)

    def test_get_reverse_hierarchy_mappings(self):

        rmappings = riu.hierarchy.get_reverse_hierarchy_mappings(_COMPLEX_MAPPINGS)

        expected = {
            'AA': 'a',
            'CC': 'c',
            'EE': 'e',
            ('EE', 'FF'): 'f',
            ('EE', 'HH'): 'h',
            ('EE', 'JJ'): 'j',
            ('EE', 'JJ', 'KK'): 'k',
            ('EE', 'JJ', 'MM'): 'm',
        }

        self.assertEqual(rmappings, expected)


        # If we reverse them again, we should end-up with the original mappings

        recovered_mappings = \
            riu.hierarchy.get_reverse_hierarchy_mappings(
                rmappings)

        self.assertEqual(recovered_mappings, _COMPLEX_MAPPINGS)

    def test_pick_from_hierarchical_records_gen(self):

        records = [
            {"timestamp_phrase": "2024-03-06T13:28:59.573663+00:00", "event_name": "create_variant", "metadata": {"write": True, "config": ["_managed:used and excellent", "large:", "grey/black/red logo:#868484"], "product_id": 8200540651811, "variant_id": 47692705431843}},
            {"timestamp_phrase": "2024-03-06T13:28:59.573721+00:00", "event_name": "want_to_upload_image_primary", "metadata": {"product_id": 8200540651811, "variant_id": 47692705431843, "config": ["_managed:used and excellent", "large:", "grey/black/red logo:#868484"], "image_filepath": "/output/workflow/dropbox/images/2024-01-10/bld00000000000150400.jpg"}},
            {"timestamp_phrase": "2024-03-06T13:29:00.629621+00:00", "event_name": "create_variant", "metadata": {"write": True, "config": ["_managed:used and excellent", "large:", "grey/black:#000000"], "product_id": 8200540651811, "variant_id": 47692706021667}},
            {"timestamp_phrase": "2024-03-06T13:29:00.629771+00:00", "event_name": "want_to_upload_image_primary", "metadata": {"product_id": 8200540651811, "variant_id": 47692706021667, "config": ["_managed:used and excellent", "large:", "grey/black:#000000"], "image_filepath": "/output/workflow/dropbox/images/2024-01-10/bld00000000000123957.jpg"}},
            {"timestamp_phrase": "2024-03-06T13:29:01.724781+00:00", "event_name": "create_variant", "metadata": {"write": True, "config": ["_managed:used and good", "2X large:", "black:#000000"], "product_id": 8200540651811, "variant_id": 47692706087203}},
            {"timestamp_phrase": "2024-03-06T13:29:01.725432+00:00", "event_name": "want_to_upload_image_primary", "metadata": {"product_id": 8200540651811, "variant_id": 47692706087203, "config": ["_managed:used and good", "2X large:", "black:#000000"], "image_filepath": "/output/workflow/dropbox/images/2024-01-10/bld00000000000123921.jpg"}},
            {"timestamp_phrase": "2024-03-06T13:29:02.466462+00:00", "event_name": "variant_already_has_images", "metadata": {"product_id": 8200540651811, "config": ["_managed:used and excellent", "extra large:", "black:#000000"], "variant_id": 47356921250083}},
            {"timestamp_phrase": "2024-03-06T13:29:02.466503+00:00", "event_name": "variant_already_has_images", "metadata": {"product_id": 8200540651811, "config": ["_managed:used and excellent", "medium:", "black:#000000"], "variant_id": 47124530463011}},
            {"timestamp_phrase": "2024-03-06T13:29:02.466529+00:00", "event_name": "variant_already_has_images", "metadata": {"product_id": 8200540651811, "config": ["_managed:used and good", "2x large:", "black:#000000"], "variant_id": 47124530495779}},
            {"timestamp_phrase": "2024-03-06T13:29:02.466550+00:00", "event_name": "variant_already_has_images", "metadata": {"product_id": 8200540651811, "config": ["_managed:used and good", "large:", "black:#000000"], "variant_id": 47124530528547}},
        ]

        mappings2 = {
            'timestamp_phrase': 'final_timestamp_phrase',
            'metadata.product_id': 'final_product_id',
        }

        g = riu.hierarchy.pick_from_hierarchical_records_gen(records, mappings2)

        picked = list(g)

        expected = [
            { 'final_timestamp_phrase': '2024-03-06T13:28:59.573663+00:00', 'final_product_id': 8200540651811 },
            { 'final_timestamp_phrase': '2024-03-06T13:28:59.573721+00:00', 'final_product_id': 8200540651811 },
            { 'final_timestamp_phrase': '2024-03-06T13:29:00.629621+00:00', 'final_product_id': 8200540651811 },
            { 'final_timestamp_phrase': '2024-03-06T13:29:00.629771+00:00', 'final_product_id': 8200540651811 },
            { 'final_timestamp_phrase': '2024-03-06T13:29:01.724781+00:00', 'final_product_id': 8200540651811 },
            { 'final_timestamp_phrase': '2024-03-06T13:29:01.725432+00:00', 'final_product_id': 8200540651811 },
            { 'final_timestamp_phrase': '2024-03-06T13:29:02.466462+00:00', 'final_product_id': 8200540651811 },
            { 'final_timestamp_phrase': '2024-03-06T13:29:02.466503+00:00', 'final_product_id': 8200540651811 },
            { 'final_timestamp_phrase': '2024-03-06T13:29:02.466529+00:00', 'final_product_id': 8200540651811 },
            { 'final_timestamp_phrase': '2024-03-06T13:29:02.466550+00:00', 'final_product_id': 8200540651811 },
        ]

        self.assertEqual(
            sorted(picked, key=lambda record: record['final_timestamp_phrase']),
            sorted(expected, key=lambda record: record['final_timestamp_phrase']))

    def test_build_tree_node__dict(self):

        # Test with single node

        record1 = {
        }

        record_index = {
            1: record1,
        }

        out_node_index = {}
        root_id = 1
        child_attribute = 'children'

        node = riu.hierarchy._build_tree_node(
                record_index,
                out_node_index,
                child_attribute,
                root_id,
                node_factory_fn=None)

        expected_node = {'children': []}

        self.assertEqual(node, expected_node)

        expected = {
            1: expected_node
        }

        self.assertEqual(out_node_index, expected)


        # Test with multiple nodes

        record1 = {
            child_attribute: [
                2,
            ],
        }

        record2 = {
        }

        record_index = {
            1: record1,
            2: record2,
        }

        out_node_index = {}
        root_id = 1

        node = riu.hierarchy._build_tree_node(
                record_index,
                out_node_index,
                child_attribute,
                root_id,
                node_factory_fn=None)

        expected_node2 = {'children': []}
        expected_node1 = {'children': [expected_node2]}

        self.assertEqual(node, expected_node1)

        expected = {
            1: expected_node1,
            2: expected_node2,
        }

        self.assertEqual(out_node_index, expected)

    def test_build_tree_node__node_class(self):

        # Test with single node

        record1 = {
            'id': 1,
        }

        record_index = {
            1: record1,
        }

        out_node_index = {}
        root_id = 1
        child_attribute = 'children'

        node = riu.hierarchy._build_tree_node(
                record_index,
                out_node_index,
                child_attribute,
                root_id,
                node_factory_fn=_TEST_NODE_FACTORY)

        expected_node1_raw = {
            'id': 1,
            'children': [],
        }

        self.assertEqual(node.raw, expected_node1_raw)

        out_node_index_flat = {
            id_: node.raw
            for id_, node
            in out_node_index.items()
        }

        expected = {
            1: expected_node1_raw
        }

        self.assertEqual(out_node_index_flat, expected)


        # Test with multiple nodes

        record1 = {
            'id': 1,

            child_attribute: [
                2,
            ],
        }

        record2 = {
            'id': 2,
        }

        record_index = {
            1: record1,
            2: record2,
        }

        out_node_index = {}
        root_id = 1

        node = riu.hierarchy._build_tree_node(
                record_index,
                out_node_index,
                child_attribute,
                root_id,
                node_factory_fn=_TEST_NODE_FACTORY)

        expected_node2_raw = {'id': 2, 'children': []}
        expected_node1_raw = {'id': 1, 'children': [expected_node2_raw]}

        self.assertEqual(node.raw, expected_node1_raw)

        out_node_index_flat = {
            id_: node.raw
            for id_, node
            in out_node_index.items()
        }

        expected = {
            1: expected_node1_raw,
            2: expected_node2_raw,
        }

        self.assertEqual(out_node_index_flat, expected)

    def test_tree_build_down__dict(self):

        records = [
            {
                'id': 1,
                'children': [
                    2,
                    3,
                ],
            },

            {
                'id': 2,
                'children': [

                ],
            },

            {
                'id': 3,
                'children': [
                    4,
                ],
            },

            {
                'id': 4,
                'children': [

                ],
            },
        ]

        id_attribute = 'id'
        child_attribute = 'children'

        node_index, \
        root_id, \
        leaf_ids = \
            riu.hierarchy.tree_build_down(
                records,
                id_attribute,
                child_attribute,
                node_factory_fn=None)

        self.assertEqual(root_id, 1)
        self.assertEqual(leaf_ids, [2, 4])


        node2 = {
            'id': 2,
            'children': [

            ],
        }

        node4 = {
            'id': 4,
            'children': [

            ],
        }

        node3 = {
            'id': 3,
            'children': [
                node4,
            ],
        }

        node1 = {
            'id': 1,
            'children': [
                node2,
                node3,
            ],
        }

        expected = {
            1: node1,
            2: node2,
            3: node3,
            4: node4,
        }

        self.assertEqual(node_index, expected)

    def test_tree_build_down__node_class(self):

        records = [
            {
                'id': 1,
                'children': [
                    2,
                    3,
                ],
            },

            {
                'id': 2,
                'children': [

                ],
            },

            {
                'id': 3,
                'children': [
                    4,
                ],
            },

            {
                'id': 4,
                'children': [

                ],
            },
        ]

        id_attribute = 'id'
        child_attribute = 'children'

        out_node_index, \
        root_id, \
        leaf_ids = \
            riu.hierarchy.tree_build_down(
                records,
                id_attribute,
                child_attribute,
                node_factory_fn=_TEST_NODE_FACTORY)

        self.assertEqual(root_id, 1)
        self.assertEqual(leaf_ids, [2, 4])


        node2 = _TestNode({
            'id': 2,
            'children': [

            ],
        })

        node4 = _TestNode({
            'id': 4,
            'children': [

            ],
        })

        node3 = _TestNode({
            'id': 3,
            'children': [
                node4,
            ],
        })

        node1 = _TestNode({
            'id': 1,
            'children': [
                node2,
                node3,
            ],
        })

        out_node_index_flat = {
            id_: node.raw
            for id_, node
            in out_node_index.items()
        }

        expected = {
            1: node1.raw,
            2: node2.raw,
            3: node3.raw,
            4: node4.raw,
        }

        self.assertEqual(out_node_index_flat, expected)

    def test_scalar_tree_build_down(self):

        class Node(riu.hierarchy.BaseTreeNode):
            def __init__(self, id_, name, children=None):
                if children is None:
                    children = []

                self._id = id_
                self._children = children

                self.name = name

                super().__init__({})

            @property
            def id(self):
                return self._id

            @property
            def children(self):
                return self._children


        node5 = Node(55, 'ee')
        node4 = Node(44, 'dd', children=[node5])
        node3 = Node(33, 'cc', children=[node4])
        node2 = Node(22, 'bb')
        node1 = Node(11, 'aa', children=[node2, node3])

        name_extractor_fn = lambda node: node.name

        flat_root_node = \
            riu.hierarchy.scalar_tree_build_down(
                node1,
                name_extractor_fn)

        expected = {
            'aa': {
                'bb': {
                    None: 22
                },

                'cc': {
                    'dd': {
                        'ee': {
                            None: 55
                        },
                        None: 44
                    },
                    None: 33
                },
                None: 11
            }
        }

        self.assertEqual(flat_root_node, expected)
