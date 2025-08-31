import os
import uuid
from pathlib import Path
import networkx as nx

# ANSI 颜色代码，用于美化终端输出
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class KnowledgeGraphManager:
    """
    一个使用 NetworkX 管理知识图谱的管理器。
    - 图数据存储在 networkx.DiGraph 对象中。
    - 数据持久化为 GraphML 文件。
    - 提供添加、删除、重命名、移动节点和渲染树状图的功能。
    """
    def __init__(self, storage_path="knowledge_graph.graphml"):
        self.storage_path = Path(storage_path)
        self.graph = nx.DiGraph()
        self._load_graph()

    def _load_graph(self):
        """从文件加载图，如果文件不存在则创建一个新的。"""
        if self.storage_path.exists():
            try:
                # 明确指定 node_type=str 来避免类型推断问题
                self.graph = nx.read_graphml(self.storage_path, node_type=str)
                print(f"✅ 已从 '{self.storage_path}' 加载知识图谱。")
            except Exception as e:
                print(f"⚠️ 加载图文件失败: {e}。将创建一个新的空图谱。")
                self._create_new_graph()
        else:
            print(f"ℹ️ 未找到图文件，正在创建新的知识图谱...")
            self._create_new_graph()

    def _create_new_graph(self):
        """创建一个带有根节点的新图谱。"""
        self.graph = nx.DiGraph()
        self.graph.add_node("root", name=".", description="知识图谱根节点", tags="")

    def _save_graph(self):
        """将当前图的状态保存到文件。"""
        try:
            nx.write_graphml(self.graph, self.storage_path)
            print("💾 图谱已保存。")
        except Exception as e:
            print(f"❌ 保存图谱失败: {e}")

    def _get_node_id_by_path(self, path: str):
        """通过'/'分隔的路径查找节点的唯一ID。"""
        if path is None or not path.strip() or path.strip() in ['.', '/']:
            return "root"

        segments = [s for s in path.strip('/').split('/') if s and s != '.']
        current_node_id = "root"

        for i, segment in enumerate(segments):
            found_child = False
            for child_id in self.graph.successors(current_node_id):
                if self.graph.nodes[child_id].get('name') == segment:
                    current_node_id = child_id
                    found_child = True
                    break
            if not found_child:
                return None
        return current_node_id

    def add_node(self, parent_path: str, node_name: str, description: str = "", tags: list[str] = None) -> str:
        """在指定父节点下添加一个新节点。"""
        if not node_name.strip():
            return "❌ 错误：节点名称不能为空。"
        if '/' in node_name:
            return f"❌ 错误：节点名称 '{node_name}' 不能包含'/'。"

        parent_id = self._get_node_id_by_path(parent_path)
        if parent_id is None:
            return f"❌ 错误：父路径 '{parent_path}' 不存在。"

        for child_id in self.graph.successors(parent_id):
            if self.graph.nodes[child_id].get('name') == node_name:
                return f"❌ 错误：在 '{parent_path}' 下已存在名为 '{node_name}' 的节点。"

        new_node_id = str(uuid.uuid4())
        tags_str = ",".join(sorted(list(set(filter(None, tags or [])))))
        self.graph.add_node(new_node_id, name=node_name, description=description, tags=tags_str)
        self.graph.add_edge(parent_id, new_node_id)

        self._save_graph()
        return f"✅ 成功在 '{parent_path}' 下添加节点 '{node_name}'。"

    def _get_tags(self, node_id: str) -> list[str]:
        """获取节点的标签列表。"""
        tags_str = self.graph.nodes[node_id].get('tags', '')
        return tags_str.split(',') if tags_str else []

    def _set_tags(self, node_id: str, tags: list[str]):
        """设置节点的标签列表。"""
        unique_tags = sorted(list(set(filter(None, tags))))
        self.graph.nodes[node_id]['tags'] = ",".join(unique_tags)

    def add_tags_to_node(self, node_path: str, tags_to_add: list[str]) -> str:
        """向指定节点添加一个或多个标签。"""
        node_id = self._get_node_id_by_path(node_path)
        if node_id is None:
            return f"❌ 错误：路径 '{node_path}' 不存在。"

        current_tags = self._get_tags(node_id)
        current_tags.extend(tags_to_add)
        self._set_tags(node_id, current_tags)
        self._save_graph()
        return f"✅ 成功向节点 '{node_path}' 添加标签: {', '.join(tags_to_add)}。"

    def remove_tags_from_node(self, node_path: str, tags_to_remove: list[str]) -> str:
        """从指定节点移除一个或多个标签。"""
        node_id = self._get_node_id_by_path(node_path)
        if node_id is None:
            return f"❌ 错误：路径 '{node_path}' 不存在。"

        current_tags = self._get_tags(node_id)
        if not current_tags:
            return f"ℹ️ 节点 '{node_path}' 没有任何标签可供移除。"

        new_tags = [tag for tag in current_tags if tag not in tags_to_remove]

        if len(new_tags) == len(current_tags):
            return f"ℹ️ 在节点 '{node_path}' 上未找到指定的标签: {', '.join(tags_to_remove)}。"

        self._set_tags(node_id, new_tags)
        self._save_graph()
        return f"✅ 成功从节点 '{node_path}' 移除标签。"

    def delete_node(self, node_path: str) -> str:
        """删除一个节点及其所有子孙节点。"""
        if node_path is None or node_path.strip() in ['.', '/']:
            return "❌ 错误：不能删除根节点。"

        node_id = self._get_node_id_by_path(node_path)
        if node_id is None:
            return f"❌ 错误：路径 '{node_path}' 不存在。"

        descendants = nx.descendants(self.graph, node_id)
        nodes_to_delete = descendants.union({node_id})

        self.graph.remove_nodes_from(nodes_to_delete)
        self._save_graph()
        return f"✅ 成功删除节点 '{node_path}' 及其所有子节点。"

    def rename_node(self, node_path: str, new_name: str) -> str:
        """重命名一个节点。"""
        if not new_name.strip():
            return "❌ 错误：新名称不能为空。"
        if '/' in new_name:
            return f"❌ 错误：新名称 '{new_name}' 不能包含'/'。"

        node_id = self._get_node_id_by_path(node_path)
        if node_id is None:
            return f"❌ 错误：路径 '{node_path}' 不存在。"
        if node_id == "root":
            return "❌ 错误：不能重命名根节点。"

        parent_id = list(self.graph.predecessors(node_id))[0]
        for sibling_id in self.graph.successors(parent_id):
            if sibling_id != node_id and self.graph.nodes[sibling_id].get('name') == new_name:
                return f"❌ 错误：同级目录下已存在名为 '{new_name}' 的节点。"

        self.graph.nodes[node_id]['name'] = new_name
        self._save_graph()
        return f"✅ 成功将节点 '{node_path}' 重命名为 '{new_name}'。"

    def move_node(self, source_path: str, target_parent_path: str) -> str:
        """将一个节点移动到另一个父节点下。"""
        if source_path is None or source_path.strip() in ['.', '/']:
            return "❌ 错误：不能移动根节点。"

        source_id = self._get_node_id_by_path(source_path)
        if source_id is None:
            return f"❌ 错误：源路径 '{source_path}' 不存在。"

        target_parent_id = self._get_node_id_by_path(target_parent_path)
        if target_parent_id is None:
            return f"❌ 错误：目标父路径 '{target_parent_path}' 不存在。"

        # 检查是否尝试将节点移动到其自身或其子孙节点下
        if source_id == target_parent_id or target_parent_id in nx.descendants(self.graph, source_id):
            return f"❌ 错误：不能将节点移动到其自身或其子孙节点下。"

        source_name = self.graph.nodes[source_id]['name']
        for child_id in self.graph.successors(target_parent_id):
            if self.graph.nodes[child_id].get('name') == source_name:
                return f"❌ 错误：目标目录 '{target_parent_path}' 下已存在同名节点 '{source_name}'。"

        old_parent_id = list(self.graph.predecessors(source_id))[0]
        self.graph.remove_edge(old_parent_id, source_id)
        self.graph.add_edge(target_parent_id, source_id)
        self._save_graph()
        return f"✅ 成功将节点 '{source_path}' 移动到 '{target_parent_path}' 下。"

    def _get_path_by_node_id(self, node_id: str) -> str:
        """通过节点ID获取其在图中的完整路径。"""
        if node_id == "root":
            return "."

        path_segments = []
        current_id = node_id
        while current_id != "root":
            if current_id not in self.graph:
                return None

            predecessors = list(self.graph.predecessors(current_id))
            if not predecessors:
                return None

            parent_id = predecessors[0]
            node_name = self.graph.nodes[current_id].get('name')
            if node_name is None:
                return None

            path_segments.append(node_name)
            current_id = parent_id

        return "/".join(reversed(path_segments))

    def get_node_details(self, node_path: str) -> str:
        """获取指定路径节点的所有详细信息。"""
        node_id = self._get_node_id_by_path(node_path)
        if node_id is None:
            path_segments = [s for s in node_path.strip('/').split('/') if s and s != '.']
            if not path_segments:
                return f"❌ 错误：路径 '{node_path}' 不存在。"

            target_name = path_segments[-1]
            suggestions = []
            for n_id, data in self.graph.nodes(data=True):
                if n_id != 'root' and target_name in data.get('name', ''):
                    full_path = self._get_path_by_node_id(n_id)
                    if full_path:
                        suggestions.append(full_path)

            if suggestions:
                suggestions = sorted(list(set(suggestions)))
                message = f"❌ 错误：路径 '{node_path}' 不存在。\n\n您是不是要找：\n"
                message += "\n".join([f"- {s}" for s in suggestions])
                return message
            else:
                return f"❌ 错误：路径 '{node_path}' 不存在。"

        node_data = self.graph.nodes[node_id]
        description = node_data.get('description', '无描述。')
        tags = self._get_tags(node_id)

        details = [f"节点: {node_path}", f"描述: {description}"]
        if tags:
            details.append(f"标签: {' '.join([f'#{t}' for t in tags])}")
        else:
            details.append("标签: 无")

        return "\n".join(details)

    def render_tree(self, show_source_tags=False) -> str:
        """渲染整个知识图谱为树状结构的文本。"""
        if not self.graph or "root" not in self.graph:
            return "图谱为空或未正确初始化。"

        tree_lines = [self.graph.nodes["root"]["name"]]
        # 调用递归函数来构建树
        self._build_tree_string_recursive("root", "", tree_lines, show_source_tags)
        return "\n".join(tree_lines)

    def _build_tree_string_recursive(self, parent_id, prefix, tree_lines, show_source_tags=False):
        """递归辅助函数，用于构建树状图字符串。"""
        children = sorted(list(self.graph.successors(parent_id)), key=lambda n: self.graph.nodes[n]['name'])

        num_children = len(children)
        for i, child_id in enumerate(children):
            is_last = (i == num_children - 1)
            connector = "└── " if is_last else "├── "
            node_name = self.graph.nodes[child_id].get('name', '[Unnamed Node]')

            # 显示标签，过滤掉以'source'开头的标签
            tags = self._get_tags(child_id)
            if show_source_tags:
                display_tags = tags
            else:
                display_tags = [t for t in tags if not t.startswith('source')]

            if display_tags:
                node_name += f" {' '.join([f'#{t}' for t in display_tags])}"

            tree_lines.append(f"{prefix}{connector}{node_name}")

            new_prefix = prefix + "    " if is_last else prefix + "│   "
            self._build_tree_string_recursive(child_id, new_prefix, tree_lines)

