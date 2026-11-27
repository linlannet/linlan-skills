# -*- coding: utf-8 -*-
"""
build_diagram.py — 结构化架构图生成器（L1 结构化中间层）

设计目标：让 AI 只描述「结构 + 语义」，不再手写坐标。
    - 输入：JSON spec（节点 / 边 / 分组 / 布局意图）
    - 输出：可编辑的 .drawio XML（未压缩，可读可 diff）
    - 风格：读取 styles/<preset>.json，默认 linlan（黑描边 + 浅色语义填充 + Tahoma + 直角）

确定性保证：
    - 同一份 spec 永远生成同一份 XML（坐标整数、吸附 gridSize）
    - 稳定语义 ID（spec 里的 id 原样保留，绝不复用 0 / 1）
    - 所有边带 <mxGeometry relative="1" as="geometry"/>

用法：
    python build_diagram.py spec.json -o diagram.drawio
    python build_diagram.py spec.json -o diagram.drawio --style styles/linlan.json
    python build_diagram.py spec.json -o diagram.drawio --compress   # 输出压缩格式（可选）

spec 格式见 references/spec-format.md。

作者：六百（linlan-skills）
"""
import os
import re
import sys
import json
import argparse
import base64
import urllib.parse
import zlib
from xml.sax.saxutils import escape, quoteattr

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_STYLE = os.path.join(HERE, '..', 'styles', 'linlan.json')

# linlan 分组描边色签名（架构图分层用）
GROUP_COLORS = {
    'default': '#000000',
    'red':     '#EA6B66',
    'green':   '#00994D',
    'blue':    '#6666FF',
    'darkred': '#660000',
}

DEFAULT_W, DEFAULT_H = 140, 60
PAD_X, PAD_Y = 60, 80
GROUP_PAD, GROUP_START = 20, 30
GRID = 10


# ---------------------------------------------------------------------------
# 1. spec 校验与规范化
# ---------------------------------------------------------------------------
def slugify(text):
    s = re.sub(r'[^\w\u4e00-\u9fff]+', '-', str(text).strip().lower())
    return s.strip('-') or 'node'


def normalize_spec(spec):
    """校验并回填默认值，返回规范化 spec。抛 ValueError 表示 spec 有错。"""
    if not isinstance(spec, dict):
        raise ValueError('spec 顶层必须是 JSON 对象')

    nodes = spec.get('nodes') or []
    edges = spec.get('edges') or []
    groups = spec.get('groups') or []
    if not nodes:
        raise ValueError('spec.nodes 不能为空')

    ids = []
    for n in nodes:
        nid = str(n.get('id') or slugify(n.get('label', 'node')))
        if nid in ('0', '1'):
            raise ValueError('节点 id 不能是 0 或 1（drawio 保留）')
        if nid in ids:
            raise ValueError('节点 id 重复：%s' % nid)
        ids.append(nid)
        n['id'] = nid
        n['label'] = str(n.get('label', ''))
        n['role'] = n.get('role') or 'service'
        n['w'] = int(n.get('w') or DEFAULT_W)
        n['h'] = int(n.get('h') or DEFAULT_H)
        n['layer'] = int(n.get('layer') or 0)
        n['group'] = n.get('group')

    idset = set(ids)
    for i, e in enumerate(edges):
        if str(e.get('from')) not in idset or str(e.get('to')) not in idset:
            raise ValueError('边 #%d 指向不存在的节点：%s -> %s'
                             % (i, e.get('from'), e.get('to')))
        e['from'] = str(e['from'])
        e['to'] = str(e['to'])
        e['id'] = 'e%d' % (i + 2)   # 避开 0/1
        e['label'] = str(e.get('label', ''))
        e['kind'] = e.get('kind') or 'sync'

    gids = set()
    for g in groups:
        gid = str(g.get('id') or slugify(g.get('label', 'group')))
        if gid in gids:
            raise ValueError('分组 id 重复：%s' % gid)
        gids.add(gid)
        g['id'] = gid
        g['label'] = str(g.get('label', ''))
        g['layer'] = int(g.get('layer') or 0)
        g['color'] = g.get('color') or 'default'
        if g['color'] not in GROUP_COLORS:
            raise ValueError('分组 %s 的 color 必须是 %s 之一'
                             % (gid, ', '.join(GROUP_COLORS)))

    layout = spec.get('layout') or 'layered'
    if layout not in ('layered', 'grid', 'free'):
        raise ValueError('layout 必须是 layered / grid / free')
    direction = (spec.get('direction') or 'TB').upper()
    if direction not in ('TB', 'LR'):
        raise ValueError('direction 必须是 TB / LR')

    spec['layout'] = layout
    spec['direction'] = direction
    spec['nodes'] = nodes
    spec['edges'] = edges
    spec['groups'] = groups
    spec['title'] = str(spec.get('title') or '')
    return spec


