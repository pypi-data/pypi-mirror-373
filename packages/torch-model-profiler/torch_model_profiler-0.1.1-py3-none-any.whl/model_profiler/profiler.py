import torch
import torch.nn as nn
from prettytable import PrettyTable



def profile_flops_and_memory_layername(model, 
                                       input_size=(1, 3, 224, 224),
                                       threshold_low=10, 
                                       threshold_high=100,
                                       mode="raw",
                                       skip_bn=True,
                                       skip_act=True,
                                       skip_Sequential=True):
    """
    分析模型 FLOPs / Memory，輸出以 layer name 為主 (不顯示層級縮排)。
    支援三種模式：
      - mode="raw":   全部子層展開 (Conv, BN, ReLU …)
      - mode="cba":   合併 Conv+BN+Act 到外層 CBA
      - mode="block": 合併到 backbone / neck / head 大 block
    """

    layer_stats = []
    cba_buf, block_buf = {}, {}

    # ===== 判斷 Tag/顏色 =====
    def _make_tag_color(ratio):
        if ratio < threshold_low:  return "Memory-bound ❗", "red"
        if ratio > threshold_high: return "Compute-bound ⚡", "blue"
        return "Balanced", "green"

    # ===== 工具 =====
    def _find_cba_parent(name: str):
        parts = name.split(".")
        if "cba_unit" in parts:
            i = parts.index("cba_unit")
            return ".".join(parts[:i])  # e.g. backbone.conv_P1_1
        return None

    def get_numel(x):
        if torch.is_tensor(x): return x.numel()
        if isinstance(x, (tuple, list)):
            return sum(get_numel(xx) for xx in x if torch.is_tensor(xx))
        return 0

    def get_params(layer):
        p = 0
        if hasattr(layer, "weight") and layer.weight is not None:
            p += layer.weight.numel()
        if hasattr(layer, "bias") and layer.bias is not None:
            p += layer.bias.numel()
        return p

    # ===== 記錄統計 =====
    def add_stats(name, layer, inp, out, flops, total_bytes):
        parent_cba = _find_cba_parent(name)

        # Input/Output Shape
        in_shape  = str(tuple(inp[0].shape)) if isinstance(inp, (list, tuple)) else str(inp.shape)
        out_shape = str(out.numpy().shape) if torch.is_tensor(out) else "?"

        # ---- Mode: cba ----
        if mode in {"cba", "block"} and parent_cba is not None:
            buf = cba_buf.setdefault(parent_cba, {
                "flops": 0, "mem": 0, "params": 0,
                "in_shape": in_shape, "out_shape": out_shape,
                "lname": f"{parent_cba} (CBA)"
            })
            buf["flops"]  += flops
            buf["mem"]    += total_bytes
            buf["params"] += get_params(layer)
            buf["out_shape"] = out_shape  # 更新到最後一層的 output shape
            return

        # ---- Mode: block ----
        if mode == "block":
            top = name.split(".")[0]
            block_buf.setdefault(top, {
                "flops": 0, "mem": 0, "params": 0,
                "in_shape": in_shape, "out_shape": out_shape,
                "lname": top
            })
            block_buf[top]["flops"]  += flops
            block_buf[top]["mem"]    += total_bytes
            block_buf[top]["params"] += get_params(layer)
            block_buf[top]["out_shape"] = out_shape
            return

        # ---- raw or 非 wrapper ----
        if mode == "raw":
            ratio = flops / total_bytes if total_bytes > 0 else 0
            tag, color = _make_tag_color(ratio)
            lname = f"{name} ({layer.__class__.__name__})"
            layer_stats.append((name, lname, in_shape, out_shape,
                                flops, total_bytes, ratio,
                                get_params(layer), tag, color))

    # ===== Hook 定義 =====
    def conv_hook(layer, name):
        def hook(self, input, output):
            if not torch.is_tensor(output): return
            b, Cin, H, W = input[0].shape
            Cout, _, Kh, Kw = self.weight.shape
            flops = b * Cout * H * W * (Cin * Kh * Kw * 2)
            mem = (get_numel(input[0]) + get_numel(output) +
                   self.weight.numel() + (self.bias.numel() if self.bias is not None else 0)) * 4
            add_stats(name, self, input, output, flops, mem)
        return hook

    def linear_hook(layer, name):
        def hook(self, input, output):
            b, In = input[0].shape
            Out = output.shape[1]
            flops = b * In * Out * 2
            mem = (get_numel(input[0]) + get_numel(output) +
                   self.weight.numel() + (self.bias.numel() if self.bias is not None else 0)) * 4
            add_stats(name, self, input, output, flops, mem)
        return hook

    def bn_hook(layer, name):
        def hook(self, input, output):
            flops = get_numel(input[0]) * 2
            w = (layer.weight.numel() if layer.weight is not None else 0)
            b = (layer.bias.numel() if layer.bias is not None else 0)
            mem = (get_numel(input[0]) + get_numel(output) + w + b) * 4
            add_stats(name, self, input, output, flops, mem)
        return hook

    def relu_hook(layer, name):
        def hook(self, input, output):
            flops = get_numel(input[0])
            mem = (get_numel(input[0]) + get_numel(output)) * 4
            add_stats(name, self, input, output, flops, mem)
        return hook

    def pool_hook(layer, name):
        def hook(self, input, output):
            ks = layer.kernel_size if isinstance(layer.kernel_size, tuple) else (layer.kernel_size, layer.kernel_size)
            flops = get_numel(output) * (ks[0] * ks[1])
            mem = (get_numel(input[0]) + get_numel(output)) * 4
            add_stats(name, self, input, output, flops, mem)
        return hook

    
    def default_hook(layer, name):
        def hook(self, input, output):
            mem = (get_numel(input[0]) + get_numel(output)) * 4
            add_stats(name, self, input, output, 0, mem)
        return hook

    # ===== 掛 Hook =====
    hooks = []
    for name, layer in model.named_modules():
        if isinstance(layer, nn.Conv2d):
            hooks.append(layer.register_forward_hook(conv_hook(layer, name)))
        elif isinstance(layer, nn.Linear):
            hooks.append(layer.register_forward_hook(linear_hook(layer, name)))
        elif isinstance(layer, (nn.BatchNorm2d, nn.BatchNorm1d)):
            if not skip_bn:
                hooks.append(layer.register_forward_hook(bn_hook(layer, name)))
        elif isinstance(layer, (nn.ReLU, nn.LeakyReLU)):
            if not skip_act:
                hooks.append(layer.register_forward_hook(relu_hook(layer, name)))
        elif isinstance(layer, (nn.MaxPool2d, nn.AvgPool2d)):
            hooks.append(layer.register_forward_hook(pool_hook(layer, name)))
        elif isinstance(layer, (nn.Sequential)):
            if not skip_Sequential:
                hooks.append(layer.register_forward_hook(default_hook(layer, name)))
        else:
            hooks.append(layer.register_forward_hook(default_hook(layer, name)))

    # ===== Forward =====
    dummy_input = torch.randn(*input_size)
    model.eval()
    with torch.no_grad():
        model(dummy_input)
    for h in hooks: h.remove()

    # ===== 合併模式處理 =====
    if mode in {"cba", "block"}:
        for key, val in cba_buf.items():
            flops, mem, params = val["flops"], val["mem"], val["params"]
            in_shape, out_shape = val["in_shape"], val["out_shape"]
            ratio = flops / mem if mem > 0 else 0
            tag, color = _make_tag_color(ratio)
            layer_stats.append((key, val["lname"], in_shape, out_shape,
                                flops, mem, ratio, params, tag, color))

    if mode == "block":
        for key, val in block_buf.items():
            flops, mem, params = val["flops"], val["mem"], val["params"]
            in_shape, out_shape = val["in_shape"], val["out_shape"]
            ratio = flops / mem if mem > 0 else 0
            tag, color = _make_tag_color(ratio)
            layer_stats.append((key, val["lname"], in_shape, out_shape,
                                flops, mem, ratio, params, tag, color))

    # ===== 輸出表格 =====
    table = PrettyTable(["Layer(Name)", "Input Shape", "Output Shape",
                         "FLOPs (M)", "Memory (KB)", "FLOP/Byte", "Params (K)", "Tag"])
    total_flops, total_mem, total_params = 0, 0, 0
    for _, lname, in_shape, out_shape, f, m, r, params, tag, _ in layer_stats:
        total_flops  += f
        total_mem    += m
        total_params += params
        table.add_row([lname, in_shape, out_shape, f/1e6, m/1024, round(r, 2), params/1e3, tag])
    print(table)

    total_ratio = (total_flops / total_mem) if total_mem > 0 else 0
    print(f"\nTotal FLOPs: {total_flops/1e9:.3f} GFLOPs")
    print(f"Total Memory: {total_mem/1e6:.3f} MB")
    print(f"Total Params: {total_params/1e6:.3f} M")
    print(f"Overall FLOPs-to-Memory Ratio: {total_ratio:.3f}")

    return layer_stats

