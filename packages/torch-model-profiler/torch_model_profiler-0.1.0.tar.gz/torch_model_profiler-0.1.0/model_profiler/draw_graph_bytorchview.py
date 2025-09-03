from torchview import draw_graph


def draw_model_with_tags(model, input_size, filename="model_bound"):
    # === 建立 name ↔ module 映射 ===
    name_to_module = {name: module for name, module in model.named_modules()}

    # === 建立 Torchview Graph ===
    graph = draw_graph(model, input_size=(input_size,), 
                       expand_nested=True, 
                       hide_inner_tensors=False, 
                       hide_module_functions=True)
    dot = graph.visual_graph

    # 強制字型
    dot.attr('graph', fontname="Arial")
    dot.attr('node', fontname="Arial")
    dot.attr('edge', fontname="Arial")

    # === 重新設定每個 node 的 label ===
    node_labels = {}
    new_body = []
    for line in dot.body:
        if "[" in line and "label=" in line:
            node_id = line.split("[", 1)[0].strip()

            # 嘗試找到匹配的 profiler 名稱
            matched_name = None
            for name in name_to_module.keys():
                if name in line:  # torchview label 裡通常會有類型
                    matched_name = name
                    break

            if matched_name:
                module_type = name_to_module[matched_name].__class__.__name__
                label_text = f"{matched_name} ({module_type})"
                new_body.append(f'{node_id} [label="{label_text}"]\n')
                node_labels[node_id] = label_text
            else:
                new_body.append(line)
        else:
            new_body.append(line)
    dot.body = new_body


    dot.render(filename, format="png", cleanup=True)
    print(f"\n✅ model structure exports as {filename}.png")
    
