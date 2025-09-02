# ic_id/core.py
import cv2
import numpy as np
import os
from os.path import join


def non_max_suppression(boxes, scores, iou_threshold=0.5):
    """非极大值抑制：去除重叠的检测框（内部函数，不对外暴露）"""
    if len(boxes) == 0:
        return []
    
    boxes = np.array(boxes, dtype=np.float32)
    scores = np.array(scores, dtype=np.float32)
    
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]
    
    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    order = scores.argsort()[::-1]
    
    keep = []
    while order.size > 0:
        top_idx = order[0]
        keep.append(top_idx)
        
        xx1 = np.maximum(x1[top_idx], x1[order[1:]])
        yy1 = np.maximum(y1[top_idx], y1[order[1:]])
        xx2 = np.minimum(x2[top_idx], x2[order[1:]])
        yy2 = np.minimum(y2[top_idx], y2[order[1:]])
        
        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)
        inter = w * h
        
        iou = inter / (areas[top_idx] + areas[order[1:]] - inter)
        inds = np.where(iou <= iou_threshold)[0]
        order = order[inds + 1]
    
    return [boxes[i].astype(np.int32) for i in keep]


def get_output_path(input_path, suffix="-cvm", ext=None):
    """生成输出路径（内部函数，不对外暴露）"""
    base_name = os.path.basename(input_path)
    file_name, file_ext = os.path.splitext(base_name)
    target_ext = ext if ext is not None else file_ext
    new_file_name = f"{file_name}{suffix}{target_ext}"
    return join(os.path.dirname(input_path), new_file_name)


def save_matches_to_txt(matches, output_image_path, target_image_path):
    txt_path = get_output_path(output_image_path, suffix="", ext=".txt")
    
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"模板匹配结果报告\n")
        f.write(f"目标图像路径: {os.path.abspath(target_image_path)}\n")
        f.write(f"匹配总数: {len(matches)}\n")
        f.write(f"="*80 + "\n")
        if matches:
            f.write(f"匹配详情:\n")
            for i, match in enumerate(matches, 1):
                x, y, w, h, score, template_name = match
                template_name = template_name.split(".")[0]
                line = f"  匹配 #{i}: 模板({template_name}) 位置({x}, {y}), 尺寸({w}x{h}), 得分: {score:.4f}\n"
                f.write(line)
        else:
            f.write("未找到任何匹配结果\n")
    
    return txt_path


def get_all_png_templates(template_dir="template"):
    if not os.path.exists(template_dir):
        raise FileNotFoundError(f"模板文件夹不存在: {os.path.abspath(template_dir)}")
    
    template_paths = []
    for file_name in os.listdir(template_dir):
        if file_name.lower().endswith(".png"):
            template_path = join(template_dir, file_name)
            if os.path.isfile(template_path):
                template_paths.append(template_path)
    
    if not template_paths:
        raise ValueError(f"模板文件夹 {os.path.abspath(template_dir)} 内未找到任何PNG格式模板")
    
    return template_paths