def snap(v):
    """吸附到 grid。"""
    return int(round(float(v) / GRID) * GRID)


# ---------------------------------------------------------------------------
# 2. 确定性布局
# ---------------------------------------------------------------------------
def layout_nodes(spec):
    """计算每个节点 / 分组的坐标，写回 spec。纯函数式，不依赖外部库。"""
    nodes, groups = spec['nodes'], spec['groups']
    layout, direction = spec['layout'], spec['direction']
    pos = {}

    if layout == 'free':
        for n in nodes:
            pos[n['id']] = (snap(n.get('x') or 0), snap(n.get('y') or 0))
    elif layout == 'grid':
        cols = max(1, int(spec.get('cols') or 3))
        for i, n in enumerate(nodes):
            pos[n['id']] = (snap((i % cols) * (DEFAULT_W + PAD_X)),
                            snap((i // cols) * (DEFAULT_H + PAD_Y)))
    else:  # layered
        layers = {}
        for n in nodes:
            layers.setdefault(n['layer'], []).append(n)
        maxlayer = max(layers) if layers else 0
        y, x = snap(GROUP_PAD), snap(GROUP_PAD)
        for li in range(maxlayer + 1):
            row = layers.get(li, [])
            if not row:
                continue
            row_w = sum(n['w'] for n in row) + PAD_X * (len(row) - 1)
            if direction == 'TB':
                # 每层水平居中（以最宽层为基准）
                px = snap(max(GROUP_PAD, (spec.get('_max_row_w', row_w) - row_w) / 2 + GROUP_PAD))
                for n in row:
                    pos[n['id']] = (px, y)
                    px = snap(px + n['w'] + PAD_X)
                y = snap(y + max(n['h'] for n in row) + PAD_Y)
            else:
                # LR：层从左到右，层内节点从上到下
                py = snap(GROUP_PAD)
                for n in row:
                    pos[n['id']] = (x, py)
                    py = snap(py + n['h'] + PAD_Y)
                x = snap(x + max(n['w'] for n in row) + PAD_X)

    # 分组：包住同组节点
    gpos = {}
    for g in groups:
        members = [n for n in nodes if n.get('group') == g['id']]
        if not members or layout == 'free':
            continue
        boxes = [(pos[n['id']][0], pos[n['id']][1], n['w'], n['h']) for n in members]
        gx = snap(min(b[0] for b in boxes) - GROUP_PAD)
        gy = snap(min(b[1] for b in boxes) - GROUP_START)
        gw = snap(max(b[0] + b[2] for b in boxes) - gx + GROUP_PAD)
        gh = snap(max(b[1] + b[3] for b in boxes) - gy + GROUP_PAD)
        gpos[g['id']] = (gx, gy, gw, gh)

    # 整体平移，保证所有分组坐标非负（swimlane 负坐标会导致渲染异常）
    shift_x = max([0] + [-g[0] for g in gpos.values()])
    shift_y = max([0] + [-g[1] for g in gpos.values()])
    if shift_x or shift_y:
        pos = {k: (snap(v[0] + shift_x), snap(v[1] + shift_y)) for k, v in pos.items()}
        gpos = {k: (snap(v[0] + shift_x), snap(v[1] + shift_y), v[2], v[3])
                for k, v in gpos.items()}

    # 页面尺寸自适应（不低于 A4 横向 1169x827）
    maxw = max([1169] + [p[0] + p[2] for p in gpos.values()] +
               [pos[n['id']][0] + n['w'] for n in nodes])
    maxh = max([827] + [p[1] + p[3] for p in gpos.values()] +
               [pos[n['id']][1] + n['h'] for n in nodes])
    return pos, gpos, snap(maxw + GROUP_PAD), snap(maxh + GROUP_PAD)


# ---------------------------------------------------------------------------
# 3. 样式映射
# ---------------------------------------------------------------------------
def node_style(node, preset):
    role = node['role']
    slot = preset.get('roles', {}).get(role, 'primary')
    pair = preset.get('palette', {}).get(slot) or {'fillColor': '#FFFFFF', 'strokeColor': '#000000'}
    shape = node.get('shape') or preset.get('shapes', {}).get(role, 'rounded=0')
    font = preset.get('font', {})
    extras = preset.get('extras', {})
    parts = [shape, 'whiteSpace=wrap', 'html=1',
             'fillColor=%s' % pair.get('fillColor', '#FFFFFF'),
             'strokeColor=%s' % pair.get('strokeColor', '#000000'),
             'fontFamily=%s' % font.get('fontFamily', 'Tahoma'),
             'fontSize=%s' % font.get('fontSize', 12),
             'strokeWidth=%s' % extras.get('globalStrokeWidth', 1)]
    if extras.get('fontColor'):
        parts.append('fontColor=%s' % extras['fontColor'])
    if node.get('dashed'):
        parts.append('dashed=1')
    if node.get('style_extra'):
        parts.append(str(node['style_extra']).strip(';'))
    return ';'.join(parts) + ';'


def group_style(group, preset):
    font = preset.get('font', {})
    color = GROUP_COLORS[group['color']]
    return ';'.join([
        'swimlane', 'html=1', 'startSize=%d' % GROUP_START,
        'fillColor=none', 'strokeColor=%s' % color,
        'swimlaneFillColor=none',
        'fontFamily=%s' % font.get('fontFamily', 'Tahoma'),
        'fontSize=%s' % font.get('fontSize', 12),
        'fontStyle=1', 'rounded=0',
    ]) + ';'


def edge_style(edge, preset):
    base = preset.get('edges', {}).get('style', 'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;')
    arrow = preset.get('edges', {}).get('arrow', 'endArrow=classic;endFill=1;')
    parts = [base.strip(';'), arrow.strip(';')]
    kind = edge.get('kind')
    dashed_for = preset.get('edges', {}).get('dashedFor') or []
    if kind == 'async' or (dashed_for and kind in dashed_for):
        parts.append('dashed=1')
    if edge.get('label'):
        parts.extend(['labelBackgroundColor=#FFFFFF', 'fontSize=10'])
    if edge.get('style_extra'):
        parts.append(str(edge['style_extra']).strip(';'))
    return ';'.join(p for p in parts if p) + ';'


# ---------------------------------------------------------------------------
# 4. XML 生成
# ---------------------------------------------------------------------------
def build_xml(spec, preset, page_w, page_h, pos, gpos):
    from xml.etree import ElementTree as ET

    model = ET.Element('mxGraphModel', {
        'dx': str(page_w), 'dy': str(page_h),
        'grid': '1', 'gridSize': str(GRID),
        'guides': '1', 'tooltips': '1', 'connect': '1', 'arrows': '1',
        'fold': '1', 'page': '1', 'pageScale': '1',
        'pageWidth': str(page_w), 'pageHeight': str(page_h),
        'math': '0', 'shadow': '0',
    })
    root = ET.SubElement(model, 'root')
    ET.SubElement(root, 'mxCell', {'id': '0'})
    ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})

    # 分组（先画，作为父容器）
    for g in spec['groups']:
        if g['id'] not in gpos:
            continue
        x, y, w, h = gpos[g['id']]
        c = ET.SubElement(root, 'mxCell', {
            'id': 'g-' + g['id'], 'value': escape(g['label']),
            'style': group_style(g, preset), 'vertex': '1', 'parent': '1',
        })
        ET.SubElement(c, 'mxGeometry', {
            'x': str(x), 'y': str(y), 'width': str(w), 'height': str(h), 'as': 'geometry',
        })

    # 节点（注意：swimlane 子节点的坐标相对父容器，需换算）
    for n in spec['nodes']:
        ax, ay = pos[n['id']]
        gid = n.get('group')
        has_group = gid and ('g-' + gid) in {c.get('id') for c in root}
        parent = 'g-' + gid if has_group else '1'
        if has_group:
            gx, gy, _, _ = gpos[gid]
            nx, ny = snap(ax - gx), snap(ay - gy)
        else:
            nx, ny = ax, ay
        c = ET.SubElement(root, 'mxCell', {
            'id': n['id'], 'value': escape(n['label']),
            'style': node_style(n, preset), 'vertex': '1', 'parent': parent,
        })
        ET.SubElement(c, 'mxGeometry', {
            'x': str(nx), 'y': str(ny), 'width': str(n['w']), 'height': str(n['h']), 'as': 'geometry',
        })

    # 边
    for e in spec['edges']:
        c = ET.SubElement(root, 'mxCell', {
            'id': e['id'], 'value': escape(e['label']),
            'style': edge_style(e, preset), 'edge': '1',
            'parent': '1', 'source': e['from'], 'target': e['to'],
        })
        ET.SubElement(c, 'mxGeometry', {'relative': '1', 'as': 'geometry'})

    ET.indent(model, space='  ')
    inner = ET.tostring(model, encoding='unicode')
    return inner, spec.get('title') or 'diagram'


def compress_xml(inner_xml):
    """把 diagram 内部 XML 压成 drawio 压缩格式（raw deflate + base64 + urlencode）。"""
    co = zlib.compressobj(9, zlib.DEFLATED, -15)
    raw = co.compress(inner_xml.encode('utf-8')) + co.flush()
    return urllib.parse.quote(base64.b64encode(raw).decode('ascii'))


def wrap_mxfile(name, inner, compressed):
    payload = compress_xml(inner) if compressed else inner
    return ('<mxfile host="app.diagrams.net" agent="linlan-build_diagram" version="24.0.0">\n'
            '  <diagram id="linlan-%s" name=%s>%s</diagram>\n</mxfile>\n'
            % (slugify(name), quoteattr(name), payload))


# ---------------------------------------------------------------------------
# 5. CLI
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description='结构化架构图生成器（DSL JSON -> .drawio）')
    ap.add_argument('spec', help='JSON spec 文件路径')
    ap.add_argument('-o', '--out', required=True, help='输出 .drawio 路径')
    ap.add_argument('--style', default=DEFAULT_STYLE, help='风格 preset（默认 styles/linlan.json）')
    ap.add_argument('--compress', action='store_true', help='输出压缩格式（默认未压缩，可读）')
    ap.add_argument('--print', action='store_true', help='同时打印生成的 XML')
    args = ap.parse_args()

    with open(args.spec, 'r', encoding='utf-8') as fp:
        spec = normalize_spec(json.load(fp))
    with open(args.style, 'r', encoding='utf-8') as fp:
        preset = json.load(fp)

    # 预先算最宽层，供各层水平居中对齐
    if spec['layout'] == 'layered' and spec['direction'] == 'TB':
        bylayer = {}
        for n in spec['nodes']:
            row_w = sum(x['w'] for x in spec['nodes'] if x['layer'] == n['layer']) + \
                    PAD_X * (len([x for x in spec['nodes'] if x['layer'] == n['layer']]) - 1)
            bylayer[n['layer']] = row_w
        spec['_max_row_w'] = max(bylayer.values()) if bylayer else 0

    pos, gpos, page_w, page_h = layout_nodes(spec)
    inner, title = build_xml(spec, preset, page_w, page_h, pos, gpos)
    payload = wrap_mxfile(title, inner, args.compress)
    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)

    with open(out, 'w', encoding='utf-8') as fp:
        fp.write(payload)

    if args.print:
        print(payload)
    print('已生成: %s' % out)
    print('节点 %d / 边 %d / 分组 %d / 页面 %dx%d / 风格 %s'
          % (len(spec['nodes']), len(spec['edges']), len(spec['groups']),
             page_w, page_h, preset.get('name', '?')))


if __name__ == '__main__':
    main()
