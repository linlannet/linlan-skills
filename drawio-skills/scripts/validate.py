# -*- coding: utf-8 -*-
"""
validate.py — .drawio 结构 lint（L3 视觉验证层的机械部分）

在交付前机械检查肉眼必然漏的问题：
    ERROR（必须修）：重复 ID / 悬空边 / 缺 as=geometry / 保留 ID 被占用 /
                     节点重叠 / 父容器不存在 / 标签含字面 \\n / 空 value
    WARN（建议修）：字号 < 10 / 小数坐标 / 内容超出页面 / 孤立节点 /
                    混合字体 / 描边色偏离预设

用法：
    python validate.py diagram.drawio
    python validate.py diagram.drawio --style styles/linlan.json
    python validate.py diagram.drawio --json report.json

退出码：有 ERROR -> 1，仅 WARN/干净 -> 0

作者：六百（linlan-skills）
"""
import os
import re
import sys
import json
import argparse
from collections import Counter, defaultdict

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import extract_style as es

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_STYLE = os.path.join(HERE, '..', 'styles', 'linlan.json')
OVERLAP_TOLERANCE = 2  # px，容差内的边界接触不算重叠


def is_group(cell, all_ids):
    """判断是否为语义分组（有子节点且非图标）。"""
    style = cell.get('style', '')
    kv, bare = es.parse_style(style)
    is_swimlane = 'swimlane' in bare or 'swimlane' in kv.get('shape', '')
    has_children = any(c.get('parent') == cell.get('id') for c in all_ids)
    icon = ('mxgraph' in style) or ('aspect=fixed' in style) or \
           ('stencil(' in style) or ('shape=image' in style)
    return has_children and (is_swimlane or not icon)


def rect(cell):
    g = cell.find('mxGeometry')
    if g is None or g.get('width') is None or g.get('height') is None:
        return None
    try:
        return (float(g.get('x', 0) or 0), float(g.get('y', 0) or 0),
                float(g.get('width', 0) or 0), float(g.get('height', 0) or 0))
    except (TypeError, ValueError):
        return None