def detect_objects(
    target_image_path,
    template_dir="template",  # 新增：模板文件夹（默认"template"，对齐新代码核心优化）
    threshold=0.95,
    iou_threshold=0.5,
    output_path=None
):
    """
    （对外入口函数，完全对齐旧版命名）模板匹配主函数：自动读取模板、检测、保存结果
    
    参数:
        target_image_path (str): 目标图像路径
        template_dir (str): 模板文件夹路径（默认"template"，自动读取内部所有PNG）
        threshold (float): 匹配阈值（默认0.95）
        iou_threshold (float): NMS重叠阈值（默认0.5）
        output_path (str): 结果图像保存路径（默认自动生成，如"目标图-cvm.png"）
    
    返回:
        dict: 包含匹配结果的字典，键如下：
            - matches: 匹配详情列表（每个元素为(x, y, w, h, score, template_name)）
            - total_matches: 匹配总数
            - output_path: 结果图像保存路径
            - txt_report_path: 匹配报告TXT保存路径
            - loaded_templates: 加载的模板名称列表
    """
    # 1. 自动加载模板（新代码核心优化点）
    template_paths = get_all_png_templates(template_dir)
    # print(f"自动加载模板 {len(template_paths)} 个: {[os.path.basename(p) for p in template_paths]}")
    
    # 2. 加载目标图像
    target_image = cv2.imread(target_image_path, cv2.IMREAD_COLOR)
    if target_image is None:
        raise ValueError(f"无法加载目标图像: {target_image_path}")
    
    # 3. 处理输出路径
    if output_path is None:
        output_path = get_output_path(target_image_path)
    
    # 4. 模板匹配核心逻辑
    gray_target = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)
    all_matches = []
    colors = [(0,255,0), (0,0,255), (255,0,0), (255,255,0), (0,255,255), (255,0,255)]

    for i, template_path in enumerate(template_paths):
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            raise ValueError(f"无法加载模板图像: {template_path}")

        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        t_rows, t_cols = gray_template.shape[:2]
        template_name = os.path.basename(template_path)

        # 模板匹配计算
        method = cv2.TM_CCOEFF_NORMED
        result = cv2.matchTemplate(gray_target, gray_template, method)

        # 初始筛选匹配框
        locations = np.where(result >= threshold)
        initial_matches = []
        boxes = []
        scores = []

        for (x, y) in zip(*locations[::-1]):
            score = result[y, x]
            x1, y1 = x, y
            x2, y2 = x + t_cols, y + t_rows
            initial_matches.append((x1, y1, t_cols, t_rows, float(score), template_name))
            boxes.append((x1, y1, x2, y2))
            scores.append(score)

        # NMS去重
        keep_boxes = non_max_suppression(boxes, scores, iou_threshold) if boxes else []

        # 整理最终匹配结果并绘制框
        for box in keep_boxes:
            x1, y1, x2, y2 = box
            width = x2 - x1
            height = y2 - y1
            # 找到对应匹配的最高分（避免重复）
            score = max([m[4] for m in initial_matches if m[0] == x1 and m[1] == y1])
            final_match = (x1, y1, width, height, float(score), template_name)
            all_matches.append(final_match)

            # 绘制矩形框（循环用颜色）
            cv2.rectangle(target_image, (x1, y1), (x2, y2), colors[i % len(colors)], 2)
            
            # 绘制标签（优化可读性）
            label = f"{template_name.split('.')[0]} {score:.2f}"
            print("\n===== 步骤3：生成标签 =====")
            print(f"  用于生成标签的template_name: {template_name}")  # 确认此处模板名
            print(f"  生成的label: {label}")  # 查看最终标签是否符合预期
            font_scale = 2.0
            thickness = 3
            vertical_offset = 30

            (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
            text_x = max(x1, 0)
            text_y = max(y1 - vertical_offset, text_height + 10)
            if text_x + text_width > target_image.shape[1]:
                text_x = target_image.shape[1] - text_width - 5

            # 黑色背景增强文字可读性
            padding = 5
            cv2.rectangle(target_image, 
                        (text_x - padding, text_y - text_height - padding),
                        (text_x + text_width + padding, text_y + padding),
                        (0, 0, 0), -1)
            cv2.putText(target_image, label, (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale,
                        colors[i % len(colors)], thickness)

    # 5. 保存结果图像和TXT报告（内置，无需用户单独调用）
    cv2.imwrite(output_path, target_image)
    txt_report_path = save_matches_to_txt(all_matches, output_path, target_image_path)

    # 6. 返回结果（对齐旧版的返回结构，新增loaded_templates）
    return {
        "matches": all_matches,
        "total_matches": len(all_matches),
        "output_path": output_path,
        "txt_report_path": txt_report_path,  # 旧版核心返回键，必须保留
        "loaded_templates": [os.path.basename(p) for p in template_paths]
    }