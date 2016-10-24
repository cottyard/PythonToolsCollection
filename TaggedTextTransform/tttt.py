from xml.dom import minidom
import operator
import os
import imp

DEBUG_MODE = False
DEBUG_PRINT_INDENT = -1

class Scope(object):
    def __init__(self, first_frame, loaded_env, template_file, target_file):
        self._tag_frames = [first_frame]
        self._revisable_env_frames = [{}]

        self._template_file = template_file
        self._target_file = target_file

        self._template_dir = os.path.dirname(template_file)
        self._target_dir = os.path.dirname(target_file) \
            if target_file else self._template_dir

        self._loaded_env = loaded_env
        self._init_tttt_env(self._loaded_env, self._template_dir)
        self._update_global_env()

        self._loaded_env_module_cache = dict()

    def _init_tttt_env(self, env, env_dir):
        env['tttt_target_dir'] = self._target_dir
        env['tttt_import'] = self._import_api_factory(env, env_dir)
        return env

    def _import_api_factory(self, env, env_dir):
        def get_module_from_cache(file_abs_path):
            return self._loaded_env_module_cache[file_abs_path]

        def put_module_into_cache(file_abs_path, module):
            self._loaded_env_module_cache[file_abs_path] = module

        def merge_dict(from_dict, to_dict, overwriting=False):
            for k, v in from_dict.items():
                if overwriting or k not in to_dict:
                    to_dict[k] = v

        def load_info_from_loaded_env(env):
            merge_dict(self._loaded_env, env)

        def create_module(file_abs_path, file_name):
            module = imp.new_module(file_name)
            load_info_from_loaded_env(module.__dict__)
            self._init_tttt_env(module.__dict__, os.path.dirname(file_abs_path))
            execfile(file_abs_path, module.__dict__)
            return module

        def put_module_into_env(env, module, module_name):
            if module_name == '':
                merge_dict(module.__dict__, env)
            else:
                env[module_name] = module

        def import_module(file_rel_path, alias=None):
            file_rel_path = os.path.join(*os.path.split(file_rel_path))
            file_abs_path = os.path.join(env_dir, file_rel_path)
            try:
                module = get_module_from_cache(file_abs_path)
            except KeyError:
                file_name = os.path.splitext(os.path.basename(file_rel_path))[0]
                module = create_module(file_abs_path, file_name)
                put_module_into_cache(file_abs_path, module)
            module_name = file_name if alias is None else alias
            put_module_into_env(env, module, module_name)

        return import_module

    def _merge_dicts(self, dict_list):
        return dict(
            reduce(
                operator.concat,
                map(lambda d: d.items(), dict_list)
            )
        )

    def _update_global_env(self):
        self._global_env = self._merge_dicts(
            [self._loaded_env] + self._revisable_env_frames[:-1]
        )

    def _lookup_transformer(self, tag_name):
        for dic in reversed(self._tag_frames):
            if dic.has_key(tag_name):
                return dic[tag_name]
            else:
                continue
        raise Exception(tag_name + ' is not a defined tag')

    def extend_frame(self):
        self._tag_frames.append({})
        self._revisable_env_frames.append({})
        self._update_global_env()

    def retract_frame(self):
        self._tag_frames.pop()
        self._revisable_env_frames.pop()
        self._update_global_env()

    def transform(self, node):
        if DEBUG_MODE:
            global DEBUG_PRINT_INDENT
            DEBUG_PRINT_INDENT += 1
            print ' ' * DEBUG_PRINT_INDENT + node.nodeName
            ret_str = self._lookup_transformer(node.nodeName)(node, self)
            print ' ' * DEBUG_PRINT_INDENT + ret_str
            print ' ' * DEBUG_PRINT_INDENT + node.nodeName
            DEBUG_PRINT_INDENT -= 1
            return ret_str
        else:
            return self._lookup_transformer(node.nodeName)(node, self)

    def register_transformer(self, tag_name, transformer):
        self._tag_frames[-1][tag_name] = transformer

    @property
    def local_env(self):
        return self._revisable_env_frames[-1]

    def evaluate(self, expr):
        try:
            return eval(expr.strip(), self._global_env, self.local_env)
        except Exception as e:
            self.print_state()
            print 'evaluating', expr
            raise e

    def execute(self, stmt):
        try:
            exec (stmt, self._global_env, self.local_env)
        except Exception as e:
            self.print_state()
            print 'executing', stmt
            raise e

    def get_source_dir_path(self, src):
        return os.path.join(self._template_dir, src)

    def load_environment(self, src):
        execfile(
            self.get_source_dir_path(src),
            self._loaded_env
        )

    def print_state(self):
        print 'in', self._template_file
        print 'tag frames', [t.keys() for t in self._tag_frames]
        print 'local env frames', self._revisable_env_frames