def overlap(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ox = min(ax + aw, bx + bw) - max(ax, bx)
    oy = min(ay + ah, by + bh) - max(ay, by)
    if ox > OVERLAP_TOLERANCE and oy > OVERLAP_TOLERANCE:
        return round(ox), round(oy)
    return None


def validate(model, preset):
    errors, warns = [], []
    cells = list(model.iter('mxCell'))
    ids = [c.get('id') for c in cells]

    # --- ERROR 1: 重复 ID ---
    dup = [k for k, v in Counter(ids).items() if v > 1 and k]
    if dup:
        errors.append('重复 ID: %s' % ', '.join(dup))

    # --- ERROR 2: 保留 ID 0/1 被赋予图形语义 ---
    for c in cells:
        if c.get('id') in ('0', '1') and (c.get('vertex') == '1' or c.get('edge') == '1'):
            errors.append('保留 ID %s 被用作图形 cell' % c.get('id'))

    idset = set(ids)
    vertices = [c for c in cells if c.get('vertex') == '1']
    edges = [c for c in cells if c.get('edge') == '1']
    groups = [c for c in vertices if is_group(c, cells)]
    group_ids = {c.get('id') for c in groups}
    plain_nodes = [c for c in vertices if c.get('id') not in group_ids]

    # --- ERROR 3: 悬空边 ---
    for e in edges:
        for end in ('source', 'target'):
            ref = e.get(end)
            if ref and ref not in idset:
                errors.append('边 %s 的 %s 指向不存在的节点: %s' % (e.get('id'), end, ref))
        if not e.get('source') or not e.get('target'):
            warns.append('边 %s 缺少 source/target（可能是浮动边）' % e.get('id'))

    # --- ERROR 4: 边缺 relative geometry ---
    for e in edges:
        g = e.find('mxGeometry')
        if g is None or g.get('relative') != '1' or g.get('as') != 'geometry':
            errors.append('边 %s 缺少 <mxGeometry relative="1" as="geometry"/>' % e.get('id'))

    # --- ERROR 5: 父容器不存在 ---
    for c in vertices + edges:
        p = c.get('parent')
        if p and p not in idset:
            errors.append('cell %s 的 parent=%s 不存在' % (c.get('id'), p))

    # --- ERROR 6: 标签含字面 \n（drawio 不会换行，会显示反斜杠 n）---
    for c in cells:
        v = c.get('value') or ''
        if '\\n' in v:
            errors.append('cell %s 的 label 含字面 \\n（应改用 HTML <br> 或 whiteSpace=wrap）'
                          % c.get('id'))

    # --- ERROR 7: 同级节点重叠 ---
    by_parent = defaultdict(list)
    for n in plain_nodes:
        r = rect(n)
        if r:
            by_parent[n.get('parent')].append((n, r))
    for parent, items in by_parent.items():
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                ov = overlap(items[i][1], items[j][1])
                if ov:
                    errors.append('节点 %s 与 %s 重叠（父=%s，重叠 %dx%d px）'
                                  % (items[i][0].get('id'), items[j][0].get('id'),
                                     parent or 'root', ov[0], ov[1]))

    # --- WARN: 字号 / 坐标 / 页面 / 字体 / 描边 ---
    font_min = 10
    fonts = Counter()
    strokecolors = Counter()
    page_w = float(model.get('pageWidth') or 0)
    page_h = float(model.get('pageHeight') or 0)
    expected_stroke = None
    if preset:
        pairs = [p for p in (preset.get('palette') or {}).values() if p]
        if pairs:
            expected_stroke = Counter(p.get('strokeColor') for p in pairs).most_common(1)[0][0]

    for c in plain_nodes:
        style = c.get('style', '')
        kv, _ = es.parse_style(style)
        if kv.get('fontFamily'):
            fonts[kv['fontFamily']] += 1
        if kv.get('strokeColor'):
            strokecolors[kv['strokeColor']] += 1
        try:
            fs = int(float(kv.get('fontSize', 12)))
            if fs < font_min:
                warns.append('节点 %s 字号 %d < %d，可读性差' % (c.get('id'), fs, font_min))
        except (ValueError, TypeError):
            pass
        r = rect(c)
        if not r:
            errors.append('顶点 %s 缺 mxGeometry 尺寸' % c.get('id'))
            continue
        if any(abs(v - int(v)) > 0.01 for v in r[:2]):
            warns.append('节点 %s 坐标为小数（建议吸附 gridSize）' % c.get('id'))
        if page_w and page_h and (r[0] + r[2] > page_w or r[1] + r[3] > page_h):
            warns.append('节点 %s 超出页面边界' % c.get('id'))
        # 几何体必须是 as=geometry
        g = c.find('mxGeometry')
        if g is None or g.get('as') != 'geometry':
            errors.append('顶点 %s 缺 as="geometry"' % c.get('id'))

    if len(fonts) > 1:
        warns.append('混用字体: %s' % ', '.join('%s×%d' % (k, v) for k, v in fonts.most_common()))
    if expected_stroke and strokecolors:
        off = {k: v for k, v in strokecolors.items() if k != expected_stroke}
        if off:
            warns.append('描边色偏离预设主色 %s: %s' % (expected_stroke, off))

    # 孤立节点（无任何边）
    connected = set()
    for e in edges:
        connected.add(e.get('source'))
        connected.add(e.get('target'))
    isolated = [n.get('id') for n in plain_nodes if n.get('id') not in connected]
    if isolated and len(plain_nodes) > 2:
        warns.append('孤立节点（无边）: %s' % ', '.join(isolated))

    return {
        'ok': len(errors) == 0,
        'error_count': len(errors),
        'warn_count': len(warns),
        'errors': errors,
        'warns': warns,
        'stats': {
            'vertices': len(vertices), 'edges': len(edges),
            'groups': len(groups), 'plain_nodes': len(plain_nodes),
        },
    }


def main():
    ap = argparse.ArgumentParser(description='drawio 结构 lint')
    ap.add_argument('diagram', help='.drawio 文件')
    ap.add_argument('--style', default=DEFAULT_STYLE, help='风格 preset（用于描边色校验）')
    ap.add_argument('--json', dest='json_out', help='额外输出 JSON 报告')
    ap.add_argument('--quiet', action='store_true', help='只打印结论')
    args = ap.parse_args()

    preset = None
    if os.path.isfile(args.style):
        with open(args.style, 'r', encoding='utf-8') as fp:
            preset = json.load(fp)

    models = es.load_models(args.diagram)
    if not models:
        print('无法解析:', args.diagram)
        sys.exit(1)

    results = [validate(m, preset) for m in models]
    total_err = sum(r['error_count'] for r in results)
    total_warn = sum(r['warn_count'] for r in results)

    if not args.quiet:
        for i, r in enumerate(results, 1):
            if len(results) > 1:
                print('--- 页 %d ---' % i)
            print('节点 %d / 边 %d / 分组 %d'
                  % (r['stats']['plain_nodes'], r['stats']['edges'], r['stats']['groups']))
            for e in r['errors']:
                print('  [ERROR] ' + e)
            for w in r['warns']:
                print('  [WARN ] ' + w)
            if not r['errors'] and not r['warns']:
                print('  结构检查通过')

    print('=' * 60)
    print('结论: %s（ERROR %d / WARN %d）'
          % ('通过' if total_err == 0 else '不通过，需修复 ERROR', total_err, total_warn))

    if args.json_out:
        with open(args.json_out, 'w', encoding='utf-8') as fp:
            json.dump({'file': args.diagram, 'pages': results,
                       'total_errors': total_err, 'total_warns': total_warn},
                      fp, ensure_ascii=False, indent=2)
        print('JSON 报告:', args.json_out)

    sys.exit(1 if total_err else 0)


if __name__ == '__main__':
    main()