def print_menu():
    """打印交互式菜单。"""
    print("\n" + "="*50)
    print("知识图谱管理器 - 交互式测试菜单")
    print("="*50)
    print(f"{colors.OKCYAN}1. 🌲 显示知识图谱树状图{colors.ENDC}")
    print(f"{colors.OKGREEN}2. ➕ 添加节点{colors.ENDC}")
    print(f"{colors.FAIL}3. ❌ 删除节点{colors.ENDC}")
    print(f"{colors.OKBLUE}4. ✏️ 重命名节点{colors.ENDC}")
    print(f"{colors.OKBLUE}5. ➡️ 移动节点{colors.ENDC}")
    print(f"{colors.OKCYAN}6. 🏷️ 添加标签{colors.ENDC}")
    print(f"{colors.OKCYAN}7. 🗑️ 移除标签{colors.ENDC}")
    print(f"{colors.OKBLUE}8. ℹ️  查看节点详细信息{colors.ENDC}")
    print(f"{colors.WARNING}9. 💥 删除图谱文件并重置{colors.ENDC}")
    print("0. 退出")
    print("-"*50)

def main_test_loop():
    """主测试循环。"""
    kgm = KnowledgeGraphManager()

    while True:
        print_menu()
        choice = input("请输入您的选择: ")

        if choice == '1':
            print("\n--- 当前知识图谱结构 ---")
            print(kgm.render_tree())
            print("------------------------")
        elif choice == '2':
            parent_path = input("请输入父节点路径 (例如 'a/b', 根节点为'.'): ")
            node_name = input("请输入新节点名称: ")
            description = input("请输入节点描述 (可选): ")
            tags_str = input("请输入标签, 以逗号分隔 (可选): ")
            tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
            result = kgm.add_node(parent_path, node_name, description, tags)
            print(f"\n{result}")
        elif choice == '3':
            node_path = input("请输入要删除的节点路径 (例如 'a/b'): ")
            result = kgm.delete_node(node_path)
            print(f"\n{result}")
        elif choice == '4':
            node_path = input("请输入要重命名的节点路径: ")
            new_name = input("请输入新名称: ")
            result = kgm.rename_node(node_path, new_name)
            print(f"\n{result}")
        elif choice == '5':
            source_path = input("请输入要移动的节点路径: ")
            target_parent_path = input("请输入目标父节点路径: ")
            result = kgm.move_node(source_path, target_parent_path)
            print(f"\n{result}")
        elif choice == '6':
            node_path = input("请输入要添加标签的节点路径: ")
            tags_str = input("请输入要添加的标签 (以逗号分隔): ")
            tags_to_add = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
            result = kgm.add_tags_to_node(node_path, tags_to_add)
            print(f"\n{result}")
        elif choice == '7':
            node_path = input("请输入要移除标签的节点路径: ")
            tags_str = input("请输入要移除的标签 (以逗号分隔): ")
            tags_to_remove = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
            result = kgm.remove_tags_from_node(node_path, tags_to_remove)
            print(f"\n{result}")
        elif choice == '8':
            node_path = input("请输入要查看详情的节点路径: ")
            details = kgm.get_node_details(node_path)
            print("\n--- 节点详细信息 ---")
            print(details)
            print("------------------------")
        elif choice == '9':
            if kgm.storage_path.exists():
                confirm = input(f"⚠️ 确定要删除 '{kgm.storage_path}' 并重置吗? (y/n): ").lower()
                if confirm == 'y':
                    os.remove(kgm.storage_path)
                    kgm = KnowledgeGraphManager(kgm.storage_path)
                    print("✅ 图谱文件已删除并重置。")
                else:
                    print("ℹ️ 操作已取消。")
            else:
                print("ℹ️ 图谱文件不存在，无需删除。")
        elif choice == '0':
            print("退出程序。")
            break
        else:
            print("无效输入，请输入0-9之间的数字。")

        input("\n按回车键继续...")