class Transformer(object):
    """
    intances of this class transforms a node into a string when called
    """
    @staticmethod
    def to_str(obj):
        if isinstance(obj, unicode):
            return obj
        try:
            return str(obj)
        except UnicodeEncodeError:
            return obj.__str__().encode('utf8')

    def _collect_attributes(self, node, scope):
        if node.attributes is None:
            return dict()

        attr_dict = self._dict_map(node.attributes, lambda v: v.nodeValue)

        for c in node.childNodes:
            if self.is_attribute(c.nodeName):
                attr_dict[c.nodeName] = Transformer()(c, scope)

        return attr_dict

    def _dict_map(self, dictionary, func):
        return dict([
            (k, func(dictionary[k])) for k in dictionary.keys()
        ])

    def _collect_child_tags(self, node):
        return [c for c in node.childNodes
                if self.is_child_tag(c.nodeName)
                and not self.is_attribute(c.nodeName)]

    # for overriding #
    def __call__(self, node, scope):
        attr_dict = self._collect_attributes(node, scope)
        child_tags = self._collect_child_tags(node)
        self.on_entry(scope)
        output = self.collect_transformation(child_tags, attr_dict, scope)
        self.on_exit(scope)
        return output

    def on_entry(self, scope):
        scope.extend_frame()

    def on_exit(self, scope):
        scope.retract_frame()

    def collect_transformation(self, child_tags, attr_dict, scope):
        retvals = [scope.transform(c) for c in child_tags]
        return ''.join(retvals)

    def is_attribute(self, attr):
        return False

    def is_child_tag(self, tag_name):
        return True


class TextTransformer(Transformer):
    def __call__(self, node, scope):
        text = node.nodeValue
        if node.previousSibling is None \
                and text.startswith('\n'):
            text = text[1:]
        return text


class CommentTransformer(Transformer):
    def __call__(self, node, scope):
        return ''


class DefineTransformer(Transformer):
    def collect_transformation(self, child_tags, attr_dict, scope):
        expression = super(DefineTransformer, self).collect_transformation(
            child_tags, attr_dict, scope)

        class NewtagTransformer(Transformer):
            def collect_transformation(self, child_tags, attr_dict, scope):
                return Transformer.to_str(scope.evaluate(expression))

        scope.register_transformer(
            attr_dict['tag'], NewtagTransformer())

        return ''

    def is_attribute(self, attr):
        return attr == 'tag'

    def on_entry(self, scope):
        pass

    def on_exit(self, scope):
        pass


class ExecuteTransformer(Transformer):
    def __call__(self, node, scope):
        stmt = super(ExecuteTransformer, self).__call__(node, scope)
        scope.execute(stmt)
        return ''

    def on_entry(self, scope):
        pass

    def on_exit(self, scope):
        pass


class LoadenvTransformer(Transformer):
    def is_attribute(self, attr):
        return attr == 'src'

    def collect_transformation(self, child_tags, attr_dict, scope):
        scope.load_environment(attr_dict['src'])
        return ''


class TransformTransformer(Transformer):
    def is_attribute(self, attr):
        return attr in ('template', 'environment')

    def collect_transformation(self, child_tags, attr_dict, scope):
        return gen_str(
            scope.get_source_dir_path(attr_dict['template']),
            scope.evaluate(attr_dict['environment'])
        )


class BrTransformer(Transformer):
    def __call__(self, node, scope):
        return '\n'


class CaseTransformer(Transformer):
    def __init__(self, select_cond):
        self.select_cond = select_cond

    def is_attribute(self, attr):
        return attr == 'cond'

    def collect_transformation(self, child_tags, attr_dict, scope):
        if scope.evaluate(attr_dict['cond']) == scope.evaluate(self.select_cond):
            return super(CaseTransformer, self).collect_transformation(
                child_tags, attr_dict, scope)
        else:
            return None

    def is_child_tag(self, tag_name):
        return tag_name != '#text'


class DefaultTransformer(Transformer):
    def is_child_tag(self, tag_name):
        return tag_name != '#text'


class SelectTransformer(Transformer):
    def is_attribute(self, attr):
        return attr == 'cond'

    def collect_transformation(self, child_tags, attr_dict, scope):
        for c in child_tags:
            if c.nodeName == 'case':
                output = CaseTransformer(attr_dict['cond'])(c, scope)
                if output is not None:
                    return output
            elif c.nodeName == 'default':
                return DefaultTransformer()(c, scope)
        return ''

    def is_child_tag(self, tag_name):
        return tag_name != '#text'