def run_automated_tests():
    """运行自动化测试，验证核心功能。"""
    print("\n" + "="*50)
    print("🚀 开始运行自动化测试...")
    print("="*50)

    test_file = "test_graph.graphml"
    if os.path.exists(test_file):
        os.remove(test_file)

    kgm = KnowledgeGraphManager(storage_path=test_file)

    # 1. 测试节点建议功能
    print("\n" + colors.HEADER + "1. 测试 'get_node_details' 的建议功能..." + colors.ENDC)
    kgm.add_node(".", "技术")
    kgm.add_node("技术", "深度学习")
    kgm.add_node("技术/深度学习", "挑战")
    kgm.add_node(".", "应用")
    kgm.add_node("应用", "挑战")

    # 查找一个不存在但有明确建议的节点
    result = kgm.get_node_details("挑战")
    expected_suggestions = ["技术/深度学习/挑战", "应用/挑战"]

    print(f"查询 '挑战' 的结果:\n{result}")

    all_found = all(suggestion in result for suggestion in expected_suggestions)
    if "您是不是要找" in result and all_found:
        print(colors.OKGREEN + "✅ 测试通过: 成功提供了正确的建议。" + colors.ENDC)
    else:
        print(colors.FAIL + "❌ 测试失败: 未能提供正确的建议。" + colors.ENDC)

    # 2. 清理测试文件
    if os.path.exists(test_file):
        os.remove(test_file)
    print("\n" + "🧹 清理测试文件完成。")
    print("\n" + "="*50)
    print("✅ 自动化测试结束。")
    print("="*50)


if __name__ == "__main__":
    run_automated_tests()
    main_test_loop()