class RepeatTransformer(Transformer):
    def is_attribute(self, attr):
        return attr == 'times'

    def collect_transformation(self, child_tags, attr_dict, scope):
        times = scope.evaluate(attr_dict['times'])
        ret_blocks = []
        default_collect = super(RepeatTransformer, self). \
            collect_transformation
        for i in range(0, times):
            ret_blocks.append(default_collect(child_tags, attr_dict, scope))
        return ''.join(ret_blocks)

    def is_child_tag(self, tag_name):
        return tag_name != '#text'


class EnumerateTransformer(Transformer):
    class IndexTransformer(Transformer):
        def __init__(self, index):
            self.index = index

        def __call__(self, node, scope):
            return str(self.index)

    class OrderTransformer(Transformer):
        def __init__(self, order_obj):
            self.order_obj = order_obj

        def __call__(self, node, scope):
            return str(self.order_obj)

    class ItemTransformer(Transformer):
        def __init__(self, item_id):
            self.item_id = item_id

        def __call__(self, node, scope):
            return str(scope.evaluate(self.item_id))

    def collect_transformation(self, child_tags, attr_dict, scope):
        container = self._get_attr_container(attr_dict, scope)
        item_id = self._get_attr_item(attr_dict)
        unique = self._get_attr_unique(attr_dict)
        order_func = self._get_attr_order(attr_dict, scope)
        order_tag = self._get_attr_order_tag(attr_dict)
        index_tag = self._get_attr_index_tag(attr_dict)

        scope.register_transformer(
            item_id, EnumerateTransformer.ItemTransformer(item_id))

        blocks = []
        blocks_set = set()

        it = iter(container)
        for i in range(0, len(container)):
            item = it.next()
            scope.local_env[item_id] = item

            if order_func is None:
                order = i
            else:
                order = order_func(item)
                scope.register_transformer(
                    order_tag, EnumerateTransformer.OrderTransformer(order))

            scope.register_transformer(
                index_tag, EnumerateTransformer.IndexTransformer(i))

            block = super(EnumerateTransformer, self). \
                collect_transformation(child_tags, attr_dict, scope)

            if unique:
                if block in blocks_set:
                    continue
                blocks_set.add(block)

            blocks.append((order, block))

        sorted_blocks = [t[1] for t in sorted(blocks, key=lambda t: t[0])]
        return ''.join(sorted_blocks)

    def _get_attr_container(self, attr_dict, scope):
        return scope.evaluate(attr_dict['container'])

    def _get_attr_order(self, attr_dict, scope):
        try:
            return scope.evaluate(attr_dict['order'])
        except KeyError:
            return None

    def _get_attr_order_tag(self, attr_dict):
        try:
            return attr_dict['order_tag']
        except KeyError:
            return 'order'

    def _get_attr_index_tag(self, attr_dict):
        try:
            return attr_dict['index_tag']
        except KeyError:
            return 'index'

    def _get_attr_unique(self, attr_dict):
        try:
            if attr_dict['unique'] == 'yes':
                return True
            return False
        except KeyError:
            return False

    def _get_attr_item(self, attr_dict):
        try:
            return attr_dict['item']
        except KeyError:
            return '__item_id__'

    def is_attribute(self, attr):
        return attr in ['container', 'item', 'order', 'unique']

    def is_child_tag(self, tag_name):
        return tag_name != '#text'


class TttTransformer(Transformer):
    def on_entry(self, scope):
        super(TttTransformer, self).on_entry(scope)
        scope.register_transformer('br', BrTransformer())
        scope.register_transformer('raw', Transformer())
        scope.register_transformer('select', SelectTransformer())
        scope.register_transformer('repeat', RepeatTransformer())
        scope.register_transformer('enumerate', EnumerateTransformer())
        scope.register_transformer('#text', TextTransformer())
        scope.register_transformer('#comment', CommentTransformer())
        scope.register_transformer('define', DefineTransformer())
        scope.register_transformer('execute', ExecuteTransformer())
        scope.register_transformer('loadenv', LoadenvTransformer())
        scope.register_transformer('transform', TransformTransformer())

    def is_child_tag(self, tag_name):
        return tag_name != '#text'


def init_scope(template_file, target_file, env={}):
    return Scope(
        {
            '#document': Transformer(),
            'ttt': TttTransformer()
        },
        env,
        template_file,
        target_file
    )


def get_dom(file):
    return minidom.parse(file)


def get_output(scope, dom):
    return scope.transform(dom)


def write_output(file, output):
    with open(file, 'w') as f:
        f.write(output.encode('utf8'))


def gen(template_file, target_file, env_statements=''):
    env = {}
    if env_statements:
        exec env_statements in env
    scope = init_scope(template_file, target_file, env)
    write_output(
        target_file,
        get_output(
            scope,
            get_dom(template_file)))

def gen_str(template_file, env={}):
    return get_output(
        init_scope(template_file, None, env),
        get_dom(template_file))


if __name__ == '__main__':
    import cmd_entry
    cmd_entry.enter(gen)
